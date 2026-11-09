"""Modern decoders on the saved v5 human/raw representations, fixed target folds."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
os.environ.setdefault('HF_HOME','/home/yagr/coma_models_check_20261012/runtime/hf')
os.environ.setdefault('HF_HUB_CACHE',os.environ['HF_HOME']+'/hub')
os.environ.setdefault('JAX_PLATFORMS','cpu')
os.environ.setdefault('XLA_FLAGS','--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=2')
from pathlib import Path
import argparse,importlib.util,json,time
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('baseline_helpers','/home/yagr/coma_models_check_20261012/run_baselines.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
TASKS=h.TASKS

def task_jobs():
 q=pd.read_csv(ROOT/'data/QAC105.csv')
 jobs=[]
 for rep in ['v5_raw','v5_human']:
  for schema,column in [('cation','fold'),('scaffold','scaffold_fold')]:
   for fold in range(5):
    tr=np.flatnonzero(q[column].to_numpy()!=fold);te=np.flatnonzero(q[column].to_numpy()==fold)
    for task in TASKS:jobs.append(dict(rep=rep,schema=schema,fold=fold,task=task,tr=tr,te=te))
  for task in TASKS:jobs.append(dict(rep=rep,schema='full-QAC105',fold=-1,task=task,tr=np.arange(105),te=np.arange(17)))
 return jobs

def run_task(model,job,shared=None):
 shared={} if shared is None else shared
 out=ROOT/'modern'/model;stem=job['rep']+'_'+job['schema']+'_'+str(job['fold'])+'_'+job['task']
 q=pd.read_csv(ROOT/'data/QAC105.csv');o=pd.read_csv(ROOT/'data/OOD17.csv')
 r=pd.read_csv(ROOT/'data/endpoint_registry.csv')
 qp=r[(r.cohort=='QAC105')&(r.task==job['task'])].sort_values('molecule_index')
 op=r[(r.cohort=='OOD17')&(r.task==job['task'])].sort_values('molecule_index')
 x=np.load(ROOT/'data'/(job['rep']+'_QAC105.npy'));xo=np.load(ROOT/'data'/(job['rep']+'_OOD17.npy'))
 OOD=job['schema']=='full-QAC105';tr,te=job['tr'],job['te']
 a,b,pre=h.transform_train_only(x[tr],xo[te] if OOD else x[te],True)
 groups=q.iloc[tr]['scaffold' if job['schema']=='scaffold' else 'cation'].to_numpy()
 start=time.time();prediction,info=h.table_prediction(model,a,qp.y.to_numpy()[tr],b,groups,out/'models'/stem,1729,shared)
 result=(op if OOD else qp).iloc[te].copy();result['prediction']=prediction
 result['representation']=job['rep'];result['schema']=job['schema'];result['fold']=job['fold'];result['model']=model;result['seed']=0
 result.to_csv(out/'chunks'/(stem+'.csv'),index=False)
 h.write_json(out/'chunks'/(stem+'.json'),dict(rep=job['rep'],schema=job['schema'],fold=job['fold'],task=job['task'],
              completed=True,n_train=len(tr),n_test=len(te),seconds=time.time()-start,model=model,info=info))
 return stem

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model',choices=['tabpfn','tabfm','autogluon']);a=ap.parse_args()
 out=ROOT/'modern'/a.model;(out/'chunks').mkdir(parents=True,exist_ok=True)
 jobs=task_jobs();done=0;shared={}
 h.write_json(out/'status.json',dict(completed=False,done=0,total=len(jobs)))
 def record(stem):
  nonlocal done
  done+=1;h.write_json(out/'status.json',dict(completed=False,done=done,total=len(jobs),last=stem));print(a.model,done,'/',len(jobs),stem,flush=True)
 if a.model=='autogluon':
  with ProcessPoolExecutor(max_workers=4) as pool:
   for f in as_completed([pool.submit(run_task,a.model,j) for j in jobs]):record(f.result())
 else:
  for job in jobs:record(run_task(a.model,job,shared))
 tables=[pd.read_csv(p) for p in sorted((out/'chunks').glob('*.csv'))]
 pd.concat(tables,ignore_index=True).to_csv(out/'predictions.csv',index=False)
 h.write_json(out/'manifest.json',dict(completed=True,fits=done,model=a.model,representations=['v5_raw','v5_human'],
     PCA=32,train_only_preprocessing=True,archived_source_overlap=True,source_training_seeds='one archived checkpoint',
     protocol='Same v15 model-specific budgets; each endpoint fitted separately; OOD excluded from all selection'))
 h.write_json(out/'status.json',dict(completed=True,done=done,total=len(jobs)))

if __name__=='__main__':main()
