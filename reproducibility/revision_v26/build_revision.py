"""Revise OOD evaluation and interpretation while retaining source chemistry and artifacts."""
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib, importlib.util, json
import pandas as pd

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
SOURCE=COMA/'2026_10_14_Paper_2_edited-v25_correlations_and_split_figures.docx'
OLD_SI=ROOT.parent/'revision_v25/Supplementary_Information_v25.docx'
MAIN=COMA/'2026_10_14_Paper_2_edited-v26_OOD_and_interpretation.docx'
SI=ROOT/'Supplementary_Information_v26.docx'
s=importlib.util.spec_from_file_location('v25',ROOT.parent/'revision_v25/build_revision.py')
v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
b=v.b;NS=v.NS;W=v.W

def sha(data):return hashlib.sha256(data).hexdigest()
def p(template,label,text,highlight=True):
    for old,new in {'Section2.2':'Section 2.2','Section2.3.5':'Section 2.3.5',
        'mainSection':'main Section','mainFigure9':'main Figure 9','FigureS35':'Figure S35',
        'TableS46':'Table S46','the17-compound':'the 17-compound','with67':'with 67',
        'the105-QAC':'the 105-QAC','and67':'and 67','Conditional95%':'Conditional 95%',
        'conditional95%':'conditional 95%','uses10,000':'uses 10,000',
        'backbone5,000':'backbone 5,000','cell4':'cell 4'}.items():text=text.replace(old,new)
    return v.v.paragraph(template,'v26_'+label,text,highlight)
def img(files,template,path,rid,uid):
    name='v26_'+path.name;files['word/media/'+name]=path.read_bytes()
    rel=E.tostring(E.Element('{'+v.v.v.REL+'}Relationship',{'Id':rid,'Type':v.v.v.R+'/image','Target':'media/'+name}),encoding='utf-8')
    key='word/_rels/document.xml.rels';at=files[key].rfind(b'</')
    files[key]=files[key][:at]+rel+files[key][at:]
    return v.v.v.figure(template,path,rid,uid)

OOD=[
('protocol','The quantitative OOD comparison uses all 17 compounds and the four MIC/MBC '
    'endpoints against S. aureus and E. coli. Each target predictor is fitted on the original '
    '105-QAC cohort before the new compounds are evaluated. Of the 68 endpoint records, '
    '67 are exact and IT505 E. coli MBC is reported as >500 mg/L. We retain this bound '
    'separately and exclude it from exact-error scores, rather than treating 500 mg/L '
    'as a measured concentration. Errors are evaluated on the log₂(mg/L) scale. The '
    'strict source-matched follow-ups exclude target cations from encoder-training panels; '
    'their frozen-source prediction protocol is distinct from the historical few-shot '
    'analysis retained in Figure S33.'),
('reference','For the archived v5 compact human encoder, the new fixed-feature decoder '
    'calculation gives pooled OOD RMSE 2.023 with text task codes, versus 2.245 for raw '
    'MolFormer under the same text-code decoder protocol. These are point estimates '
    'from one archived source checkpoint; no source-run SD is available. Historical '
    'source overlap with the original QAC targets distinguishes this reference from the '
    'source-excluded controls below. Full task-coding and endpoint results are in '
    'Tables S35–S36 and S49. The full-corpus quantitative checkpoint from the original '
    'Table S46 is not substituted by the available QAC-only ablation.'),
('compact','The source-matched compact encoders from Section2.2 provide a stricter test '
    'of supervisory content. With fixed categorical task codes, OOD RMSE is '
    '2.268 ± 0.077 for human guidance, 2.276 ± 0.095 for binary MIC guidance and '
    '2.474 ± 0.131 for continuous MIC guidance; the fixed raw reference gives 2.504. '
    'Here ± is sample SD across five source runs. Shuffled-human supervision gives '
    '2.172 ± 0.112, so these results do not establish an advantage of meaningful '
    'human-label assignment. Human minus raw has ΔRMSE −0.236, with conditional '
    'four-family bootstrap interval [−0.524, −0.016], whereas human minus shuffled '
    'has +0.096 [−0.143, +0.283]. Thus the representation-learning procedure can '
    'improve the raw reference without demonstrating a uniquely human semantic effect.'),
('backbone','A separate backbone experiment tests whether grouped-validation performance '
    'persists under the new chemical families. Full fine-tuning gives OOD RMSE '
    '3.032 ± 0.408, LoRA 2.756 ± 0.172 and the frozen pretrained backbone with a '
    'linear head 2.560 ± 0.206. Human-guided partial-backbone direct prediction gives '
    '2.412 ± 0.088, compared with 2.106 ± 0.071 for frozen human-guided source '
    'features decoded with CatBoost. These five routes use three runs, and the two '
    'human routes share source checkpoints. The direct-minus-decoder point contrast '
    'is +0.306, with conditional four-family interval [−0.278, +0.971]. The lower '
    'decoder point loss is therefore not a resolved generalisation advantage at this '
    'sample size, and the route comparison changes decoding and adaptation together.'),
('figure','Figure 9 shows the observed OOD error distributions for the compact and '
    'backbone experiments in separate panels. The 17 molecules cover four scaffold '
    'families rather than 67 independent biological replicates. Endpoint errors within '
    'one compound and across runs are dependent, and variation over four families '
    'remains poorly determined. Censor sensitivity, per-endpoint scores and complete '
    'run statistics are reported in SI. These results support conditional predictive '
    'usefulness under the stated protocols; they do not establish universal superiority '
    'or equivalence of human and quantitative supervision.')]

