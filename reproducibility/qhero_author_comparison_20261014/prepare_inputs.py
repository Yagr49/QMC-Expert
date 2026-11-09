"""Assemble the common endpoint and audit public-data alignment before fitting."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parent.parent
BASE = COMA / 'reproducibility' / 'revision_v12'
PUBLIC = Path('/private/tmp/coma_qhero_20261014')
OUT = ROOT / 'data'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    original = pd.read_excel(PUBLIC / 'JCIM_QAC Dataset.xlsx', sheet_name='Features-MIC')
    si = pd.read_excel(COMA.parent / 'Veresh_paper_Mendeley' / 'ci6c00390_si_002.xlsx',
                       sheet_name='QACs')
    si['numeric_mic'] = pd.to_numeric(si['MIC S. aureus (µM)'], errors='coerce')
    numeric = si[si.numeric_mic.notna()].reset_index(drop=True)
    descriptors = original.columns[:-1].tolist()
    assert len(original) == len(numeric) == 421 and len(descriptors) == 35
    assert np.array_equal(original.iloc[:, -1].values, numeric.numeric_mic.values)
    assert np.allclose(original.iloc[:, :-1].values,
                       numeric[descriptors].values, equal_nan=True)
    original.to_csv(OUT / 'author_features_MIC.csv', index=False)

    target = pd.read_csv(BASE / 'data' / 'target_Q-HERO-405.csv')
    assert len(target) == target.can.nunique() == 405
    assert not target.label_conflict.any()
    assert np.allclose(target.y.values, np.log2(target.sa_mic_um.values))
    folds = pd.read_csv(BASE / 'data' / 'target_folds.csv')
    folds = folds[folds.target.eq('Q-HERO-405')].set_index('can').fold
    target['scaffold_fold'] = target.can.map(folds)
    assert target.scaffold_fold.notna().all()
    assert target.groupby('scaffold').scaffold_fold.nunique().max() == 1
    y = (target.sa_mic_um.values <= 8).astype(int)
    tr, te = train_test_split(np.arange(len(target)), test_size=.2,
                             random_state=0, stratify=y)
    target['random_split'] = 'train'
    target.loc[te, 'random_split'] = 'test'
    x = target[descriptors].to_numpy(float)
    assert x.shape == (405, 35) and np.isfinite(x).all()
    np.save(OUT / 'descriptors.npy', x)
    target[['can','cation','scaffold','compound_id','sa_mic_um','y',
            'scaffold_fold','random_split']].to_csv(OUT / 'target.csv', index=False)

    overlaps = {}
    for source_name in ('expert', 'quant'):
        source = pd.read_csv(BASE / 'data' / ('matched-pooled_' + source_name + '.csv'))
        overlaps[source_name] = dict(
            source_molecules=len(source),
            full_salt_overlap=len(set(source.can) & set(target.can)),
            cation_overlap=len(set(source.cation) & set(target.cation)))
        assert overlaps[source_name]['full_salt_overlap'] == 0
        assert overlaps[source_name]['cation_overlap'] == 0

    feature_files = ['raw-molformer_Q-HERO-405.npy']
    feature_files += [arm+'_seed'+str(seed)+'_Q-HERO-405.npy'
                     for arm in ('expert','expert-shuffled','quant-continuous')
                     for seed in range(5)]
    for name in feature_files:
        p = BASE / 'results' / 'representations' / name
        features = np.load(p)
        assert features.shape == (405, 768) and np.isfinite(features).all()
        shutil.copyfile(p, OUT / name)

    manifest = dict(
        author_repo='https://github.com/pb0316/Q-HERO',
        author_commit=subprocess.check_output(['git','-C',str(PUBLIC),'rev-parse','HEAD'],
                                              text=True).strip(),
        public_workbook=sha(PUBLIC / 'JCIM_QAC Dataset.xlsx'),
        public_RF_code=sha(PUBLIC / 'JCIM_RF.rtf'),
        target_source=sha(BASE / 'data' / 'target_Q-HERO-405.csv'),
        binary_target='1 iff MIC S. aureus <= 8 micromolar',
        source_representation='Matched partial MolFormer fine-tuning; 681 source molecules; source seeds 0..4',
        source_overlaps=overlaps,
        n_target=405, n_descriptors=35, n_train=len(tr), n_test=len(te),
        positive_count=int(y.sum()), test_positives=int(y[te].sum()),
        train_test_full_salt_overlap=len(set(target.can.iloc[tr]) & set(target.can.iloc[te])),
        train_test_cation_overlap=len(set(target.cation.iloc[tr]) & set(target.cation.iloc[te])),
        historical_compact_v5_adapter_used=False,
        target_numeric_MIC_used_to_train_classifier=True,
        test_used_for_model_selection=False,
        input_sha256={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()})
    (ROOT / 'input_manifest.json').write_text(json.dumps(manifest, indent=2))
    with tarfile.open(ROOT / 'payload.tar.gz', 'w:gz') as tf:
        for p in sorted(OUT.iterdir()):
            tf.add(p, arcname='data/'+p.name)
        for name in ('run_comparison.py','input_manifest.json'):
            tf.add(ROOT/name, arcname=name)
    print(json.dumps({k:v for k,v in manifest.items() if k!='input_sha256'}, indent=2))


if __name__ == '__main__':
    main()
