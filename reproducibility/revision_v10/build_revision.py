from pathlib import Path
import importlib.util,json,zipfile,copy,html
import xml.etree.ElementTree as E
import pandas as pd
R=Path(__file__).resolve().parent;C=R.parents[1];V=R.parent/'revision_v9'
spec=importlib.util.spec_from_file_location('v9_helpers',V/'build_revision.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
W=h.W;NS=h.NS
S=pd.read_csv(R/'analysis/summary.csv');P=pd.read_csv(R/'analysis/contrasts.csv')
MODELS=['molformer','c3-molformer','chemberta100m','chemfm1b']
LABELS={'molformer':'MolFormer-XL','c3-molformer':'c3-MoLFormer','chemberta100m':'ChemBERTa-100M','chemfm1b':'ChemFM-1B'}
TITLE='Human Binary Annotations as Supervision for QAC Potency Modelling: Controlled Comparisons with Quantitative Measurements'
def metric(model,arm,panel='matched-pooled',target='Q-HERO-405'):
    return S[(S.backbone==model)&(S.panel==panel)&(S.arm==arm)&(S.target==target)].iloc[0]
def pair(model,comparison,panel='matched-pooled',unit='seed+scaffold'):
    return P[(P.backbone==model)&(P.panel==panel)&(P.comparison==comparison)&(P.target=='Q-HERO-405')&(P.unit==unit)].iloc[0]
def ci(model,comparison,panel='matched-pooled',unit='seed+scaffold'):
    p=pair(model,comparison,panel,unit);return f'{p.delta_RMSE:+.3f} [{p.ci_low:+.3f}, {p.ci_high:+.3f}]'
def score(model,arm,panel='matched-pooled'):
    m=metric(model,arm,panel);return f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}'
def embed(files,filename='figure8_modern_context.png',rid='rIdV10Figure8',docid='9908'):
    rels=E.fromstring(files['word/_rels/document.xml.rels'])
    E.SubElement(rels,f'{{{h.PKG}}}Relationship',Id=rid,Type=h.R+'/image',Target='media/'+filename)
    path=R/'figures'/filename;files['word/media/'+filename]=path.read_bytes();files['word/_rels/document.xml.rels']=h.serialize(rels)
    el=h.image_paragraph(rid,path)
    el.find('.//wp:docPr',NS).set('id',docid);el.find('.//wp:docPr',NS).set('name',filename)
    return el
def document(path):
    with zipfile.ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
    tree=E.fromstring(files['word/document.xml']);return files,tree,tree.find(f'{{{W}}}body')
def readable(tree,path):
    lines=[]
    for el in tree.find(f'{{{W}}}body'):
        if el.tag==f'{{{W}}}tbl':
            rows=[[h.text(c) for c in t.findall(f'{{{W}}}tc')] for t in el.findall(f'{{{W}}}tr')]
            if rows:
                lines.extend(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(row)+' |' for row in rows[1:]])
        elif h.text(el):lines.append(h.text(el))
        lines.append('')
    path.write_text('\n'.join(lines))