INTERPRET=[
('geometry','The human embeddings are learned transformations of frozen MolFormer '
    'features. We therefore ask separately how much geometry is retained, how the '
    'quantitative decoder uses the transformed features, and whether matched label '
    'assignment or learned weights affect prediction. The archived similarity analysis '
    'gives linear CKA 0.933 in-domain and 0.946 on the new compounds. Five-fold linear '
    'probes recover human features from MolFormer with R² 0.891 ± 0.037 and MolFormer '
    'features from human embeddings with R² 0.844 ± 0.060, where ± is fold SD. '
    'These results describe shared geometry and linear recoverability, rather than '
    'an identified partition into structural and biological information.'),
('shap','In the archived concatenated-feature CatBoost model, summed mean absolute '
    'SHAP values on the 67 exact OOD endpoints are 2.930 for MolFormer features, '
    '0.636 for human features and 0.761 for the task identifier. The human-to-MolFormer '
    'block ratio is 0.217. These attributions describe how that fitted model allocates '
    'prediction contributions among correlated feature blocks of different dimensions. '
    'They are neither fractions of biological variance nor evidence for a separate '
    'causal knowledge channel. Detailed archived geometry and attribution results '
    'remain in SI, together with the original conceptual diagram in Figure S34.'),
('controls','The stronger test of supervisory content is a comparison with shuffled '
    'labels on the same source molecules and training budget. For the compact v5 '
    'architecture, shuffled-human guidance remains competitive under grouped and '
    'OOD evaluation (Figures 6 and 9). A separate human-guided partial-backbone '
    'experiment does resolve a lower cation-held-out error than its shuffled control: '
    'ΔRMSE −0.120, conditional 95% interval [−0.217, −0.043]. The Q-HERO scaffold '
    'comparison similarly favours human over shuffled guidance (Section2.2). These '
    'results locate usefulness within particular adaptation procedures and target '
    'distributions; they do not support an architecture-independent semantic effect.'),
('weights','Weight interventions provide a complementary check. Restoring source '
    'encoder weights in the partial-backbone experiment raises cation-held-out '
    'RMSE by +0.109, conditional interval [+0.037, +0.201], while scaffold and '
    'four-family OOD intervals include zero. The compact weight-reset experiment '
    'does not resolve a corresponding effect and retains BatchNorm state, so it '
    'is distinct from an entirely untrained encoder. Figure S35 and Table S50 '
    'show the full contrasts for both architectures. Such interventions address '
    'dependence of the prediction procedure on learned updates, rather than a '
    'causal effect of a molecular fragment on antibacterial activity.'),
('interpretation','The evidence supports a compact, task-oriented transformation of '
    'a pretrained molecular representation whose quantitative usefulness depends '
    'on source supervision, adaptation and decoding. Close prediction scores or '
    'intervals spanning zero do not establish equivalence without an appropriate '
    'design and a justified prespecified margin. The historical residual-based '
    'causal-forest analysis likewise does not identify biological causality or '
    'equivalence to the full quantitative corpus; its protocol and limitations '
    'are retained in SI. Confirmation of what numerical information annotators '
    'saw remains necessary before assigning an independent human-knowledge '
    'interpretation to their labels.')]

