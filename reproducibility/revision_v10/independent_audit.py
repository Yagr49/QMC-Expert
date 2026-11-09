from pathlib import Path
import numpy as np,pandas as pd,json
R=Path(__file__).resolve().parent
p=pd.read_csv(R/'predictions.csv');m=pd.read_csv(R/'metrics.csv')
rows=[]
for keys,d in p.groupby(['panel','arm','seed','head','target']):
    mse=float(((d.y-d.pred)**2).mean());r2=1-mse/float(((d.y-d.y.mean())**2).mean())
    z=m[(m.panel==keys[0])&(m.arm==keys[1])&(m.seed==keys[2])&(m['head']==keys[3])&(m.target==keys[4])].iloc[0]
    errors=[abs(np.sqrt(mse)-z.RMSE),abs(r2-z.R2)]
    assert np.isclose(np.sqrt(mse),z.RMSE,rtol=1e-11,atol=1e-8) and np.isclose(r2,z.R2,rtol=1e-11,atol=1e-8)
    rows.append(max(errors))

s=p[(p.panel=='matched-pooled')&(p['head']=='catboost')&(p.target=='Q-HERO-405')].copy();s['se']=(s.y-s.pred)**2
pairs=[]
for aa,bb in [('expert','expert-shuffled'),('expert','quant-continuous'),('quant-continuous','quant-shuffled')]:
    a=s[s.arm==aa].pivot(index='seed',columns='can',values='se');b=s[s.arm==bb].pivot(index='seed',columns='can',values='se').reindex(columns=a.columns)
    g=s.drop_duplicates('can').set_index('can').loc[a.columns].scaffold.values;ids=np.unique(g)
    av=a.values.mean(0);bv=b.values.mean(0);sizes=np.array([(g==k).sum() for k in ids]);sa=np.array([av[g==k].sum() for k in ids]);sb=np.array([bv[g==k].sum() for k in ids]);ix=np.random.default_rng(1729).integers(len(ids),size=(10000,len(ids)))
    delta=np.sqrt(sa[ix].sum(1)/sizes[ix].sum(1))-np.sqrt(sb[ix].sum(1)/sizes[ix].sum(1));ci=np.quantile(delta,[.025,.975])
    pairs.append({'comparison':aa+' minus '+bb,'delta':float(np.sqrt(av.mean())-np.sqrt(bv.mean())),'ci':ci.tolist(),'scaffolds':len(ids)})
result={'metric_rows':len(rows),'prediction_rows':len(p),'max_metric_error':max(rows),'numpy':np.__version__,'pandas':pd.__version__,'paired_scaffold_audit':pairs}
(R/'independent_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
