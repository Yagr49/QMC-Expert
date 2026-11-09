"""New reconstruction of the author's five-fold multitask CV, with saved fold scores."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='2'
from pathlib import Path
import argparse,hashlib,json,time
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from catboost import CatBoostRegressor,Pool
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
def write_json(path,data):
 path=Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));tmp.replace(path)
def job(input_root,output_root,representation,encoding):
 source=Path(input_root)/'data';out=Path(output_root);pairs=pd.read_csv(source/'original108_endpoints.csv')
 vectors=np.load(source/(representation+'_original108.npy'))
 x=vectors[pairs.molecule_index.to_numpy()];task=np.array([TASKS.index(t) for t in pairs.task]);cat=[]
 if encoding in ['categorical_task_id','categorical_org_met']:
  x=pd.DataFrame(x,columns=[f'e{i}' for i in range(x.shape[1])])
  if encoding=='categorical_task_id':x['task_id']=task.astype(str);cat=['task_id']
  else:
   # LabelEncoder order in the April notebook: E. coli < S. aureus, MBC < MIC.
   x['org']=(task<2).astype(int).astype(str);x['met']=(task%2==0).astype(int).astype(str);cat=['org','met']
 else:x=np.column_stack([x,np.load(source/'task_text_embeddings.npy')[task]])
 predictions=np.full(len(pairs),np.nan);folds=np.full(len(pairs),-1);scores=[];exposure=[]
 for fold,(tr,te) in enumerate(KFold(n_splits=5,shuffle=True,random_state=42).split(x)):
  select=lambda indices:x.iloc[indices] if isinstance(x,pd.DataFrame) else x[indices]
  model=CatBoostRegressor(iterations=500,learning_rate=.05,depth=6,random_seed=42,thread_count=2,verbose=False,allow_writing_files=False)
  model.fit(Pool(select(tr),label=pairs.y.iloc[tr].to_numpy(),cat_features=cat))
  pred=model.predict(Pool(select(te),cat_features=cat));predictions[te]=pred;folds[te]=fold
  g=pairs.iloc[te].copy();g['prediction']=pred
  for task_name in TASKS+['pooled']:
   a=g if task_name=='pooled' else g[g.task==task_name];err=a.prediction-a.y
   scores.append(dict(representation=representation,encoding=encoding,fold=fold,task=task_name,n=len(a),RMSE=np.sqrt(np.mean(err**2)),MAE=np.mean(abs(err)),R2=r2_score(a.y,a.prediction)))
  train_molecules=set(pairs.can.iloc[tr]);test_molecules=set(pairs.can.iloc[te])
  exposure.append(dict(fold=fold,unique_train_salts=len(train_molecules),unique_test_salts=len(test_molecules),test_salts_also_in_train=len(test_molecules&train_molecules)))
 assert np.isfinite(predictions).all()
 frame=pairs.copy();frame['prediction']=predictions;frame['fold']=folds;frame['representation']=representation;frame['encoding']=encoding
 stem=representation+'_'+encoding
 frame.to_csv(out/'chunks'/(stem+'_predictions.csv'),index=False);pd.DataFrame(scores).to_csv(out/'chunks'/(stem+'_fold_metrics.csv'),index=False)
 write_json(out/'chunks'/(stem+'.json'),dict(completed=True,representation=representation,encoding=encoding,fits=5,exposure=exposure))
 return stem
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--output-root',required=True);a=ap.parse_args()
 out=Path(a.output_root);(out/'chunks').mkdir(parents=True,exist_ok=True)
 assert not (out/'manifest.json').exists(),'Never overwrite a completed run'
 jobs=[(rep,code) for rep in ['v5_raw','v5_human'] for code in ['categorical_task_id','categorical_org_met','text']]
 write_json(out/'status.json',dict(completed=False,done=0,total=6));start=time.time();done=0
 with ProcessPoolExecutor(max_workers=6) as pool:
  fs=[pool.submit(job,a.input_root,a.output_root,rep,code) for rep,code in jobs]
  for f in as_completed(fs):
   name=f.result();done+=1;write_json(out/'status.json',dict(completed=False,done=done,total=6,last=name));print('CV',done,'/6',name,flush=True)
 frames=[pd.read_csv(p) for p in sorted((out/'chunks').glob('*_fold_metrics.csv'))]
 metrics=pd.concat(frames,ignore_index=True);metrics.to_csv(out/'fold_metrics.csv',index=False)
 rows=[]
 for (rep,code,task),g in metrics.groupby(['representation','encoding','task']):
  row=dict(representation=rep,encoding=code,task=task,n_folds=len(g))
  assert len(g)==5
  for metric in ['RMSE','MAE','R2']:row[metric+'_mean']=float(g[metric].mean());row[metric+'_sd']=float(g[metric].std(ddof=0))
  rows.append(row)
 pd.DataFrame(rows).to_csv(out/'summary.csv',index=False)
 inputs=['original108_endpoints.csv','v5_raw_original108.npy','v5_human_original108.npy','task_text_embeddings.npy']
 write_json(out/'manifest.json',dict(completed=True,fits=30,configurations=6,folds=5,fold_split='KFold over molecule-task rows, shuffle=True, random_state=42',
  decoder='CatBoost 500/depth6/lr.05/seed42',SD='Across five fold scores; numpy.std ddof=0, matching the original CV code; not a 95% CI',
  provenance='New approximate reconstruction of the author CV approach, not recovered original CV uncertainty',
  task_codes='categorical_org_met matches April cell6; task_id matches May cell20; text uses reconstructed cached October vectors',
  encoder='Existing saved human encoder, no source retraining and no change to its historical SMOTE',
  exposure='Different tasks for a molecule can cross row-wise CV folds; grouped-transfer results are separate',
  seconds=time.time()-start,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  input_sha256={p:hashlib.sha256((Path(a.input_root)/'data'/p).read_bytes()).hexdigest() for p in inputs}))
 write_json(out/'status.json',dict(completed=True,done=6,total=6));print('All 30 decoder fits completed',flush=True)
if __name__=='__main__':main()