CONCLUSION=[
('scope','We combined expert guidance with pretrained molecular features to predict '
    'four antibacterial MIC/MBC endpoints for QACs and evaluated transfer to '
    '17 newly synthesised compounds from four chemical families. The reference '
    'results show that expert-guided compact embeddings can support competitive '
    'quantitative prediction when combined with a task-aware decoder.'),
('supervision','The completed source-matched experiments refine this conclusion. '
    'Human and quantitative guidance can yield useful representations, but their '
    'ordering depends on architecture, decoder and evaluation protocol. Shuffled '
    'labels remain competitive for the compact encoder, whereas particular '
    'partial-backbone experiments, including Q-HERO scaffold classification, '
    'support a contribution from meaningful label assignment. Statistical '
    'equivalence, universal superiority and a label-to-measurement exchange '
    'rate are not established.'),
('adaptation','Full fine-tuning improves some grouped target scores but gives '
    'higher OOD error under the tested budget; frozen human-guided features '
    'with CatBoost give the lower OOD point loss among the tested backbone '
    'routes. The small four-family sample limits uncertainty assessment. '
    'Geometry, SHAP and computational controls clarify feature reuse and '
    'prediction dependence without identifying an antibacterial mechanism. '
    'Structured expert labels are therefore a practical supervision source '
    'whose value should be assessed with matched numerical and shuffled '
    'controls, alongside complete annotation provenance.')]

def main():
    ROOT.mkdir(exist_ok=True);infos,files=v.v.read(SOURCE);original=files['word/document.xml']
    body=list(E.fromstring(original).find('w:body',NS));spans=b.body_ranges(original)
    index=lambda prefix:next(i for i,n in enumerate(body) if b.text(n).startswith(prefix))
    first=index('2.3 Out of domain');evaluation=index('2.3.5 ');interpret=index('2.4 ')
    conclusion=index('3. Conclusion');experimental=index('4. Experimental')
    template=body[index('To verify out-of-domain')];cap9=index('Figure 9.');cap10=index('Figure 10.')
    original_eval=body[evaluation+1:interpret];original_interpret=body[interpret+1:conclusion]
    oldfigure9=body[cap9-1];oldfigure10=body[cap10-1]
    paragraphs=[p(template,'ood_'+label,value) for label,value in OOD]
    paragraphs.extend([img(files,oldfigure9,ROOT/'figures/figure9_OOD17_prediction_errors.png','rIdV26OOD',266009),
        p(body[cap9],'ood_caption',(ROOT/'figure9_caption_EN.txt').read_text().strip())])
    newinterpret=[p(template,'interpret_'+label,value) for label,value in INTERPRET]
    newconclusion=[p(template,'conclusion_'+label,value) for label,value in CONCLUSION]
    intro=p(body[first+1],'ood_intro','To evaluate prediction beyond the reference chemical '
        'families, we assembled a set of 17 newly synthesised QACs across four scaffolds: '
        'kojic acid, tetrahydropyridine, dihydropyran and glycoluril derivatives. These '
        'cover mono-, bis- and multi-QAC architectures (Figure 8). Their independent '
        'MIC/MBC measurements form the structural OOD case study described below; '
        'the new computational evaluation keeps these measurements outside target '
        'model training and assesses quantitative predictions in Section2.3.5.')
    edits=[(spans[first+1]['start'],spans[first+1]['end'],E.tostring(intro,encoding='utf-8')),
        (spans[evaluation]['end'],spans[interpret]['start'],b''.join(E.tostring(n,encoding='utf-8') for n in paragraphs)),
        (spans[interpret]['end'],spans[conclusion]['start'],b''.join(E.tostring(n,encoding='utf-8') for n in newinterpret)),
        (spans[conclusion]['end'],spans[experimental]['start'],b''.join(E.tostring(n,encoding='utf-8') for n in newconclusion))]
    updated=original
    for a,z,blob in sorted(edits,reverse=True):updated=updated[:a]+blob+updated[z:]
    E.fromstring(updated);files['word/document.xml']=updated;v.v.write(MAIN,infos,files)
    build_si(files,oldfigure9,oldfigure10,original_eval,original_interpret,template)
    v.v.export_html(files,ROOT/'MANUSCRIPT_REVIEW.html')
    for filename,paragraphs in [('SECTION_2_3_5_EN.md',OOD),('SECTION_2_4_EN.md',INTERPRET),('CONCLUSION_EN.md',CONCLUSION)]:
        (ROOT/filename).write_text('\n\n'.join(value for _,value in paragraphs)+'\n')
    manifest=dict(source=str(SOURCE),source_sha256=sha(SOURCE.read_bytes()),main=str(MAIN),main_sha256=sha(MAIN.read_bytes()),
        SI=str(SI),SI_sha256=sha(SI.read_bytes()),chemistry_subsections_and_schemes_preserved=True,
        introduction_and_sections2_1_2_2_unchanged=True,new_OOD_figure='Figure9 two separate experiment panels',
        original_OOD_zero_few_shot_moved='FigureS33',original_information_diagram_moved='FigureS34',
        conditional_intervention_figure='FigureS35',conclusion_aligned_with_corrected_sections=True,
        no_new_fits=True,yellow_revised_text=True)
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('v26 main/SI built: new OOD results, revised interpretation, original chemistry retained.')

