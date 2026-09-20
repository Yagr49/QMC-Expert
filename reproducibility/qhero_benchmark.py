"""Q-HERO external benchmark: expert vs multi-regression vs raw MolFormer.

Q-HERO is the only available QAC collection with a matched S. aureus MIC endpoint
that is essentially disjoint from the QAC-105 in-domain benchmark (overlap = 1).
It DOES overlap the expert-labelled training set by 222 molecules, so the honest
evaluation is restricted to the Q-HERO molecules the expert encoder never saw.
"""
import numpy as np, pandas as pd, torch, torch.nn as nn, pickle, warnings, os, json
warnings.filterwarnings('ignore')
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from sklearn.model_selection import GroupKFold, KFold
from sklearn.metrics import r2_score, mean_squared_error
from catboost import CatBoostRegressor

D='/Users/egorilin/Desktop'; C=f'{D}/COMA'; V=f'{D}/Veresh_paper'
OUT=f'{C}/reproducibility/qhero'; os.makedirs(OUT,exist_ok=True)
RS=42

def can(s):
    try:
        m=Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None
    except Exception: return None

q=pd.read_csv(f'{D}/Veresh_paper_Mendeley/outputs/prepared_qhero.csv')
q['can']=q.canonical_full_smiles.map(can)
q=q.dropna(subset=['can','log2_sa_mic_um']).drop_duplicates('can').reset_index(drop=True)
print(f'Q-HERO usable: {len(q)}')

H=set(pd.read_csv(f'{C}/expert_labels/expert_labels_1103.csv').canonical_smiles.dropna())
q['seen_by_expert_encoder']=q.can.isin(H)
print(f'  seen by expert encoder: {q.seen_by_expert_encoder.sum()}  | unseen: {(~q.seen_by_expert_encoder).sum()}')

# ---- MolFormer embeddings ----
cache=f'{OUT}/qhero_molformer.npy'
if os.path.exists(cache):
    MF=np.load(cache)
else:
    from transformers import AutoModel, AutoTokenizer
    tok=AutoTokenizer.from_pretrained("ibm/MoLFormer-XL-both-10pct", trust_remote_code=True, revision="7b12d946c181a37f6012b9dc3b002275de070314")
    mdl=AutoModel.from_pretrained("ibm/MoLFormer-XL-both-10pct", deterministic_eval=True, revision="7b12d946c181a37f6012b9dc3b002275de070314",
                                  trust_remote_code=True).eval()
    embs=[]
    for i in range(0,len(q),64):
        b=q.can.iloc[i:i+64].tolist()
        with torch.no_grad():
            o=mdl(**tok(b,padding=True,truncation=True,return_tensors='pt'))
        embs.append(o.pooler_output.numpy())
        print(f'  embedded {min(i+64,len(q))}/{len(q)}')
    MF=np.vstack(embs); np.save(cache,MF)
print('MolFormer:',MF.shape)

# ---- encoders ----
class Enc(nn.Module):
    def __init__(s,inp=768,h=[512,384,256],pd_=128,dr=0.3):
        super().__init__(); L=[];p=inp
        for d in h: L+=[nn.Linear(p,d),nn.BatchNorm1d(d),nn.ReLU(),nn.Dropout(dr)];p=d
        s.encoder=nn.Sequential(*L)
        s.projection_head=nn.Sequential(nn.Linear(h[-1],pd_),nn.BatchNorm1d(pd_),nn.ReLU(),
                                        nn.Dropout(dr*.5),nn.Linear(pd_,pd_),nn.BatchNorm1d(pd_))
    def forward(s,x): return s.encoder(x)

scaler=pickle.load(open(f'{V}/scaler_classification.pkl','rb'))
Xs=scaler.transform(MF)
def embed(p):
    e=Enc(); e.load_state_dict(torch.load(p,map_location='cpu')); e.eval()
    with torch.no_grad(): return e(torch.FloatTensor(Xs)).numpy()
REP={'expert (Good/Bad)':embed(f'{V}/encoder_borderline_smote.pth'),
     'multi-regression':embed(f'{C}/analysis/encoder_reg_only.pth'),
     'MolFormer (raw)':MF.astype(np.float32)}

y=q.log2_sa_mic_um.values
groups=q.scaffold_key.fillna('none').values
CB=dict(iterations=800,learning_rate=0.05,depth=6,verbose=0)

def cv(X,y,grp,scaffold,seed):
    kf=(GroupKFold(n_splits=5) if scaffold else KFold(n_splits=5,shuffle=True,random_state=seed))
    pred=np.zeros(len(y))
    for tr,te in (kf.split(X,y,groups=grp) if scaffold else kf.split(X)):
        m=CatBoostRegressor(random_seed=seed,**CB); m.fit(X[tr],y[tr]); pred[te]=m.predict(X[te])
    return r2_score(y,pred), np.sqrt(mean_squared_error(y,pred)), pred

rows=[]
for subset,mask in [('all Q-HERO',np.ones(len(q),bool)),
                    ('unseen by expert encoder',(~q.seen_by_expert_encoder).values)]:
    for scaffold,sname in [(False,'random 5-fold'),(True,'scaffold 5-fold')]:
        for name,E in REP.items():
            r2s,rmses=[],[]
            for seed in range(5):
                r2,rmse,_=cv(E[mask],y[mask],groups[mask],scaffold,seed)
                r2s.append(r2); rmses.append(rmse)
            rows.append(dict(subset=subset,split=sname,representation=name,n=int(mask.sum()),
                             R2_mean=np.mean(r2s),R2_sd=np.std(r2s),
                             RMSE_mean=np.mean(rmses),RMSE_sd=np.std(rmses)))
            print(f'  {subset:26s} {sname:16s} {name:20s} R2={np.mean(r2s):.3f}±{np.std(r2s):.3f}  RMSE={np.mean(rmses):.3f}')
res=pd.DataFrame(rows); res.to_csv(f'{OUT}/qhero_metrics.csv',index=False)

# ---- paired per-molecule residuals for the violin plot + sign test ----
resid=[]
for subset,mask in [('all Q-HERO',np.ones(len(q),bool)),
                    ('unseen by expert encoder',(~q.seen_by_expert_encoder).values)]:
    for name,E in REP.items():
        _,_,pred=cv(E[mask],y[mask],groups[mask],True,RS)
        resid.append(pd.DataFrame(dict(subset=subset,representation=name,
                                       can=q.can.values[mask],
                                       abs_residual=np.abs(pred-y[mask]))))
pd.concat(resid).to_csv(f'{OUT}/qhero_residuals.csv',index=False)
print('\nwrote',OUT)
