"""Preserve the v11 author fields and append completed matched-FT evidence."""
from pathlib import Path
import importlib.util, copy, re, json
import pandas as pd
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parent; OLD=ROOT.parent/'revision_v11'; COMA=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('v11_builder',OLD/'build_revision.py')
v11=importlib.util.module_from_spec(spec);spec.loader.exec_module(v11)
h=v11.h;W,R,NS=v11.W,v11.R,v11.NS
MAIN=COMA/'2026_10_11_Paper_2_edited-v12_matched_finetuning.docx'
FIGURES=dict(v11.FIGURES,matched='figure5_matched_finetuning.png')

def prepare_text():
    all_summary=pd.read_csv(ROOT/'analysis/summary.csv');summary=all_summary.query("target == 'Q-HERO-405'").set_index('arm')
    secondary=all_summary.query("arm == 'expert'").set_index('target')
    contrasts=pd.read_csv(ROOT/'analysis/contrasts.csv').query("target == 'Q-HERO-405' and unit == 'seed+scaffold'").set_index('comparison')
    direct=pd.read_csv(ROOT/'analysis/direct_summary.csv').query("target == 'Q-HERO-405'").set_index('arm')
    ranks=pd.read_csv(ROOT/'analysis/direct_contrasts.csv').query("target == 'Q-HERO-405'").set_index('comparison')
    meta=json.loads((ROOT/'results/manifest.json').read_text()); raw=summary.loc['raw-molformer']; human=summary.loc['expert']; quant=summary.loc['quant-continuous']
    def diff(frame,name,field='delta_RMSE'):
        row=frame.loc[name];return f'{row[field]:+.3f} [{row.ci_low:+.3f}, {row.ci_high:+.3f}]'
    real=contrasts.loc['expert minus expert-shuffled']; overraw=contrasts.loc['expert minus raw-molformer']
    assignment=('Real human labels yield lower loss than shuffled human labels under this matched training procedure.'
                if real.ci_high<0 else 'The interval does not resolve an advantage of real human over shuffled human labels under this matched training procedure.'
                if real.ci_low<=0 else 'Real human labels yield higher loss than shuffled human labels under this matched training procedure.')
    rawclaim=('The matched partial-fine-tuning intervention establishes an exploratory improvement over the raw-feature reference in this setting.'
              if overraw.ci_high<0 else 'Improvement over the raw-feature reference remains unresolved.'
              if overraw.ci_low<=0 else 'The human intervention increases error relative to the raw-feature reference in this setting.')
    draft=(OLD/'main_draft.md').read_text()
    draft=draft.replace('Real-versus-shuffled labels preserve class counts and source chemistry while disrupting the structure–label relation.', 'Real-versus-shuffled labels preserve source-training marginal label distributions (class counts for binary arms and empirical values for continuous arms) and source chemistry while disrupting the structure–label relation.')
    capacity=('Adaptation capacity is a separate experimental choice. A small trainable projection over frozen molecular features and updates to transformer layers can respond differently to the same labels. Small projections offer a lower parameter budget; their predictive advantage must be tested with matched source chemistry and evaluation. The projection used here is a feature encoder, distinct from an internal adapter or LoRA. We therefore include matched partial backbone fine-tuning rather than assuming that small adapters are preferable.')
    anchor='We examine these questions with two complementary protocols:'
    start=draft.index(anchor);end=draft.index('\n\n',start)
    original=draft[start:end]
    replacement=original.replace('two complementary protocols','three complementary protocols').replace(
        'partial MolFormer fine-tuning on the eligible supervision collections and matched-molecule training of a small encoder over frozen features.',
        'archived partial MolFormer fine-tuning on eligible supervision collections, matched-molecule training of a small encoder over frozen features, and new partial fine-tuning on those same matched molecules.')
    draft=draft[:start]+capacity+'\n\n'+replacement+draft[end:]
    draft=draft.replace('The partial-fine-tuning protocol removes all 532 evaluation full-salt identities',
                        'The archived partial-fine-tuning protocol removes all 532 evaluation full-salt identities')
    draft=draft.replace('### 2.3. Partial backbone fine-tuning and direct transfer',
                        '### 2.3. Archived partial backbone fine-tuning and direct transfer')
    method=f'''### 2.7. Matched partial backbone fine-tuning

The new experiment reuses the ordered 681-molecule pooled source panel, its 377/304 source-training/validation partition, evaluation-cation exclusions and QAC-104/Q-HERO-405 target folds from Section 2.4. MolFormer uses the same pinned checkpoint as Section 2.3. Embedding parameters and parameters in layers 0–3 remain frozen; layers 4–11, the pooler and a dropout-0.1 scalar head are trained, totalling {meta['trainable_parameters_including_head']:,} trainable parameters. Source salts are right-padded to 202 tokens; every source and target is checked without truncation. Attention feature maps are refreshed during native MolFormer training and deterministic in evaluation; their stochastic seeds and forward-call schedules are paired across arms. Float32 arithmetic is used.

The six arms are human, continuous pooled MIC and binary pooled MIC, with each corresponding source-training-only shuffled control. The human and binary-MIC training arms each contain 52 positive calls among 377 molecules in this panel. Continuous targets are standardised on source training and inverted for direct predictions; binary MIC uses the same source-training prevalence rule as Section 2.4. Five seeds (0–4) share initial weights, minibatch permutations and stochastic seeds across arms. AdamW, weight decay 0.01, peak learning rate 3 × 10−5 with a one-cycle schedule, batch size 32 and gradient clipping at norm one are fixed. Every arm performs 30 epochs and 360 updates. Validation losses are recorded but the final checkpoint is always used; no early stopping or target-based selection occurs.

Representation-quality evaluation uses the common 300-iteration CatBoost from Section 2.4. The raw backbone is re-encoded in the same environment and included as the primary raw reference; archived raw features are retained for numerical auditing. Direct transfer retains the source head without target fitting, including shuffled controls, and reports rank agreement plus descriptive target-median AUC. Ten thousand paired seed/scaffold draws supply exploratory intervals for mean seed-specific rank differences; bootstrap midranks account for repeated molecules from sampled scaffold groups. This extension followed inspection of earlier analyses. Its protocol was written before its own training and outcomes, without a confirmatory preregistration claim. The archived MLP comparison also changes adaptation architecture, optimisation schedule and computing environment, so it does not isolate trainable capacity alone.

'''
    draft=draft.replace('[FIGURE:design]',method+'[FIGURE:design]',1)
    start=draft.index('Figure 1.');end=draft.index('\n\n',start)
    draft=draft[:start]+('Figure 1. Three evaluation protocols. (a) Archived partial fine-tuning uses unequal source collections and Q-HERO-411. (b) Matched frozen-feature adaptation and (c) matched partial MolFormer fine-tuning share the 681-molecule source panel, source partition, strict evaluation-cation exclusions and Q-HERO-405 scaffold folds. The matched fine-tuning experiment supplies both target-refit and direct-transfer controls. The historical cohorts and optimisation procedures remain distinct.')+draft[end:]
    draft=draft.replace('The strongest practical competition occurs with partial backbone fine-tuning, whereas the strictest label controls adapt frozen features on matched molecules.', 'Archived partial fine-tuning describes practical competition under unequal source collections; the two matched extensions provide controlled label replacements under frozen-feature and partial-backbone adaptation.')
    draft=draft.replace('A matched-molecule partial-fine-tuning experiment would connect these two observations within one protocol.',
                        'The matched partial-fine-tuning extension in Section 3.6 connects the two observations on the same source and target identities.')
    results=f'''### 3.6. Matched partial fine-tuning connects adaptation and supervision comparisons

With the same 681 source molecules and fixed final-checkpoint budget, partial MolFormer fine-tuning yields Q-HERO-405 mean RMSE {human.RMSE:.3f} ± {human.RMSE_sd:.3f} for human labels, {quant.RMSE:.3f} ± {quant.RMSE_sd:.3f} for continuous MIC and {summary.loc['quant-binary'].RMSE:.3f} ± {summary.loc['quant-binary'].RMSE_sd:.3f} for binary MIC; raw features yield {raw.RMSE:.3f} (Table 4; Figure 5a). The corresponding mean R² values are {human.R2:.3f}, {quant.R2:.3f} and {summary.loc['quant-binary'].R2:.3f}, with raw R² {raw.R2:.3f}. These scores use the same held-out target folds and common decoder.

[TABLE:matched]

Table 4. Matched partial MolFormer fine-tuning on the 681-molecule pooled panel, with Q-HERO-405 evaluation. Trained arms: mean ± standard deviation over five source-training seeds; raw: one fixed decoder run. Downstream RMSE uses log2 µM and target-refit scaffold CV. Direct rank agreement uses the source head without target fitting. Every trained arm has identical initial weights within seed, source split, minibatch order and 360-update budget. Direct ranking is undefined as an activity endpoint for the raw representation without a source-trained head.

Human-minus-shuffled-human paired ΔRMSE is {diff(contrasts,'expert minus expert-shuffled')}; human-minus-raw is {diff(contrasts,'expert minus raw-molformer')} (Figure 5b). {assignment} {rawclaim} Human minus continuous MIC is {diff(contrasts,'expert minus quant-continuous')}, and human minus binary MIC is {diff(contrasts,'expert minus quant-binary')}. Expert-versus-continuous supervision changes both target content and objective, while the binary-MIC comparison shares a binary objective. The exploratory continuous-MIC interval favours continuous supervision, while the human-versus-binary-MIC interval includes zero. Statistical equivalence is not assessed: no equivalence test or pre-specified margin is used.

Direct human rank agreement is {direct.loc['expert'].rank_agreement:.3f} ± {direct.loc['expert'].rank_sd:.3f}, versus {direct.loc['expert-shuffled'].rank_agreement:.3f} ± {direct.loc['expert-shuffled'].rank_sd:.3f} for shuffled human labels and {direct.loc['quant-continuous'].rank_agreement:.3f} ± {direct.loc['quant-continuous'].rank_sd:.3f} for continuous MIC (Figure 5c). The paired human-minus-shuffled rank difference is {diff(ranks,'expert minus expert-shuffled','delta_rank')}; human minus continuous MIC is {diff(ranks,'expert minus quant-continuous','delta_rank')} (Figure 5d). The human real-minus-shuffled rank interval includes zero, so this direct label-assignment advantage remains unresolved despite its positive point estimate. Positive rank agreement concerns ordering; it does not establish absolute MIC calibration. Full numerical direct-regression outcomes, source-validation curves, secondary targets, adaptation contrasts and matched error violins are retained in Supporting Information Section S18.

[FIGURE:matched]

Figure 5. Matched partial fine-tuning on Q-HERO-405. (a) Downstream target-refit RMSE and the same-environment raw reference. (b) Paired loss contrasts. (c) Direct rank agreement with no target fitting. (d) Paired rank contrasts. Points show five source seeds and bars show seed standard deviations. Contrast intervals use 10,000 paired seed/scaffold draws and are exploratory, unadjusted and conditional on fixed target folds. Five shuffled runs supply diagnostic null controls rather than a calibrated permutation test.

Secondary-target accuracy remains limited: human mean R² is {secondary.loc["QAC-104"].R2:.3f} on QAC-104 and {secondary.loc["OOD-17"].R2:.3f} on OOD-17. All trained arms have negative mean R² on both collections, limiting the positive supervision-assignment finding to the specified Q-HERO evaluation rather than a general high-accuracy or prospective prediction claim.

The matched extension removes source-identity, source-partition and update-budget differences between human and MIC fine-tuning. It does not optimise each objective independently or show that fine-tuning is generally beneficial or harmful. Comparing it with the small frozen-feature encoder tests two specified adaptation procedures, whose architecture and optimisation differ; it does not establish a general superiority of internal adapters. Human annotation provenance and the possibility that annotators saw numerical endpoints remain reserved for coauthor completion.

'''
    draft=draft.replace('## 4. Conclusions',results+'## 4. Conclusions',1)
    start=draft.index('## Abstract\n\n')+len('## Abstract\n\n');end=draft.index('\n\n## Keywords',start)
    abstract=(f'Human Good/Bad annotations may provide supervision for molecular learning, but transferable signal, competition with numerical measurements and added value over pretrained features require separate tests. For antibacterial quaternary ammonium compounds, matched partial MolFormer fine-tuning on identical source molecules yields Q-HERO scaffold-CV RMSE {human.RMSE:.3f} for human labels versus {summary.loc["quant-binary"].RMSE:.3f} for binary MIC, {quant.RMSE:.3f} for continuous MIC and {raw.RMSE:.3f} for raw features, with direct human rank agreement {direct.loc["expert"].rank_agreement:.3f} without target refitting. Paired real-versus-shuffled controls, frozen-feature experiments across four backbones and same-chemistry numerical-context comparisons reveal dependence on supervision assignment, adaptation procedure and source composition. These exploratory results evaluate human annotations as protocol-dependent supervision, restrict causal interpretation to controlled replacements within specified learning procedures and leave measurement equivalence, biological mechanism and human denoising unresolved.')
    draft=draft[:start]+abstract+draft[end:]
    conclusion=(f'On identical source molecules, the matched partial-fine-tuning extension yields Q-HERO mean R² {human.R2:.3f} with human supervision versus {quant.R2:.3f} with continuous MIC and {raw.R2:.3f} with raw features. {assignment} {rawclaim} Direct human rank agreement is {direct.loc["expert"].rank_agreement:.3f}; this result includes a matched shuffled-head control and uses no target refitting. Its paired real-minus-shuffled interval includes zero.\n\n')
    draft=draft.replace('Quantitative supervision remains the stronger point estimate in several comparisons,',conclusion+'Quantitative supervision remains the stronger point estimate in several comparisons,',1)
    draft=draft.replace('Quantitative supervision remains the stronger point estimate in several comparisons, and pooled numerical context can transfer better than exact organism-matched MIC on identical source chemistry.', 'In matched partial fine-tuning, continuous MIC yields lower downstream error and stronger direct ranking than human supervision under the exploratory unadjusted intervals, while human-versus-binary-MIC and human-versus-raw intervals include zero. Pooled numerical context can transfer better than exact organism-matched MIC on identical source chemistry.')
    draft=draft.replace('partial-fine-tuning and direct-transfer tables;', 'archived and matched partial-fine-tuning and direct-transfer tables;',1)
    (ROOT/'main_draft.md').write_text(draft)
    tables=v11.tables()
    matched=[['Source arm','Seeds','RMSE (log2 µM)','R²','Direct rank agreement']]
    for arm,label in [('raw-molformer','Raw MolFormer'),('expert','Human'),('quant-continuous','Continuous MIC'),('quant-binary','Binary MIC'),('expert-shuffled','Shuffled human'),('quant-shuffled','Shuffled continuous MIC'),('quant-binary-shuffled','Shuffled binary MIC')]:
        s=summary.loc[arm]
        if arm=='raw-molformer':matched.append([label,1,f'{s.RMSE:.3f}',f'{s.R2:.3f}','—'])
        else:
            d=direct.loc[arm];matched.append([label,5,f'{s.RMSE:.3f} ± {s.RMSE_sd:.3f}',f'{s.R2:.3f} ± {s.R2_sd:.3f}',f'{d.rank_agreement:.3f} ± {d.rank_sd:.3f}'])
    tables['matched']=matched
    return draft,tables


