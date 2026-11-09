"""Validate scientific-number retention, DOCX integrity and author fields."""
from pathlib import Path
import hashlib, json, posixpath, re, zipfile
import xml.etree.ElementTree as E
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS={'w':W,'r':R,'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
docs=[COMA/'2026_10_11_Paper_2_edited-v11_JCIM_author_draft.docx',
      ROOT/'Supplementary_Information_v11.docx',ROOT/'Human_annotation_methods_for_coauthors.docx']
checks={'new_experiments_run':False,'source_validation':'../revision_v10/validation.json'}
source=json.loads((ROOT.parent/'revision_v10/validation.json').read_text())
assert source['recomputed_catboost_metric_rows']==687 and source['source_target_cation_overlap']==0
checks['existing_prediction_metric_validation']=source['recomputed_catboost_metric_rows']
checks['documents']=[]
for path in docs:
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names=set(z.namelist())
        for name in names:
            if name.endswith(('.xml','.rels')):E.fromstring(z.read(name))
        tree=E.fromstring(z.read('word/document.xml'))
        body=tree.find('w:body',NS)
        rels={el.get('Id'):el for el in E.fromstring(z.read('word/_rels/document.xml.rels'))}
        for rel in rels.values():
            if rel.get('TargetMode')!='External':
                assert posixpath.normpath(posixpath.join('word',rel.get('Target'))) in names,(path,rel.attrib)
        for el in tree.iter():
            for key,value in el.attrib.items():
                if key.startswith('{'+R+'}'):assert value in rels,(path,key,value)
        ids=[el.get('id') for el in tree.findall('.//wp:docPr',NS)]
        assert len(ids)==len(set(ids))
        styles={x.get('{'+W+'}styleId') for x in E.fromstring(z.read('word/styles.xml')).findall('w:style',NS)}
        for style in tree.findall('.//w:pPr/w:pStyle',NS):assert style.get('{'+W+'}val') in styles
        text='\n'.join(''.join(el.text or '' for el in p.findall('.//w:t',NS)) for p in body)
        texts=[''.join(el.text or '' for el in p.findall('.//w:t',NS)).strip() for p in body]
        fields=re.findall(r'\[COAUTHORS ([HDCA]\d+)\b',text)
        if path==docs[0]:
            assert fields==['A1','H1','H2','H3','H4','H5','H6','H7','D1','D2']
            captions=[int(re.match(r'^Figure (\d+)\.',x)[1]) for x in texts if re.match(r'^Figure (\d+)\.',x)]
            tables=[int(re.match(r'^Table (\d+)\.',x)[1]) for x in texts if re.match(r'^Table (\d+)\.',x)]
            assert captions==[1,2,3,4] and tables==[1,2,3]
            assert len(tree.findall('.//wp:docPr',NS))==4
            assert 'partial backbone fine-tuning' in text.lower()
            assert '377 training and 304 validation' in text
            assert 'measurement equivalence' in text and 'no non-inferiority margin' in text
            assert 'COAUTHORS H4' in text and 'quantitative supervision were available' in text
            assert 'OpenAI Codex' in text and 'Kimi Code' in text
            with zipfile.ZipFile(COMA/'2026_10_11_Paper_2_edited-v10_modern_models_QHERO.docx') as old:
                for name in old.namelist():
                    if name.startswith('word/media/'):assert z.read(name)==old.read(name)
        elif path==docs[1]:
            captions=[int(re.match(r'^Figure S(\d+)\.',x)[1]) for x in texts if re.match(r'^Figure S(\d+)\.',x)]
            tables=[int(re.match(r'^Table S(\d+)\.',x)[1]) for x in texts if re.match(r'^Table S(\d+)\.',x)]
            assert captions==list(range(1,17)),captions
            assert tables==list(range(1,10)),tables
            assert 'S16.6.4. MIC and MBC determination' in text
            with zipfile.ZipFile(ROOT.parent/'revision_v10/Supplementary_Information_v10.docx') as old:
                for name in old.namelist():
                    if name.startswith('word/media/'):assert z.read(name)==old.read(name)
        else:
            assert fields==['H1','H2','H3','H4','H5','H6','H7']
        checks['documents'].append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'xml_relationships_styles_valid':True,'coauthor_fields':fields,
            'figure_count':len(tree.findall('.//wp:docPr',NS))})

# Abstract format and bibliography sequence are verified on the editable source.
draft=(ROOT/'main_draft.md').read_text()
abstract=draft.split('## Abstract\n\n')[1].split('\n\n## Keywords')[0]
assert len(re.split(r'(?<=[.!?])\s+(?=[A-Z])',abstract))==4
title=draft.splitlines()[0][2:];assert len(title.split())<=12
checks['title_words']=len(title.split());checks['abstract_sentences']=4
checks['abstract_words']=len(abstract.split())

# Check the data plotted in the new partial-fine-tuning/direct figure.
fig=json.loads((ROOT/'figure2_values.json').read_text())
arch=ROOT.parent/'finetune'
quality=pd.DataFrame([json.loads(x) for x in (arch/'runs.jsonl').read_text().splitlines()])
direct=pd.DataFrame([json.loads(x) for x in (arch/'runs_direct.jsonl').read_text().splitlines()])
for row in fig['sources']:
    a=quality[(quality.target=='Q-HERO')&(quality.representation=='FT '+row['source'])].R2
    b=direct[(direct.target=='Q-HERO')&(direct.representation=='FT '+row['source']+' (direct)')].rank_agreement
    assert len(a)==len(b)==3
    assert np.isclose(a.mean(),row['downstream_R2']) and np.isclose(b.mean(),row['direct_rank'])
checks['new_figure_uses_archived_three_seed_results']=True

# Main-document tables must reproduce the prior numerical summaries unchanged.
old=pd.read_csv(ROOT.parent/'revision_v10/analysis/summary.csv')
with zipfile.ZipFile(docs[0]) as z:
    body=E.fromstring(z.read('word/document.xml')).find('w:body',NS)
    tables=body.findall('w:tbl',NS)
    def rows(table):return [[''.join(c.itertext()).strip() for c in r.findall('w:tc',NS)] for r in table.findall('w:tr',NS)]
    back=rows(tables[1]);context=rows(tables[2])
    for cells,model in zip(back[1:],['molformer','c3-molformer','chemberta100m','chemfm1b']):
        for cell,arm,panel in zip(cells[1:],['raw-'+model,'expert','quant-continuous','expert-shuffled'],['baseline','matched-pooled','matched-pooled','matched-pooled']):
            m=old[(old.backbone==model)&(old.panel==panel)&(old.arm==arm)&(old.target=='Q-HERO-405')].iloc[0]
            assert cell.startswith(f'{m.RMSE:.3f}'),(cell,m.RMSE)
    for cells,arm in zip(context[1:],['expert','quant-pooled','quant-sa','quant-pooled-shuffled','quant-sa-shuffled']):
        m=old[(old.backbone=='molformer')&(old.panel=='context')&(old.arm==arm)&(old.target=='Q-HERO-405')].iloc[0]
        assert cells[3]==f'{m.R2:+.3f}' and cells[4]==f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}'
checks['modern_and_context_tables_match_original_results']=True
checks['status']='author draft; annotation, archive and primary chemistry fields pending'
(ROOT/'validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
