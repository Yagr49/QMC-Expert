"""Builds the fine-tuning sources and the evaluation targets, with all
evaluation molecules held out of every training source."""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')

D='/Users/egorilin/Desktop'; C=f'{D}/COMA'; M=f'{D}/Veresh_paper_Mendeley/outputs'
OUT=f'{C}/reproducibility/finetune/data'; os.makedirs(OUT,exist_ok=True)

def can(s):
    try:
        m=Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None
    except Exception: return None

def scaffold(s):
    try:
        from rdkit.Chem.Scaffolds import MurckoScaffold
        m=Chem.MolFromSmiles(str(s))
        if m is None: return 'none'
        sc=MurckoScaffold.MurckoScaffoldSmiles(mol=m, includeChirality=False)
        return sc if sc else 'acyclic'
    except Exception: return 'none'

# ---------------- evaluation targets ----------------
q105=pd.read_csv(f'{M}/prepared_qac_target.csv'); q105['can']=q105.canonical_full_smiles.map(can)
q105=q105.dropna(subset=['can','log2_sa_mic_um']).drop_duplicates('can')[['can','log2_sa_mic_um']]
q105.columns=['can','y']

qhero=pd.read_csv(f'{M}/prepared_qhero.csv'); qhero['can']=qhero.canonical_full_smiles.map(can)
qhero=qhero.dropna(subset=['can','log2_sa_mic_um']).drop_duplicates('can')[['can','log2_sa_mic_um']]
qhero.columns=['can','y']

ood=pd.read_excel(f'{D}/Veresh_paper/QACs_SMILES_MIC_MBC.xlsx','Лист1')
mw=pd.read_excel(f'{D}/Veresh_paper/Data_biocides.xlsx')  # not needed; OOD stays in mg/L -> convert
def num(v):
    if pd.isna(v): return np.nan
    return float(str(v).replace('>','').replace('<','').strip())
ood['can']=ood.SMILES.map(can)
ood['mic_mgl']=ood['MIC Sa'].map(num)
from rdkit.Chem import Descriptors
ood['mw']=ood.can.map(lambda s: Descriptors.MolWt(Chem.MolFromSmiles(s)) if s else np.nan)
ood['y']=np.log2(ood.mic_mgl/ood.mw*1000)
ood=ood.dropna(subset=['can','y']).drop_duplicates('can')[['can','y']]

EVAL={'QAC-105':q105,'Q-HERO':qhero,'OOD-17':ood}
HOLD=set().union(*[set(v.can) for v in EVAL.values()])
print('evaluation targets:', {k:len(v) for k,v in EVAL.items()}, '| union held out:',len(HOLD))

# ---------------- fine-tuning sources ----------------
exp=pd.read_csv(f'{C}/expert_labels/expert_labels_1103.csv')
exp=exp.dropna(subset=['canonical_smiles']).drop_duplicates('canonical_smiles')
exp=exp[['canonical_smiles','label_binary']]; exp.columns=['can','y']
exp['task']='binary'

qmr=pd.read_excel(f'{D}/Veresh_Dataset_Paper/QMR_dataset_JCIM_v8_publication_ready.xlsx','All',
                  usecols=['Canonical SMILES_v2','MIC_uM_unified','Strain_normalized'])
qmr=qmr.dropna(subset=['Canonical SMILES_v2','MIC_uM_unified'])
qmr=qmr[qmr.MIC_uM_unified>0]
qmr['can']=qmr['Canonical SMILES_v2'].map(can)
qmr=qmr.dropna(subset=['can'])
qmr['y']=np.log2(qmr.MIC_uM_unified.astype(float))
qmr=qmr[np.isfinite(qmr.y)]
rec=qmr[['can','y']].copy(); rec['task']='reg'
mol=qmr.groupby('can').y.median().reset_index(); mol['task']='reg'

SRC={'expert-binary':exp,'quant-molecule':mol,'quant-record':rec}
meta={}
for k,v in SRC.items():
    before=len(v)
    v=v[~v.can.isin(HOLD)].reset_index(drop=True)
    v['scaffold']=v.can.map(scaffold)
    v.to_csv(f'{OUT}/src_{k}.csv',index=False)
    meta[k]=dict(rows=len(v),removed=before-len(v),molecules=int(v.can.nunique()),
                 task=v.task.iloc[0],scaffolds=int(v.scaffold.nunique()))
    print(f'  {k:16s} {len(v):6d} rows ({before-len(v)} held out)  {v.can.nunique():5d} mols  {v.scaffold.nunique():4d} scaffolds')

for k,v in EVAL.items():
    v=v.copy(); v['scaffold']=v.can.map(scaffold)
    v.to_csv(f'{OUT}/eval_{k}.csv',index=False)
    meta[f'eval:{k}']=dict(rows=len(v),scaffolds=int(v.scaffold.nunique()))
json.dump(meta,open(f'{OUT}/meta.json','w'),indent=1)
print('\nwrote',OUT)
