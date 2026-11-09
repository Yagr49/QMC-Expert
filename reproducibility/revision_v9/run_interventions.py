"""Matched computational interventions on archived/frozen molecular features."""
import os
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import json, argparse, copy, hashlib, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from catboost import CatBoostRegressor
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'

class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(768,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU())
        self.head=nn.Linear(128,1)
    def forward(self,x): return self.head(self.encoder(x)).squeeze(-1)

def features(df,x,index): return x[[index[s] for s in df.can]]

def decoder(head):
    if head=='ridge': return Ridge(alpha=10)
    return CatBoostRegressor(iterations=300,depth=5,learning_rate=.05,random_seed=1729,
                             thread_count=4,verbose=False,allow_writing_files=False)

def fit_predict(head,xtr,ytr,xte):
    # The linear decoder's scaler is always fitted on target train, never target test.
    sc=StandardScaler().fit(xtr) if head=='ridge' else None
    m=decoder(head)
    m.fit(sc.transform(xtr) if sc else xtr,ytr)
    return m.predict(sc.transform(xte) if sc else xte)

def evaluate(reps,targets,folds,head):
    results={}
    for name in ['QAC-104','Q-HERO-405']:
        d=targets[name];x=reps[name];pred=np.zeros(len(d))
        for tr,te in folds[name]:pred[te]=fit_predict(head,x[tr],d.y.values[tr],x[te])
        results[name]=pred
    results['OOD-17']=fit_predict(head,reps['QAC-104'],targets['QAC-104'].y.values,reps['OOD-17'])
    return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--panels',nargs='+',default=['matched-pooled','matched-sa','full'])
    ap.add_argument('--device',default='auto');ap.add_argument('--seeds',type=int,default=5)
    ap.add_argument('--fold-file',type=Path,help='Reuse archived target identities/folds across environments')
    ap.add_argument('--output-dir',type=Path,help='Keep independent reproduction separate from original results')
    ap.add_argument('--heads',nargs='+',choices=['ridge','catboost'],default=['ridge','catboost'])
    ap.add_argument('--arms',nargs='+',help='Optional subset for independent checks')
    a=ap.parse_args();torch.set_num_threads(4)
    dev=torch.device('cuda' if a.device=='auto' and torch.cuda.is_available() else ('cpu' if a.device=='auto' else a.device))
    out=a.output_dir or ROOT/('results_'+'_'.join(a.panels));out.mkdir(parents=True,exist_ok=True)
    x=np.load(DATA/'molformer.npy');smis=json.loads((DATA/'smiles.json').read_text());index={s:i for i,s in enumerate(smis)}
    targets={n:pd.read_csv(DATA/f'target_{n}.csv') for n in ['QAC-104','Q-HERO-405','OOD-17']}
    folds={n:list(GroupKFold(n_splits=5).split(d,groups=d.scaffold)) for n,d in targets.items() if n!='OOD-17'}
    if a.fold_file:
        assignments=pd.read_csv(a.fold_file)
        for name in folds:
            d=targets[name];f=assignments[assignments.target==name].set_index('can')
            assert f.index.is_unique and set(f.index)==set(d.can)
            labels=f.loc[d.can,'fold'].values
            folds[name]=[(np.flatnonzero(labels!=k),np.flatnonzero(labels==k)) for k in sorted(set(labels))]
    fold_rows=[]
    for name,parts in folds.items():
        for k,(tr,te) in enumerate(parts):
            assert not set(targets[name].iloc[tr].scaffold)&set(targets[name].iloc[te].scaffold)
            fold_rows.extend({'target':name,'can':targets[name].can.iloc[i],'fold':k} for i in te)
    pd.DataFrame(fold_rows).to_csv(out/'target_folds.csv',index=False)
    manifest={'device':str(dev),'torch':torch.__version__,'epochs':80,'seeds':a.seeds,
              'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
              'features_sha256':hashlib.sha256((DATA/'molformer.npy').read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'heads':a.heads,'arms':a.arms,
              'fixed_folds_sha256':hashlib.sha256(a.fold_file.read_bytes()).hexdigest() if a.fold_file else None}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    metrics=[];predictions=[];train_rows=[]
    def record(panel,arm,seed,reps):
        for head in a.heads:
            pp=evaluate(reps,targets,folds,head)
            for name,p in pp.items():
                d=targets[name]
                metrics.append(dict(panel=panel,arm=arm,seed=seed,head=head,target=name,n=len(d),
                                    R2=r2_score(d.y,p),RMSE=np.sqrt(mean_squared_error(d.y,p))))
                predictions.extend(dict(panel=panel,arm=arm,seed=seed,head=head,target=name,
                                        can=d.can.iloc[i],scaffold=d.scaffold.iloc[i],y=d.y.iloc[i],pred=float(p[i])) for i in range(len(d)))
        pd.DataFrame(metrics).to_csv(out/'metrics.csv',index=False)
        pd.DataFrame(predictions).to_csv(out/'predictions.csv',index=False)
        print(panel,arm,seed,[(m['target'],m['head'],round(m['RMSE'],3)) for m in metrics[-6:]],flush=True)
    record('baseline','raw-molformer',0,{n:features(d,x,index) for n,d in targets.items()})
    for panel in a.panels:
        if panel=='full':
            experiments=[(name,pd.read_csv(DATA/f'source_{name}.csv')) for name in ['expert-full','quant-pooled-full','quant-sa-full','quant-iltox-full']]
        else:
            e=pd.read_csv(DATA/f'{panel}_expert.csv');q=pd.read_csv(DATA/f'{panel}_quant.csv')
            assert e.can.tolist()==q.can.tolist() and e.scaffold.tolist()==q.scaffold.tolist()
            experiments=[('expert',e),('quant-continuous',q),('quant-binary',q),('expert-shuffled',e),('quant-shuffled',q),('untrained',e)]
        if a.arms:experiments=[(name,df) for name,df in experiments if name in a.arms]
        for seed in range(a.seeds):
            for arm,df in experiments:
                torch.manual_seed(seed);np.random.seed(seed)
                tr,va=next(GroupShuffleSplit(n_splits=1,test_size=.15,random_state=1729).split(df,groups=df.scaffold))
                assert not set(df.iloc[tr].scaffold)&set(df.iloc[va].scaffold)
                sc=StandardScaler().fit(features(df.iloc[tr],x,index))
                xx=sc.transform(features(df,x,index)).astype('float32')
                y=df.y.values.astype('float32').copy()
                binary=arm.startswith('expert') or (panel!='full' and arm=='untrained')
                cutoff=None
                if arm=='quant-binary':
                    prevalence=float(e.y.values[tr].mean())
                    cutoff=float(np.quantile(y[tr],prevalence))
                    y=(y<=cutoff).astype('float32');binary=True
                if not binary:
                    mu=float(y[tr].mean());sd=max(float(y[tr].std()),1e-6);y=(y-mu)/sd
                if arm in ['expert-shuffled','quant-shuffled']:
                    rng=np.random.default_rng(100000+seed);y[tr]=rng.permutation(y[tr])
                net=Encoder().to(dev)
                initial_hash=hashlib.sha256(b''.join(v.detach().cpu().numpy().tobytes() for v in net.state_dict().values())).hexdigest()
                xt=torch.tensor(xx[tr],device=dev);yt=torch.tensor(y[tr],device=dev)
                opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.01)
                lossfn=nn.BCEWithLogitsLoss() if binary else nn.MSELoss()
                start=time.time()
                if arm!='untrained':
                    for ep in range(80):
                        net.train();perm=torch.randperm(len(tr),device=dev)
                        for k in range(0,len(tr),64):
                            ii=perm[k:k+64];opt.zero_grad();loss=lossfn(net(xt[ii]),yt[ii]);loss.backward();opt.step()
                net.eval()
                with torch.no_grad():
                    val_loss=float(lossfn(net(torch.tensor(xx[va],device=dev)),torch.tensor(y[va],device=dev)).cpu())
                    reps={n:net.encoder(torch.tensor(sc.transform(features(d,x,index)).astype('float32'),device=dev)).cpu().numpy() for n,d in targets.items()}
                train_rows.append(dict(panel=panel,arm=arm,seed=seed,n=len(df),train=len(tr),validation=len(va),
                                       init_sha256=initial_hash,train_identity_sha256=hashlib.sha256('\n'.join(df.can.iloc[tr]).encode()).hexdigest(),
                                       positive_prevalence=float(y[tr].mean()) if binary else None,binary_cutoff=cutoff,val_loss=val_loss,seconds=time.time()-start))
                pd.DataFrame(train_rows).to_csv(out/'training.csv',index=False)
                record(panel,arm,seed,reps)
    print('DONE',flush=True)

if __name__=='__main__':main()
