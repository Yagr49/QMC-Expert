from pathlib import Path
import json
import numpy as np,pandas as pd
R=Path(__file__).resolve().parent;V=R.parent/'revision_v9';B=10000
MODELS=['molformer','c3-molformer','chemberta100m','chemfm1b']
def load():
    parts=[];metrics=[]
    original=V/'results_matched-pooled_matched-sa_full'
    d=pd.read_csv(original/'predictions.csv');d=d[d['head']=='catboost'].copy();d['backbone']='molformer';parts.append(d)
    m=pd.read_csv(original/'metrics.csv');m=m[m['head']=='catboost'].copy();m['backbone']='molformer';metrics.append(m)
    for folder in sorted(R.glob('results_*')):
        if not (folder/'manifest.json').exists():continue
        meta=json.loads((folder/'manifest.json').read_text());backbone=meta['backbone']
        for name,collection in [('predictions',parts),('metrics',metrics)]:
            d=pd.read_csv(folder/(name+'.csv'));d['backbone']=backbone;collection.append(d)
    keys=['backbone','panel','arm','seed','head','target']
    p=pd.concat(parts).drop_duplicates(keys+['can']);m=pd.concat(metrics).drop_duplicates(keys)
    return p,m
def contrast(sub,aa,bb):
    a=sub[sub.arm==aa].pivot(index='seed',columns='can',values='se').sort_index(axis=1)
    b=sub[sub.arm==bb].pivot(index='seed',columns='can',values='se').reindex(columns=a.columns)
    if len(a)==1 and len(b)==5:a=pd.DataFrame(np.repeat(a.values,5,axis=0),index=b.index,columns=a.columns)
    if len(b)==1 and len(a)==5:b=pd.DataFrame(np.repeat(b.values,5,axis=0),index=a.index,columns=a.columns)
    if len(a)!=5 or len(b)!=5:return []
    assert not a.isna().any().any() and not b.isna().any().any()
    g=sub.drop_duplicates('can').set_index('can').loc[a.columns].scaffold.values;ids=np.unique(g)
    A=np.stack([a.values[:,g==i].sum(1) for i in ids],axis=1);C=np.stack([b.values[:,g==i].sum(1) for i in ids],axis=1)
    sizes=np.array([(g==i).sum() for i in ids]);point=float(np.sqrt(a.values.mean())-np.sqrt(b.values.mean()));out=[]
    for nested in [False,True]:
        rng=np.random.default_rng(1729);ix=rng.integers(len(ids),size=(B,len(ids)))
        if nested:
            si=rng.integers(5,size=(B,5));sa=A[si].mean(1);sb=C[si].mean(1)
            da=np.take_along_axis(sa,ix,axis=1).sum(1);db=np.take_along_axis(sb,ix,axis=1).sum(1)
        else:da=A.mean(0)[ix].sum(1);db=C.mean(0)[ix].sum(1)
        delta=np.sqrt(da/sizes[ix].sum(1))-np.sqrt(db/sizes[ix].sum(1));lo,hi=np.quantile(delta,[.025,.975])
        leave=[]
        for j in range(len(ids)):
            mask=np.arange(len(ids))!=j;leave.append(float(np.sqrt(A[:,mask].sum()/5/sizes[mask].sum())-np.sqrt(C[:,mask].sum()/5/sizes[mask].sum())))
        out.append(dict(comparison=aa+' minus '+bb,n=len(a.columns),scaffolds=len(ids),seeds=5,unit='seed+scaffold' if nested else 'scaffold',delta_RMSE=point,ci_low=float(lo),ci_high=float(hi),leave_scaffold_min=min(leave),leave_scaffold_max=max(leave)))
    return out
def main():
    p,m=load();p['se']=(p.y-p.pred)**2
    summary=m.groupby(['backbone','panel','arm','target']).agg(seeds=('seed','nunique'),n=('n','first'),R2=('R2','mean'),R2_sd=('R2','std'),RMSE=('RMSE','mean'),RMSE_sd=('RMSE','std')).reset_index()
    summary.to_csv(R/'analysis/summary.csv',index=False);rows=[]
    for (model,panel,target),d in p[p.panel!='baseline'].groupby(['backbone','panel','target']):
        raw=p[(p.backbone==model)&(p.panel=='baseline')&(p.target==target)]
        sub=pd.concat([d,raw]);pairs=[('expert','expert-shuffled'),('expert','quant-continuous'),('expert','quant-binary'),('expert','untrained'),('expert','raw-'+model),('quant-continuous','quant-shuffled'),('quant-binary','quant-binary-shuffled'),('quant-binary-shuffled','expert-shuffled')]
        pairs.append(('quant-continuous','raw-'+model))
        if panel=='context':pairs=[('expert','expert-shuffled'),('expert','quant-pooled'),('expert','quant-sa'),('quant-pooled','quant-sa'),('quant-pooled','quant-pooled-shuffled'),('quant-sa','quant-sa-shuffled'),('expert','raw-molformer'),('quant-pooled','raw-molformer')]
        for a,b in pairs:
            if a not in set(sub.arm) or b not in set(sub.arm):continue
            for row in contrast(sub,a,b):rows.append(dict(backbone=model,panel=panel,target=target,**row))
    contrasts=pd.DataFrame(rows);contrasts.to_csv(R/'analysis/contrasts.csv',index=False)
    meta={'exploratory':True,'bootstrap_samples':B,'intervals':'unadjusted; fixed target folds; conditional scaffold and nested seed/scaffold sensitivity; five seeds are not independent datasets','completed_models':[name for name in MODELS if len(summary[(summary.backbone==name)&(summary.panel=='matched-pooled')&(summary.target=='Q-HERO-405')&(summary.seeds==5)])==7],'contrast_rows':len(contrasts)}
    (R/'analysis/meta.json').write_text(json.dumps(meta,indent=2))
    print(summary[summary.target=='Q-HERO-405'].to_string(index=False));print(contrasts[(contrasts.target=='Q-HERO-405')&(contrasts.unit=='seed+scaffold')].to_string(index=False))
if __name__=='__main__':main()
