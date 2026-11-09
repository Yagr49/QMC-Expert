"""Build the original-cohort narrative; preserve native author/reference fields."""
from pathlib import Path
import importlib.util, copy, re, json
import pandas as pd
import numpy as np
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('v11_builder',ROOT.parent/'revision_v11/build_revision.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
h=v.h;W,R,NS=v.W,v.R,v.NS
TITLE='Human Judgement as Molecular Supervision: Matched Quantitative Comparisons and Scaffold Transfer in Quaternary Ammonium Biocides'
MAIN=COMA/'2026_10_11_Paper_2_edited-v14_QAC105_OOD17.docx'
FIGURES={'design':'figure1_supervision_and_transfer.png','parity':'figure2_QAC105_parity.png',
    'encoding':'figure3_task_encoding.png','structures':'figure4_OOD_families_ACS1996.png','violins':'figure5_paired_error_violins.png'}
ARMS=['expert','quant-continuous','quant-binary','raw-molformer']
LABEL={'expert':'Human','quant-continuous':'Continuous MIC','quant-binary':'Binary MIC','raw-molformer':'Raw MolFormer'}
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
TLABEL={'Sa_MIC':'S. aureus MIC','Sa_MBC':'S. aureus MBC','Ec_MIC':'E. coli MIC','Ec_MBC':'E. coli MBC'}

def prepare():
    s=pd.read_csv(ROOT/'analysis/summary.csv');c=pd.read_csv(ROOT/'analysis/contrasts.csv')
    scaffold=pd.read_csv(ROOT/'analysis/scaffold_summary.csv')
    def metric(arm,cohort='QAC105',task='pooled',encoding='onehot'):
        return s[(s.arm==arm)&(s.cohort==cohort)&(s.task==task)&(s.encoding==encoding)].iloc[0]
    def contrast(name,cohort='QAC105',task='pooled'):
        row=c[(c.comparison==name)&(c.cohort==cohort)&(c.task==task)].iloc[0]
        return f'{row.delta_RMSE:+.3f} [{row.ci_low:+.3f}, {row.ci_high:+.3f}]'
    human=metric('expert');quant=metric('quant-continuous');binary=metric('quant-binary');raw=metric('raw-molformer')
    oh=metric('expert','OOD17');oq=metric('quant-continuous','OOD17');ob=metric('quant-binary','OOD17');orr=metric('raw-molformer','OOD17')
    old=(ROOT.parent/'revision_v12/main_draft.md').read_text()
    fields='\n\n'.join(block for block in old.split('\n\n') if block.startswith('[COAUTHORS H'))
    datafields='\n\n'.join(block for block in old.split('\n\n') if block.startswith('[COAUTHORS D'))
    cur=pd.read_csv(ROOT/'analysis/QAC104_curation_sensitivity.csv')
    cur=cur[(cur.cohort=='QAC105')&(cur.task=='pooled')&(cur.encoding=='onehot')&(cur.provenance=='matched-source-excluded')].set_index('arm')
    delta=max(abs(metric(a).RMSE-cur.loc[a].RMSE) for a in ARMS)
    sh=scaffold[(scaffold.arm=='expert')&(scaffold.cohort=='QAC105')&(scaffold.task.isin(TASKS))].set_index('task')
    sp=scaffold[(scaffold.cohort=='QAC105')&(scaffold.task=='pooled')].set_index('arm')
    sc=pd.read_csv(ROOT/'analysis/scaffold_contrasts.csv')
    sc=sc[(sc.cohort=='QAC105')&(sc.task=='pooled')].set_index('comparison')
    sr=sc.loc['expert minus raw-molformer'];sn=sc.loc['expert minus expert-shuffled']
    gt=metric('expert',encoding='text')
    censor=pd.read_csv(ROOT/'analysis/censoring_minimum_error_summary.csv')
    censor=censor[(censor.arm=='expert')&(censor.encoding=='onehot')].set_index('task')
    draft=f'''# {TITLE}

## Abstract

Human Good/Bad judgements offer a coarse supervisory signal for molecular learning, but their value relative to quantitative measurements depends on how transfer is tested. We compare matched human, continuous-MIC and binary-MIC supervision using identical source molecules, five paired training seeds and common downstream models for four antibacterial endpoints in the original 105 quaternary ammonium compounds (QACs). With cation-held-out validation and one-hot task metadata, mean pooled RMSE is {human.RMSE:.3f}, {quant.RMSE:.3f} and {binary.RMSE:.3f} log2(mg/L), respectively, versus {raw.RMSE:.3f} for raw MolFormer features; fixed text embeddings provide no consistently resolved advantage over one-hot encoding. A scaffold-held-out follow-up retains a pooled-loss improvement over raw features, whereas 17 named compounds from four new scaffold families expose weak absolute concentration prediction. This exploratory revision centres the original cohorts after inspection of earlier analyses and retains Q-HERO comparisons in Supporting Information. The supported claim is protocol-dependent molecular supervision with controlled label-replacement tests, rather than measurement equivalence or biological causality.

## Keywords

Quaternary ammonium compounds; expert annotations; molecular representation learning; MIC; MBC; multitask learning; scaffold transfer

## 1. Introduction

Molecular learning usually treats an experimental concentration or a class derived from it as the training target. Chemists also make categorical decisions about whether a compound is promising. Such judgements can be learned for molecular prioritisation (1), raising a more specific question: can they shape representations that remain useful for predicting measured antibacterial activity? Quaternary ammonium compounds provide a practical setting because molecular structure, charge and antibacterial endpoints vary across related series (2).

Human annotations and numerical measurements describe different supervisory signals. MIC records may repeat the same molecule across organisms and assays, while a final Good/Bad call may summarise several observations. Comparing the number of records with the number of human calls alone therefore cannot establish greater information efficiency. The relevant comparison holds source chemistry and learning conditions fixed, and then measures prediction on compounds excluded from representation training. Whether annotators themselves saw numerical measurements is a separate provenance question.

Adaptation capacity also matters. A small trainable projection can compress fixed foundation-model features at a lower parameter budget than updates to transformer layers. This makes compact encoders attractive, but does not show that fine-tuning is harmful or that internal adapters are always preferable. We retain the original 256-dimensional contrastive-encoder branch as a historical analysis and use matched partial MolFormer fine-tuning to test supervision assignment under one common adaptation procedure (4).

We preserve the original workflow: learn guided representations, predict MIC/MBC in the original 105 QACs, test 17 compounds from four new scaffold families, and inspect which conclusions survive controls. Species and endpoint metadata are represented either by one-hot indicators or fixed text-embedding-3-small vectors. All four endpoints of each cation stay together in validation. Real-versus-shuffled labels, continuous and binarised MIC, and raw pretrained features distinguish activity-related signal from a generic effect of adaptation. The earlier Q-HERO analyses (3) and additional backbone/context experiments (5–8) are retained as supplementary evidence; the present change of narrative follows inspection of those earlier results and is exploratory.

In the archived matched partial-fine-tuning Q-HERO comparison, human/continuous-MIC/raw RMSE was 1.529/1.453/1.607 log2 µM: continuous MIC had lower error, and the human-versus-raw interval included zero. These prior outcomes are retained alongside the original-cohort analysis so that the revised emphasis cannot be read as universal human superiority.

[FIGURE:design]

Figure 1. Matched supervision and target evaluation. The same source chemistry supplies real and shuffled human, continuous-MIC and binary-MIC arms, with paired initialisations and training budgets. The original 105 salts supply cation-held-out validation and the training data for a final decoder applied to the named OOD compounds. Cation-held-out validation permits scaffold overlap; a separate scaffold-held-out sensitivity uses all 105 salts. Text vectors describe only the four tasks. OOD measurements never enter fitting or selection.

## 2. Results and Discussion

### 2.1. Learning guidance under matched source chemistry

The expert archive contains 1,103 final annotation entries, comprising 244 Good and 859 Bad calls before standardisation and exclusions. After matching eligible expert and quantitative records and excluding all evaluation cations, the common panel contains 681 source molecules with 4,938 underlying MIC records and 96 positive human calls. The fixed scaffold-disjoint source split contains 377 training and 304 validation molecules; 52 training calls are positive. Records repeat molecules and are not independent training compounds (Table 1).

[TABLE:sources]

Table 1. Source and evaluation counts. The 681-source panel is the matched eligibility panel, not a count of training molecules; only 377 source molecules are used for gradient updates. Original QAC structures are excluded from the source. The original 108 target rows collapse to 105 full-salt identities and 103 cations. One conflicting duplicate is retained by the documented historical median rule, with a 104-molecule exclusion sensitivity.

The primary controlled comparison uses the same partial MolFormer adaptation for each source arm. Human and binary-MIC targets share a binary objective, while continuous MIC uses regression. Shuffling occurs only within source training and preserves the marginal label distribution. Within seed, initial weights, molecule order, stochastic schedule and 360 gradient-update budget are shared. These controls isolate a replacement of supervision within a specified algorithm; they do not turn the labels into randomised biological treatments.

### 2.2. Prediction on the original 105 QACs

The original four targets are MIC and MBC against S. aureus ATCC 43300 and E. coli ATCC 25922. A fixed CatBoost decoder produces one out-of-fold prediction per compound and endpoint under five cation-grouped folds. Different counterion forms of the same cation remain together. The main comparison uses shared one-hot task metadata (Figure 2; Table 2).

[TABLE:qac]

Table 2. Original QAC-105 cation-held-out prediction. Each cell gives RMSE in log2(mg/L), as mean ± source-seed SD, followed by mean seed-specific R². Raw features have one fixed decoder run. All 105 structures and 420 endpoint values are retained. Cation-held-out folds allow members of the same scaffold family in both training and test and assess interpolation to a new cation within the sampled chemistry.

[FIGURE:parity]

Figure 2. QAC-105 parity plots with the common one-hot decoder. Rows correspond to the four species/endpoint tasks; columns compare human, continuous-MIC and binary-MIC guidance. Points show mean predictions over source seeds, while annotation boxes report mean seed-specific scores rather than ensemble scores. The dashed line is y = x; no target-fitted calibration line is applied. All concentration axes use log2(mg/L).

Across all four endpoint losses, human-guided representations yield mean pooled RMSE {human.RMSE:.3f}, compared with {quant.RMSE:.3f} for continuous MIC, {binary.RMSE:.3f} for binary MIC and {raw.RMSE:.3f} for raw features. Human minus shuffled-human ΔRMSE is {contrast('expert minus expert-shuffled')}; human minus raw is {contrast('expert minus raw-molformer')}. These exploratory, unadjusted seed/scaffold intervals support a contribution from the real label assignment and an improvement over raw features in this cation-held-out, pooled-loss setting.

The quantitative controls also carry signal: continuous-MIC minus shuffled-continuous ΔRMSE is {contrast('quant-continuous minus quant-shuffled')}, and binary-MIC minus shuffled-binary is {contrast('quant-binary minus quant-binary-shuffled')}. The continuous real-versus-shuffled improvement has a larger point magnitude than the human improvement; the binary-MIC interval includes zero. Real-label benefits therefore do not uniquely privilege human supervision.

Human minus continuous MIC is {contrast('expert minus quant-continuous')}, and human minus binary MIC is {contrast('expert minus quant-binary')}. Their intervals include zero, so the point estimates show practical proximity under this protocol without establishing statistical equivalence. The result concerns prediction losses on measured endpoints, not replacement of experimental assays by annotations. Pooled R² is not used to claim within-task accuracy because differences between species and MIC/MBC can inflate a pooled score. Endpoint-specific R² and errors are reported throughout.

The conflicting duplicate is target_25e7bff606cb (original rows 75 and 76). Its supplied S. aureus MIC values are 0.25/0.5 mg/L, S. aureus MBC values 2/0.5 mg/L, and E. coli MBC values 8/2 mg/L; E. coli MIC is 2 mg/L in both rows. The historical full-salt median rule yields 0.375, 1.25, 5 and 2 mg/L, respectively. Retaining it makes the full original cohort traceable rather than asserting that the median is a new measurement. Excluding its already-held-out predictions changes the main-arm pooled RMSE by at most {delta:.4f} log2 units; this post-exclusion score sensitivity does not retrain folds and is distinguished from the independently curated QAC-104 analysis in Supporting Information.

### 2.3. Task descriptions and the limit of within-family validation

One-hot indicators and text vectors both identify the same four tasks. The fixed texts name the strain and describe MIC or MBC; their 1,536-dimensional vectors are identical for every molecule within a task. They add no new measured activity or compound-specific biological data. Text coding can alter which task partitions CatBoost selects, but any difference here cannot by itself identify semantic understanding or biological information transfer.

For human-guided representations, text coding changes pooled QAC RMSE from {human.RMSE:.3f} to {gt.RMSE:.3f}; paired text-minus-one-hot ΔRMSE is {contrast('text minus onehot: expert')}. Figure 3 shows the task-specific scores. The paired text-versus-one-hot intervals include zero for the primary trained arms on pooled QAC loss, and no consistent text-coding advantage is established on OOD. The historical no-metadata comparison is reconstructed with four separate endpoint models in Supporting Information; it changes pooling and the number of rows per fitted model as well as task metadata, and is not an isolated metadata intervention.

Endpoint-specific text effects can point in opposite directions. On the OOD raw-feature reference, text coding reduces E. coli MBC error by 0.311 log2 units but increases S. aureus MBC error by 0.123; both exploratory four-family intervals exclude zero in opposite directions. These reversals, reported with all endpoint contrasts in the computational supplement, reinforce the distinction between an occasional task-partitioning benefit and a consistent semantic advantage.

[FIGURE:encoding]

Figure 3. Task encoding on the original 105 QACs. Circles denote one-hot and open squares fixed text embeddings. Lines connect encodings applied to the same source arm and target folds. Error bars are source-seed SD; the raw representation is a single fixed run. The comparison does not establish a semantic benefit of language-model task descriptions.

New-cation interpolation and new-scaffold transfer are different demands. An additional five-fold validation groups all 105 structures by their 29 cation Murcko scaffolds, keeping entire families outside each decoder training fold (Table 3). It was added after inspecting this extension and receiving protocol reviews, with fixed source checkpoints, hyperparameters and one-hot encoding. Human endpoint R² values under scaffold holdout are {sh.loc['Sa_MIC'].R2:.3f}, {sh.loc['Sa_MBC'].R2:.3f}, {sh.loc['Ec_MIC'].R2:.3f} and {sh.loc['Ec_MBC'].R2:.3f}, respectively. These results delimit how far the gains in cation-held-out prediction transfer. The complete source arms, adverse results and fold assignments are retained.

Under scaffold holdout, pooled RMSE is {sp.loc['expert'].RMSE:.3f} for human supervision, {sp.loc['quant-continuous'].RMSE:.3f} for continuous MIC, {sp.loc['quant-binary'].RMSE:.3f} for binary MIC and {sp.loc['raw-molformer'].RMSE:.3f} for raw features. The human-minus-raw contrast is {sr.delta_RMSE:+.3f} [{sr.ci_low:+.3f}, {sr.ci_high:+.3f}], retaining an exploratory pooled-loss benefit. The real-minus-shuffled-human interval is [{sn.ci_low:+.4f}, {sn.ci_high:+.4f}], with its upper limit only just below zero. This boundary result is especially sensitive to the fixed folds, five seeds and unadjusted comparisons and is not an independent confirmation.

[TABLE:scaffold]

Table 3. QAC-105 scaffold-held-out sensitivity, using the same endpoints, units, source representations and one-hot decoder as Table 2. Cells give mean RMSE ± source-seed SD (log2 mg/L), followed by mean seed-specific R². Entire cation-scaffold families remain together. This exploratory follow-up is separate from the cation-held-out primary analysis and from the earlier QAC-104 single-task micromolar analysis.

### 2.4. Named out-of-domain compounds

The 17 newly synthesised QACs form four scaffold families (Figure 4), with no cation or cation-scaffold overlap with either the matched source panel or QAC-105. The CF3-dihydropyran mono-QACs are IT505, IT502 and IT499; kojic-acid-derived bis-QACs are DA253, PDD13, PDD14 and PDD11; tetrahydropyridine bis-QACs are IT442, IT469, IT452, IT493 and IT380; and glycoluril tetra-QACs are SEV-0338, SEV-035, SEV-036, SEV-030 and SEV-033. Codes follow the source spreadsheet, including SEV-0338.

This collection preserves the chemical scope of the original work. Kojic-acid-linked precursors are converted to bis-pyridinium salts through chlorination and quaternisation. A multicomponent tetrahydropyridine preparation supplies another bis-pyridinium family; the source synthesis records also describe competing pyran formation and epimerisation. The fluorinated dihydropyran precursors yield mono-QACs after N-alkylation, while a glycoluril-based multistep route supplies four-cation products. Reaction schemes, available characterisation and microbiological procedures are retained in Supporting Information Section S16, with missing primary spectra and assay provenance reserved for the chemistry coauthors. Scaffold novelty is verified from supplied structures and does not establish an independently blinded prospective discovery trial.

[FIGURE:structures]

Figure 4. The four OOD scaffold families, represented by exact named compounds and depicted in ACS 1996 style. The panel identifies mono-, bis- and tetra-cationic compounds and includes counterions. Full structures and codes for all 17 compounds, and a complete structure registry for the original 105 compounds, accompany the reproducibility files.

A final decoder trained on all 105 QACs predicts every OOD endpoint without using OOD activities in fitting or hyperparameter selection. Exact-value scoring retains 17 values for each task except E. coli MBC, where IT505 is reported as >500 mg/L and supplies only a lower bound. Table 4 reports endpoint MAE; RMSE, R², seed dispersion, per-family losses and every named prediction remain in Supporting Information. Averaging across the 67 exact pairs gives human MAE {oh.MAE:.3f} and RMSE {oh.RMSE:.3f}, versus continuous-MIC MAE {oq.MAE:.3f}/RMSE {oq.RMSE:.3f}, binary-MIC {ob.MAE:.3f}/{ob.RMSE:.3f}, and raw-feature {orr.MAE:.3f}/{orr.RMSE:.3f}, all in log2(mg/L).

[TABLE:ood]

Table 4. OOD endpoint MAE in log2(mg/L), mean ± source-seed SD. The fixed decoder is trained only on QAC-105. S. aureus MIC/MBC and E. coli MIC each have 17 exact values; E. coli MBC has 16 exact values and one separately reported >500 bound. Raw features have one run. Differences across five seeds describe optimisation variability, not uncertainty across independent chemical families.

Human representations have lower pooled error point estimates than the numerical and raw references in this small collection, but endpoint concentration accuracy remains limited: three of four human endpoint R² means are negative, with S. aureus MBC close to zero. The S. aureus MIC task-median reference has lower mean absolute error than the human-guided decoder. Moreover, all five human-guided E. coli MBC predictions for IT505 lie below its >500 mg/L bound (21.2–37.0 mg/L), an explicit extrapolation failure retained in the named prediction table.

The censored observation also bounds its error: IT505's E. coli MBC absolute error exceeds 3.76–4.56 log2 units across the human-guided seeds. Using its bound only as a minimum error contribution raises the human mean E. coli MBC RMSE lower bound to {censor.loc['Ec_MBC'].minimum_RMSE:.3f} and pooled 68-pair RMSE lower bound to {censor.loc['pooled'].minimum_RMSE:.3f}. The true errors can be larger; this sensitivity does not replace >500 by an exact measurement. All arms' minimum-error sensitivities are retained.

[FIGURE:violins]

Figure 5. Human-versus-continuous-MIC absolute-error distributions for each endpoint in QAC-105 and OOD-17. Each value is a molecule's mean absolute error over five source seeds. Left and right half-violins use the same exact-valued compounds; horizontal bars indicate medians and vertical bars IQR. OOD points are also shown individually. Density shape and median similarity do not establish equivalence or independent significance.

Four OOD scaffold groups provide little basis for stable interval estimation. The paired pooled human-minus-continuous ΔRMSE is {contrast('expert minus quant-continuous','OOD17')}, and human-minus-shuffled is {contrast('expert minus expert-shuffled','OOD17')}. These are exploratory percentile intervals conditional on the four observed families, not confirmatory population bounds; their apparent separation from zero cannot resolve general OOD superiority. A supplementary sensitivity omits each family in turn. Individual compounds and endpoint failures carry more practical information here than a single pooled score.

Direct source-only scoring asks a different question. The earlier matched human head, with no QAC decoder fitting, has mean OOD S. aureus MIC potency-rank agreement 0.667 ± 0.120 across five source seeds, compared with 0.399 ± 0.192 for continuous MIC. The paired human-minus-continuous and human-minus-shuffled rank intervals include zero. This is a suggestive ordering signal in 17 compounds, not an absolute concentration prediction: a binary human logit has no MIC units. Its outcomes are reported separately from the target-trained decoder and are not counted as replication.

### 2.5. What the controlled comparison identifies

The paired intervention changes which supervision is supplied to the same algorithm while retaining source chemistry, initialisation, source split and training schedule. Real-versus-shuffled labels preserve binary class counts or the continuous value distribution while disrupting the structure–label association. Improved loss under real human labels therefore concerns the learning procedure under that assignment. Comparison against raw features is needed in addition, because a trained representation may outperform a damaged shuffled representation without improving the original features.

On the cation-held-out pooled QAC loss, both real-versus-shuffled and human-versus-raw contrasts favour human guidance under the exploratory interval convention. This supports the usefulness of the available final labels in that setting. It does not identify the causal effect of a chemical fragment, charge count or assay protocol on antibacterial activity. Human-versus-continuous MIC also changes the objective, whereas binary MIC provides an objective-matched comparator. Unresolved differences are not statistical equivalence; no equivalence margin or annotation-to-measurement exchange rate is specified.

The original geometry and attribution analyses illustrate compression and reorganisation of foundation-model features. Similarity, t-SNE separation and SHAP attribution cannot by themselves identify a distinct biological component, prove that annotation denoises heterogeneous assays, or establish generalisation. Historical encoders were trained on archives overlapping the original target structures, so their favourable v5 tables and reconstructed task-coding results are preserved separately from the strict source-excluded comparisons. Assay heterogeneity motivates richer metadata; it does not make numerical measurements intrinsically inferior. Annotation information access and adjudication remain for coauthor completion.

## 3. Conclusions

Human Good/Bad calls can serve as molecular supervision for antibacterial QAC prediction. Under identical source chemistry and matched partial MolFormer training, their pooled cation-held-out QAC loss improves over raw features and shuffled-human controls, while remaining close to the continuous- and binary-MIC competitors. The exploratory scaffold-held-out follow-up retains a pooled-loss benefit over raw features, with a borderline real-versus-shuffled interval. This preserves the original question of economical human guidance without claiming that a label substitutes for a fixed number of assays.

Interpretation of the final labels as independent human knowledge remains provisional pending the annotation information-access and adjudication records in H1–H7. If annotators saw the quantitative endpoints, the comparison must be described as learning from human-compressed measurement information rather than an independent channel. The post-hoc scaffold follow-up and its borderline interval are hypothesis-generating.

The limits are equally clear. Holding out entire scaffold families is harder than holding out new cations, the 17-compound structural OOD collection does not establish accurate absolute concentrations, and text embeddings of four fixed task descriptions provide no consistently resolved advantage over one-hot metadata. Small projections remain a useful lower-cost design choice, but these comparisons do not show that fine-tuning is generally harmful or that internal adapters universally outperform it. The contribution is a traceable, controlled comparison of supervision and validation regimes, with the complete original cohort, named OOD compounds and unsuccessful predictions kept visible.

## 4. Experimental protocol

### 4.1. Human annotation collection and source curation

The final expert archive supplies 1,103 entries (244 Good, 859 Bad). Structure repairs, duplicate handling, eligibility counts, source-target exclusions and hashes are retained in the reproducibility manifests. Individual votes and adjudication logs are absent from the supplied computational archive; no inter-rater agreement is inferred from final calls. The following collection-method fields are reserved for the coauthors.

Pooled quantitative source MIC follows the archive's unified cross-organism field, including encoded censoring bounds, before molecule-level aggregation. It is not a homogeneous strain-specific measurement or the four target endpoints. This source definition is retained across real and shuffled quantitative arms and is separate from the explicit exact/bound treatment of the target workbooks.

{fields}

### 4.2. Matched representation learning

MolFormer-XL uses revision 7b12d946c181a37f6012b9dc3b002275de070314 (4). Embeddings and layers 0–3 remain frozen; layers 4–11, the pooler and dropout-0.1 scalar head are trained, totalling 28,375,297 trainable parameters. The 681-molecule panel and fixed 377/304 scaffold-disjoint source split are identical across human, continuous pooled MIC, binary MIC and their source-training-only shuffled controls. Five paired seeds (0–4) use identical initial weights, minibatch permutations and stochastic forward schedules. Binary MIC targets use a training-only threshold chosen to match human positive prevalence; both binary training arms contain 52 positive calls. Continuous source targets are standardised on source training and inverted for direct scores.

The reused source panel follows the archived v12 eligibility rules and excludes the cations of QAC, OOD and the supplementary Q-HERO cohort. This exclusion history is part of the panel definition even though the new main narrative centres QAC-105 and OOD-17.

Every source arm trains on exactly 377 molecule-level examples per epoch, with one equally weighted target per molecule. Continuous source MIC is the within-molecule median of log2 µM values from the pooled archive; binary MIC is derived from those molecule-level values. The 4,938 records contribute to aggregation across the full eligible panel and are not presented as repeated gradient examples in this matched experiment.

AdamW uses weight decay 0.01, a one-cycle schedule with peak learning rate 3 × 10−5, batch size 32 and norm-one gradient clipping. All arms use float32 and their final checkpoint after 30 epochs/360 updates; validation is diagnostic without early stopping. Native stochastic attention feature maps are refreshed during training and deterministic in evaluation. Reconstruction checkpoints retain trained parameters and replayed final persistent buffers, with all 30 full target-vector reproductions previously audited. This extension reuses those vectors and encodes the one previously omitted conflicting target. Three reference structures verify each restored model to a maximum vector difference below 4 × 10−6. No upstream retraining or target-based checkpoint selection occurs.

The raw reference is re-encoded from the same pinned model and environment. Historical human/quantitative 256-d encoder checkpoints, their common archived scaler and original raw features are kept as a separate overlapping-source reconstruction. They are not the matched intervention, an internal adapter, or a LoRA experiment.

### 4.3. Task encoding, target learning and validation

Target values are log2(MIC or MBC in mg/L), matching the original endpoint tables. This differs from earlier log2 µM analyses, which remain explicitly labelled in Supporting Information. Duplicate full-salt targets use the prepared historical median rule; the conflicting identity is named in Section 2.2. All 420 QAC training values are numeric and uncensored in the supplied workbook. OOD IT505 E. coli MBC is right-censored and is excluded from exact-value metrics without removing its molecule or bound.

CatBoost uses 300 iterations, depth five, learning rate 0.05, seed 1729 and two threads, without additional hand-selected descriptors or tuning. Cation-held-out GroupKFold supplies five folds of 21 salts each, grouping all four endpoints and all counterion variants. The follow-up scaffold GroupKFold instead groups the 29 canonical cation Murcko scaffolds. Fold assignment uses identities only. The final OOD decoder fits all QAC-105 rows and no OOD measurements. A task-median reference uses each task's training-fold median, or the full QAC median for OOD.

The cation counts in folds 0–4 are 20, 20, 21, 21 and 21, respectively. Folds 0 and 1 each contain one cation represented by two salt identities, yielding 21 salts per fold while preserving all 103 cation groups. No manual fold reassignment or outcome balancing is used.

One-hot metadata uses four species/endpoint indicators. Text metadata uses four fixed archived English descriptions, freshly reconstructed with openai/text-embedding-3-small via OpenRouter on the local computer and cached as a 4 × 1,536 float32 array. The request contains no measured activities or molecular structures. The cache SHA256 is 58f5b9417d437c18f69503322aec6923d03bbf05441d53e355cc1910600c1ff6; exact texts, model response metadata and checksums are archived. All primary real-label seeds and raw features use both encodings, while matched shuffled controls use one-hot. Historical encoders also use four separate endpoint decoders as a no-pooling comparison; these are not a reconstruction of every v5 hyperparameter.

### 4.4. Metrics, intervals and exploratory scope

RMSE, MAE, R² and Spearman correlation are recomputed from saved out-of-fold or OOD predictions for each seed and endpoint. Trained-arm tables report mean ± source-seed SD; plotted mean predictions do not replace mean seed-specific metrics. Pooled losses combine exact endpoint errors on a common log2 mg/L scale. Pooled R² is retained only in machine-readable tables and cannot establish within-task prediction skill.

Ten thousand paired bootstrap draws sample the observed scaffold groups with replacement and the five source-seed indices with replacement. The same group weights and sampled seed indices are applied to both arms in each contrast; all endpoints within a sampled group remain together. Each draw averages seed-specific RMSE, rather than evaluating an ensemble mean. Raw-feature predictions repeat the same fixed prediction across seed draws. Intervals are exploratory, unadjusted for multiple comparisons and conditional on fixed folds; OOD has only four groups. Five shuffled runs are diagnostic controls, not a calibrated permutation test. Frozen-feature, architecture, context and direct-score studies remain separate supplementary analyses.

The decoder seed is fixed for every arm; decoder-randomness variability is not represented in these intervals. Source-seed variability applies to the adapted representations, while the raw pretrained reference is fixed. Accordingly, the reported gains are conditional on this common decoder rather than a claim over all decoder initialisations.

The QAC-105/OOD-17 narrative was selected after inspecting earlier outcomes. The first extension protocol preceded its own decoder predictions; the all-endpoint scaffold sensitivity followed inspection and protocol reviews. Neither is a confirmatory preregistration. No new OOD families were selected by optimising these scores, and the prior Q-HERO outcomes remain available in Supporting Information rather than being discarded. Annotation blinding and the chronology of design, measurement and model access remain unresolved until the coauthors complete the collection and assay records.

### 4.5. Chemistry and microbiological measurements

The available synthetic procedures, characterisation descriptions, bacterial-strain information and MIC/MBC protocols are preserved in Supporting Information Section S16. Newly redrawn exact structures use ACS 1996 bond and atom-label settings. Primary spectra, optimisation material, assay controls and replicate records are reserved in field C1; the computational revision does not create new chemical or microbiological observations.

## Supporting Information

Full annotation/source audits; archived Q-HERO, backbone and numerical-context results; historical contrastive and task-encoding reconstructions; independently audited matched-training records; all original 105 structures and all 17 named OOD compounds; cation and scaffold folds; every prediction and censoring qualifier; endpoint-specific metrics, paired contrasts, curation and leave-one-family-out sensitivities; synthesis, characterisation and microbiological procedures. Main computations are in reproducibility/revision_v14; the separately labelled prior experiments remain in earlier revision directories.

## Data Availability Statement

{datafields}

## Author Contributions

[EXISTING:credit]

## Conflicts of Interest

The authors declare no competing financial interests.

## Acknowledgments

[EXISTING:acknowledgments]

OpenAI Codex assisted with analysis-code preparation, manuscript revision, figure preparation and consistency checks. Kimi Code and Claude Sonnet 4.6 supplied internal critical feedback. Text-embedding-3-small supplied four fixed task-description vectors. Numerical conclusions are supported by executable scripts and saved predictions; the human authors retain responsibility for the scientific content.

## References

[REFERENCES]
'''
    tables={'sources':[['Collection','Unit','Total','Used for learning','Use'],
        ['Expert archive','Final annotation entries',1103,'244 Good / 859 Bad','Curation source'],
        ['Matched source','Molecules / MIC records','681 / 4,938','377 train; 304 validation','Representation learning'],
        ['Original QAC','Full salts / cations','105 / 103','420 measured endpoints','Decoder CV and OOD training'],
        ['Own OOD','Named molecules / scaffolds','17 / 4','No target fitting','67 exact values; 1 bound']]}
    for key,frame,cohort,col in [('qac',s,'QAC105','RMSE'),('scaffold',scaffold,'QAC105','RMSE'),('ood',s,'OOD17','MAE')]:
        rows=[['Endpoint']+[LABEL[a] for a in ARMS]]
        for task in TASKS:
            line=[TLABEL[task]]
            for arm in ARMS:
                row=frame[(frame.arm==arm)&(frame.cohort==cohort)&(frame.task==task)&(frame.encoding=='onehot')].iloc[0]
                value=f'{row[col]:.3f}'
                if row.seeds==5:value+=f' ± {row[col+"_sd"]:.3f}'
                if col=='RMSE':value+=f' (R² {row.R2:.3f})'
                line.append(value)
            rows.append(line)
        tables[key]=rows
    (ROOT/'main_draft.md').write_text(draft)
    return draft,tables

def main():
    draft,tables=prepare()
    files,tree,oldbody=v.read_doc(COMA/'2026_10_11_Paper_2_edited-v12_matched_finetuning.docx')
    old=list(oldbody);normal=next(p for p in oldbody if h.text(p).startswith('Supervision for molecular learning'))
    template=next(t for t in oldbody.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
    sec=copy.deepcopy(oldbody.find('w:sectPr',NS));credit=copy.deepcopy(h.find(oldbody,'Egor A. Ilin: Conceptualization'));ack=copy.deepcopy(h.find(oldbody,'This work was supported by the Russian Science Foundation'))
    refidx=next(i for i,p in enumerate(old) if h.text(p)=='References');refs=[copy.deepcopy(p) for p in old[refidx+1:] if h.text(p)]
    abstractidx=next(i for i,p in enumerate(old) if h.text(p)=='Abstract');authors=[copy.deepcopy(p) for p in old[1:abstractidx]]
    body=E.Element('{'+W+'}body');tree.remove(oldbody);tree.append(body)
    for block in draft.strip().split('\n\n'):
        if block.startswith('# '):
            body.append(v.paragraph(normal,block[2:],1))
            for p in authors:body.append(p)
        elif block.startswith('#'):
            hashes=len(block)-len(block.lstrip('#'));body.append(v.paragraph(normal,block[hashes:].strip(),min(hashes-1,3)))
        elif block.startswith('[FIGURE:'):
            key=block[8:-1];body.append(v.embed(files,ROOT/'figures'/FIGURES[key],'rIdV14'+key.title()))
        elif block.startswith('[TABLE:'):body.append(h.table(template,tables[block[7:-1]]))
        elif block=='[EXISTING:credit]':body.append(credit)
        elif block=='[EXISTING:acknowledgments]':body.append(ack)
        elif block=='[REFERENCES]':
            for p in refs:body.append(p)
        else:body.append(v.paragraph(normal,block,marked=block.startswith('[COAUTHORS')))
    body.append(sec);v.unique_ids(tree);h.write(files,tree,MAIN)
    v.TITLE=TITLE;v.exports(files,tree,ROOT/'manuscript_v14_readable.md',ROOT/'manuscript_v14.html')
    build_si(normal,template);print(MAIN)

def build_si(normal,template):
    files,tree,body=v.read_doc(ROOT.parent/'revision_v12/Supplementary_Information_v12.docx')
    sec=body.find('w:sectPr',NS)
    for node in body.findall('w:p',NS):
        text=h.text(node);revised=text.replace('main Section 2.1.1','main Section 4.1')
        revised=revised.replace('main Sections 3.2–3.3','archived v12 main Sections 3.2–3.3')
        revised=revised.replace('the main text reports the nested seed/scaffold sensitivity','the archived v12 main text reports the nested seed/scaffold sensitivity')
        if text.startswith('To examine out-of-domain behaviour, we assembled'):
            revised='The source manuscript reports synthesis and activity measurements for 17 QACs from the four scaffold families listed below. This collection is structurally held out from the supplied training collections. Final assay conditions, measurement chronology and the independence of experimental assessment are reserved for coauthor completion in C1; the computational analysis treats the set as a small descriptive case study.'
        if revised!=text:h.replace(node,revised)
    note=v.paragraph(normal,'Scope of the QAC-105/OOD-17 revision',1)
    body.insert(0,note)
    body.insert(1,v.paragraph(normal,'The main article now centres the original 105 QAC structures and the named 17-molecule structural OOD case study. Prior Q-HERO, frozen-feature, backbone, numerical-context and direct-score analyses are preserved below as archived supplementary evidence. They are not the primary evaluation in the new main article. Sections S19–S20 add the new four-endpoint mg/L experiment and exact registries; older micromolar metrics and different cohorts remain labelled separately.'))
    def append(node):body.insert(list(body).index(sec),node)
    def add(text,level=None):append(v.paragraph(normal,text,level))
    def table(rows):append(h.table(template,rows))
    add('S19. Original-cohort four-endpoint evaluation',1)
    add('All new concentration metrics use log2 mg/L. Cation-held-out QAC-105 CV is an interpolation test and permits scaffold overlap. The follow-up scaffold-held-out QAC-105 uses all 29 scaffold families. OOD-17 uses a decoder trained on the 105 structures only. Human annotation fields remain in main Section 4.1; chemical field C1 and source procedures remain in S16. All protocols, hashes, model snapshots, folds, per-seed predictions and reviews are in revision_v14.')
    add('Table S16. Endpoint-specific results for all new primary and historical configurations. Trained arms are mean ± source-seed SD. Legacy arms overlap the original target in representation learning and are descriptive; they are segregated by provenance. OOD E. coli MBC uses 16 exact observations; its one bound is retained separately.')
    s=pd.read_csv(ROOT/'analysis/summary.csv')
    for provenance in ['matched-source-excluded','target-training-only','legacy-overlapping-source']:
        add('Provenance: '+provenance,2)
        rows=[['Cohort / task','Arm / encoding','Seeds / n','RMSE ± SD','R² ± SD']]
        for row in s[(s.provenance==provenance)&(s.task!='pooled')].itertuples():
            rows.append([row.cohort+' / '+row.task,row.arm+' / '+row.encoding,f'{row.seeds} / {row.n}',f'{row.RMSE:.3f} ± {row.RMSE_sd:.3f}',f'{row.R2:.3f} ± {row.R2_sd:.3f}'])
        table(rows)
    add('Table S17. Paired pooled-loss contrasts. Ten thousand paired seed/scaffold draws; exploratory, unadjusted and conditional on fixed predictions. OOD has four groups, so these intervals cannot supply stable population bounds. Endpoint-specific intervals are retained in analysis/contrasts.csv.')
    rows=[['Cohort','Comparison','ΔRMSE','95% lower','95% upper']]
    for row in pd.read_csv(ROOT/'analysis/contrasts.csv').query("task=='pooled'").itertuples():
        rows.append([row.cohort,row.comparison,f'{row.delta_RMSE:+.3f}',f'{row.ci_low:+.3f}',f'{row.ci_high:+.3f}'])
    table(rows)
    add('Table S18. Scaffold-held-out QAC-105, full controls and all endpoints. Every structure from the same cation-scaffold family remains in one target fold. The follow-up was specified after inspection of this extension; existing source training and target hyperparameters were retained.')
    rows=[['Task','Arm','Seeds / n','RMSE ± SD','R² ± SD']]
    for row in pd.read_csv(ROOT/'analysis/scaffold_summary.csv').query("cohort=='QAC105' and task!='pooled'").itertuples():
        rows.append([row.task,row.arm,f'{row.seeds} / {row.n}',f'{row.RMSE:.3f} ± {row.RMSE_sd:.3f}',f'{row.R2:.3f} ± {row.R2_sd:.3f}'])
    table(rows)
    for name,caption in [('figureS19_OOD17_parity','Figure S19. Exact OOD endpoint parity. The right-facing triangle denotes the >500 mg/L bound for IT505 E. coli MBC; it is excluded from exact-value statistics. Displayed points average predictions across seeds, while boxes give mean seed-specific metrics. These are concentration-prediction failures as well as successes, not a prospectively blinded discovery validation.'),
        ('figureS20_OOD17_individual_endpoints','Figure S20. Every named OOD prediction by endpoint. Diamonds are exact measurements, the upward triangle is the IT505 MBC lower bound, circles are model predictions and bars source-seed SD. Vertical separators divide the four scaffold families. The complete table and qualifiers are in analysis/OOD17_all_predictions_named.csv.'),
        ('figureS21_scaffold_transfer','Figure S21. Cation-held-out versus scaffold-held-out original-cohort performance, by endpoint. The same source representations and one-hot decoder are used. Colours denote supervision and markers denote validation regime. Source-seed SD does not capture sampling uncertainty across chemical families.')]:
        append(v.embed(files,ROOT/'figures'/(name+'.png'),'rIdV14'+name));add(caption)
    add('S20. Complete original and OOD registries',1)
    add('Table S19. All 105 original full-salt identities and their raw row identifiers. Exact structures are in original_QAC105_structures.pdf and data/QAC105.csv; all four endpoints and their fold assignments are machine-readable. The conflicting full-salt identity retains its historical median in the 105-cohort view and is flagged. Original rows are zero-based identifiers from the workbook.')
    rows=[['Compound ID','Original rows','Charge','Sa MIC (mg/L)','Curation status']]
    q=pd.read_csv(ROOT/'data/QAC105.csv')
    for row in q.itertuples():rows.append([row.compound_id,row.original_row_ids,row.formal_charge,f'{row.sa_mic_mg_l:g}','Conflicting duplicate' if row.label_conflict else 'Retained'])
    table(rows)
    add('Table S20. All 17 OOD compounds and supplied endpoint values in mg/L. Exact molecular structures, salts and source codes are retained. Each family has zero cation-scaffold overlap with both the matched source panel and QAC-105.')
    rows=[['Code / family','Sa MIC','Sa MBC','Ec MIC','Ec MBC']]
    o=pd.read_csv(ROOT/'data/OOD17.csv')
    for row in o.itertuples():
        rows.append([row.code+' / '+row.scaffold_group,f'{row.sa_mic_mg_l:g}',f'{row.sa_mbc_mg_l:g}',f'{row.ec_mic_mg_l:g}',('>' if row.ec_mbc_mg_l_qualifier=='>' else '')+f'{row.ec_mbc_mg_l:g}'])
    table(rows)
    add('Table S21. Leave-one-OOD-family-out score sensitivity. Each row removes a family only during scoring; no model is fitted on OOD. It probes whether the pooled error contrast depends on one family and does not expand the four-family population.')
    rows=[['Omitted family','Exact pairs','Human RMSE','Continuous RMSE','Human − continuous']]
    for row in pd.read_csv(ROOT/'analysis/OOD_leave_one_family_out.csv').itertuples():rows.append([row.omitted_family,row.exact_pairs,f'{row.human_RMSE:.3f}',f'{row.continuous_RMSE:.3f}',f'{row.delta_RMSE:+.3f}'])
    table(rows)
    add('Table S22. Right-censored endpoint minimum-error sensitivity. Exact residuals are combined with max(lower bound − prediction, 0) for IT505 E. coli MBC. Values are lower bounds on the true RMSE and MAE, not metrics obtained by declaring the bound exact. Endpoint Ec MBC uses 16 exact values plus one bound; pooled scoring uses 67 exact values plus that bound.')
    rows=[['Arm / encoding','Task','Seeds','Minimum RMSE ± SD','Minimum MAE']]
    for row in pd.read_csv(ROOT/'analysis/censoring_minimum_error_summary.csv').query("encoding=='onehot' and arm in ['expert','quant-continuous','quant-binary','raw-molformer']").itertuples():
        rows.append([row.arm+' / '+row.encoding,row.task,row.seeds,f'{row.minimum_RMSE:.3f} ± {row.minimum_RMSE_sd:.3f}',f'{row.minimum_MAE:.3f}'])
    table(rows)
    add('The complete ACS 1996 structure atlases are standalone vector PDF/SVG files in revision_v14/figures. Original individual structures remain in revision_v13/figures/molecules_ACS1996. Primary compound spectra and missing assay records remain reserved for coauthors; vector depictions are not evidence of identity or purity.')
    v.unique_ids(tree);h.write(files,tree,ROOT/'Supplementary_Information_v14.docx')
    v.exports(files,tree,ROOT/'supplement_v14_readable.md',ROOT/'Supplementary_Information_v14.html')

if __name__=='__main__':main()
