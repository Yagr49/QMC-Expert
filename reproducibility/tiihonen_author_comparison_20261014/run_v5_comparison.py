"""Frozen v5 raw/human transfer to the author's fixed COE split.

Prespecified 500/depth6/.05/seed42 CatBoost; no test tuning. Uses local model
and locally owned scaler/checkpoint, never public pickled estimators.
"""
import os
from pathlib import Path
_CACHE=Path(__file__).resolve().parent/'runtime_cache'
os.environ.setdefault('HF_HOME',str(_CACHE))
os.environ.setdefault('HF_MODULES_CACHE',str(_CACHE/'modules'))
os.environ.setdefault('TRANSFORMERS_CACHE',str(_CACHE/'hub'))
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
import sys,json,pickle,hashlib,time
import numpy as np,pandas as pd,torch
from rdkit import Chem
from transformers import AutoTokenizer,AutoModel
from catboost import CatBoostRegressor
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
sys.path.insert(0,str(COMA/'reproducibility/v5_hypotheses_20261013'))
from prepare import HistoricalEncoder

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 start=time.time();torch.set_num_threads(6);torch.manual_seed(1729)
 frame=pd.read_csv(ROOT/'endpoint_registry.csv')
 frame=frame[frame.rdkit_valid].reset_index(drop=True)
 frame['canonical_smiles']=[Chem.MolToSmiles(Chem.MolFromSmiles(s)) for s in frame.smiles]
 assert len(frame[frame.split=='train'])==78 and len(frame[frame.split=='test'])==20
 frame.to_csv(ROOT/'valid_smiles_registry.csv',index=False)
 runtime=COMA/'reproducibility/revision_v9/runtime/molformer'
 tok=AutoTokenizer.from_pretrained(runtime,trust_remote_code=True,local_files_only=True)
 strings=frame.canonical_smiles.tolist()
 lengths=[len(x) for x in tok(strings,truncation=False)['input_ids']]
 frame['token_length']=lengths
 frame['truncated_202']=frame.token_length>202
 frame.to_csv(ROOT/'valid_smiles_registry.csv',index=False)
 manifest=dict(device='cpu',n_rows=len(frame),frozen=True,source_encoder='archived v5 compact human',
  target_task='E.coli K12 MIC',unit='log2(mg/L), equal to author log2(µg/mL)',
  tokenisation=dict(smiles='RDKit canonical full supplied graph',max_length=202,padding='max_length',
                    max_tokens=max(lengths),truncated=int(sum(x>202 for x in lengths)),
                    truncated_indices=frame.loc[frame.truncated_202,'author_index'].tolist()),
  catboost=dict(iterations=500,depth=6,learning_rate=.05,random_seed=42,thread_count=4),inputs={})
 for p in runtime.iterdir():
  if p.is_file():manifest['inputs'][str(p)]=sha(p)
 if (ROOT/'v5_raw_embeddings.npy').exists():
  prev=json.loads((ROOT/'v5_comparison_manifest.json').read_text())
  assert prev['canonical_smiles_sha256']==hashlib.sha256('\n'.join(strings).encode()).hexdigest()
  raw=np.load(ROOT/'v5_raw_embeddings.npy')
 else:
  model=AutoModel.from_pretrained(runtime,trust_remote_code=True,local_files_only=True,
                                  deterministic_eval=True).eval()
  for module in model.modules():
   if hasattr(module,'deterministic'):module.deterministic=True
  rows=[]
  with torch.no_grad():
   for k in range(0,len(strings),16):
    batch=tok(strings[k:k+16],padding='max_length',truncation=True,max_length=202,return_tensors='pt')
    rows.append(model(**batch).pooler_output.numpy())
    print('embedded',min(k+16,len(strings)),'/',len(strings),flush=True)
  raw=np.vstack(rows).astype('float32');np.save(ROOT/'v5_raw_embeddings.npy',raw)
 assert raw.shape==(105,768) and np.isfinite(raw).all()
 scaler_path=COMA.parent/'Veresh_paper/scaler_classification.pkl'
 net_path=COMA.parent/'Veresh_paper/encoder_borderline_smote.pth'
 scaler=pickle.load(scaler_path.open('rb'))
 net=HistoricalEncoder();net.load_state_dict(torch.load(net_path,map_location='cpu',weights_only=True));net.eval()
 with torch.no_grad():human=net.encoder(torch.tensor(scaler.transform(raw),dtype=torch.float32)).numpy()
 np.save(ROOT/'v5_human_embeddings.npy',human)
 for p in [scaler_path,net_path,ROOT/'endpoint_registry.csv']:manifest['inputs'][str(p)]=sha(p)
 train=frame.split.eq('train').to_numpy();metrics=[];predictions=[]
 for name,x in [('v5_raw',raw),('v5_human',human)]:
  model=CatBoostRegressor(**manifest['catboost'],verbose=False,allow_writing_files=False)
  model.fit(x[train],frame.loc[train,'log2mic'])
  for split in ['test','newdata']:
   sub=frame.split.eq(split).to_numpy();d=frame.loc[sub]
   y=d.log2mic.to_numpy();pred=model.predict(x[sub])
   metrics.append(dict(model=name+'_CatBoost',n_train=int(train.sum()),evaluation=split,
    n=len(d),R2=r2_score(y,pred),RMSE=mean_squared_error(y,pred,squared=False),MAE=mean_absolute_error(y,pred)))
   for i,yv,pv in zip(d.author_index,y,pred):
    predictions.append(dict(model=name+'_CatBoost',evaluation=split,author_index=int(i),y=float(yv),pred=float(pv)))
 pd.DataFrame(metrics).to_csv(ROOT/'v5_metrics.csv',index=False)
 pd.DataFrame(predictions).to_csv(ROOT/'v5_predictions.csv',index=False)
 manifest['seconds']=time.time()-start
 manifest['canonical_smiles_sha256']=hashlib.sha256('\n'.join(strings).encode()).hexdigest()
 manifest['source_overlap_note']='Full expert1103 source audit:0/20 test cations,2/78 train,1/7 newdata. Training membership within saved encoder not fully recovered. Newdata includes source-overlap and is not clean independent transfer.'
 manifest['test_tuning']=False
 (ROOT/'v5_comparison_manifest.json').write_text(json.dumps(manifest,indent=2))
 print(pd.DataFrame(metrics).to_string(index=False),flush=True)
 print(json.dumps(manifest['tokenisation']),flush=True)

if __name__=='__main__':main()