def main():
    assert set(json.loads((R/'analysis/meta.json').read_text())['completed_models'])==set(MODELS)
    for name in MODELS[1:]:assert json.loads((R/'data'/f'{name}_meta.json').read_text())['truncated']==0
    files,tree,body=document(C/'2026_10_11_Paper_2_edited-v9_supervision_controls.docx')
    normal=copy.deepcopy(h.find(body,'The bottleneck in this domain'));heading=copy.deepcopy(h.find(body,'2.6 Controlled'))
    template=next(t for t in body.findall(f'{{{W}}}tbl') if len(t.find(f'{{{W}}}tr').findall(f'{{{W}}}tc'))==5)
    h.replace(h.find(body,'Human Binary Annotations Compete'),TITLE)
    abstract=f'''Human Good/Bad annotations may provide useful supervision for molecular activity modelling, but competitive prediction and causal attribution require distinct tests. We compare final expert labels with molecule-level and record-level MIC, organism-matched MIC, and mammalian-cell cytotoxicity for quaternary ammonium compounds. Archived partial fine-tuning yields Q-HERO R² = 0.269 with 740 expert labels versus 0.312/0.308 with 1,153 numerical molecule targets/9,338 MIC records. New frozen-backbone interventions pair source molecules, initial weights, scaffold splits and training budgets. On 681 common molecules, real expert labels improve Q-HERO error relative to shuffled labels with MolFormer-XL and c3-MoLFormer; their nested seed/scaffold ΔRMSE intervals are {ci('molformer','expert minus expert-shuffled')} and {ci('c3-molformer','expert minus expert-shuffled')} log2 µM. The effect is backbone-dependent and does not establish added value over raw pretrained features. On the 529-molecule panel the expert encoder underperforms raw MolFormer. Holding those same molecules fixed, pooled MIC yields RMSE 1.525 versus 1.617 for exact S. aureus MIC, so narrower assay context does not automatically improve transfer. Direct expert scores also track measured potency despite receiving no numerical concentration targets. These results support human labels as a learnable, protocol-dependent supervision signal and demonstrate practical competition under partial fine-tuning. They identify changes in predictive loss caused by supervision interventions within the specified algorithms, while leaving biological mechanism, universal denoising and measurement equivalence unresolved.'''
    h.replace(h.find(body,'Binary human annotations can'),abstract)
    p=h.find(body,'On the smaller S. aureus-matched panel')
    h.replace(p,h.text(p)+f' Relative to the raw MolFormer backbone, the expert encoder has higher error: nested seed/scaffold ΔRMSE {ci("molformer","expert minus raw-molformer","matched-sa")}. This adverse result is retained alongside the positive pooled-panel result.')
    p=h.find(body,'For the pooled panel, mean Q-HERO-405')
    h.replace(p,h.text(p)+f' A nested seed/scaffold sensitivity gives expert minus continuous MIC {ci("molformer","expert minus quant-continuous")}; this interval includes zero, qualifying the conditional-scaffold interval. Continuous MIC versus shuffled continuous MIC gives {ci("molformer","quant-continuous minus quant-shuffled")}. All intervals are exploratory and unadjusted for multiple comparisons.')
    for p in body.findall(f'{{{W}}}p'):
        text=h.text(p)
        if 'nfrolov@ioc.ac,ru' in text:h.replace(p,text.replace('nfrolov@ioc.ac,ru','nfrolov@ioc.ac.ru'))
        if text.startswith('The descriptor baseline is positive on Q-HERO'):
            h.replace(p,'The six-descriptor baseline is weakly positive on Q-HERO (R² = +0.057) and negative on QAC-105 (−0.310) and OOD-17 (−0.486). These comparisons are descriptive.')
        if text.startswith('Update this table of contents in Word'):
            for node in p.findall('.//w:t',NS):node.text=''
    rows=[['Frozen backbone','Raw RMSE','Human RMSE','Continuous MIC RMSE','Shuffled human RMSE']]
    for name in MODELS:
        raw=metric(name,'raw-'+name,'baseline');rows.append([LABELS[name],f'{raw.RMSE:.3f}',score(name,'expert'),score(name,'quant-continuous'),score(name,'expert-shuffled')])
    blocks=[h.clone(heading,'2.7 Modern backbone sensitivity on external Q-HERO')]
    blocks.append(h.clone(normal,'To test backbone dependence we added ChemFM-1B (80), c3-MoLFormer and ChemBERTa-100M from the ChemBERTa-3 framework (81). These published checkpoints were selected before examining their QAC performance. All models encode the same canonical full salts and use the identical 681-molecule source panel, cation exclusions, target scaffold folds and fixed CatBoost decoder. The model representations are frozen; the intervened neural encoder retains 256- and 128-unit hidden layers, with input dimension set by each backbone. This tests supervision within each representation rather than reproducing full transformer fine-tuning or isolating model size.'))
    blocks.append(h.table(template,rows))
    blocks.append(h.clone(normal,'Table 4. Q-HERO-405 RMSE in log2 µM under fixed target scaffold folds. Trained encoders: mean ± seed standard deviation, five seeds. Raw representations use one fixed decoder run. The c3-MoLFormer checkpoint name “1.1B” refers to the pretraining corpus; its encoder has 44.4 million parameters. All binary-MIC, shuffled-binary-MIC and untrained controls and secondary evaluation targets appear in Supporting Information.'))
    sentences=[]
    for name in MODELS:
        sentences.append(f'{LABELS[name]}: expert minus shuffled expert {ci(name,"expert minus expert-shuffled")}; expert minus continuous MIC {ci(name,"expert minus quant-continuous")}; expert minus raw backbone {ci(name,"expert minus raw-"+name)}.')
    blocks.append(h.clone(normal,'Nested seed/scaffold contrasts, conditional on the fixed target folds, are as follows (ΔRMSE in log2 µM; unadjusted 95% intervals). '+' '.join(sentences)))
    blocks.append(h.clone(normal,'The real-versus-shuffled human contrast supports learnable label content in the two MolFormer representations, but does not reproduce uniformly across backbones. None of these contrasts should be read as a guarantee that human supervision improves raw pretrained representations. Shuffling binary MIC after thresholding also shows why a real-versus-shuffled comparison requires raw and untrained anchors: destroying label assignment can damage an encoder, with an objective-dependent magnitude. The experiments separate label-content effects, added predictive value and practical competition.'))
    blocks.append(h.clone(heading,'2.8 Assay-context sensitivity with molecular composition held fixed'))
    blocks.append(h.clone(normal,'The pooled-versus-organism-matched panels in Section 2.6 differ by 152 molecules. We therefore hold the 529 shared source molecules, 91 cation scaffolds, 78 positive expert calls, initial weights and source partition fixed, and replace only the numerical aggregation policy. The expert and exact-S. aureus runs deterministically repeat the same 529-molecule experiment as Section 2.6 and are anchors, not independent replications. Pooled MIC summarises 4,049 underlying records; exact S. aureus MIC summarises 855. Records per molecule are not independent measurements of information quantity. This intervention changes organism mixture, censoring treatment, record count and aggregation together; it cannot identify a pure laboratory-provenance effect.'))
    context=[['Source on same 529 molecules','Molecules','Underlying records','Q-HERO R²','Q-HERO RMSE']]
    for arm,label,n in [('expert','Final expert calls',None),('quant-pooled','Pooled MIC',4049),('quant-sa','Exact S. aureus MIC',855),('quant-pooled-shuffled','Shuffled pooled MIC',4049),('quant-sa-shuffled','Shuffled exact S. aureus MIC',855)]:
        m=metric('molformer',arm,'context');context.append([label,529,'—' if n is None else n,f'{m.R2:+.3f}',f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}'])
    blocks.append(h.table(template,context));blocks.append(h.clone(normal,'Table 5. Context sensitivity on identical source chemistry and the same held-out Q-HERO cohort. Expert labels are final molecule-level calls; no observation count or lab-cost exchange rate is inferred.'))
    blocks.append(h.clone(normal,f'Pooled versus exact S. aureus MIC gives nested seed/scaffold ΔRMSE {ci("molformer","quant-pooled minus quant-sa","context")}. Pooled MIC versus its shuffled counterpart gives {ci("molformer","quant-pooled minus quant-pooled-shuffled","context")}. Thus the richer pooled numerical source transfers better in this setting despite its broader context. The interval for the context comparison is close to zero and unadjusted; the directional result does not identify which component of the aggregation policy matters. A general denoising account of expert supervision is therefore unsupported.'))
    blocks.append(h.clone(normal,'The external Q-HERO collection originates from continuing work across the Wuest and Minbiole laboratories (52), but the supplied structural/MIC worksheet does not attach strain identifier, assay protocol or laboratory provenance to individual records. Programme-level coordination is not proof of identical historical assay conditions. The separate Mendeley source-comparison results are useful descriptive evidence about transfer-source choice, but changing entire source collections also changes chemical coverage, sample size and selection. They cannot establish that provenance alone causes transfer success. The QMR same-compound/same-strain replicate audit further precludes interpreting every pooled conflict as laboratory error.'))
    blocks.append(embed(files));blocks.append(h.clone(normal,'Figure 8. (a) Expert-minus-shuffled-expert Q-HERO contrasts for four frozen backbones; (b) source-context contrasts on the same 529 molecules. Intervals resample source initialisation seeds and whole target scaffolds, while keeping target folds fixed; all contrasts are exploratory and unadjusted. Negative values favour the first named arm.'))
    blocks.append(h.clone(normal,'The distributions in Figure 9 complement the paired loss contrasts. Exact uncensored source MIC records are aggregated to one median log2 value per molecule and organism class, avoiding treatment of repeated assay reports as independent compounds. Mono- and bis-cationic compounds differ in chemistry as well as nitrogen count; their distributions describe chemical context rather than a causal effect of adding a charged centre. Q-HERO is shown separately. Model-error violins average absolute errors across five source seeds for each held-out molecule, and the paired panel preserves correspondence between human and numerical-supervision predictions. Similar medians do not establish equivalent RMSE, because tail errors contribute differently to the aggregate metric.'))
    blocks.append(embed(files,'figure9_MIC_error_violins.png','rIdV10Figure9','9909'))
    blocks.append(h.clone(normal,'Figure 9. Split violin comparisons of chemical context and prediction errors. (a) Exact source MIC, after evaluation-cation exclusion, for mono- versus bis-cationic QACs in Gram-positive, Gram-negative and fungal classes; n counts molecule × organism-class pairs, and a molecule can occur in more than one class. (b) Measured Q-HERO MIC by number of cationic nitrogen atoms; one compound with no cationic N is omitted. (c) Absolute errors on the same 405 scaffold-held-out Q-HERO molecules under human versus continuous MIC supervision, averaged over five source seeds. (d) Paired absolute-error differences for those molecules. KDE is estimated in plotted log2 coordinates and clipped to observed support; bars show median and interquartile range. These descriptive distributions carry no independent-observation p-values or biological causal interpretation.'))
    h.add_sequence(body,h.find(body,'3. Conclusion'),blocks)
    p=h.find(body,'Final human Good/Bad annotations contain activity-related')
    h.replace(p,'Final human Good/Bad annotations supply learnable activity-related supervision in defined protocols. External Q-HERO is the principal evidence: archived partial fine-tuning shows practical competition with numerical MIC targets, while matched-molecule interventions distinguish label content from added value over pretrained representations. The positive human-versus-shuffled effect is reproduced with c3-MoLFormer and remains bounded by backbone and source chemistry.')
    p=h.find(body,'One result deserves separate emphasis.')
    h.replace(p,h.text(p)+' The archived three-seed Q-HERO direct rank agreement is 0.397 ± 0.050 (seed standard deviation; runs_direct.jsonl). Figure S11 illustrates measured potency distributions from a fixed logit=0 class threshold for one direct expert checkpoint, without selecting the threshold on target measurements. Predicted classes are outputs of the expert-supervised model, not new human labels of Q-HERO compounds.')
    p=h.find(body,'The defensible causal claim concerns changing supervision')
    h.replace(p,h.text(p)+' Modern-checkpoint tests and composition-fixed context sensitivity add boundary conditions: human supervision does not work uniformly across backbones, and narrowing numerical supervision to exact S. aureus MIC does not improve Q-HERO transfer on the same source molecules. Heterogeneity is an assay-context hypothesis requiring richer metadata, rather than an established explanation for the human signal.')
    method='Modern frozen-feature extraction pins checkpoint revisions before evaluation. ChemFM uses the final non-padding hidden token; ChemBERTa uses the attention-masked mean of hidden tokens, excluding a randomly initialised pooler; c3-MoLFormer uses deterministic MoLFormer pooling. Maximum observed token counts and context windows are audited; no molecule is truncated. The source encoder has input dimension equal to each representation, followed by 256 and 128 units, with the same 80-epoch source training. Comparisons within backbone pair initial weights and source identities; representation capacities and pooling differ between backbones. Numerical labels are permuted within source training; the binary-MIC shuffled control first binarises at the training-only threshold and then permutes. Nested bootstrap resamples the five paired source seeds and 29 Q-HERO cation-scaffold clusters; this sensitivity does not estimate uncertainty over target fold assignments. Leave-one-scaffold-out loss contrasts are supplied. All extension analyses are exploratory, not preregistered, with unadjusted intervals and no model or checkpoint selected by target results.'
    h.add_sequence(body,h.find(body,'4.2 Chemistry'),[h.clone(normal,method)])
    refs=['80.Cai, F.; Hanna, K.; Zhu, T.; et al. ChemFM as a scaling law guided foundation model pre-trained on informative chemicals. Communications Chemistry 2026, 9, 3 (published online 18 December 2025). https://doi.org/10.1038/s42004-025-01793-8.','81.Singh, R.; Barsainyan, A. A.; Irfan, R.; et al. ChemBERTa-3: an open source training framework for chemical foundation models. Digital Discovery 2026, 5, 662–685. https://doi.org/10.1039/D5DD00348B.']
    for text in refs:body.insert(len(body)-1,h.clone(normal,text))
    output=C/'2026_10_11_Paper_2_edited-v10_modern_models_QHERO.docx';h.write(files,tree,output);readable(tree,R/'manuscript_v10_readable.md')
    build_si()
    print(output)
def build_si():
    files,tree,body=document(V/'Supplementary_Information_v9.docx')
    normal=next(p for p in body.findall(f'{{{W}}}p') if len(h.text(p))>100)
    heading=next(p for p in body.findall(f'{{{W}}}p') if h.text(p).startswith('S7.'))
    template=next(t for t in body.findall(f'{{{W}}}tbl') if len(t.find(f'{{{W}}}tr').findall(f'{{{W}}}tc'))==5)
    rows=[['Backbone / panel','Supervision / target','Seeds','R² ± seed SD','RMSE ± seed SD']]
    for _,m in S[(S.panel.isin(['baseline','matched-pooled','context']))].iterrows():
        rows.append([LABELS[m.backbone]+' / '+m.panel,m.arm+' / '+m.target,int(m.seeds),f'{m.R2:+.3f} ± {m.R2_sd:.3f}',f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}'])
    contrasts=[['Backbone / panel','Comparison','Bootstrap unit','ΔRMSE','95% interval']]
    for _,p in P[P.target=='Q-HERO-405'].iterrows():contrasts.append([LABELS[p.backbone]+' / '+p.panel,p.comparison,p.unit,f'{p.delta_RMSE:+.3f}',f'[{p.ci_low:+.3f}, {p.ci_high:+.3f}]'])
    blocks=[h.clone(heading,'S12. Modern checkpoint and context extension'),h.clone(normal,(R/'PROTOCOL.md').read_text()),h.table(template,rows),h.clone(normal,'Table S7. Complete CatBoost extension results, including all secondary targets and negative controls. Raw-backbone values come from one fixed decoder run. Seed standard deviations are descriptive. Older partial-fine-tuning and new frozen-feature results use different cohorts and are not one leaderboard.'),h.clone(heading,'S13. Nested uncertainty and scaffold influence'),h.table(template,contrasts),h.clone(normal,'Table S8. All Q-HERO extension contrasts with conditional-scaffold and nested seed/scaffold intervals. No multiplicity adjustment or post-hoc equivalence margin. Other targets and leave-one-scaffold-out loss ranges are supplied in analysis/contrasts.csv. Nested resampling of five seeds has limited precision and is a sensitivity analysis, not evidence from five independent datasets.'),h.clone(heading,'S14. Cross-environment checks and descriptive visual comparisons'),h.clone(normal,'All 486 v9 metric rows and paired scaffold-bootstrap intervals were independently recalculated on the second supplied server. A training reproduction on the first server gives small Q-HERO differences across PyTorch/scikit-learn versions; individual seed outputs are not bitwise reproducible. All original results remain authoritative, with server comparisons archived separately.'),h.clone(normal,'Q-HERO row-level strain/protocol provenance is absent from the provided worksheet. Public programme-level descriptions support coordinated collection, without certifying identical assay conditions for every historical compound. Same-molecule context sensitivity changes organism mixture, censoring policy, record count and numerical aggregation together. Human denoising and laboratory-bias removal are not identified. Checkpoint metadata, feature hashes, target-fold assignments, paired initialisation hashes, source-identity hashes and complete prediction files accompany the extension.')]
    blocks.extend([h.clone(normal,'Figure S10. Chemical-space illustration from frozen MolFormer features, with per-molecule L2 normalisation and PCA fitted on source-training molecules. Joint t-SNE uses held-out structures solely for illustration; proximity does not establish transferability or causal mechanisms. Source validation reserves 15% of scaffold groups rather than 15% of molecules: in the pooled panel, 377 molecules are in training and 304 in validation.'),embed(files,'figureS10_chemical_space.png','rIdV10FigureS10','9910'),h.clone(normal,'Figure S11. (a) Measured external MIC distributions by the predicted Good/Bad class of one archived direct expert checkpoint, threshold logit=0 fixed without target labels; Q-HERO-405 subset, descriptive and conditional on seed 0. These are model-predicted classes, not human annotations of external compounds. (b) Three-seed direct rank agreement from the original Q-HERO-411 cohort, with mean and seed standard deviation. No downstream target refitting in either panel; cohorts differ, and raw direct MIC calibration remains unvalidated.'),embed(files,'figureS11_direct_expert_violin.png','rIdV10FigureS11','9911')])
    for el in blocks:body.insert(len(body)-1,el)
    h.write(files,tree,R/'Supplementary_Information_v10.docx');readable(tree,R/'supplement_v10_readable.md')
    content='<html><meta charset="utf-8"><title>COMA Supplement v10</title><body><pre style="white-space:pre-wrap">'+html.escape((R/'supplement_v10_readable.md').read_text())+'</pre></body></html>'
    (R/'Supplementary_Information_v10.html').write_text(content)
if __name__=='__main__':main()
