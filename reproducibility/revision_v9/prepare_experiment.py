"""Prepare auditable supervision interventions; original artifacts remain intact."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ['HF_HOME'] = str(ROOT / 'runtime/hf')
os.environ['TRANSFORMERS_CACHE'] = str(ROOT / 'runtime/hf/hub')
os.environ['HF_MODULES_CACHE'] = str(ROOT / 'runtime/hf/modules')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
import json, hashlib
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold
RDLogger.DisableLog('rdApp.*')
DESKTOP = ROOT.parents[2]
COMA = ROOT.parents[1]
MEN = DESKTOP / 'Veresh_paper_Mendeley/outputs'
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)

def canonical(s):
    m = Chem.MolFromSmiles(str(s))
    return Chem.MolToSmiles(m) if m else None

def cation(s):
    m = Chem.MolFromSmiles(str(s))
    frags = Chem.GetMolFrags(m, asMols=True)
    pos = [f for f in frags if Chem.GetFormalCharge(f) > 0]
    # Fallback retains neutral structural identity rather than empty groups.
    use = pos or [max(frags, key=lambda f: f.GetNumHeavyAtoms())]
    return '.'.join(sorted(Chem.MolToSmiles(f) for f in use))

def scaffold(s):
    m = Chem.MolFromSmiles(cation(s))
    sc = MurckoScaffold.MurckoScaffoldSmiles(mol=m, includeChirality=False)
    return sc or 'acyclic'

def standard(df, smiles, target):
    d = df.copy()
    d['can'] = d[smiles].map(canonical)
    d['y'] = pd.to_numeric(d[target], errors='coerce')
    d = d.dropna(subset=['can', 'y'])
    d = d[np.isfinite(d.y)].copy()
    d['cation'] = d.can.map(cation)
    d['scaffold'] = d.can.map(scaffold)
    return d

def main():
    inputs = [COMA/'expert_labels/expert_labels_1103.csv',
              DESKTOP/'Veresh_Dataset_Paper/QMR_dataset_JCIM_v8_publication_ready.xlsx',
              MEN/'prepared_qac_target.csv', MEN/'prepared_qhero.csv',
              MEN/'prepared_iltox_24h_mtt.csv',
              COMA/'reproducibility/finetune/data/eval_OOD-17.csv']
    meta = {'inputs': {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
            'design':'Frozen MolFormer, matched molecules and initialization, fixed 80 epochs; exploratory protocol fixed before new results.',
            'model_revision':'7b12d946c181a37f6012b9dc3b002275de070314',
            'seeds':list(range(5)), 'epochs':80}
    targets = {}
    for name, filename in [('QAC-104', 'prepared_qac_target.csv'),('Q-HERO-405','prepared_qhero.csv')]:
        d = pd.read_csv(MEN/filename)
        d = d[~d.label_conflict.astype(bool)]
        cleaned = standard(d,'canonical_full_smiles','log2_sa_mic_um').drop_duplicates('can')
        if name == 'Q-HERO-405':
            cleaned = cleaned[~cleaned.cation.isin(set(targets['QAC-104'].cation))]
        targets[name] = cleaned.reset_index(drop=True)
    targets['OOD-17'] = standard(pd.read_csv(inputs[-1]), 'can','y')
    # Same target identity partition for all arms; no counterion variants in sources.
    ban = set().union(*(set(d.cation) for d in targets.values()))
    expert = standard(pd.read_csv(inputs[0]),'canonical_smiles','label_binary')
    conflicting = set(expert.groupby('can').y.nunique().loc[lambda x:x>1].index)
    expert = expert[~expert.can.isin(conflicting)].drop_duplicates('can')
    exp = expert[~expert.cation.isin(ban)].copy()
    quant = pd.read_excel(inputs[1], sheet_name='All')
    quant = standard(quant,'Canonical SMILES_v2','MIC_uM_unified')
    quant = quant[(quant.y>0)&(~quant.cation.isin(ban))].copy()
    quant['y'] = np.log2(quant.y)
    sa = quant[quant.Strain_normalized.astype(str).str.contains('aureus',case=False)&
               (quant.MIC_qualifier.astype(str)=='none')].copy()
    def aggregate(d):
        return d.groupby('can',sort=True).agg(y=('y','median'),cation=('cation','first'),scaffold=('scaffold','first'),n_records=('y','size')).reset_index()
    pooled,sa_mol = aggregate(quant),aggregate(sa)
    il = pd.read_csv(inputs[4])
    print('ILTox columns:',il.columns.tolist(),flush=True)
    iy = next(c for c in il.columns if c.startswith('log2_'))
    il = standard(il,'canonical_full_smiles',iy)
    il = il[~il.cation.isin(ban)].drop_duplicates('can')
    sources={'expert-full':exp,'quant-pooled-full':pooled,'quant-sa-full':sa_mol,'quant-iltox-full':il}
    # Explicitly save separate common-support matrices.
    for panel,q in [('matched-pooled',pooled),('matched-sa',sa_mol)]:
        common=sorted(set(exp.can)&set(q.can))
        e=exp.set_index('can').loc[common].reset_index()
        m=q.set_index('can').loc[common].reset_index()
        e.to_csv(DATA/f'{panel}_expert.csv',index=False)
        m.to_csv(DATA/f'{panel}_quant.csv',index=False)
        meta[panel]={'molecules':len(common),'positive_labels':int(e.y.sum()),'scaffolds':e.scaffold.nunique(),'records':int(m.n_records.sum())}
    for name,d in sources.items():
        assert not set(d.cation)&ban
        d.to_csv(DATA/f'source_{name}.csv',index=False)
        meta[name]={'molecules':len(d),'scaffolds':d.scaffold.nunique()}
    for name,d in targets.items():
        assert d.can.is_unique
        d.to_csv(DATA/f'target_{name}.csv',index=False)
        meta[name]={'molecules':len(d),'scaffolds':d.scaffold.nunique()}
    meta['conflicting_expert_structures_removed']=len(conflicting)
    meta['heldout_cations']=len(ban)
    meta['exact_source_target_cation_overlap']=0
    all_smis=sorted(set().union(*(set(d.can) for d in list(sources.values())+list(targets.values()))))
    old_smis = json.loads((DATA/'smiles.json').read_text()) if (DATA/'smiles.json').exists() else None
    old_meta = json.loads((DATA/'meta.json').read_text()) if (DATA/'meta.json').exists() else {}
    (DATA/'smiles.json').write_text(json.dumps(all_smis))
    if old_smis == all_smis and (DATA/'molformer.npy').exists():
        assert np.load(DATA/'molformer.npy',mmap_mode='r').shape == (len(all_smis),768)
        meta['token_lengths'] = old_meta['token_lengths']
        (DATA/'meta.json').write_text(json.dumps(meta,indent=2,default=int))
        print('Reused identical cached feature matrix; prepared targets', {k:len(v) for k,v in targets.items()},flush=True)
        return
    (DATA/'meta.json').write_text(json.dumps(meta,indent=2,default=int))
    print(json.dumps(meta,indent=2,default=int),flush=True)
    import torch
    from transformers import AutoModel,AutoTokenizer
    torch.set_num_threads(6)
    torch.manual_seed(1729)
    dev=torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    tok=AutoTokenizer.from_pretrained(ROOT/'runtime/molformer',trust_remote_code=True)
    model=AutoModel.from_pretrained(ROOT/'runtime/molformer',trust_remote_code=True,deterministic_eval=True).to(dev).eval()
    for module in model.modules():
        if hasattr(module,'deterministic'): module.deterministic=True
    lengths=[len(x) for x in tok(all_smis,truncation=False)['input_ids']]
    meta['token_lengths']={'max':max(lengths),'truncated_over_202':sum(x>202 for x in lengths),'total':len(all_smis)}
    (DATA/'meta.json').write_text(json.dumps(meta,indent=2,default=int))
    features=[]
    with torch.no_grad():
        for start in range(0,len(all_smis),32):
            batch=tok(all_smis[start:start+32],padding='max_length',truncation=True,max_length=202,return_tensors='pt').to(dev)
            features.append(model(**batch).pooler_output.cpu().numpy())
            print(f'embedded {min(start+32,len(all_smis))}/{len(all_smis)} on {dev}',flush=True)
    x=np.vstack(features).astype('float32')
    assert np.isfinite(x).all() and x.shape==(len(all_smis),768)
    np.save(DATA/'molformer.npy',x)
    print('DONE',x.shape,flush=True)

if __name__=='__main__': main()
