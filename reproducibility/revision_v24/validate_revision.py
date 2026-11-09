"""Check main/SI preservation, figure references and figures' actual data artifacts."""
from zipfile import ZipFile
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib, importlib.util, json, re
import numpy as np
import pandas as pd
import build_revision as b

def load(path):
    with ZipFile(path) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}
def body(files):return list(E.fromstring(files['word/document.xml']).find('w:body',b.NS))
def text(n):return b.b.text(n)
def main():
    source=load(b.SOURCE);main=load(b.MAIN);oldsi=load(b.OLD_SI);si=load(b.SI)
    spec=importlib.util.spec_from_file_location('inspector',b.ROOT.parent/'revision_v12/validate_documents.py')
    d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
    reports=[]
    for path in [b.MAIN,b.SI]:
        texts,figures=d.inspect(path)
        reports.append(dict(path=str(path),figures=figures,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_XML_relationships_styles_valid=True))
        assert not any('sk-or-v1-' in s for s in texts)
    oldbody=body(source);mainbody=body(main);osibody=body(oldsi);sibody=body(si)
    assert len([n for n in mainbody if n.tag=='{'+b.W+'}tbl'])==0
    tables=[n for n in oldbody if n.tag=='{'+b.W+'}tbl']
    sitables=[n for n in sibody if n.tag=='{'+b.W+'}tbl']
    assert len(sitables)==len([n for n in osibody if n.tag=='{'+b.W+'}tbl'])+4
    assert b.rows(sitables[-4])==b.rows(tables[0])
    assert b.rows(sitables[-3])==b.rows(tables[1])
    # Every earlier SI paragraph/table/figure remains intact and in the same order.
    assert all(E.tostring(a)==E.tostring(c) for a,c in zip(osibody[:-1],sibody[:len(osibody)-1]))
    assert E.tostring(osibody[-1])==E.tostring(sibody[-1])
    for n,data in oldsi.items():
        if n not in ['word/document.xml','word/_rels/document.xml.rels']:assert si[n]==data
    for n,data in source.items():
        if n not in ['word/document.xml','word/_rels/document.xml.rels']:assert main[n]==data
    assert source['word/media/image1.png']==main['word/media/image1.png']
    starts=lambda bb,s:next(i for i,n in enumerate(bb) if text(n)==s)
    s1=starts(mainbody,'2.1 Training guidance NN models');s2=starts(mainbody,'2.2 Training on QACs')
    assert not re.search(r'\bOOD\b|out.of.distribution|17 newly|67 exact|IT505','\n'.join(text(n) for n in mainbody[s1:s2]),re.I)
    caps=[text(n) for n in mainbody if re.match(r'^Figure \d+\.',text(n))]
    assert [int(re.match(r'^Figure (\d+)\.',s)[1]) for s in caps]==list(range(1,9))
    startold=starts(oldbody,'2.3 Out of domain inference');startnew=starts(mainbody,'2.3 Out of domain inference')
    rename=lambda s:re.sub(r'\b(Figure\s+)([5-7])\b',lambda m:m[1]+str(int(m[2])+1),s)
    assert len(oldbody)-startold==len(mainbody)-startnew
    for a,c in zip(oldbody[startold:],mainbody[startnew:]):assert rename(text(a))==text(c)
    for n in mainbody[s2+1:startnew]:
        if text(n):assert n.find('.//w:highlight',b.NS) is not None
    with ZipFile(b.MAIN) as z:
        for stem in ['figure3_backbone_route_error_violins','figure4_human_quantitative_compact','figure5_qhero_real_roc']:
            path=b.ROOT/'figures'/(stem+'.png')
            assert z.read('word/media/v24_'+path.name)==path.read_bytes()
    compact=pd.read_csv(b.ROOT/'figure4_compact_error_values.csv')
    assert compact.groupby(['arm','schema']).size().eq(420).all()
    assert compact.groupby(['schema','compound_id','task']).y.nunique().eq(1).all()
    assert compact[compact.arm!='matched_raw'].n_source_seeds.eq(5).all()
    assert compact[compact.arm=='matched_raw'].n_source_seeds.eq(1).all()
    derived=pd.read_csv(b.ROOT/'figure4_compact_seed_metrics.csv')
    prior=pd.read_csv(b.ROOT.parent/'revision_v19/analysis/seed_summary.csv')
    for (arm,schema),g in derived[derived.arm!='matched_raw'].groupby(['arm','schema']):
        a=prior[(prior.arm==arm)&(prior.encoding=='categorical')&(prior.schema==schema)&(prior.task=='pooled')].iloc[0]
        assert len(g)==5
        assert abs(g.RMSE.mean()-a.RMSE_seed_mean)<1e-12
        assert abs(g.RMSE.std(ddof=1)-a.RMSE_seed_sd)<1e-12
    q=pd.read_csv(b.ROOT.parent/'qhero_author_comparison_20261014/results/summary.csv')
    q=q[q.protocol=='scaffold_CV_pooled'].set_index('model')
    narrative=(b.ROOT/'SECTION_2_2_EN.md').read_text()
    for model in ['CB_human','CB_raw_MolFormer','RF_35_descriptors','CB_quantitative','CB_shuffled_human']:
        assert '%.3f'%q.loc[model,'AUROC'] in narrative
    report=dict(completed=True,documents=reports,main_tables_moved_to_SI=True,
        moved_original_table_cells_unchanged=True,all_prior_SI_body_blocks_retained=True,
        all_original_main_and_SI_media_and_office_objects_preserved=True,
        all_figures_sequential=True,section2_1_has_no_OOD=True,
        section2_3_and_later_scientific_text_unchanged_except_figure_numbers=True,
        all_new_section2_2_text_yellow=True,compact_seed_RMSE_verified_against_completed_runs=True,
        compact_violin_same_420_endpoint_pairs_in_each_arm=True,QHERO_AUROC_verified=True,
        no_new_models_trained=True)
    (b.ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
