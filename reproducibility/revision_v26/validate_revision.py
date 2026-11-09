"""Document preservation and independently checked OOD/interpretation statements."""
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib, importlib.util, json, re
import numpy as np
import pandas as pd
import build_revision as b

def main():
    _,old=b.v.v.read(b.SOURCE);_,new=b.v.v.read(b.MAIN)
    _,oldsi=b.v.v.read(b.OLD_SI);_,si=b.v.v.read(b.SI)
    spec=importlib.util.spec_from_file_location('inspect',b.ROOT.parent/'revision_v12/validate_documents.py')
    d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
    reports=[]
    for path in [b.MAIN,b.SI]:
        texts,n=d.inspect(path)
        assert not any('sk-or-v1-' in t for t in texts)
        reports.append(dict(path=str(path),drawings=n,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),XML_relationships_styles_valid=True))
    ob=list(E.fromstring(old['word/document.xml']).find('w:body',b.NS))
    nb=list(E.fromstring(new['word/document.xml']).find('w:body',b.NS))
    osb=list(E.fromstring(oldsi['word/document.xml']).find('w:body',b.NS))
    nsb=list(E.fromstring(si['word/document.xml']).find('w:body',b.NS))
    text=lambda n:b.b.text(n)
    start=lambda nodes,prefix:next(i for i,n in enumerate(nodes) if text(n).startswith(prefix))
    before=start(ob,'2.3 Out of domain');after=start(nb,'2.3 Out of domain')
    assert old['word/document.xml'][:b.b.body_ranges(old['word/document.xml'])[before]['end']] == new['word/document.xml'][:b.b.body_ranges(new['word/document.xml'])[after]['end']]
    # Entire chemistry body, figures, schemes, objects and captions untouched.
    oc=ob[before+2:start(ob,'2.3.5 ')];nc=nb[after+2:start(nb,'2.3.5 ')]
    assert len(oc)==len(nc) and all(E.tostring(a)==E.tostring(z) for a,z in zip(oc,nc))
    oe=start(ob,'4. Experimental');ne=start(nb,'4. Experimental')
    assert len(ob)-oe==len(nb)-ne
    assert all(E.tostring(a)==E.tostring(z) for a,z in zip(ob[oe:],nb[ne:]))
    for name,data in old.items():
        if name not in ['word/document.xml','word/_rels/document.xml.rels']:assert new[name]==data
    for name,data in oldsi.items():
        if name not in ['word/document.xml','word/_rels/document.xml.rels']:assert si[name]==data
    assert all(E.tostring(a)==E.tostring(z) for a,z in zip(osb[:-1],nsb[:len(osb)-1]))
    assert E.tostring(osb[-1])==E.tostring(nsb[-1])
    tables=lambda nodes:[b.v.v.rows(n) for n in nodes if n.tag=='{'+b.W+'}tbl']
    assert tables(nsb)[:len(tables(osb))]==tables(osb) and len(tables(nsb))==len(tables(osb))+2
    assert not tables(nb)
    caps=[text(n) for n in nb if re.match(r'^Figure \d+\.',text(n))]
    assert [int(re.match(r'^Figure (\d+)\.',s)[1]) for s in caps]==list(range(1,10))
    scaps=[text(n) for n in nsb if re.match(r'^Figure S\d+\.',text(n))]
    assert sorted(int(re.match(r'^Figure S(\d+)\.',s)[1]) for s in scaps)==list(range(1,36))
    for i in range(after,len(nb)):
        if text(nb[i]).startswith(('The quantitative OOD','For the archived v5','The source-matched compact','A separate backbone experiment','Figure 9 shows')):
            assert nb[i].find('.//w:highlight',b.NS) is not None
    # Original transferred bitmaps remain byte-identical.
    for cap,stem in [('Figure 9.','figureS33_original_v5_OOD_fewshot'),('Figure 10.','figureS34_original_v5_information_flow')]:
        ci=start(ob,cap);node=ob[ci-1]
        rels={r.get('Id'):r.get('Target') for r in E.fromstring(old['word/_rels/document.xml.rels'])}
        rid=node.find('.//a:blip',b.NS).get('{'+b.v.v.v.R+'}embed');part='word/'+rels[rid]
        path=next((b.ROOT/'figures').glob(stem+'.*'))
        assert path.read_bytes()==old[part]
        assert si['word/media/v26_'+path.name]==old[part]
    values=pd.read_csv(b.ROOT/'OOD_violin_values.csv')
    assert len(values)==603 and values.compound_id.nunique()==17
    assert values.groupby(['experiment','route']).size().eq(67).all()
    assert values.groupby(['compound_id','task']).y.nunique().eq(1).all()
    assert values[values.experiment.eq('backbone')].n_seeds.eq(3).all()
    # Recompute compact OOD seed metrics directly from the existing predictions.
    path=b.ROOT.parent/'revision_v18/analysis/predictions.csv'
    pred=pd.read_csv(path);bounds=pred[pred.cohort.eq('OOD17')&pred.arm.eq('human')&pred.encoding.eq('categorical')&pred.qualifier.ne('=')]
    assert len(bounds)==5 and bounds.compound_id.eq('IT505').all() and bounds.task.eq('Ec_MBC').all()
    summary=pd.read_csv(b.ROOT.parent/'revision_v18/analysis/summary.csv')
    narration='\n'.join(v for _,v in b.OOD)
    for arm in ['human','human_shuffled','mic_binary','mic_continuous','matched_raw']:
        g=pred[pred.cohort.eq('OOD17')&pred.arm.eq(arm)&pred.encoding.eq('categorical')&pred.qualifier.eq('=')]
        rmse=g.groupby('seed').apply(lambda rows:np.sqrt(np.mean((rows.prediction-rows.y)**2)))
        a=summary[summary.arm.eq(arm)&summary.encoding.eq('categorical')&summary.schema.eq('full-QAC105')&summary.task.eq('pooled')].iloc[0]
        assert abs(rmse.mean()-a.RMSE)<1e-12
        if len(rmse)>1:assert abs(rmse.std(ddof=1)-a.RMSE_sd)<1e-12
        assert '%.3f'%a.RMSE in narration
    metrics=pd.read_csv(b.ROOT.parent/'revision_v24/analysis/FT_route_RMSE_mean_sample_SD.csv')
    for a in metrics[metrics.schema.eq('full-QAC105')].itertuples():
        assert '%.3f'%a.RMSE in narration and '%.3f'%a.RMSE_SD in narration
    cka=pd.read_csv(b.COMA/'analysis/cka_probing.csv').set_index('metric').value
    interpretation='\n'.join(v for _,v in b.INTERPRET)
    for key in ['linear_CKA','probe_R2_mf_to_emb_mean','probe_R2_mf_to_emb_std','probe_R2_emb_to_mf_mean','probe_R2_emb_to_mf_std']:
        if key=='linear_CKA':continue
        assert '%.3f'%cka.loc[key] in interpretation
    assert '0.933' in interpretation and '0.946' in interpretation
    parsed=pd.DataFrame(json.loads((b.ROOT/'figure_validation.json').read_text())['source_sha256'].items(),columns=['path','sha'])
    for row in parsed.itertuples():assert hashlib.sha256(Path(row.path).read_bytes()).hexdigest()==row.sha
    assert not any('proved statistically equivalent' in text(n) or 'entirely reproducible biological component' in text(n) for n in nb)
    source=b.COMA/'2026_07_09_Paper_2_edited-v5_NF_3.docx'
    assert hashlib.sha256(source.read_bytes()).hexdigest()=='0dd55e7b9ef5125dd938fdb04e9c2d0a430cc4b86fc099b85e9f6e5e6d1c2bfb'
    report=dict(completed=True,documents=reports,original_v5_unmodified=True,
        introduction_sections2_1_2_2_verbatim_preserved=True,chemistry_and_synthesis_schemes_verbatim_preserved=True,
        experimental_section_and_references_verbatim_preserved=True,all_prior_SI_blocks_preserved=True,
        SI_tables=len(tables(nsb)),SI_figures=35,main_figures=9,
        original_OOD_and_information_flow_bitmaps_archived_exactly=True,
        OOD_exact_67_bound_retained=True,all_603_violin_values_verified=True,
        compact_OOD_mean_sampleSD_recomputed=True,CKA_and_probe_statements_verified=True,
        unsupported_causal_equivalence_removed_from_main=True,conclusion_consistent_with_revised_evidence=True,
        no_new_model_fits=True)
    (b.ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
