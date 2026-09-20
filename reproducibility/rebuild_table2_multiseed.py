import numpy as np,pandas as pd,torch,torch.nn as nn,pickle,warnings;warnings.filterwarnings('ignore')
exec(open('/tmp/rebuild_t2.py').read().split('# long format pairs')[0])
base=target[['Molecular weight','LogP']].values.astype(np.float32)
for k in list(E): E[k]=np.hstack([E[k],base])
rows=[]
for i in range(len(target)):
    for tc in TC:
        v=target[tc].iloc[i]
        if pd.notna(v) and v>0:
            org='S. aureus' if 'aureus' in tc else 'E. coli'
            rows.append(dict(mol=i,org=org,met='MIC' if 'MIC' in tc else 'MBC',
                             ep=f"{org} {'MIC' if 'MIC' in tc else 'MBC'}",y=np.log2(float(v))))
P=pd.DataFrame(rows)
from sklearn.model_selection import train_test_split,GroupShuffleSplit
from sklearn.metrics import r2_score,mean_squared_error
from catboost import CatBoostRegressor
def onehot(P): return np.column_stack([(P.org=='S. aureus').astype(float),(P.org=='E. coli').astype(float),(P.met=='MIC').astype(float),(P.met=='MBC').astype(float)])
def run(emb,mode,split,seed):
    X=emb[P.mol.values]
    if mode=='multitask': X=np.hstack([X,onehot(P)])
    y=P.y.values
    if split=='pairs': tr,te=train_test_split(np.arange(len(P)),test_size=.2,random_state=seed)
    else: tr,te=next(GroupShuffleSplit(1,test_size=.2,random_state=seed).split(X,y,groups=P.mol.values))
    m=CatBoostRegressor(iterations=1000,learning_rate=0.05,depth=6,random_seed=seed,verbose=0)
    m.fit(X[tr],y[tr]);pr=m.predict(X[te])
    return {ep:r2_score(y[te][P.ep.values[te]==ep],pr[P.ep.values[te]==ep]) for ep in ['S. aureus MIC','S. aureus MBC','E. coli MIC','E. coli MBC']}
EPS=['S. aureus MIC','S. aureus MBC','E. coli MIC','E. coli MBC']
for split in ['pairs','mol']:
    print(f'\n===== +MW/LogP, multitask, split={split}, mean R2 over 10 seeds =====')
    print(f'{"embeddings":20s}'+''.join(f'{e:>18s}' for e in EPS))
    for name,emb in E.items():
        R=np.array([[run(emb,'multitask',split,s)[ep] for ep in EPS] for s in range(10)])
        print(f'{name:20s}'+''.join(f'{R[:,j].mean():10.2f}±{R[:,j].std():5.2f}' for j in range(4)))
