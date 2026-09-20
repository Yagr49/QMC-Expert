"""Dataset overlap / leakage audit between the expert-labelled set,
the quantitative QMR corpus, the QAC-105 regression benchmark,
the Q-HERO external benchmark and the 17-compound OOD set."""
import pandas as pd, warnings; warnings.filterwarnings('ignore')
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
D='/Users/egorilin/Desktop'
def can(s):
    try:
        m=Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None
    except Exception: return None
H=set(pd.read_csv('expert_labels/expert_labels_1103.csv').canonical_smiles.dropna())
Q=set(pd.read_csv(f'{D}/Veresh_paper_Mendeley/outputs/prepared_qac_target.csv').canonical_full_smiles.map(can).dropna())
QH=set(pd.read_csv(f'{D}/Veresh_paper_Mendeley/outputs/prepared_qhero.csv').canonical_full_smiles.map(can).dropna())
O=set(pd.read_excel(f'{D}/Veresh_paper/QACs_SMILES_MIC_MBC.xlsx','Лист1').SMILES.map(can).dropna())
M=set(pd.read_excel(f'{D}/Veresh_Dataset_Paper/QMR_dataset_JCIM_v8_publication_ready.xlsx','All',
                    usecols=['Canonical SMILES_v2'])['Canonical SMILES_v2'].dropna().map(can).dropna())
S={'expert-1103':H,'QMR-quant':M,'QAC-105':Q,'Q-HERO':QH,'OOD-17':O}
print(f'{"":14s}'+''.join(f'{k:>13s}' for k in S)); 
for k,v in S.items():
    print(f'{k:14s}'+''.join(f'{len(v&w):13d}' for w in S.values()))
print('\nsizes:',{k:len(v) for k,v in S.items()})
