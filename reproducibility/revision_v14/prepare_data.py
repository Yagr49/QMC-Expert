from pathlib import Path
import json, hashlib, sys, pickle, warnings
import numpy as np
import pandas as pd
import torch
from torch import nn
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parents[1]
DESKTOP = COMA.parent
TASKS = ['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
COLS = ['sa_mic_mg_l','sa_mbc_mg_l','ec_mic_mg_l','ec_mbc_mg_l']

def canonical(s): return Chem.MolToSmiles(Chem.MolFromSmiles(str(s)))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Enc(nn.Module):
    def __init__(self):
        super().__init__(); layers=[]; p=768
        for d in [512,384,256]:
            layers += [nn.Linear(p,d),nn.BatchNorm1d(d),nn.ReLU(),nn.Dropout(.3)]; p=d
        self.encoder=nn.Sequential(*layers)
        self.projection_head=nn.Sequential(nn.Linear(256,128),nn.BatchNorm1d(128),nn.ReLU(),
            nn.Dropout(.15),nn.Linear(128,128),nn.BatchNorm1d(128))

def main():
    warnings.filterwarnings('ignore',message='Data Validation extension')
    data=ROOT/'data';rep=ROOT/'representations';data.mkdir(exist_ok=True);rep.mkdir(exist_ok=True)
    old=COMA/'reproducibility/revision_v12'
    source=old/'data/target_QAC-104.csv'
    q=pd.read_csv(COMA/'reproducibility/revision_v13/data/original_QAC105_registry.csv')
    q['cation']=q.canonical_cation_smiles
    q['scaffold']=q.cation.map(lambda s: MurckoScaffold.MurckoScaffoldSmiles(mol=Chem.MolFromSmiles(s)))
    folds=np.zeros(len(q),dtype=int)
    for fold,(_,te) in enumerate(GroupKFold(n_splits=5).split(q,groups=q.cation)): folds[te]=fold
    q['fold']=folds
    assert len(q)==105 and q.can.is_unique
    s=pd.read_csv(old/'data/matched-pooled_expert.csv')
    assert not set(q.cation)&set(s.cation)
    q.to_csv(data/'QAC105.csv',index=False)
    o=pd.read_csv(COMA/'reproducibility/revision_v13/data/OOD17_named_registry.csv')
    rawood=pd.read_excel(DESKTOP/'Veresh_paper/QACs_SMILES_MIC_MBC.xlsx')
    rawood['can']=rawood.SMILES.map(canonical)
    rawood=rawood.set_index('can').loc[o.can]
    assert not set(o.cation)&(set(q.cation)|set(s.cation))
    assert not set(o.scaffold)&(set(q.scaffold)|set(s.scaffold))
    for col,rawcol in zip(COLS,['MIC Sa','MBC Sa','MIC Ec','MBC Ec']):
        values=rawood[rawcol].astype(str)
        o[col+'_qualifier']=values.map(lambda x:'>' if x.startswith('>') else '=') .values
        o[col]=values.map(lambda x:float(x.lstrip('>'))).values
    assert (o.ec_mbc_mg_l_qualifier=='>').sum()==1
    o.to_csv(data/'OOD17.csv',index=False)
    pairs=[]
    for cohort,df in [('QAC105',q),('OOD17',o)]:
        for i,row in df.iterrows():
            for task,col in zip(TASKS,COLS):
                value=float(row[col]); assert value>0
                pairs.append(dict(cohort=cohort,molecule_index=i,compound_id=row.compound_id if cohort=='QAC105' else row.code,
                    can=row.can,cation=row.cation,scaffold=row.scaffold,task=task,
                    y=np.log2(value),value_mg_l=value,
                    qualifier='=' if cohort=='QAC105' else row[col+'_qualifier'],
                    fold=int(row.fold) if cohort=='QAC105' else -1))
    pd.DataFrame(pairs).to_csv(data/'endpoint_registry.csv',index=False)
    # Align archived raw feature rows by workbook identity, not implicit positions.
    origpath=DESKTOP/'Veresh_paper/Data_biocides.xlsx'
    orig=pd.read_excel(origpath);orig['can']=orig.iloc[:,1].map(canonical)
    x=pd.read_excel(DESKTOP/'Veresh_paper/Test_molformer_original_biocides.xlsx').drop(columns=['Unnamed: 0']).to_numpy(dtype=np.float32)
    assert len(orig)==len(x)==108
    grouped={can:x[np.flatnonzero(orig.can.values==can)] for can in q.can}
    assert all(np.max(np.abs(v-v[0]))<1e-5 for v in grouped.values())
    xq=np.vstack([grouped[can].mean(axis=0) for can in q.can])
    xo=pd.read_excel(DESKTOP/'Veresh_paper/Test_molformer_ood.xlsx').drop(columns=['Unnamed: 0']).to_numpy(dtype=np.float32)
    raworder=pd.read_excel(DESKTOP/'Veresh_paper/QACs_SMILES_MIC_MBC.xlsx').SMILES.map(canonical).tolist()
    xo=xo[[raworder.index(can) for can in o.can]]
    scalerpath=DESKTOP/'Veresh_paper/scaler_classification.pkl'
    scaler=pickle.load(scalerpath.open('rb'))
    paths={'legacy-human':DESKTOP/'Veresh_paper/encoder_borderline_smote.pth',
           'legacy-quantitative':COMA/'analysis/encoder_reg_only.pth'}
    configurations=[]
    for name in ['legacy-raw','legacy-human','legacy-quantitative']:
        if name=='legacy-raw': a,b=xq,xo
        else:
            net=Enc();net.load_state_dict(torch.load(paths[name],map_location='cpu',weights_only=False));net.eval()
            with torch.no_grad():
                a=net.encoder(torch.tensor(scaler.transform(xq),dtype=torch.float32)).numpy()
                b=net.encoder(torch.tensor(scaler.transform(xo),dtype=torch.float32)).numpy()
        np.save(rep/(name+'_QAC105.npy'),a);np.save(rep/(name+'_OOD17.npy'),b)
        configurations.append(dict(name=name,arm=name,seed=-1,provenance='legacy-overlapping-source',encodings=['separate','onehot','text']))
    (data/'legacy_configurations.json').write_text(json.dumps(configurations,indent=2))
    audit=dict(QAC_full_salts=len(q),QAC_cations=q.cation.nunique(),QAC_scaffolds=q.scaffold.nunique(),
        QAC_conflicting_duplicates=int(q.label_conflict.sum()),OOD_molecules=len(o),OOD_scaffolds=o.scaffold.nunique(),
        QAC_exact_pairs=420,OOD_exact_pairs=67,OOD_right_censored_pairs=1,
        source_target_cation_overlap=0,OOD_source_scaffold_overlap=0,OOD_QAC_scaffold_overlap=0,
        fold_counts=q.groupby('fold').size().to_dict(),
        protocol_sha256=sha(ROOT/'PROTOCOL.md'),legacy_encoder_sha256={k:sha(p) for k,p in paths.items()},
        scaler_sha256=sha(scalerpath),original_workbook_sha256=sha(origpath),
        archived_vectors_note='Historical encoders overlap original cohort; strictly matched v12 vectors are primary.')
    (data/'cohort_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))

if __name__=='__main__':main()
