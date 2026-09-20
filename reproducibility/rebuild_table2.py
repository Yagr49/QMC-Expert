import numpy as np, pandas as pd, torch, torch.nn as nn, pickle, warnings, os
warnings.filterwarnings('ignore')
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from catboost import CatBoostRegressor
V='/Users/egorilin/Desktop/Veresh_paper'; C='/Users/egorilin/Desktop/COMA'
RS=42; TEST=0.2
CB=dict(iterations=1000,learning_rate=0.05,depth=6,random_seed=RS,verbose=0)

target=pd.read_excel(f'{V}/Data_biocides.xlsx')
mf=pd.read_excel(f'{V}/Test_molformer_original_biocides.xlsx').drop(['Unnamed: 0'],axis=1)
TC=[c for c in target.columns if 'Activity' in c]
print('targets:',TC); print('molformer:',mf.shape)

class Enc(nn.Module):
    def __init__(s,inp=768,h=[512,384,256],pd_=128,dr=0.3):
        super().__init__(); L=[];p=inp
        for d in h: L+=[nn.Linear(p,d),nn.BatchNorm1d(d),nn.ReLU(),nn.Dropout(dr)];p=d
        s.encoder=nn.Sequential(*L)
        s.projection_head=nn.Sequential(nn.Linear(h[-1],pd_),nn.BatchNorm1d(pd_),nn.ReLU(),
                                        nn.Dropout(dr*.5),nn.Linear(pd_,pd_),nn.BatchNorm1d(pd_))
    def forward(s,x): return s.encoder(x)

scaler=pickle.load(open(f'{V}/scaler_classification.pkl','rb'))
Xs=scaler.transform(mf)
def embed(path):
    e=Enc(); e.load_state_dict(torch.load(path,map_location='cpu')); e.eval()
    with torch.no_grad(): return e(torch.FloatTensor(Xs)).numpy()
E={'human (Good/Bad)':embed(f'{V}/encoder_borderline_smote.pth'),
   'multi-regression':embed(f'{C}/analysis/encoder_reg_only.pth'),
   'MolFormer (raw)':mf.values.astype(np.float32)}
for k,v in E.items(): print(f'  {k}: {v.shape}')

# long format pairs
rows=[]
for i in range(len(target)):
    for tc in TC:
        v=target[tc].iloc[i]
        if pd.notna(v) and v>0:
            org='S. aureus' if 'aureus' in tc else 'E. coli'
            met='MIC' if 'MIC' in tc else 'MBC'
            rows.append(dict(mol=i,org=org,met=met,ep=f'{org} {met}',y=np.log2(float(v))))
P=pd.DataFrame(rows); print('pairs:',len(P),'| molecules:',P.mol.nunique())

def onehot(P):
    return np.column_stack([(P.org=='S. aureus').astype(float),(P.org=='E. coli').astype(float),
                            (P.met=='MIC').astype(float),(P.met=='MBC').astype(float)])
def run(emb,mode,split):
    X=emb[P.mol.values]
    if mode=='multitask': X=np.hstack([X,onehot(P)])
    y=P.y.values
    if split=='pairs':
        tr,te=train_test_split(np.arange(len(P)),test_size=TEST,random_state=RS)
    else:
        tr,te=next(GroupShuffleSplit(n_splits=1,test_size=TEST,random_state=RS).split(X,y,groups=P.mol.values))
    m=CatBoostRegressor(**CB); m.fit(X[tr],y[tr]); pr=m.predict(X[te])
    out={}
    for ep in ['S. aureus MIC','S. aureus MBC','E. coli MIC','E. coli MBC']:
        msk=P.ep.values[te]==ep
        if msk.sum()<3: out[ep]=(np.nan,np.nan,int(msk.sum())); continue
        out[ep]=(np.sqrt(mean_squared_error(y[te][msk],pr[msk])),r2_score(y[te][msk],pr[msk]),int(msk.sum()))
    return out

for split,lbl in [('pairs','A. SPLIT BY PAIRS  (protocol of the notebook = current paper)'),
                  ('mol','B. SPLIT BY MOLECULE  (no molecule in both train and test)')]:
    print('\n'+'='*104); print(lbl); print('='*104)
    print(f'{"embeddings":20s} {"setting":12s}'+''.join(f'{e:>18s}' for e in ['S.aureus MIC','S.aureus MBC','E.coli MIC','E.coli MBC']))
    for name,emb in E.items():
        for mode in ['plain','multitask']:
            r=run(emb,mode,split)
            line=f'{name:20s} {mode:12s}'
            for ep in ['S. aureus MIC','S. aureus MBC','E. coli MIC','E. coli MBC']:
                rm,r2,n=r[ep]
                line+=f'{rm:8.2f} (R2={r2:5.2f})' if not np.isnan(rm) else f'{"n/a":>18s}'
            print(line)
    print(f'  (n_test per endpoint: '+', '.join(f'{ep}={run(E["MolFormer (raw)"],"plain",split)[ep][2]}' for ep in ['S. aureus MIC','E. coli MIC'])+')')