def archive_image(main_files,node,filename):
    rels={r.get('Id'):r.get('Target') for r in E.fromstring(main_files['word/_rels/document.xml.rels'])}
    rid=node.find('.//a:blip',NS).get('{'+v.v.v.R+'}embed');data=main_files['word/'+rels[rid]]
    suffix=Path(rels[rid]).suffix;path=ROOT/'figures'/(filename+suffix);path.write_bytes(data);return path

def build_si(main_files,oldfigure9,oldfigure10,original_eval,original_interpret,template):
    infos,files=v.v.read(OLD_SI);raw=files['word/document.xml']
    body=list(E.fromstring(raw).find('w:body',NS));spans=b.body_ranges(raw)
    sec=next(i for i,n in enumerate(body) if n.tag=='{'+W+'}sectPr')
    normal=next(n for n in body if b.text(n).startswith('The expert archive contains'))
    para=lambda label,value:p(normal,'si_'+label,value,False)
    old9=archive_image(main_files,oldfigure9,'figureS33_original_v5_OOD_fewshot')
    old10=archive_image(main_files,oldfigure10,'figureS34_original_v5_information_flow')
    nodes=[para('scope','S35. Structural OOD evaluation and interpretation controls, revision v26'),
        para('scope_note','The current mainSection2.3.5 distinguishes the archived reference '
            'representation from source-excluded compact and partial-backbone follow-ups. '
            'All use the17-compound register, with67 exact endpoints and IT505 Ec_MBC '
            '>500 mg/L retained as a bound. Historical zero/few-shot and residual-based '
            'interpretation analyses are retained below as archival material; their '
            'equivalence and causal interpretations are superseded by mainSection2.4.'),
        para('table49','Table S49. Quantitative OOD route scores, mean ± sample SD where '
            'repeated runs are available. All predictors use the105-QAC target-training '
            'cohort and67 exact OOD endpoints. Architecture, task code, decoder and '
            'source-run counts differ across the three blocks; compare within each '
            'protocol rather than selecting across heterogeneous rows. Historical '
            'reference encoders have one checkpoint and no invented SD.')]
    labels={'matched_raw':'Raw MolFormer','human':'Human','human_shuffled':'Shuffled human',
        'mic_binary':'Binary MIC','mic_continuous':'Continuous MIC', 'human_weight_only':'Weights reset; BN retained'}
    values=[]
    old=pd.read_csv(ROOT.parent/'revision_v18/analysis/summary.csv')
    for arm in ['v5_raw','v5_human','v5_qac_ablation']:
        a=old[old.arm.eq(arm)&old.encoding.eq('text')&old.schema.eq('full-QAC105')&old.task.eq('pooled')].iloc[0]
        values.append(['Archived reference',arm,'Text', '1','%.3f'%a.RMSE])
    for arm in labels:
        a=old[old.arm.eq(arm)&old.encoding.eq('categorical')&old.schema.eq('full-QAC105')&old.task.eq('pooled')].iloc[0]
        value='%.3f ± %.3f'%(a.RMSE,a.RMSE_sd) if pd.notna(a.RMSE_sd) else '%.3f'%a.RMSE
        values.append(['Matched compact',labels[arm],'Categorical',str(int(a.n_seeds)),value])
    routes=pd.read_csv(ROOT.parent/'revision_v24/analysis/FT_route_RMSE_mean_sample_SD.csv')
    for a in routes[routes.schema.eq('full-QAC105')].itertuples():
        values.append(['Backbone routes',a.route,'Route-specific','3','%.3f ± %.3f'%(a.RMSE,a.RMSE_SD)])
    nodes.append(v.v.simple_table(normal,['Experiment','Route','Task code','Runs','RMSE log2 mg/L'],values))
    contrasts=pd.read_csv(ROOT/'interpretation_contrasts.csv')
    rows=[[a.experiment,a.scheme,a.contrast,'%+.3f'%a.delta,'[%+.3f, %+.3f]'%(a.low,a.high),str(a.groups)] for a in contrasts.itertuples()]
    nodes.extend([para('table50','Table S50. Complete contrasts plotted in Figure S35. '
        'Conditional95% intervals resample paired source seeds and scaffold clusters from '
        'fixed predictions; compact uses10,000 draws, partial backbone5,000. No training '
        'refits or multiplicity adjustment are performed. Compact weight resets retain '
        'BatchNorm state, and the partial rewind representation retains experiment-specific '
        'buffer state. This is model-procedure intervention evidence, not biological causality.'),
        v.v.simple_table(normal,['Architecture','Evaluation','Contrast','DeltaRMSE','Conditional95%CI','Scaffolds'],rows),
        img(files,oldfigure9,ROOT/'figures/figureS35_interpretation_controls.png','rIdV26Controls',266035),
        para('control_caption',(ROOT/'figureS35_caption_EN.txt').read_text().strip()),
        para('ood_original','Historical v5 OOD zero/few-shot presentation'),
        img(files,oldfigure9,old9,'rIdV26ArchiveOOD',266033),
        para('old9caption','Figure S33. Original v5 zero/few-shot OOD figure, retained with '
            'unchanged raster bytes. The few-shot arm uses a fraction of OOD labels for '
            'adaptation and is distinct from the frozen OOD evaluation in mainFigure9. '
            'The supplied archive does not establish repeated disjoint few-shot uncertainty; '
            'these curves are retained as historical exploratory evidence.'),
        para('historical_protocol','The original main-section text accompanying this figure '
            'is reproduced below for provenance. Its superiority statements are interpreted '
            'within the archived plot protocol and do not replace the new source-excluded '
            'comparisons. OOD labels used for few-shot adaptation cannot also count as '
            'untouched external validation.')])
    for i,n in enumerate(original_eval):
        value=b.text(n)
        if value and not value.startswith('Figure 9.'):
            nodes.append(para('old_eval_%d'%i,value))
    nodes.extend([para('geometry','Archived representation geometry and information-flow illustration'),
        img(files,oldfigure10,old10,'rIdV26ArchiveFlow',266034),
        para('old10caption','Figure S34. Original v5 information-flow diagram, retained with '
            'unchanged raster bytes. It is a conceptual interpretation, not an estimated '
            'additive decomposition into structural and biological components. CKA, linear '
            'probes and SHAP do not establish the causal component claimed in the historical '
            'diagram. The current interpretation is given in mainSection2.4 and FigureS35.'),
        para('limitations','The historical residual-based CausalForestDML analysis and its '
            'reported interval are preserved below as provenance, not used to establish '
            'equivalence. Different source panels, source information access, objective '
            'choices and checkpoint provenance are not isolated by assigning treatment '
            'to a residual. No prospective equivalence margin or complete assay-variability '
            'model was supplied. The QAC-binned encoder is distinct from the full-corpus '
            'quantitative encoder of TableS46. A non-significant contrast is not an '
            'equivalence test, and historical bootstrap precision does not identify '
            'a causal biological mechanism.')])
    for i,n in enumerate(original_interpret):
        value=b.text(n)
        if value and not value.startswith('Figure 10.'):
            nodes.append(para('old_interpret_%d'%i,'Historical v5 text: '+value))
    nodes.append(para('artifacts','Reproducibility: revision_v26/OOD_violin_values.csv '
        '(603 endpoint summaries), interpretation_contrasts.csv, figure_validation.json; '
        'revision_v18/analysis/{predictions,summary,contrasts}.csv; revision_v16/analysis/'
        '{paired_bootstrap,primary_10000draw_contrasts}.csv; revision_v24/analysis/'
        'FT_route_RMSE_mean_sample_SD.csv. CKA and probes are verified against '
        'analysis/cka_probing.csv and the recovered May causal_final notebook. '
        'SHAP block scores are the saved output of that notebook, cell4. '
        'No new model training was performed for this revision.'))
    addition=b''.join(E.tostring(n,encoding='utf-8') for n in nodes)
    files['word/document.xml']=raw[:spans[sec]['start']]+addition+raw[spans[sec]['start']:]
    E.fromstring(files['word/document.xml']);v.v.write(SI,infos,files)
    v.v.export_html(files,ROOT/'Supplementary_Information_v26.html')

if __name__=='__main__':main()
