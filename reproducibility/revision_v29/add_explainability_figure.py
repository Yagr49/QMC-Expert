"""Add the existing supervision-contrast figure to Section2.4 of immutable v28."""
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib, importlib.util, json
import pandas as pd

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
SOURCE=COMA/'2026_10_14_Paper_2_edited-v28_intro_aligned.docx'
OUTPUT=COMA/'2026_10_14_Paper_2_edited-v29_explainability_figure.docx'
FIGURE=ROOT.parent/'revision_v27/figures/figure10_supervision_contrasts_futura.png'
spec=importlib.util.spec_from_file_location('v25',ROOT.parent/'revision_v25/build_revision.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
b=v.b;NS=v.NS

CAPTION=('Figure 9. Predictive contribution of human supervision under matched controls. '
    '(a) External compact encoders: human minus continuous-MIC, shuffled-human or raw '
    'MolFormer errors. (b) Partial-backbone adaptation: human minus shuffled-human or '
    'raw MolFormer errors. Points show pooled ΔRMSE on log₂(mg/L); negative values '
    'favour human guidance. Lines are conditional 95% paired source-seed/group bootstrap '
    'intervals; hollow points mark intervals including zero. Five paired source runs '
    'are resampled with 103 cations for cation holdout, 29 scaffolds for scaffold '
    'holdout or 17 OOD cations. Compact and partial-backbone intervals use 10,000 '
    'and 5,000 resamples, respectively, with prediction models held fixed and no '
    'multiplicity adjustment. Cation-clustered intervals here differ from the '
    'scaffold-clustered sensitivity intervals quoted in the text. The architectures '
    'and decoders differ between panels; contrasts describe prediction procedures '
    'rather than biological causality or equivalence.')
LINK=('Figure 9 places these supervisory controls in a common visual comparison. '
    'For compact encoders, human guidance improves the raw OOD reference while '
    'remaining unresolved against the quantitative and shuffled-label controls '
    'under the displayed intervals. For the separate partial-backbone procedure, '
    'the displayed contrasts favour human guidance over raw and shuffled-human '
    'references. The difference between panels reinforces the dependence on '
    'adaptation and decoding, rather than an architecture-independent effect '
    'of human-label meaning.')

def sha(data):return hashlib.sha256(data).hexdigest()

def contrast_rows():
    compact=pd.read_csv(ROOT.parent/'revision_v18/analysis/contrasts.csv')
    backbone=pd.read_csv(ROOT.parent/'revision_v16/analysis/paired_bootstrap.csv')
    rows=[]
    for scheme,unit in [('cation','cation'),('scaffold','scaffold'),('full-QAC105','cation')]:
        for key in ['human minus mic_continuous','human minus human_shuffled','human minus matched_raw']:
            a=compact[compact.comparison.eq(key)&compact.schema.eq(scheme)&compact.unit.eq(unit)].iloc[0]
            assert a.n_seeds==5 and a.bootstrap_draws==10000
            rows.append(dict(panel='compact',comparison=key,schema=scheme,grouping=unit,
                delta=float(a.delta_RMSE),low=float(a.ci_low),high=float(a.ci_high),
                groups=int(a.n_clusters),seeds=5,draws=10000))
        for key,other in [('real_vs_shuffled','expert-shuffled/intact'),('source_vs_pure_raw','raw-molformer/raw')]:
            a=backbone[backbone.contrast.eq(key)&backbone.a.eq('expert/intact')&backbone.b.eq(other)&
                backbone.schema.eq(scheme)&backbone.grouping.eq(unit)].iloc[0]
            assert a.seeds==5 and a.draws==5000 and a.high<0
            rows.append(dict(panel='partial_backbone',comparison=key,schema=scheme,grouping=unit,
                delta=float(a.delta_RMSE_a_minus_b),low=float(a.low),high=float(a.high),
                groups=int(a.groups),seeds=5,draws=5000))
    assert len(rows)==15
    pd.DataFrame(rows).to_csv(ROOT/'inserted_figure_contrasts.csv',index=False)
    return rows

def main():
    ROOT.mkdir(exist_ok=True)
    infos,files=v.v.read(SOURCE);raw=files['word/document.xml']
    body=list(E.fromstring(raw).find('w:body',NS));spans=b.body_ranges(raw)
    start=next(i for i,n in enumerate(body) if b.text(n)=='2.4 Understanding the new embeddings')
    end=next(i for i,n in enumerate(body) if b.text(n)=='3. Conclusion')
    anchor=next(i for i in range(start,end) if b.text(body[i]).startswith('The stronger test of supervisory content'))
    template=body[anchor]
    original_cap=next(i for i,n in enumerate(body) if b.text(n).startswith('Figure 8.'))
    graphic=body[original_cap-1]
    new_nodes=[v.v.paragraph(template,'v29_explainability_link',LINK),
        v.v.v.figure(graphic,FIGURE,'rIdV29Explainability',299009),
        v.v.paragraph(body[original_cap],'v29_explainability_caption',CAPTION)]
    new_nodes[1].set('{'+b.W14+'}paraId',sha(b'v29_explainability_image')[:8].upper())
    insertion=b''.join(E.tostring(n,encoding='utf-8') for n in new_nodes)
    at=spans[anchor]['end'];newraw=raw[:at]+insertion+raw[at:]
    E.fromstring(newraw);files['word/document.xml']=newraw
    part='word/media/v29_'+FIGURE.name;files[part]=FIGURE.read_bytes()
    rel=E.tostring(E.Element('{'+v.v.v.REL+'}Relationship',{
        'Id':'rIdV29Explainability','Type':v.v.v.R+'/image','Target':part.removeprefix('word/')
        if hasattr(str,'removeprefix') else part[5:]}),encoding='utf-8')
    name='word/_rels/document.xml.rels';pos=files[name].rfind(b'</')
    files[name]=files[name][:pos]+rel+files[name][pos:]
    v.v.write(OUTPUT,infos,files)
    rows=contrast_rows()
    manifest=dict(source=str(SOURCE),source_sha256=sha(SOURCE.read_bytes()),output=str(OUTPUT),output_sha256=sha(OUTPUT.read_bytes()),
        figure_source=str(FIGURE),figure_sha256=sha(FIGURE.read_bytes()),main_figure_number=9,
        source_filename_number=10,section='2.4 Understanding the new embeddings',
        insertion_after_original_body_index=anchor,inserted_document_XML_sha256=sha(insertion),
        original_document_XML_retained=True,new_caption_and_reference_highlighted_yellow=True,
        existing_figures_unchanged=True,no_new_model_fits=True,contrasts=rows)
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2))
    (ROOT/'figure9_caption_EN.txt').write_text(CAPTION+'\n')
    v.v.export_html(files,ROOT/'MANUSCRIPT_REVIEW.html')
    print('Added existing contrast figure as mainFigure9 in Section2.4; sourcev28 preserved.')

if __name__=='__main__':main()
