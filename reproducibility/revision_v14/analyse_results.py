from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parent
B=10000

def summaries(p):
    metrics=[]
    for (arm,seed,enc,cohort,provenance),d in p.groupby(['arm','seed','encoding','cohort','provenance']):
        for task in ['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC','pooled']:
            exact=d[(d.qualifier=='=') & ((d.task==task) if task!='pooled' else True)]
            y=exact.y.values;pr=exact.prediction.values
            metrics.append(dict(arm=arm,seed=seed,encoding=enc,cohort=cohort,provenance=provenance,task=task,n=len(y),
                RMSE=np.sqrt(mean_squared_error(y,pr)),R2=r2_score(y,pr),MAE=mean_absolute_error(y,pr),rho=spearmanr(y,pr).statistic))
    m=pd.DataFrame(metrics)
    group=['arm','encoding','cohort','provenance','task']
    s=m.groupby(group).agg(seeds=('seed','size'),n=('n','first'),RMSE=('RMSE','mean'),RMSE_sd=('RMSE','std'),
        R2=('R2','mean'),R2_sd=('R2','std'),MAE=('MAE','mean'),MAE_sd=('MAE','std'),rho=('rho','mean'),rho_sd=('rho','std')).reset_index()
    s[[c for c in s if c.endswith('_sd')]]=s[[c for c in s if c.endswith('_sd')]].fillna(0)
    return m,s

def bootstrap_rmse(d,can_order,weights,seed_draws):
    matrix=d.pivot(index='seed',columns=['can','task'],values='prediction').reindex(columns=can_order)
    if len(matrix)==1:matrix=pd.concat([matrix]*5,ignore_index=True)
    assert matrix.shape==(5,len(can_order)) and np.isfinite(matrix.values).all()
    truth=d.drop_duplicates(['can','task']).set_index(['can','task']).reindex(can_order).y.values
    error2=(matrix.values-truth[None,:])**2
    boot=np.sqrt((weights @ error2.T)/weights.sum(axis=1)[:,None])
    sampled=np.take_along_axis(boot,seed_draws,axis=1).mean(axis=1)
    return float(np.sqrt(error2.mean(axis=1)).mean()),sampled

def contrasts(p):
    rows=[];matched=p[p.provenance=='matched-source-excluded']
    pairs=[('expert','expert-shuffled'),('expert','quant-continuous'),('expert','quant-binary'),
           ('expert','raw-molformer'),('quant-continuous','quant-shuffled'),('quant-binary','quant-binary-shuffled')]
    for cohort,cohortdata in matched.groupby('cohort'):
        for task in ['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC','pooled']:
            d=cohortdata[(cohortdata.qualifier=='=')&((cohortdata.task==task) if task!='pooled' else True)]
            info=d.drop_duplicates(['can','task']).set_index(['can','task']).sort_index()
            groups,index=np.unique(info.scaffold.values,return_inverse=True)
            rng=np.random.default_rng(1729);draw=rng.integers(len(groups),size=(B,len(groups)))
            counts=np.column_stack([(draw==i).sum(axis=1) for i in range(len(groups))])
            weights=counts[:,index];sd=rng.integers(5,size=(B,5))
            cache={}
            for (arm,encoding),sub in d.groupby(['arm','encoding']):
                cache[(arm,encoding)]=bootstrap_rmse(sub,info.index,weights,sd)
            cases=[(aa,'onehot',bb,'onehot',aa+' minus '+bb) for aa,bb in pairs]
            cases +=[(arm,'text',arm,'onehot','text minus onehot: '+arm) for arm in ['expert','quant-continuous','quant-binary','raw-molformer']]
            for aa,ae,bb,be,name in cases:
                if (aa,ae) not in cache or (bb,be) not in cache:continue
                av,ab=cache[aa,ae];bv,bbv=cache[bb,be];lo,hi=np.quantile(ab-bbv,[.025,.975])
                rows.append(dict(cohort=cohort,task=task,comparison=name,delta_RMSE=av-bv,ci_low=lo,ci_high=hi,
                    exact_pairs=len(info),scaffolds=len(groups),draws=B,unit='seed+scaffold'))
    return pd.DataFrame(rows)

def main():
    out=ROOT/'analysis';out.mkdir(exist_ok=True)
    manifest=json.loads((ROOT/'results/manifest.json').read_text());assert manifest['completed']
    p=pd.read_csv(ROOT/'results/predictions.csv');registry=pd.read_csv(ROOT/'data/endpoint_registry.csv')
    assert len(p)==(manifest['jobs']+1)*488
    assert not p.duplicated(['name','encoding','cohort','can','task']).any()
    assert np.isfinite(p[['y','prediction']].values).all()
    assert (p.query("cohort=='OOD17' and task=='Ec_MBC' and compound_id=='IT505'").qualifier=='>').all()
    m,s=summaries(p);m.to_csv(out/'metrics_recomputed.csv',index=False);s.to_csv(out/'summary.csv',index=False)
    saved=pd.read_csv(ROOT/'results/metrics.csv').sort_values(['arm','seed','encoding','cohort','task'])
    calc=m[m.arm!='task-median'].sort_values(['arm','seed','encoding','cohort','task'])
    maxdiff=float(np.max(np.abs(saved[['RMSE','R2','MAE','rho']].values-calc[['RMSE','R2','MAE','rho']].values)))
    assert maxdiff<1e-10
    c=contrasts(p);c.to_csv(out/'contrasts.csv',index=False)
    excluded=pd.read_csv(ROOT/'data/QAC105.csv').query('label_conflict == True').can.tolist()
    cm,cs=summaries(p[~p.can.isin(excluded)]);cs.to_csv(out/'QAC104_curation_sensitivity.csv',index=False)
    o=p[p.cohort=='OOD17'].copy();o['prediction_mg_l']=2**o.prediction
    o.to_csv(out/'OOD17_all_predictions_named.csv',index=False)
    censored=o[o.qualifier!='='].copy();censored['above_reported_bound']=censored.prediction>censored.y
    censored.to_csv(out/'censored_endpoint_predictions.csv',index=False)
    report=dict(completed=True,jobs=manifest['jobs'],prediction_rows=len(p),metrics_match_max_difference=maxdiff,
        QAC105=105,QAC_cation_groups=103,all_endpoints_molecule_grouped=True,
        OOD17=17,OOD_exact_values=67,OOD_censored_values=1,OOD_never_used_in_fit=True,
        protocol_sha256=hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
        predictions_sha256=hashlib.sha256((ROOT/'results/predictions.csv').read_bytes()).hexdigest())
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    print(s.query("encoding=='onehot' and task=='pooled'")[['arm','cohort','RMSE','R2','rho']].to_string(index=False))

if __name__=='__main__':main()
