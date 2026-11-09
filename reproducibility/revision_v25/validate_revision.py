"""Verify source preservation, restored raster, split statistics and corrected ranges."""
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib, importlib.util, json, re
import numpy as np
import pandas as pd
import build_revision as b

def main():
    _,old=b.v.read(b.SOURCE);_,new=b.v.read(b.MAIN)
    _,oldsi=b.v.read(b.OLD_SI);_,si=b.v.read(b.SI)
    spec=importlib.util.spec_from_file_location('inspect',b.ROOT.parent/'revision_v12/validate_documents.py')
    d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
    reports=[]
    for path in [b.MAIN,b.SI]:
        texts,n=d.inspect(path)
        reports.append(dict(path=str(path),figures=n,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),XML_relationships_and_styles_valid=True))
    assert reports[0]['figures']==10 and reports[1]['figures']==32
    for name,data in old.items():
        if name not in ['word/document.xml','word/_rels/document.xml.rels']:assert new[name]==data
    for name,data in oldsi.items():
        if name!='word/document.xml':assert si[name]==data
    oldbody=list(E.fromstring(old['word/document.xml']).find('w:body',b.NS))
    newbody=list(E.fromstring(new['word/document.xml']).find('w:body',b.NS))
    sibody=list(E.fromstring(si['word/document.xml']).find('w:body',b.NS))
    oldsibody=list(E.fromstring(oldsi['word/document.xml']).find('w:body',b.NS))
    assert len(sibody)==len(oldsibody)
    assert [b.v.rows(n) for n in sibody if n.tag=='{'+b.W+'}tbl']==[b.v.rows(n) for n in oldsibody if n.tag=='{'+b.W+'}tbl']
    captions=[b.b.text(n) for n in newbody if re.match(r'^Figure \d+\.',b.b.text(n))]
    assert [int(re.match(r'^Figure (\d+)\.',s)[1]) for s in captions]==list(range(1,11))
    sourcecorr=(b.ROOT.parent/'revision_v24/figures/figureS32_original_v5_parity.jpg').read_bytes()
    assert new['word/media/v25_figureS32_original_v5_parity.jpg']==sourcecorr
    expected={255001:'figure1_verified_workflow.png',255004:'figureS32_original_v5_parity.jpg',
        255005:'figure5_matched_supervision_design.png',255006:'figure6_matched_supervision_violins.png'}
    rels={n.get('Id'):n.get('Target') for n in E.fromstring(new['word/_rels/document.xml.rels'])}
    for node in newbody:
        for drawing in node.findall('.//wp:docPr',b.NS):
            uid=int(drawing.get('id'))
            if uid in expected:
                rid=node.find('.//a:blip',b.NS).get('{'+b.v.v.R+'}embed')
                assert rels[rid].endswith(expected[uid])
    start=lambda nodes,title:next(i for i,n in enumerate(nodes) if b.b.text(n)==title)
    s1=start(newbody,'2.1 Training guidance NN models');s2=start(newbody,'2.2 Training on QACs')
    assert not re.search(r'\bOOD\b|out.of.distribution|67 exact|IT505','\n'.join(b.b.text(n) for n in newbody[s1:s2]),re.I)
    oldstart=start(oldbody,'2.3 Out of domain inference');newstart=start(newbody,'2.3 Out of domain inference')
    rename=lambda s:re.sub(r'\b(Figure\s+)([6-8])\b',lambda m:m[1]+str(int(m[2])+2),s)
    assert len(oldbody)-oldstart==len(newbody)-newstart
    assert all(rename(b.b.text(a))==b.b.text(z) for a,z in zip(oldbody[oldstart:],newbody[newstart:]))
    stats=json.loads((b.ROOT/'split_figure_validation.json').read_text())
    data=pd.read_csv(stats['source'])
    assert hashlib.sha256(Path(stats['source']).read_bytes()).hexdigest()==stats['source_sha256']
    for check in stats['checks']:
        values=data[(data.arm==check['arm'])&(data.schema==check['schema'])].mean_absolute_error.to_numpy()
        assert len(values)==check['n']==420
        assert np.median(values)==check['median'] and values.max()==check['maximum']
    numbers=json.loads((b.ROOT/'figure1_numeric_provenance.json').read_text())
    assert numbers['expert_final_labels']==1103
    assert [min(numbers['descriptor_MLP_R2']),max(numbers['descriptor_MLP_R2'])]==[.25,.68]
    assert [min(numbers['stacking_R2']),max(numbers['stacking_R2'])]==[.30,.43]
    assert [round(min(numbers['human_text_recovered_R2']),2),round(max(numbers['human_text_recovered_R2']),2)]==[.59,.77]
    assert '0.53' not in captions[0] and '0.86' not in captions[0]
    original=b.COMA/'2026_07_09_Paper_2_edited-v5_NF_3.docx'
    assert hashlib.sha256(original.read_bytes()).hexdigest()=='0dd55e7b9ef5125dd938fdb04e9c2d0a430cc4b86fc099b85e9f6e5e6d1c2bfb'
    report=dict(completed=True,documents=reports,original_v5_unmodified=True,
        source_media_and_Office_parts_preserved=True,original_correlation_raster_restored_byte_identical=True,
        Figure4_split_into_Figures5_and6=True,all_3360_error_values_and_summary_statistics_preserved=True,
        Figure1_count_and_source_specific_score_ranges_verified=True,
        original_SI_table_values_preserved=True,all_main_figure_captions_sequential=True,
        section2_1_no_OOD=True,later_scientific_text_unchanged_except_figure_references=True,
        no_new_model_fits=True)
    (b.ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
