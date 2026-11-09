"""Server-only v5 reconstruction and compact-encoder hypothesis checks (no API)."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from pathlib import Path
import argparse,copy,hashlib,json,math,time,platform,traceback
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd
try:
 import torch
 from torch import nn
except ImportError:
 torch=None;nn=None
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from catboost import CatBoostRegressor,Pool

ROOT=Path(__file__).resolve().parent;DATA=ROOT/'data'
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
ARMS=['human','mic_continuous','mic_binary','human_shuffled','continuous_shuffled','binary_shuffled']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def state_sha(state):return hashlib.sha256(b''.join(k.encode()+v.cpu().numpy().tobytes() for k,v in sorted(state.items()))).hexdigest()
def write_json(p,value):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2,default=str));tmp.replace(p)

class Compact(nn.Module if torch is not None else object):
 def __init__(self):
  super().__init__();layers=[];previous=768
  for width in [512,384,256]:
   layers.extend([nn.Linear(previous,width),nn.BatchNorm1d(width),nn.ReLU(),nn.Dropout(.3)]);previous=width
  self.encoder=nn.Sequential(*layers)
  self.projection_head=nn.Sequential(nn.Linear(256,128),nn.BatchNorm1d(128),nn.ReLU(),
    nn.Dropout(.15),nn.Linear(128,128),nn.BatchNorm1d(128))
  self.regression_head=nn.Linear(256,1)
 def forward(self,x):
  h=self.encoder(x);return h,self.projection_head(h),self.regression_head(h).flatten()

def contrastive(projection,labels):
 f=nn.functional.normalize(projection,dim=1);sim=f@f.T/.05
 positive=(labels[:,None]==labels[None,:]).float();negative=1-positive
 diagonal=1-torch.eye(len(labels),device=sim.device);positive=positive*diagonal;negative=negative*diagonal
 exp=torch.exp(sim)*diagonal;logp=sim-torch.log(exp.sum(1,keepdim=True))
 pos=(positive*logp).sum(1)/positive.sum(1).clamp(min=1.)
 weights=nn.functional.softmax(torch.exp(sim)*negative/.05,dim=1)
 hard=(weights*sim*negative).sum(1)
 return (-(.05/.07)*pos+.3*hard).mean()

def extract(net,x,device):
 net.eval()
 with torch.no_grad():return net.encoder(torch.as_tensor(x,dtype=torch.float32,device=device)).cpu().numpy()

def train_compact():
 device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
 torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
 if device.type=='cuda':torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 out=ROOT/'compact';out.mkdir(exist_ok=True);(out/'representations').mkdir(exist_ok=True);(out/'checkpoints').mkdir(exist_ok=True)
 source=pd.read_csv(DATA/'matched_source.csv');tr=np.flatnonzero(source.source_split=='train');va=np.flatnonzero(source.source_split=='validation')
 raw={name:np.load(DATA/('matched_raw_'+name+'.npy')) for name in ['source','QAC105','OOD17']}
 scaler=StandardScaler().fit(raw['source'][tr]);x={k:scaler.transform(v).astype(np.float32) for k,v in raw.items()}
 np.savez(out/'source_scaler.npz',mean=scaler.mean_,scale=scaler.scale_)
 cutoff=float(np.quantile(source.quant_y.iloc[tr],source.y.iloc[tr].mean()))
 qmean=float(source.quant_y.iloc[tr].mean());qsd=float(source.quant_y.iloc[tr].std(ddof=0))
 starts=[];completed=0;records=[];epochs=[];names=[]
 write_json(out/'status.json',dict(completed=False,done=0,total=30,device=str(device)))
 for seed in range(5):
  for arm in ARMS:
   torch.manual_seed(seed)
   if device.type=='cuda':torch.cuda.manual_seed_all(seed)
   net=Compact().to(device);initial={k:v.detach().clone() for k,v in net.state_dict().items()}
   initial_hash=state_sha(initial);starts.append(dict(seed=seed,arm=arm,initial_sha256=initial_hash))
   binary=arm not in ['mic_continuous','continuous_shuffled']
   if arm.startswith('human'):y=source.y.to_numpy(dtype=np.float32).copy()
   elif arm in ['mic_binary','binary_shuffled']:y=(source.quant_y.to_numpy()<=cutoff).astype(np.float32)
   else:y=((source.quant_y.to_numpy()-qmean)/qsd).astype(np.float32)
   before=y[tr].copy()
   if arm.endswith('shuffled'):y[tr]=np.random.default_rng(100000+seed).permutation(y[tr])
   assert np.array_equal(np.sort(before),np.sort(y[tr]))
   labelhash=hashlib.sha256(y[tr].tobytes()).hexdigest()
   optimiser=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001)
   schedule=torch.optim.lr_scheduler.CosineAnnealingLR(optimiser,T_max=80,eta_min=.000001)
   random=np.random.default_rng(42000+seed);batchhash=hashlib.sha256();updates=0;start=time.time()
   for epoch in range(80):
    net.train();losses=[]
    for idx in np.array_split(random.permutation(tr),math.ceil(len(tr)/64)):
     batchhash.update(idx.tobytes());optimiser.zero_grad(set_to_none=True)
     features,projection,pred=net(torch.as_tensor(x['source'][idx],device=device))
     labels=torch.as_tensor(y[idx],device=device)
     loss=contrastive(projection,labels) if binary else nn.functional.mse_loss(pred,labels)
     assert torch.isfinite(loss);loss.backward();nn.utils.clip_grad_norm_(net.parameters(),1.);optimiser.step()
     losses.append(float(loss.detach()));updates+=1
    schedule.step();epochs.append(dict(seed=seed,arm=arm,epoch=epoch+1,training_loss=np.mean(losses)))
    if epoch%10==0:write_json(out/'status.json',dict(completed=False,done=completed,total=30,seed=seed,arm=arm,epoch=epoch+1,device=str(device)))
   assert updates==480
   name=f'compact_{arm}_seed{seed}'
   for cohort in ['QAC105','OOD17']:np.save(out/'representations'/(name+'_'+cohort+'.npy'),extract(net,x[cohort],device))
   # Restore encoder parameters only; retain its learned BatchNorm running state.
   if arm=='human':
    rewind=copy.deepcopy(net)
    for key,param in rewind.named_parameters():param.data.copy_(initial[key])
    for cohort in ['QAC105','OOD17']:np.save(out/'representations'/(f'compact_human_weight_only_seed{seed}_'+cohort+'.npy'),extract(rewind,x[cohort],device))
   if arm=='human':
    fresh=Compact().to(device);fresh.load_state_dict(initial)
    for cohort in ['QAC105','OOD17']:np.save(out/'representations'/(f'compact_initial_seed{seed}_'+cohort+'.npy'),extract(fresh,x[cohort],device))
   torch.save(dict(state_dict={k:v.cpu() for k,v in net.state_dict().items()},initial_state={k:v.cpu() for k,v in initial.items()},
                   source_training_ids=source.can.iloc[tr].tolist(),labels=y[tr],arm=arm,seed=seed),out/'checkpoints'/(name+'.pt'))
   active=sum(p.numel() for p in net.encoder.parameters())+sum(p.numel() for p in (net.projection_head if binary else net.regression_head).parameters())
   records.append(dict(name=name,arm=arm,seed=seed,encoder_parameters=sum(p.numel() for p in net.encoder.parameters()),active_trainable_parameters=active,
    source_parameters=sum(p.numel() for p in net.parameters()),epochs=80,updates=updates,
    initial_sha256=initial_hash,batch_sha256=batchhash.hexdigest(),label_sha256=labelhash,
    source_positive=int(y[tr].sum()) if binary else None,seconds=time.time()-start))
   pd.DataFrame(records).to_csv(out/'training.csv',index=False);pd.DataFrame(epochs).to_csv(out/'epochs.csv',index=False)
   completed+=1;print('SOURCE',completed,'/30',name,'seconds',round(time.time()-start),flush=True)
 for seed in range(5):
  assert len({r['initial_sha256'] for r in records if r['seed']==seed})==1
  assert len({r['batch_sha256'] for r in records if r['seed']==seed})==1
 write_json(out/'manifest.json',dict(completed=True,fits=30,device=str(device),gpu=torch.cuda.get_device_name() if device.type=='cuda' else None,
  decoder_independent=True,train_only_scaler=True,binary_cutoff=cutoff,source_continuous_mean=qmean,source_continuous_sd=qsd,
  train_n=len(tr),validation_n=len(va),paired_initial_states=True,paired_batches=True,training=records,
  script_sha256=sha(__file__),torch=torch.__version__))
 write_json(out/'status.json',dict(completed=True,done=30,total=30,device=str(device)))

def feature_design(vectors,pairs,encoding):
 x=vectors[pairs.molecule_index.to_numpy()];task=np.array([TASKS.index(t) for t in pairs.task])
 if encoding=='categorical':
  frame=pd.DataFrame(x,columns=[f'f{i}' for i in range(x.shape[1])]);frame['task_id']=task.astype(str);return frame
 if encoding=='onehot':return np.column_stack([x,np.eye(4,dtype=np.float32)[task]])
 if encoding in ['text','text_permuted','random_code']:
  codes=np.load(DATA/'task_text_embeddings.npy')
  if encoding=='text_permuted':codes=codes[[2,0,3,1]]
  if encoding=='random_code':
   random=np.random.default_rng(1729).normal(size=codes.shape)
   random=random/np.linalg.norm(random,axis=1,keepdims=True);codes=(random*np.linalg.norm(codes,axis=1,keepdims=True)).astype(np.float32)
  return np.column_stack([x,codes[task]])
 return x

def fit_predict(x,y,test,encoding,model_path=None):
 m=CatBoostRegressor(iterations=500,depth=6,learning_rate=.05,random_seed=42,thread_count=2,
                    verbose=False,allow_writing_files=False)
 if encoding=='categorical':m.fit(Pool(x,label=y,cat_features=['task_id']));pred=m.predict(Pool(test,cat_features=['task_id']))
 else:m.fit(x,y);pred=m.predict(test)
 if model_path:m.save_model(str(model_path))
 return np.asarray(pred)

def subset(x,idx):return x.iloc[idx] if isinstance(x,pd.DataFrame) else x[idx]

def score_rows(output):
 rows=[]
 for (cohort,schema),g in output.groupby(['cohort','schema']):
  for task in TASKS+['pooled']:
   exact=g[(g.qualifier=='=')&(True if task=='pooled' else g.task==task)]
   e=exact.prediction.to_numpy()-exact.y.to_numpy()
   rows.append(dict(cohort=cohort,schema=schema,task=task,n=len(exact),RMSE=float(np.sqrt(np.mean(e**2))),
                    MAE=float(np.mean(abs(e))),R2=float(r2_score(exact.y,exact.prediction)) if task!='pooled' else None))
 return rows

def decode(job):
 name,encoding=job['name'],job['encoding'];start=time.time()
 base=ROOT/'compact/representations' if name.startswith('compact_') else DATA
 outputs=[];fits=0
 if job.get('original'):
  q=pd.read_csv(DATA/'original108_endpoints.csv');x=feature_design(np.load(base/(name+'_original108.npy')),q,encoding)
  pred=np.full(len(q),np.nan)
  for task in TASKS if encoding=='separate' else ['all']:
   chosen=np.flatnonzero(np.ones(len(q),dtype=bool) if task=='all' else q.task==task)
   tr,te=train_test_split(chosen,test_size=.2,random_state=42,stratify=q.task.iloc[chosen] if task=='all' else None)
   pred[te]=fit_predict(subset(x,tr),q.y.to_numpy()[tr],subset(x,te),encoding);fits+=1
  out=q[np.isfinite(pred)].copy();out['prediction']=pred[np.isfinite(pred)];out['cohort']='original108';out['schema']='v5_row_task_holdout';outputs.append(out)
 else:
  r=pd.read_csv(DATA/'endpoint_registry.csv');q=r[r.cohort=='QAC105'].reset_index(drop=True);o=r[r.cohort=='OOD17'].reset_index(drop=True)
  qm=pd.read_csv(DATA/'QAC105.csv');x=feature_design(np.load(base/(name+'_QAC105.npy')),q,encoding)
  xo=feature_design(np.load(base/(name+'_OOD17.npy')),o,encoding)
  for schema in ['cation','scaffold']:
   folded=qm['fold' if schema=='cation' else 'scaffold_fold'].to_numpy()[q.molecule_index.to_numpy()]
   pred=np.full(len(q),np.nan)
   for task in TASKS if encoding=='separate' else ['all']:
    selected=np.ones(len(q),dtype=bool) if task=='all' else q.task.to_numpy()==task
    for fold in range(5):
     tr=np.flatnonzero(selected&(folded!=fold));te=np.flatnonzero(selected&(folded==fold))
     group='cation' if schema=='cation' else 'scaffold'
     assert not set(q[group].iloc[tr])&set(q[group].iloc[te])
     pred[te]=fit_predict(subset(x,tr),q.y.to_numpy()[tr],subset(x,te),encoding);fits+=1
   out=q.copy();out['prediction']=pred;out['schema']=schema;outputs.append(out)
  pred=np.full(len(o),np.nan);models=ROOT/'results/models';models.mkdir(parents=True,exist_ok=True)
  for task in TASKS if encoding=='separate' else ['all']:
   tr=np.flatnonzero(np.ones(len(q),dtype=bool) if task=='all' else q.task.to_numpy()==task)
   te=np.flatnonzero(np.ones(len(o),dtype=bool) if task=='all' else o.task.to_numpy()==task)
   pred[te]=fit_predict(subset(x,tr),q.y.to_numpy()[tr],subset(xo,te),encoding,models/(name+'_'+encoding+'_'+task+'.cbm'));fits+=1
  out=o.copy();out['prediction']=pred;out['schema']='full-QAC105';outputs.append(out)
 output=pd.concat(outputs,ignore_index=True);assert np.isfinite(output.prediction).all()
 for key in ['name','encoding','arm','seed','provenance']:output[key]=job.get(key,'archived')
 metrics=score_rows(output)
 for row in metrics:row.update({k:job.get(k,'archived') for k in ['name','encoding','arm','seed','provenance']})
 chunks=ROOT/'results/chunks';chunks.mkdir(parents=True,exist_ok=True)
 stem=name+'_'+encoding+('_original' if job.get('original') else '')
 output.to_csv(chunks/(stem+'.csv'),index=False);pd.DataFrame(metrics).to_csv(chunks/(stem+'_metrics.csv'),index=False)
 write_json(chunks/(stem+'.json'),dict(**job,completed=True,fits=fits,seconds=time.time()-start,predictions=len(output)))
 return dict(name=name,encoding=encoding,original=bool(job.get('original')),fits=fits,seconds=time.time()-start)

def jobs(original_only=False):
 result=[]
 for name in ['v5_raw','v5_human','v5_qac_ablation']:
  for enc in ['categorical','text','separate']:
   result.append(dict(name=name,encoding=enc,original=True,arm=name,seed=-1,provenance='v5_archived_approximate_reconstruction'))
  if not original_only:
   for enc in ['categorical','onehot','text','separate']:
    result.append(dict(name=name,encoding=enc,arm=name,seed=-1,provenance='v5_archived_grouped_followup'))
 if original_only:return result
 for enc in ['categorical','onehot','text']:
  result.append(dict(name='matched_raw',encoding=enc,arm='matched_raw',seed=-1,provenance='same_frozen_features_as_compact_controls'))
 for seed in range(5):
  for arm in ARMS:
   for enc in ['categorical']+(['text'] if not arm.endswith('shuffled') else []):
    result.append(dict(name=f'compact_{arm}_seed{seed}',encoding=enc,arm=arm,seed=seed,provenance='v5_architecture_matched_source'))
  for arm,name in [('initial',f'compact_initial_seed{seed}'),('human_weight_only',f'compact_human_weight_only_seed{seed}')]:
   result.append(dict(name=name,encoding='categorical',arm=arm,seed=seed,provenance='v5_architecture_weight_control'))
  if seed==0:
   for enc in ['onehot','text_permuted','random_code']:
    result.append(dict(name='compact_human_seed0',encoding=enc,arm='human',seed=0,provenance='v5_architecture_task_code_control'))
 return result

def decode_all(original_only=False):
 out=ROOT/('independent_original' if original_only else 'results');out.mkdir(exist_ok=True)
 pending=jobs(original_only);results=[]
 write_json(out/'status.json',dict(completed=False,done=0,total=len(pending)))
 with ProcessPoolExecutor(max_workers=6) as pool:
  futures={pool.submit(decode,job):job for job in pending}
  for f in as_completed(futures):
   record=f.result();results.append(record)
   write_json(out/'status.json',dict(completed=False,done=len(results),total=len(pending),last=record))
   print('DECODE',len(results),'/',len(pending),record['name'],record['encoding'],'fits',record['fits'],flush=True)
 write_json(out/'manifest.json',dict(completed=True,jobs=len(results),fits=sum(r['fits'] for r in results),
  results=results,script_sha256=sha(__file__),python=platform.python_version(),torch=torch.__version__ if torch is not None else None,
  catboost=__import__('catboost').__version__,numpy=np.__version__,data_manifest_sha256=sha(DATA/'manifest.json')))
 write_json(out/'status.json',dict(completed=True,done=len(results),total=len(pending)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['train','decode','original','all']);a=ap.parse_args()
 if a.stage in ['train','all']:train_compact()
 if a.stage in ['decode','original','all']:decode_all(a.stage=='original')

if __name__=='__main__':main()
