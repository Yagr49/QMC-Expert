"""Independent checks of numbers, paired design and DOCX packaging."""
from pathlib import Path
import json, hashlib, zipfile, posixpath, io
import xml.etree.ElementTree as E
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score,mean_squared_error
ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
checks={}
meta=json.loads((ROOT/'data/meta.json').read_text())
for path,digest in meta['inputs'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
checks['input_file_hashes']=len(meta['inputs'])
targets={p.stem:pd.read_csv(p) for p in (ROOT/'data').glob('target_*.csv')}
ban=set().union(*(set(d.cation) for d in targets.values()))
for p in (ROOT/'data').glob('source_*.csv'):
    d=pd.read_csv(p);assert not set(d.cation)&ban
for panel in ['matched-pooled','matched-sa']:
    a=pd.read_csv(ROOT/'data'/f'{panel}_expert.csv');b=pd.read_csv(ROOT/'data'/f'{panel}_quant.csv')
    assert a.can.tolist()==b.can.tolist()
    assert a.scaffold.tolist()==b.scaffold.tolist()
checks['all_source_target_cation_overlap']=0
checks['target_sizes']={k:len(v) for k,v in targets.items()}
x=np.load(ROOT/'data/molformer.npy');assert np.isfinite(x).all() and x.shape[1]==768
checks['finite_backbone_features']=list(x.shape)
result=ROOT/'results_matched-pooled_matched-sa_full'
training=pd.read_csv(result/'training.csv')
assert len(training)==80
for _,g in training[training.panel.str.startswith('matched')].groupby(['panel','seed']):
    assert len(g)==6 and g.init_sha256.nunique()==1 and g.train_identity_sha256.nunique()==1
checks['paired_initialisation_and_source_identities']=True
pred=pd.read_csv(result/'predictions.csv');metrics=pd.read_csv(result/'metrics.csv')
assert not pred.duplicated(['panel','arm','head','seed','target','can']).any()
assert np.isfinite(pred[['y','pred']].values).all()
assert len(metrics)==486
for _,r in metrics.iterrows():
    p=pred[(pred.panel==r.panel)&(pred.arm==r.arm)&(pred['head']==r['head'])&(pred.seed==r.seed)&(pred.target==r.target)]
    assert len(p)==r.n
    assert np.isclose(r.R2,r2_score(p.y,p.pred),rtol=1e-8,atol=1e-9)
    assert np.isclose(r.RMSE,np.sqrt(mean_squared_error(p.y,p.pred)),rtol=1e-8)
    tgt=targets['target_'+r.target].set_index('can')
    assert np.allclose(p.y,tgt.loc[p.can].y.values)
checks['independently_recomputed_metric_rows']=len(metrics)
checks['prediction_rows']=len(pred)
fold=pd.read_csv(result/'target_folds.csv')
for _,d in fold.groupby('target'):
    target=targets['target_'+d.target.iloc[0]].set_index('can')
    d=d.assign(scaffold=target.loc[d.can].scaffold.values)
    assert d.groupby('scaffold').fold.nunique().max()==1
checks['target_scaffolds_disjoint_between_folds']=True
paired=pd.read_csv(ROOT/'analysis/paired_bootstrap.csv')
assert (paired.ci_low<=paired.ci_high).all() and np.isfinite(paired[['delta_RMSE','ci_low','ci_high']]).all().all()
checks['paired_intervals']=len(paired)
assert json.loads((ROOT/'analysis/analysis_meta.json').read_text())['complete']
docs=[]
for new,old in [
    (COMA/'2026_10_11_Paper_2_edited-v9_supervision_controls.docx',COMA/'2026_07_09_Paper_2_edited-v8_scientifically_revised.docx'),
    (ROOT/'Supplementary_Information_v9.docx',COMA/'reproducibility/Supplementary_Information_v8_scientifically_revised.docx')]:
    with zipfile.ZipFile(new) as z,zipfile.ZipFile(old) as before:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith('.xml') or name.endswith('.rels'):E.fromstring(z.read(name))
        for name in before.namelist():
            if name.startswith('word/media/'):assert z.read(name)==before.read(name)
        for relationship in E.fromstring(z.read('word/_rels/document.xml.rels')):
            if relationship.get('TargetMode')!='External':
                target=relationship.get('Target')
                resolved=posixpath.normpath(posixpath.join('word',target))
                assert resolved in z.namelist(),resolved
        doc=E.fromstring(z.read('word/document.xml'))
        rels={r.get('Id') for r in E.fromstring(z.read('word/_rels/document.xml.rels'))}
        for el in doc.iter():
            for attr in [f'{{{R}}}embed',f'{{{R}}}id',f'{{{R}}}link']:
                if attr in el.attrib:assert el.attrib[attr] in rels
        # iterparse yields (event,(prefix,uri)).
        bindings={prefix:uri for event,(prefix,uri) in E.iterparse(io.BytesIO(z.read('word/document.xml')),events=['start-ns'])}
        ignorable=doc.get('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable','').split()
        assert all(p in bindings for p in ignorable)
        docs.append({'path':str(new),'original_media_preserved':True,'xml_and_relationships_valid':True,'sha256':hashlib.sha256(new.read_bytes()).hexdigest()})
checks['documents']=docs
(ROOT/'validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
