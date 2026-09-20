import numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from sklearn.model_selection import GroupKFold, KFold
from sklearn.metrics import r2_score
from catboost import CatBoostRegressor
M='/Users/egorilin/Desktop/Veresh_paper_Mendeley/outputs'
def can(s):
    try:
        m=Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None
    except Exception: return None
H=pd.read_csv(f'{M}/prepared_qhero.csv'); H['can']=H.canonical_full_smiles.map(can)
H=H.dropna(subset=['can','log2_sa_mic_um']).drop_duplicates('can').reset_index(drop=True)
y=H.log2_sa_mic_um.values; g=H.scaffold_key.fillna('none').values
MF=np.load('reproducibility/qhero/qhero_molformer.npy')
assert len(MF)==len(H)

FEAT={
 'tail_length only':H[['tail_length']].values.astype(float),
 'tail + MW + cLogP':H[['tail_length','MW','Consensus Log P']].values.astype(float),
 '6 SwissADME desc':H[['tail_length','MW','Consensus Log P','TPSA','#Rotatable bonds','formal_charge']].values.astype(float),
 'MolFormer 768':MF,
}
def cv(X,scaffold):
    kf=GroupKFold(5) if scaffold else KFold(5,shuffle=True,random_state=0)
    p=np.zeros(len(y))
    for tr,te in (kf.split(X,y,groups=g) if scaffold else kf.split(X)):
        m=CatBoostRegressor(iterations=600,learning_rate=.05,depth=6,verbose=0,random_seed=0)
        m.fit(X[tr],y[tr]); p[te]=m.predict(X[te])
    return r2_score(y,p)
print(f'{"features":22s}{"random CV":>12s}{"scaffold CV":>14s}')
for k,X in FEAT.items():
    print(f'{k:22s}{cv(X,False):12.3f}{cv(X,True):14.3f}')
print()
from scipy.stats import spearmanr
print('Spearman(tail_length, log2 MIC) = %+.3f'%spearmanr(H.tail_length,y).statistic)
print('Spearman(cLogP,       log2 MIC) = %+.3f'%spearmanr(H['Consensus Log P'],y).statistic)
print('variance of y: %.2f  (sd %.2f)'%(y.var(),y.std()))
print('\nscaffold groups: %d | largest %d (%.0f%% of rows)'%(
    H.scaffold_key.nunique(),H.scaffold_key.value_counts().iloc[0],
    H.scaffold_key.value_counts().iloc[0]/len(H)*100))
