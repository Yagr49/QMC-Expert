"""Audit new DOCX structure, retained coauthor fields and numerical statements."""
from pathlib import Path
import hashlib,json,posixpath,re,zipfile
import xml.etree.ElementTree as E
import pandas as pd

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS={'w':W,'r':R,'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}

def inspect(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names=set(z.namelist())
        for name in names:
            if name.endswith(('.xml','.rels')):E.fromstring(z.read(name))
        tree=E.fromstring(z.read('word/document.xml'));body=tree.find('w:body',NS)
        rels={el.get('Id'):el for el in E.fromstring(z.read('word/_rels/document.xml.rels'))}
        for rel in rels.values():
            if rel.get('TargetMode')!='External':assert posixpath.normpath(posixpath.join('word',rel.get('Target'))) in names
        for el in tree.iter():
            for key,value in el.attrib.items():
                if key.startswith('{'+R+'}'):assert value in rels
        ids=[el.get('id') for el in tree.findall('.//wp:docPr',NS)];assert len(ids)==len(set(ids))
        styles={x.get('{'+W+'}styleId') for x in E.fromstring(z.read('word/styles.xml')).findall('w:style',NS)}
        for node in tree.findall('.//w:pPr/w:pStyle',NS):assert node.get('{'+W+'}val') in styles
        texts=[''.join(x.text or '' for x in p.findall('.//w:t',NS)).strip() for p in body]
    return texts,len(ids)

def main():
    old,_=inspect(COMA/'2026_10_11_Paper_2_edited-v11_JCIM_author_draft.docx')
    oldfields={re.search(r'\[COAUTHORS ([AHD]\d+)',p)[1]:p for p in old if re.search(r'\[COAUTHORS ([AHD]\d+)',p)}
    paths=[COMA/'2026_10_11_Paper_2_edited-v12_matched_finetuning.docx',ROOT/'Supplementary_Information_v12.docx']
    reports=[]
    for path in paths:
        texts,count=inspect(path);text='\n'.join(texts)
        if path==paths[0]:
            fields={re.search(r'\[COAUTHORS ([AHD]\d+)',p)[1]:p for p in texts if re.search(r'\[COAUTHORS ([AHD]\d+)',p)}
            assert fields==oldfields
            assert [int(re.match(r'^Figure (\d+)\.',p)[1]) for p in texts if re.match(r'^Figure (\d+)\.',p)]==[1,2,3,4,5]
            assert [int(re.match(r'^Table (\d+)\.',p)[1]) for p in texts if re.match(r'^Table (\d+)\.',p)]==[1,2,3,4]
            assert count==5
            assert '2.7. Matched partial backbone fine-tuning' in text
            assert '3.6. Matched partial fine-tuning' in text
            assert 'would connect these two observations' not in text
            assert 'no early stopping or target-based selection' in text
            assert 'distinct from an internal adapter or LoRA' in text
            s=pd.read_csv(ROOT/'analysis/summary.csv').query("target == 'Q-HERO-405'").set_index('arm')
            assert f"mean RMSE {s.loc['expert'].RMSE:.3f}" in text
            assert f"raw features yield {s.loc['raw-molformer'].RMSE:.3f}" in text
            c=pd.read_csv(ROOT/'analysis/contrasts.csv').query("target == 'Q-HERO-405' and unit == 'seed+scaffold'").set_index('comparison')
            for pair in ['expert minus expert-shuffled','expert minus raw-molformer','expert minus quant-continuous','expert minus quant-binary']:
                row=c.loc[pair];assert f'{row.delta_RMSE:+.3f} [{row.ci_low:+.3f}, {row.ci_high:+.3f}]' in text
        else:
            assert count==18
            assert [int(re.match(r'^Figure S(\d+)\.',p)[1]) for p in texts if re.match(r'^Figure S(\d+)\.',p)]==list(range(1,19))
            assert 'COAUTHORS C1' in text
            assert 'S16.6.4. MIC and MBC determination' in text
            for number in range(11,16):assert f'Table S{number}.' in text
        reports.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),figure_count=count,xml_relationships_styles_valid=True))
    draft=(ROOT/'main_draft.md').read_text();abstract=draft.split('## Abstract\n\n')[1].split('\n\n## Keywords')[0]
    assert len(re.split(r'(?<=[.!?])\s+(?=[A-Z])',abstract))==4
    assert len(abstract.split())<200
    for path in [ROOT/'figures/figure5_matched_finetuning.pdf',ROOT/'figures/figureS18_matched_finetuning_error_violins.pdf']:
        assert path.stat().st_size>10000
    report=dict(documents=reports,coauthor_fields_preserved=True,abstract_sentences=4,abstract_words=len(abstract.split()),source_validation='validation.json')
    (ROOT/'document_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
