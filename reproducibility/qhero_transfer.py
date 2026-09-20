"""Zero-shot transfer between two independent QAC collections.

Complements qhero_benchmark.py. That script trains the downstream regressor
*inside* Q-HERO under cross-validation, which probes how much S. aureus MIC
signal each frozen representation carries. This script instead trains on one
collection and predicts the other with no adaptation - the setting that matches
the out-of-domain framing of the manuscript.

Both endpoints are log2 MIC in uM, so the two collections are directly comparable.
The encoders are frozen feature extractors throughout; nothing is fine-tuned.
"""
import numpy as np, pandas as pd, torch, torch.nn as nn, pickle, warnings, os
warnings.filterwarnings('ignore')
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import spearmanr
from catboost import CatBoostRegressor

D='/Users/egorilin/Desktop'; C=f'{D}/COMA'; V=f'{D}/Veresh_paper'
M=f'{D}/Veresh_paper_Mendeley/outputs'
OUT=f'{C}/reproducibility/qhero'; os.makedirs(OUT,exist_ok=True)

def can(s):
    try:
        m=Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None
    except Exception: return None

def load(path,smi,y):
    d=pd.read_csv(path); d['can']=d[smi].map(can)
    return d.dropna(subset=['can',y]).drop_duplicates('can').reset_index(drop=True)

Q=load(f'{M}/prepared_qac_target.csv','canonical_full_smiles','log2_sa_mic_um')
H=load(f'{M}/prepared_qhero.csv','canonical_full_smiles','log2_sa_mic_um')
print(f'QAC-105: {len(Q)}   Q-HERO: {len(H)}   shared: {len(set(Q.can)&set(H.can))}')

E=set(pd.read_csv(f'{C}/expert_labels/expert_labels_1103.csv').canonical_smiles.dropna())
H['unseen']=~H.can.isin(E); Q['unseen']=~Q.can.isin(E)
print(f'  Q-HERO unseen by expert encoder: {H.unseen.sum()}   QAC-105 unseen: {Q.unseen.sum()}')

# ---- frozen MolFormer ----
def molformer(sm,cache):
    p=f'{OUT}/{cache}'
    if os.path.exists(p): return np.load(p)
    from transformers import AutoModel, AutoTokenizer
    REV="7b12d946c181a37f6012b9dc3b002275de070314"
    tok=AutoTokenizer.from_pretrained("ibm/MoLFormer-XL-both-10pct",trust_remote_code=True,revision=REV)
    mdl=AutoModel.from_pretrained("ibm/MoLFormer-XL-both-10pct",deterministic_eval=True,
                                  revision=REV,trust_remote_code=True).eval()
    out=[]
    for i in range(0,len(sm),64):
        with torch.no_grad():
            o=mdl(**tok(sm[i:i+64],padding=True,truncation=True,return_tensors='pt'))
        out.append(o.pooler_output.numpy())
    a=np.vstack(out); np.save(p,a); return a
MF_Q=molformer(Q.can.tolist(),'qac105_molformer.npy')
MF_H=molformer(H.can.tolist(),'qhero_molformer.npy')

class Enc(nn.Module):
    def __init__(s,inp=768,h=[512,384,256],pd_=128,dr=0.3):
        super().__init__(); L=[];p=inp
        for d in h: L+=[nn.Linear(p,d),nn.BatchNorm1d(d),nn.ReLU(),nn.Dropout(dr)];p=d
        s.encoder=nn.Sequential(*L)
        s.projection_head=nn.Sequential(nn.Linear(h[-1],pd_),nn.BatchNorm1d(pd_),nn.ReLU(),
                                        nn.Dropout(dr*.5),nn.Linear(pd_,pd_),nn.BatchNorm1d(pd_))
    def forward(s,x): return s.encoder(x)
sc=pickle.load(open(f'{V}/scaler_classification.pkl','rb'))
def enc(path,MFx):
    e=Enc(); e.load_state_dict(torch.load(path,map_location='cpu')); e.eval()
    with torch.no_grad(): return e(torch.FloatTensor(sc.transform(MFx))).numpy()
def reps(MFx):
    return {'expert (Good/Bad)':enc(f'{V}/encoder_borderline_smote.pth',MFx),
            'multi-regression':enc(f'{C}/analysis/encoder_reg_only.pth',MFx),
            'MolFormer (raw)':MFx.astype(np.float32)}
RQ,RH=reps(MF_Q),reps(MF_H)
CB=dict(iterations=800,learning_rate=0.05,depth=6,verbose=0)

rows=[]
def transfer(name,Rtr,ytr,Rte,yte,mask,tag):
    for rep in RQ:
        Xtr,Xte=Rtr[rep],Rte[rep][mask]
        P=[]
        for s in range(5):
            m=CatBoostRegressor(random_seed=s,**CB); m.fit(Xtr,ytr); P.append(m.predict(Xte))
        pred=np.mean(P,axis=0); yt=yte[mask]
        rows.append(dict(direction=name,test_subset=tag,representation=rep,n=int(mask.sum()),
                         R2=r2_score(yt,pred),RMSE=np.sqrt(mean_squared_error(yt,pred)),
                         spearman=spearmanr(yt,pred).statistic))
        print(f'  {name:28s} {tag:24s} {rep:20s} R2={rows[-1]["R2"]:+.3f}  RMSE={rows[-1]["RMSE"]:.3f}  rho={rows[-1]["spearman"]:+.3f}')

shared=set(Q.can)&set(H.can)
yH,yQ=H.log2_sa_mic_um.values,Q.log2_sa_mic_um.values
print('\n=== ZERO-SHOT TRANSFER (no fine-tuning, frozen encoders) ===')
transfer('QAC-105 -> Q-HERO',RQ,yQ,RH,yH,(~H.can.isin(shared)).values,'all (excl. shared)')
transfer('QAC-105 -> Q-HERO',RQ,yQ,RH,yH,(H.unseen&~H.can.isin(shared)).values,'unseen by expert enc.')
transfer('Q-HERO -> QAC-105',RH,yH,RQ,yQ,(~Q.can.isin(shared)).values,'all (excl. shared)')

df=pd.DataFrame(rows); df.to_csv(f'{OUT}/qhero_transfer.csv',index=False)
print('\nbaseline (predict training mean):')
for nm,ytr,yte,msk in [('QAC-105 -> Q-HERO',yQ,yH,(~H.can.isin(shared)).values),
                       ('Q-HERO -> QAC-105',yH,yQ,(~Q.can.isin(shared)).values)]:
    print(f'  {nm:28s} R2={r2_score(yte[msk],np.full(msk.sum(),ytr.mean())):+.3f}')
print('\nwrote',f'{OUT}/qhero_transfer.csv')
