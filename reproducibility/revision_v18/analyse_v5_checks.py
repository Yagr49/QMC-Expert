"""Analyse saved v5-anchored predictions; no fitting or outcome-based selection."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent;RUN=ROOT.parent/'v5_hypotheses_20261013'
OUT=ROOT/'analysis';OUT.mkdir(exist_ok=True)
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
def snapshot(which):return Path(json.loads((RUN/(which+'_latest_snapshot.json')).read_text())['path'])
def metrics(pred,keys):
 records=[]
 for values,g in pred.groupby(keys):
  if not isinstance(values,tuple):values=(values,)
  base=dict(zip(keys,values));g=g[g.qualifier=='=']
  for task in TASKS+['pooled']:
   a=g if task=='pooled' else g[g.task==task];e=a.prediction.to_numpy()-a.y.to_numpy()
   den=np.sum((a.y.to_numpy()-a.y.mean())**2)
   records.append(dict(**base,task=task,n=len(a),RMSE=np.sqrt(np.mean(e**2)),MAE=np.mean(abs(e)),
    R2=np.nan if task=='pooled' else 1-np.sum(e**2)/den))
 return pd.DataFrame(records)
def paired(a,b,label,unit='cation'):
 a=a[a.qualifier=='='].copy();b=b[b.qualifier=='='].copy()
 sa=sorted(a.seed.unique());sb=sorted(b.seed.unique())
 if sa==[-1] and sb!=[-1]:a=pd.concat([a.assign(seed=s) for s in sb],ignore_index=True)
 if sb==[-1] and sa!=[-1]:b=pd.concat([b.assign(seed=s) for s in sa],ignore_index=True)
 j=a.merge(b,on=['cohort','schema','compound_id','task','seed'],suffixes=('_a','_b'),validate='one_to_one')
 assert len(j)==len(a)==len(b) and np.allclose(j.y_a,j.y_b)
 records=[]
 for schema,g in j.groupby('schema'):
  seeds=sorted(g.seed.unique());groups=sorted(g[unit+'_a'].unique());n=np.zeros((len(seeds),len(groups)))
  ma=n.copy();mb=n.copy()
  for i,seed in enumerate(seeds):
   for k,group in enumerate(groups):
    z=g[(g.seed==seed)&(g[unit+'_a']==group)];n[i,k]=len(z)
    ma[i,k]=np.sum((z.prediction_a-z.y_a)**2);mb[i,k]=np.sum((z.prediction_b-z.y_b)**2)
  delta=np.mean(np.sqrt(ma.sum(1)/n.sum(1))-np.sqrt(mb.sum(1)/n.sum(1)))
  rng=np.random.default_rng(1729);weights=rng.multinomial(len(groups),np.ones(len(groups))/len(groups),size=10000)
  seed_indices=rng.integers(len(seeds),size=(10000,len(seeds)))
  ar=np.sqrt(weights@ma.T/(weights@n.T));br=np.sqrt(weights@mb.T/(weights@n.T))
  draws=np.take_along_axis(ar-br,seed_indices,axis=1).mean(1);lo,hi=np.quantile(draws,[.025,.975])
  records.append(dict(comparison=label,schema=schema,unit=unit,n_seeds=len(seeds),n_clusters=len(groups),
   delta_RMSE=delta,ci_low=lo,ci_high=hi,bootstrap_draws=10000))
 return records
def main():
 source=snapshot('main');other=snapshot('independent')
 chunks=source/'results/chunks';paths=sorted(p for p in chunks.glob('*.csv') if not p.name.endswith('_metrics.csv'))
 pred=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True);assert len(paths)==82
 pred.to_csv(OUT/'predictions.csv',index=False)
 m=metrics(pred,['name','encoding','arm','seed','cohort','schema']);m.to_csv(OUT/'metrics.csv',index=False)
 keys=['arm','encoding','cohort','schema','task']
 summary=m.groupby(keys).agg(RMSE=('RMSE','mean'),RMSE_sd=('RMSE','std'),MAE=('MAE','mean'),R2=('R2','mean'),n_seeds=('seed','nunique'),n=('n','first')).reset_index()
 summary.to_csv(OUT/'summary.csv',index=False)
 verify=[]
 for p in sorted((other/'results/chunks').glob('*.csv')):
  if p.name.endswith('_metrics.csv'):continue
  a=pd.read_csv(chunks/p.name);b=pd.read_csv(p);order=['compound_id','task']
  a=a.sort_values(order).reset_index(drop=True);b=b.sort_values(order).reset_index(drop=True)
  assert a[order].equals(b[order]) and np.array_equal(a.y,b.y)
  gap=float(np.max(abs(a.prediction-b.prediction)));assert gap<1e-10
  verify.append(dict(configuration=p.stem,max_prediction_difference=gap,n=len(a)))
 assert len(verify)==9
 pd.DataFrame(verify).to_csv(OUT/'independent_replay.csv',index=False)
 controlled=pred[(pred.provenance.str.startswith('v5_architecture'))&(pred.encoding=='categorical')]
 cs=[]
 for aa,bb in [('human','human_shuffled'),('human','mic_continuous'),('human','mic_binary'),('mic_binary','binary_shuffled'),('mic_continuous','continuous_shuffled'),('human_weight_only','human'),('initial','human')]:
  for unit in ['cation','scaffold']:cs+=paired(controlled[controlled.arm==aa],controlled[controlled.arm==bb],aa+' minus '+bb,unit)
 for unit in ['cation','scaffold']:
  cs+=paired(controlled[controlled.arm=='human'],pred[(pred.name=='matched_raw')&(pred.encoding=='categorical')],'human minus matched_raw',unit)
 pd.DataFrame(cs).to_csv(OUT/'contrasts.csv',index=False)
 modern=[];status={}
 for model in ['tabpfn','tabfm','autogluon']:
  folder=source/'modern'/model;status[model]=json.loads((folder/'status.json').read_text())
  if not status[model]['completed']:continue
  frame=pd.read_csv(folder/'predictions.csv');modern.append(frame)
 if modern:
  mp=pd.concat(modern,ignore_index=True);mp.to_csv(OUT/'modern_predictions.csv',index=False)
  metrics(mp,['model','representation','schema','cohort']).to_csv(OUT/'modern_metrics.csv',index=False)
 # Censored values remain separate from exact-endpoint loss.
 bound=pred[(pred.cohort=='OOD17')&(pred.qualifier!='=')].copy()
 bound['minimum_absolute_error']=np.maximum(bound.y-bound.prediction,0.)
 bound.to_csv(OUT/'censored_predictions.csv',index=False)
 manifest=dict(completed_core=True,compact_source_fits=30,decoder_fits=json.loads((source/'results/manifest.json').read_text())['fits'],
  modern_status=status,independent_original_fits=18,independent_prediction_max_difference=max(x['max_prediction_difference'] for x in verify),
  main_snapshot=str(source),independent_snapshot=str(other),seeds_averaged_as='Mean of per-seed RMSE, not ensemble predictions',
  CIs='Paired seed and molecule-cluster bootstrap; 10000 draws; pointwise 95%; all four endpoints retained per cluster',
  OOD_exact=67,OOD_censored=1,negative_delta='First configuration has lower RMSE',
  original_replay='Approximate: missing historical text cache and environment; restored saved encoder is not retrained',
  source_sha256={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 print('Compact categorical controls (mean of five source seeds):')
 print(summary[(summary.encoding=='categorical')&summary.arm.isin(['human','human_shuffled','mic_continuous','mic_binary','human_weight_only','initial','matched_raw'])&(summary.task=='pooled')][['arm','schema','RMSE','RMSE_sd']].to_string(index=False))
 print('Contrasts (cation clustering):')
 print(pd.DataFrame(cs).query("unit=='cation'")[['comparison','schema','delta_RMSE','ci_low','ci_high']].to_string(index=False))
 print('Modern status:',status)
if __name__=='__main__':main()
