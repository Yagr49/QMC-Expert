from pathlib import Path
import json,hashlib,zipfile,posixpath
import xml.etree.ElementTree as E
import numpy as np,pandas as pd
from sklearn.metrics import r2_score,mean_squared_error
from analyse_extension import load,MODELS
R=Path(__file__).resolve().parent;C=R.parents[1]
p,m=load();keys=['backbone','panel','arm','head','seed','target'];checks={}
assert not p.duplicated(keys+['can']).any() and np.isfinite(p[['y','pred']].values).all()
targets={name:pd.read_csv(R/'data'/f'target_{name}.csv') for name in ['QAC-104','Q-HERO-405','OOD-17']}
ban=set().union(*(set(t.cation) for t in targets.values()))
for file in (R/'data').glob('*.csv'):
    if file.name.startswith(('source_','matched-','context_')):
        source=pd.read_csv(file);assert not set(source.cation)&ban
checks['source_target_cation_overlap']=0
for name in MODELS[1:]:
    meta=json.loads((R/'data'/f'{name}_meta.json').read_text());assert meta['truncated']==0
    if (R/'data'/f'{name}.npy').exists():
        f=R/'data'/f'{name}.npy';x=np.load(f);assert len(x)==1939 and np.isfinite(x).all();assert hashlib.sha256(f.read_bytes()).hexdigest()==meta['features_sha256']
    else:
        server=json.loads((R/'server_checks/feature_validation_server.json').read_text())[name]
        assert server['finite'] and server['sha256']==meta['features_sha256'] and server['shape']==meta['shape']
    assert meta['loading_info']['error_msgs']==[] and meta['loading_info']['mismatched_keys']==[]
    # ChemBERTa's unused pooler may be missing; no encoder weights may be missing.
    assert not [s for s in meta['loading_info']['missing_keys'] if 'pooler' not in s]
checks['modern_checkpoint_metadata_valid']=True
for folder in R.glob('results_*'):
    if not (folder/'manifest.json').exists():continue
    tr=pd.read_csv(folder/'training.csv')
    for _,d in tr.groupby(['panel','seed']):
        assert d.init_sha256.nunique()==1 and d.train_identity_sha256.nunique()==1
    folds=pd.read_csv(folder/'target_folds.csv');original=pd.read_csv(R/'data/target_folds.csv')
    assert folds.sort_values(['target','can']).reset_index(drop=True).equals(original.sort_values(['target','can']).reset_index(drop=True))
checks['paired_initialisation_identities_and_archived_folds']=True
for _,z in m.iterrows():
    d=p[(p.backbone==z.backbone)&(p.panel==z.panel)&(p.arm==z.arm)&(p.seed==z.seed)&(p.target==z.target)]
    assert len(d)==z.n and np.isclose(z.R2,r2_score(d.y,d.pred),rtol=1e-9,atol=1e-8) and np.isclose(z.RMSE,np.sqrt(mean_squared_error(d.y,d.pred)),rtol=1e-9)
    t=targets[z.target].set_index('can');assert np.allclose(d.y,t.loc[d.can].y)
checks['recomputed_catboost_metric_rows']=len(m);checks['prediction_rows']=len(p)
assert set(json.loads((R/'analysis/meta.json').read_text())['completed_models'])==set(MODELS)
checks['all_four_backbones_complete']=True
docs=[]
for path,old in [(C/'2026_10_11_Paper_2_edited-v10_modern_models_QHERO.docx',C/'2026_10_11_Paper_2_edited-v9_supervision_controls.docx'),(R/'Supplementary_Information_v10.docx',R.parent/'revision_v9/Supplementary_Information_v9.docx')]:
    with zipfile.ZipFile(path) as z,zipfile.ZipFile(old) as original:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith(('.xml','.rels')):E.fromstring(z.read(name))
        for name in original.namelist():
            if name.startswith('word/media/'):assert z.read(name)==original.read(name)
        for rel in E.fromstring(z.read('word/_rels/document.xml.rels')):
            if rel.get('TargetMode')!='External':assert posixpath.normpath(posixpath.join('word',rel.get('Target'))) in z.namelist()
        text=''.join(E.fromstring(z.read('word/document.xml')).itertext());assert 'S. aureus' in text
    docs.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'media_preserved':True,'xml_relationships_valid':True})
checks['documents']=docs
(R/'validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
