"""Analyse paired predictions; preserve molecular and seed dependence."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'analysis'
OUT.mkdir(exist_ok=True)
B=10000

def intervals(a,b,groups=None):
    """a,b: matched squared-error matrices, rows=seeds, columns=molecules."""
    point=float(np.sqrt(a.mean())-np.sqrt(b.mean()))
    rng=np.random.default_rng(1729)
    n=a.shape[1]
    av,bv=a.mean(axis=0),b.mean(axis=0)
    if groups is None:
        idx=rng.integers(0,n,size=(B,n))
        ds=np.sqrt(av[idx].mean(axis=1))-np.sqrt(bv[idx].mean(axis=1))
    else:
        ids=np.unique(groups)
        sums_a=np.array([av[groups==g].sum() for g in ids]);sums_b=np.array([bv[groups==g].sum() for g in ids])
        sizes=np.array([(groups==g).sum() for g in ids]);idx=rng.integers(0,len(ids),size=(B,len(ids)))
        ds=np.sqrt(sums_a[idx].sum(axis=1)/sizes[idx].sum(axis=1))-np.sqrt(sums_b[idx].sum(axis=1)/sizes[idx].sum(axis=1))
    lo,hi=np.quantile(ds,[.025,.975])
    return point,float(lo),float(hi)

def main():
    dirs=[p for p in ROOT.glob('results_*') if (p/'predictions.csv').exists()]
    df=pd.concat([pd.read_csv(p/'predictions.csv') for p in dirs],ignore_index=True)
    df=df.drop_duplicates(['panel','arm','seed','head','target','can'])
    metrics=pd.concat([pd.read_csv(p/'metrics.csv') for p in dirs],ignore_index=True).drop_duplicates(['panel','arm','seed','head','target'])
    summary=metrics.groupby(['panel','arm','head','target']).agg(seeds=('seed','nunique'),n=('n','first'),R2=('R2','mean'),R2_sd=('R2','std'),RMSE=('RMSE','mean'),RMSE_sd=('RMSE','std')).reset_index()
    summary.to_csv(OUT/'summary.csv',index=False)
    df['se']=(df.y-df.pred)**2
    rows=[]
    for panel in ['matched-pooled','matched-sa']:
      for head in ['catboost','ridge']:
       for target in ['QAC-104','Q-HERO-405','OOD-17']:
        sub=df[(df.panel==panel)&(df['head']==head)&(df.target==target)]
        for comparator in ['quant-continuous','quant-binary','expert-shuffled','quant-shuffled','untrained','raw-molformer']:
            e=sub[sub.arm=='expert'];c=(df[(df.panel=='baseline')&(df['head']==head)&(df.target==target)] if comparator=='raw-molformer' else sub[sub.arm==comparator])
            aa=e.pivot(index='seed',columns='can',values='se').sort_index(axis=1)
            bb=c.pivot(index='seed',columns='can',values='se').sort_index(axis=1)
            if comparator=='raw-molformer' and len(bb)==1:bb=pd.DataFrame(np.repeat(bb.values,len(aa),axis=0),index=aa.index,columns=bb.columns)
            common=aa.index.intersection(bb.index)
            if len(common)!=5: continue
            assert aa.columns.tolist()==bb.columns.tolist()
            a,b=aa.loc[common].values,bb.loc[common].values
            groups=e.drop_duplicates('can').set_index('can').loc[aa.columns].scaffold.values
            for unit,gg in [('molecule',None),('scaffold',groups)]:
                point,lo,hi=intervals(a,b,gg)
                rows.append(dict(panel=panel,head=head,target=target,comparison=f'expert minus {comparator}',seeds=len(common),n=len(aa.columns),unit=unit,delta_RMSE=point,ci_low=lo,ci_high=hi))
    paired=pd.DataFrame(rows);paired.to_csv(OUT/'paired_bootstrap.csv',index=False)
    # Direct expert ranking is independently supported by existing FT predictions.
    old=pd.read_csv(ROOT.parents[0]/'finetune/predictions_seed0.csv')
    rank=[]
    for target,d in old[old.source=='expert-binary'].groupby('target'):
        # Expert logit increases with Good; lower MIC indicates greater potency.
        rho=float(spearmanr(-d.pred,d.y).statistic)
        rng=np.random.default_rng(1729);samples=[]
        for _ in range(B):
            ix=rng.integers(0,len(d),len(d));r=spearmanr(-d.pred.values[ix],d.y.values[ix]).statistic
            if np.isfinite(r):samples.append(r)
        lo,hi=np.quantile(samples,[.025,.975]);rank.append(dict(target=target,n=len(d),seed=0,rho=rho,ci_low=float(lo),ci_high=float(hi),unit='molecule; conditional on one FT checkpoint'))
    pd.DataFrame(rank).to_csv(OUT/'archived_direct_expert_rank.csv',index=False)
    payload={'primary_metric':'CatBoost scaffold-held-out Q-HERO-405 paired RMSE; log2 uM',
             'bootstrap_samples':B,'uncertainty':'molecule and scaffold intervals condition on five trained source seeds; scaffold folds fixed; seeds are not five independent datasets',
             'negative_controls':'five paired initialization seeds, not a permutation test with multiple shuffled label realizations',
             'complete': all(len(metrics[(metrics.panel==p)&(metrics.arm==a)].seed.unique())==5 for p in ['matched-pooled','matched-sa'] for a in ['expert','quant-continuous','quant-binary','expert-shuffled','quant-shuffled','untrained']) and all(len(metrics[(metrics.panel=='full')&(metrics.arm==a)].seed.unique())==5 for a in ['expert-full','quant-pooled-full','quant-sa-full','quant-iltox-full'])}
    (OUT/'analysis_meta.json').write_text(json.dumps(payload,indent=2))
    print(summary[(summary['head']=='catboost')&(summary.target=='Q-HERO-405')].to_string(index=False))
    print(paired[(paired['head']=='catboost')&(paired.target=='Q-HERO-405')&(paired.unit=='scaffold')].to_string(index=False))
    print('COMPLETE',payload['complete'])

if __name__=='__main__':main()
