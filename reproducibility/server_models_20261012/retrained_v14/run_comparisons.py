"""Fixed cation-grouped QAC CV and untouched OOD prediction, all tasks."""
from pathlib import Path
import os
for var in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[var]='2'
import json, time, hashlib, platform
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parent
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']

def decoder(x,y,test):
    model=CatBoostRegressor(iterations=300,depth=5,learning_rate=.05,random_seed=1729,
        thread_count=2,verbose=False,allow_writing_files=False)
    model.fit(x,y);return model.predict(test)

def design(vectors,pairs,mode):
    x=vectors[pairs.molecule_index.values]
    if mode=='onehot':
        idx=np.asarray([TASKS.index(t) for t in pairs.task])
        metadata=np.column_stack([idx<2,idx>=2,idx%2==0,idx%2==1]).astype(np.float32)
        x=np.hstack([x,metadata])
    elif mode=='text':
        metadata=np.load(ROOT/'data/task_text_embeddings.npy')[[TASKS.index(t) for t in pairs.task]]
        x=np.hstack([x,metadata])
    return x

def run(configuration,encoding):
    registry=pd.read_csv(ROOT/'data/endpoint_registry.csv')
    q=registry[registry.cohort=='QAC105'].reset_index(drop=True)
    o=registry[registry.cohort=='OOD17'].reset_index(drop=True)
    x=design(np.load(ROOT/'representations'/(configuration['name']+'_QAC105.npy')),q,encoding)
    xo=design(np.load(ROOT/'representations'/(configuration['name']+'_OOD17.npy')),o,encoding)
    pred=np.full(len(q),np.nan);po=np.full(len(o),np.nan)
    for task in TASKS if encoding=='separate' else ['all']:
        select=np.ones(len(q),dtype=bool) if task=='all' else q.task.values==task
        osel=np.ones(len(o),dtype=bool) if task=='all' else o.task.values==task
        for fold in sorted(q.fold.unique()):
            tr=select&(q.fold.values!=fold);te=select&(q.fold.values==fold)
            assert not set(q.cation[tr])&set(q.cation[te])
            assert not set(q.can[tr])&set(q.can[te])
            pred[te]=decoder(x[tr],q.y.values[tr],x[te])
        po[osel]=decoder(x[select],q.y.values[select],xo[osel])
    assert np.isfinite(pred).all() and np.isfinite(po).all()
    rows=[];metrics=[]
    for df,pr in [(q,pred),(o,po)]:
        output=df.copy();output['prediction']=pr
        for k,v in configuration.items():
            if k!='encodings':output[k]=v
        output['encoding']=encoding;rows.append(output)
        for task in TASKS+['pooled']:
            subset=np.ones(len(df),dtype=bool) if task=='pooled' else df.task.values==task
            subset&=df.qualifier.values=='='
            y=df.y.values[subset];p=pr[subset]
            metrics.append(dict(name=configuration['name'],arm=configuration['arm'],seed=configuration['seed'],
                provenance=configuration['provenance'],encoding=encoding,cohort=df.cohort.iloc[0],task=task,n=len(y),
                RMSE=float(np.sqrt(mean_squared_error(y,p))),R2=float(r2_score(y,p)),
                MAE=float(mean_absolute_error(y,p)),rho=float(spearmanr(y,p).statistic)))
    return pd.concat(rows,ignore_index=True),metrics

def baseline():
    registry=pd.read_csv(ROOT/'data/endpoint_registry.csv');q=registry[registry.cohort=='QAC105'].copy();o=registry[registry.cohort=='OOD17'].copy()
    for task in TASKS:
        for fold in q.fold.unique():
            q.loc[(q.task==task)&(q.fold==fold),'prediction']=q.loc[(q.task==task)&(q.fold!=fold),'y'].median()
        o.loc[o.task==task,'prediction']=q.loc[q.task==task,'y'].median()
    d=pd.concat([q,o]);d['name']='task-median';d['arm']='task-median';d['seed']=-1;d['encoding']='baseline';d['provenance']='target-training-only'
    return d

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True);start=time.time()
    jobs=[(c,e) for c in json.loads((ROOT/'data/configurations.json').read_text()) for e in c['encodings']]
    manifest=dict(started=start,completed=False,jobs=len(jobs),protocol_sha256=hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
        python=platform.python_version(),thread_count=2,workers=6,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*') if p.is_file()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    allpred=[];allmetrics=[]
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(run,c,e):(c['name'],e) for c,e in jobs}
        for future in as_completed(futures):
            name,encoding=futures[future];pred,metrics=future.result();allpred.append(pred);allmetrics+=metrics
            pred.to_csv(out/(name+'_'+encoding+'_predictions.csv'),index=False)
            pd.DataFrame(allmetrics).to_csv(out/'metrics.csv',index=False)
            (out/'progress.json').write_text(json.dumps(dict(done=len(allpred),total=len(jobs),elapsed_s=time.time()-start)))
            print('COMPLETED',len(allpred),'/',len(jobs),name,encoding,'elapsed',round(time.time()-start),flush=True)
    allpred.append(baseline());pd.concat(allpred,ignore_index=True).to_csv(out/'predictions.csv',index=False)
    manifest.update(completed=True,elapsed_s=time.time()-start,prediction_rows=sum(len(d) for d in allpred))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('DONE',json.dumps(manifest),flush=True)

if __name__=='__main__':main()
