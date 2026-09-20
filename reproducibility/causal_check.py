"""Re-derivation of the OOD ablation and the equivalence test in section 2.4.

Trains on the 108 in-domain biocides, predicts the 17 OOD compounds, and compares
the expert-supervised encoder against the regression-supervised one on the paired
per-(compound, endpoint) absolute residuals.
"""
import numpy as np, pandas as pd, torch, torch.nn as nn, pickle, warnings, os
warnings.filterwarnings('ignore')
from scipy import stats
from sklearn.metrics import mean_squared_error
from catboost import CatBoostRegressor
D='/Users/egorilin/Desktop'; C=f'{D}/COMA'; V=f'{D}/Veresh_paper'
OUT=f'{C}/reproducibility/causal'; os.makedirs(OUT,exist_ok=True)

tgt=pd.read_excel(f'{V}/Data_biocides.xlsx')
mf=pd.read_excel(f'{V}/Test_molformer_original_biocides.xlsx').drop(['Unnamed: 0'],axis=1)
ood_mf=pd.read_excel(f'{V}/Test_molformer_ood.xlsx').drop(['Unnamed: 0'],axis=1)
ood=pd.read_excel(f'{V}/QACs_SMILES_MIC_MBC.xlsx','Лист1')
TC=[c for c in tgt.columns if 'Activity' in c]
OC=['MIC Sa','MBC Sa','MIC Ec','MBC Ec']
print('in-domain',mf.shape,'| ood',ood_mf.shape,'| ood targets',ood[OC].notna().sum().to_dict())

class Enc(nn.Module):
    def __init__(s,inp=768,h=[512,384,256],pd_=128,dr=0.3):
        super().__init__(); L=[];p=inp
        for d in h: L+=[nn.Linear(p,d),nn.BatchNorm1d(d),nn.ReLU(),nn.Dropout(dr)];p=d
        s.encoder=nn.Sequential(*L)
        s.projection_head=nn.Sequential(nn.Linear(h[-1],pd_),nn.BatchNorm1d(pd_),nn.ReLU(),
                                        nn.Dropout(dr*.5),nn.Linear(pd_,pd_),nn.BatchNorm1d(pd_))
    def forward(s,x): return s.encoder(x)
sc=pickle.load(open(f'{V}/scaler_classification.pkl','rb'))
def embed(path,X):
    e=Enc(); e.load_state_dict(torch.load(path,map_location='cpu')); e.eval()
    with torch.no_grad(): return e(torch.FloatTensor(sc.transform(X))).numpy()
ENC={'expert':f'{V}/encoder_borderline_smote.pth','regression':f'{C}/analysis/encoder_reg_only.pth'}
REP={k:(embed(p,mf),embed(p,ood_mf)) for k,p in ENC.items()}
REP['molformer']=(mf.values.astype(np.float32), ood_mf.values.astype(np.float32))

def pairs(df,cols,emb,n):
    R=[]
    for i in range(n):
        for j,c in enumerate(cols):
            v=df[c].iloc[i]
            if pd.isna(v): continue
            # right-censored entries ('>500') are treated at the censoring bound
            v=float(str(v).replace('>','').replace('<','').strip())
            if v>0: R.append((i,j,np.log2(v)))
    return R
