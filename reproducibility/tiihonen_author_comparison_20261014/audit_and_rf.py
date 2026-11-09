"""Safe CSV/XLSX audit and fresh native RF fit; no author pickle execution."""
from pathlib import Path
import hashlib,json,zipfile,platform
import numpy as np,pandas as pd
from rdkit import Chem,RDLogger
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score,mean_squared_error
import sklearn

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
DATA=COMA/'Data_and_models/Data'
PUBLIC=Path('/private/tmp/coma_tiihonen_20261014')
if not PUBLIC.exists():PUBLIC=ROOT/'author_code_snapshot'
FEATURES=['MSD','MaxDD','TI2_L','MATS4v','MATS4i','P_VSA_MR_5','P_VSA_MR_6',
 'TDB06s','RDF040m','Mor20m','Mor25m','Mor31m','Mor10v','Mor20v','Mor25v','Mor26s',
 'R7u','H-046','H-047','SHED_AL','ALOGP']
PARAMS=dict(bootstrap=True,max_depth=18,max_features='log2',max_samples=.99,
 min_samples_leaf=1,min_samples_split=2,n_estimators=236,random_state=3,n_jobs=4,
 criterion='squared_error')
RDLogger.DisableLog('rdApp.*')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cation(s):
 m=Chem.MolFromSmiles(str(s))
 if m is None:return None
 frags=Chem.GetMolFrags(m,asMols=True,sanitizeFrags=True)
 positive=[f for f in frags if Chem.GetFormalCharge(f)>0]
 chosen=max(positive or frags,key=lambda x:x.GetNumHeavyAtoms())
 return Chem.MolToSmiles(chosen,isomericSmiles=True)
def read(name):
 p=DATA/'Reference_data_files'/name
 d=pd.read_csv(p,index_col=0);d.index.name='author_index';return d

def main():
 manifest=dict(inputs={},archive_comparison={},version=dict(python=platform.python_version(),
 sklearn=sklearn.__version__,rdkit=Chem.rdBase.rdkitVersion),native_rf=PARAMS,features=FEATURES)
 local=COMA/'Data_and_models.zip';download=PUBLIC/'Data_and_models.zip'
 if not download.exists():download=local
 for p in [local,download,Path('/Users/egorilin/Downloads/Data_and_models.zip')]:
  if p.exists():manifest['inputs'][str(p)]=sha(p)
 with zipfile.ZipFile(download) as z:
  matched=[];different=[];missing=[]
  for p in (COMA/'Data_and_models').rglob('*'):
   if not p.is_file():continue
   rel=str(p.relative_to(COMA)).replace('\\','/')
   names=[rel,str(p.relative_to(COMA/'Data_and_models'))]
   member=next((n for n in names if n in z.namelist()),None)
   if member is None:missing.append(rel);continue
   (matched if hashlib.sha256(z.read(member)).hexdigest()==sha(p) else different).append(rel)
  manifest['archive_comparison']=dict(matched_files=len(matched),different=different,missing=missing)
 frame=pd.read_csv(DATA/'dataset_outliers_dropped.csv',index_col=0)
 train=read('y_opt_train_seed3.csv');test=read('y_opt_test_seed3.csv');new=read('y_opt_newdata.csv')
 registry=[]
 for split,d in [('train',train),('test',test),('newdata',new)]:
  for i,row in d.iterrows():
   registry.append(dict(author_index=int(i),split=split,name=frame.loc[i,'name'] if i in frame.index else '',
    smiles=row.smiles,log2mic=row.log2mic,rdkit_valid=Chem.MolFromSmiles(str(row.smiles)) is not None,cation=cation(row.smiles)))
 registry=pd.DataFrame(registry);registry.to_csv(ROOT/'endpoint_registry.csv',index=False)
 manifest['cohorts']=registry.groupby('split').agg(n=('author_index','size'),rdkit_valid=('rdkit_valid','sum')).to_dict('index')
 manifest['descriptor_source_rows']=len(frame)
 manifest['target_alignment']={}
 for split,d in [('train',train),('test',test),('newdata',new)]:
  assert set(d.index).issubset(frame.index)
  assert np.array_equal(d.log2mic.to_numpy(),frame.loc[d.index,'log2mic'].to_numpy())
  manifest['target_alignment'][split]=True
 valid_train=[i for i in train.index if Chem.MolFromSmiles(str(train.loc[i,'smiles'])) is not None]
 fp=pd.read_csv(DATA/'Reference_data_files/Fingerprints/y_smiles_train_seed3.csv',index_col=0)
 manifest['smiles_train78_matches_valid_train80']=fp.index.tolist()==valid_train
 manifest['invalid_train_indices']=[int(i) for i in train.index if i not in valid_train]
 results=[];predictions=[]
 for train_name,ids in [('author_descriptor_train80',train.index),('matched_valid_smiles_train78',valid_train)]:
  model=RandomForestRegressor(**PARAMS)
  model.fit(frame.loc[ids,FEATURES],train.loc[ids,'log2mic'])
  for split,d in [('test20',test),('newdata7',new)]:
   pred=model.predict(frame.loc[d.index,FEATURES]);y=d.log2mic.to_numpy()
   results.append(dict(model='Author_RF21_refit',train=train_name,n_train=len(ids),evaluation=split,n=len(d),
     R2=r2_score(y,pred),RMSE=mean_squared_error(y,pred,squared=False)))
   for i,yv,pv in zip(d.index,y,pred):predictions.append(dict(model='Author_RF21_refit',train=train_name,evaluation=split,
      author_index=int(i),y=float(yv),pred=float(pv)))
 # Check overlap of target structures with actual known source corpora.
 expert=pd.read_csv(COMA/'expert_labels/expert_labels_1103.csv')
 sources={'expert1103':expert.canonical_smiles,
          'matched681':pd.read_csv(COMA/'reproducibility/v5_hypotheses_20261013/data/matched_source.csv').can}
 for name in ['expert-binary','quant-molecule','quant-record']:
  p=COMA/('reproducibility/finetune/data/src_'+name+'.csv')
  sources['previous_ft_'+name]=pd.read_csv(p).can
 overlaps=[]
 for source,smiles in sources.items():
  keys={cation(s) for s in smiles};keys.discard(None)
  for split,d in registry.groupby('split'):
   hit=d[d.cation.isin(keys)]
   overlaps.append(dict(source=source,split=split,n_unique_cations=len(keys),n_target_overlap=len(hit),
     author_indices=hit.author_index.tolist(),names=hit.name.tolist()))
 manifest['source_overlap']=overlaps
 for p in [DATA/'dataset_outliers_dropped.csv',DATA/'Reference_data_files/y_opt_train_seed3.csv',
           DATA/'Reference_data_files/y_opt_test_seed3.csv',DATA/'Reference_data_files/y_opt_newdata.csv',
           PUBLIC/'Main_downselection.py',PUBLIC/'Functions_downselection_training_RF.py']:
  manifest['inputs'][str(p)]=sha(p)
 pd.DataFrame(results).to_csv(ROOT/'rf_metrics.csv',index=False)
 pd.DataFrame(predictions).to_csv(ROOT/'rf_predictions.csv',index=False)
 (ROOT/'audit_manifest.json').write_text(json.dumps(manifest,indent=2))
 print(pd.DataFrame(results).to_string(index=False))
 print(json.dumps({k:manifest[k] for k in ['cohorts','archive_comparison','invalid_train_indices','source_overlap']},indent=2))

if __name__=='__main__':main()
