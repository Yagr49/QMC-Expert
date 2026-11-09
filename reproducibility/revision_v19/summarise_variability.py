"""SD of CV fold scores versus SD of complete source-seed runs, kept separate."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'revision_v18';OUT=ROOT/'analysis';OUT.mkdir(exist_ok=True)
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC','pooled']
def fold_metrics(frame,keys):
 records=[]
 for values,g in frame.groupby(keys+['schema','cv_fold']):
  base=dict(zip(keys+['schema','cv_fold'],values));assert g.qualifier.eq('=').all()
  for task in TASKS:
   a=g if task=='pooled' else g[g.task==task];e=a.prediction-a.y
   records.append(dict(**base,task=task,n=len(a),RMSE=np.sqrt(np.mean(e**2)),MAE=np.mean(abs(e)),
    R2=np.nan if task=='pooled' else 1-np.sum(e**2)/np.sum((a.y-a.y.mean())**2)))
 return pd.DataFrame(records)
def main():
 q=pd.read_csv(ROOT.parent/'v5_hypotheses_20261013/data/QAC105.csv')
 p=pd.read_csv(OLD/'analysis/predictions.csv');a=p[p.cohort=='QAC105'].copy()
 a['cv_fold']=[int(q.iloc[int(i)]['fold' if schema=='cation' else 'scaffold_fold']) for i,schema in zip(a.molecule_index,a.schema)]
 fm=fold_metrics(a,['name','encoding','arm','seed']);fm.to_csv(OUT/'core_fold_metrics.csv',index=False)
 fs=fm.groupby(['name','encoding','arm','seed','schema','task']).agg(RMSE_fold_mean=('RMSE','mean'),RMSE_fold_sd=('RMSE',lambda x:float(x.std(ddof=0))),R2_fold_mean=('R2','mean'),R2_fold_sd=('R2',lambda x:float(x.std(ddof=0))),n_folds=('cv_fold','nunique')).reset_index()
 assert fs.n_folds.eq(5).all();fs.to_csv(OUT/'core_fold_summary.csv',index=False)
 modern=pd.read_csv(OLD/'analysis/modern_predictions.csv');m=modern[modern.cohort=='QAC105'].copy();m['cv_fold']=m.fold.astype(int)
 expected=[int(q.iloc[int(i)]['fold' if schema=='cation' else 'scaffold_fold']) for i,schema in zip(m.molecule_index,m.schema)]
 assert np.array_equal(m.cv_fold,np.asarray(expected))
 mf=fold_metrics(m,['model','representation']);mf.to_csv(OUT/'modern_fold_metrics.csv',index=False)
 mf.groupby(['model','representation','schema','task']).agg(RMSE_fold_mean=('RMSE','mean'),RMSE_fold_sd=('RMSE',lambda x:float(x.std(ddof=0))),R2_fold_mean=('R2','mean'),R2_fold_sd=('R2',lambda x:float(x.std(ddof=0))),n_folds=('cv_fold','nunique')).reset_index().to_csv(OUT/'modern_fold_summary.csv',index=False)
 seeds=pd.read_csv(OLD/'analysis/metrics.csv');s=seeds[seeds.name.str.startswith('compact_')]
 ss=s.groupby(['arm','encoding','cohort','schema','task']).agg(RMSE_seed_mean=('RMSE','mean'),RMSE_seed_sd=('RMSE',lambda x:float(x.std(ddof=1))),R2_seed_mean=('R2','mean'),R2_seed_sd=('R2',lambda x:float(x.std(ddof=1))),n_seeds=('seed','nunique')).reset_index()
 ss.to_csv(OUT/'seed_summary.csv',index=False)
 rowcv=ROOT/'rowcv_results/summary.csv'
 manifest=dict(original_SD_recovered=['Linear probe MolFormer→human R² 0.891±0.037','Linear probe human→MolFormer R² 0.844±0.060'],
  original_probe_SD='Saved May cell5; np.std of 5 folds, ddof=0',
  strong_May_R2='Single holdout; no matched saved CV SD identified for 0.7494/0.6752/0.5918/0.7708',
  grouped_fold_SD='Unweighted mean ± population SD of five fold scores; numpy std ddof=0; not 95% CI',
  source_seed_SD='Mean ± sample SD of five complete source-seed runs; ddof=1; not CV-fold SD',
  OOD='No OOD CV folds; seed variability can be reported for multiple source runs, not one archived checkpoint',
  rowcv_completed=rowcv.exists(),input_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in [OLD/'analysis/predictions.csv',OLD/'analysis/modern_predictions.csv',OLD/'analysis/metrics.csv']})
 (OUT/'variability_manifest.json').write_text(json.dumps(manifest,indent=2));print('Saved 5-fold scores and separate source-seed summaries.')
if __name__=='__main__':main()