TR=pairs(tgt,TC,None,len(tgt)); TE=pairs(ood,OC,None,len(ood))
print(f'train pairs {len(TR)} | test pairs {len(TE)} over {len(set(t[0] for t in TE))} OOD molecules')
oh=lambda j: [j//2==0, j//2==1, j%2==0, j%2==1]

res={}
for name,(Ein,Eood) in REP.items():
    Xtr=np.array([list(Ein[i])+oh(j) for i,j,_ in TR]); ytr=np.array([v for _,_,v in TR])
    Xte=np.array([list(Eood[i])+oh(j) for i,j,_ in TE]); yte=np.array([v for _,_,v in TE])
    P=[]
    for s in range(5):
        m=CatBoostRegressor(iterations=800,learning_rate=0.05,depth=6,random_seed=s,verbose=0)
        m.fit(Xtr,ytr); P.append(m.predict(Xte))
    pred=np.mean(P,axis=0)
    res[name]=np.abs(pred-yte)
    print(f'  {name:11s} OOD RMSE = {np.sqrt(mean_squared_error(yte,pred)):.3f}')

mol=np.array([i for i,_,_ in TE]); ep=np.array([j for _,j,_ in TE])
df=pd.DataFrame({'mol':mol,'endpoint':[OC[j] for j in ep],
                 **{f'absres_{k}':v for k,v in res.items()}})
df['delta_expert_minus_reg']=df.absres_expert-df.absres_regression
df.to_csv(f'{OUT}/ood_paired_residuals.csv',index=False)

d=df.delta_expert_minus_reg.values
print(f'\n=== paired difference (expert - regression), n={len(d)} pairs, {df.mol.nunique()} molecules ===')
print(f'  mean delta            = {d.mean():+.4f}')
print(f'  favours expert        = {(d<0).sum()}/{len(d)} = {(d<0).mean()*100:.0f}%')
bt=stats.binomtest((d<0).sum(),len(d),0.5)
print(f'  sign test p           = {bt.pvalue:.4f}')
w=stats.wilcoxon(df.absres_expert,df.absres_regression)
print(f'  Wilcoxon p            = {w.pvalue:.4f}')

# cluster bootstrap over molecules
rng=np.random.default_rng(0); mols=df.mol.unique(); B=[]
for _ in range(10000):
    s=rng.choice(mols,len(mols),replace=True)
    B.append(np.concatenate([d[df.mol.values==m] for m in s]).mean())
lo,hi=np.percentile(B,[2.5,97.5])
print(f'  cluster bootstrap ATE = {np.mean(B):+.4f}  95% CI [{lo:+.3f}, {hi:+.3f}]  (n_clusters={len(mols)})')

try:
    from econml.dml import CausalForestDML
    from sklearn.ensemble import RandomForestRegressor
    long=pd.concat([df.assign(T=0,Y=df.absres_regression),df.assign(T=1,Y=df.absres_expert)])
    X=pd.get_dummies(long.endpoint).values.astype(float)
    est=CausalForestDML(model_y=RandomForestRegressor(n_estimators=200,random_state=0),
                        model_t=RandomForestRegressor(n_estimators=200,random_state=0),
                        n_estimators=1000,random_state=0,cv=3)
    est.fit(long.Y.values,long['T'].values,X=X,groups=long.mol.values)
    inf=est.ate_inference(X=X)
    print(f'\n  CausalForestDML ATE   = {inf.mean_point:+.4f}  95% CI [{inf.conf_int_mean()[0]:+.3f}, {inf.conf_int_mean()[1]:+.3f}]')
except Exception as e:
    print('\n  CausalForestDML failed:',repr(e)[:160])

# ---------------- TOST equivalence on the paired differences ----------------
print('\n=== TOST (two one-sided tests) on paired differences, clustered by molecule ===')
per_mol=df.groupby('mol').delta_expert_minus_reg.mean().values
n=len(per_mol); m=per_mol.mean(); se=per_mol.std(ddof=1)/np.sqrt(n)
print(f'  molecule-level mean delta = {m:+.4f}  SE = {se:.4f}  (n = {n} molecules)')
for margin in [1.0, 0.5, 0.25]:
    t_lo=(m-(-margin))/se; t_hi=(m-margin)/se
    p_lo=stats.t.sf(t_lo,n-1); p_hi=stats.t.cdf(t_hi,n-1)
    p=max(p_lo,p_hi)
    ci=stats.t.interval(0.90,n-1,loc=m,scale=se)
    print(f'  margin +/-{margin:<5}  TOST p = {p:.4f}  ->  {"EQUIVALENT" if p<0.05 else "not shown"}'
          f'   (90% CI [{ci[0]:+.3f}, {ci[1]:+.3f}])')
print('\n  note: +/-1.0 log2 is ~45% of the OOD RMSE and ~6x the observed effect,')
print('        so equivalence at that margin has very little discriminating power.')