def main():
    draft,tables=prepare_text()
    files,tree,oldbody=v11.read_doc(COMA/'2026_10_11_Paper_2_edited-v11_JCIM_author_draft.docx')
    old=list(oldbody);normal=next(p for p in oldbody if h.text(p).startswith('Supervision for molecular learning'))
    template=next(t for t in oldbody.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
    sec=copy.deepcopy(oldbody.find('w:sectPr',NS)); credit=copy.deepcopy(h.find(oldbody,'Egor A. Ilin: Conceptualization'));ack=copy.deepcopy(h.find(oldbody,'This work was supported by the Russian Science Foundation'))
    refidx=next(i for i,p in enumerate(old) if h.text(p)=='References');refs=[copy.deepcopy(p) for p in old[refidx+1:] if h.text(p)]
    abstractidx=next(i for i,p in enumerate(old) if h.text(p)=='Abstract')
    authorparts=[copy.deepcopy(p) for p in old[1:abstractidx]]
    body=E.Element('{'+W+'}body');tree.remove(oldbody);tree.append(body)
    for block in draft.strip().split('\n\n'):
        if block.startswith('# '):
            body.append(v11.paragraph(normal,block[2:],1))
            for p in authorparts:body.append(p)
        elif block.startswith('#'):
            hashes=len(block)-len(block.lstrip('#'));body.append(v11.paragraph(normal,block[hashes:].strip(),min(hashes-1,3)))
        elif block.startswith('[FIGURE:'):
            key=block[8:-1];body.append(v11.embed(files,ROOT/'figures'/FIGURES[key],'rIdV12'+key.title()))
        elif block.startswith('[TABLE:'):body.append(h.table(template,tables[block[7:-1]]))
        elif block=='[EXISTING:credit]':body.append(credit)
        elif block=='[EXISTING:acknowledgments]':body.append(ack)
        elif block=='[REFERENCES]':
            for p in refs:body.append(p)
        else:body.append(v11.paragraph(normal,block,marked=block.startswith('[COAUTHORS')))
    body.append(sec);v11.unique_ids(tree);h.write(files,tree,MAIN)
    v11.exports(files,tree,ROOT/'manuscript_v12_readable.md',ROOT/'manuscript_v12.html')
    build_si(normal);print(MAIN)


def build_si(normal):
    files,tree,body=v11.read_doc(OLD/'Supplementary_Information_v11.docx')
    sec=body.find('w:sectPr',NS)
    template=next(t for t in body.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
    def append(node):body.insert(list(body).index(sec),node)
    def add(text,level=None):append(v11.paragraph(normal,text,level))
    add('S18. Matched partial MolFormer fine-tuning',1)
    add('This exploratory extension uses the same 681 source molecules, 377/304 source partition, strict target-cation exclusions and target folds as the pooled matched frozen-feature panel. Six supervision arms, five paired seeds, float32 and 30 fixed epochs are used. All 360-update final checkpoints are evaluated, without early stopping. The task-scoped protocol, checksums, paired initialisations and minibatch hashes, epoch losses, full predictions and independent audits are in reproducibility/revision_v12. Original trainable-parameter checkpoints remain on the provided compute server, with their immutable hashes and locations in training.csv. Native MolFormer refreshes feature-map buffers during training. A separate forward-RNG replay recovers final persistent buffers and writes reconstruction checkpoints without overwriting the original files; all 30 reconstructions reproduce saved target features and direct scores. Their checksums and numerical audits are in analysis/checkpoint_reconstruction.csv. Restore frozen parameters from the pinned base checkpoint and load the saved trained parameters plus final buffers. The original protocol and its dated implementation clarification are both archived.')
    add('S18.1. All target-refit and direct-transfer outcomes',2)
    s=pd.read_csv(ROOT/'analysis/summary.csv');d=pd.read_csv(ROOT/'analysis/direct_summary.csv')
    add('Table S11. Complete matched partial-fine-tuning target-refit results. Mean ± source-seed SD; the raw representation has a single fixed decoder run. QAC-104 and Q-HERO-405 use scaffold CV, while OOD-17 uses the QAC-trained decoder. RMSE is in log2 µM.')
    rows=[['Target','Arm','Seeds','R²','RMSE']]
    for row in s.itertuples():rows.append([row.target,row.arm,row.seeds,f'{row.R2:.3f} ± {row.R2_sd:.3f}' if row.seeds==5 else f'{row.R2:.3f}',f'{row.RMSE:.3f} ± {row.RMSE_sd:.3f}' if row.seeds==5 else f'{row.RMSE:.3f}'])
    append(h.table(template,rows))
    add('Table S12. Direct source-only predictions, without target fitting or recalibration. Rank agreement and AUC are seed means; binary logits have no direct concentration calibration. Continuous-MIC raw R² and RMSE are retained in direct_metrics.csv, including negative R² values.')
    rows=[['Target','Arm','Rank agreement ± SD','AUC','Raw R² / RMSE']]
    for row in d.itertuples():rows.append([row.target,row.arm,f'{row.rank_agreement:.3f} ± {row.rank_sd:.3f}',f'{row.AUC:.3f}',f'{row.R2:.3f} / {row.RMSE:.3f}' if row.kind=='continuous' else '—'])
    append(h.table(template,rows))
    add('S18.2. Paired contrasts and adaptation sensitivity',2)
    for filename,number,title,field in [('contrasts.csv',13,'Matched supervision RMSE contrasts','delta_RMSE'),
        ('adaptation_contrasts.csv',14,'Partial fine-tuning minus archived frozen-feature MLP RMSE','delta_RMSE'),
        ('direct_contrasts.csv',15,'Matched direct rank-agreement contrasts','delta_rank')]:
        add(f'Table S{number}. {title}. Nested seed/scaffold 95% intervals are exploratory, unadjusted and conditional on fixed target folds. The adaptation comparison also changes architecture, optimisation and computing environment.')
        c=pd.read_csv(ROOT/'analysis'/filename);c=c[c.unit=='seed+scaffold'];rows=[['Target','Comparison','Difference','95% lower','95% upper']]
        for row in c.to_dict('records'):rows.append([row['target'],row['comparison'],f"{row[field]:+.3f}",f"{row['ci_low']:+.3f}",f"{row['ci_high']:+.3f}"])
        append(h.table(template,rows))
    audit=json.loads((ROOT/'validation.json').read_text())
    add('S18.3. Numerical reproduction and training diagnostics',2)
    for row in audit['raw_feature_comparison']:
        add(f"{row['target']}: fresh-versus-archived raw feature maximum absolute difference {row['max_absolute_difference']:.6g}, mean absolute difference {row['mean_absolute_difference']:.6g}. The same-environment fresh raw representation is the primary matched fine-tuning reference. Archived raw predictions and frozen-feature results are retained rather than silently substituted.")
    append(v11.embed(files,ROOT/'figures/figureS17_matched_finetuning_learning.png','rIdV12S17'))
    add('Figure S17. Source-validation losses for matched partial fine-tuning. Thin curves are the five source seeds and thick curves their means. Binary BCE and standardised continuous-MIC MSE occupy separate panels. Validation is diagnostic only: all arms use their final 30-epoch checkpoint.')
    append(v11.embed(files,ROOT/'figures/figureS18_matched_finetuning_error_violins.png','rIdV12S18'))
    add('Figure S18. Matched partial-fine-tuning absolute-error distributions on the same 405 Q-HERO structures. (a) Split violins for human and continuous-MIC supervision, with median and IQR. (b) Paired within-structure absolute-error differences. Absolute errors are averaged across the five source seeds. These are descriptive distributions; they do not establish measurement equivalence or independent-record significance.')
    v11.unique_ids(tree);h.write(files,tree,ROOT/'Supplementary_Information_v12.docx')
    v11.exports(files,tree,ROOT/'supplement_v12_readable.md',ROOT/'Supplementary_Information_v12.html')


if __name__=='__main__':main()
