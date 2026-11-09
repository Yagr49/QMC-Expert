Supporting Information — author workflows, CV and source-seed variability

Human Judgement as Molecular Supervision: Matched Quantitative Comparisons and Scaffold Transfer in Quaternary Ammonium Biocides

Original supplementary figures and expanded computational record

Figures S1–S4 preserve the four original author-supplied figures. Their classification and geometrical analyses are retained as historical material with their own protocol; they do not substitute for the new source-excluded MIC/MBC regression comparisons. Earlier computational Figures S1–S22 are renumbered S5–S26. Section and table numbers retain their existing sequence.


Figure S1. F1 scores across four representations in the original five-fold classification study. Retained from the author’s original Supporting_Info.docx; this is separate from the matched MIC/MBC regression and weight-intervention protocols.


Figure S2. Classification accuracy across representations in the original supplementary study. Retained from the author’s original Supporting_Info.docx; this is separate from the matched MIC/MBC regression and weight-intervention protocols.


Figure S3. Fold-specific classification scores from the original supplementary study. Retained from the author’s original Supporting_Info.docx; this is separate from the matched MIC/MBC regression and weight-intervention protocols.


Figure S4. Geometrical cluster diagnostics before and after the historical contrastive encoder. Retained from the author’s original Supporting_Info.docx; this is separate from the matched MIC/MBC regression and weight-intervention protocols.

Scope of the QAC-105/OOD-17 revision and fixed-model extension

The main article now centres the original 105 QAC structures and the named 17-molecule structural OOD case study. Prior Q-HERO, frozen-feature, backbone, numerical-context and direct-score analyses are preserved below as archived supplementary evidence. They are not the primary evaluation in the new main article. Sections S19–S20 add the new four-endpoint mg/L experiment and exact registries; older micromolar metrics and different cohorts remain labelled separately. Sections S21–S22 add the completed model comparison and independent reproduction audit from 12 October 2026. Older sections retain their archival protocols; recovered notebook provenance is described below and does not merge May and July metrics into one result. Sections S23–S27 add completed direct-target fine-tuning, weight rewinds and the publication metric audit; earlier section numbers and archival experiments are retained.

Supporting Information — Human Supervision and Controlled Quantitative Comparisons

Human versus Quantitative Supervision for Antibacterial Molecular Representation Learning

Scope and evaluation protocols

This Supporting Information accompanies the focused author draft. Partial-fine-tuning, matched frozen-feature and historical analyses use different source exclusions, cohorts and architectures. Their results are reported separately; source metadata and full prediction files accompany the computational analyses.

The main comparisons use partial backbone fine-tuning or frozen-feature adaptation as specified. MIC record counts are distinguished from unique molecules. OOD-17 is a small secondary collection, affine recalibration is exploratory and in-sample, and individual expert votes and a pre-specified equivalence criterion are unavailable in the supplied archive. The human-annotation collection protocol is reserved for coauthor completion in main Section 4.1.

S1. Dataset audit and annotation provenance

The expert archive contains 1,103 final labels (859 Bad, 244 Good). Individual votes and adjudication records are absent, so the historical three-expert majority-vote procedure cannot be independently verified and inter-rater agreement cannot be calculated. The expert and quantitative collections substantially overlap at molecule level. This produces a controlled comparison of coarse and quantitative supervision on related chemical space, not a comparison of independent datasets.

Table S1. Canonical-molecule overlap (from reproducibility/leakage_check.py).

| Collection | Canonical molecules | ∩ expert | ∩ quantitative | Source/evaluation role |
| --- | --- | --- | --- | --- |
| Expert final labels | 1,066 | 1,066 | 1,035 | supervision source |
| Quantitative corpus | 1,515 | 1,035 | 1,515 | supervision source |
| QAC-105 | 105 | 105 | 99 | in-domain / historical |
| Q-HERO | 411 | 222 | 255 | external benchmark |
| OOD-17 | 17 | 0 | 0 | small case study |


Figure S5. Expert-label audit: class balance and annotation-round drift. The final labels are the available supervision artifact; individual votes are not archived.


Figure S6. Molecule-level overlap. The overlap is a design feature for a controlled supervision comparison but limits claims of independent dataset superiority.

S2. Q-HERO external benchmark and residual distributions

The historical Q-HERO collection contains 411 structures with a matched S. aureus MIC endpoint. The archived residual plots are descriptive. These analyses precede the strict evaluation-cation exclusions and matched controls used for Q-HERO-405; they do not establish equivalence or an independently identified expert advantage.


Figure S7. Historical absolute-residual distributions on Q-HERO. Similar distribution shapes are descriptive and do not establish equivalence; cohort and source exclusions differ from the matched Q-HERO-405 experiments.


Figure S8. Q-HERO benchmark results. Interpret representation differences with the reported seed variation and the controlled overlap design.

S3. Historical OOD comparison

The historical 17-compound comparison is retained under its original log2 micromolar protocol, separately from the four-endpoint mg/L comparison in the current main article. The recovered May endpoint-residual bootstrap gives human minus regression mean ΔRMSE −0.086 [−0.227, +0.054]. It is descriptive, samples dependent endpoint residuals individually and does not establish statistical equivalence. The July metric provenance and the different modern grouped comparisons are documented in S22.


Figure S9. Historical residual and TOST analysis, retained for transparency. The small sample and absence of a pre-specified equivalence margin make the analysis exploratory.


Figure S10. Split-design effect. Pair-level splitting can place the same molecule in train and test; molecule-grouped splits are required for conservative inference.

S4. Partial fine-tuning and downstream refitting

MolFormer-XL was partially fine-tuned: the embedding layer and four lower encoder layers remain frozen (16.0/44.4 M parameters). Evaluation molecules were excluded from all fine-tuning sources. Under downstream refitting, mean Q-HERO R² is +0.269 for 740 final expert labels, +0.312 for 1,153 molecule-level MIC values, and +0.308 for 9,338 MIC records. This supports comparable representation quality under this protocol, not equivalence of individual labels.

Table S2. Representation quality, mean ± SD across three seeds (from finetune/runs.jsonl).

| Representation | QAC-105 R² | Q-HERO R² | OOD-17 R² | Protocol |
| --- | --- | --- | --- | --- |
| Predict-the-mean | +0.000 | +0.000 | −0.058 | null baseline |
| 6 descriptors | −0.310 | +0.057 | −0.486 | null baseline |
| Frozen MolFormer | −0.105 ± 0.03 | +0.134 ± 0.02 | −0.289 ± 0.09 | no FT |
| Partial FT expert | +0.053 ± 0.09 | +0.269 ± 0.02 | −0.174 ± 0.19 | 740 labels |
| Partial FT quantitative | −0.004 ± 0.04 | +0.312 ± 0.06 | −0.191 ± 0.21 | 1,153 molecules |
| Partial FT quantitative | +0.048 ± 0.07 | +0.308 ± 0.03 | −0.027 ± 0.09 | 9,338 records |


Figure S11. Downstream representation quality, mean ± standard deviation over three seeds, after partial backbone fine-tuning. The descriptor baseline is positive on Q-HERO (R² = +0.057); absolute scores remain modest.

S5. Direct zero-shot transfer and exploratory calibration

Without target refitting, quantitative supervision produces stronger rank agreement than expert supervision on Q-HERO and OOD-17, while raw R² remains negative. The highest OOD-17 mean rank agreement is ρ = 0.75 for the 9,338-record model; this estimate has n = 17. Expert scores still carry positive potency-related rank signal despite never observing concentrations.

Table S3. Direct-transfer rank agreement and AUC, means across three seeds (from finetune/runs_direct.jsonl).

| Source | QAC-105 ρ / AUC | Q-HERO ρ / AUC | OOD-17 ρ / AUC | Interpretation |
| --- | --- | --- | --- | --- |
| Expert (740 labels) | +0.221 / 0.644 | +0.397 / 0.688 | +0.295 / 0.597 | rank signal only |
| Quant. 1,153 molecules | +0.210 / 0.652 | +0.547 / 0.780 | +0.619 / 0.852 | stronger ranking |
| Quant. 9,338 records | +0.176 / 0.630 | +0.612 / 0.814 | +0.752 / 0.866 | strongest; OOD n=17 |


Figure S12. Direct zero-shot transfer. These predictions are best interpreted as rankings, not calibrated absolute MIC estimates.

Affine recalibration was fitted and evaluated on the same target predictions. It is included only as an exploratory diagnostic of scale mismatch; it does not demonstrate generalisable target calibration.

Table S4. Exploratory in-sample affine recalibration (from finetune/recalibration.csv).

| Target | Raw R² | In-sample affine R² | Mean slope | Mean offset log₂ |
| --- | --- | --- | --- | --- |
| QAC-105 | −0.83 | +0.03 | 0.23 | +1.20 |
| Q-HERO | −1.62 | +0.36 | 0.47 | +2.11 |
| OOD-17 | −2.92 | +0.49 | 0.98 | +3.01 |


Figure S13. Exploratory in-sample affine recalibration. A held-out or nested target-calibration protocol is required before reporting calibrated generalisation.

S6. Reproducibility inventory and limitations

Primary archived artifacts include reproducibility/finetune/runs.jsonl, runs_direct.jsonl, recalibration.csv, qhero/qhero_metrics.csv, qhero_residuals.csv and analysis/ablation_bootstrap.csv. April–May notebook snapshots and a July SHAP/causal-analysis notebook were recovered on 12 October 2026, including code and saved metric outputs. The updated FINDINGS.md and S22 distinguish the provenance recovered from exact independent reproduction. Geometry and attribution remain descriptive; they do not identify biological causal mechanisms.

S7. New controlled supervision experiments

The new experiment holds source molecules, source cation-scaffold split, frozen MolFormer features, initial weights and training budget constant within each matched panel. Source sizes: 681 pooled-MIC common molecules (4,938 underlying records) and 529 exact S. aureus-MIC common molecules (855 records). Evaluation sizes: QAC-104 = 104, Q-HERO-405 = 405, OOD-17 = 17. Every evaluation cation, including counterion variants, is absent from all new sources. Binary source labels use BCE-with-logits; quantitative source targets use source-training standardised MSE. A 768→256→128 neural encoder is trained for 80 epochs with five paired seeds. Target decoders refit on fixed target folds, so this is representation evaluation rather than direct transfer. Bootstrap intervals condition on those folds and trained seeds. The Ridge decoder with target-training standardisation can extrapolate unstably; all extreme results remain available. No non-inferiority or equivalence margin is introduced.


Figure S14. Earlier supervision comparisons, retained as supplementary context. Partial-fine-tuning and frozen-feature panels have different cohorts and architectures. Error bars are conditional-scaffold intervals; the archived v12 main text reports the nested seed/scaffold sensitivity.

Table S5. New experiment RMSE in log2 µM, mean ± SD across five source-training seeds (one raw baseline run). Both CatBoost and Ridge are reported. Extreme Ridge errors are retained as sensitivity results rather than removed.

| Panel | Supervision / decoder | QAC-104 RMSE | Q-HERO-405 RMSE | OOD-17 RMSE |
| --- | --- | --- | --- | --- |
| baseline | raw-molformer / catboost | 2.074 | 1.602 | 1.698 |
| baseline | raw-molformer / ridge | 2.240 | 2.187 | 3.173 |
| matched-pooled | expert / catboost | 2.207 ± 0.037 | 1.607 ± 0.032 | 1.836 ± 0.203 |
| matched-pooled | expert / ridge | 2.364 ± 0.273 | 2.412 ± 1.391 | 2.048 ± 0.699 |
| matched-pooled | expert-shuffled / catboost | 2.192 ± 0.049 | 1.780 ± 0.105 | 1.916 ± 0.182 |
| matched-pooled | expert-shuffled / ridge | 2.525 ± 0.656 | 1.877 ± 0.102 | 2.030 ± 0.184 |
| matched-pooled | quant-binary / catboost | 2.064 ± 0.108 | 1.646 ± 0.041 | 1.927 ± 0.214 |
| matched-pooled | quant-binary / ridge | 2.049 ± 0.054 | 1.738 ± 0.124 | 2.318 ± 0.664 |
| matched-pooled | quant-continuous / catboost | 2.033 ± 0.047 | 1.497 ± 0.052 | 1.986 ± 0.177 |
| matched-pooled | quant-continuous / ridge | 3612.647 ± 8059.806 | 2.559 ± 0.786 | 7.191 ± 5.484 |
| matched-pooled | quant-shuffled / catboost | 2.068 ± 0.095 | 1.605 ± 0.050 | 1.909 ± 0.165 |
| matched-pooled | quant-shuffled / ridge | 3.206 ± 0.908 | 3.978 ± 1.342 | 7.624 ± 11.194 |
| matched-pooled | untrained / catboost | 1.994 ± 0.047 | 1.666 ± 0.074 | 1.821 ± 0.122 |
| matched-pooled | untrained / ridge | 4.466 ± 4.042 | 3.190 ± 0.813 | 15.258 ± 20.300 |
| matched-sa | expert / catboost | 2.092 ± 0.073 | 1.785 ± 0.075 | 2.257 ± 0.416 |
| matched-sa | expert / ridge | 11.183 ± 11.272 | 3.517 ± 2.538 | 2.909 ± 1.886 |
| matched-sa | expert-shuffled / catboost | 2.141 ± 0.137 | 1.761 ± 0.040 | 2.078 ± 0.201 |
| matched-sa | expert-shuffled / ridge | 2.404 ± 0.638 | 1.987 ± 0.415 | 5.493 ± 7.625 |
| matched-sa | quant-binary / catboost | 2.030 ± 0.088 | 1.730 ± 0.022 | 1.959 ± 0.209 |
| matched-sa | quant-binary / ridge | 2.457 ± 0.779 | 2.017 ± 0.360 | 1.984 ± 0.269 |
| matched-sa | quant-continuous / catboost | 2.075 ± 0.059 | 1.617 ± 0.016 | 2.047 ± 0.168 |
| matched-sa | quant-continuous / ridge | 5.557 ± 2.448 | 2.237 ± 0.188 | 4.191 ± 1.787 |
| matched-sa | quant-shuffled / catboost | 2.229 ± 0.117 | 1.670 ± 0.069 | 1.818 ± 0.276 |
| matched-sa | quant-shuffled / ridge | 6.942 ± 5.095 | 32.905 ± 42.839 | 5.285 ± 0.886 |
| matched-sa | untrained / catboost | 2.022 ± 0.053 | 1.677 ± 0.032 | 1.891 ± 0.161 |
| matched-sa | untrained / ridge | 5.308 ± 3.679 | 3.291 ± 1.476 | 5.811 ± 1.834 |
| full | expert-full / catboost | 2.065 ± 0.017 | 1.631 ± 0.060 | 2.112 ± 0.232 |
| full | expert-full / ridge | 2.213 ± 0.092 | 1.853 ± 0.226 | 1.808 ± 0.285 |
| full | quant-iltox-full / catboost | 1.944 ± 0.084 | 1.641 ± 0.059 | 1.719 ± 0.146 |
| full | quant-iltox-full / ridge | 4.187 ± 2.603 | 3.204 ± 0.496 | 8.874 ± 12.739 |
| full | quant-pooled-full / catboost | 2.091 ± 0.114 | 1.489 ± 0.027 | 1.779 ± 0.125 |
| full | quant-pooled-full / ridge | 7.313 ± 7.252 | 2.494 ± 1.162 | 2.654 ± 0.588 |
| full | quant-sa-full / catboost | 2.041 ± 0.065 | 1.547 ± 0.064 | 1.906 ± 0.134 |
| full | quant-sa-full / ridge | 5.224 ± 4.519 | 9.759 ± 16.934 | 41.728 ± 75.709 |

S8. Paired supervision contrasts

Table S6. Q-HERO-405 CatBoost expert-minus-comparator ΔRMSE with 95% whole-scaffold bootstrap intervals. Negative values favour expert supervision. Contrasts average squared errors across seeds before forming RMSE; they therefore differ slightly from subtracting the means of seed-specific RMSE.

| Panel | Expert minus | ΔRMSE | 95% lower | 95% upper |
| --- | --- | --- | --- | --- |
| matched-pooled | quant-continuous | +0.109 | +0.007 | +0.210 |
| matched-pooled | quant-binary | -0.039 | -0.139 | +0.136 |
| matched-pooled | expert-shuffled | -0.175 | -0.258 | -0.058 |
| matched-pooled | quant-shuffled | +0.002 | -0.100 | +0.097 |
| matched-pooled | untrained | -0.060 | -0.138 | +0.037 |
| matched-pooled | raw-molformer | +0.005 | -0.092 | +0.109 |
| matched-sa | quant-continuous | +0.169 | -0.004 | +0.454 |
| matched-sa | quant-binary | +0.056 | -0.126 | +0.346 |
| matched-sa | expert-shuffled | +0.025 | -0.139 | +0.311 |
| matched-sa | quant-shuffled | +0.116 | -0.035 | +0.359 |
| matched-sa | untrained | +0.109 | -0.051 | +0.354 |
| matched-sa | raw-molformer | +0.185 | +0.056 | +0.380 |

S9. Quantitative-source provenance and interpretation

The full eligible sources contain 712 final expert-labelled molecules, 1,120 pooled-MIC molecules, 888 exact S. aureus-MIC molecules and 273 ILToxDB molecules. The QMR source is one corpus represented with different filters and aggregation, not multiple independent datasets. The three earlier Veresh workbooks are corpus versions. Q-HERO is the external antibacterial evaluation collection in the new experiment. Full-source comparisons vary chemistry and sample size and cannot identify endpoint/provenance effects.

QMR same-compound/same-strain repeated-report audit: 38 strata over 23 compounds and five strains, median range 0 log2, 94.7% within one dilution. Within-group strain sensitivity: 279 strata, median range 1 log2. These results do not support assigning all discordant pooled records to laboratory error. The cytotoxicity export mixes CC50/IC50/EC50 in one field, even after restricting to 24h MTT. Source-comparison and repeat-range results are descriptive.

S10. What the experiment identifies

The manipulated variable is supervision inside a fixed training algorithm. Expert versus shuffled expert contrasts preserve sample identities, initialisation, source split, architecture, objective and training budget. Expert versus continuous MIC also changes the loss objective. The paired effect is conditional on the declared source chemistry, architecture and transfer protocol. The real-label advantage appears in the 681-molecule pooled panel, and does not replicate in the 529-molecule organism-matched panel. No antibacterial mechanism, universal denoising effect, non-inferiority margin or economic saving is identified.

The quantitative continuous arm is stronger than expert supervision in the pooled frozen-head panel. The historical partial-fine-tuning analysis still shows practical competition. These observations answer different questions and must be reported together. A successful label-versus-shuffled-label contrast does not by itself demonstrate an improvement over the raw backbone or over the best quantitative source.

S11. Reproducibility and artifact inventory

Reproducibility files: revision_v9/PROTOCOL.md; prepare_experiment.py; run_interventions.py; analyse_interventions.py; data/meta.json; data/smiles.json and molformer.npy; results_*/training.csv, target_folds.csv, metrics.csv and predictions.csv; analysis/summary.csv and paired_bootstrap.csv. Input workbook hashes, feature hashes, initial-weight hashes and matched-source-identity hashes are recorded. The protocol was written before inspecting new prediction results, but follows earlier exploratory work and is not formal preregistration.

The historical direct expert seed-0 predictions provide Spearman ρ = 0.453 on Q-HERO, with a molecule-bootstrap interval [0.373, 0.526]. This interval is conditional on one checkpoint and does not account for scaffold dependence; the manuscript therefore leads with the three-seed mean rank result and treats this additional interval as a descriptive sensitivity analysis. Corresponding OOD-17 and QAC-105 intervals are retained in analysis/archived_direct_expert_rank.csv.

Original v8 sections remain the supporting record for the historical analyses. Their revision labels refer to the archived experiment. The new results do not retrospectively repair the historical few-shot scan, make in-sample calibration external, or recover individual expert votes.

S12. Modern checkpoint and context extension

# Exploratory extension fixed before inspecting new outputs (11 October 2026)
This extension follows already inspected v9 and Mendeley results and Kimi review. It is not preregistered. No performance-based model or checkpoint selection.

Models selected by publication/availability: ChemFM/ChemFM-1B (ChemFM, Communications Chemistry, online Dec 2025); DeepChem/MoLFormer-c3-1.1B and DeepChem/ChemBERTa-100M-MLM (ChemBERTa-3, Digital Discovery 2026). Hugging Face commit SHA pinned before extraction. The c3 name counts pretraining molecules, not parameters.
All 1939 canonical full salts from v9 are encoded, without concentration labels, on the supplied server. ChemFM uses last non-padding token (causal encoder, compatible with sequence-classification convention); RoBERTa/ChemBERTa uses attention-masked mean hidden states (avoids randomly initialized pooler); c3 uses deterministic MoLFormer pooler. Verify no truncation; abort if a molecule exceeds model context. These are frozen-feature probes, not reproductions of fully fine-tuned published leaderboards. Unsupervised pretraining membership of evaluation compounds is unknown.

Identical archived target-cation exclusions and target folds. CatBoost decoder unchanged. Within each backbone, source matched-pooled panel (681 molecules), source scaffold train/validation, five seeds, 80 epochs, minibatch and initial weights paired. Arms: expert, continuous MIC, binary MIC prevalence-matched, expert shuffled, continuous shuffled, binary MIC shuffled, untrained encoder, raw backbone. Network input dimension follows the backbone, remaining layers 256 and128. Training architecture capacity thus differs across backbones; compare supervision contrasts within backbone, not as a pure parameter-count effect. CPU encoder training keeps RNG convention consistent with v9. Fixed learning parameters, no target-driven tuning.

Context sensitivity uses the identical 529 common molecules with expert labels, pooled quantitative MIC and exact S. aureus MIC and respective shuffled controls. Input MolFormer features/initial weights/source split/budget identical. This is an algorithmic intervention in the target definition and aggregation policy, not an isolated effect of provenance: organism mixture, censoring, number of observations and aggregation all vary.

Primary descriptive focus Q-HERO-405 scaffold-held-out predictions. Report all targets and arms. Bootstrap whole scaffolds conditional on trained seeds plus nested seed/scaffold sensitivity; designate all extension comparisons exploratory with no multiplicity-adjusted significance claims. Existing v9 raw results retained. Repeated scaffold assignments and leave-one-scaffold-out loss sensitivity quantify evaluation dependence. Do not claim human denoising, equivalence/noninferiority, or biological causal mechanism.

| Backbone / panel | Supervision / target | Seeds | R² ± seed SD | RMSE ± seed SD |
| --- | --- | --- | --- | --- |
| c3-MoLFormer / baseline | raw-c3-molformer / OOD-17 | 1 | -0.269 ± nan | 1.852 ± nan |
| c3-MoLFormer / baseline | raw-c3-molformer / Q-HERO-405 | 1 | +0.076 ± nan | 1.649 ± nan |
| c3-MoLFormer / baseline | raw-c3-molformer / QAC-104 | 1 | -0.076 ± nan | 1.984 ± nan |
| c3-MoLFormer / matched-pooled | expert / OOD-17 | 5 | -0.796 ± 0.152 | 2.201 ± 0.092 |
| c3-MoLFormer / matched-pooled | expert / Q-HERO-405 | 5 | +0.010 ± 0.055 | 1.705 ± 0.047 |
| c3-MoLFormer / matched-pooled | expert / QAC-104 | 5 | -0.193 ± 0.045 | 2.089 ± 0.040 |
| c3-MoLFormer / matched-pooled | expert-shuffled / OOD-17 | 5 | -0.261 ± 0.357 | 1.832 ± 0.256 |
| c3-MoLFormer / matched-pooled | expert-shuffled / Q-HERO-405 | 5 | -0.125 ± 0.076 | 1.818 ± 0.061 |
| c3-MoLFormer / matched-pooled | expert-shuffled / QAC-104 | 5 | -0.313 ± 0.110 | 2.190 ± 0.092 |
| c3-MoLFormer / matched-pooled | quant-binary / OOD-17 | 5 | -0.266 ± 0.161 | 1.847 ± 0.117 |
| c3-MoLFormer / matched-pooled | quant-binary / Q-HERO-405 | 5 | +0.004 ± 0.045 | 1.711 ± 0.039 |
| c3-MoLFormer / matched-pooled | quant-binary / QAC-104 | 5 | -0.140 ± 0.017 | 2.043 ± 0.015 |
| c3-MoLFormer / matched-pooled | quant-binary-shuffled / OOD-17 | 5 | -0.445 ± 0.184 | 1.973 ± 0.122 |
| c3-MoLFormer / matched-pooled | quant-binary-shuffled / Q-HERO-405 | 5 | -0.053 ± 0.080 | 1.759 ± 0.066 |
| c3-MoLFormer / matched-pooled | quant-binary-shuffled / QAC-104 | 5 | -0.263 ± 0.114 | 2.148 ± 0.098 |
| c3-MoLFormer / matched-pooled | quant-continuous / OOD-17 | 5 | -0.096 ± 0.182 | 1.716 ± 0.140 |
| c3-MoLFormer / matched-pooled | quant-continuous / Q-HERO-405 | 5 | +0.145 ± 0.052 | 1.585 ± 0.048 |
| c3-MoLFormer / matched-pooled | quant-continuous / QAC-104 | 5 | -0.077 ± 0.072 | 1.985 ± 0.067 |
| c3-MoLFormer / matched-pooled | quant-shuffled / OOD-17 | 5 | -0.140 ± 0.307 | 1.744 ± 0.225 |
| c3-MoLFormer / matched-pooled | quant-shuffled / Q-HERO-405 | 5 | -0.062 ± 0.080 | 1.767 ± 0.067 |
| c3-MoLFormer / matched-pooled | quant-shuffled / QAC-104 | 5 | -0.159 ± 0.112 | 2.058 ± 0.101 |
| c3-MoLFormer / matched-pooled | untrained / OOD-17 | 5 | -0.153 ± 0.092 | 1.764 ± 0.071 |
| c3-MoLFormer / matched-pooled | untrained / Q-HERO-405 | 5 | +0.009 ± 0.058 | 1.706 ± 0.050 |
| c3-MoLFormer / matched-pooled | untrained / QAC-104 | 5 | -0.191 ± 0.089 | 2.087 ± 0.077 |
| ChemBERTa-100M / baseline | raw-chemberta100m / OOD-17 | 1 | -0.056 ± nan | 1.690 ± nan |
| ChemBERTa-100M / baseline | raw-chemberta100m / Q-HERO-405 | 1 | -0.127 ± nan | 1.821 ± nan |
| ChemBERTa-100M / baseline | raw-chemberta100m / QAC-104 | 1 | -0.011 ± nan | 1.923 ± nan |
| ChemBERTa-100M / matched-pooled | expert / OOD-17 | 5 | -0.122 ± 0.093 | 1.740 ± 0.072 |
| ChemBERTa-100M / matched-pooled | expert / Q-HERO-405 | 5 | -0.157 ± 0.054 | 1.844 ± 0.043 |
| ChemBERTa-100M / matched-pooled | expert / QAC-104 | 5 | -0.218 ± 0.121 | 2.109 ± 0.105 |
| ChemBERTa-100M / matched-pooled | expert-shuffled / OOD-17 | 5 | -0.108 ± 0.220 | 1.723 ± 0.176 |
| ChemBERTa-100M / matched-pooled | expert-shuffled / Q-HERO-405 | 5 | -0.139 ± 0.062 | 1.830 ± 0.051 |
| ChemBERTa-100M / matched-pooled | expert-shuffled / QAC-104 | 5 | -0.123 ± 0.200 | 2.021 ± 0.185 |
| ChemBERTa-100M / matched-pooled | quant-binary / OOD-17 | 5 | +0.003 ± 0.131 | 1.639 ± 0.112 |
| ChemBERTa-100M / matched-pooled | quant-binary / Q-HERO-405 | 5 | -0.141 ± 0.025 | 1.832 ± 0.020 |
| ChemBERTa-100M / matched-pooled | quant-binary / QAC-104 | 5 | -0.365 ± 0.135 | 2.233 ± 0.112 |
| ChemBERTa-100M / matched-pooled | quant-binary-shuffled / OOD-17 | 5 | -0.291 ± 0.445 | 1.849 ± 0.302 |
| ChemBERTa-100M / matched-pooled | quant-binary-shuffled / Q-HERO-405 | 5 | -0.112 ± 0.023 | 1.808 ± 0.018 |
| ChemBERTa-100M / matched-pooled | quant-binary-shuffled / QAC-104 | 5 | -0.133 ± 0.158 | 2.032 ± 0.139 |
| ChemBERTa-100M / matched-pooled | quant-continuous / OOD-17 | 5 | +0.043 ± 0.138 | 1.605 ± 0.114 |
| ChemBERTa-100M / matched-pooled | quant-continuous / Q-HERO-405 | 5 | -0.163 ± 0.065 | 1.848 ± 0.053 |
| ChemBERTa-100M / matched-pooled | quant-continuous / QAC-104 | 5 | -0.091 ± 0.113 | 1.996 ± 0.103 |
| ChemBERTa-100M / matched-pooled | quant-shuffled / OOD-17 | 5 | -0.065 ± 0.150 | 1.693 ± 0.118 |
| ChemBERTa-100M / matched-pooled | quant-shuffled / Q-HERO-405 | 5 | -0.123 ± 0.069 | 1.816 ± 0.057 |
| ChemBERTa-100M / matched-pooled | quant-shuffled / QAC-104 | 5 | -0.079 ± 0.127 | 1.984 ± 0.118 |
| ChemBERTa-100M / matched-pooled | untrained / OOD-17 | 5 | -0.304 ± 0.373 | 1.863 ± 0.260 |
| ChemBERTa-100M / matched-pooled | untrained / Q-HERO-405 | 5 | -0.115 ± 0.051 | 1.810 ± 0.042 |
| ChemBERTa-100M / matched-pooled | untrained / QAC-104 | 5 | -0.015 ± 0.068 | 1.927 ± 0.065 |
| ChemFM-1B / baseline | raw-chemfm1b / OOD-17 | 1 | -0.050 ± nan | 1.685 ± nan |
| ChemFM-1B / baseline | raw-chemfm1b / Q-HERO-405 | 1 | +0.039 ± nan | 1.681 ± nan |
| ChemFM-1B / baseline | raw-chemfm1b / QAC-104 | 1 | -0.058 ± nan | 1.968 ± nan |
| ChemFM-1B / matched-pooled | expert / OOD-17 | 5 | +0.040 ± 0.104 | 1.609 ± 0.085 |
| ChemFM-1B / matched-pooled | expert / Q-HERO-405 | 5 | -0.084 ± 0.081 | 1.784 ± 0.066 |
| ChemFM-1B / matched-pooled | expert / QAC-104 | 5 | -0.045 ± 0.079 | 1.954 ± 0.074 |
| ChemFM-1B / matched-pooled | expert-shuffled / OOD-17 | 5 | -0.044 ± 0.120 | 1.678 ± 0.095 |
| ChemFM-1B / matched-pooled | expert-shuffled / Q-HERO-405 | 5 | -0.111 ± 0.021 | 1.808 ± 0.017 |
| ChemFM-1B / matched-pooled | expert-shuffled / QAC-104 | 5 | -0.168 ± 0.111 | 2.065 ± 0.098 |
| ChemFM-1B / matched-pooled | quant-binary / OOD-17 | 5 | -0.043 ± 0.164 | 1.675 ± 0.131 |
| ChemFM-1B / matched-pooled | quant-binary / Q-HERO-405 | 5 | -0.070 ± 0.072 | 1.773 ± 0.059 |
| ChemFM-1B / matched-pooled | quant-binary / QAC-104 | 5 | -0.018 ± 0.039 | 1.930 ± 0.037 |
| ChemFM-1B / matched-pooled | quant-binary-shuffled / OOD-17 | 5 | -0.109 ± 0.181 | 1.727 ± 0.139 |
| ChemFM-1B / matched-pooled | quant-binary-shuffled / Q-HERO-405 | 5 | -0.120 ± 0.024 | 1.814 ± 0.019 |
| ChemFM-1B / matched-pooled | quant-binary-shuffled / QAC-104 | 5 | -0.155 ± 0.099 | 2.054 ± 0.088 |
| ChemFM-1B / matched-pooled | quant-continuous / OOD-17 | 5 | -0.073 ± 0.215 | 1.697 ± 0.169 |
| ChemFM-1B / matched-pooled | quant-continuous / Q-HERO-405 | 5 | -0.010 ± 0.059 | 1.722 ± 0.050 |
| ChemFM-1B / matched-pooled | quant-continuous / QAC-104 | 5 | -0.226 ± 0.114 | 2.116 ± 0.098 |
| ChemFM-1B / matched-pooled | quant-shuffled / OOD-17 | 5 | -0.261 ± 0.366 | 1.833 ± 0.249 |
| ChemFM-1B / matched-pooled | quant-shuffled / Q-HERO-405 | 5 | -0.138 ± 0.066 | 1.828 ± 0.052 |
| ChemFM-1B / matched-pooled | quant-shuffled / QAC-104 | 5 | -0.248 ± 0.166 | 2.133 ± 0.146 |
| ChemFM-1B / matched-pooled | untrained / OOD-17 | 5 | -0.191 ± 0.221 | 1.788 ± 0.163 |
| ChemFM-1B / matched-pooled | untrained / Q-HERO-405 | 5 | -0.037 ± 0.025 | 1.746 ± 0.021 |
| ChemFM-1B / matched-pooled | untrained / QAC-104 | 5 | -0.083 ± 0.104 | 1.989 ± 0.097 |
| MolFormer-XL / baseline | raw-molformer / OOD-17 | 1 | -0.067 ± nan | 1.698 ± nan |
| MolFormer-XL / baseline | raw-molformer / Q-HERO-405 | 1 | +0.128 ± nan | 1.602 ± nan |
| MolFormer-XL / baseline | raw-molformer / QAC-104 | 1 | -0.176 ± nan | 2.074 ± nan |
| MolFormer-XL / context | expert / OOD-17 | 5 | -0.935 ± 0.742 | 2.257 ± 0.416 |
| MolFormer-XL / context | expert / Q-HERO-405 | 5 | -0.085 ± 0.090 | 1.785 ± 0.075 |
| MolFormer-XL / context | expert / QAC-104 | 5 | -0.197 ± 0.082 | 2.092 ± 0.073 |
| MolFormer-XL / context | expert-shuffled / OOD-17 | 5 | -0.609 ± 0.314 | 2.078 ± 0.201 |
| MolFormer-XL / context | expert-shuffled / Q-HERO-405 | 5 | -0.055 ± 0.048 | 1.761 ± 0.040 |
| MolFormer-XL / context | expert-shuffled / QAC-104 | 5 | -0.257 ± 0.157 | 2.141 ± 0.137 |
| MolFormer-XL / context | quant-pooled / OOD-17 | 5 | -0.529 ± 0.210 | 2.029 ± 0.140 |
| MolFormer-XL / context | quant-pooled / Q-HERO-405 | 5 | +0.209 ± 0.049 | 1.525 ± 0.048 |
| MolFormer-XL / context | quant-pooled / QAC-104 | 5 | -0.186 ± 0.037 | 2.083 ± 0.033 |
| MolFormer-XL / context | quant-pooled-shuffled / OOD-17 | 5 | -0.416 ± 0.297 | 1.947 ± 0.215 |
| MolFormer-XL / context | quant-pooled-shuffled / Q-HERO-405 | 5 | +0.018 ± 0.050 | 1.699 ± 0.043 |
| MolFormer-XL / context | quant-pooled-shuffled / QAC-104 | 5 | -0.184 ± 0.065 | 2.081 ± 0.057 |
| MolFormer-XL / context | quant-sa / OOD-17 | 5 | -0.559 ± 0.255 | 2.047 ± 0.168 |
| MolFormer-XL / context | quant-sa / Q-HERO-405 | 5 | +0.110 ± 0.017 | 1.617 ± 0.016 |
| MolFormer-XL / context | quant-sa / QAC-104 | 5 | -0.177 ± 0.067 | 2.075 ± 0.059 |
| MolFormer-XL / context | quant-sa-shuffled / OOD-17 | 5 | -0.246 ± 0.352 | 1.818 ± 0.276 |
| MolFormer-XL / context | quant-sa-shuffled / Q-HERO-405 | 5 | +0.051 ± 0.079 | 1.670 ± 0.069 |
| MolFormer-XL / context | quant-sa-shuffled / QAC-104 | 5 | -0.361 ± 0.145 | 2.229 ± 0.117 |
| MolFormer-XL / context | untrained / OOD-17 | 5 | -0.330 ± 0.223 | 1.891 ± 0.161 |
| MolFormer-XL / context | untrained / Q-HERO-405 | 5 | +0.043 ± 0.037 | 1.677 ± 0.032 |
| MolFormer-XL / context | untrained / QAC-104 | 5 | -0.118 ± 0.059 | 2.022 ± 0.053 |
| MolFormer-XL / matched-pooled | expert / OOD-17 | 5 | -0.259 ± 0.286 | 1.836 ± 0.203 |
| MolFormer-XL / matched-pooled | expert / Q-HERO-405 | 5 | +0.122 ± 0.035 | 1.607 ± 0.032 |
| MolFormer-XL / matched-pooled | expert / QAC-104 | 5 | -0.331 ± 0.045 | 2.207 ± 0.037 |
| MolFormer-XL / matched-pooled | expert-shuffled / OOD-17 | 5 | -0.368 ± 0.264 | 1.916 ± 0.182 |
| MolFormer-XL / matched-pooled | expert-shuffled / Q-HERO-405 | 5 | -0.080 ± 0.129 | 1.780 ± 0.105 |
| MolFormer-XL / matched-pooled | expert-shuffled / QAC-104 | 5 | -0.314 ± 0.058 | 2.192 ± 0.049 |
| MolFormer-XL / matched-pooled | quant-binary / OOD-17 | 5 | -0.388 ± 0.293 | 1.927 ± 0.214 |
| MolFormer-XL / matched-pooled | quant-binary / Q-HERO-405 | 5 | +0.079 ± 0.046 | 1.646 ± 0.041 |
| MolFormer-XL / matched-pooled | quant-binary / QAC-104 | 5 | -0.167 ± 0.121 | 2.064 ± 0.108 |
| MolFormer-XL / matched-pooled | quant-binary-shuffled / OOD-17 | 5 | -0.540 ± 0.478 | 2.019 ± 0.329 |
| MolFormer-XL / matched-pooled | quant-binary-shuffled / Q-HERO-405 | 5 | -0.037 ± 0.071 | 1.746 ± 0.060 |
| MolFormer-XL / matched-pooled | quant-binary-shuffled / QAC-104 | 5 | -0.170 ± 0.127 | 2.066 ± 0.114 |
| MolFormer-XL / matched-pooled | quant-continuous / OOD-17 | 5 | -0.469 ± 0.259 | 1.986 ± 0.177 |
| MolFormer-XL / matched-pooled | quant-continuous / Q-HERO-405 | 5 | +0.237 ± 0.052 | 1.497 ± 0.052 |
| MolFormer-XL / matched-pooled | quant-continuous / QAC-104 | 5 | -0.129 ± 0.052 | 2.033 ± 0.047 |
| MolFormer-XL / matched-pooled | quant-shuffled / OOD-17 | 5 | -0.356 ± 0.235 | 1.909 ± 0.165 |
| MolFormer-XL / matched-pooled | quant-shuffled / Q-HERO-405 | 5 | +0.124 ± 0.054 | 1.605 ± 0.050 |
| MolFormer-XL / matched-pooled | quant-shuffled / QAC-104 | 5 | -0.170 ± 0.110 | 2.068 ± 0.095 |
| MolFormer-XL / matched-pooled | untrained / OOD-17 | 5 | -0.231 ± 0.169 | 1.821 ± 0.122 |
| MolFormer-XL / matched-pooled | untrained / Q-HERO-405 | 5 | +0.055 ± 0.086 | 1.666 ± 0.074 |
| MolFormer-XL / matched-pooled | untrained / QAC-104 | 5 | -0.087 ± 0.051 | 1.994 ± 0.047 |

Table S7. Complete CatBoost extension results, including all secondary targets and negative controls. Raw-backbone values come from one fixed decoder run. Seed standard deviations are descriptive. Older partial-fine-tuning and new frozen-feature results use different cohorts and are not one leaderboard.

S13. Nested uncertainty and scaffold influence

| Backbone / panel | Comparison | Bootstrap unit | ΔRMSE | 95% interval |
| --- | --- | --- | --- | --- |
| c3-MoLFormer / matched-pooled | expert minus expert-shuffled | scaffold | -0.113 | [-0.218, -0.052] |
| c3-MoLFormer / matched-pooled | expert minus expert-shuffled | seed+scaffold | -0.113 | [-0.246, -0.012] |
| c3-MoLFormer / matched-pooled | expert minus quant-continuous | scaffold | +0.120 | [-0.007, +0.216] |
| c3-MoLFormer / matched-pooled | expert minus quant-continuous | seed+scaffold | +0.120 | [-0.010, +0.228] |
| c3-MoLFormer / matched-pooled | expert minus quant-binary | scaffold | -0.005 | [-0.107, +0.169] |
| c3-MoLFormer / matched-pooled | expert minus quant-binary | seed+scaffold | -0.005 | [-0.115, +0.172] |
| c3-MoLFormer / matched-pooled | expert minus untrained | scaffold | -0.001 | [-0.063, +0.086] |
| c3-MoLFormer / matched-pooled | expert minus untrained | seed+scaffold | -0.001 | [-0.084, +0.093] |
| c3-MoLFormer / matched-pooled | expert minus raw-c3-molformer | scaffold | +0.057 | [-0.011, +0.159] |
| c3-MoLFormer / matched-pooled | expert minus raw-c3-molformer | seed+scaffold | +0.057 | [-0.024, +0.162] |
| c3-MoLFormer / matched-pooled | quant-continuous minus quant-shuffled | scaffold | -0.182 | [-0.285, -0.041] |
| c3-MoLFormer / matched-pooled | quant-continuous minus quant-shuffled | seed+scaffold | -0.182 | [-0.299, -0.029] |
| c3-MoLFormer / matched-pooled | quant-binary minus quant-binary-shuffled | scaffold | -0.049 | [-0.276, +0.046] |
| c3-MoLFormer / matched-pooled | quant-binary minus quant-binary-shuffled | seed+scaffold | -0.049 | [-0.275, +0.065] |
| c3-MoLFormer / matched-pooled | quant-binary-shuffled minus expert-shuffled | scaffold | -0.059 | [-0.096, -0.011] |
| c3-MoLFormer / matched-pooled | quant-binary-shuffled minus expert-shuffled | seed+scaffold | -0.059 | [-0.164, +0.058] |
| c3-MoLFormer / matched-pooled | quant-continuous minus raw-c3-molformer | scaffold | -0.063 | [-0.127, +0.039] |
| c3-MoLFormer / matched-pooled | quant-continuous minus raw-c3-molformer | seed+scaffold | -0.063 | [-0.140, +0.052] |
| ChemBERTa-100M / matched-pooled | expert minus expert-shuffled | scaffold | +0.014 | [-0.107, +0.079] |
| ChemBERTa-100M / matched-pooled | expert minus expert-shuffled | seed+scaffold | +0.014 | [-0.115, +0.098] |
| ChemBERTa-100M / matched-pooled | expert minus quant-continuous | scaffold | -0.004 | [-0.122, +0.077] |
| ChemBERTa-100M / matched-pooled | expert minus quant-continuous | seed+scaffold | -0.004 | [-0.138, +0.122] |
| ChemBERTa-100M / matched-pooled | expert minus quant-binary | scaffold | +0.013 | [-0.111, +0.081] |
| ChemBERTa-100M / matched-pooled | expert minus quant-binary | seed+scaffold | +0.013 | [-0.119, +0.108] |
| ChemBERTa-100M / matched-pooled | expert minus untrained | scaffold | +0.034 | [-0.043, +0.082] |
| ChemBERTa-100M / matched-pooled | expert minus untrained | seed+scaffold | +0.034 | [-0.058, +0.113] |
| ChemBERTa-100M / matched-pooled | expert minus raw-chemberta100m | scaffold | +0.024 | [-0.055, +0.086] |
| ChemBERTa-100M / matched-pooled | expert minus raw-chemberta100m | seed+scaffold | +0.024 | [-0.068, +0.096] |
| ChemBERTa-100M / matched-pooled | quant-continuous minus quant-shuffled | scaffold | +0.032 | [-0.028, +0.098] |
| ChemBERTa-100M / matched-pooled | quant-continuous minus quant-shuffled | seed+scaffold | +0.032 | [-0.077, +0.140] |
| ChemBERTa-100M / matched-pooled | quant-binary minus quant-binary-shuffled | scaffold | +0.024 | [-0.054, +0.087] |
| ChemBERTa-100M / matched-pooled | quant-binary minus quant-binary-shuffled | seed+scaffold | +0.024 | [-0.068, +0.108] |
| ChemBERTa-100M / matched-pooled | quant-binary-shuffled minus expert-shuffled | scaffold | -0.022 | [-0.060, +0.013] |
| ChemBERTa-100M / matched-pooled | quant-binary-shuffled minus expert-shuffled | seed+scaffold | -0.022 | [-0.091, +0.049] |
| ChemBERTa-100M / matched-pooled | quant-continuous minus raw-chemberta100m | scaffold | +0.028 | [-0.067, +0.167] |
| ChemBERTa-100M / matched-pooled | quant-continuous minus raw-chemberta100m | seed+scaffold | +0.028 | [-0.090, +0.175] |
| ChemFM-1B / matched-pooled | expert minus expert-shuffled | scaffold | -0.022 | [-0.152, +0.054] |
| ChemFM-1B / matched-pooled | expert minus expert-shuffled | seed+scaffold | -0.022 | [-0.183, +0.074] |
| ChemFM-1B / matched-pooled | expert minus quant-continuous | scaffold | +0.062 | [-0.071, +0.128] |
| ChemFM-1B / matched-pooled | expert minus quant-continuous | seed+scaffold | +0.062 | [-0.091, +0.163] |
| ChemFM-1B / matched-pooled | expert minus quant-binary | scaffold | +0.011 | [-0.111, +0.098] |
| ChemFM-1B / matched-pooled | expert minus quant-binary | seed+scaffold | +0.011 | [-0.138, +0.131] |
| ChemFM-1B / matched-pooled | expert minus untrained | scaffold | +0.039 | [-0.050, +0.093] |
| ChemFM-1B / matched-pooled | expert minus untrained | seed+scaffold | +0.039 | [-0.073, +0.135] |
| ChemFM-1B / matched-pooled | expert minus raw-chemfm1b | scaffold | +0.104 | [-0.002, +0.179] |
| ChemFM-1B / matched-pooled | expert minus raw-chemfm1b | seed+scaffold | +0.104 | [-0.017, +0.202] |
| ChemFM-1B / matched-pooled | quant-continuous minus quant-shuffled | scaffold | -0.106 | [-0.149, -0.046] |
| ChemFM-1B / matched-pooled | quant-continuous minus quant-shuffled | seed+scaffold | -0.106 | [-0.176, -0.021] |
| ChemFM-1B / matched-pooled | quant-binary minus quant-binary-shuffled | scaffold | -0.041 | [-0.117, +0.048] |
| ChemFM-1B / matched-pooled | quant-binary minus quant-binary-shuffled | seed+scaffold | -0.041 | [-0.139, +0.065] |
| ChemFM-1B / matched-pooled | quant-binary-shuffled minus expert-shuffled | scaffold | +0.007 | [-0.057, +0.062] |
| ChemFM-1B / matched-pooled | quant-binary-shuffled minus expert-shuffled | seed+scaffold | +0.007 | [-0.099, +0.095] |
| ChemFM-1B / matched-pooled | quant-continuous minus raw-chemfm1b | scaffold | +0.042 | [-0.039, +0.133] |
| ChemFM-1B / matched-pooled | quant-continuous minus raw-chemfm1b | seed+scaffold | +0.042 | [-0.049, +0.151] |
| MolFormer-XL / context | expert minus expert-shuffled | scaffold | +0.025 | [-0.139, +0.311] |
| MolFormer-XL / context | expert minus expert-shuffled | seed+scaffold | +0.025 | [-0.150, +0.347] |
| MolFormer-XL / context | expert minus quant-pooled | scaffold | +0.261 | [+0.084, +0.511] |
| MolFormer-XL / context | expert minus quant-pooled | seed+scaffold | +0.261 | [+0.067, +0.537] |
| MolFormer-XL / context | expert minus quant-sa | scaffold | +0.169 | [-0.004, +0.454] |
| MolFormer-XL / context | expert minus quant-sa | seed+scaffold | +0.169 | [-0.015, +0.471] |
| MolFormer-XL / context | quant-pooled minus quant-sa | scaffold | -0.092 | [-0.142, -0.026] |
| MolFormer-XL / context | quant-pooled minus quant-sa | seed+scaffold | -0.092 | [-0.159, -0.001] |
| MolFormer-XL / context | quant-pooled minus quant-pooled-shuffled | scaffold | -0.174 | [-0.259, -0.061] |
| MolFormer-XL / context | quant-pooled minus quant-pooled-shuffled | seed+scaffold | -0.174 | [-0.282, -0.040] |
| MolFormer-XL / context | quant-sa minus quant-sa-shuffled | scaffold | -0.053 | [-0.172, +0.056] |
| MolFormer-XL / context | quant-sa minus quant-sa-shuffled | seed+scaffold | -0.053 | [-0.187, +0.075] |
| MolFormer-XL / context | expert minus raw-molformer | scaffold | +0.185 | [+0.056, +0.380] |
| MolFormer-XL / context | expert minus raw-molformer | seed+scaffold | +0.185 | [+0.050, +0.404] |
| MolFormer-XL / context | quant-pooled minus raw-molformer | scaffold | -0.076 | [-0.178, +0.047] |
| MolFormer-XL / context | quant-pooled minus raw-molformer | seed+scaffold | -0.076 | [-0.186, +0.057] |
| MolFormer-XL / matched-pooled | expert minus expert-shuffled | scaffold | -0.175 | [-0.258, -0.058] |
| MolFormer-XL / matched-pooled | expert minus expert-shuffled | seed+scaffold | -0.175 | [-0.322, -0.024] |
| MolFormer-XL / matched-pooled | expert minus quant-continuous | scaffold | +0.109 | [+0.007, +0.210] |
| MolFormer-XL / matched-pooled | expert minus quant-continuous | seed+scaffold | +0.109 | [-0.001, +0.226] |
| MolFormer-XL / matched-pooled | expert minus quant-binary | scaffold | -0.039 | [-0.139, +0.136] |
| MolFormer-XL / matched-pooled | expert minus quant-binary | seed+scaffold | -0.039 | [-0.149, +0.148] |
| MolFormer-XL / matched-pooled | expert minus untrained | scaffold | -0.060 | [-0.138, +0.037] |
| MolFormer-XL / matched-pooled | expert minus untrained | seed+scaffold | -0.060 | [-0.187, +0.057] |
| MolFormer-XL / matched-pooled | expert minus raw-molformer | scaffold | +0.005 | [-0.092, +0.109] |
| MolFormer-XL / matched-pooled | expert minus raw-molformer | seed+scaffold | +0.005 | [-0.102, +0.115] |
| MolFormer-XL / matched-pooled | quant-continuous minus quant-shuffled | scaffold | -0.107 | [-0.201, -0.042] |
| MolFormer-XL / matched-pooled | quant-continuous minus quant-shuffled | seed+scaffold | -0.107 | [-0.228, -0.016] |
| MolFormer-XL / matched-pooled | quant-binary minus quant-binary-shuffled | scaffold | -0.100 | [-0.290, -0.003] |
| MolFormer-XL / matched-pooled | quant-binary minus quant-binary-shuffled | seed+scaffold | -0.100 | [-0.314, +0.033] |
| MolFormer-XL / matched-pooled | quant-binary-shuffled minus expert-shuffled | scaffold | -0.036 | [-0.086, +0.051] |
| MolFormer-XL / matched-pooled | quant-binary-shuffled minus expert-shuffled | seed+scaffold | -0.036 | [-0.148, +0.112] |
| MolFormer-XL / matched-pooled | quant-continuous minus raw-molformer | scaffold | -0.104 | [-0.196, -0.012] |
| MolFormer-XL / matched-pooled | quant-continuous minus raw-molformer | seed+scaffold | -0.104 | [-0.208, -0.003] |
| MolFormer-XL / matched-sa | expert minus expert-shuffled | scaffold | +0.025 | [-0.139, +0.311] |
| MolFormer-XL / matched-sa | expert minus expert-shuffled | seed+scaffold | +0.025 | [-0.150, +0.347] |
| MolFormer-XL / matched-sa | expert minus quant-continuous | scaffold | +0.169 | [-0.004, +0.454] |
| MolFormer-XL / matched-sa | expert minus quant-continuous | seed+scaffold | +0.169 | [-0.015, +0.471] |
| MolFormer-XL / matched-sa | expert minus quant-binary | scaffold | +0.056 | [-0.126, +0.346] |
| MolFormer-XL / matched-sa | expert minus quant-binary | seed+scaffold | +0.056 | [-0.143, +0.368] |
| MolFormer-XL / matched-sa | expert minus untrained | scaffold | +0.109 | [-0.051, +0.354] |
| MolFormer-XL / matched-sa | expert minus untrained | seed+scaffold | +0.109 | [-0.067, +0.392] |
| MolFormer-XL / matched-sa | expert minus raw-molformer | scaffold | +0.185 | [+0.056, +0.380] |
| MolFormer-XL / matched-sa | expert minus raw-molformer | seed+scaffold | +0.185 | [+0.050, +0.404] |
| MolFormer-XL / matched-sa | quant-continuous minus quant-shuffled | scaffold | -0.053 | [-0.172, +0.056] |
| MolFormer-XL / matched-sa | quant-continuous minus quant-shuffled | seed+scaffold | -0.053 | [-0.187, +0.075] |
| MolFormer-XL / matched-sa | quant-continuous minus raw-molformer | scaffold | +0.016 | [-0.126, +0.144] |
| MolFormer-XL / matched-sa | quant-continuous minus raw-molformer | seed+scaffold | +0.016 | [-0.127, +0.146] |

Table S8. All Q-HERO extension contrasts with conditional-scaffold and nested seed/scaffold intervals. No multiplicity adjustment or post-hoc equivalence margin. Other targets and leave-one-scaffold-out loss ranges are supplied in analysis/contrasts.csv. Nested resampling of five seeds has limited precision and is a sensitivity analysis, not evidence from five independent datasets.

S14. Cross-environment checks and descriptive visual comparisons

All 486 v9 metric rows and paired scaffold-bootstrap intervals were independently recalculated on the second supplied server. A training reproduction on the first server gives small Q-HERO differences across PyTorch/scikit-learn versions; individual seed outputs are not bitwise reproducible. All original results remain authoritative, with server comparisons archived separately.

Q-HERO row-level strain/protocol provenance is absent from the provided worksheet. Public programme-level descriptions support coordinated collection, without certifying identical assay conditions for every historical compound. Same-molecule context sensitivity changes organism mixture, censoring policy, record count and numerical aggregation together. Human denoising and laboratory-bias removal are not identified. Checkpoint metadata, feature hashes, target-fold assignments, paired initialisation hashes, source-identity hashes and complete prediction files accompany the extension.

Figure S15. Chemical-space illustration from frozen MolFormer features, with per-molecule L2 normalisation and PCA fitted on source-training molecules. Joint t-SNE uses held-out structures solely for illustration; proximity does not establish transferability or causal mechanisms. Source validation reserves 15% of scaffold groups rather than 15% of molecules: in the pooled panel, 377 molecules are in training and 304 in validation.


Figure S16. (a) Measured external MIC distributions by the predicted Good/Bad class of one archived direct expert checkpoint, threshold logit=0 fixed without target labels; Q-HERO-405 subset, descriptive and conditional on seed 0. These are model-predicted classes, not human annotations of external compounds. (b) Three-seed direct rank agreement from the original Q-HERO-411 cohort, with mean and seed standard deviation. No downstream target refitting in either panel; cohorts differ, and raw direct MIC calibration remains unvalidated.


S15. Historical contrastive, in-domain and geometric analyses

These historical branches are supplementary descriptive material. They use a contrastive architecture distinct from the matched 256→128 encoder, and some source exclusions or generating scripts are incomplete. They are not used to identify the main supervision-intervention effects. Citation numbers in Sections S15–S16 follow the supplementary reference list in S17.


Figure S17. Historical expert-guidance diagram. This branch is distinct from the matched source-label interventions in the main article.

S15.1. Historical contrastive encoder


The expert-guidance dataset contains 1,103 final Good/Bad annotations. Repository artifacts retain the final label but not the individual annotator votes or adjudication records. The historical description of three independent experts and majority resolution therefore cannot be independently verified from the archived files, and inter-rater agreement cannot be calculated. We analyse the final labels as the available supervision signal. The class balance is 859 Bad and 244 Good; annotation-round drift and SMILES quality-control limitations are reported in the Supporting Information.

For exploratory model selection, we benchmarked MolFormer, ChemBERTa, Morgan, and MACCS representations under a five-fold stratified protocol. MolFormer produced the highest archived mean F1-score (0.655 with an MLP and StandardScaler) and accuracy (0.856). Because the expert-label set is imbalanced, accuracy alone is not interpreted as a performance claim; these internal model-selection diagnostics are separate from external validation.

Building on the MolFormer baseline, we trained a dedicated MLP-based encoder (512 → 384 → 256 neurons) with a supervised contrastive objective to distill the implicit “chemical intuition” embedded in the expert labels into a compact, task-specific latent space. To address the inherent class imbalance of the expert-annotated dataset, we employed Borderline SMOTE (sampling strategy = 0.8) during encoder training. The model was optimized with a hard-negative contrastive loss, which explicitly pushes hard misclassified negatives away from the anchor embedding, thereby sharpening inter-class boundaries. The resulting 256-dimensional representations are referred to as human embeddings hereafter.

Figure S18 presents t-SNE projections (perplexity = 30) of a held-out fold before and after contrastive refinement. The internal clustering diagnostics changed from silhouette 0.007 to 0.108, Davies–Bouldin 6.54 to 2.58, and Calinski–Harabasz 3.60 to 22.08. These visual and internal diagnostics indicate separation of the final label classes within this analysis; they are not evidence of external antibacterial-prediction performance.


Figure S18. Historical t-SNE class-separation illustration for the contrastive encoder. Class separation does not establish external potency-prediction performance.


S15.2. Audited in-domain comparison

The historical architecture table is not used for comparative inference because its RMSE and R² entries combine different pipelines and split definitions. Table S9 retains the audited molecule-grouped comparison; the new cation-clean supervision interventions are reported separately in Tables S5–S6.

Historical analyses of one-hot and text-encoded task labels are exploratory because the corresponding metrics were generated under incompatible pipelines and splits. They are not evidence for the controlled supervision comparisons reported here.



Table S9 reports the audited molecule-grouped comparison on QAC-105. Under this conservative split, expert, quantitative, and raw MolFormer representations are within seed variation. This in-domain result is descriptive and should be read with the external Q-HERO and partial-fine-tuning analyses.


A natural objection to using expert Good/Bad labels is that a larger body of quantitative data should be preferable when it is available. The original in-domain comparison is retained as a descriptive analysis, but its absolute values are not used as primary evidence: QAC-105 molecules overlap the representation-training collections and the historical table combines outputs from different pipelines and split definitions. The externally held-out and controlled partial-fine-tuning results in Supporting Information Section S4 provide the principal current comparison.

The quantitative corpus used in the historical comparison was assembled from broad QAC activity records. Its record count must not be interpreted as the number of independent molecules: the fine-tuning subset used in Supporting Information Section S4 contains 9,338 MIC records over 1,153 unique molecules. The expert and quantitative collections have substantial molecule-level overlap, which makes their comparison controlled but not independent.

Both embedding types were subsequently evaluated on the same QAC collection. This retrospective in-domain result is consistent with similar downstream behaviour of the two supervision sources, but it is not a clean external validation. The molecule-level overlap and pair-level split can change the information available during evaluation, and raw MolFormer is also competitive under the audited re-run. We therefore do not use this table to claim that human annotations outperform or are statistically equivalent to quantitative measurements.

Similarity in one downstream protocol does not mean that a binary label is informationally equivalent to a quantitative measurement. A final expert call may reflect multiple activity reports and additional considerations, while pooled quantitative records contain repeated molecules and heterogeneous assay contexts. The appropriate conclusion is limited to comparable representation quality under the evaluated refitting protocol.


Table S9. Audited QAC-105 molecule-grouped comparison: CatBoost R², mean ± seed standard deviation over ten seeds. Molecules are held out of the target-regressor training fold; representation-training source overlap remains a limitation. Values are retained from the archived audit.

| Representation | S. aureus MIC | S. aureus MBC | E. coli MIC | E. coli MBC |
| --- | --- | --- | --- | --- |
| Raw MolFormer | 0.19 ± 0.19 | 0.00 ± 0.30 | 0.12 ± 0.19 | 0.08 ± 0.22 |
| Expert (Good/Bad) | 0.27 ± 0.16 | 0.06 ± 0.27 | 0.09 ± 0.19 | 0.06 ± 0.27 |
| Quantitative regression | 0.31 ± 0.13 | 0.08 ± 0.22 | 0.16 ± 0.22 | 0.08 ± 0.26 |


S15.3. Archived representation geometry and attribution

Representational similarity and matched prediction contrasts answer different questions. Archived CKA/probing describes geometry, whereas the new interventions in archived v12 main Sections 3.2–3.3 manipulate supervision within a fixed algorithm. Neither a similarity score nor SHAP attribution identifies molecular antibacterial mechanisms (78).


Figure S19. Historical conceptual information flow in the contrastive encoder. The diagram is not a quantitative causal decomposition.

The archived CKA/probing table reports high alignment between MolFormer and the expert embedding (CKA 0.933 in-domain and 0.946 OOD; linear-probe R² 0.891 from MolFormer to embedding and 0.844 in reverse). Generating code and selected outputs were recovered in notebook snapshots. Exact encoder and execution-state provenance for every historical summary is not fully resolved, and these values have not been independently regenerated. They remain descriptive evidence about geometry, not the causal supervision test.

Geometric similarity does not determine how a downstream model uses each representation. The archived SHAP summary has unresolved provenance: the available decomposition file reports a different aggregate embedding attribution from the manuscript, and it is not confirmed that the same encoder generated all analyses. We therefore omit numerical SHAP attribution as a basis for mechanistic or causal claims. A fully versioned pipeline is required before interpreting feature attributions.

The recovered May causal_final notebook records historical OOD RMSE 2.314/2.189/2.276 for raw/human/regression. Its endpoint-residual bootstrap gives human minus regression mean ΔRMSE −0.086 [−0.227, +0.054], matching analysis/ablation_bootstrap.csv. It samples endpoint residuals rather than molecule or scaffold clusters and is retained as a descriptive historical analysis. The July shap_causal_analysis notebook instead records regression RMSE 2.133 with the same rounded raw and human values. This supplies the saved output behind the original article’s 2.13; the May result cannot be used as an arithmetic correction of it. Neither historical interval establishes equivalence or a chemical causal mechanism.

The descriptive pattern does not identify a robust subgroup advantage for either supervision source in the 17-compound case study. Any finer claim would require an a priori margin, a larger independent set, and a preregistered non-inferiority or equivalence protocol.

The archived analyses describe preservation of pretrained geometry and similar downstream behaviour under some protocols. Their incomplete provenance precludes a quantitative causal decomposition. archived v12 main Sections 3.2–3.3 supplies a stronger test of supervision content through paired interventions, while retaining the distinction between an algorithmic effect and antibacterial causality.

S16. Synthesis, characterisation and microbiological protocols

This section preserves the chemical descriptions and available protocols from the source manuscript. OOD-17 is a small secondary case study. The original text refers to additional NMR/HRMS/IR spectra, an optimisation Table S1 and auxiliary Schemes S1–S2, which are not present as primary spectrum files in the current computational folder. Those chemical supplements must be supplied by the chemistry coauthors; their identifiers below are reserved separately as Table S10 and Schemes S5–S6.

The source manuscript reports synthesis and activity measurements for 17 QACs from the four scaffold families listed below. This collection is structurally held out from the supplied training collections. Final assay conditions, measurement chronology and the independence of experimental assessment are reserved for coauthor completion in C1; the computational analysis treats the set as a small descriptive case study.


Figure S20. Molecular classes in the historical QAC, Q-HERO and OOD collections.

The QAC's architecture follows the principle of core, tail and linker interconnection. While QACs can be classified in variety of ways, the usual approach is division by quantity of charged cores. Within the framework of current study, we sought to utilize three main subclasses of QACs (mono-, bis-, and multi-QACs) for a thorough assessment of predictive potential of the developed ML model.

Heterocycles are among the most well-known and diverse classes of compounds in organic chemistry, forming the basic structural backbones of most modern drugs, including QACs, which often have a heterocyclic nature 54-57. For the purposes of this study, we selected four suitable scaffolds to obtain the target structures: kojic acid, tetrahydropyridine, dihydropyran, and glycoluril derivatives. All 17 novel obtained compounds were subjected to MIC and MBC evaluation via broth microdilution assay. Detailed representation of the synthesis methodologies, microbiological results and compounds description can be found in the experimental section and supplementary materials. The synthetic approaches are described below.

S16.1. Kojic acid-based bis-QACs

Kojic acid (KA) is a multifunctional natural low toxic organic compound used in cosmetics as skin-depigmenting agent 58, 59. KA itself possesses moderate antibacterial activity, but several synthetically derived classes show significantly enhanced potency against a broad spectrum of bacteria 60-65. Here we used the functionalization of KA to obtain bis-QACs architectures in similar fashion to the commercially available antiseptic octenidine with alkylaminopyridine pharmacophore group. First, dimerization of KA with 1,5-dibromopentane afforded the dihydroxy-platform. Chlorination of dimer 1 and subsequent quaternization with 4-(alkylamino)pyridines occurred at the pyridine nitrogen atom led to the target bis-QACs 1-4 (Scheme S1). The required 4-(alkylamino)pyridines were obtained separately in three steps from carboxylic acids as reported previously 66.


Scheme S1. Synthesis of KA-based bis-QACs.


S16.2. Tetrahydropyridine-based bis-QACs

Tetrahydropyridine (THP) scaffold is a versatile nitrogen-containing heterocycle widely used in medicinal chemistry as a bioactive ring system and pharmacophore 67. One of the key features of THP-based drug design is efficient and fast synthesis through multicomponent reactions (MCR) 68. Previously, we found that 1,4,5,6-THP are produced through a MCR between aromatic aldehydes, malononitrile, methyl acetoacetate, and ammonium acetate in methanol at 64 ℃ for 2 h 69. When using 3-pyridinecarboxaldehyde as the aromatic moiety, MCR is a convenient method for creating bis-pyridine platforms which are known precursors of bis-QACs. The followed Menshutkin reaction yielded the second set of bis-QACs 5-9 (Scheme S2).


Scheme S2. Synthesis of THP-based bis-QACs.

However, despite the well-known nature of the method, we encountered several unexpected difficulties during the implementation of the process requiring optimization of the MCR synthesis conditions. First, the desired THP was produced in mixture with 4H-pyran as a result of a competitive process of intramolecular cyclization via the attack of carbonyl on the nitrile group after Michael addition (Scheme S5). The MCR conditions for a 3-pyridinecarboxaldehyde, malononitrile, methyl acetoacetate and ammonium acetate were optimized by varying the solvent, temperature, and the equivalents of ammonium acetate (Table S10). 4H-Pyran was the primary product during the reaction at room temperature, while at 64 ℃ and increased solvent load the quantity of the by-product slightly decreased (Table S10 entry 3). As the amount of NH4OAc increases to 4.0 mol. equiv., the reaction’s sole product is desired THP. Consequently, we attempted to conduct the reaction using ethanol, which is less hazardous to human health and is classified as a green solvent 70. Carrying out a similar reaction in ethanol at 78 ℃ resulted in 62% yield of the desired THP (Table S10 entry 7). Second, the Menshutkin reaction led to the formation of bis-QAC in the form of a pair of diastereoisomers (Scheme S6). In our previous study, we found that 4SR,6RS-THP convert to more stable epimers when heated in DMSO. Thus, we carried out additional epimerization step in order to obtain a more diastereoselectively pure product. The subsequent Menshutkin reaction yielded bis-pyridinium salts in the form of a single diastereomer.

S16.3. Dihydropyran-based mono-QACs

Next, we decided to use the obtained data on the pyran derivatives formation during the MCR to optimize the synthesis of dihydropyrans with trifluoro-substituted groups as a basis for the mono-QACs. The trifluoromethyl group serves as a crucial structural component in numerous fluorinated compounds that possess significant biological and pharmaceutical relevance. As a result, fluorine-containing heterocyclic compounds are now acknowledged as organic molecules exhibiting noteworthy biological activity, with potential utility in both medical and agricultural fields 71, 72. The CF3-dihydropyran was synthesized through a similar MCR involving ethyl 4,4,4-trifluoroacetoacetate as Michael addition component. The method is simple to operate, since the reaction can be carried out at room temperature, and the target product is isolated by simple filtration. N-alkylation of dihydropyran via Menshutkin reaction led to mono-QACs 10-12 (Scheme S3).


Scheme S3. Synthesis of dihydropyrans -based mono-QACs.


S16.4. Glycoluril-based multi-QACs

Finally, a series of glycoluril-based multi-QACs was synthesized through a four-step synthetic route starting from 2-(2-aminoethoxy)ethan-1-ol (AmEtO). Glycoluril (GU) is a rigid bicyclic bis-urea heterocycle that serves as a key industrial and pharmaceutical building block — most notably as the classical precursor of cucurbituril macrocycles and as the core of the clinically used tranquilizer/nootropic drug mebicar (N,N,N′,N′-tetramethylglycoluril) 73. Its compact tetra-nitrogen bicyclic core represents an attractive, still largely unexplored scaffold for constructing multivalent QACs architectures. In addition, functionalized GU derivatives have attracted growing interest as biologically active molecules, highlighting the potential of the GU scaffold for medicinal chemistry 74, 75. Direct alkylation of GU backbone is problematic, so the heterocyclic linker was assembled synthetically from an amino alcohol, dimethyl carbonate, and glyoxal. Initially, a urea intermediate was prepared and subjected to condensation with glyoxal to afford the tetrahydroxyglycoluril scaffold. The obtained tetrahydroxyglycoluril was converted into a tetrachloride, which was reacted with 4-alkylaminopyridines in a final Menshutkin quaternization step to afford the target multi-QACs 13-17 (Scheme S4).


Scheme S4. Synthesis of glycoluril-based multi-QACs.


S16.5. Chemistry

S16.5.1. General information

All starting reagents were obtained from commercial suppliers and were used without further purification. All solvents used were reagent grade and distilled prior to application. Air sensitive reactions were performed under high purity argon atmosphere. Thin-layer chromatography was performed using silica gel 60 F254 aluminum sheets under UV light. IR spectra were recorded with a Bruker ALPHA-T FT-IR spectrometer in KBr pellets. HR-ESI-MS were recorded on a Bruker microTOF II instrument (Bruker Daltonik GmbH, Bremen, Germany); external or internal calibration was performed with electrospray calibrant solution (Fluka). All melting points were measured with a Stuart SMP30 melting point apparatus and are uncorrected. 1H and 13C NMR spectra were recorded with a Bruker AM300 at ambient temperature in Dimethyl sulfoxide-d₆ (DMSO-d6) or Chloroform-d (CDCl3) solutions. The NMR, HRMS and FT-IR spectra of the newly synthesized compounds can be found in the supporting information.

S16.5.2. Synthesis and Characterization of Substrates and Products

Synthesis of 5,5'-(pentane-1,5-diylbis(oxy))bis(2-(hydroxymethyl)-4H-pyran-4-one) A:

To a solution of kojic acid (1.847 g, 13 mmol) in anhydrous DMF (25 mL) was added K2CO3 (1.794 g, 13 mmol). The suspension was stirred at 60 oC for 1 h. 1,5-Dibromopentane (1.356 g, 5.9 mmol) was added and the mixture was stirred at 80 oC for 24 h. Result of reaction was confirmed by TLC (MeOH/CHCl3 1:10). The solvent was removed under reduced pressure. Distilled water (20 mL) was added to the crude residue, and the mixture was stirred at RT for 2 h. Formed precipitates were filtrated through a glass filter, washed with acetone (20 mL), and dried under a vacuum to afford sand yellow solid product X (1.46 g, 4.1 mmol, 70% yield).

C17H20O8; M. w. 352.339; Sand yellow solid; M. p. 143–145°C; 1H NMR (300 MHz, DMSO-d6): δ 8.10 (s, 2H, 2CH), 6.30 (s, 2H, 2CH), 5.69 (br s, 2H, 2OH), 4.30 (s, 4H, 2CH2), 3.83 (t, J = 6.3 Hz, 4H, 2CH2), 1.73 (p, J = 7.0 Hz, 4H, 2CH2), 1.58-1.44 (m, 2H, CH2) ppm; 13C NMR (75 MHz, DMSO-d6): δ 173.1, 167.9, 147.1, 140.1, 110.9, 68.7, 59.3, 28.2, 21.9 ppm; HRMS (ESI): calcd for C17H20O8 375.1050, found 375.1051.

Synthesis of 1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(alkylamino)pyridin-1-ium) dichlorides 1-4:

Compound A (1.33 g, 3.77 mmol) was dissolved in 25 ml of chloroform. The resulting suspension was cooled in an ice bath, and a solution of thionyl chloride (1.094 mL, 15.08 mmol) in 7 mL of CHCl3 was added dropwise under stirring. The reaction mixture was then heated under reflux with stirring for 24 hours. Progress of the reaction was monitored by TLC (MeOH:CHCl3, 1:10). Upon completion, the reaction mixture was concentrated and dried using a rotary evaporator. The residue was resuspended in 5 mL of chloroform and filtered through a Schott filter. After solvent evaporation, brown powder was obtained. The obtained brown powder (0.2 g, 0.5 mmol) and 4-alkylaminopyridine (1.1 mmol) were dissolved in 7 ml of acetonitrile. The resulting mixture was heated under reflux with stirring for 24 hours. Upon completion, the reaction was cooled to room temperature, and the solvent was evaporated under vacuum. The crude residue was washed with acetone (15 ml) and dried under a vacuum to afford light brown solid.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(octylamino)pyridin-1-ium) dichloride (1):

C43H62Cl2N4O6; M. w. 730.989; light brown solid (0.346 g, 0.474 mmol, 94% yield); M. p. 165–168°C; IR (neat/cm−1): 3429, 3212, 2927, 2855, 1652, 1591, 1189; 1H NMR (300 MHz, DMSO-d6): δ 9.32 (t, J = 5.7 Hz, 2H, 2NH), 8.38 (d, J = 7.4 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.09-6.95 (m, 4H, 2CHpy), 6.46 (s, 2H, 2CH), 5.39 (s, 4H, 2CH2), 3.80 (t, J = 6.4 Hz, 4H, 2CH2N+), 3.32-3.24 (m, 4H, 2CH2), 1.78-1.18 (m, 30H, 15CH2), 0.85 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.6, 160.3, 157.0, 147.3, 143.9, 141.5, 140.6, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.1, 28.6, 28.0, 27.8, 26.2, 22.0, 21.9, 13.9 ppm; HRMS (ESI): calcd for C43H62N4O6 365.2329, found 365.2339.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(nonylamino)pyridin-1-ium) dichloride (2):

C45H66Cl2N4O6; M. w. 759.044; light brown solid (0.357 g, 0.47 mmol, 94% yield); M. p. 207–210°C; IR (neat/cm−1): 3432, 3211, 2926, 2855, 1653, 1591, 1190; 1H NMR (300 MHz, DMSO-d6): δ 9.33 (t, J = 5.4 Hz, 2H, 2NH), 8.38 (d, J = 7.3 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.010-6.96 (m, 4H, 2CHpy), 6.47 (s, 2H, 2CH), 5.40 (s, 4H, 2CH2), 3.81 (t, J = 6.3 Hz, 4H, 2CH2N+), 3.33-3.24 (m, 4H, 2CH2), 1.80-1.17 (m, 34H, 17CH2), 0.86 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.5, 160.3, 157.0, 147.2, 143.9, 141.4, 140.6, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.2, 28.8, 28.6, 28.5, 28.0, 27.8, 26.2, 22.0, 21.9, 13.8 ppm; HRMS (ESI): calcd for C45H66N4O6 379.2486, found 379.2493.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(decylamino)pyridin-1-ium) dichloride (3):

C47H70Cl2N4O6; M. w. 787.098; light brown solid (0.342 g, 0.434 mmol, 87% yield); M. p. 169–172°C; IR (neat/cm−1): 3432, 3210, 2926, 2854, 1653, 1591, 1190; 1H NMR (300 MHz, DMSO-d6): δ 9.25 (t, J = 5.6 Hz, 2H, 2NH), 8.37 (d, J = 7.2 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.08-6.96 (m, 4H, 2CHpy), 6.46 (s, 2H, 2CH), 5.39 (s, 4H, 2CH2), 3.81 (t, J = 6.3 Hz, 4H, 2CH2N+), 3.32-3.24 (m, 4H, 2CH2), 1.80-1.17 (m, 38H, 19CH2), 0.85 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.5, 160.3, 157.0, 147.2, 143.9, 141.4, 140.6, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.2, 28.93, 28.91, 28.6, 28.0, 27.8, 26.2, 22.0, 21.9, 13.9 ppm; HRMS (ESI): calcd for C47H70N4O6 393.2642, found 393.2633.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(dodecylamino)pyridin-1-ium) dichloride (4):

C51H78Cl2N4O6; M. w. 843.206; light brown solid (0.375 g, 0.445 mmol, 89% yield); M. p. 215–217°C; IR (neat/cm−1): 3429, 3211, 2925, 2853, 1654, 1591, 1191; 1H NMR (300 MHz, DMSO-d6): δ 9.32 (t, J = 5.7 Hz, 2H, 2NH), 8.38 (d, J = 7.4 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.10-6.95 (m, 4H, 2CHpy), 6.46 (s, 2H, 2CH), 5.40 (s, 4H, 2CH2), 3.81 (t, J = 6.2 Hz, 4H, 2CH2N+), 3.34-3.22 (m, 4H, 2CH2), 1.79-1.16 (m, 46H, 23CH2), 0.85 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.5, 160.3, 157.0, 147.2, 143.9, 141.4, 140.5, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.2, 29.0, 28.9, 28.6, 28.0, 27.8, 26.2, 22.0, 21.9, 13.9 ppm; HRMS (ESI): calcd for C51H78N4O6 421.2955, found 421.2942.

Synthesis of Methyl (4SR,6RS)-5,5-dicyano-2-methyl-4,6-(3-pyridine)-1,4,5,6-tetrahydropyridine-3-carboxylate B:

A mixture of 3-pyridinecarboxaldehyde (6 mmol), malononitrile (3 mmol), methyl acetoacetate (3 mmol) and ammonium acetate (12 mmol, 924 mg) was refluxed in ethanol (10 ml) for 4 h. Formed precipitates were quickly filtrated through a glass filter, and dried under a vacuum to afford white solid product B (0.67 g, 1.8 mmol, 62%).

C20H17N5O2; M. w. 359.39; White solid; M. p. 200–203°C; 1H NMR (300 MHz, DMSO-d6): δ = 8.81 (d, J = 8 Hz, 1H, Ar), 8.72 (dd, J = 4.8 Hz, J1 = 1.5 Hz, 1H, Ar), 8.56–8.53 (m, 2H, Ar), 8.03 (dt, J = 8 Hz, J1 = 1.7 Hz, 1H, Ar), 7.8 (s, 1H, NH), 7.68 (dt, J = 8 Hz, J1 = 1.6 Hz, 1H, Ar), 7.6 (dd, J = 8 Hz, J1 = 4.8 Hz, 1H, Ar), 7.43 (dd, J = 8 Hz, J1 = 4.8 Hz, 1H, Ar), 5.42 (s, 1H, CH), 4.95 (s, 1H, CH), 3.16 (s, 3H, OCH3), 2.36 (s, 3H, CH3) ppm.

Synthesis of Methyl (4RS,6RS)-5,5-dicyano-2-methyl-4,6-(3-pyridine)-1,4,5,6-tetrahydropyridine-3-carboxylate C:

Tetrahydropyridine B (1.39 mmol, 500 mg) in anhydrous DMSO (20 ml) was heated to 80-85 oC for 11 h. After heating, the mixture was concentrated under reduced pressure, water (25 ml) was added to the crude residue. Formed precipitates were filtrated through a glass filter and dried under a vacuum. Compound C was purified by recrystallization in methanol (0.38 g, 1 mmol, 76%).

C20H17N5O2; M. w. 359.39; White solid; M. p. 245–248°C; 1H NMR (300 MHz, DMSO-d6): δ = 8.74-8.63 (m, 3H, Ar), 8.60 (d, J = 4.8 Hz, 1H, Ar), 8.09 (s, 1H, NH), 7.93 (d, J = 8.0 Hz, 1H, Ar), 7.80 (d, J = 7.9 Hz, 1H, Ar), 7.56 (dd, J = 8.1 Hz, J1 = 4.8 Hz, 1H, Ar), 7.47 (dd, J = 7.9 Hz, J1 = 4.8 Hz, 1H, Ar), 5.08 (s, 1H, CH), 4.67 (s, 1H, CH), 3.45 (s, 3H, OCH3), 2.52 (s, 3H, CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 166.2, 154.7, 151.2, 150.8, 149.7, 149.4, 137.3, 136.5, 134.6, 129.5, 123.6, 123.5, 113.6, 112.9, 89.0, 53.3, 50.6, 43.4, 42.4, 19.8 ppm; HRMS (ESI): calcd for C20H18N5O2 360.1455, found 360.1458.

(2'R,4'R)-3',3'-Dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-dialkyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-ium dibromides 5-9:

Halogenoalkane (2 mmol) was added to a solution of C (0.5 mmol, 0.200 g) in dry acetonitrile (3 mL). The mixture was stirred and heated to reflux for 24 h. Result of reaction was confirmed by TLC (ethyl acetate/petroleum ether 1:1). After solvent evaporation under reduced pressure, ethyl acetate (5 mL) was added to the reaction residue and the mixture was vigorously stirred for 1 h. Formed precipitates were quickly filtrated through a glass filter, and dried under a vacuum to afford white solid product.

(2'R,4'R)-3',3'-Dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-dioctyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-ium dibromide (5):

C36H51Br2N5O2; M. w. 585.83; White solid (0.258 g, 0.44 mmol, 88% yield); M. p. 213-216 °C; IR (neat/cm−1): 3438, 3188, 2927, 2856, 2250, 1668, 1252; 1H NMR (300 MHz, DMSO-d6): δ 9.55 (s, 1H, NH), 9.33 (d, J = 6.1 Hz, 1H, CHpy), 9.29-9.20 (m, 2H, 2CHpy), 8.87-8.74 (m, 2H, 2CHpy), 8.50 (s, 1H, CHpy), 8.45-8.28 (m, 2H, 2CHpy), 5.46 (s, 1H, CH), 5.27 (s, 1H, CH), 4.85-4.62 (m, 4H, 2CH2N+), 3.47 (s, 3H, OCH3), 2.57 (s, 3H, CH3), 1.97-1.91 (m, 4H, 2CH2), 1.31-1.20 (m, 20H, 10CH2), 0.92-0.80 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.5, 146.3, 145.3, 145.2, 144.8, 144.7, 139.2, 133.8, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.1, 51.7, 50.7, 42.5, 41.9, 31.08, 31.02, 30.6, 30.5, 28.38, 28.31, 25.2, 25.1, 21.98, 21.96, 20.1, 13.8 ppm; HRMS (ESI): calcd for C36H51N5O2 292.7016, found 292.7010.

(2'R,4'R)-3',3'-Dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-dinonyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-ium dibromide (6):

C38H55Br2N5O2; M. w. 613.89; White solid (0.264 g, 0.43 mmol, 86% yield); M. p. 214-217 °C; IR (neat/cm−1): 3430, 3186, 2927, 2855, 2251, 1668, 1253; 1H NMR (300 MHz, DMSO-d6): δ 9.55 (s, 1H, NH), 9.33 (d, J = 6.1 Hz, 1H, CHpy), 9.30-9.20 (m, 2H, 2CHpy), 8.87-8.74 (m, 2H, 2CHpy), 8.50 (s, 1H, CHpy), 8.45-8.28 (m, 2H, 2CHpy), 5.46 (s, 1H, CH), 5.28 (s, 1H, CH), 4.86-4.65 (m, 4H, 2CH2N+), 3.48 (s, 3H, OCH3), 2.58 (s, 3H, CH3), 1.97-1.91 (m, 4H, 2CH2), 1.32-1.16 (m, 24H, 12CH2), 0.92-0.81 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.5, 146.3, 145.3, 145.1, 144.79, 144.70, 139.2, 133.8, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.0, 51.7, 50.7, 42.4, 41.8, 31.15, 31.12, 30.6, 30.5, 28.66, 28.6, 28.5, 28.4, 28.3, 25.2, 25.1, 22.0, 21.9, 20.1, 13.8 ppm; HRMS (ESI): calcd for C38H53N5O2 306.7172, found 306.7181.

(2'R,4'R)-3',3'-Dicyano-1,1''-didecyl-5'-(methoxycarbonyl)-6'-methyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-diium bromide (7):

C40H59Br2N5O2; M. w. 641.94; White solid (0.289 g, 0.45 mmol, 90% yield); M. p. 218-221 °C; IR (neat/cm−1): 3434, 3189, 2926, 2855, 2249, 1668, 1251; 1H NMR (300 MHz, DMSO-d6): δ 9.54 (s, 1H, NH), 9.34 (d, J = 6.1 Hz, 1H, CHpy), 9.30-9.23 (m, 2H, 2CHpy), 8.88-8.76 (m, 2H, 2CHpy), 8.50 (s, 1H, CHpy), 8.46-8.32 (m, 2H, 2CHpy), 5.48 (s, 1H, CH), 5.26 (s, 1H, CH), 4.82-4.70 (m, 4H, 2CH2N+), 3.50 (s, 3H, OCH3), 2.59 (s, 3H, CH3), 1.99-1.93 (m, 4H, 2CH2), 1.36-1.19 (m, 28H, 14CH2), 0.94-0.84 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.7, 156.1, 146.6, 146.3, 145.3, 145.2, 144.7, 139.3, 133.9, 128.1, 128.0, 112.3, 111.9, 87.7, 61.3, 61.1, 51.8, 50.8, 42.5, 41.9, 31.2, 30.6, 30.5, 28.8, 28.79, 28.76, 28.70, 28.6, 28.3, 25.2, 22.0, 20.1, 13.9 ppm; HRMS (ESI): calcd for C40H59N5O2 320.7329, found 320.7327.

(2'R,4'R)-3',3'-dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-diundecyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-diium bromide (8):

C42H63Br2N5O2; M. w. 669.99; White solid (0.281 g, 0.42 mmol, 84% yield); M. p. 215-218 °C; IR (neat/cm−1): 3433, 3187, 2926, 2854, 2249, 1669, 1251; 1H NMR (300 MHz, DMSO-d6): δ 9.55 (s, 1H, NH), 9.33 (d, J = 6.1 Hz, 1H, CHpy), 9.29-9.20 (m, 2H, 2CHpy), 8.87-8.74 (m, 2H, 2CHpy), 8.51 (s, 1H, CHpy), 8.44-8.28 (m, 2H, 2CHpy), 5.45 (s, 1H, CH), 5.28 (s, 1H, CH), 4.85-4.64 (m, 4H, 2CH2N+), 3.47 (s, 3H, OCH3), 2.56 (s, 3H, CH3), 1.98-1.90 (m, 4H, 2CH2), 1.31-1.14 (m, 32H, 16CH2), 0.91-0.81 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.5, 146.3, 145.3, 145.2, 144.8, 144.7, 139.2, 133.8, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.1, 51.7, 50.7, 42.5, 41.9, 31.2, 30.6, 30.5, 28.9, 28.89, 28.83, 28.7, 28.68, 28.64, 28.3, 25.2, 25.1, 22.0, 20.1, 13.8 ppm; HRMS (ESI): calcd for C42H63N5O2 334.7485, found 334.7497.

(2'R,4'R)-3',3'-dicyano-1,1''-didodecyl-5'-(methoxycarbonyl)-6'-methyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-diium bromide (9):

C44H67Br2N5O2; M. w. 698.05; White solid (0.321 g, 0.46 mmol, 92% yield); M. p. 229-232 °C; IR (neat/cm−1): 3438, 3189, 2925, 2853, 2249, 1669, 1250; 1H NMR (300 MHz, DMSO-d6): δ 9.52 (s, 1H, NH), 9.31 (d, J = 6.1 Hz, 1H, CHpy), 8.85-8.72 (m, 2H, 2CHpy), 8.47 (s, 1H, CHpy), 8.44-8.26 (m, 2H, 2CHpy), 5.44 (s, 1H, CH), 5.24 (s, 1H, CH), 4.81-4.63 (m, 4H, 2CH2N+), 3.46 (s, 3H, OCH3), 2.56 (s, 3H, CH3), 1.96-1.90 (m, 4H, 2CH2), 1.36-1.13 (m, 36H, 18CH2), 0.85 (t, J = 6.5 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.6, 146.3, 145.3, 145.2, 144.7, 139.2, 133.9, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.1, 51.7, 50.7, 42.4, 41.9, 31.2, 30.6, 30.5, 28.96, 28.91, 28.8, 28.7, 28.6, 28.3, 25.27, 25.1, 22.0, 20.1, 13.9 ppm; HRMS (ESI): calcd for C44H67N5O2 348.7642, found 348.7636.

Synthesis of Ethyl 6-amino-5-cyano-2-methoxy-4-(pyridin-3-yl)-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-3-carboxylate D:

A mixture of 3-pyridinecarboxaldehyde (2 mmol), malononitrile (2 mmol), ethyl 4,4,4-trifluoroacetoacetate (2 mmol) and ammonium acetate (2 mmol, 154 mg) was stirred in methanol (5 мл) for 6 h. The compound D was isolated by simple filtration (0.47 g, 1.26 mmol, 63% yield).

C16H16F3N3O4; M. w. 371,316; White solid; M. p. 196–199°C; 1H NMR (300 MHz, DMSO-d6): δ 8.54-8.46 (m, 2H, 2CHpy), 7.82 (d, J = 7.9 Hz, 1H, CHpy), 7.38 (t, J = 5.9 Hz, 1H, CHpy), 7.11 (s, 2H, NH2), 4.00 (d, J = 11.9 Hz, 1H, CH), 3.90 (q, J = 7.1 Hz, 2H, CH2), 3.34 (s, 3H, OCH3), 3.23 (d, J = 11.9 Hz, 1H, CH), 0.90 (t, J = 7.1 Hz, 3H, CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 166.4, 159.3, 150.0, 149.1, 136.1, 134.6, 123.6, 121.3 (q, J = 291.1 Hz, CF3), 119.0, 96.1 (q, J = 31.9 Hz, C(CF3)), 60.9, 56.5, 52.5, 48.8, 36.3, 13.4 ppm; HRMS (ESI): calcd for C16H16F3N3O4 372.1166, found 372.1179.

Synthesis of 3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-alkylpyridin-1-ium bromides 10-12:

Halogenoalkane (2 mmol) was added to a solution of D (0.5 mmol, 0.200 g) in dry acetonitrile (3 mL). The mixture was stirred and heated to reflux for 24 h. Result of reaction was confirmed by TLC (ethyl acetate/petroleum ether 1:1). After solvent evaporation under reduced pressure, ethyl acetate (5 mL) was added to the reaction residue and the mixture was vigorously stirred for 1 h. Formed precipitates were quickly filtrated through a glass filter, and dried under a vacuum to afford white solid product.

3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-nonylpyridin-1-ium bromide (10):

C25H35BrF3N3O4; M. w. 578,471; White solid (0.257 g, 0.44 mmol, 89% yield); M. p. 178–180; IR (neat/cm−1): 3258, 3094, 2929, 2857, 2194, 1738, 1636, 1600; 1H NMR (300 MHz, DMSO-d6): δ 9.35 (s, 1H, CHpy), 9.13 (d, J = 6.0 Hz, 1H, CHpy), 8.80 (d, J = 8.1 Hz, 1H, CHpy), 8.29-8.19 (m, 1H, CHpy), 7.39 (s, 2H, NH2), 4.63 (t, J = 7.1 Hz, 2H, 2CH2N+), 4.32 (d, J = 11.9 Hz, 1H, CH), 4.06-3.82 (m, 2H, OCH2), 3.61-3.52 (m, 4H, CH + OCH3), 1.96-1.85 (m, 2H, CH2), 1.27-1.21 (m, 12H, 6CH2), 0.98 (t, J = 7.1 Hz, 3H, CH3), 0.87 (t, J = 6.3 Hz, CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.9, 159.6, 145.8, 144.7, 144.6, 140.5, 128.1, 121.1 (q, J = 291.3 Hz, CF3), 118.7, 96.2 (q, J = 33.2 Hz, C(CF3)), 61.4, 60.9, 54.9, 52.7, 47.6, 36.1, 31.1, 30.6, 28.6, 28.4, 28.3, 25.0, 22.0, 13.8, 13.5 ppm; HRMS (ESI): calcd for C25H35F3N3O4 498.2574, found 498.2568.

3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-undecylpyridin-1-ium bromide (11):

C27H39BrF3N3O4; M. w. 606,525; White solid (0.242 g, 0.39 mmol, 84% yield); M. p. 162–165°C; IR (neat/cm−1): 3258, 3091, 2928, 2856, 2194, 1738, 1635, 1600; 1H NMR (300 MHz, DMSO-d6): δ 9.35 (s, 1H, CHpy), 9.14 (d, J = 6.0 Hz, 1H, CHpy), 8.80 (d, J = 8.1 Hz, 1H, CHpy), 8.24 (t, J = 7.1 Hz, 1H, CHpy), 7.37 (s, 2H, NH2), 4.63 (t, J = 7.1 Hz, 2H, 2CH2N+), 4.32 (d, J = 12.0 Hz, 1H, CH), 4.06-3.82 (m, 2H, OCH2), 3.62-3.50 (m, 4H, CH + OCH3), 1.96-1.85 (m, 2H, CH2), 1.36-1.13 (m, 16H, 8CH2), 0.98 (t, J = 7.1 Hz, 3H, CH3), 0.87 (t, J = 6.3 Hz, CH3); 13C NMR (75 MHz, DMSO-d6): δ 165.9, 159.5, 145.8, 144.7, 144.6, 140.5, 128.7, 121.1 (q, J = 290.4 Hz, CF3), 118.7, 96.2 (q, J = 32.8 Hz, C(CF3)), 61.4, 60.9, 54.9, 52.7, 47.6, 36.1, 31.2, 30.6, 28.9, 28.8, 28.7, 28.6, 28.3, 25.0, 22.0, 13.8, 13.5 ppm; HRMS (ESI): calcd for C27H39F3N3O4 526.2887, found 526.2879.

3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-dodecylpyridin-1-ium bromide (12):

C28H41BrF3N3O4; M. w. 620,552; White solid (0.251 g, 0.4 mmol, 81% yield); M. p. 175–177°C; IR (neat/cm−1): 3259, 3084, 2927, 2855, 2193, 1738, 1634, 1600; 1H NMR (300 MHz, DMSO-d6): δ 9.35 (s, 1H, CHpy), 9.13 (d, J = 6.0 Hz, 1H, CHpy), 8.80 (d, J = 8.1 Hz, 1H, CHpy), 8.29-8.18 (m, 1H, CHpy), 7.37 (s, 2H, NH2), 4.63 (t, J = 7.1 Hz, 2H, 2CH2N+), 4.32 (d, J = 12.0 Hz, 1H, CH), 4.06-3.82 (m, 2H, OCH2), 3.61-3.52 (m, 4H, CH + OCH3), 1.96-1.85 (m, 2H, CH2), 1.35-1.13 (m, 18H, 9CH2), 0.98 (t, J = 7.1 Hz, 3H, CH3), 0.88 (t, J = 6.3 Hz, CH3); 13C NMR (75 MHz, DMSO-d6): δ 166.0, 159.6, 145.8, 144.8, 144.6, 140.5, 128.1, 121.2 (q, J = 291.9 Hz, CF3), 119.0, 96.3 (q, J = 31.7 Hz, C(CF3)), 61.4, 60.9, 54.9, 52.7, 47.6, 36.1, 31.2, 30.7, 28.98, 28.95, 28.8, 28.7, 28.6, 28.3, 25.1, 22.0, 13.9, 13.5 ppm; HRMS (ESI): calcd for C28H41F3N3O4 540.3044, found 540.3022.

Synthesis of ethyl (2-(2-hydroxyethoxy)ethyl)carbamate (X)

A round-bottom flask equipped with a Dean–Stark apparatus was charged with diethyl carbonate (42 mmol) and 2-(2-aminoethoxy)ethan-1-ol (85 mmol). The reaction mixture was stirred at 125°C for 24 h and then heated under reflux at 150 °C for 4 days. The product was purified by column chromatography (EtOAc/MeOH, 8:1) and obtained as an orange oil in 75% yield (31.5 mmol, 5.58 g).

C7H15NO4; M. w. 177.200; orange oil; 1H NMR (300 MHz, DMSO-d6) δ 7.13 – 7.03 (m, 1H, NH), 4.59 (t, J = 5.5 Hz, 1H, OH), 3.99 (q, J = 7.1 Hz, 2H, СH2), 3.50 (q, J = 5.3 Hz, 2H, CH2), 3.45 – 3.37 (m, 4H, 2CH2), 3.13 (q, J = 5.9 Hz, 2H, 2CH2), 1.16 (t, J = 7.1 Hz, 3H, CH3).

1,3-bis(2-(2-hydroxyethoxy)ethyl)urea (X)

Ethyl(2-(2-hydroxyethoxy)ethyl)carbamate (9 mmol) and 2-(2-aminoethoxy)ethan-1-ol (10 mmol) were placed in a round-bottom flask equipped with a Dean–Stark apparatus. The reaction mixture was stirred at 180–190 °C for 7 days. Purification by column chromatography (EtOAc/MeOH, 8:1) afforded the desired product as an orange oil in 60% yield (5.4 mmol, 1.28 g).

C9H20N2O5; M. w. 236.268; orange oil; 1H NMR (300 MHz, DMSO-d6) δ 6.08 – 5.87 (m, 2H, 2NH), 4.58 (t, 2H, 2OH), 3.65 – 3.46 (m, 4H, 2CH2), 3.46 – 3.36 (m, 8H, 4CH2), 3.20 – 3.12 (m, 4H, 2CH2).

1,3,4,6-tetrakis(2-(2-hydroxyethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione (X)

1,3-Bis(2-(2-hydroxyethoxy)ethyl)urea (2.54 mmol) and a 45% aqueous solution of glyoxal (1.15 mmol in 0.5 mL of water) were placed in a round-bottom flask. The mixture was acidified to pH~1 with concentrated HCl and stirred at 90 °C for 6 h. The reaction progress was monitored by TLC (EtOAc/MeOH, 2:1). The reaction mixture was then neutralized with 25% aqueous NaOH and concentrated to dryness under reduced pressure. The resulting yellow oily crude product was purified by column chromatography (EtOAc/MeOH, 8:1) to afford the desired product in 53% yield (1.35 mmol, 0,668 g).

C20H38N4O10; M. w. 494.542; light yellow oil;1H NMR (300 MHz, DMSO-d6) δ 5.54 (s, 2H, 2CH), 4.63 (t, J = 5.3 Hz, 4H, 4OH), 3.64 – 3.47 (m, 20H, 10CH2), 3.47 – 3.39 (m, 8H, 4CH2), 3.34 – 3.26 (m, 4H, 2CH2). 13C NMR (75 MHz, DMSO-d6) δ 158.41, 72.26, 69.02, 68.53, 60.19, 42.17, 25.49.

1,3,4,6-tetrakis(2-(2-chloroethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione (X)

A round-bottom flask containing the compound (0.6 mmol) in chloroform (2 ml) was placed in an ice bath. Thionyl chloride (3.36 mmol) was added dropwise to the stirred solution. The reaction mixture was then heated under reflux for 12 h. The solvent was removed under reduced pressure, and the resulting yellow oily crude product was purified by column chromatography (chloroform) to afford the desired product in 70% yield (0.42 mmol, 0.238 g).

C20H34Cl4N4O6; M. w. 568.314; light yellow oil; 1H NMR (300 MHz, CDCl3) δ 5.69 (s, 2H, 2CH), 3.77 – 3.59 (m, 28H, 14CH2), 3.53 – 3.47 (m, 2H, CH2), 3.47 – 3.42 (m, 2H, CH2). 13C NMR (75 MHz, CDCl3) δ 158.87, 71.14, 70.33, 70.07, 43.25, 42.59.

1,3,4,6-tetrakis(2-(2-(4-(alkylamino)-1λ4 -pyridin-1-yl)ethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione (13-17)

1,3,4,6-Tetrakis(2-(2-chloroethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione and N-alkylpyridin-4-amine were placed in a round-bottom flask. Dry 1-butanol (1–2 mL) was added, and the mixture was heated under reflux for 5 days. After completion, the reaction mixture was concentrated to dryness under reduced pressure. The resulting yellow solid was purified by recrystallization from acetonitrile to afford the product.

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(heptylamino)pyridin-1-ium) tetrachloride (13)

C68H114Cl4N12O6; M. w. 1337.538; white hygroscopic solid (0.176 g, 0.13 mmol, 71% yield); IR (neat/cm−1): 3208, 3102, 3015, 2955, 2929, 2857, 1695, 1653, 1590, 1557, 1520, 1482, 1351, 1320, 1237, 1316, 1194, 1117, 1053, 905, 842, 782, 724, 664, 578, 544, 506 1H NMR (300 MHz, DMSO-d6) δ 9.19 – 8.97 (m, 4H, NH), 8.29 (d, J = 7.0 Hz, 4H, CHpy), 8.10 (d, J = 7.2 Hz, 4H, CHpy), 6.94 (dd, J = 27.7, 7.3 Hz, 8H, CHar), 5.33 (s, 2H, CHgl), 4.48 – 4.20 (m, 8H, CH2(py)), 3.79 – 3.69 (m, 8H, CH2(gl)), 3.60 – 3.37 (m, J = 29.0 Hz, 12H, CH2(alk)), 3.28 – 3.15 (m, J = 5.8 Hz, 12H, CH2(NH)), 1.63 – 1.45 (m, J = 6.9 Hz, 8H, CH2(alk)), 1.42 – 1.12 (m, 32H, CH2(alk)), 0.86 (t, J = 6.8 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 158.75, 157.19, 144.41, 142.04, 110.34, 105.35, 69.39, 68.68, 56.59, 42.72, 42.64, 31.67, 28.84, 28.40, 26.78, 22.51, 14.40. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C68H114N12O64+ 298.7229, found 298.7249.

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(octylamino)pyridin-1-ium) tetrachloride (14)

C72H122Cl4N12O6; M. w. 1393.646; white hygroscopic solid (0.162 g, 0.12 mmol, 68% yield); IR (neat/cm−1): 3207, 3100, 2926, 2855, 2326, 1695, 1652, 1590, 1556, 1482, 1352, 1318, 1237, 1193, 1117, 1064, 841, 782, 723, 508; 1H NMR (300 Мгц, DMSO-d6) δ 9.16 – 9.05 (m, 4H, NH), 8.38 – 8.24 (m, 4H, CHpy), 8.10 (dd, J = 7.3, 1.7 Hz, 4H, CHpy), 6.99 (dd, J = 7.3, 2.8 Hz, 4H, CHpy), 6.89 (dd, J = 7.5, 2.8 Hz, 4H, CHpy), 5.34 (s, 2H, CHgl), 4.38 – 4.22 (m, 8H, CH2(py)), 3.85 – 3.65 (m, 8H, CH2(gl)), 3.62 – 3.37 (m, 12H, CH2(alk)), 3.28 – 3.11 (m, 12H, CH2(NH)), 1.66 – 1.46 (m, 8H, CH2(alk)), 1.40 – 1.17 (m, 40H, CH2(alk)), 0.86 (t, J = 6.3 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 158.77, 157.20, 144.42, 142.04, 110.37, 105.35, 69.62, 69.40, 68.69, 56.60, 42.74, 31.71, 29.16, 29.12, 28.40, 26.84, 22.55, 14.41. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C72H122N12O64+ 312.7390, found 312.7397.

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(nonylamino)pyridin-1-ium) tetrachloride (15)

C76H130Cl4N12O6; M. w. 1449.754; white hygroscopic solid (0.190 g, 0.13 mmol, 75% yield); IR (neat/cm−1): 3206, 3100, 2926, 2855. 1695, 1653, 1590, 1558, 1520, 1352, 1320, 1237, 1195, 1118, 1054, 905, 842, 782, 723, 581, 507; 1H NMR (300 MHz, DMSO-d6) δ 9.14 (t, J = 5.3 Hz, 4H, NH), 8.31 (d, J = 7.8 Hz, 4H, CHpy), 8.12 (d, J = 6.1 Hz, 4H, CHpy), 7.01 (dd, J = 7.3, 2.6 Hz, 4H, CHar), 6.88 (dd, J = 7.5, 2.6 Hz, 4H, CHar), 5.35 (s, 2H, CHgl), 4.47 – 4.17 (m, 8H, CH2(py)), 3.86 – 3.62 (m, 8H, CH2(gl)), 3.62 – 3.36 (m, J = 19.9, 8.3 Hz, 12H, CH2(alk)), 3.27 – 3.14 (m, 12H, CH2(NH)), 1.66 – 1.43 (m, J = 6.8 Hz, 8H, CH2(alk)), 1.41 – 1.06 (m, 48H, CH2(alk)), 0.86 (t, J = 6.6 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 158.75, 157.18, 144.40, 142.04, 110.35, 105.36, 69.38, 68.67, 56.60, 42.73, 42.64, 31.74, 29.43, 29.20, 29.13, 28.40, 26.83, 22.56, 14.70. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C76H130N12O64+ 326.7561, found 326.7554

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(decylamino)pyridin-1-ium) tetrachloride (16)

C80H138Cl4N12O6; M. w. 1505.862; white hygroscopic solid (0.168 g, 0.11 mmol, 81% yield); IR (neat/cm−1): 3207, 3100, 2926, 2855, 1695, 1663, 1591, 1557, 1519, 1480, 1352, 1321, 1237, 1194, 1117, 1056, 844, 786, 753, 719, 545, 507; 1H NMR (300 MHz, DMSO-d6) δ 9.18 – 9.07 (m, 4H, NH), 8.30 (d, J = 7.4 Hz, 4H, CHpy), 8.11 (d, J = 7.5 Hz, 4H, CHpy), 6.99 (d, J = 7.2 Hz, 4H, CHpy), 6.89 (d, J = 6.4 Hz, 4H, CHpy), 5.34 (s, 2H, CHgl), 4.41 – 4.26 (m, 8H, CH2(py)), 3.81 – 3.66 (m, 8H, CH2(gl)), 3.57 – 3.39 (m, 12H, CH2(alk)), 3.28 – 3.17 (m, 12H, CH2(NH)), 1.65 – 1.48 (m, 8H, CH2(alk)), 1.41 – 1.17 (m, 56H, CH2(alk)), 0.86 (t, J = 6.3 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 157.20, 144.43, 142.06, 110.37, 105.37, 69.40, 68.68, 56.61, 42.75, 31.77, 29.49, 29.46, 29.22, 29.18, 28.40, 26.85, 22.57, 14.42. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C80H138N12O64+ 340.7697, found 340.7710

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(dodecylamino)pyridin-1-ium) tetrachloride (17)

C88H154Cl4N12O6; M. w. 1618.078; white hygroscopic solid (0.174 g, 0.11 mmol, 70% yield); IR (neat/cm−1): 3207, 3099, 2925, 2854, 1695, 1653, 1591, 1557, 1469, 1353, 1194, 1118, 1056, 842, 754, 622, 580, 505; 1H NMR (300 MHz, DMSO-d6) δ 9.40 – 9.18 (m, 4H, NH), 8.28 (d, J = 3.5 Hz, 4H, CHpy), 8.07 (d, J = 5.2 Hz, 4H, CHpy), 7.01 (d, J = 7.2 Hz, 4H, CHpy), 6.87 (d, J = 7.7 Hz, 4H, CHpy), 5.32 (s, 2H, CHgl), 4.44 – 4.14 (m, 8H, CH2(py)), 3.82 – 3.64 (m, 8H, CH2(gl)), 3.58 – 3.41 (m, 12H, CH2(alk)), 3.26 – 3.13 (m, 12H, CH2(NH)), 1.62 – 1.48 (m, 8H, CH2(alk)), 1.42 – 1.14 (m, 72H, CH2(alk)), 0.86 (t, J = 6.5 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 157.20, 144.42, 142.04, 110.38, 105.35, 69.40, 68.68, 56.60, 42.75, 31.78, 29.56, 29.51, 29.24, 29.20, 28.41, 26.87, 22.57, 14.41. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C88H154N12O64+ 368.8040, found 368.8023


S16.6. Microbiological assay

S16.6.1. Bacterial strains

Laboratory strains of the microorganisms E. coli ATCC 25922, S. aureus ATCC 43300 were obtained from the State Collection of Pathogenic Microorganisms (Obolensk, Russia).

S16.6.2. Identification of microorganisms

Species identification of microorganisms was carried out on a MALDI-TOF Biotyper mass spectrometer (Bruker, Billerica, MA, USA) according to the standard microflex User Manual. One part of the daily bacterial culture was introduced into a 2 mL tube (Eppendorf, Hamburg, Germany) containing 300 µL of deionized water and triturated until a homogeneous suspension was obtained. Then, 900 µL of 96% ethanol was added and shaken. The tube was then centrifuged at 12,000× g for 2 min. The supernatant was discarded, and the precipitate was dried in air. After drying, the precipitate was thoroughly mixed with 30 µL of 70% formic acid, incubated for 10 min at room temperature, and then mixed with 30 µL of acetonitrile (Sigma-Aldrich, St. Louis, MO, USA) and incubated for another 10 min. This mixture was centrifuged at 12,000×g for 2 min; then, 1 µL of the supernatant was transferred to an MSP 96 Polished Steel MALDI Target Plate (Bruker Daltonik GmbH, Bremen, Germany), air-dried, and covered with 1 µL of a saturated solution of α-cyano-4-hydroxycinnamic acid (Bruker Daltonik, Bremen, Germany). The MALDI target plate was placed in a MALDI-TOF microflex LRF instrument (Bruker Daltonik, Bremen, Germany). The data acquisition settings were as follows: ion source 1 at 19.50 kV, ion source 2 at 18.22 kV, lens at 7.01 kV, and a mass range of 2000 to 20,000 Da. Spectrum registration was performed automatically using MALDI Biotyper RTC 3.1 software (Bruker Daltonik, Bremen, Germany). The obtained spectra were compared with the reference spectra of the FFL v1.0 data-base. Identification scores ≥2.0 and 1.7–1.99 indicated recognition of the species and genus levels, respectively, while scores <1.7 indicated a lack of reliable data.

S16.6.3. Cultivation of microorganisms

Microorganisms were cultivated using agar and GRM broth. Cultivation of microorganisms was carried out for 20–24 h at a temperature of 37°C.

S16.6.4. MIC and MBC determination

The synthesized QACs were dissolved in the DMSO/water system at a ratio of 1/9 with a final concentration of 1000 mg/L. For better dissolution, the samples were sonicated for 15 to 60 minutes at 40°C. MIC and MBC were determined by broth microdilution. General broth-dilution methodology is described in CLSI M07 (76); this citation identifies the relevant methodological standard without independently verifying all details of the archived assays.

[COAUTHORS C1 — Supply the original compound spectra and evidence of identity/purity, the optimisation table and auxiliary reaction schemes cited above; describe the final assay conditions, controls, replicate counts and endpoint conversions. Chemical Table S10 and Schemes S5–S6 are reserved for this material.]

S17. Supplementary references for historical and chemical descriptions

References below preserve the source numbering used in Sections S15–S16 and other historical material. Main-article references use a separate, shorter sequence. Duplicate references 30 and 77 refer to the same MolSkill publication and are retained solely to resolve the source numbering.

1.Iskandar, K.; Murugaiyan, J.; Hammoudi Halat, D.; Hage, S. E.; Chibabhai, V.; Adukkadukkam, S.; Roques, C.; Molinier, L.; Salameh, P.; Van Dongen, M., Antibiotic Discovery and Resistance: The Chase and the Race. Antibiotics (Basel) 2022, 11.

2.Gargate, N.; Laws, M.; Rahman, K. M., Current economic and regulatory challenges in developing antibiotics for Gram-negative bacteria. npj Antimicrobials and Resistance 2025, 3, 50.

3.Lack of innovation set to undermine antibiotic performance and health gains. https://www.who.int/news/item/22-06-2022-22-06-2022-lack-of-innovation-set-to-undermine-antibiotic-performance-and-health-gains (15.04.2026),

4.Melchiorri, D.; Rocke, T.; Alm, R. A.; Cameron, A. M.; Gigante, V., Addressing urgent priorities in antibiotic development: insights from WHO 2023 antibacterial clinical pipeline analyses. Lancet Microbe 2025, 6, 100992.

5.Sati, H.; Carrara, E.; Savoldi, A.; Hansen, P.; Garlasco, J.; Campagnaro, E.; Boccia, S.; Castillo-Polo, J. A.; Magrini, E.; Garcia-Vello, P.; Wool, E.; Gigante, V.; Duffy, E.; Cassini, A.; Huttner, B.; Pardo, P. R.; Naghavi, M.; Mirzayev, F.; Zignol, M.; Cameron, A.; Tacconelli, E.; Aboderin, A.; Al Ghoribi, M.; Al-Salman, J.; Amir, A.; Apisarnthanarak, A.; Blaser, M.; El-Sharif, A.; Essack, S.; Harbarth, S.; Huang, X.; Kapoor, G.; Knight, G.; Muhwa, J. C.; Monnet, D. L.; Ousassa, T.; Sacsaquispe, R.; Severin, J.; Sugai, M.; Taneja, N.; Umubyeyi Nyaruhirira, A., The WHO Bacterial Priority Pathogens List 2024: a prioritisation study to guide research, development, and public health strategies against antimicrobial resistance. The Lancet Infectious Diseases 2025, 25, 1033-1043.

6.Schroder, H.; Machunsky, C.; Strobach, H.; Schror, K., Nitric oxide but not prostacyclin has an autocrine function in porcine aortic endothelial cells. Advances in prostaglandin, thromboxane, and leukotriene research 1991, 21B, 671-4.

7.Organization, W. H., Analysis of antibacterial agents in clinical and preclinical development: overview and analysis 2025. 2025.

8.Coelho, J. R.; Carriço, J. A.; Knight, D.; Martínez, J. L.; Morrissey, I.; Oggioni, M. R.; Freitas, A. T., The use of machine learning methodologies to analyse antibiotic and biocide susceptibility in Staphylococcus aureus. PLoS One 2013, 8, e55582.

9.Lin, B.; Yan, S.; Zhen, B., A machine learning method for predicting molecular antimicrobial activity. Scientific Reports 2025, 15, 6559.

10.Krishnan, R.; Howard, I. S.; Comber, S.; Jha, A. N., In silico prediction of acute chemical toxicity of biocides in marine crustaceans using machine learning. Science of The Total Environment 2023, 887, 164072.

11.Jukič, M.; Bren, U., Machine Learning in Antibacterial Drug Design. Frontiers in Pharmacology 2022, Volume 13 - 2022.

12.Shankarnarayan, S. A.; Guthrie, J. D.; Charlebois, D. A. Machine learning for antimicrobial resistance research and drug development. In The Global Antimicrobial Resistance Epidemic-Innovative Approaches and Cutting-Edge Solutions; IntechOpen: 2022.

13.Diéguez-Santana, K.; González-Díaz, H., Machine learning in antibacterial discovery and development: A bibliometric and network analysis of research hotspots and trends. Computers in Biology and Medicine 2023, 155, 106638.

14.Liu, Z.; Chen, Q.; Yao, C.; Wang, Y.; Zhu, S.; Guan, J.; Miao, Y., The chemical design of antimicrobial ionic liquids guided by machine learning: a review on balancing efficacy and toxicity. Journal of Materials Chemistry B 2026, 14, 3023-3047.

15.Sadaghiyanfam, S.; Kamberaj, H.; Isler, Y., Leveraging ChemBERTa and machine learning for accurate toxicity prediction of ionic liquids. Journal of the Taiwan Institute of Chemical Engineers 2025, 171, 106030.

16.Krishnan, A.; Anahtar, M. N.; Valeri, J. A.; Jin, W.; Donghia, N. M.; Sieben, L.; Luttens, A.; Zhang, Y.; Modaresi, S. M.; Hennes, A.; Fromer, J.; Bandyopadhyay, P.; Chen, J. C.; Rehman, D.; Desai, R.; Edwards, P.; Lach, R. S.; Aschtgen, M.-S.; Gaborieau, M.; Gaetani, M.; Palace, S. G.; Omori, S.; Khonde, L.; Moroz, Y. S.; Blough, B.; Jin, C.; Loh, E.; Grad, Y. H.; Saei, A. A.; Coley, C. W.; Wong, F.; Collins, J. J., A generative deep learning approach to <em>de novo</em> antibiotic design. Cell 2025, 188, 5962-5979.e22.

17.Olayo-Alarcon, R.; Amstalden, M. K.; Zannoni, A.; Bajramovic, M.; Sharma, C. M.; Brochado, A. R.; Rezaei, M.; Müller, C. L., Pre-trained molecular representations enable antimicrobial discovery. Nature Communications 2025, 16, 3420.

18.Taha, M. M. E.; Oraibi, B.; Abdelwahab, S. I.; Sahli, K. A.; Assiri, A.; Qadri, M.; Alarifi, A.; Khardali, A.; Farasani, A.; Moshi, J. M.; Alsaadi, K. H.; Alshahrani, S.; Shubaily, H. M.; Binjomah, A. Z., Global trends and thematic evolution in antimicrobial stewardship research: a comprehensive bibliometric and network analysis (1977–2025). Journal of Hospital Infection 2026, 171, 11-26.

19.Wang, X.; Rai, N.; Merchel Piovesan Pereira, B.; Eetemadi, A.; Tagkopoulos, I., Accelerated knowledge discovery from omics data by optimal experimental design. Nature Communications 2020, 11, 5026.

20.Sowers, A.; Wang, G.; Xing, M.; Li, B., Advances in Antimicrobial Peptide Discovery via Machine Learning and Delivery via Nanotechnology. Microorganisms 2023, 11, 1129.

21.Wang, Y.; Zhao, L.; Li, Z.; Xi, Y.; Pan, Y.; Zhao, G.; Zhang, L., A generative artificial intelligence approach for the discovery of antimicrobial peptides against multidrug-resistant bacteria. Nature Microbiology 2025, 10, 2997-3012.

22.Raissi, M.; Perdikaris, P.; Karniadakis, G. E., Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. Journal of Computational Physics 2019, 378, 686-707.

23.Cuomo, S.; Di Cola, V. S.; Giampaolo, F.; Rozza, G.; Raissi, M.; Piccialli, F., Scientific Machine Learning Through Physics–Informed Neural Networks: Where we are and What’s Next. Journal of Scientific Computing 2022, 92, 88.

24.Kuang, T.; Liu, P.; Ren, Z., Impact of Domain Knowledge and Multi-Modality on Intelligent Molecular Property Prediction: A Systematic Survey. Big Data Mining and Analytics 2024, 7, 858-888.

25.Wahyudi, A.; Sueviriyapan, N.; Suriyapraphadilok, U., Generalizable physics-informed graph neural network for CO2 solubility prediction across amine classes. Separation and Purification Technology 2026, 385, 136395.

26.Selby, D. A.; Jakhmola, R.; Sprang, M.; Großmann, G.; Raki, H.; Maani, N.; Pavliuk, D.; Ewald, J.; Vollmer, S., Visible neural networks for multi-omics integration: a critical review. Frontiers in Artificial Intelligence 2025, Volume 8 - 2025.

27.Bickerton, G. R.; Paolini, G. V.; Besnard, J.; Muresan, S.; Hopkins, A. L., Quantifying the chemical beauty of drugs. Nature chemistry 2012, 4, 90-8.

28.Lajiness, M. S.; Maggiora, G. M.; Shanmugasundaram, V., Assessment of the consistency of medicinal chemists in reviewing sets of compounds. J Med Chem 2004, 47, 4891-6.

29.Kutchukian, P. S.; Vasilyeva, N. Y.; Xu, J.; Lindvall, M. K.; Dillon, M. P.; Glick, M.; Coley, J. D.; Brooijmans, N., Inside the Mind of a Medicinal Chemist: The Role of Human Bias in Compound Prioritization during Drug Discovery. PLOS ONE 2012, 7, e48476.

30.Choung, O.-H.; Vianello, R.; Segler, M.; Stiefl, N.; Jiménez-Luna, J., Extracting medicinal chemistry intuition via preference machine learning. Nature Communications 2023, 14, 6651.

31.Sundin, I.; Voronov, A.; Xiao, H.; Papadopoulos, K.; Bjerrum, E. J.; Heinonen, M.; Patronov, A.; Kaski, S.; Engkvist, O., Human-in-the-loop assisted de novo molecular design. Journal of Cheminformatics 2022, 14, 86.

32.Menke, J.; Nahal, Y.; Bjerrum, E. J.; Kabeshov, M.; Kaski, S.; Engkvist, O., Metis: a python-based user interface to collect expert feedback for generative chemistry models. Journal of Cheminformatics 2024, 16, 100.

33.Christiano, P. F.; Leike, J.; Brown, T.; Martic, M.; Legg, S.; Amodei, D. Deep Reinforcement Learning from Human Preferences. In Advances in Neural Information Processing Systems, 2017; Curran Associates, Inc.: 2017; Vol. 30; pp 4299-4307.

34.Ouyang, L.; Wu, J.; Jiang, X.; Almeida, D.; Wainwright, C.; Mishkin, P.; Zhang, C.; Agarwal, S.; Slama, K.; Ray, A.; Schulman, J.; Hilton, J.; Kelton, F.; Miller, L.; Simens, M.; Askell, A.; Welinder, P.; Christiano, P. F.; Leike, J.; Lowe, R. Training language models to follow instructions with human feedback. In Advances in Neural Information Processing Systems, 2022; Curran Associates, Inc.: 2022; Vol. 35; pp 27730-27744.

35.Georgoulis, E.; Zervou, M. A.; Pantazis, Y., Transfer learning on protein language models improves antimicrobial peptide classification. Scientific Reports 2025, 15, 37456.

36.Cai, J.; Yan, J.; Un, C.; Wang, Y.; Campbell-Valois, F.-X.; Siu, S. W. I., BERT-AmPEP60: A BERT-Based Transfer Learning Approach to Predict the Minimum Inhibitory Concentrations of Antimicrobial Peptides for Escherichia coli and Staphylococcus aureus. Journal of Chemical Information and Modeling 2025, 65, 3186-3202.

37.Kalliokoski, T.; Kramer, C.; Vulpetti, A.; Gedeck, P., Comparability of Mixed IC50 Data – A Statistical Analysis. PLOS ONE 2013, 8, e61007.

38.Kramer, C.; Kalliokoski, T.; Gedeck, P.; Vulpetti, A., The Experimental Uncertainty of Heterogeneous Public Ki Data. Journal of Medicinal Chemistry 2012, 55, 5165-5173.

39.Landrum, G. A.; Riniker, S., Combining IC50 or Ki Values from Different Sources Is a Source of Significant Noise. Journal of Chemical Information and Modeling 2024, 64, 1560-1567.

40.Campisi, E.; Di Liberto, E.; Barchitta, M.; Maugeri, A.; Favara, G.; Magnano San Lio, R.; Vecchi, E.; D'Ancona, F.; Agodi, A., Evaluation of preventive interventions addressing healthcare-associated infections and antimicrobial resistance: a systematic review. Journal of Hospital Infection 2026, 171, 120-136.

41.Alves, P. J.; Gryson, L.; Hajjar, J.; Lepelletier, D.; Reners, M.; Rodríguez Salazar, J.; Simon, A., Role of antiseptics in the prevention and treatment of infections in nursing homes. Journal of Hospital Infection 2023, 131, 58-69.

42.Buciński, A.; Socha, A.; Wnuk, M.; Bączek, T.; Nowaczyk, A.; Krysiński, J.; Goryński, K.; Koba, M., Artificial neural networks in prediction of antifungal activity of a series of pyridine derivatives against Candida albicans. Journal of Microbiological Methods 2009, 76, 25-29.

43.Wnuk, M.; Marszałł, M.; Zapęcka, A.; Nowaczyk, A.; Krysiński, J.; Romaszko, J.; Kawczak, P.; Bączek, T.; Buciński, A., Prediction of antimicrobial activity of imidazole derivatives by artificial neural networks. 2013, 8, 1-15.

44.Badura, A.; Krysiński, J.; Nowaczyk, A.; Buciński, A., Prediction of the antimicrobial activity of quaternary ammonium salts against Staphylococcus aureus using artificial neural networks. Arabian Journal of Chemistry 2021, 14, 103233.

45.Badura, A.; Krysiński, J.; Nowaczyk, A.; Buciński, A., Application of artificial neural networks to prediction of new substances with antimicrobial activity against Escherichia coli. Journal of Applied Microbiology 2021, 130, 40-49.

46.Badura, A.; Krysiński, J.; Nowaczyk, A.; Buciński, A., Application of artificial neural networks to the prediction of antifungal activity of imidazole derivatives against Candida albicans. Chemometrics and Intelligent Laboratory Systems 2022, 222, 104501.

47.Ramić, A.; Skočibušić, M.; Odžak, R.; Čipak Gašparović, A.; Milković, L.; Mikelić, A.; Sović, K.; Primožič, I.; Hrenar, T. Antimicrobial Activity of Quasi-Enantiomeric Cinchona Alkaloid Derivatives and Prediction Model Developed by Machine Learning. Antibiotics, 10, 659, 2021.

48.Lorenc, A.; Badura, A.; Karolak, M.; Pałkowski, Ł.; Kubik, Ł.; Skrzypczak, A.; Buciński, A., Hybrid Machine Learning Model for Dual Prediction of Antimicrobial Activity against Staphylococcus aureus and Candida albicans. Journal of Pharmaceutical Innovation 2026, 21, 174.

49.Tiihonen, A.; Cox-Vazquez, S. J.; Liang, Q.; Ragab, M.; Ren, Z.; Hartono, N. T. P.; Liu, Z.; Sun, S.; Zhou, C.; Incandela, N. C.; Limwongyut, J.; Moreland, A. S.; Jayavelu, S.; Bazan, G. C.; Buonassisi, T., Predicting Antimicrobial Activity of Conjugated Oligoelectrolyte Molecules via Machine Learning. Journal of the American Chemical Society 2021, 143, 18917-18931.

50.Hodyna, D.; Kovalishyn, V.; Rogalsky, S.; Blagodatnyi, V.; Petko, K.; Metelytsia, L., Antibacterial Activity of Imidazolium-Based Ionic Liquids Investigated by QSAR Modeling and Experimental Studies. Chem Biol Drug Des 2016, 88, 422-33.

51.Makarov, D. M.; Fadeeva, Y. A.; Safonova, E. A.; Shmukler, L. E., Predictive modeling of antibacterial activity of ionic liquids by machine learning methods. Computational Biology and Chemistry 2022, 101, 107775.

52.Ghaemi, S.; Consylman, A.; Pan, B.; Wu, A.; Petersen, A.; Chang, G.; McDonough, D.; Forman, M.; Bezold, E. L.; Wuest, W. M.; Shehu, A.; Zhao, L.; Minbiole, K. P. C., Topology-Aware Generation and Activity-Based Filtering: A Computational-Experimental Framework for Data-Scarce Quaternary Ammonium Compound Discovery. Journal of Chemical Information and Modeling 2026, 66, 3117-3128.

53.Ilin, E. A.; Frolov, N. A.; Seferyan, M. A.; Valeev, A. B.; Vinokurov, A. D.; Detusheva, E. V.; Son, E.; Medvedev, M. G.; Vereshchagin, A. N., Tackling the challenge of ML-assisted antibacterial activity prediction: One step closer to controlled quaternary ammonium compounds design via neural networks model. Bioorganic Chemistry 2025, 167, 109175.

54.Ward, M.; O'Boyle, N. M., Analysis of the structural diversity of heterocycles amongst European medicines agency approved pharmaceuticals (2014–2023). RSC Medicinal Chemistry 2025, 16, 4540-4570.

55.Fedorowicz, J.; Sączewski, J. Advances in the Synthesis of Biologically Active Quaternary Ammonium Compounds. International Journal of Molecular Sciences, 25, 4649, 2024.

56.Ma, J.; Liu, N.; Huang, M.; Wang, L.; Han, J.; Qian, H.; Che, F., Synthesis, physicochemical and antimicrobial properties of cardanol-derived quaternary ammonium compounds (QACs) with heterocyclic polar head. Journal of Molecular Liquids 2019, 294, 111669.

57.Zhou, Z.; Zhou, S.; Zhang, X.; Zeng, S.; Xu, Y.; Nie, W.; Zhou, Y.; Xu, T.; Chen, P., Quaternary Ammonium Salts: Insights into Synthesis and New Directions in Antibacterial Applications. Bioconjugate Chemistry 2023, 34, 302-325.

58.Burnett, C. L.; Bergfeld, W. F.; Belsito, D. V.; Hill, R. A.; Klaassen, C. D.; Liebler, D. C.; Marks, J. G., Jr.; Shank, R. C.; Slaga, T. J.; Snyder, P. W.; Andersen, F. A., Final report of the safety assessment of Kojic acid as used in cosmetics. Int J Toxicol 2010, 29, 244s-73.

59.Aati, H. Y.; Lotfy, M. M.; Al-tweel, A.; Al-enezi, B.; Abdelkader, K.; AbouZid, S. F.; Rateb, M. E.; Hassan, H. M.; Mohammed, R.; El Amir, D., Kojic acid: A River Nile-derived fungal secondary metabolite with preservative potential against Listeria monocytogenes in milk. Microbial Pathogenesis 2025, 204, 107532.

60.Wu, Y.; Shi, Y. G.; Zeng, L. Y.; Pan, Y.; Huang, X. Y.; Bian, L. Q.; Zhu, Y. J.; Zhang, R. R.; Zhang, J., Evaluation of antibacterial and anti-biofilm properties of kojic acid against five food-related bacteria and related subcellular mechanisms of bacterial inactivation. Food Sci Technol Int 2019, 25, 3-15.

61.Sie, C.; Ngaini, Z.; Suhaili, N.; Madiahlagan, E., Synthesis of Kojic Ester Derivatives as Potential Antibacterial Agent. Journal of Chemistry 2018, 2018, 1-7.

62.Aytemir, M. D.; Özçelik, B., A study of cytotoxicity of novel chlorokojic acid derivatives with their antimicrobial and antiviral activities. European Journal of Medicinal Chemistry 2010, 45, 4089-4095.

63.Emami, S.; Ghafouri, E.; Faramarzi, M. A.; Samadi, N.; Irannejad, H.; Foroumadi, A., Mannich bases of 7-piperazinylquinolones and kojic acid derivatives: Synthesis, in vitro antibacterial activity and in silico study. European Journal of Medicinal Chemistry 2013, 68, 185-191.

64.Liu, X.; Xia, W.; Jiang, Q.; Xu, Y.; Yu, P., Effect of kojic acid-grafted-chitosan oligosaccharides as a novel antibacterial agent on cell membrane of gram-positive and gram-negative bacteria. Journal of Bioscience and Bioengineering 2015, 120, 335-339.

65.Liu, X.; Xia, W.; Jiang, Q.; Xu, Y.; Yu, P., Synthesis, Characterization, and Antimicrobial Activity of Kojic Acid Grafted Chitosan Oligosaccharide. Journal of Agricultural and Food Chemistry 2014, 62, 297-303.

66.Vereshchagin, A. N.; Frolov, N. A.; Minaeva, A. P.; Detusheva, E. V.; Derkach, Y. V.; Egorov, M. P., Synthesis and biological evaluation of novel cyanuric acid-tethered tris-pyridinium derivatives. Mendeleev Communications 2021, 31, 368-369.

67.Mateeva, N. N.; Winfield, L. L.; Redda, K. K., The chemistry and pharmacology of tetrahydropyridines. Curr Med Chem 2005, 12, 551-71.

68.Khan, M. M.; Faiz, F. A.; Khan, M. S., Tetrahydropyridines: a recent update for their multicomponent synthesis. RSC Advances 2026, 16, 2007-2029.

69.Vereshchagin, A. N.; Iliyasov, T. M.; Karpenko, K. A.; Akchurin, R. N.; Minyaev, M. E. Tetrahydropyridines’ Stereoselective Formation, How Lockdown Assisted in the Identification of the Features of Its Mechanism. Molecules, 27, 4367, 2022.

70.Tekin, K.; Hao, N.; Karagoz, S.; Ragauskas, A. J., Ethanol: A Promising Green Solvent for the Deconstruction of Lignocellulose. ChemSusChem 2018, 11, 3559-3575.

71.Zheng, Z.; Dai, A.; Jin, Z.; Chi, Y. R.; Wu, J., Trifluoromethylpyridine: An Important Active Fragment for the Discovery of New Pesticides. Journal of Agricultural and Food Chemistry 2022, 70, 11019-11030.

72.Wang, Y.; Xu, F.; Luo, D.; Guo, S.; He, F.; Dai, A.; Song, B.; Wu, J., Synthesis of Anthranilic Diamide Derivatives Containing Moieties of Trifluoromethylpyridine and Hydrazone as Potential Anti-Viral Agents for Plants. Journal of Agricultural and Food Chemistry 2019, 67, 13344-13352.

73.Ponomarenko, O. V.; Panshina, S. Y.; Bakibaev, A. A.; Erkasov, R. S.; Kenzhebaj, M. S.; Montaeva, A. S., Glycoluril and Its Chemical Properties. EURASIAN JOURNAL OF CHEMISTRY 2023, 28.

74.Kravchenko, A. N.; Baranov, V. V.; Gazieva, G. A., Synthesis of glycolurils and their analogues. Russian Chemical Reviews 2018, 87, 89.

75.Galochkin, A. A.; Baranov, V. V.; Hansford, K. A.; Friberg, L. I. M.; Strel'tzova, E. D.; Lipatov, E. S.; Nelyubina, Y. V.; Kravchenko, A. N., Synthesis, Structures and Antifungal Activity of Selenoglycolurils. ChemistrySelect 2023, 8, e202300765.

76.Clinical and Laboratory Standards Institute. Methods for Dilution Antimicrobial Susceptibility Tests for Bacteria That Grow Aerobically. 12th ed.; CLSI standard M07; CLSI: Wayne, PA, 2024. https://clsi.org/shop/standards/m07/.

77.Choung, O.-H.; Vianello, R.; Segler, M.; Stiefl, N.; Jiménez-Luna, J. Extracting medicinal chemistry intuition via preference machine learning. Nature Communications 2023, 14, 6651. https://doi.org/10.1038/s41467-023-42242-1.

78.Schölkopf, B.; Locatello, F.; Bauer, S.; Ke, N. R.; Kalchbrenner, N.; Goyal, A.; Bengio, Y. Towards Causal Representation Learning. 2021. https://arxiv.org/abs/2102.11107.

79.Toukach, P. V.; Arakelyan, L. A.; Egorova, K. S. ILToxDB: A Database on Cytotoxicity of Ionic Liquids. Environmental Science & Technology Letters 2025, 12, 1631–1635. https://doi.org/10.1021/acs.estlett.5c00860.

80.Cai, F.; Zacour, K.; Zhu, T.; et al. ChemFM as a scaling law guided foundation model pre-trained on informative chemicals. Communications Chemistry 2026, 9, 3 (published online 18 December 2025). https://doi.org/10.1038/s42004-025-01793-8.

81.Singh, R.; Barsainyan, A. A.; Irfan, R.; et al. ChemBERTa-3: an open source training framework for chemical foundation models. Digital Discovery 2026, 5, 662–685. https://doi.org/10.1039/D5DD00348B.

S18. Matched partial MolFormer fine-tuning

This exploratory extension uses the same 681 source molecules, 377/304 source partition, strict target-cation exclusions and target folds as the pooled matched frozen-feature panel. Six supervision arms, five paired seeds, float32 and 30 fixed epochs are used. All 360-update final checkpoints are evaluated, without early stopping. The task-scoped protocol, checksums, paired initialisations and minibatch hashes, epoch losses, full predictions and independent audits are in reproducibility/revision_v12. Original trainable-parameter checkpoints remain on the provided compute server, with their immutable hashes and locations in training.csv. Native MolFormer refreshes feature-map buffers during training. A separate forward-RNG replay recovers final persistent buffers and writes reconstruction checkpoints without overwriting the original files; all 30 reconstructions reproduce saved target features and direct scores. Their checksums and numerical audits are in analysis/checkpoint_reconstruction.csv. Restore frozen parameters from the pinned base checkpoint and load the saved trained parameters plus final buffers. The original protocol and its dated implementation clarification are both archived.

S18.1. All target-refit and direct-transfer outcomes

Table S11. Complete matched partial-fine-tuning target-refit results. Mean ± source-seed SD; the raw representation has a single fixed decoder run. QAC-104 and Q-HERO-405 use scaffold CV, while OOD-17 uses the QAC-trained decoder. RMSE is in log2 µM.

| Target | Arm | Seeds | R² | RMSE |
| --- | --- | --- | --- | --- |
| OOD-17 | expert | 5 | -0.118 ± 0.218 | 1.731 ± 0.178 |
| Q-HERO-405 | expert | 5 | 0.205 ± 0.031 | 1.529 ± 0.030 |
| QAC-104 | expert | 5 | -0.103 ± 0.043 | 2.008 ± 0.040 |
| OOD-17 | expert-shuffled | 5 | -0.207 ± 0.087 | 1.805 ± 0.064 |
| Q-HERO-405 | expert-shuffled | 5 | 0.056 ± 0.048 | 1.666 ± 0.042 |
| QAC-104 | expert-shuffled | 5 | -0.125 ± 0.056 | 2.029 ± 0.051 |
| OOD-17 | quant-binary | 5 | -0.382 ± 0.268 | 1.926 ± 0.181 |
| Q-HERO-405 | quant-binary | 5 | 0.209 ± 0.015 | 1.525 ± 0.014 |
| QAC-104 | quant-binary | 5 | -0.069 ± 0.098 | 1.976 ± 0.091 |
| OOD-17 | quant-binary-shuffled | 5 | -0.245 ± 0.330 | 1.822 ± 0.243 |
| Q-HERO-405 | quant-binary-shuffled | 5 | 0.062 ± 0.091 | 1.659 ± 0.082 |
| QAC-104 | quant-binary-shuffled | 5 | -0.118 ± 0.120 | 2.021 ± 0.111 |
| OOD-17 | quant-continuous | 5 | -0.122 ± 0.042 | 1.741 ± 0.033 |
| Q-HERO-405 | quant-continuous | 5 | 0.282 ± 0.016 | 1.453 ± 0.016 |
| QAC-104 | quant-continuous | 5 | -0.034 ± 0.055 | 1.944 ± 0.053 |
| OOD-17 | quant-shuffled | 5 | -0.027 ± 0.067 | 1.665 ± 0.053 |
| Q-HERO-405 | quant-shuffled | 5 | 0.133 ± 0.047 | 1.596 ± 0.044 |
| QAC-104 | quant-shuffled | 5 | -0.102 ± 0.044 | 2.008 ± 0.040 |
| OOD-17 | raw-molformer | 1 | -0.067 | 1.698 |
| Q-HERO-405 | raw-molformer | 1 | 0.122 | 1.607 |
| QAC-104 | raw-molformer | 1 | -0.177 | 2.075 |

Table S12. Direct source-only predictions, without target fitting or recalibration. Rank agreement and AUC are seed means; binary logits have no direct concentration calibration. Continuous-MIC raw R² and RMSE are retained in direct_metrics.csv, including negative R² values.

| Target | Arm | Rank agreement ± SD | AUC | Raw R² / RMSE |
| --- | --- | --- | --- | --- |
| OOD-17 | expert | 0.667 ± 0.120 | 0.861 | — |
| Q-HERO-405 | expert | 0.197 ± 0.020 | 0.554 | — |
| QAC-104 | expert | 0.227 ± 0.063 | 0.652 | — |
| OOD-17 | expert-shuffled | 0.215 ± 0.340 | 0.608 | — |
| Q-HERO-405 | expert-shuffled | 0.039 ± 0.095 | 0.548 | — |
| QAC-104 | expert-shuffled | -0.016 ± 0.117 | 0.504 | — |
| OOD-17 | quant-binary | 0.588 ± 0.136 | 0.869 | — |
| Q-HERO-405 | quant-binary | 0.287 ± 0.022 | 0.612 | — |
| QAC-104 | quant-binary | 0.307 ± 0.067 | 0.707 | — |
| OOD-17 | quant-binary-shuffled | 0.197 ± 0.248 | 0.592 | — |
| Q-HERO-405 | quant-binary-shuffled | -0.026 ± 0.146 | 0.485 | — |
| QAC-104 | quant-binary-shuffled | 0.005 ± 0.230 | 0.525 | — |
| OOD-17 | quant-continuous | 0.399 ± 0.192 | 0.675 | -4.561 / 3.870 |
| Q-HERO-405 | quant-continuous | 0.326 ± 0.060 | 0.645 | -3.394 / 3.592 |
| QAC-104 | quant-continuous | 0.164 ± 0.030 | 0.626 | -2.471 / 3.548 |
| OOD-17 | quant-shuffled | 0.003 ± 0.283 | 0.469 | -7.046 / 4.641 |
| Q-HERO-405 | quant-shuffled | 0.014 ± 0.084 | 0.526 | -6.457 / 4.672 |
| QAC-104 | quant-shuffled | -0.171 ± 0.142 | 0.429 | -5.327 / 4.809 |

S18.2. Paired contrasts and adaptation sensitivity

Table S13. Matched supervision RMSE contrasts. Nested seed/scaffold 95% intervals are exploratory, unadjusted and conditional on fixed target folds. The adaptation comparison also changes architecture, optimisation and computing environment.

| Target | Comparison | Difference | 95% lower | 95% upper |
| --- | --- | --- | --- | --- |
| OOD-17 | expert minus expert-shuffled | -0.068 | -0.255 | +0.125 |
| OOD-17 | expert minus raw-molformer | +0.040 | -0.134 | +0.268 |
| OOD-17 | expert minus quant-continuous | -0.003 | -0.236 | +0.244 |
| OOD-17 | expert minus quant-binary | -0.194 | -0.446 | +0.016 |
| OOD-17 | quant-continuous minus quant-shuffled | +0.075 | -0.088 | +0.234 |
| OOD-17 | quant-binary minus quant-binary-shuffled | +0.098 | -0.151 | +0.366 |
| OOD-17 | quant-continuous minus raw-molformer | +0.043 | -0.050 | +0.153 |
| OOD-17 | quant-binary minus raw-molformer | +0.234 | +0.022 | +0.471 |
| Q-HERO-405 | expert minus expert-shuffled | -0.137 | -0.275 | -0.055 |
| Q-HERO-405 | expert minus raw-molformer | -0.078 | -0.189 | +0.001 |
| Q-HERO-405 | expert minus quant-continuous | +0.076 | +0.011 | +0.143 |
| Q-HERO-405 | expert minus quant-binary | +0.004 | -0.056 | +0.097 |
| Q-HERO-405 | quant-continuous minus quant-shuffled | -0.144 | -0.284 | -0.069 |
| Q-HERO-405 | quant-binary minus quant-binary-shuffled | -0.136 | -0.304 | -0.024 |
| Q-HERO-405 | quant-continuous minus raw-molformer | -0.154 | -0.262 | -0.079 |
| Q-HERO-405 | quant-binary minus raw-molformer | -0.082 | -0.235 | +0.006 |
| QAC-104 | expert minus expert-shuffled | -0.020 | -0.175 | +0.130 |
| QAC-104 | expert minus raw-molformer | -0.066 | -0.228 | +0.126 |
| QAC-104 | expert minus quant-continuous | +0.064 | -0.074 | +0.218 |
| QAC-104 | expert minus quant-binary | +0.031 | -0.098 | +0.199 |
| QAC-104 | quant-continuous minus quant-shuffled | -0.063 | -0.190 | +0.039 |
| QAC-104 | quant-binary minus quant-binary-shuffled | -0.046 | -0.217 | +0.100 |
| QAC-104 | quant-continuous minus raw-molformer | -0.130 | -0.264 | -0.004 |
| QAC-104 | quant-binary minus raw-molformer | -0.098 | -0.260 | +0.043 |

Table S14. Partial fine-tuning minus archived frozen-feature MLP RMSE. Nested seed/scaffold 95% intervals are exploratory, unadjusted and conditional on fixed target folds. The adaptation comparison also changes architecture, optimisation and computing environment.

| Target | Comparison | Difference | 95% lower | 95% upper |
| --- | --- | --- | --- | --- |
| OOD-17 | ft-expert minus mlp-expert | -0.106 | -0.509 | +0.304 |
| OOD-17 | ft-quant-continuous minus mlp-quant-continuous | -0.251 | -0.532 | +0.039 |
| Q-HERO-405 | ft-expert minus mlp-expert | -0.078 | -0.225 | +0.023 |
| Q-HERO-405 | ft-quant-continuous minus mlp-quant-continuous | -0.045 | -0.143 | +0.009 |
| QAC-104 | ft-expert minus mlp-expert | -0.198 | -0.368 | -0.016 |
| QAC-104 | ft-quant-continuous minus mlp-quant-continuous | -0.088 | -0.238 | +0.044 |

Table S15. Matched direct rank-agreement contrasts. Nested seed/scaffold 95% intervals are exploratory, unadjusted and conditional on fixed target folds. The adaptation comparison also changes architecture, optimisation and computing environment.

| Target | Comparison | Difference | 95% lower | 95% upper |
| --- | --- | --- | --- | --- |
| OOD-17 | expert minus expert-shuffled | +0.452 | -0.100 | +0.981 |
| OOD-17 | expert minus quant-continuous | +0.268 | -0.167 | +0.590 |
| OOD-17 | expert minus quant-binary | +0.079 | -0.095 | +0.335 |
| OOD-17 | quant-continuous minus quant-shuffled | +0.396 | -0.028 | +1.009 |
| OOD-17 | quant-binary minus quant-binary-shuffled | +0.391 | +0.025 | +0.970 |
| Q-HERO-405 | expert minus expert-shuffled | +0.159 | -0.001 | +0.429 |
| Q-HERO-405 | expert minus quant-continuous | -0.129 | -0.239 | -0.004 |
| Q-HERO-405 | expert minus quant-binary | -0.090 | -0.179 | +0.006 |
| Q-HERO-405 | quant-continuous minus quant-shuffled | +0.312 | +0.172 | +0.516 |
| Q-HERO-405 | quant-binary minus quant-binary-shuffled | +0.313 | +0.121 | +0.576 |
| QAC-104 | expert minus expert-shuffled | +0.243 | -0.142 | +0.606 |
| QAC-104 | expert minus quant-continuous | +0.063 | -0.115 | +0.221 |
| QAC-104 | expert minus quant-binary | -0.081 | -0.277 | +0.095 |
| QAC-104 | quant-continuous minus quant-shuffled | +0.335 | -0.078 | +0.730 |
| QAC-104 | quant-binary minus quant-binary-shuffled | +0.302 | -0.002 | +0.680 |

S18.3. Numerical reproduction and training diagnostics

QAC-104: fresh-versus-archived raw feature maximum absolute difference 4.29153e-06, mean absolute difference 3.71091e-07. The same-environment fresh raw representation is the primary matched fine-tuning reference. Archived raw predictions and frozen-feature results are retained rather than silently substituted.

Q-HERO-405: fresh-versus-archived raw feature maximum absolute difference 3.8147e-06, mean absolute difference 3.7107e-07. The same-environment fresh raw representation is the primary matched fine-tuning reference. Archived raw predictions and frozen-feature results are retained rather than silently substituted.

OOD-17: fresh-versus-archived raw feature maximum absolute difference 2.38419e-06, mean absolute difference 3.58518e-07. The same-environment fresh raw representation is the primary matched fine-tuning reference. Archived raw predictions and frozen-feature results are retained rather than silently substituted.


Figure S21. Source-validation losses for matched partial fine-tuning. Thin curves are the five source seeds and thick curves their means. Binary BCE and standardised continuous-MIC MSE occupy separate panels. Validation is diagnostic only: all arms use their final 30-epoch checkpoint.


Figure S22. Matched partial-fine-tuning absolute-error distributions on the same 405 Q-HERO structures. (a) Split violins for human and continuous-MIC supervision, with median and IQR. (b) Paired within-structure absolute-error differences. Absolute errors are averaged across the five source seeds. These are descriptive distributions; they do not establish measurement equivalence or independent-record significance.

S19. Original-cohort four-endpoint evaluation

All new concentration metrics use log2 mg/L. Cation-held-out QAC-105 CV is an interpolation test and permits scaffold overlap. The follow-up scaffold-held-out QAC-105 uses all 29 scaffold families. OOD-17 uses a decoder trained on the 105 structures only. Human annotation fields remain in main Section 4.1; chemical field C1 and source procedures remain in S16. All protocols, hashes, model snapshots, folds, per-seed predictions and reviews are in revision_v14.

Table S16. Endpoint-specific results for all new primary and historical configurations. Trained arms are mean ± source-seed SD. Legacy arms overlap the original target in representation learning and are descriptive; they are segregated by provenance. OOD E. coli MBC uses 16 exact observations; its one bound is retained separately.

Provenance: matched-source-excluded

| Cohort / task | Arm / encoding | Seeds / n | RMSE ± SD | R² ± SD |
| --- | --- | --- | --- | --- |
| OOD17 / Ec_MBC | expert / onehot | 5 / 16 | 2.195 ± 0.133 | -0.235 ± 0.150 |
| OOD17 / Ec_MIC | expert / onehot | 5 / 17 | 2.074 ± 0.171 | -0.306 ± 0.213 |
| OOD17 / Sa_MBC | expert / onehot | 5 / 17 | 2.066 ± 0.119 | 0.045 ± 0.112 |
| OOD17 / Sa_MIC | expert / onehot | 5 / 17 | 1.868 ± 0.148 | -0.147 ± 0.181 |
| QAC105 / Ec_MBC | expert / onehot | 5 / 105 | 1.763 ± 0.055 | 0.288 ± 0.045 |
| QAC105 / Ec_MIC | expert / onehot | 5 / 105 | 1.640 ± 0.051 | 0.307 ± 0.043 |
| QAC105 / Sa_MBC | expert / onehot | 5 / 105 | 1.832 ± 0.045 | 0.129 ± 0.042 |
| QAC105 / Sa_MIC | expert / onehot | 5 / 105 | 1.707 ± 0.025 | 0.241 ± 0.022 |
| OOD17 / Ec_MBC | expert / text | 5 / 16 | 2.266 ± 0.187 | -0.320 ± 0.216 |
| OOD17 / Ec_MIC | expert / text | 5 / 17 | 2.149 ± 0.224 | -0.407 ± 0.285 |
| OOD17 / Sa_MBC | expert / text | 5 / 17 | 2.094 ± 0.121 | 0.019 ± 0.111 |
| OOD17 / Sa_MIC | expert / text | 5 / 17 | 1.903 ± 0.099 | -0.187 ± 0.122 |
| QAC105 / Ec_MBC | expert / text | 5 / 105 | 1.756 ± 0.040 | 0.294 ± 0.032 |
| QAC105 / Ec_MIC | expert / text | 5 / 105 | 1.617 ± 0.028 | 0.326 ± 0.023 |
| QAC105 / Sa_MBC | expert / text | 5 / 105 | 1.803 ± 0.020 | 0.157 ± 0.019 |
| QAC105 / Sa_MIC | expert / text | 5 / 105 | 1.708 ± 0.023 | 0.240 ± 0.020 |
| OOD17 / Ec_MBC | expert-shuffled / onehot | 5 / 16 | 2.557 ± 0.157 | -0.676 ± 0.211 |
| OOD17 / Ec_MIC | expert-shuffled / onehot | 5 / 17 | 2.637 ± 0.154 | -1.106 ± 0.249 |
| OOD17 / Sa_MBC | expert-shuffled / onehot | 5 / 17 | 2.217 ± 0.086 | -0.098 ± 0.086 |
| OOD17 / Sa_MIC | expert-shuffled / onehot | 5 / 17 | 1.865 ± 0.112 | -0.140 ± 0.138 |
| QAC105 / Ec_MBC | expert-shuffled / onehot | 5 / 105 | 1.929 ± 0.048 | 0.147 ± 0.042 |
| QAC105 / Ec_MIC | expert-shuffled / onehot | 5 / 105 | 1.776 ± 0.037 | 0.187 ± 0.034 |
| QAC105 / Sa_MBC | expert-shuffled / onehot | 5 / 105 | 1.923 ± 0.047 | 0.041 ± 0.047 |
| QAC105 / Sa_MIC | expert-shuffled / onehot | 5 / 105 | 1.796 ± 0.034 | 0.159 ± 0.033 |
| OOD17 / Ec_MBC | quant-binary / onehot | 5 / 16 | 2.137 ± 0.184 | -0.175 ± 0.208 |
| OOD17 / Ec_MIC | quant-binary / onehot | 5 / 17 | 2.003 ± 0.164 | -0.219 ± 0.199 |
| OOD17 / Sa_MBC | quant-binary / onehot | 5 / 17 | 2.214 ± 0.184 | -0.099 ± 0.186 |
| OOD17 / Sa_MIC | quant-binary / onehot | 5 / 17 | 2.024 ± 0.071 | -0.341 ± 0.093 |
| QAC105 / Ec_MBC | quant-binary / onehot | 5 / 105 | 1.841 ± 0.049 | 0.223 ± 0.041 |
| QAC105 / Ec_MIC | quant-binary / onehot | 5 / 105 | 1.706 ± 0.048 | 0.250 ± 0.042 |
| QAC105 / Sa_MBC | quant-binary / onehot | 5 / 105 | 1.925 ± 0.076 | 0.038 ± 0.075 |
| QAC105 / Sa_MIC | quant-binary / onehot | 5 / 105 | 1.741 ± 0.092 | 0.208 ± 0.083 |
| OOD17 / Ec_MBC | quant-binary / text | 5 / 16 | 2.206 ± 0.124 | -0.247 ± 0.140 |
| OOD17 / Ec_MIC | quant-binary / text | 5 / 17 | 2.024 ± 0.183 | -0.246 ± 0.229 |
| OOD17 / Sa_MBC | quant-binary / text | 5 / 17 | 2.222 ± 0.162 | -0.106 ± 0.162 |
| OOD17 / Sa_MIC | quant-binary / text | 5 / 17 | 1.981 ± 0.118 | -0.286 ± 0.158 |
| QAC105 / Ec_MBC | quant-binary / text | 5 / 105 | 1.842 ± 0.067 | 0.222 ± 0.057 |
| QAC105 / Ec_MIC | quant-binary / text | 5 / 105 | 1.716 ± 0.063 | 0.241 ± 0.056 |
| QAC105 / Sa_MBC | quant-binary / text | 5 / 105 | 1.895 ± 0.087 | 0.067 ± 0.084 |
| QAC105 / Sa_MIC | quant-binary / text | 5 / 105 | 1.703 ± 0.074 | 0.244 ± 0.065 |
| OOD17 / Ec_MBC | quant-binary-shuffled / onehot | 5 / 16 | 2.558 ± 0.130 | -0.676 ± 0.169 |
| OOD17 / Ec_MIC | quant-binary-shuffled / onehot | 5 / 17 | 2.619 ± 0.144 | -1.076 ± 0.227 |
| OOD17 / Sa_MBC | quant-binary-shuffled / onehot | 5 / 17 | 2.318 ± 0.178 | -0.204 ± 0.187 |
| OOD17 / Sa_MIC | quant-binary-shuffled / onehot | 5 / 17 | 1.938 ± 0.303 | -0.251 ± 0.407 |
| QAC105 / Ec_MBC | quant-binary-shuffled / onehot | 5 / 105 | 1.996 ± 0.083 | 0.086 ± 0.077 |
| QAC105 / Ec_MIC | quant-binary-shuffled / onehot | 5 / 105 | 1.845 ± 0.078 | 0.122 ± 0.074 |
| QAC105 / Sa_MBC | quant-binary-shuffled / onehot | 5 / 105 | 1.918 ± 0.088 | 0.044 ± 0.085 |
| QAC105 / Sa_MIC | quant-binary-shuffled / onehot | 5 / 105 | 1.791 ± 0.084 | 0.163 ± 0.076 |
| OOD17 / Ec_MBC | quant-continuous / onehot | 5 / 16 | 2.477 ± 0.069 | -0.569 ± 0.087 |
| OOD17 / Ec_MIC | quant-continuous / onehot | 5 / 17 | 2.448 ± 0.103 | -0.813 ± 0.152 |
| OOD17 / Sa_MBC | quant-continuous / onehot | 5 / 17 | 2.119 ± 0.101 | -0.004 ± 0.094 |
| OOD17 / Sa_MIC | quant-continuous / onehot | 5 / 17 | 1.852 ± 0.154 | -0.127 ± 0.183 |
| QAC105 / Ec_MBC | quant-continuous / onehot | 5 / 105 | 1.735 ± 0.041 | 0.310 ± 0.032 |
| QAC105 / Ec_MIC | quant-continuous / onehot | 5 / 105 | 1.615 ± 0.051 | 0.327 ± 0.042 |
| QAC105 / Sa_MBC | quant-continuous / onehot | 5 / 105 | 1.831 ± 0.055 | 0.129 ± 0.052 |
| QAC105 / Sa_MIC | quant-continuous / onehot | 5 / 105 | 1.669 ± 0.052 | 0.274 ± 0.046 |
| OOD17 / Ec_MBC | quant-continuous / text | 5 / 16 | 2.503 ± 0.188 | -0.609 ± 0.238 |
| OOD17 / Ec_MIC | quant-continuous / text | 5 / 17 | 2.382 ± 0.260 | -0.731 ± 0.366 |
| OOD17 / Sa_MBC | quant-continuous / text | 5 / 17 | 2.150 ± 0.014 | -0.032 ± 0.013 |
| OOD17 / Sa_MIC | quant-continuous / text | 5 / 17 | 1.891 ± 0.104 | -0.172 ± 0.129 |
| QAC105 / Ec_MBC | quant-continuous / text | 5 / 105 | 1.750 ± 0.056 | 0.298 ± 0.045 |
| QAC105 / Ec_MIC | quant-continuous / text | 5 / 105 | 1.637 ± 0.076 | 0.309 ± 0.064 |
| QAC105 / Sa_MBC | quant-continuous / text | 5 / 105 | 1.825 ± 0.068 | 0.135 ± 0.064 |
| QAC105 / Sa_MIC | quant-continuous / text | 5 / 105 | 1.676 ± 0.052 | 0.268 ± 0.045 |
| OOD17 / Ec_MBC | quant-shuffled / onehot | 5 / 16 | 2.486 ± 0.072 | -0.582 ± 0.091 |
| OOD17 / Ec_MIC | quant-shuffled / onehot | 5 / 17 | 2.536 ± 0.114 | -0.946 ± 0.174 |
| OOD17 / Sa_MBC | quant-shuffled / onehot | 5 / 17 | 2.163 ± 0.119 | -0.046 ± 0.114 |
| OOD17 / Sa_MIC | quant-shuffled / onehot | 5 / 17 | 1.869 ± 0.083 | -0.144 ± 0.102 |
| QAC105 / Ec_MBC | quant-shuffled / onehot | 5 / 105 | 1.971 ± 0.048 | 0.110 ± 0.043 |
| QAC105 / Ec_MIC | quant-shuffled / onehot | 5 / 105 | 1.809 ± 0.053 | 0.156 ± 0.049 |
| QAC105 / Sa_MBC | quant-shuffled / onehot | 5 / 105 | 1.909 ± 0.036 | 0.054 ± 0.035 |
| QAC105 / Sa_MIC | quant-shuffled / onehot | 5 / 105 | 1.791 ± 0.030 | 0.164 ± 0.028 |
| OOD17 / Ec_MBC | raw-molformer / onehot | 1 / 16 | 2.498 ± 0.000 | -0.595 ± 0.000 |
| OOD17 / Ec_MIC | raw-molformer / onehot | 1 / 17 | 2.562 ± 0.000 | -0.983 ± 0.000 |
| OOD17 / Sa_MBC | raw-molformer / onehot | 1 / 17 | 2.071 ± 0.000 | 0.044 ± 0.000 |
| OOD17 / Sa_MIC | raw-molformer / onehot | 1 / 17 | 1.871 ± 0.000 | -0.144 ± 0.000 |
| QAC105 / Ec_MBC | raw-molformer / onehot | 1 / 105 | 1.939 ± 0.000 | 0.139 ± 0.000 |
| QAC105 / Ec_MIC | raw-molformer / onehot | 1 / 105 | 1.800 ± 0.000 | 0.165 ± 0.000 |
| QAC105 / Sa_MBC | raw-molformer / onehot | 1 / 105 | 1.921 ± 0.000 | 0.043 ± 0.000 |
| QAC105 / Sa_MIC | raw-molformer / onehot | 1 / 105 | 1.768 ± 0.000 | 0.186 ± 0.000 |
| OOD17 / Ec_MBC | raw-molformer / text | 1 / 16 | 2.187 ± 0.000 | -0.222 ± 0.000 |
| OOD17 / Ec_MIC | raw-molformer / text | 1 / 17 | 2.366 ± 0.000 | -0.691 ± 0.000 |
| OOD17 / Sa_MBC | raw-molformer / text | 1 / 17 | 2.194 ± 0.000 | -0.073 ± 0.000 |
| OOD17 / Sa_MIC | raw-molformer / text | 1 / 17 | 1.944 ± 0.000 | -0.236 ± 0.000 |
| QAC105 / Ec_MBC | raw-molformer / text | 1 / 105 | 2.000 ± 0.000 | 0.084 ± 0.000 |
| QAC105 / Ec_MIC | raw-molformer / text | 1 / 105 | 1.862 ± 0.000 | 0.107 ± 0.000 |
| QAC105 / Sa_MBC | raw-molformer / text | 1 / 105 | 1.940 ± 0.000 | 0.024 ± 0.000 |
| QAC105 / Sa_MIC | raw-molformer / text | 1 / 105 | 1.825 ± 0.000 | 0.133 ± 0.000 |

Provenance: target-training-only

| Cohort / task | Arm / encoding | Seeds / n | RMSE ± SD | R² ± SD |
| --- | --- | --- | --- | --- |
| OOD17 / Ec_MBC | task-median / baseline | 1 / 16 | 2.368 ± 0.000 | -0.433 ± 0.000 |
| OOD17 / Ec_MIC | task-median / baseline | 1 / 17 | 2.742 ± 0.000 | -1.270 ± 0.000 |
| OOD17 / Sa_MBC | task-median / baseline | 1 / 17 | 2.124 ± 0.000 | -0.007 ± 0.000 |
| OOD17 / Sa_MIC | task-median / baseline | 1 / 17 | 1.749 ± 0.000 | 0.000 ± 0.000 |
| QAC105 / Ec_MBC | task-median / baseline | 1 / 105 | 2.153 ± 0.000 | -0.062 ± 0.000 |
| QAC105 / Ec_MIC | task-median / baseline | 1 / 105 | 2.003 ± 0.000 | -0.033 ± 0.000 |
| QAC105 / Sa_MBC | task-median / baseline | 1 / 105 | 1.966 ± 0.000 | -0.002 ± 0.000 |
| QAC105 / Sa_MIC | task-median / baseline | 1 / 105 | 1.981 ± 0.000 | -0.022 ± 0.000 |

Provenance: legacy-overlapping-source

| Cohort / task | Arm / encoding | Seeds / n | RMSE ± SD | R² ± SD |
| --- | --- | --- | --- | --- |
| OOD17 / Ec_MBC | legacy-human / onehot | 1 / 16 | 2.282 ± 0.000 | -0.332 ± 0.000 |
| OOD17 / Ec_MIC | legacy-human / onehot | 1 / 17 | 2.318 ± 0.000 | -0.624 ± 0.000 |
| OOD17 / Sa_MBC | legacy-human / onehot | 1 / 17 | 2.113 ± 0.000 | 0.004 ± 0.000 |
| OOD17 / Sa_MIC | legacy-human / onehot | 1 / 17 | 1.694 ± 0.000 | 0.062 ± 0.000 |
| QAC105 / Ec_MBC | legacy-human / onehot | 1 / 105 | 1.964 ± 0.000 | 0.116 ± 0.000 |
| QAC105 / Ec_MIC | legacy-human / onehot | 1 / 105 | 1.845 ± 0.000 | 0.124 ± 0.000 |
| QAC105 / Sa_MBC | legacy-human / onehot | 1 / 105 | 2.004 ± 0.000 | -0.042 ± 0.000 |
| QAC105 / Sa_MIC | legacy-human / onehot | 1 / 105 | 1.843 ± 0.000 | 0.116 ± 0.000 |
| OOD17 / Ec_MBC | legacy-human / separate | 1 / 16 | 2.256 ± 0.000 | -0.300 ± 0.000 |
| OOD17 / Ec_MIC | legacy-human / separate | 1 / 17 | 2.169 ± 0.000 | -0.421 ± 0.000 |
| OOD17 / Sa_MBC | legacy-human / separate | 1 / 17 | 2.057 ± 0.000 | 0.056 ± 0.000 |
| OOD17 / Sa_MIC | legacy-human / separate | 1 / 17 | 1.769 ± 0.000 | -0.023 ± 0.000 |
| QAC105 / Ec_MBC | legacy-human / separate | 1 / 105 | 2.013 ± 0.000 | 0.072 ± 0.000 |
| QAC105 / Ec_MIC | legacy-human / separate | 1 / 105 | 1.893 ± 0.000 | 0.077 ± 0.000 |
| QAC105 / Sa_MBC | legacy-human / separate | 1 / 105 | 2.006 ± 0.000 | -0.044 ± 0.000 |
| QAC105 / Sa_MIC | legacy-human / separate | 1 / 105 | 1.800 ± 0.000 | 0.156 ± 0.000 |
| OOD17 / Ec_MBC | legacy-human / text | 1 / 16 | 2.295 ± 0.000 | -0.347 ± 0.000 |
| OOD17 / Ec_MIC | legacy-human / text | 1 / 17 | 2.227 ± 0.000 | -0.498 ± 0.000 |
| OOD17 / Sa_MBC | legacy-human / text | 1 / 17 | 1.976 ± 0.000 | 0.129 ± 0.000 |
| OOD17 / Sa_MIC | legacy-human / text | 1 / 17 | 1.688 ± 0.000 | 0.068 ± 0.000 |
| QAC105 / Ec_MBC | legacy-human / text | 1 / 105 | 2.004 ± 0.000 | 0.080 ± 0.000 |
| QAC105 / Ec_MIC | legacy-human / text | 1 / 105 | 1.880 ± 0.000 | 0.090 ± 0.000 |
| QAC105 / Sa_MBC | legacy-human / text | 1 / 105 | 2.031 ± 0.000 | -0.070 ± 0.000 |
| QAC105 / Sa_MIC | legacy-human / text | 1 / 105 | 1.820 ± 0.000 | 0.138 ± 0.000 |
| OOD17 / Ec_MBC | legacy-quantitative / onehot | 1 / 16 | 2.676 ± 0.000 | -0.831 ± 0.000 |
| OOD17 / Ec_MIC | legacy-quantitative / onehot | 1 / 17 | 2.751 ± 0.000 | -1.286 ± 0.000 |
| OOD17 / Sa_MBC | legacy-quantitative / onehot | 1 / 17 | 2.190 ± 0.000 | -0.069 ± 0.000 |
| OOD17 / Sa_MIC | legacy-quantitative / onehot | 1 / 17 | 1.659 ± 0.000 | 0.100 ± 0.000 |
| QAC105 / Ec_MBC | legacy-quantitative / onehot | 1 / 105 | 1.956 ± 0.000 | 0.124 ± 0.000 |
| QAC105 / Ec_MIC | legacy-quantitative / onehot | 1 / 105 | 1.775 ± 0.000 | 0.188 ± 0.000 |
| QAC105 / Sa_MBC | legacy-quantitative / onehot | 1 / 105 | 1.901 ± 0.000 | 0.063 ± 0.000 |
| QAC105 / Sa_MIC | legacy-quantitative / onehot | 1 / 105 | 1.707 ± 0.000 | 0.241 ± 0.000 |
| OOD17 / Ec_MBC | legacy-quantitative / separate | 1 / 16 | 2.647 ± 0.000 | -0.791 ± 0.000 |
| OOD17 / Ec_MIC | legacy-quantitative / separate | 1 / 17 | 2.546 ± 0.000 | -0.958 ± 0.000 |
| OOD17 / Sa_MBC | legacy-quantitative / separate | 1 / 17 | 2.262 ± 0.000 | -0.142 ± 0.000 |
| OOD17 / Sa_MIC | legacy-quantitative / separate | 1 / 17 | 1.693 ± 0.000 | 0.063 ± 0.000 |
| QAC105 / Ec_MBC | legacy-quantitative / separate | 1 / 105 | 1.997 ± 0.000 | 0.086 ± 0.000 |
| QAC105 / Ec_MIC | legacy-quantitative / separate | 1 / 105 | 1.775 ± 0.000 | 0.188 ± 0.000 |
| QAC105 / Sa_MBC | legacy-quantitative / separate | 1 / 105 | 1.954 ± 0.000 | 0.009 ± 0.000 |
| QAC105 / Sa_MIC | legacy-quantitative / separate | 1 / 105 | 1.753 ± 0.000 | 0.200 ± 0.000 |
| OOD17 / Ec_MBC | legacy-quantitative / text | 1 / 16 | 2.717 ± 0.000 | -0.887 ± 0.000 |
| OOD17 / Ec_MIC | legacy-quantitative / text | 1 / 17 | 2.657 ± 0.000 | -1.133 ± 0.000 |
| OOD17 / Sa_MBC | legacy-quantitative / text | 1 / 17 | 2.305 ± 0.000 | -0.186 ± 0.000 |
| OOD17 / Sa_MIC | legacy-quantitative / text | 1 / 17 | 1.829 ± 0.000 | -0.094 ± 0.000 |
| QAC105 / Ec_MBC | legacy-quantitative / text | 1 / 105 | 1.936 ± 0.000 | 0.141 ± 0.000 |
| QAC105 / Ec_MIC | legacy-quantitative / text | 1 / 105 | 1.768 ± 0.000 | 0.195 ± 0.000 |
| QAC105 / Sa_MBC | legacy-quantitative / text | 1 / 105 | 1.914 ± 0.000 | 0.050 ± 0.000 |
| QAC105 / Sa_MIC | legacy-quantitative / text | 1 / 105 | 1.700 ± 0.000 | 0.248 ± 0.000 |
| OOD17 / Ec_MBC | legacy-raw / onehot | 1 / 16 | 2.769 ± 0.000 | -0.960 ± 0.000 |
| OOD17 / Ec_MIC | legacy-raw / onehot | 1 / 17 | 2.738 ± 0.000 | -1.265 ± 0.000 |
| OOD17 / Sa_MBC | legacy-raw / onehot | 1 / 17 | 2.022 ± 0.000 | 0.088 ± 0.000 |
| OOD17 / Sa_MIC | legacy-raw / onehot | 1 / 17 | 1.457 ± 0.000 | 0.306 ± 0.000 |
| QAC105 / Ec_MBC | legacy-raw / onehot | 1 / 105 | 1.999 ± 0.000 | 0.085 ± 0.000 |
| QAC105 / Ec_MIC | legacy-raw / onehot | 1 / 105 | 1.839 ± 0.000 | 0.129 ± 0.000 |
| QAC105 / Sa_MBC | legacy-raw / onehot | 1 / 105 | 1.952 ± 0.000 | 0.012 ± 0.000 |
| QAC105 / Sa_MIC | legacy-raw / onehot | 1 / 105 | 1.823 ± 0.000 | 0.135 ± 0.000 |
| OOD17 / Ec_MBC | legacy-raw / separate | 1 / 16 | 2.488 ± 0.000 | -0.583 ± 0.000 |
| OOD17 / Ec_MIC | legacy-raw / separate | 1 / 17 | 2.552 ± 0.000 | -0.967 ± 0.000 |
| OOD17 / Sa_MBC | legacy-raw / separate | 1 / 17 | 2.093 ± 0.000 | 0.023 ± 0.000 |
| OOD17 / Sa_MIC | legacy-raw / separate | 1 / 17 | 1.619 ± 0.000 | 0.144 ± 0.000 |
| QAC105 / Ec_MBC | legacy-raw / separate | 1 / 105 | 2.010 ± 0.000 | 0.075 ± 0.000 |
| QAC105 / Ec_MIC | legacy-raw / separate | 1 / 105 | 1.878 ± 0.000 | 0.092 ± 0.000 |
| QAC105 / Sa_MBC | legacy-raw / separate | 1 / 105 | 1.936 ± 0.000 | 0.028 ± 0.000 |
| QAC105 / Sa_MIC | legacy-raw / separate | 1 / 105 | 1.772 ± 0.000 | 0.182 ± 0.000 |
| OOD17 / Ec_MBC | legacy-raw / text | 1 / 16 | 2.761 ± 0.000 | -0.948 ± 0.000 |
| OOD17 / Ec_MIC | legacy-raw / text | 1 / 17 | 2.698 ± 0.000 | -1.198 ± 0.000 |
| OOD17 / Sa_MBC | legacy-raw / text | 1 / 17 | 1.927 ± 0.000 | 0.172 ± 0.000 |
| OOD17 / Sa_MIC | legacy-raw / text | 1 / 17 | 1.392 ± 0.000 | 0.366 ± 0.000 |
| QAC105 / Ec_MBC | legacy-raw / text | 1 / 105 | 1.994 ± 0.000 | 0.089 ± 0.000 |
| QAC105 / Ec_MIC | legacy-raw / text | 1 / 105 | 1.830 ± 0.000 | 0.138 ± 0.000 |
| QAC105 / Sa_MBC | legacy-raw / text | 1 / 105 | 1.977 ± 0.000 | -0.014 ± 0.000 |
| QAC105 / Sa_MIC | legacy-raw / text | 1 / 105 | 1.812 ± 0.000 | 0.144 ± 0.000 |

Table S17. Paired pooled-loss contrasts. Ten thousand paired seed/scaffold draws; exploratory, unadjusted and conditional on fixed predictions. OOD has four groups, so these intervals cannot supply stable population bounds. Endpoint-specific intervals are retained in analysis/contrasts.csv.

| Cohort | Comparison | ΔRMSE | 95% lower | 95% upper |
| --- | --- | --- | --- | --- |
| OOD17 | expert minus expert-shuffled | -0.282 | -0.611 | -0.024 |
| OOD17 | expert minus quant-continuous | -0.183 | -0.415 | -0.004 |
| OOD17 | expert minus quant-binary | -0.045 | -0.254 | +0.136 |
| OOD17 | expert minus raw-molformer | -0.211 | -0.514 | +0.010 |
| OOD17 | quant-continuous minus quant-shuffled | -0.040 | -0.182 | +0.092 |
| OOD17 | quant-binary minus quant-binary-shuffled | -0.273 | -0.619 | +0.023 |
| OOD17 | text minus onehot: expert | +0.053 | -0.028 | +0.165 |
| OOD17 | text minus onehot: quant-continuous | +0.006 | -0.131 | +0.112 |
| OOD17 | text minus onehot: quant-binary | +0.013 | -0.063 | +0.086 |
| OOD17 | text minus onehot: raw-molformer | -0.087 | -0.261 | +0.060 |
| QAC105 | expert minus expert-shuffled | -0.120 | -0.217 | -0.043 |
| QAC105 | expert minus quant-continuous | +0.022 | -0.053 | +0.101 |
| QAC105 | expert minus quant-binary | -0.069 | -0.157 | +0.009 |
| QAC105 | expert minus raw-molformer | -0.121 | -0.214 | -0.044 |
| QAC105 | quant-continuous minus quant-shuffled | -0.157 | -0.242 | -0.086 |
| QAC105 | quant-binary minus quant-binary-shuffled | -0.083 | -0.231 | +0.046 |
| QAC105 | text minus onehot: expert | -0.015 | -0.051 | +0.024 |
| QAC105 | text minus onehot: quant-continuous | +0.009 | -0.026 | +0.051 |
| QAC105 | text minus onehot: quant-binary | -0.015 | -0.043 | +0.013 |
| QAC105 | text minus onehot: raw-molformer | +0.050 | -0.007 | +0.110 |

Table S18. Scaffold-held-out QAC-105, full controls and all endpoints. Every structure from the same cation-scaffold family remains in one target fold. The follow-up was specified after inspection of this extension; existing source training and target hyperparameters were retained.

| Task | Arm | Seeds / n | RMSE ± SD | R² ± SD |
| --- | --- | --- | --- | --- |
| Ec_MBC | expert | 5 / 105 | 1.825 ± 0.062 | 0.236 ± 0.051 |
| Ec_MIC | expert | 5 / 105 | 1.722 ± 0.075 | 0.235 ± 0.066 |
| Sa_MBC | expert | 5 / 105 | 1.980 ± 0.020 | -0.017 ± 0.021 |
| Sa_MIC | expert | 5 / 105 | 1.829 ± 0.042 | 0.129 ± 0.040 |
| Ec_MBC | expert-shuffled | 5 / 105 | 2.007 ± 0.061 | 0.077 ± 0.056 |
| Ec_MIC | expert-shuffled | 5 / 105 | 1.907 ± 0.062 | 0.063 ± 0.061 |
| Sa_MBC | expert-shuffled | 5 / 105 | 2.022 ± 0.045 | -0.061 ± 0.047 |
| Sa_MIC | expert-shuffled | 5 / 105 | 1.913 ± 0.041 | 0.046 ± 0.040 |
| Ec_MBC | quant-binary | 5 / 105 | 1.851 ± 0.052 | 0.215 ± 0.044 |
| Ec_MIC | quant-binary | 5 / 105 | 1.766 ± 0.048 | 0.196 ± 0.044 |
| Sa_MBC | quant-binary | 5 / 105 | 1.993 ± 0.078 | -0.032 ± 0.080 |
| Sa_MIC | quant-binary | 5 / 105 | 1.806 ± 0.109 | 0.148 ± 0.099 |
| Ec_MBC | quant-binary-shuffled | 5 / 105 | 2.007 ± 0.052 | 0.076 ± 0.048 |
| Ec_MIC | quant-binary-shuffled | 5 / 105 | 1.902 ± 0.048 | 0.067 ± 0.046 |
| Sa_MBC | quant-binary-shuffled | 5 / 105 | 2.044 ± 0.128 | -0.087 ± 0.136 |
| Sa_MIC | quant-binary-shuffled | 5 / 105 | 1.904 ± 0.114 | 0.054 ± 0.112 |
| Ec_MBC | quant-continuous | 5 / 105 | 1.807 ± 0.058 | 0.251 ± 0.049 |
| Ec_MIC | quant-continuous | 5 / 105 | 1.726 ± 0.058 | 0.232 ± 0.052 |
| Sa_MBC | quant-continuous | 5 / 105 | 1.949 ± 0.027 | 0.015 ± 0.027 |
| Sa_MIC | quant-continuous | 5 / 105 | 1.767 ± 0.029 | 0.187 ± 0.027 |
| Ec_MBC | quant-shuffled | 5 / 105 | 1.971 ± 0.015 | 0.110 ± 0.014 |
| Ec_MIC | quant-shuffled | 5 / 105 | 1.859 ± 0.014 | 0.109 ± 0.013 |
| Sa_MBC | quant-shuffled | 5 / 105 | 2.030 ± 0.027 | -0.069 ± 0.029 |
| Sa_MIC | quant-shuffled | 5 / 105 | 1.916 ± 0.033 | 0.044 ± 0.033 |
| Ec_MBC | raw-molformer | 1 / 105 | 2.045 ± 0.000 | 0.042 ± 0.000 |
| Ec_MIC | raw-molformer | 1 / 105 | 1.958 ± 0.000 | 0.013 ± 0.000 |
| Sa_MBC | raw-molformer | 1 / 105 | 2.008 ± 0.000 | -0.046 ± 0.000 |
| Sa_MIC | raw-molformer | 1 / 105 | 1.896 ± 0.000 | 0.064 ± 0.000 |
| Ec_MBC | task-median | 1 / 105 | 2.113 ± 0.000 | -0.023 ± 0.000 |
| Ec_MIC | task-median | 1 / 105 | 2.004 ± 0.000 | -0.035 ± 0.000 |
| Sa_MBC | task-median | 1 / 105 | 1.966 ± 0.000 | -0.002 ± 0.000 |
| Sa_MIC | task-median | 1 / 105 | 1.981 ± 0.000 | -0.022 ± 0.000 |


Figure S23. Exact OOD endpoint parity. The right-facing triangle denotes the >500 mg/L bound for IT505 E. coli MBC; it is excluded from exact-value statistics. Displayed points average predictions across seeds, while boxes give mean seed-specific metrics. These are concentration-prediction failures as well as successes, not a prospectively blinded discovery validation.


Figure S24. Every named OOD prediction by endpoint. Diamonds are exact measurements, the upward triangle is the IT505 MBC lower bound, circles are model predictions and bars source-seed SD. Vertical separators divide the four scaffold families. The complete table and qualifiers are in analysis/OOD17_all_predictions_named.csv.


Figure S25. Cation-held-out versus scaffold-held-out original-cohort performance, by endpoint. The same source representations and one-hot decoder are used. Colours denote supervision and markers denote validation regime. Source-seed SD does not capture sampling uncertainty across chemical families.

S20. Complete original and OOD registries

Table S19. All 105 original full-salt identities and their raw row identifiers. Exact structures are in original_QAC105_structures.pdf and data/QAC105.csv; all four endpoints and their fold assignments are machine-readable. The conflicting full-salt identity retains its historical median in the 105-cohort view and is flagged. Original rows are zero-based identifiers from the workbook.

| Compound ID | Original rows | Charge | Sa MIC (mg/L) | Curation status |
| --- | --- | --- | --- | --- |
| target_39d054f801b1 | 0 | 2 | 1 | Retained |
| target_e9a452e19a6a | 1 | 2 | 4 | Retained |
| target_c803b3e79921 | 2 | 2 | 32 | Retained |
| target_cd7c8017793d | 3 | 2 | 16 | Retained |
| target_dd7e84d8a48f | 4 | 2 | 2 | Retained |
| target_d242f6d6a206 | 5 | 2 | 1 | Retained |
| target_783500710dcd | 6 | 2 | 2 | Retained |
| target_c2ddfd19b70e | 7 | 2 | 2 | Retained |
| target_5f37ee0641f8 | 8;10 | 2 | 4 | Retained |
| target_d082fd83866c | 9;11 | 2 | 2 | Retained |
| target_e5d66d3687d1 | 12 | 2 | 0.5 | Retained |
| target_b05a88be5f23 | 13 | 2 | 1 | Retained |
| target_26532df36cea | 14 | 2 | 1 | Retained |
| target_111ff26b1ba5 | 15 | 2 | 0.5 | Retained |
| target_9fa0d41f98df | 16 | 2 | 1 | Retained |
| target_cb02d2b72ad1 | 17 | 3 | 8 | Retained |
| target_a7a01fb877a8 | 18 | 3 | 8 | Retained |
| target_0c5264564dbd | 19 | 3 | 8 | Retained |
| target_7b9cd55bc878 | 20 | 3 | 16 | Retained |
| target_d44f59f31d5a | 21 | 3 | 16 | Retained |
| target_47029288753c | 22 | 3 | 32 | Retained |
| target_60f858741a39 | 23 | 3 | 8 | Retained |
| target_5a09b1639e8a | 24 | 3 | 8 | Retained |
| target_13069bc2b9a7 | 25 | 3 | 2 | Retained |
| target_54f705e7b634 | 26 | 3 | 16 | Retained |
| target_ac9f6ec5371d | 27 | 3 | 4 | Retained |
| target_c8944399d06e | 28 | 3 | 500 | Retained |
| target_944f891f9866 | 29 | 3 | 4 | Retained |
| target_55a4ccf326fb | 30 | 3 | 4 | Retained |
| target_14b46fc20087 | 31 | 3 | 8 | Retained |
| target_ed5dca0ab1a0 | 32 | 3 | 8 | Retained |
| target_f3049d508e66 | 33 | 3 | 8 | Retained |
| target_d739545655c4 | 34 | 3 | 16 | Retained |
| target_c7ea11f844f5 | 35 | 3 | 1 | Retained |
| target_9a22770bcaec | 36 | 3 | 1 | Retained |
| target_d70ac6fff1db | 37 | 3 | 0.5 | Retained |
| target_7df62429239c | 38 | 3 | 0.5 | Retained |
| target_7af915076170 | 39 | 3 | 0.5 | Retained |
| target_86c683f900f0 | 40 | 3 | 4 | Retained |
| target_fb840be32c7f | 41 | 3 | 8 | Retained |
| target_db77fe595601 | 42 | 3 | 4 | Retained |
| target_bd4b63380ec6 | 43 | 3 | 1 | Retained |
| target_af33959aae17 | 44 | 3 | 1 | Retained |
| target_d0cc4c7775a3 | 45 | 3 | 4 | Retained |
| target_aefd51c38de5 | 46 | 3 | 2 | Retained |
| target_6cc29577e95e | 47 | 2 | 1 | Retained |
| target_2c13aad3472f | 48 | 2 | 0.5 | Retained |
| target_fda274b855a9 | 49 | 2 | 0.5 | Retained |
| target_3741a879ef5f | 50 | 2 | 0.5 | Retained |
| target_c4c063d5b1a7 | 51 | 2 | 4 | Retained |
| target_e15a783a8ef3 | 52 | 2 | 16 | Retained |
| target_0f265aa7d7ea | 53 | 2 | 63 | Retained |
| target_f5e64b6d13fd | 54 | 2 | 2 | Retained |
| target_623fd6010c3a | 55 | 2 | 0.5 | Retained |
| target_b5bfddf8ee22 | 56 | 2 | 0.5 | Retained |
| target_270eb600c18e | 57 | 2 | 2 | Retained |
| target_8100230f50b6 | 58 | 2 | 4 | Retained |
| target_90b019aa6408 | 59 | 2 | 8 | Retained |
| target_d4e3a7f389d4 | 60 | 2 | 32 | Retained |
| target_c6bad5c9e57b | 61 | 2 | 0.5 | Retained |
| target_9bbcd4d4efdf | 62 | 2 | 1 | Retained |
| target_c8105814f7d7 | 63 | 2 | 1 | Retained |
| target_4d1910eaf8e7 | 64 | 2 | 2 | Retained |
| target_3ece311d6799 | 65 | 2 | 4 | Retained |
| target_b423693dd5d7 | 66 | 2 | 1 | Retained |
| target_aa7a420227be | 67 | 2 | 1 | Retained |
| target_90836dc3b79d | 68 | 2 | 8 | Retained |
| target_235544231979 | 69 | 2 | 2 | Retained |
| target_a0205d14932c | 70 | 2 | 0.5 | Retained |
| target_e62c6eb76913 | 71 | 2 | 0.25 | Retained |
| target_2852df1f1098 | 72 | 2 | 0.25 | Retained |
| target_04edfe20fcd6 | 73 | 2 | 8 | Retained |
| target_d949721c7a47 | 74 | 2 | 1 | Retained |
| target_25e7bff606cb | 75;76 | 2 | 0.375 | Conflicting duplicate |
| target_3c7e4c921f07 | 77 | 2 | 0.5 | Retained |
| target_7649e5557386 | 78 | 2 | 0.5 | Retained |
| target_6b31d8919b5d | 79 | 2 | 0.5 | Retained |
| target_f3fb36f09486 | 80 | 2 | 4 | Retained |
| target_a2b856633eb8 | 81 | 2 | 2 | Retained |
| target_29136ba3d6e0 | 82 | 1 | 2 | Retained |
| target_60e170d4a935 | 83 | 1 | 4 | Retained |
| target_6d9e4a369e18 | 84 | 2 | 16 | Retained |
| target_bb933c914257 | 85 | 2 | 1 | Retained |
| target_83baa869cd02 | 86 | 2 | 1 | Retained |
| target_0cdf888f7d44 | 87 | 2 | 1 | Retained |
| target_8e42242fabbc | 88 | 2 | 1 | Retained |
| target_9b2907932aff | 89 | 2 | 1 | Retained |
| target_057fdb05f9e2 | 90 | 2 | 8 | Retained |
| target_5d7aad53bdb2 | 91 | 2 | 1 | Retained |
| target_de643a2c8fc8 | 92 | 2 | 1 | Retained |
| target_e596f98b6ea4 | 93 | 2 | 4 | Retained |
| target_4328478245c9 | 94 | 2 | 32 | Retained |
| target_2897184299f3 | 95 | 2 | 8 | Retained |
| target_d7ce1f084838 | 96 | 2 | 1 | Retained |
| target_1e7e903c973a | 97 | 2 | 1 | Retained |
| target_72fcfd195eb4 | 98 | 2 | 2 | Retained |
| target_63d88e02cb2d | 99 | 2 | 4 | Retained |
| target_941721b4f23b | 100 | 2 | 8 | Retained |
| target_3e6bbdfa112c | 101 | 2 | 1 | Retained |
| target_891b66e0a998 | 102 | 2 | 2 | Retained |
| target_41bdc6042a86 | 103 | 2 | 0.5 | Retained |
| target_c555910e1515 | 104 | 2 | 2 | Retained |
| target_c9bf7d430547 | 105 | 2 | 4 | Retained |
| target_66b664b9319d | 106 | 2 | 0.5 | Retained |
| target_0e5b2d624437 | 107 | 2 | 8 | Retained |

Table S20. All 17 OOD compounds and supplied endpoint values in mg/L. Exact molecular structures, salts and source codes are retained. Each family has zero cation-scaffold overlap with both the matched source panel and QAC-105.

| Code / family | Sa MIC | Sa MBC | Ec MIC | Ec MBC |
| --- | --- | --- | --- | --- |
| IT505 / G1 | 4 | 64 | 500 | >500 |
| IT502 / G1 | 2 | 32 | 125 | 250 |
| IT499 / G1 | 1 | 8 | 125 | 125 |
| DA253 / G2 | 0.25 | 2 | 4 | 8 |
| PDD13 / G2 | 0.5 | 4 | 32 | 32 |
| PDD14 / G2 | 1 | 2 | 32 | 32 |
| PDD11 / G2 | 0.5 | 8 | 32 | 32 |
| IT442 / G3 | 16 | 64 | 125 | 125 |
| IT469 / G3 | 2 | 16 | 8 | 8 |
| IT452 / G3 | 0.5 | 0.5 | 32 | 500 |
| IT493 / G3 | 1 | 1 | 4 | 4 |
| IT380 / G3 | 8 | 16 | 64 | 250 |
| SEV-0338 / G4 | 2 | 8 | 16 | 16 |
| SEV-035 / G4 | 2 | 16 | 8 | 8 |
| SEV-036 / G4 | 4 | 4 | 32 | 32 |
| SEV-030 / G4 | 8 | 16 | 64 | 64 |
| SEV-033 / G4 | 16 | 125 | 32 | 32 |

Table S21. Leave-one-OOD-family-out score sensitivity. Each row removes a family only during scoring; no model is fitted on OOD. It probes whether the pooled error contrast depends on one family and does not expand the four-family population.

| Omitted family | Exact pairs | Human RMSE | Continuous RMSE | Human − continuous |
| --- | --- | --- | --- | --- |
| G1 | 56 | 1.942 | 2.042 | -0.100 |
| G2 | 51 | 2.122 | 2.362 | -0.240 |
| G3 | 47 | 1.832 | 2.027 | -0.196 |
| G4 | 47 | 2.303 | 2.504 | -0.201 |

Table S22. Right-censored endpoint minimum-error sensitivity. Exact residuals are combined with max(lower bound − prediction, 0) for IT505 E. coli MBC. Values are lower bounds on the true RMSE and MAE, not metrics obtained by declaring the bound exact. Endpoint Ec MBC uses 16 exact values plus one bound; pooled scoring uses 67 exact values plus that bound.

| Arm / encoding | Task | Seeds | Minimum RMSE ± SD | Minimum MAE |
| --- | --- | --- | --- | --- |
| expert / onehot | Ec_MBC | 5 | 2.356 ± 0.128 | 1.835 |
| expert / onehot | pooled | 5 | 2.101 ± 0.093 | 1.686 |
| quant-binary / onehot | Ec_MBC | 5 | 2.301 ± 0.175 | 1.799 |
| quant-binary / onehot | pooled | 5 | 2.143 ± 0.080 | 1.741 |
| quant-continuous / onehot | Ec_MBC | 5 | 2.703 ± 0.071 | 1.997 |
| quant-continuous / onehot | pooled | 5 | 2.305 ± 0.027 | 1.793 |
| raw-molformer / onehot | Ec_MBC | 1 | 2.787 ± 0.000 | 2.210 |
| raw-molformer / onehot | pooled | 1 | 2.352 ± 0.000 | 1.910 |

The complete ACS 1996 structure atlases are standalone vector PDF/SVG files in revision_v14/figures. Original individual structures remain in revision_v13/figures/molecules_ACS1996. Primary compound spectra and missing assay records remain reserved for coauthors; vector depictions are not evidence of identity or purity.

S21. Fixed graph and tabular model comparison

All 913 fits completed. Metrics were independently recomputed from saved per-compound predictions. This extension was selected after earlier results and is exploratory. It uses one adapted source seed (0), fixed CV folds, full QAC-105 and all 17 OOD molecules. Four tabular decoders predict each endpoint separately; Chemprop predicts four targets jointly. Human and quantitative features use the archived layout. Absolute concentrations and qualifiers are preserved, including IT505 Ec_MBC >500 mg/L. The complete run, configuration and code-version ledgers are in server_models_20261012.

Table S23. Complete pooled-loss fixed-model comparison, corresponding to main Table 5. Units are log2(mg/L). Graph results are means of three seed-specific RMSE values; all tabular comparisons have one source seed. No point estimate is a declaration of general method superiority.

| Model | Representation | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| CatBoost (PCA control) | Human | 1.767 | 1.901 | 2.124 |
| CatBoost (PCA control) | Continuous MIC | 1.872 | 1.892 | 2.349 |
| CatBoost (PCA control) | Binary MIC | 1.856 | 1.971 | 2.224 |
| CatBoost (PCA control) | Raw MolFormer | 1.890 | 1.956 | 2.295 |
| CatBoost (PCA control) | RDKit descriptors | 1.615 | 1.818 | 2.066 |
| AutoGluon | Human | 1.810 | 1.934 | 2.148 |
| AutoGluon | Continuous MIC | 1.886 | 1.955 | 2.289 |
| AutoGluon | Binary MIC | 1.852 | 1.911 | 2.197 |
| AutoGluon | Raw MolFormer | 1.953 | 1.938 | 2.208 |
| AutoGluon | RDKit descriptors | 1.716 | 1.828 | 2.222 |
| TabPFN-V2 | Human | 1.822 | 1.833 | 1.966 |
| TabPFN-V2 | Continuous MIC | 1.853 | 1.932 | 2.265 |
| TabPFN-V2 | Binary MIC | 1.838 | 1.920 | 1.995 |
| TabPFN-V2 | Raw MolFormer | 1.948 | 1.984 | 2.225 |
| TabPFN-V2 | RDKit descriptors | 1.725 | 1.909 | 1.978 |
| TabFM | Human | 1.730 | 1.814 | 1.992 |
| TabFM | Continuous MIC | 1.772 | 1.888 | 2.541 |
| TabFM | Binary MIC | 1.814 | 1.936 | 2.110 |
| TabFM | Raw MolFormer | 1.900 | 1.952 | 2.299 |
| TabFM | RDKit descriptors | 1.619 | 1.909 | 2.027 |
| Chemprop D-MPNN | Molecular graph | 2.031 | 2.003 | 2.375 |

Table S24. Every endpoint score in the fixed-model comparison. Trained graph entries are mean ± graph-seed SD (three seeds); tabular entries have one fit per endpoint and no seed SD. Source-seed uncertainty is not included. Pooled R² is deliberately omitted; each reported R² assesses variation within one species/endpoint.

| Model / representation | Scheme / endpoint | Seeds / n | RMSE | MAE / R² |
| --- | --- | --- | --- | --- |
| AutoGluon / Human | cation / Ec_MBC | 1 / 105 | 1.824 | 1.436 / 0.238 |
| AutoGluon / Human | cation / Ec_MIC | 1 / 105 | 1.667 | 1.254 / 0.284 |
| AutoGluon / Human | cation / Sa_MBC | 1 / 105 | 1.959 | 1.398 / 0.004 |
| AutoGluon / Human | cation / Sa_MIC | 1 / 105 | 1.778 | 1.325 / 0.177 |
| AutoGluon / Human | full-QAC105 / Ec_MBC | 1 / 16 | 2.357 | 1.908 / -0.420 |
| AutoGluon / Human | full-QAC105 / Ec_MIC | 1 / 17 | 2.284 | 1.931 / -0.576 |
| AutoGluon / Human | full-QAC105 / Sa_MBC | 1 / 17 | 2.149 | 1.744 / -0.030 |
| AutoGluon / Human | full-QAC105 / Sa_MIC | 1 / 17 | 1.767 | 1.516 / -0.021 |
| AutoGluon / Human | scaffold / Ec_MBC | 1 / 105 | 1.947 | 1.508 / 0.131 |
| AutoGluon / Human | scaffold / Ec_MIC | 1 / 105 | 1.848 | 1.447 / 0.120 |
| AutoGluon / Human | scaffold / Sa_MBC | 1 / 105 | 1.960 | 1.472 / 0.003 |
| AutoGluon / Human | scaffold / Sa_MIC | 1 / 105 | 1.977 | 1.510 / -0.018 |
| AutoGluon / Binary MIC | cation / Ec_MBC | 1 / 105 | 1.936 | 1.538 / 0.141 |
| AutoGluon / Binary MIC | cation / Ec_MIC | 1 / 105 | 1.772 | 1.387 / 0.191 |
| AutoGluon / Binary MIC | cation / Sa_MBC | 1 / 105 | 1.946 | 1.418 / 0.018 |
| AutoGluon / Binary MIC | cation / Sa_MIC | 1 / 105 | 1.744 | 1.284 / 0.208 |
| AutoGluon / Binary MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.419 | 1.969 / -0.496 |
| AutoGluon / Binary MIC | full-QAC105 / Ec_MIC | 1 / 17 | 2.233 | 1.867 / -0.506 |
| AutoGluon / Binary MIC | full-QAC105 / Sa_MBC | 1 / 17 | 2.134 | 1.734 / -0.015 |
| AutoGluon / Binary MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.995 | 1.697 / -0.301 |
| AutoGluon / Binary MIC | scaffold / Ec_MBC | 1 / 105 | 2.002 | 1.571 / 0.081 |
| AutoGluon / Binary MIC | scaffold / Ec_MIC | 1 / 105 | 1.879 | 1.456 / 0.091 |
| AutoGluon / Binary MIC | scaffold / Sa_MBC | 1 / 105 | 1.893 | 1.414 / 0.070 |
| AutoGluon / Binary MIC | scaffold / Sa_MIC | 1 / 105 | 1.868 | 1.504 / 0.091 |
| AutoGluon / Continuous MIC | cation / Ec_MBC | 1 / 105 | 1.991 | 1.584 / 0.092 |
| AutoGluon / Continuous MIC | cation / Ec_MIC | 1 / 105 | 1.848 | 1.417 / 0.120 |
| AutoGluon / Continuous MIC | cation / Sa_MBC | 1 / 105 | 1.898 | 1.322 / 0.066 |
| AutoGluon / Continuous MIC | cation / Sa_MIC | 1 / 105 | 1.800 | 1.386 / 0.156 |
| AutoGluon / Continuous MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.673 | 1.870 / -0.826 |
| AutoGluon / Continuous MIC | full-QAC105 / Ec_MIC | 1 / 17 | 2.578 | 1.978 / -1.008 |
| AutoGluon / Continuous MIC | full-QAC105 / Sa_MBC | 1 / 17 | 2.052 | 1.798 / 0.060 |
| AutoGluon / Continuous MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.753 | 1.451 / -0.005 |
| AutoGluon / Continuous MIC | scaffold / Ec_MBC | 1 / 105 | 1.992 | 1.614 / 0.091 |
| AutoGluon / Continuous MIC | scaffold / Ec_MIC | 1 / 105 | 1.924 | 1.519 / 0.046 |
| AutoGluon / Continuous MIC | scaffold / Sa_MBC | 1 / 105 | 1.958 | 1.401 / 0.005 |
| AutoGluon / Continuous MIC | scaffold / Sa_MIC | 1 / 105 | 1.945 | 1.562 / 0.015 |
| AutoGluon / Raw MolFormer | cation / Ec_MBC | 1 / 105 | 2.112 | 1.687 / -0.022 |
| AutoGluon / Raw MolFormer | cation / Ec_MIC | 1 / 105 | 1.907 | 1.550 / 0.063 |
| AutoGluon / Raw MolFormer | cation / Sa_MBC | 1 / 105 | 1.951 | 1.495 / 0.013 |
| AutoGluon / Raw MolFormer | cation / Sa_MIC | 1 / 105 | 1.832 | 1.483 / 0.126 |
| AutoGluon / Raw MolFormer | full-QAC105 / Ec_MBC | 1 / 16 | 2.421 | 1.982 / -0.498 |
| AutoGluon / Raw MolFormer | full-QAC105 / Ec_MIC | 1 / 17 | 2.504 | 2.063 / -0.894 |
| AutoGluon / Raw MolFormer | full-QAC105 / Sa_MBC | 1 / 17 | 2.008 | 1.769 / 0.101 |
| AutoGluon / Raw MolFormer | full-QAC105 / Sa_MIC | 1 / 17 | 1.843 | 1.543 / -0.111 |
| AutoGluon / Raw MolFormer | scaffold / Ec_MBC | 1 / 105 | 2.052 | 1.658 / 0.035 |
| AutoGluon / Raw MolFormer | scaffold / Ec_MIC | 1 / 105 | 1.905 | 1.505 / 0.066 |
| AutoGluon / Raw MolFormer | scaffold / Sa_MBC | 1 / 105 | 1.942 | 1.417 / 0.021 |
| AutoGluon / Raw MolFormer | scaffold / Sa_MIC | 1 / 105 | 1.848 | 1.523 / 0.111 |
| AutoGluon / RDKit descriptors | cation / Ec_MBC | 1 / 105 | 1.800 | 1.364 / 0.258 |
| AutoGluon / RDKit descriptors | cation / Ec_MIC | 1 / 105 | 1.613 | 1.230 / 0.330 |
| AutoGluon / RDKit descriptors | cation / Sa_MBC | 1 / 105 | 1.739 | 1.315 / 0.215 |
| AutoGluon / RDKit descriptors | cation / Sa_MIC | 1 / 105 | 1.708 | 1.318 / 0.240 |
| AutoGluon / RDKit descriptors | full-QAC105 / Ec_MBC | 1 / 16 | 2.436 | 1.930 / -0.517 |
| AutoGluon / RDKit descriptors | full-QAC105 / Ec_MIC | 1 / 17 | 2.486 | 2.083 / -0.868 |
| AutoGluon / RDKit descriptors | full-QAC105 / Sa_MBC | 1 / 17 | 2.147 | 1.776 / -0.029 |
| AutoGluon / RDKit descriptors | full-QAC105 / Sa_MIC | 1 / 17 | 1.754 | 1.435 / -0.005 |
| AutoGluon / RDKit descriptors | scaffold / Ec_MBC | 1 / 105 | 1.843 | 1.416 / 0.222 |
| AutoGluon / RDKit descriptors | scaffold / Ec_MIC | 1 / 105 | 1.659 | 1.250 / 0.291 |
| AutoGluon / RDKit descriptors | scaffold / Sa_MBC | 1 / 105 | 1.894 | 1.429 / 0.069 |
| AutoGluon / RDKit descriptors | scaffold / Sa_MIC | 1 / 105 | 1.905 | 1.527 / 0.055 |
| CatBoost (PCA control) / Human | cation / Ec_MBC | 1 / 105 | 1.816 | 1.428 / 0.244 |
| CatBoost (PCA control) / Human | cation / Ec_MIC | 1 / 105 | 1.640 | 1.273 / 0.307 |
| CatBoost (PCA control) / Human | cation / Sa_MBC | 1 / 105 | 1.895 | 1.347 / 0.068 |
| CatBoost (PCA control) / Human | cation / Sa_MIC | 1 / 105 | 1.706 | 1.272 / 0.242 |
| CatBoost (PCA control) / Human | full-QAC105 / Ec_MBC | 1 / 16 | 2.278 | 1.794 / -0.327 |
| CatBoost (PCA control) / Human | full-QAC105 / Ec_MIC | 1 / 17 | 2.155 | 1.757 / -0.403 |
| CatBoost (PCA control) / Human | full-QAC105 / Sa_MBC | 1 / 17 | 2.210 | 1.783 / -0.090 |
| CatBoost (PCA control) / Human | full-QAC105 / Sa_MIC | 1 / 17 | 1.833 | 1.529 / -0.098 |
| CatBoost (PCA control) / Human | scaffold / Ec_MBC | 1 / 105 | 1.890 | 1.492 / 0.182 |
| CatBoost (PCA control) / Human | scaffold / Ec_MIC | 1 / 105 | 1.770 | 1.375 / 0.193 |
| CatBoost (PCA control) / Human | scaffold / Sa_MBC | 1 / 105 | 1.999 | 1.475 / -0.037 |
| CatBoost (PCA control) / Human | scaffold / Sa_MIC | 1 / 105 | 1.938 | 1.496 / 0.022 |
| CatBoost (PCA control) / Binary MIC | cation / Ec_MBC | 1 / 105 | 1.935 | 1.509 / 0.143 |
| CatBoost (PCA control) / Binary MIC | cation / Ec_MIC | 1 / 105 | 1.775 | 1.336 / 0.188 |
| CatBoost (PCA control) / Binary MIC | cation / Sa_MBC | 1 / 105 | 1.944 | 1.395 / 0.020 |
| CatBoost (PCA control) / Binary MIC | cation / Sa_MIC | 1 / 105 | 1.764 | 1.282 / 0.190 |
| CatBoost (PCA control) / Binary MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.304 | 1.837 / -0.357 |
| CatBoost (PCA control) / Binary MIC | full-QAC105 / Ec_MIC | 1 / 17 | 2.099 | 1.728 / -0.331 |
| CatBoost (PCA control) / Binary MIC | full-QAC105 / Sa_MBC | 1 / 17 | 2.283 | 1.899 / -0.163 |
| CatBoost (PCA control) / Binary MIC | full-QAC105 / Sa_MIC | 1 / 17 | 2.208 | 1.865 / -0.594 |
| CatBoost (PCA control) / Binary MIC | scaffold / Ec_MBC | 1 / 105 | 2.018 | 1.587 / 0.067 |
| CatBoost (PCA control) / Binary MIC | scaffold / Ec_MIC | 1 / 105 | 1.862 | 1.467 / 0.107 |
| CatBoost (PCA control) / Binary MIC | scaffold / Sa_MBC | 1 / 105 | 2.099 | 1.528 / -0.142 |
| CatBoost (PCA control) / Binary MIC | scaffold / Sa_MIC | 1 / 105 | 1.895 | 1.450 / 0.065 |
| CatBoost (PCA control) / Continuous MIC | cation / Ec_MBC | 1 / 105 | 1.943 | 1.540 / 0.135 |
| CatBoost (PCA control) / Continuous MIC | cation / Ec_MIC | 1 / 105 | 1.789 | 1.379 / 0.175 |
| CatBoost (PCA control) / Continuous MIC | cation / Sa_MBC | 1 / 105 | 1.933 | 1.363 / 0.031 |
| CatBoost (PCA control) / Continuous MIC | cation / Sa_MIC | 1 / 105 | 1.817 | 1.396 / 0.140 |
| CatBoost (PCA control) / Continuous MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.890 | 2.096 / -1.135 |
| CatBoost (PCA control) / Continuous MIC | full-QAC105 / Ec_MIC | 1 / 17 | 2.622 | 2.116 / -1.076 |
| CatBoost (PCA control) / Continuous MIC | full-QAC105 / Sa_MBC | 1 / 17 | 1.897 | 1.620 / 0.198 |
| CatBoost (PCA control) / Continuous MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.850 | 1.598 / -0.119 |
| CatBoost (PCA control) / Continuous MIC | scaffold / Ec_MBC | 1 / 105 | 1.903 | 1.546 / 0.170 |
| CatBoost (PCA control) / Continuous MIC | scaffold / Ec_MIC | 1 / 105 | 1.787 | 1.428 / 0.177 |
| CatBoost (PCA control) / Continuous MIC | scaffold / Sa_MBC | 1 / 105 | 2.030 | 1.465 / -0.069 |
| CatBoost (PCA control) / Continuous MIC | scaffold / Sa_MIC | 1 / 105 | 1.839 | 1.466 / 0.119 |
| CatBoost (PCA control) / Raw MolFormer | cation / Ec_MBC | 1 / 105 | 1.976 | 1.573 / 0.106 |
| CatBoost (PCA control) / Raw MolFormer | cation / Ec_MIC | 1 / 105 | 1.857 | 1.457 / 0.112 |
| CatBoost (PCA control) / Raw MolFormer | cation / Sa_MBC | 1 / 105 | 1.914 | 1.457 / 0.050 |
| CatBoost (PCA control) / Raw MolFormer | cation / Sa_MIC | 1 / 105 | 1.811 | 1.457 / 0.146 |
| CatBoost (PCA control) / Raw MolFormer | full-QAC105 / Ec_MBC | 1 / 16 | 2.526 | 1.979 / -0.631 |
| CatBoost (PCA control) / Raw MolFormer | full-QAC105 / Ec_MIC | 1 / 17 | 2.381 | 1.955 / -0.713 |
| CatBoost (PCA control) / Raw MolFormer | full-QAC105 / Sa_MBC | 1 / 17 | 2.127 | 1.717 / -0.009 |
| CatBoost (PCA control) / Raw MolFormer | full-QAC105 / Sa_MIC | 1 / 17 | 2.137 | 1.830 / -0.493 |
| CatBoost (PCA control) / Raw MolFormer | scaffold / Ec_MBC | 1 / 105 | 1.984 | 1.580 / 0.098 |
| CatBoost (PCA control) / Raw MolFormer | scaffold / Ec_MIC | 1 / 105 | 1.889 | 1.513 / 0.081 |
| CatBoost (PCA control) / Raw MolFormer | scaffold / Sa_MBC | 1 / 105 | 2.070 | 1.503 / -0.111 |
| CatBoost (PCA control) / Raw MolFormer | scaffold / Sa_MIC | 1 / 105 | 1.873 | 1.511 / 0.087 |
| CatBoost (PCA control) / RDKit descriptors | cation / Ec_MBC | 1 / 105 | 1.591 | 1.117 / 0.420 |
| CatBoost (PCA control) / RDKit descriptors | cation / Ec_MIC | 1 / 105 | 1.594 | 1.151 / 0.346 |
| CatBoost (PCA control) / RDKit descriptors | cation / Sa_MBC | 1 / 105 | 1.583 | 1.174 / 0.350 |
| CatBoost (PCA control) / RDKit descriptors | cation / Sa_MIC | 1 / 105 | 1.691 | 1.297 / 0.256 |
| CatBoost (PCA control) / RDKit descriptors | full-QAC105 / Ec_MBC | 1 / 16 | 2.283 | 1.692 / -0.332 |
| CatBoost (PCA control) / RDKit descriptors | full-QAC105 / Ec_MIC | 1 / 17 | 2.163 | 1.782 / -0.413 |
| CatBoost (PCA control) / RDKit descriptors | full-QAC105 / Sa_MBC | 1 / 17 | 1.915 | 1.611 / 0.182 |
| CatBoost (PCA control) / RDKit descriptors | full-QAC105 / Sa_MIC | 1 / 17 | 1.889 | 1.593 / -0.167 |
| CatBoost (PCA control) / RDKit descriptors | scaffold / Ec_MBC | 1 / 105 | 1.752 | 1.343 / 0.297 |
| CatBoost (PCA control) / RDKit descriptors | scaffold / Ec_MIC | 1 / 105 | 1.617 | 1.262 / 0.326 |
| CatBoost (PCA control) / RDKit descriptors | scaffold / Sa_MBC | 1 / 105 | 1.979 | 1.478 / -0.016 |
| CatBoost (PCA control) / RDKit descriptors | scaffold / Sa_MIC | 1 / 105 | 1.902 | 1.479 / 0.057 |
| Chemprop D-MPNN / Molecular graph | cation / Ec_MBC | 3 / 105 | 2.101 ± 0.015 | 1.717 ± 0.011 / -0.012 ± 0.015 |
| Chemprop D-MPNN / Molecular graph | cation / Ec_MIC | 3 / 105 | 1.968 ± 0.013 | 1.525 ± 0.018 / 0.002 ± 0.013 |
| Chemprop D-MPNN / Molecular graph | cation / Sa_MBC | 3 / 105 | 2.097 ± 0.020 | 1.567 ± 0.003 / -0.140 ± 0.022 |
| Chemprop D-MPNN / Molecular graph | cation / Sa_MIC | 3 / 105 | 1.953 ± 0.012 | 1.497 ± 0.011 / 0.007 ± 0.012 |
| Chemprop D-MPNN / Molecular graph | full-QAC105 / Ec_MBC | 3 / 16 | 2.574 ± 0.172 | 2.073 ± 0.127 / -0.698 ± 0.231 |
| Chemprop D-MPNN / Molecular graph | full-QAC105 / Ec_MIC | 3 / 17 | 2.645 ± 0.207 | 2.264 ± 0.165 / -1.122 ± 0.328 |
| Chemprop D-MPNN / Molecular graph | full-QAC105 / Sa_MBC | 3 / 17 | 2.271 ± 0.141 | 1.913 ± 0.155 / -0.154 ± 0.145 |
| Chemprop D-MPNN / Molecular graph | full-QAC105 / Sa_MIC | 3 / 17 | 1.956 ± 0.043 | 1.636 ± 0.034 / -0.251 ± 0.055 |
| Chemprop D-MPNN / Molecular graph | scaffold / Ec_MBC | 3 / 105 | 2.041 ± 0.005 | 1.671 ± 0.005 / 0.045 ± 0.005 |
| Chemprop D-MPNN / Molecular graph | scaffold / Ec_MIC | 3 / 105 | 1.999 ± 0.009 | 1.553 ± 0.008 / -0.030 ± 0.010 |
| Chemprop D-MPNN / Molecular graph | scaffold / Sa_MBC | 3 / 105 | 2.074 ± 0.012 | 1.571 ± 0.026 / -0.116 ± 0.013 |
| Chemprop D-MPNN / Molecular graph | scaffold / Sa_MIC | 3 / 105 | 1.892 ± 0.010 | 1.488 ± 0.020 / 0.068 ± 0.010 |
| TabFM / Human | cation / Ec_MBC | 1 / 105 | 1.723 | 1.277 / 0.320 |
| TabFM / Human | cation / Ec_MIC | 1 / 105 | 1.603 | 1.184 / 0.338 |
| TabFM / Human | cation / Sa_MBC | 1 / 105 | 1.871 | 1.324 / 0.092 |
| TabFM / Human | cation / Sa_MIC | 1 / 105 | 1.713 | 1.287 / 0.236 |
| TabFM / Human | full-QAC105 / Ec_MBC | 1 / 16 | 2.200 | 1.795 / -0.238 |
| TabFM / Human | full-QAC105 / Ec_MIC | 1 / 17 | 2.057 | 1.697 / -0.279 |
| TabFM / Human | full-QAC105 / Sa_MBC | 1 / 17 | 1.942 | 1.572 / 0.159 |
| TabFM / Human | full-QAC105 / Sa_MIC | 1 / 17 | 1.753 | 1.465 / -0.004 |
| TabFM / Human | scaffold / Ec_MBC | 1 / 105 | 1.760 | 1.368 / 0.291 |
| TabFM / Human | scaffold / Ec_MIC | 1 / 105 | 1.581 | 1.204 / 0.356 |
| TabFM / Human | scaffold / Sa_MBC | 1 / 105 | 2.039 | 1.506 / -0.079 |
| TabFM / Human | scaffold / Sa_MIC | 1 / 105 | 1.845 | 1.425 / 0.113 |
| TabFM / Binary MIC | cation / Ec_MBC | 1 / 105 | 1.854 | 1.421 / 0.213 |
| TabFM / Binary MIC | cation / Ec_MIC | 1 / 105 | 1.673 | 1.266 / 0.279 |
| TabFM / Binary MIC | cation / Sa_MBC | 1 / 105 | 1.940 | 1.381 / 0.024 |
| TabFM / Binary MIC | cation / Sa_MIC | 1 / 105 | 1.778 | 1.308 / 0.177 |
| TabFM / Binary MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.202 | 1.729 / -0.239 |
| TabFM / Binary MIC | full-QAC105 / Ec_MIC | 1 / 17 | 2.075 | 1.675 / -0.301 |
| TabFM / Binary MIC | full-QAC105 / Sa_MBC | 1 / 17 | 2.287 | 1.903 / -0.166 |
| TabFM / Binary MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.859 | 1.560 / -0.130 |
| TabFM / Binary MIC | scaffold / Ec_MBC | 1 / 105 | 1.922 | 1.524 / 0.153 |
| TabFM / Binary MIC | scaffold / Ec_MIC | 1 / 105 | 1.765 | 1.402 / 0.197 |
| TabFM / Binary MIC | scaffold / Sa_MBC | 1 / 105 | 2.139 | 1.570 / -0.186 |
| TabFM / Binary MIC | scaffold / Sa_MIC | 1 / 105 | 1.901 | 1.434 / 0.059 |
| TabFM / Continuous MIC | cation / Ec_MBC | 1 / 105 | 1.819 | 1.374 / 0.242 |
| TabFM / Continuous MIC | cation / Ec_MIC | 1 / 105 | 1.682 | 1.288 / 0.271 |
| TabFM / Continuous MIC | cation / Sa_MBC | 1 / 105 | 1.888 | 1.323 / 0.076 |
| TabFM / Continuous MIC | cation / Sa_MIC | 1 / 105 | 1.691 | 1.272 / 0.255 |
| TabFM / Continuous MIC | full-QAC105 / Ec_MBC | 1 / 16 | 3.107 | 2.276 / -1.468 |
| TabFM / Continuous MIC | full-QAC105 / Ec_MIC | 1 / 17 | 3.000 | 2.475 / -1.718 |
| TabFM / Continuous MIC | full-QAC105 / Sa_MBC | 1 / 17 | 2.070 | 1.712 / 0.044 |
| TabFM / Continuous MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.752 | 1.457 / -0.003 |
| TabFM / Continuous MIC | scaffold / Ec_MBC | 1 / 105 | 1.895 | 1.514 / 0.177 |
| TabFM / Continuous MIC | scaffold / Ec_MIC | 1 / 105 | 1.800 | 1.435 / 0.165 |
| TabFM / Continuous MIC | scaffold / Sa_MBC | 1 / 105 | 2.055 | 1.476 / -0.096 |
| TabFM / Continuous MIC | scaffold / Sa_MIC | 1 / 105 | 1.789 | 1.369 / 0.167 |
| TabFM / Raw MolFormer | cation / Ec_MBC | 1 / 105 | 2.000 | 1.610 / 0.084 |
| TabFM / Raw MolFormer | cation / Ec_MIC | 1 / 105 | 1.856 | 1.463 / 0.113 |
| TabFM / Raw MolFormer | cation / Sa_MBC | 1 / 105 | 1.919 | 1.414 / 0.045 |
| TabFM / Raw MolFormer | cation / Sa_MIC | 1 / 105 | 1.819 | 1.444 / 0.139 |
| TabFM / Raw MolFormer | full-QAC105 / Ec_MBC | 1 / 16 | 2.507 | 2.044 / -0.607 |
| TabFM / Raw MolFormer | full-QAC105 / Ec_MIC | 1 / 17 | 2.584 | 2.095 / -1.018 |
| TabFM / Raw MolFormer | full-QAC105 / Sa_MBC | 1 / 17 | 2.166 | 1.780 / -0.047 |
| TabFM / Raw MolFormer | full-QAC105 / Sa_MIC | 1 / 17 | 1.882 | 1.569 / -0.158 |
| TabFM / Raw MolFormer | scaffold / Ec_MBC | 1 / 105 | 2.002 | 1.624 / 0.082 |
| TabFM / Raw MolFormer | scaffold / Ec_MIC | 1 / 105 | 1.842 | 1.504 / 0.126 |
| TabFM / Raw MolFormer | scaffold / Sa_MBC | 1 / 105 | 2.060 | 1.479 / -0.101 |
| TabFM / Raw MolFormer | scaffold / Sa_MIC | 1 / 105 | 1.899 | 1.554 / 0.061 |
| TabFM / RDKit descriptors | cation / Ec_MBC | 1 / 105 | 1.634 | 1.176 / 0.388 |
| TabFM / RDKit descriptors | cation / Ec_MIC | 1 / 105 | 1.508 | 1.083 / 0.415 |
| TabFM / RDKit descriptors | cation / Sa_MBC | 1 / 105 | 1.585 | 1.210 / 0.349 |
| TabFM / RDKit descriptors | cation / Sa_MIC | 1 / 105 | 1.741 | 1.286 / 0.211 |
| TabFM / RDKit descriptors | full-QAC105 / Ec_MBC | 1 / 16 | 2.292 | 1.803 / -0.343 |
| TabFM / RDKit descriptors | full-QAC105 / Ec_MIC | 1 / 17 | 1.989 | 1.657 / -0.194 |
| TabFM / RDKit descriptors | full-QAC105 / Sa_MBC | 1 / 17 | 2.017 | 1.658 / 0.093 |
| TabFM / RDKit descriptors | full-QAC105 / Sa_MIC | 1 / 17 | 1.796 | 1.505 / -0.054 |
| TabFM / RDKit descriptors | scaffold / Ec_MBC | 1 / 105 | 1.872 | 1.406 / 0.197 |
| TabFM / RDKit descriptors | scaffold / Ec_MIC | 1 / 105 | 1.762 | 1.401 / 0.200 |
| TabFM / RDKit descriptors | scaffold / Sa_MBC | 1 / 105 | 2.074 | 1.557 / -0.115 |
| TabFM / RDKit descriptors | scaffold / Sa_MIC | 1 / 105 | 1.915 | 1.475 / 0.044 |
| TabPFN-V2 / Human | cation / Ec_MBC | 1 / 105 | 1.810 | 1.360 / 0.250 |
| TabPFN-V2 / Human | cation / Ec_MIC | 1 / 105 | 1.697 | 1.292 / 0.258 |
| TabPFN-V2 / Human | cation / Sa_MBC | 1 / 105 | 1.913 | 1.412 / 0.051 |
| TabPFN-V2 / Human | cation / Sa_MIC | 1 / 105 | 1.860 | 1.424 / 0.099 |
| TabPFN-V2 / Human | full-QAC105 / Ec_MBC | 1 / 16 | 2.179 | 1.766 / -0.214 |
| TabPFN-V2 / Human | full-QAC105 / Ec_MIC | 1 / 17 | 1.903 | 1.605 / -0.094 |
| TabPFN-V2 / Human | full-QAC105 / Sa_MBC | 1 / 17 | 2.038 | 1.678 / 0.074 |
| TabPFN-V2 / Human | full-QAC105 / Sa_MIC | 1 / 17 | 1.727 | 1.374 / 0.024 |
| TabPFN-V2 / Human | scaffold / Ec_MBC | 1 / 105 | 1.828 | 1.448 / 0.235 |
| TabPFN-V2 / Human | scaffold / Ec_MIC | 1 / 105 | 1.714 | 1.325 / 0.244 |
| TabPFN-V2 / Human | scaffold / Sa_MBC | 1 / 105 | 1.937 | 1.496 / 0.027 |
| TabPFN-V2 / Human | scaffold / Sa_MIC | 1 / 105 | 1.848 | 1.496 / 0.111 |
| TabPFN-V2 / Binary MIC | cation / Ec_MBC | 1 / 105 | 1.879 | 1.437 / 0.191 |
| TabPFN-V2 / Binary MIC | cation / Ec_MIC | 1 / 105 | 1.742 | 1.338 / 0.219 |
| TabPFN-V2 / Binary MIC | cation / Sa_MBC | 1 / 105 | 1.880 | 1.327 / 0.083 |
| TabPFN-V2 / Binary MIC | cation / Sa_MIC | 1 / 105 | 1.848 | 1.391 / 0.110 |
| TabPFN-V2 / Binary MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.047 | 1.615 / -0.072 |
| TabPFN-V2 / Binary MIC | full-QAC105 / Ec_MIC | 1 / 17 | 1.949 | 1.603 / -0.147 |
| TabPFN-V2 / Binary MIC | full-QAC105 / Sa_MBC | 1 / 17 | 2.075 | 1.720 / 0.040 |
| TabPFN-V2 / Binary MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.907 | 1.631 / -0.189 |
| TabPFN-V2 / Binary MIC | scaffold / Ec_MBC | 1 / 105 | 1.911 | 1.539 / 0.163 |
| TabPFN-V2 / Binary MIC | scaffold / Ec_MIC | 1 / 105 | 1.849 | 1.466 / 0.119 |
| TabPFN-V2 / Binary MIC | scaffold / Sa_MBC | 1 / 105 | 2.017 | 1.497 / -0.056 |
| TabPFN-V2 / Binary MIC | scaffold / Sa_MIC | 1 / 105 | 1.898 | 1.504 / 0.062 |
| TabPFN-V2 / Continuous MIC | cation / Ec_MBC | 1 / 105 | 1.937 | 1.535 / 0.141 |
| TabPFN-V2 / Continuous MIC | cation / Ec_MIC | 1 / 105 | 1.782 | 1.381 / 0.182 |
| TabPFN-V2 / Continuous MIC | cation / Sa_MBC | 1 / 105 | 1.848 | 1.350 / 0.114 |
| TabPFN-V2 / Continuous MIC | cation / Sa_MIC | 1 / 105 | 1.841 | 1.430 / 0.117 |
| TabPFN-V2 / Continuous MIC | full-QAC105 / Ec_MBC | 1 / 16 | 2.815 | 1.961 / -1.026 |
| TabPFN-V2 / Continuous MIC | full-QAC105 / Ec_MIC | 1 / 17 | 2.404 | 1.937 / -0.746 |
| TabPFN-V2 / Continuous MIC | full-QAC105 / Sa_MBC | 1 / 17 | 1.992 | 1.640 / 0.114 |
| TabPFN-V2 / Continuous MIC | full-QAC105 / Sa_MIC | 1 / 17 | 1.733 | 1.429 / 0.018 |
| TabPFN-V2 / Continuous MIC | scaffold / Ec_MBC | 1 / 105 | 1.957 | 1.608 / 0.123 |
| TabPFN-V2 / Continuous MIC | scaffold / Ec_MIC | 1 / 105 | 1.928 | 1.570 / 0.043 |
| TabPFN-V2 / Continuous MIC | scaffold / Sa_MBC | 1 / 105 | 1.992 | 1.506 / -0.030 |
| TabPFN-V2 / Continuous MIC | scaffold / Sa_MIC | 1 / 105 | 1.847 | 1.484 / 0.112 |
| TabPFN-V2 / Raw MolFormer | cation / Ec_MBC | 1 / 105 | 2.003 | 1.628 / 0.081 |
| TabPFN-V2 / Raw MolFormer | cation / Ec_MIC | 1 / 105 | 1.901 | 1.499 / 0.069 |
| TabPFN-V2 / Raw MolFormer | cation / Sa_MBC | 1 / 105 | 1.954 | 1.486 / 0.010 |
| TabPFN-V2 / Raw MolFormer | cation / Sa_MIC | 1 / 105 | 1.933 | 1.579 / 0.027 |
| TabPFN-V2 / Raw MolFormer | full-QAC105 / Ec_MBC | 1 / 16 | 2.567 | 2.072 / -0.684 |
| TabPFN-V2 / Raw MolFormer | full-QAC105 / Ec_MIC | 1 / 17 | 2.313 | 1.920 / -0.616 |
| TabPFN-V2 / Raw MolFormer | full-QAC105 / Sa_MBC | 1 / 17 | 2.091 | 1.694 / 0.025 |
| TabPFN-V2 / Raw MolFormer | full-QAC105 / Sa_MIC | 1 / 17 | 1.893 | 1.584 / -0.171 |
| TabPFN-V2 / Raw MolFormer | scaffold / Ec_MBC | 1 / 105 | 2.052 | 1.677 / 0.036 |
| TabPFN-V2 / Raw MolFormer | scaffold / Ec_MIC | 1 / 105 | 1.951 | 1.562 / 0.019 |
| TabPFN-V2 / Raw MolFormer | scaffold / Sa_MBC | 1 / 105 | 1.988 | 1.527 / -0.025 |
| TabPFN-V2 / Raw MolFormer | scaffold / Sa_MIC | 1 / 105 | 1.942 | 1.639 / 0.018 |
| TabPFN-V2 / RDKit descriptors | cation / Ec_MBC | 1 / 105 | 1.600 | 1.150 / 0.414 |
| TabPFN-V2 / RDKit descriptors | cation / Ec_MIC | 1 / 105 | 1.544 | 1.166 / 0.386 |
| TabPFN-V2 / RDKit descriptors | cation / Sa_MBC | 1 / 105 | 1.786 | 1.326 / 0.173 |
| TabPFN-V2 / RDKit descriptors | cation / Sa_MIC | 1 / 105 | 1.940 | 1.503 / 0.020 |
| TabPFN-V2 / RDKit descriptors | full-QAC105 / Ec_MBC | 1 / 16 | 2.245 | 1.603 / -0.289 |
| TabPFN-V2 / RDKit descriptors | full-QAC105 / Ec_MIC | 1 / 17 | 2.054 | 1.723 / -0.275 |
| TabPFN-V2 / RDKit descriptors | full-QAC105 / Sa_MBC | 1 / 17 | 1.806 | 1.475 / 0.273 |
| TabPFN-V2 / RDKit descriptors | full-QAC105 / Sa_MIC | 1 / 17 | 1.788 | 1.468 / -0.046 |
| TabPFN-V2 / RDKit descriptors | scaffold / Ec_MBC | 1 / 105 | 1.837 | 1.439 / 0.227 |
| TabPFN-V2 / RDKit descriptors | scaffold / Ec_MIC | 1 / 105 | 1.825 | 1.502 / 0.142 |
| TabPFN-V2 / RDKit descriptors | scaffold / Sa_MBC | 1 / 105 | 2.087 | 1.614 / -0.130 |
| TabPFN-V2 / RDKit descriptors | scaffold / Sa_MIC | 1 / 105 | 1.875 | 1.565 / 0.085 |

Table S25. All fixed-source-seed human-minus-comparator paired ΔRMSE intervals. 2,000 paired cluster-bootstrap draws; negative values favour human. These unadjusted exploratory intervals condition on fitted decoders and one source seed. OOD cation grouping has 17 groups; scaffold grouping has only four families. The four-family estimates cannot be treated as stable population bounds.

| Model / scheme | Comparator | ΔRMSE / 95% interval | Grouping / groups | Exact n |
| --- | --- | --- | --- | --- |
| CatBoost (PCA control) / cation | RDKit descriptors | +0.152 [-0.012, +0.307] | cation / 103 | 420 |
| CatBoost (PCA control) / cation | Raw MolFormer | -0.123 [-0.241, -0.020] | cation / 103 | 420 |
| CatBoost (PCA control) / cation | Continuous MIC | -0.105 [-0.175, -0.034] | cation / 103 | 420 |
| CatBoost (PCA control) / cation | Binary MIC | -0.089 [-0.165, -0.016] | cation / 103 | 420 |
| CatBoost (PCA control) / scaffold | RDKit descriptors | +0.083 [-0.081, +0.269] | scaffold / 29 | 420 |
| CatBoost (PCA control) / scaffold | Raw MolFormer | -0.054 [-0.155, +0.036] | scaffold / 29 | 420 |
| CatBoost (PCA control) / scaffold | Continuous MIC | +0.009 [-0.104, +0.110] | scaffold / 29 | 420 |
| CatBoost (PCA control) / scaffold | Binary MIC | -0.069 [-0.197, +0.052] | scaffold / 29 | 420 |
| CatBoost (PCA control) / full-QAC105 | RDKit descriptors | +0.058 [-0.153, +0.296] | cation / 17 | 67 |
| CatBoost (PCA control) / full-QAC105 | RDKit descriptors | +0.058 [-0.072, +0.164] | scaffold / 4 | 67 |
| CatBoost (PCA control) / full-QAC105 | Raw MolFormer | -0.172 [-0.359, +0.030] | cation / 17 | 67 |
| CatBoost (PCA control) / full-QAC105 | Raw MolFormer | -0.172 [-0.370, -0.034] | scaffold / 4 | 67 |
| CatBoost (PCA control) / full-QAC105 | Continuous MIC | -0.226 [-0.401, -0.025] | cation / 17 | 67 |
| CatBoost (PCA control) / full-QAC105 | Continuous MIC | -0.226 [-0.415, +0.033] | scaffold / 4 | 67 |
| CatBoost (PCA control) / full-QAC105 | Binary MIC | -0.100 [-0.247, +0.027] | cation / 17 | 67 |
| CatBoost (PCA control) / full-QAC105 | Binary MIC | -0.100 [-0.261, -0.003] | scaffold / 4 | 67 |
| AutoGluon / cation | RDKit descriptors | +0.094 [-0.039, +0.230] | cation / 103 | 420 |
| AutoGluon / cation | Raw MolFormer | -0.143 [-0.268, -0.018] | cation / 103 | 420 |
| AutoGluon / cation | Continuous MIC | -0.076 [-0.147, -0.006] | cation / 103 | 420 |
| AutoGluon / cation | Binary MIC | -0.042 [-0.121, +0.033] | cation / 103 | 420 |
| AutoGluon / scaffold | RDKit descriptors | +0.106 [-0.049, +0.243] | scaffold / 29 | 420 |
| AutoGluon / scaffold | Raw MolFormer | -0.005 [-0.144, +0.156] | scaffold / 29 | 420 |
| AutoGluon / scaffold | Continuous MIC | -0.021 [-0.176, +0.132] | scaffold / 29 | 420 |
| AutoGluon / scaffold | Binary MIC | +0.022 [-0.113, +0.175] | scaffold / 29 | 420 |
| AutoGluon / full-QAC105 | RDKit descriptors | -0.074 [-0.147, -0.008] | cation / 17 | 67 |
| AutoGluon / full-QAC105 | RDKit descriptors | -0.074 [-0.124, -0.043] | scaffold / 4 | 67 |
| AutoGluon / full-QAC105 | Raw MolFormer | -0.060 [-0.201, +0.082] | cation / 17 | 67 |
| AutoGluon / full-QAC105 | Raw MolFormer | -0.060 [-0.174, +0.026] | scaffold / 4 | 67 |
| AutoGluon / full-QAC105 | Continuous MIC | -0.141 [-0.395, +0.113] | cation / 17 | 67 |
| AutoGluon / full-QAC105 | Continuous MIC | -0.141 [-0.270, +0.042] | scaffold / 4 | 67 |
| AutoGluon / full-QAC105 | Binary MIC | -0.049 [-0.112, +0.010] | cation / 17 | 67 |
| AutoGluon / full-QAC105 | Binary MIC | -0.049 [-0.158, +0.022] | scaffold / 4 | 67 |
| TabPFN-V2 / cation | RDKit descriptors | +0.097 [-0.017, +0.208] | cation / 103 | 420 |
| TabPFN-V2 / cation | Raw MolFormer | -0.126 [-0.226, -0.028] | cation / 103 | 420 |
| TabPFN-V2 / cation | Continuous MIC | -0.031 [-0.098, +0.033] | cation / 103 | 420 |
| TabPFN-V2 / cation | Binary MIC | -0.016 [-0.074, +0.041] | cation / 103 | 420 |
| TabPFN-V2 / scaffold | RDKit descriptors | -0.076 [-0.208, +0.052] | scaffold / 29 | 420 |
| TabPFN-V2 / scaffold | Raw MolFormer | -0.150 [-0.280, -0.019] | scaffold / 29 | 420 |
| TabPFN-V2 / scaffold | Continuous MIC | -0.098 [-0.207, +0.009] | scaffold / 29 | 420 |
| TabPFN-V2 / scaffold | Binary MIC | -0.087 [-0.139, -0.027] | scaffold / 29 | 420 |
| TabPFN-V2 / full-QAC105 | RDKit descriptors | -0.013 [-0.150, +0.149] | cation / 17 | 67 |
| TabPFN-V2 / full-QAC105 | RDKit descriptors | -0.013 [-0.053, +0.037] | scaffold / 4 | 67 |
| TabPFN-V2 / full-QAC105 | Raw MolFormer | -0.259 [-0.499, -0.019] | cation / 17 | 67 |
| TabPFN-V2 / full-QAC105 | Raw MolFormer | -0.259 [-0.684, -0.005] | scaffold / 4 | 67 |
| TabPFN-V2 / full-QAC105 | Continuous MIC | -0.299 [-0.540, -0.013] | cation / 17 | 67 |
| TabPFN-V2 / full-QAC105 | Continuous MIC | -0.299 [-0.736, +0.070] | scaffold / 4 | 67 |
| TabPFN-V2 / full-QAC105 | Binary MIC | -0.029 [-0.139, +0.066] | cation / 17 | 67 |
| TabPFN-V2 / full-QAC105 | Binary MIC | -0.029 [-0.167, +0.060] | scaffold / 4 | 67 |
| TabFM / cation | RDKit descriptors | +0.111 [-0.047, +0.258] | cation / 103 | 420 |
| TabFM / cation | Raw MolFormer | -0.170 [-0.290, -0.058] | cation / 103 | 420 |
| TabFM / cation | Continuous MIC | -0.042 [-0.098, +0.014] | cation / 103 | 420 |
| TabFM / cation | Binary MIC | -0.084 [-0.150, -0.019] | cation / 103 | 420 |
| TabFM / scaffold | RDKit descriptors | -0.095 [-0.211, +0.023] | scaffold / 29 | 420 |
| TabFM / scaffold | Raw MolFormer | -0.139 [-0.245, -0.047] | scaffold / 29 | 420 |
| TabFM / scaffold | Continuous MIC | -0.074 [-0.172, +0.019] | scaffold / 29 | 420 |
| TabFM / scaffold | Binary MIC | -0.123 [-0.215, -0.039] | scaffold / 29 | 420 |
| TabFM / full-QAC105 | RDKit descriptors | -0.035 [-0.162, +0.108] | cation / 17 | 67 |
| TabFM / full-QAC105 | RDKit descriptors | -0.035 [-0.064, +0.014] | scaffold / 4 | 67 |
| TabFM / full-QAC105 | Raw MolFormer | -0.307 [-0.605, -0.022] | cation / 17 | 67 |
| TabFM / full-QAC105 | Raw MolFormer | -0.307 [-0.865, +0.075] | scaffold / 4 | 67 |
| TabFM / full-QAC105 | Continuous MIC | -0.549 [-0.803, -0.247] | cation / 17 | 67 |
| TabFM / full-QAC105 | Continuous MIC | -0.549 [-0.997, -0.125] | scaffold / 4 | 67 |
| TabFM / full-QAC105 | Binary MIC | -0.119 [-0.267, +0.036] | cation / 17 | 67 |
| TabFM / full-QAC105 | Binary MIC | -0.119 [-0.320, +0.023] | scaffold / 4 | 67 |

S21.1. Exact model versions and evaluation budgets

Main Section 4.6 specifies the pipelines. Chemprop 2.3.1 uses three fixed graph seeds, 100 final-checkpoint epochs, hidden dimension 300, depth three and four outputs. AutoGluon-Tabular 1.6.3 uses RF/XT/GBM/CAT, a 60-second selection budget and extra refit time. TabPFN library 9.1.0 uses the public V2 regressor with four estimators; checkpoint SHA256 2ab5a07d5c41dfe6db9aa7ae106fc6de898326c2765be66505a07e2868c10736. TabFM package 1.0.1 uses code fbb665569425fd2f490c6576b3af967876fe11ff904 and google/tabfm-1.0.0-jax revision d5e74033fcf257699fab013e2cdd7edf424ff904, CPU float32 and four estimators. RDKit descriptors use 2026.3.6. Package and checkpoint manifests distinguish code-version changes needed for setup from the parameters of each completed fit. Each recorded script and protocol SHA maps to its saved source in server_models_20261012/code_versions.

Group assignments are fixed across decoders. All preprocessing excludes outer test and OOD rows. AutoGluon preprocessing fits on the outer training fold before its grouped internal selection split, and is therefore not independently refitted inside that inner split. OOD is never used for architecture, epoch or hyperparameter selection. Descriptor, graph and guided-feature inputs contain different prior information and receive different fixed compute budgets. The study measures performance under these declared pipelines; it does not isolate architecture at equal total data or compute.

S22. Independent reproduction and recovered notebook provenance

Table S26. Reproduction outcomes. The original v14 primary metrics remain associated with their archived batch layout. Altered-layout outputs are separately named sensitivity results, avoiding silent replacement of the primary tables.

| Experiment | Evidence | Outcome | Scope | Record |
| --- | --- | --- | --- | --- |
| v14 cached cation refits | 27,816 common predictions | Exactly equal | All saved arms and encodings | audit_repeats.json |
| v14 cached scaffold refits | 15,616 common predictions | Exactly equal | All saved scaffold arms | audit_repeats.json |
| Matched partial fine-tuning | 30 independent source-training runs | Final losses exactly equal | Six arms × five seeds | audit_repeats.json |
| Historical target representations | 93 target arrays | Byte-identical | Archived encoding layout | source_repeat_array_audit.json |
| QAC-105/OOD-17 representations | 62 target arrays | Byte-identical | Independent models; archived layout | layout_audit.json |
| Fresh QAC-105 batching | Feature changes around 10−6 | Some CatBoost predictions differ | Changed layout; replay resolves | audit_repeats.json |
| c3-MolFormer / ChemFM | Common archived predictions | Exactly equal | Declared frozen-feature repeats | audit_repeats.json |
| MolFormer / ChemBERTa / context MLP | Equal initial weights and training IDs | Mac/Linux losses and predictions differ | Exact cause not fully localised | audit_repeats.json |
| Historical Ridge sensitivity | Extreme predictions retained | Numerically unstable | Not evidence for a robust ranking | audit_repeats.json |

S22.1. Batch-layout sensitivity and checkpoint state

Fresh target encoding uses the independently retrained models but a different compound batch layout. Small floating-point changes in feature vectors alter some CatBoost splits; individual predictions can change substantially despite vector differences around 10−6. The independently retrained models reproduce all 62 original QAC-105 and OOD-17 arrays byte-for-byte when the archived layout is replayed: the original 104-compound target array is combined with the omitted compound encoded together with the same three reference compounds. This diagnostic uses structure identities and model state, not target activities or outcome-based checkpoint selection. Checkpoint reconstruction preserves all persistent and nonpersistent buffers. The exact replication refers to this pinned implementation and environment, rather than promising bitwise equality across arbitrary hardware or packages.

S22.2. Cross-environment historical branches

The frozen-feature MLP comparison includes a transition from Mac/PyTorch 2.4.1 to Linux/PyTorch 2.14, with NumPy, BLAS and hardware differences. Some branches diverge despite identical initial model hashes and training identities. These differences are not fully attributed to an individual operation. They are retained as unresolved environment sensitivities, while c3-MolFormer, ChemFM and the matched partial-fine-tuning branches reproduce exactly in their declared replay conditions. Extreme Ridge errors are preserved and are not used to support general model rankings.

S22.3. Historical numbers recovered from saved notebook outputs

The recovery inventory contains 48 saved notebook snapshots and selected April–May copies, plus the July follow-up. It records source paths, dates, hashes and cell numbers; credential literals are removed from recovered copies. The notebooks are not rerun by the recovery process. In the May task-comparison notebook, saved human categorical-task R² values are 0.7102, 0.6403, 0.4269 and 0.7394. The text-vector values are 0.7494, 0.6752, 0.5918 and 0.7708. Seven of eight agree with the v5 table after normal rounding. The Ec MIC text score rounds to 0.59 rather than the printed 0.60. Corresponding endpoint RMSE outputs are not printed in that cell, so this recovers their R² provenance rather than fully reproducing every historical metric.

Those cells stratify molecule × task rows by task identity and use CatBoost categorical task_id in the found baseline variant, not literal one-hot columns. Different endpoint rows of a molecule can cross the split. Historical source overlap is documented separately; an overlap count alone does not prove membership in the actual checkpoint training split. An April notebook searches 100 test seeds and selects seed 79, but its direct contribution to the v5 table has not been established. Finding that search therefore does not justify attributing all favourable historical scores to seed selection.

The May causal_final notebook prints raw/human/regression OOD RMSE 2.314/2.189/2.276. The July shap_causal_analysis notebook prints 2.314/2.189/2.133. The latter supports the original rounded regression value 2.13. The earlier suggestion of an arithmetic correction to 2.27 is withdrawn. Distinct execution states, encoders and validation protocols must remain distinguishable. Saved notebook code may also have been edited after its last execution; output provenance alone does not establish a clean end-to-end reproduction.

S23. Published metrics and adaptation context

Before interpreting the new comparison, primary publications and the official ChemBERTa-3 repository were checked. Table S27 preserves dataset and split context and cannot be ranked against our log2(mg/L) scores. The MoLFormer comparison uses the same rotary model family and five QM9 splits; its ± is SD. The ChemBERTa-3 repository states that ± is the range of three runs, not SD or a confidence interval. ChemFM’s antibiotic result is classification, not MIC/MBC regression. These examples motivate testing adaptation rather than assuming that fine-tuning is harmful.

Table S27. Selected verified published results. Dataset identity, units, split conventions and uncertainty definitions are not interchangeable across rows.

| Model / adaptation | Dataset / metric | Split or comparison | Reported value | Primary locator |
| --- | --- | --- | --- | --- |
| MoLFormer-XL rotary / frozen | QM9 dipole mu / MAE Debye | 80/10/10 repeated five splits; SD over five folds | 0.8089 ± 0.0205 | Table 11 |
| MoLFormer-XL rotary / fine-tuned | QM9 dipole mu / MAE Debye | 80/10/10 repeated five splits; SD over five folds | 0.3709 ± 0.0065 | Table 11 |
| c3-MoLFormer-1.1B / fine-tuned | ESOL / RMSE reported benchmark scale | MoLFormer splits; range of three runs | 0.651 ± 0.034 | official Figure 2 |
| c3-MoLFormer-1.1B / fine-tuned | ESOL / RMSE reported benchmark scale | DeepChem scaffold splits; reported plus/minus; repository range convention | 0.829 ± 0.019 | official Figure 4 |
| c3-MoLFormer-1.1B / fine-tuned | BBBP / ROC-AUC | MoLFormer splits; range of three runs | 0.900 ± 0.015 | official Figure 2 |
| c3-MoLFormer-1.1B / fine-tuned | BBBP / ROC-AUC | DeepChem scaffold splits; reported plus/minus; repository range convention | 0.735 ± 0.019 | official Figure 4 |
| ChemFM-3B / LoRA property prediction | antibiotic activity classification / PRC-AUC | original antibiotic task protocol; not reported in cited body paragraph | 0.428 | Potential discovery of novel antibiotics |
| Chemprop comparator / target-trained graph model | antibiotic activity classification / PRC-AUC | original antibiotic task protocol; not reported in cited body paragraph | 0.364 | Potential discovery of novel antibiotics |

Primary sources: Ross et al., doi:10.1038/s42256-022-00580-7, author manuscript https://arxiv.org/html/2106.09553v3, Table 11; Singh et al., doi:10.1039/D5DD00348B, official repository https://github.com/deepforestsci/chemberta3 and its two benchmark figures, pinned commit 706f58472c351825960edc05ee9dd9aebd7bec6c; Cai, Zacour et al., doi:10.1038/s42004-025-01793-8, antibiotic-discovery results and training-efficiency subsection. The latter reports 6.5 million trainable parameters for rank-four LoRA on ChemFM-3B. Our query/value rank-eight MolFormer adapter is a separate recipe. Published ESOL values are retained on their reported benchmark scale; no conversion to QAC concentration is attempted. The complete audit and figure hashes are in server_finetune_causal_20261012/literature.

S24. Direct four-target fine-tuning

All 363 direct fits completed. Three source/target seeds are paired one-to-one. No adaptation configuration is selected on OOD. All fits have 30 epochs (90 CV updates, or 120 updates in final QAC-105 training); train-only target standardisation is inverted before scoring in log2(mg/L). Train/test IDs, parameters, head hashes, batch-order hashes, curves and predictions are archived. Partially and fully trained CV backbone weights are identified by hashes and replay recipes; full final-OOD trainable weights are retained on the server.

Table S28. Complete direct-target pooled errors, matching main Table 6. Means and SD describe three seed-specific scores, not an ensemble.

| Initialisation / target adaptation | Trainable parameters | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| Pretrained / Frozen + linear | 4,612 | 2.013 ± 0.006 | 1.986 ± 0.003 | 2.560 ± 0.206 |
| Pretrained / Frozen + MLP | 231,812 | 1.981 ± 0.015 | 2.009 ± 0.007 | 2.864 ± 0.082 |
| Pretrained / LoRA | 299,524 | 2.040 ± 0.049 | 2.089 ± 0.012 | 2.756 ± 0.172 |
| Pretrained / Partial FT | 28,379,140 | 1.894 ± 0.037 | 1.996 ± 0.034 | 3.008 ± 0.427 |
| Pretrained / Full FT | 44,379,652 | 1.863 ± 0.045 | 1.970 ± 0.026 | 3.032 ± 0.408 |
| Human / Partial FT | 28,379,140 | 1.797 ± 0.057 | 1.834 ± 0.058 | 2.412 ± 0.088 |
| Continuous MIC / Partial FT | 28,379,140 | 1.737 ± 0.007 | 1.869 ± 0.014 | 3.075 ± 0.335 |
| Binary MIC / Partial FT | 28,379,140 | 1.745 ± 0.055 | 1.901 ± 0.044 | 2.510 ± 0.137 |
| Shuffled human / Partial FT | 28,379,140 | 1.929 ± 0.070 | 1.990 ± 0.022 | 2.963 ± 0.456 |
| Shuffled continuous MIC / Partial FT | 28,379,140 | 1.820 ± 0.039 | 1.907 ± 0.062 | 3.116 ± 0.195 |
| Shuffled binary MIC / Partial FT | 28,379,140 | 1.945 ± 0.052 | 2.027 ± 0.049 | 3.076 ± 0.568 |

Table S29. All direct-target endpoint scores. RMSE and MAE are mean ± SD over three paired seeds. R² and Spearman are means of seed-specific scores. QAC has 105 exact values per task; OOD has 17 except Ec_MBC, which has 16.

| Initialisation / adaptation | Regime / endpoint | Seeds / n | RMSE | MAE / R² / Spearman |
| --- | --- | --- | --- | --- |
| Human / Partial FT | cation / Ec_MBC | 3 / 105 | 1.847 ± 0.100 | 1.439 ± 0.109 / 0.217 / 0.513 |
| Human / Partial FT | cation / Ec_MIC | 3 / 105 | 1.653 ± 0.103 | 1.239 ± 0.107 / 0.295 / 0.572 |
| Human / Partial FT | cation / Sa_MBC | 3 / 105 | 1.855 ± 0.025 | 1.360 ± 0.069 / 0.107 / 0.444 |
| Human / Partial FT | cation / Sa_MIC | 3 / 105 | 1.822 ± 0.050 | 1.370 ± 0.060 / 0.135 / 0.481 |
| Human / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 2.660 ± 0.241 | 2.134 ± 0.195 / -0.818 / 0.385 |
| Human / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 2.267 ± 0.322 | 1.944 ± 0.267 / -0.573 / 0.640 |
| Human / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 2.522 ± 0.180 | 2.037 ± 0.084 / -0.424 / 0.115 |
| Human / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.149 ± 0.247 | 1.832 ± 0.242 / -0.522 / -0.088 |
| Human / Partial FT | scaffold / Ec_MBC | 3 / 105 | 1.842 ± 0.046 | 1.456 ± 0.036 / 0.222 / 0.522 |
| Human / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.751 ± 0.059 | 1.391 ± 0.056 / 0.210 / 0.530 |
| Human / Partial FT | scaffold / Sa_MBC | 3 / 105 | 1.925 ± 0.080 | 1.395 ± 0.033 / 0.037 / 0.397 |
| Human / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.815 ± 0.056 | 1.387 ± 0.044 / 0.142 / 0.456 |
| Shuffled human / Partial FT | cation / Ec_MBC | 3 / 105 | 2.008 ± 0.045 | 1.638 ± 0.038 / 0.076 / 0.311 |
| Shuffled human / Partial FT | cation / Ec_MIC | 3 / 105 | 1.780 ± 0.080 | 1.395 ± 0.071 / 0.183 / 0.429 |
| Shuffled human / Partial FT | cation / Sa_MBC | 3 / 105 | 2.008 ± 0.106 | 1.498 ± 0.075 / -0.048 / 0.261 |
| Shuffled human / Partial FT | cation / Sa_MIC | 3 / 105 | 1.908 ± 0.069 | 1.465 ± 0.072 / 0.051 / 0.377 |
| Shuffled human / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 3.251 ± 0.336 | 2.485 ± 0.246 / -1.720 / -0.059 |
| Shuffled human / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 3.165 ± 0.678 | 2.583 ± 0.610 / -2.118 / -0.019 |
| Shuffled human / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 3.012 ± 0.353 | 2.602 ± 0.378 / -1.042 / -0.197 |
| Shuffled human / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.332 ± 0.565 | 1.981 ± 0.493 / -0.847 / -0.417 |
| Shuffled human / Partial FT | scaffold / Ec_MBC | 3 / 105 | 2.016 ± 0.070 | 1.614 ± 0.048 / 0.068 / 0.336 |
| Shuffled human / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.921 ± 0.060 | 1.499 ± 0.046 / 0.049 / 0.324 |
| Shuffled human / Partial FT | scaffold / Sa_MBC | 3 / 105 | 2.102 ± 0.035 | 1.593 ± 0.032 / -0.146 / 0.143 |
| Shuffled human / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.914 ± 0.031 | 1.481 ± 0.027 / 0.045 / 0.355 |
| Binary MIC / Partial FT | cation / Ec_MBC | 3 / 105 | 1.811 ± 0.057 | 1.421 ± 0.061 / 0.248 / 0.527 |
| Binary MIC / Partial FT | cation / Ec_MIC | 3 / 105 | 1.591 ± 0.070 | 1.210 ± 0.045 / 0.347 / 0.603 |
| Binary MIC / Partial FT | cation / Sa_MBC | 3 / 105 | 1.805 ± 0.079 | 1.332 ± 0.080 / 0.154 / 0.491 |
| Binary MIC / Partial FT | cation / Sa_MIC | 3 / 105 | 1.761 ± 0.068 | 1.313 ± 0.080 / 0.191 / 0.523 |
| Binary MIC / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 2.696 ± 0.071 | 2.180 ± 0.141 / -0.859 / 0.298 |
| Binary MIC / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 2.413 ± 0.342 | 2.055 ± 0.325 / -0.783 / 0.469 |
| Binary MIC / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 2.571 ± 0.130 | 2.108 ± 0.088 / -0.477 / 0.191 |
| Binary MIC / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.346 ± 0.089 | 2.080 ± 0.083 / -0.801 / -0.297 |
| Binary MIC / Partial FT | scaffold / Ec_MBC | 3 / 105 | 1.969 ± 0.044 | 1.564 ± 0.021 / 0.112 / 0.441 |
| Binary MIC / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.852 ± 0.097 | 1.460 ± 0.067 / 0.115 / 0.455 |
| Binary MIC / Partial FT | scaffold / Sa_MBC | 3 / 105 | 1.972 ± 0.030 | 1.468 ± 0.051 / -0.009 / 0.356 |
| Binary MIC / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.806 ± 0.057 | 1.371 ± 0.038 / 0.150 / 0.466 |
| Shuffled binary MIC / Partial FT | cation / Ec_MBC | 3 / 105 | 2.026 ± 0.074 | 1.656 ± 0.060 / 0.059 / 0.284 |
| Shuffled binary MIC / Partial FT | cation / Ec_MIC | 3 / 105 | 1.802 ± 0.089 | 1.415 ± 0.071 / 0.162 / 0.414 |
| Shuffled binary MIC / Partial FT | cation / Sa_MBC | 3 / 105 | 2.014 ± 0.028 | 1.520 ± 0.027 / -0.053 / 0.216 |
| Shuffled binary MIC / Partial FT | cation / Sa_MIC | 3 / 105 | 1.927 ± 0.064 | 1.477 ± 0.053 / 0.032 / 0.364 |
| Shuffled binary MIC / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 3.332 ± 0.446 | 2.522 ± 0.318 / -1.872 / -0.203 |
| Shuffled binary MIC / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 3.268 ± 0.819 | 2.591 ± 0.694 / -2.361 / -0.243 |
| Shuffled binary MIC / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 3.164 ± 0.532 | 2.723 ± 0.518 / -1.275 / -0.255 |
| Shuffled binary MIC / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.458 ± 0.527 | 2.132 ± 0.494 / -1.036 / -0.344 |
| Shuffled binary MIC / Partial FT | scaffold / Ec_MBC | 3 / 105 | 2.065 ± 0.071 | 1.643 ± 0.094 / 0.022 / 0.298 |
| Shuffled binary MIC / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.960 ± 0.014 | 1.536 ± 0.035 / 0.011 / 0.275 |
| Shuffled binary MIC / Partial FT | scaffold / Sa_MBC | 3 / 105 | 2.117 ± 0.116 | 1.614 ± 0.099 / -0.165 / 0.108 |
| Shuffled binary MIC / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.960 ± 0.076 | 1.549 ± 0.048 / -0.001 / 0.322 |
| Continuous MIC / Partial FT | cation / Ec_MBC | 3 / 105 | 1.796 ± 0.081 | 1.390 ± 0.101 / 0.260 / 0.539 |
| Continuous MIC / Partial FT | cation / Ec_MIC | 3 / 105 | 1.568 ± 0.024 | 1.199 ± 0.016 / 0.367 / 0.608 |
| Continuous MIC / Partial FT | cation / Sa_MBC | 3 / 105 | 1.779 ± 0.018 | 1.325 ± 0.054 / 0.179 / 0.511 |
| Continuous MIC / Partial FT | cation / Sa_MIC | 3 / 105 | 1.792 ± 0.069 | 1.359 ± 0.077 / 0.163 / 0.508 |
| Continuous MIC / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 3.578 ± 0.444 | 2.853 ± 0.354 / -2.306 / 0.045 |
| Continuous MIC / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 3.227 ± 0.469 | 2.700 ± 0.376 / -2.190 / 0.299 |
| Continuous MIC / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 3.079 ± 0.171 | 2.637 ± 0.301 / -1.119 / 0.012 |
| Continuous MIC / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.300 ± 0.282 | 1.958 ± 0.213 / -0.746 / -0.141 |
| Continuous MIC / Partial FT | scaffold / Ec_MBC | 3 / 105 | 1.893 ± 0.065 | 1.513 ± 0.033 / 0.178 / 0.510 |
| Continuous MIC / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.820 ± 0.039 | 1.443 ± 0.067 / 0.147 / 0.508 |
| Continuous MIC / Partial FT | scaffold / Sa_MBC | 3 / 105 | 1.958 ± 0.047 | 1.466 ± 0.063 / 0.006 / 0.363 |
| Continuous MIC / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.799 ± 0.038 | 1.391 ± 0.056 / 0.157 / 0.485 |
| Shuffled continuous MIC / Partial FT | cation / Ec_MBC | 3 / 105 | 1.866 ± 0.079 | 1.507 ± 0.084 / 0.202 / 0.433 |
| Shuffled continuous MIC / Partial FT | cation / Ec_MIC | 3 / 105 | 1.647 ± 0.035 | 1.301 ± 0.052 / 0.301 / 0.527 |
| Shuffled continuous MIC / Partial FT | cation / Sa_MBC | 3 / 105 | 1.916 ± 0.007 | 1.447 ± 0.024 / 0.047 / 0.321 |
| Shuffled continuous MIC / Partial FT | cation / Sa_MIC | 3 / 105 | 1.838 ± 0.052 | 1.426 ± 0.056 / 0.120 / 0.425 |
| Shuffled continuous MIC / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 3.349 ± 0.243 | 2.574 ± 0.191 / -1.877 / -0.040 |
| Shuffled continuous MIC / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 3.368 ± 0.377 | 2.724 ± 0.189 / -2.454 / 0.102 |
| Shuffled continuous MIC / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 3.305 ± 0.163 | 2.809 ± 0.193 / -1.440 / -0.122 |
| Shuffled continuous MIC / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.315 ± 0.265 | 1.977 ± 0.203 / -0.768 / -0.318 |
| Shuffled continuous MIC / Partial FT | scaffold / Ec_MBC | 3 / 105 | 1.887 ± 0.075 | 1.497 ± 0.086 / 0.183 / 0.441 |
| Shuffled continuous MIC / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.805 ± 0.117 | 1.426 ± 0.108 / 0.159 / 0.440 |
| Shuffled continuous MIC / Partial FT | scaffold / Sa_MBC | 3 / 105 | 2.055 ± 0.081 | 1.567 ± 0.051 / -0.097 / 0.231 |
| Shuffled continuous MIC / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.870 ± 0.079 | 1.475 ± 0.049 / 0.088 / 0.409 |
| Pretrained / Frozen + MLP | cation / Ec_MBC | 3 / 105 | 2.037 ± 0.018 | 1.671 ± 0.020 / 0.049 / 0.296 |
| Pretrained / Frozen + MLP | cation / Ec_MIC | 3 / 105 | 1.860 ± 0.018 | 1.491 ± 0.020 / 0.109 / 0.376 |
| Pretrained / Frozen + MLP | cation / Sa_MBC | 3 / 105 | 2.082 ± 0.012 | 1.583 ± 0.007 / -0.125 / 0.054 |
| Pretrained / Frozen + MLP | cation / Sa_MIC | 3 / 105 | 1.936 ± 0.019 | 1.512 ± 0.002 / 0.024 / 0.333 |
| Pretrained / Frozen + MLP | full-QAC105 / Ec_MBC | 3 / 16 | 3.280 ± 0.096 | 2.268 ± 0.072 / -1.752 / -0.279 |
| Pretrained / Frozen + MLP | full-QAC105 / Ec_MIC | 3 / 17 | 3.489 ± 0.151 | 2.567 ± 0.150 / -2.682 / -0.377 |
| Pretrained / Frozen + MLP | full-QAC105 / Sa_MBC | 3 / 17 | 2.447 ± 0.041 | 2.116 ± 0.010 / -0.336 / -0.169 |
| Pretrained / Frozen + MLP | full-QAC105 / Sa_MIC | 3 / 17 | 2.010 ± 0.045 | 1.657 ± 0.027 / -0.321 / -0.141 |
| Pretrained / Frozen + MLP | scaffold / Ec_MBC | 3 / 105 | 2.037 ± 0.001 | 1.669 ± 0.007 / 0.050 / 0.306 |
| Pretrained / Frozen + MLP | scaffold / Ec_MIC | 3 / 105 | 1.970 ± 0.016 | 1.559 ± 0.025 / 0.001 / 0.260 |
| Pretrained / Frozen + MLP | scaffold / Sa_MBC | 3 / 105 | 2.093 ± 0.014 | 1.566 ± 0.015 / -0.136 / 0.084 |
| Pretrained / Frozen + MLP | scaffold / Sa_MIC | 3 / 105 | 1.931 ± 0.021 | 1.485 ± 0.009 / 0.029 / 0.368 |
| Pretrained / Full FT | cation / Ec_MBC | 3 / 105 | 1.911 ± 0.062 | 1.548 ± 0.062 / 0.163 / 0.375 |
| Pretrained / Full FT | cation / Ec_MIC | 3 / 105 | 1.702 ± 0.033 | 1.325 ± 0.026 / 0.253 / 0.493 |
| Pretrained / Full FT | cation / Sa_MBC | 3 / 105 | 1.977 ± 0.075 | 1.462 ± 0.047 / -0.015 / 0.248 |
| Pretrained / Full FT | cation / Sa_MIC | 3 / 105 | 1.850 ± 0.012 | 1.431 ± 0.022 / 0.109 / 0.410 |
| Pretrained / Full FT | full-QAC105 / Ec_MBC | 3 / 16 | 3.308 ± 0.574 | 2.518 ± 0.341 / -1.854 / -0.081 |
| Pretrained / Full FT | full-QAC105 / Ec_MIC | 3 / 17 | 3.356 ± 0.724 | 2.724 ± 0.582 / -2.507 / -0.056 |
| Pretrained / Full FT | full-QAC105 / Sa_MBC | 3 / 17 | 3.087 ± 0.103 | 2.605 ± 0.171 / -1.127 / -0.192 |
| Pretrained / Full FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.228 ± 0.256 | 1.886 ± 0.208 / -0.637 / -0.444 |
| Pretrained / Full FT | scaffold / Ec_MBC | 3 / 105 | 1.947 ± 0.052 | 1.568 ± 0.061 / 0.131 / 0.380 |
| Pretrained / Full FT | scaffold / Ec_MIC | 3 / 105 | 1.897 ± 0.020 | 1.502 ± 0.035 / 0.073 / 0.341 |
| Pretrained / Full FT | scaffold / Sa_MBC | 3 / 105 | 2.125 ± 0.023 | 1.598 ± 0.026 / -0.172 / 0.124 |
| Pretrained / Full FT | scaffold / Sa_MIC | 3 / 105 | 1.902 ± 0.053 | 1.475 ± 0.030 / 0.057 / 0.370 |
| Pretrained / Frozen + linear | cation / Ec_MBC | 3 / 105 | 2.079 ± 0.019 | 1.688 ± 0.017 / 0.010 / 0.219 |
| Pretrained / Frozen + linear | cation / Ec_MIC | 3 / 105 | 1.931 ± 0.020 | 1.522 ± 0.014 / 0.039 / 0.257 |
| Pretrained / Frozen + linear | cation / Sa_MBC | 3 / 105 | 2.082 ± 0.008 | 1.584 ± 0.008 / -0.124 / 0.004 |
| Pretrained / Frozen + linear | cation / Sa_MIC | 3 / 105 | 1.957 ± 0.031 | 1.543 ± 0.021 / 0.002 / 0.300 |
| Pretrained / Frozen + linear | full-QAC105 / Ec_MBC | 3 / 16 | 2.878 ± 0.225 | 1.997 ± 0.127 / -1.125 / -0.279 |
| Pretrained / Frozen + linear | full-QAC105 / Ec_MIC | 3 / 17 | 2.965 ± 0.371 | 2.170 ± 0.240 / -1.683 / -0.322 |
| Pretrained / Frozen + linear | full-QAC105 / Sa_MBC | 3 / 17 | 2.378 ± 0.117 | 2.041 ± 0.137 / -0.264 / -0.311 |
| Pretrained / Frozen + linear | full-QAC105 / Sa_MIC | 3 / 17 | 1.890 ± 0.103 | 1.573 ± 0.075 / -0.170 / -0.204 |
| Pretrained / Frozen + linear | scaffold / Ec_MBC | 3 / 105 | 2.020 ± 0.010 | 1.630 ± 0.016 / 0.065 / 0.281 |
| Pretrained / Frozen + linear | scaffold / Ec_MIC | 3 / 105 | 1.960 ± 0.006 | 1.523 ± 0.017 / 0.011 / 0.229 |
| Pretrained / Frozen + linear | scaffold / Sa_MBC | 3 / 105 | 2.076 ± 0.013 | 1.558 ± 0.013 / -0.118 / 0.009 |
| Pretrained / Frozen + linear | scaffold / Sa_MIC | 3 / 105 | 1.881 ± 0.011 | 1.460 ± 0.019 / 0.078 / 0.391 |
| Pretrained / LoRA | cation / Ec_MBC | 3 / 105 | 2.093 ± 0.060 | 1.731 ± 0.058 / -0.005 / 0.267 |
| Pretrained / LoRA | cation / Ec_MIC | 3 / 105 | 1.916 ± 0.103 | 1.537 ± 0.108 / 0.052 / 0.306 |
| Pretrained / LoRA | cation / Sa_MBC | 3 / 105 | 2.145 ± 0.020 | 1.637 ± 0.018 / -0.194 / 0.015 |
| Pretrained / LoRA | cation / Sa_MIC | 3 / 105 | 1.998 ± 0.060 | 1.561 ± 0.018 / -0.040 / 0.313 |
| Pretrained / LoRA | full-QAC105 / Ec_MBC | 3 / 16 | 3.057 ± 0.172 | 2.294 ± 0.032 / -1.393 / -0.148 |
| Pretrained / LoRA | full-QAC105 / Ec_MIC | 3 / 17 | 3.244 ± 0.365 | 2.546 ± 0.208 / -2.206 / -0.349 |
| Pretrained / LoRA | full-QAC105 / Sa_MBC | 3 / 17 | 2.616 ± 0.026 | 2.235 ± 0.094 / -0.526 / -0.135 |
| Pretrained / LoRA | full-QAC105 / Sa_MIC | 3 / 17 | 1.932 ± 0.091 | 1.674 ± 0.139 / -0.222 / -0.118 |
| Pretrained / LoRA | scaffold / Ec_MBC | 3 / 105 | 2.104 ± 0.011 | 1.709 ± 0.016 / -0.014 / 0.229 |
| Pretrained / LoRA | scaffold / Ec_MIC | 3 / 105 | 2.048 ± 0.033 | 1.618 ± 0.007 / -0.080 / 0.182 |
| Pretrained / LoRA | scaffold / Sa_MBC | 3 / 105 | 2.220 ± 0.036 | 1.656 ± 0.014 / -0.278 / -0.041 |
| Pretrained / LoRA | scaffold / Sa_MIC | 3 / 105 | 1.976 ± 0.034 | 1.549 ± 0.011 / -0.018 / 0.306 |
| Pretrained / Partial FT | cation / Ec_MBC | 3 / 105 | 1.958 ± 0.046 | 1.607 ± 0.042 / 0.121 / 0.349 |
| Pretrained / Partial FT | cation / Ec_MIC | 3 / 105 | 1.734 ± 0.049 | 1.352 ± 0.024 / 0.225 / 0.473 |
| Pretrained / Partial FT | cation / Sa_MBC | 3 / 105 | 2.009 ± 0.051 | 1.493 ± 0.030 / -0.047 / 0.206 |
| Pretrained / Partial FT | cation / Sa_MIC | 3 / 105 | 1.865 ± 0.017 | 1.433 ± 0.008 / 0.094 / 0.403 |
| Pretrained / Partial FT | full-QAC105 / Ec_MBC | 3 / 16 | 3.297 ± 0.610 | 2.504 ± 0.367 / -1.842 / -0.065 |
| Pretrained / Partial FT | full-QAC105 / Ec_MIC | 3 / 17 | 3.384 ± 0.665 | 2.734 ± 0.530 / -2.548 / -0.069 |
| Pretrained / Partial FT | full-QAC105 / Sa_MBC | 3 / 17 | 3.029 ± 0.181 | 2.557 ± 0.256 / -1.052 / -0.221 |
| Pretrained / Partial FT | full-QAC105 / Sa_MIC | 3 / 17 | 2.162 ± 0.290 | 1.843 ± 0.249 / -0.547 / -0.327 |
| Pretrained / Partial FT | scaffold / Ec_MBC | 3 / 105 | 1.980 ± 0.036 | 1.597 ± 0.047 / 0.101 / 0.342 |
| Pretrained / Partial FT | scaffold / Ec_MIC | 3 / 105 | 1.930 ± 0.022 | 1.523 ± 0.027 / 0.041 / 0.300 |
| Pretrained / Partial FT | scaffold / Sa_MBC | 3 / 105 | 2.143 ± 0.067 | 1.609 ± 0.054 / -0.193 / 0.085 |
| Pretrained / Partial FT | scaffold / Sa_MIC | 3 / 105 | 1.924 ± 0.047 | 1.497 ± 0.037 / 0.036 / 0.348 |

S25. Encoder-weight controls and both prediction routes

All 1,331 decoder fits completed. Six source arms × five seeds × four encoder states are evaluated in each of three regimes, alongside one pure raw reference. Encoder buffers are fixed across interventions; the decoder is independently refitted. Source arms share buffer state within each seed. Restoring all weights makes all six representations and all their decoder predictions identical within every seed/regime. Restoring just one component may interact with the remaining adapted weights; component effects are not additive.

Table S30. Every pooled weight-control score. Mean ± SD is over five source seeds; the pure raw reference has one fixed fit per split.

| Source supervision | Encoder state / regime | Seeds / exact pairs | RMSE | MAE |
| --- | --- | --- | --- | --- |
| Human | Intact / cation | 5 / 420 | 1.737 ± 0.032 | 1.314 ± 0.039 |
| Human | Intact / full-QAC105 | 5 / 67 | 2.054 ± 0.093 | 1.649 ± 0.035 |
| Human | Intact / scaffold | 5 / 420 | 1.842 ± 0.044 | 1.410 ± 0.048 |
| Human | Rewind all weights / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Human | Rewind all weights / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Human | Rewind all weights / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Human | Rewind eight blocks / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Human | Rewind eight blocks / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Human | Rewind eight blocks / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.024 |
| Human | Rewind outer norm / cation | 5 / 420 | 1.737 ± 0.032 | 1.314 ± 0.039 |
| Human | Rewind outer norm / full-QAC105 | 5 / 67 | 2.054 ± 0.093 | 1.649 ± 0.035 |
| Human | Rewind outer norm / scaffold | 5 / 420 | 1.842 ± 0.044 | 1.410 ± 0.048 |
| Shuffled human | Intact / cation | 5 / 420 | 1.857 ± 0.034 | 1.433 ± 0.038 |
| Shuffled human | Intact / full-QAC105 | 5 / 67 | 2.336 ± 0.116 | 1.863 ± 0.084 |
| Shuffled human | Intact / scaffold | 5 / 420 | 1.963 ± 0.047 | 1.543 ± 0.047 |
| Shuffled human | Rewind all weights / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Shuffled human | Rewind all weights / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Shuffled human | Rewind all weights / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Shuffled human | Rewind eight blocks / cation | 5 / 420 | 1.847 ± 0.047 | 1.431 ± 0.042 |
| Shuffled human | Rewind eight blocks / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Shuffled human | Rewind eight blocks / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.024 |
| Shuffled human | Rewind outer norm / cation | 5 / 420 | 1.858 ± 0.034 | 1.434 ± 0.035 |
| Shuffled human | Rewind outer norm / full-QAC105 | 5 / 67 | 2.336 ± 0.116 | 1.863 ± 0.084 |
| Shuffled human | Rewind outer norm / scaffold | 5 / 420 | 1.963 ± 0.047 | 1.542 ± 0.047 |
| Binary MIC | Intact / cation | 5 / 420 | 1.806 ± 0.057 | 1.358 ± 0.054 |
| Binary MIC | Intact / full-QAC105 | 5 / 67 | 2.099 ± 0.076 | 1.706 ± 0.053 |
| Binary MIC | Intact / scaffold | 5 / 420 | 1.856 ± 0.070 | 1.423 ± 0.046 |
| Binary MIC | Rewind all weights / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Binary MIC | Rewind all weights / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Binary MIC | Rewind all weights / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Binary MIC | Rewind eight blocks / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Binary MIC | Rewind eight blocks / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Binary MIC | Rewind eight blocks / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.024 |
| Binary MIC | Rewind outer norm / cation | 5 / 420 | 1.806 ± 0.057 | 1.358 ± 0.054 |
| Binary MIC | Rewind outer norm / full-QAC105 | 5 / 67 | 2.099 ± 0.076 | 1.706 ± 0.053 |
| Binary MIC | Rewind outer norm / scaffold | 5 / 420 | 1.856 ± 0.070 | 1.423 ± 0.046 |
| Shuffled binary MIC | Intact / cation | 5 / 420 | 1.889 ± 0.079 | 1.466 ± 0.062 |
| Shuffled binary MIC | Intact / full-QAC105 | 5 / 67 | 2.373 ± 0.161 | 1.921 ± 0.138 |
| Shuffled binary MIC | Intact / scaffold | 5 / 420 | 1.966 ± 0.085 | 1.544 ± 0.076 |
| Shuffled binary MIC | Rewind all weights / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Shuffled binary MIC | Rewind all weights / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Shuffled binary MIC | Rewind all weights / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Shuffled binary MIC | Rewind eight blocks / cation | 5 / 420 | 1.845 ± 0.044 | 1.430 ± 0.041 |
| Shuffled binary MIC | Rewind eight blocks / full-QAC105 | 5 / 67 | 2.294 ± 0.186 | 1.835 ± 0.103 |
| Shuffled binary MIC | Rewind eight blocks / scaffold | 5 / 420 | 1.939 ± 0.038 | 1.525 ± 0.026 |
| Shuffled binary MIC | Rewind outer norm / cation | 5 / 420 | 1.890 ± 0.079 | 1.466 ± 0.062 |
| Shuffled binary MIC | Rewind outer norm / full-QAC105 | 5 / 67 | 2.373 ± 0.161 | 1.921 ± 0.138 |
| Shuffled binary MIC | Rewind outer norm / scaffold | 5 / 420 | 1.966 ± 0.085 | 1.544 ± 0.076 |
| Continuous MIC | Intact / cation | 5 / 420 | 1.715 ± 0.045 | 1.288 ± 0.035 |
| Continuous MIC | Intact / full-QAC105 | 5 / 67 | 2.237 ± 0.023 | 1.744 ± 0.033 |
| Continuous MIC | Intact / scaffold | 5 / 420 | 1.814 ± 0.035 | 1.388 ± 0.026 |
| Continuous MIC | Rewind all weights / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Continuous MIC | Rewind all weights / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Continuous MIC | Rewind all weights / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Continuous MIC | Rewind eight blocks / cation | 5 / 420 | 1.847 ± 0.047 | 1.431 ± 0.042 |
| Continuous MIC | Rewind eight blocks / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Continuous MIC | Rewind eight blocks / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Continuous MIC | Rewind outer norm / cation | 5 / 420 | 1.715 ± 0.045 | 1.288 ± 0.035 |
| Continuous MIC | Rewind outer norm / full-QAC105 | 5 / 67 | 2.237 ± 0.023 | 1.744 ± 0.033 |
| Continuous MIC | Rewind outer norm / scaffold | 5 / 420 | 1.814 ± 0.035 | 1.388 ± 0.026 |
| Shuffled continuous MIC | Intact / cation | 5 / 420 | 1.872 ± 0.040 | 1.449 ± 0.035 |
| Shuffled continuous MIC | Intact / full-QAC105 | 5 / 67 | 2.277 ± 0.084 | 1.844 ± 0.066 |
| Shuffled continuous MIC | Intact / scaffold | 5 / 420 | 1.945 ± 0.015 | 1.537 ± 0.029 |
| Shuffled continuous MIC | Rewind all weights / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Shuffled continuous MIC | Rewind all weights / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Shuffled continuous MIC | Rewind all weights / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Shuffled continuous MIC | Rewind eight blocks / cation | 5 / 420 | 1.846 ± 0.047 | 1.430 ± 0.042 |
| Shuffled continuous MIC | Rewind eight blocks / full-QAC105 | 5 / 67 | 2.297 ± 0.180 | 1.832 ± 0.108 |
| Shuffled continuous MIC | Rewind eight blocks / scaffold | 5 / 420 | 1.938 ± 0.037 | 1.523 ± 0.025 |
| Shuffled continuous MIC | Rewind outer norm / cation | 5 / 420 | 1.872 ± 0.040 | 1.449 ± 0.035 |
| Shuffled continuous MIC | Rewind outer norm / full-QAC105 | 5 / 67 | 2.277 ± 0.084 | 1.844 ± 0.066 |
| Shuffled continuous MIC | Rewind outer norm / scaffold | 5 / 420 | 1.945 ± 0.015 | 1.537 ± 0.029 |
| Pretrained | Pure pretrained / cation | 1 / 420 | 1.858 | 1.455 |
| Pretrained | Pure pretrained / full-QAC105 | 1 / 67 | 2.265 | 1.854 |
| Pretrained | Pure pretrained / scaffold | 1 / 420 | 1.978 | 1.555 |

Table S31. Every endpoint score after encoder-weight controls. Pooled R² is excluded from within-task interpretation.

| Initialisation / adaptation | Regime / endpoint | Seeds / n | RMSE | MAE / R² / Spearman |
| --- | --- | --- | --- | --- |
| Human / Intact | cation / Ec_MBC | 5 / 105 | 1.763 ± 0.055 | 1.380 ± 0.064 / 0.288 / 0.538 |
| Human / Intact | cation / Ec_MIC | 5 / 105 | 1.640 ± 0.051 | 1.240 ± 0.055 / 0.307 / 0.569 |
| Human / Intact | cation / Sa_MBC | 5 / 105 | 1.832 ± 0.045 | 1.330 ± 0.040 / 0.129 / 0.402 |
| Human / Intact | cation / Sa_MIC | 5 / 105 | 1.707 ± 0.025 | 1.308 ± 0.039 / 0.241 / 0.473 |
| Human / Intact | full-QAC105 / Ec_MBC | 5 / 16 | 2.195 ± 0.133 | 1.690 ± 0.013 / -0.235 / 0.088 |
| Human / Intact | full-QAC105 / Ec_MIC | 5 / 17 | 2.074 ± 0.171 | 1.669 ± 0.111 / -0.306 / 0.342 |
| Human / Intact | full-QAC105 / Sa_MBC | 5 / 17 | 2.066 ± 0.119 | 1.704 ± 0.094 / 0.045 / 0.138 |
| Human / Intact | full-QAC105 / Sa_MIC | 5 / 17 | 1.868 ± 0.148 | 1.535 ± 0.130 / -0.147 / 0.050 |
| Human / Intact | scaffold / Ec_MBC | 5 / 105 | 1.825 ± 0.062 | 1.419 ± 0.065 / 0.236 / 0.512 |
| Human / Intact | scaffold / Ec_MIC | 5 / 105 | 1.722 ± 0.075 | 1.305 ± 0.083 / 0.235 / 0.525 |
| Human / Intact | scaffold / Sa_MBC | 5 / 105 | 1.980 ± 0.020 | 1.469 ± 0.040 / -0.017 / 0.219 |
| Human / Intact | scaffold / Sa_MIC | 5 / 105 | 1.829 ± 0.042 | 1.448 ± 0.057 / 0.129 / 0.370 |
| Human / Rewind all weights | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Human / Rewind all weights | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Human / Rewind all weights | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Human / Rewind all weights | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Human / Rewind all weights | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Human / Rewind all weights | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Human / Rewind all weights | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Human / Rewind all weights | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Human / Rewind all weights | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Human / Rewind all weights | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Human / Rewind all weights | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Human / Rewind all weights | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Human / Rewind eight blocks | cation / Ec_MBC | 5 / 105 | 1.924 ± 0.059 | 1.549 ± 0.055 / 0.151 / 0.369 |
| Human / Rewind eight blocks | cation / Ec_MIC | 5 / 105 | 1.772 ± 0.041 | 1.365 ± 0.043 / 0.191 / 0.421 |
| Human / Rewind eight blocks | cation / Sa_MBC | 5 / 105 | 1.905 ± 0.056 | 1.423 ± 0.035 / 0.058 / 0.278 |
| Human / Rewind eight blocks | cation / Sa_MIC | 5 / 105 | 1.776 ± 0.044 | 1.383 ± 0.053 / 0.178 / 0.413 |
| Human / Rewind eight blocks | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Human / Rewind eight blocks | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Human / Rewind eight blocks | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Human / Rewind eight blocks | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Human / Rewind eight blocks | scaffold / Ec_MBC | 5 / 105 | 1.959 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Human / Rewind eight blocks | scaffold / Ec_MIC | 5 / 105 | 1.863 ± 0.034 | 1.452 ± 0.033 / 0.106 / 0.341 |
| Human / Rewind eight blocks | scaffold / Sa_MBC | 5 / 105 | 2.024 ± 0.060 | 1.532 ± 0.038 / -0.063 / 0.134 |
| Human / Rewind eight blocks | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.018 / 0.057 / 0.274 |
| Human / Rewind outer norm | cation / Ec_MBC | 5 / 105 | 1.763 ± 0.055 | 1.380 ± 0.064 / 0.288 / 0.538 |
| Human / Rewind outer norm | cation / Ec_MIC | 5 / 105 | 1.640 ± 0.051 | 1.240 ± 0.055 / 0.307 / 0.569 |
| Human / Rewind outer norm | cation / Sa_MBC | 5 / 105 | 1.832 ± 0.045 | 1.330 ± 0.040 / 0.129 / 0.402 |
| Human / Rewind outer norm | cation / Sa_MIC | 5 / 105 | 1.707 ± 0.025 | 1.308 ± 0.039 / 0.241 / 0.473 |
| Human / Rewind outer norm | full-QAC105 / Ec_MBC | 5 / 16 | 2.195 ± 0.133 | 1.690 ± 0.013 / -0.235 / 0.088 |
| Human / Rewind outer norm | full-QAC105 / Ec_MIC | 5 / 17 | 2.074 ± 0.171 | 1.669 ± 0.111 / -0.306 / 0.342 |
| Human / Rewind outer norm | full-QAC105 / Sa_MBC | 5 / 17 | 2.066 ± 0.119 | 1.704 ± 0.094 / 0.045 / 0.138 |
| Human / Rewind outer norm | full-QAC105 / Sa_MIC | 5 / 17 | 1.868 ± 0.148 | 1.535 ± 0.130 / -0.147 / 0.050 |
| Human / Rewind outer norm | scaffold / Ec_MBC | 5 / 105 | 1.825 ± 0.062 | 1.419 ± 0.065 / 0.236 / 0.512 |
| Human / Rewind outer norm | scaffold / Ec_MIC | 5 / 105 | 1.722 ± 0.075 | 1.305 ± 0.083 / 0.235 / 0.525 |
| Human / Rewind outer norm | scaffold / Sa_MBC | 5 / 105 | 1.980 ± 0.020 | 1.469 ± 0.040 / -0.017 / 0.219 |
| Human / Rewind outer norm | scaffold / Sa_MIC | 5 / 105 | 1.829 ± 0.042 | 1.448 ± 0.057 / 0.129 / 0.370 |
| Shuffled human / Intact | cation / Ec_MBC | 5 / 105 | 1.929 ± 0.048 | 1.543 ± 0.055 / 0.147 / 0.348 |
| Shuffled human / Intact | cation / Ec_MIC | 5 / 105 | 1.776 ± 0.037 | 1.345 ± 0.037 / 0.187 / 0.411 |
| Shuffled human / Intact | cation / Sa_MBC | 5 / 105 | 1.923 ± 0.047 | 1.435 ± 0.035 / 0.041 / 0.261 |
| Shuffled human / Intact | cation / Sa_MIC | 5 / 105 | 1.796 ± 0.034 | 1.410 ± 0.028 / 0.159 / 0.396 |
| Shuffled human / Intact | full-QAC105 / Ec_MBC | 5 / 16 | 2.557 ± 0.157 | 1.975 ± 0.104 / -0.676 / -0.199 |
| Shuffled human / Intact | full-QAC105 / Ec_MIC | 5 / 17 | 2.637 ± 0.154 | 2.122 ± 0.130 / -1.106 / -0.203 |
| Shuffled human / Intact | full-QAC105 / Sa_MBC | 5 / 17 | 2.217 ± 0.086 | 1.814 ± 0.065 / -0.098 / -0.070 |
| Shuffled human / Intact | full-QAC105 / Sa_MIC | 5 / 17 | 1.865 ± 0.112 | 1.548 ± 0.096 / -0.140 / -0.185 |
| Shuffled human / Intact | scaffold / Ec_MBC | 5 / 105 | 2.007 ± 0.061 | 1.624 ± 0.064 / 0.077 / 0.276 |
| Shuffled human / Intact | scaffold / Ec_MIC | 5 / 105 | 1.907 ± 0.062 | 1.491 ± 0.057 / 0.063 / 0.254 |
| Shuffled human / Intact | scaffold / Sa_MBC | 5 / 105 | 2.022 ± 0.045 | 1.508 ± 0.031 / -0.061 / 0.141 |
| Shuffled human / Intact | scaffold / Sa_MIC | 5 / 105 | 1.913 ± 0.041 | 1.548 ± 0.056 / 0.046 / 0.238 |
| Shuffled human / Rewind all weights | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Shuffled human / Rewind all weights | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Shuffled human / Rewind all weights | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Shuffled human / Rewind all weights | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Shuffled human / Rewind all weights | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Shuffled human / Rewind all weights | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Shuffled human / Rewind all weights | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Shuffled human / Rewind all weights | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Shuffled human / Rewind all weights | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Shuffled human / Rewind all weights | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Shuffled human / Rewind all weights | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Shuffled human / Rewind all weights | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Shuffled human / Rewind eight blocks | cation / Ec_MBC | 5 / 105 | 1.925 ± 0.058 | 1.550 ± 0.055 / 0.150 / 0.370 |
| Shuffled human / Rewind eight blocks | cation / Ec_MIC | 5 / 105 | 1.772 ± 0.041 | 1.365 ± 0.043 / 0.191 / 0.422 |
| Shuffled human / Rewind eight blocks | cation / Sa_MBC | 5 / 105 | 1.907 ± 0.057 | 1.425 ± 0.038 / 0.056 / 0.273 |
| Shuffled human / Rewind eight blocks | cation / Sa_MIC | 5 / 105 | 1.776 ± 0.045 | 1.383 ± 0.054 / 0.178 / 0.414 |
| Shuffled human / Rewind eight blocks | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Shuffled human / Rewind eight blocks | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Shuffled human / Rewind eight blocks | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Shuffled human / Rewind eight blocks | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Shuffled human / Rewind eight blocks | scaffold / Ec_MBC | 5 / 105 | 1.959 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Shuffled human / Rewind eight blocks | scaffold / Ec_MIC | 5 / 105 | 1.863 ± 0.034 | 1.452 ± 0.033 / 0.106 / 0.341 |
| Shuffled human / Rewind eight blocks | scaffold / Sa_MBC | 5 / 105 | 2.024 ± 0.060 | 1.532 ± 0.038 / -0.063 / 0.134 |
| Shuffled human / Rewind eight blocks | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.018 / 0.057 / 0.274 |
| Shuffled human / Rewind outer norm | cation / Ec_MBC | 5 / 105 | 1.930 ± 0.047 | 1.544 ± 0.053 / 0.147 / 0.348 |
| Shuffled human / Rewind outer norm | cation / Ec_MIC | 5 / 105 | 1.776 ± 0.037 | 1.345 ± 0.037 / 0.188 / 0.412 |
| Shuffled human / Rewind outer norm | cation / Sa_MBC | 5 / 105 | 1.924 ± 0.047 | 1.439 ± 0.029 / 0.039 / 0.257 |
| Shuffled human / Rewind outer norm | cation / Sa_MIC | 5 / 105 | 1.797 ± 0.034 | 1.410 ± 0.027 / 0.159 / 0.394 |
| Shuffled human / Rewind outer norm | full-QAC105 / Ec_MBC | 5 / 16 | 2.557 ± 0.157 | 1.975 ± 0.104 / -0.676 / -0.199 |
| Shuffled human / Rewind outer norm | full-QAC105 / Ec_MIC | 5 / 17 | 2.637 ± 0.154 | 2.122 ± 0.130 / -1.106 / -0.203 |
| Shuffled human / Rewind outer norm | full-QAC105 / Sa_MBC | 5 / 17 | 2.217 ± 0.086 | 1.814 ± 0.065 / -0.098 / -0.070 |
| Shuffled human / Rewind outer norm | full-QAC105 / Sa_MIC | 5 / 17 | 1.865 ± 0.112 | 1.548 ± 0.096 / -0.140 / -0.185 |
| Shuffled human / Rewind outer norm | scaffold / Ec_MBC | 5 / 105 | 2.006 ± 0.062 | 1.625 ± 0.063 / 0.077 / 0.277 |
| Shuffled human / Rewind outer norm | scaffold / Ec_MIC | 5 / 105 | 1.906 ± 0.063 | 1.491 ± 0.058 / 0.063 / 0.255 |
| Shuffled human / Rewind outer norm | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.044 | 1.508 ± 0.030 / -0.062 / 0.141 |
| Shuffled human / Rewind outer norm | scaffold / Sa_MIC | 5 / 105 | 1.912 ± 0.044 | 1.546 ± 0.060 / 0.047 / 0.238 |
| Binary MIC / Intact | cation / Ec_MBC | 5 / 105 | 1.841 ± 0.049 | 1.429 ± 0.056 / 0.223 / 0.478 |
| Binary MIC / Intact | cation / Ec_MIC | 5 / 105 | 1.706 ± 0.048 | 1.291 ± 0.055 / 0.250 / 0.519 |
| Binary MIC / Intact | cation / Sa_MBC | 5 / 105 | 1.925 ± 0.076 | 1.402 ± 0.080 / 0.038 / 0.310 |
| Binary MIC / Intact | cation / Sa_MIC | 5 / 105 | 1.741 ± 0.092 | 1.310 ± 0.080 / 0.208 / 0.469 |
| Binary MIC / Intact | full-QAC105 / Ec_MBC | 5 / 16 | 2.137 ± 0.184 | 1.656 ± 0.121 / -0.175 / 0.114 |
| Binary MIC / Intact | full-QAC105 / Ec_MIC | 5 / 17 | 2.003 ± 0.164 | 1.637 ± 0.163 / -0.219 / 0.302 |
| Binary MIC / Intact | full-QAC105 / Sa_MBC | 5 / 17 | 2.214 ± 0.184 | 1.815 ± 0.152 / -0.099 / 0.035 |
| Binary MIC / Intact | full-QAC105 / Sa_MIC | 5 / 17 | 2.024 ± 0.071 | 1.711 ± 0.061 / -0.341 / -0.075 |
| Binary MIC / Intact | scaffold / Ec_MBC | 5 / 105 | 1.851 ± 0.052 | 1.461 ± 0.026 / 0.215 / 0.493 |
| Binary MIC / Intact | scaffold / Ec_MIC | 5 / 105 | 1.766 ± 0.048 | 1.345 ± 0.028 / 0.196 / 0.489 |
| Binary MIC / Intact | scaffold / Sa_MBC | 5 / 105 | 1.993 ± 0.078 | 1.479 ± 0.055 / -0.032 / 0.210 |
| Binary MIC / Intact | scaffold / Sa_MIC | 5 / 105 | 1.806 ± 0.109 | 1.406 ± 0.092 / 0.148 / 0.415 |
| Binary MIC / Rewind all weights | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Binary MIC / Rewind all weights | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Binary MIC / Rewind all weights | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Binary MIC / Rewind all weights | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Binary MIC / Rewind all weights | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Binary MIC / Rewind all weights | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Binary MIC / Rewind all weights | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Binary MIC / Rewind all weights | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Binary MIC / Rewind all weights | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Binary MIC / Rewind all weights | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Binary MIC / Rewind all weights | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Binary MIC / Rewind all weights | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Binary MIC / Rewind eight blocks | cation / Ec_MBC | 5 / 105 | 1.924 ± 0.059 | 1.549 ± 0.055 / 0.151 / 0.369 |
| Binary MIC / Rewind eight blocks | cation / Ec_MIC | 5 / 105 | 1.772 ± 0.041 | 1.365 ± 0.043 / 0.191 / 0.421 |
| Binary MIC / Rewind eight blocks | cation / Sa_MBC | 5 / 105 | 1.905 ± 0.056 | 1.423 ± 0.035 / 0.058 / 0.278 |
| Binary MIC / Rewind eight blocks | cation / Sa_MIC | 5 / 105 | 1.776 ± 0.044 | 1.383 ± 0.053 / 0.178 / 0.413 |
| Binary MIC / Rewind eight blocks | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Binary MIC / Rewind eight blocks | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Binary MIC / Rewind eight blocks | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Binary MIC / Rewind eight blocks | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Binary MIC / Rewind eight blocks | scaffold / Ec_MBC | 5 / 105 | 1.959 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Binary MIC / Rewind eight blocks | scaffold / Ec_MIC | 5 / 105 | 1.863 ± 0.034 | 1.452 ± 0.033 / 0.106 / 0.341 |
| Binary MIC / Rewind eight blocks | scaffold / Sa_MBC | 5 / 105 | 2.024 ± 0.060 | 1.532 ± 0.038 / -0.063 / 0.134 |
| Binary MIC / Rewind eight blocks | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.018 / 0.057 / 0.274 |
| Binary MIC / Rewind outer norm | cation / Ec_MBC | 5 / 105 | 1.841 ± 0.049 | 1.429 ± 0.056 / 0.223 / 0.478 |
| Binary MIC / Rewind outer norm | cation / Ec_MIC | 5 / 105 | 1.706 ± 0.048 | 1.291 ± 0.055 / 0.250 / 0.519 |
| Binary MIC / Rewind outer norm | cation / Sa_MBC | 5 / 105 | 1.925 ± 0.076 | 1.402 ± 0.080 / 0.038 / 0.310 |
| Binary MIC / Rewind outer norm | cation / Sa_MIC | 5 / 105 | 1.741 ± 0.092 | 1.310 ± 0.080 / 0.208 / 0.469 |
| Binary MIC / Rewind outer norm | full-QAC105 / Ec_MBC | 5 / 16 | 2.137 ± 0.184 | 1.656 ± 0.121 / -0.175 / 0.114 |
| Binary MIC / Rewind outer norm | full-QAC105 / Ec_MIC | 5 / 17 | 2.003 ± 0.164 | 1.637 ± 0.163 / -0.219 / 0.302 |
| Binary MIC / Rewind outer norm | full-QAC105 / Sa_MBC | 5 / 17 | 2.214 ± 0.184 | 1.815 ± 0.152 / -0.099 / 0.035 |
| Binary MIC / Rewind outer norm | full-QAC105 / Sa_MIC | 5 / 17 | 2.024 ± 0.071 | 1.711 ± 0.061 / -0.341 / -0.075 |
| Binary MIC / Rewind outer norm | scaffold / Ec_MBC | 5 / 105 | 1.851 ± 0.052 | 1.461 ± 0.026 / 0.215 / 0.493 |
| Binary MIC / Rewind outer norm | scaffold / Ec_MIC | 5 / 105 | 1.766 ± 0.048 | 1.345 ± 0.028 / 0.196 / 0.489 |
| Binary MIC / Rewind outer norm | scaffold / Sa_MBC | 5 / 105 | 1.993 ± 0.078 | 1.479 ± 0.055 / -0.032 / 0.210 |
| Binary MIC / Rewind outer norm | scaffold / Sa_MIC | 5 / 105 | 1.806 ± 0.109 | 1.406 ± 0.092 / 0.148 / 0.415 |
| Shuffled binary MIC / Intact | cation / Ec_MBC | 5 / 105 | 1.996 ± 0.083 | 1.600 ± 0.081 / 0.086 / 0.295 |
| Shuffled binary MIC / Intact | cation / Ec_MIC | 5 / 105 | 1.845 ± 0.078 | 1.421 ± 0.074 / 0.122 / 0.347 |
| Shuffled binary MIC / Intact | cation / Sa_MBC | 5 / 105 | 1.918 ± 0.088 | 1.449 ± 0.058 / 0.044 / 0.243 |
| Shuffled binary MIC / Intact | cation / Sa_MIC | 5 / 105 | 1.791 ± 0.084 | 1.393 ± 0.050 / 0.163 / 0.389 |
| Shuffled binary MIC / Intact | full-QAC105 / Ec_MBC | 5 / 16 | 2.558 ± 0.130 | 2.001 ± 0.099 / -0.676 / -0.098 |
| Shuffled binary MIC / Intact | full-QAC105 / Ec_MIC | 5 / 17 | 2.619 ± 0.144 | 2.128 ± 0.137 / -1.076 / -0.091 |
| Shuffled binary MIC / Intact | full-QAC105 / Sa_MBC | 5 / 17 | 2.318 ± 0.178 | 1.925 ± 0.157 / -0.204 / -0.173 |
| Shuffled binary MIC / Intact | full-QAC105 / Sa_MIC | 5 / 17 | 1.938 ± 0.303 | 1.635 ± 0.248 / -0.251 / -0.155 |
| Shuffled binary MIC / Intact | scaffold / Ec_MBC | 5 / 105 | 2.007 ± 0.052 | 1.614 ± 0.047 / 0.076 / 0.281 |
| Shuffled binary MIC / Intact | scaffold / Ec_MIC | 5 / 105 | 1.902 ± 0.048 | 1.470 ± 0.050 / 0.067 / 0.264 |
| Shuffled binary MIC / Intact | scaffold / Sa_MBC | 5 / 105 | 2.044 ± 0.128 | 1.550 ± 0.109 / -0.087 / 0.078 |
| Shuffled binary MIC / Intact | scaffold / Sa_MIC | 5 / 105 | 1.904 ± 0.114 | 1.541 ± 0.103 / 0.054 / 0.242 |
| Shuffled binary MIC / Rewind all weights | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Shuffled binary MIC / Rewind all weights | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Shuffled binary MIC / Rewind all weights | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Shuffled binary MIC / Rewind all weights | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Shuffled binary MIC / Rewind all weights | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Shuffled binary MIC / Rewind all weights | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Shuffled binary MIC / Rewind all weights | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Shuffled binary MIC / Rewind all weights | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Shuffled binary MIC / Rewind all weights | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Shuffled binary MIC / Rewind all weights | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Shuffled binary MIC / Rewind all weights | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Shuffled binary MIC / Rewind all weights | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Shuffled binary MIC / Rewind eight blocks | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.057 | 1.550 ± 0.055 / 0.150 / 0.370 |
| Shuffled binary MIC / Rewind eight blocks | cation / Ec_MIC | 5 / 105 | 1.771 ± 0.038 | 1.364 ± 0.044 / 0.192 / 0.425 |
| Shuffled binary MIC / Rewind eight blocks | cation / Sa_MBC | 5 / 105 | 1.904 ± 0.052 | 1.422 ± 0.037 / 0.059 / 0.274 |
| Shuffled binary MIC / Rewind eight blocks | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.042 | 1.382 ± 0.052 / 0.180 / 0.415 |
| Shuffled binary MIC / Rewind eight blocks | full-QAC105 / Ec_MBC | 5 / 16 | 2.541 ± 0.260 | 1.960 ± 0.130 / -0.665 / -0.088 |
| Shuffled binary MIC / Rewind eight blocks | full-QAC105 / Ec_MIC | 5 / 17 | 2.606 ± 0.308 | 2.109 ± 0.198 / -1.074 / -0.134 |
| Shuffled binary MIC / Rewind eight blocks | full-QAC105 / Sa_MBC | 5 / 17 | 2.171 ± 0.082 | 1.793 ± 0.087 / -0.053 / 0.067 |
| Shuffled binary MIC / Rewind eight blocks | full-QAC105 / Sa_MIC | 5 / 17 | 1.767 ± 0.110 | 1.485 ± 0.077 / -0.024 / 0.143 |
| Shuffled binary MIC / Rewind eight blocks | scaffold / Ec_MBC | 5 / 105 | 1.959 ± 0.036 | 1.580 ± 0.023 / 0.120 / 0.350 |
| Shuffled binary MIC / Rewind eight blocks | scaffold / Ec_MIC | 5 / 105 | 1.866 ± 0.035 | 1.456 ± 0.038 / 0.103 / 0.338 |
| Shuffled binary MIC / Rewind eight blocks | scaffold / Sa_MBC | 5 / 105 | 2.025 ± 0.062 | 1.532 ± 0.039 / -0.064 / 0.131 |
| Shuffled binary MIC / Rewind eight blocks | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.045 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Shuffled binary MIC / Rewind outer norm | cation / Ec_MBC | 5 / 105 | 1.999 ± 0.081 | 1.602 ± 0.080 / 0.084 / 0.294 |
| Shuffled binary MIC / Rewind outer norm | cation / Ec_MIC | 5 / 105 | 1.849 ± 0.076 | 1.422 ± 0.073 / 0.118 / 0.345 |
| Shuffled binary MIC / Rewind outer norm | cation / Sa_MBC | 5 / 105 | 1.916 ± 0.087 | 1.446 ± 0.057 / 0.046 / 0.246 |
| Shuffled binary MIC / Rewind outer norm | cation / Sa_MIC | 5 / 105 | 1.790 ± 0.084 | 1.393 ± 0.050 / 0.164 / 0.389 |
| Shuffled binary MIC / Rewind outer norm | full-QAC105 / Ec_MBC | 5 / 16 | 2.558 ± 0.130 | 2.001 ± 0.099 / -0.676 / -0.098 |
| Shuffled binary MIC / Rewind outer norm | full-QAC105 / Ec_MIC | 5 / 17 | 2.619 ± 0.144 | 2.128 ± 0.137 / -1.076 / -0.091 |
| Shuffled binary MIC / Rewind outer norm | full-QAC105 / Sa_MBC | 5 / 17 | 2.318 ± 0.178 | 1.925 ± 0.157 / -0.204 / -0.173 |
| Shuffled binary MIC / Rewind outer norm | full-QAC105 / Sa_MIC | 5 / 17 | 1.938 ± 0.303 | 1.635 ± 0.248 / -0.251 / -0.155 |
| Shuffled binary MIC / Rewind outer norm | scaffold / Ec_MBC | 5 / 105 | 2.007 ± 0.052 | 1.614 ± 0.047 / 0.076 / 0.281 |
| Shuffled binary MIC / Rewind outer norm | scaffold / Ec_MIC | 5 / 105 | 1.902 ± 0.048 | 1.470 ± 0.050 / 0.067 / 0.264 |
| Shuffled binary MIC / Rewind outer norm | scaffold / Sa_MBC | 5 / 105 | 2.044 ± 0.128 | 1.550 ± 0.109 / -0.087 / 0.078 |
| Shuffled binary MIC / Rewind outer norm | scaffold / Sa_MIC | 5 / 105 | 1.904 ± 0.114 | 1.541 ± 0.103 / 0.054 / 0.242 |
| Continuous MIC / Intact | cation / Ec_MBC | 5 / 105 | 1.735 ± 0.041 | 1.344 ± 0.031 / 0.310 / 0.553 |
| Continuous MIC / Intact | cation / Ec_MIC | 5 / 105 | 1.615 ± 0.051 | 1.212 ± 0.038 / 0.327 / 0.582 |
| Continuous MIC / Intact | cation / Sa_MBC | 5 / 105 | 1.831 ± 0.055 | 1.326 ± 0.059 / 0.129 / 0.397 |
| Continuous MIC / Intact | cation / Sa_MIC | 5 / 105 | 1.669 ± 0.052 | 1.270 ± 0.031 / 0.274 / 0.512 |
| Continuous MIC / Intact | full-QAC105 / Ec_MBC | 5 / 16 | 2.477 ± 0.069 | 1.803 ± 0.056 / -0.569 / -0.103 |
| Continuous MIC / Intact | full-QAC105 / Ec_MIC | 5 / 17 | 2.448 ± 0.103 | 1.902 ± 0.104 / -0.813 / -0.035 |
| Continuous MIC / Intact | full-QAC105 / Sa_MBC | 5 / 17 | 2.119 ± 0.101 | 1.729 ± 0.118 / -0.004 / 0.117 |
| Continuous MIC / Intact | full-QAC105 / Sa_MIC | 5 / 17 | 1.852 ± 0.154 | 1.545 ± 0.126 / -0.127 / 0.063 |
| Continuous MIC / Intact | scaffold / Ec_MBC | 5 / 105 | 1.807 ± 0.058 | 1.416 ± 0.047 / 0.251 / 0.524 |
| Continuous MIC / Intact | scaffold / Ec_MIC | 5 / 105 | 1.726 ± 0.058 | 1.314 ± 0.040 / 0.232 / 0.507 |
| Continuous MIC / Intact | scaffold / Sa_MBC | 5 / 105 | 1.949 ± 0.027 | 1.430 ± 0.009 / 0.015 / 0.247 |
| Continuous MIC / Intact | scaffold / Sa_MIC | 5 / 105 | 1.767 ± 0.029 | 1.390 ± 0.021 / 0.187 / 0.427 |
| Continuous MIC / Rewind all weights | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Continuous MIC / Rewind all weights | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Continuous MIC / Rewind all weights | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Continuous MIC / Rewind all weights | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Continuous MIC / Rewind all weights | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Continuous MIC / Rewind all weights | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Continuous MIC / Rewind all weights | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Continuous MIC / Rewind all weights | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Continuous MIC / Rewind all weights | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Continuous MIC / Rewind all weights | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Continuous MIC / Rewind all weights | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Continuous MIC / Rewind all weights | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Continuous MIC / Rewind eight blocks | cation / Ec_MBC | 5 / 105 | 1.927 ± 0.059 | 1.552 ± 0.056 / 0.148 / 0.368 |
| Continuous MIC / Rewind eight blocks | cation / Ec_MIC | 5 / 105 | 1.774 ± 0.042 | 1.367 ± 0.045 / 0.189 / 0.423 |
| Continuous MIC / Rewind eight blocks | cation / Sa_MBC | 5 / 105 | 1.908 ± 0.057 | 1.424 ± 0.037 / 0.055 / 0.274 |
| Continuous MIC / Rewind eight blocks | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.044 | 1.381 ± 0.052 / 0.180 / 0.416 |
| Continuous MIC / Rewind eight blocks | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Continuous MIC / Rewind eight blocks | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Continuous MIC / Rewind eight blocks | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Continuous MIC / Rewind eight blocks | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Continuous MIC / Rewind eight blocks | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Continuous MIC / Rewind eight blocks | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Continuous MIC / Rewind eight blocks | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Continuous MIC / Rewind eight blocks | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Continuous MIC / Rewind outer norm | cation / Ec_MBC | 5 / 105 | 1.735 ± 0.041 | 1.344 ± 0.031 / 0.310 / 0.553 |
| Continuous MIC / Rewind outer norm | cation / Ec_MIC | 5 / 105 | 1.615 ± 0.051 | 1.212 ± 0.038 / 0.327 / 0.582 |
| Continuous MIC / Rewind outer norm | cation / Sa_MBC | 5 / 105 | 1.831 ± 0.055 | 1.326 ± 0.059 / 0.129 / 0.397 |
| Continuous MIC / Rewind outer norm | cation / Sa_MIC | 5 / 105 | 1.669 ± 0.052 | 1.270 ± 0.031 / 0.274 / 0.512 |
| Continuous MIC / Rewind outer norm | full-QAC105 / Ec_MBC | 5 / 16 | 2.477 ± 0.069 | 1.803 ± 0.056 / -0.569 / -0.103 |
| Continuous MIC / Rewind outer norm | full-QAC105 / Ec_MIC | 5 / 17 | 2.448 ± 0.103 | 1.902 ± 0.104 / -0.813 / -0.035 |
| Continuous MIC / Rewind outer norm | full-QAC105 / Sa_MBC | 5 / 17 | 2.119 ± 0.101 | 1.729 ± 0.118 / -0.004 / 0.117 |
| Continuous MIC / Rewind outer norm | full-QAC105 / Sa_MIC | 5 / 17 | 1.852 ± 0.154 | 1.545 ± 0.126 / -0.127 / 0.063 |
| Continuous MIC / Rewind outer norm | scaffold / Ec_MBC | 5 / 105 | 1.807 ± 0.058 | 1.416 ± 0.047 / 0.251 / 0.524 |
| Continuous MIC / Rewind outer norm | scaffold / Ec_MIC | 5 / 105 | 1.726 ± 0.058 | 1.314 ± 0.040 / 0.232 / 0.507 |
| Continuous MIC / Rewind outer norm | scaffold / Sa_MBC | 5 / 105 | 1.949 ± 0.027 | 1.430 ± 0.009 / 0.015 / 0.247 |
| Continuous MIC / Rewind outer norm | scaffold / Sa_MIC | 5 / 105 | 1.767 ± 0.029 | 1.390 ± 0.021 / 0.187 / 0.427 |
| Shuffled continuous MIC / Intact | cation / Ec_MBC | 5 / 105 | 1.971 ± 0.048 | 1.589 ± 0.042 / 0.110 / 0.311 |
| Shuffled continuous MIC / Intact | cation / Ec_MIC | 5 / 105 | 1.809 ± 0.053 | 1.402 ± 0.055 / 0.156 / 0.376 |
| Shuffled continuous MIC / Intact | cation / Sa_MBC | 5 / 105 | 1.909 ± 0.036 | 1.410 ± 0.033 / 0.054 / 0.278 |
| Shuffled continuous MIC / Intact | cation / Sa_MIC | 5 / 105 | 1.791 ± 0.030 | 1.396 ± 0.021 / 0.164 / 0.389 |
| Shuffled continuous MIC / Intact | full-QAC105 / Ec_MBC | 5 / 16 | 2.486 ± 0.072 | 1.945 ± 0.074 / -0.582 / -0.042 |
| Shuffled continuous MIC / Intact | full-QAC105 / Ec_MIC | 5 / 17 | 2.536 ± 0.114 | 2.073 ± 0.108 / -0.946 / 0.002 |
| Shuffled continuous MIC / Intact | full-QAC105 / Sa_MBC | 5 / 17 | 2.163 ± 0.119 | 1.802 ± 0.139 / -0.046 / 0.077 |
| Shuffled continuous MIC / Intact | full-QAC105 / Sa_MIC | 5 / 17 | 1.869 ± 0.083 | 1.561 ± 0.058 / -0.144 / -0.110 |
| Shuffled continuous MIC / Intact | scaffold / Ec_MBC | 5 / 105 | 1.971 ± 0.015 | 1.601 ± 0.026 / 0.110 / 0.334 |
| Shuffled continuous MIC / Intact | scaffold / Ec_MIC | 5 / 105 | 1.859 ± 0.014 | 1.476 ± 0.019 / 0.109 / 0.322 |
| Shuffled continuous MIC / Intact | scaffold / Sa_MBC | 5 / 105 | 2.030 ± 0.027 | 1.529 ± 0.045 / -0.069 / 0.134 |
| Shuffled continuous MIC / Intact | scaffold / Sa_MIC | 5 / 105 | 1.916 ± 0.033 | 1.542 ± 0.052 / 0.044 / 0.240 |
| Shuffled continuous MIC / Rewind all weights | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Shuffled continuous MIC / Rewind all weights | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Shuffled continuous MIC / Rewind all weights | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Shuffled continuous MIC / Rewind all weights | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Shuffled continuous MIC / Rewind all weights | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Shuffled continuous MIC / Rewind all weights | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Shuffled continuous MIC / Rewind all weights | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Shuffled continuous MIC / Rewind all weights | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Shuffled continuous MIC / Rewind all weights | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Shuffled continuous MIC / Rewind all weights | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Shuffled continuous MIC / Rewind all weights | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Shuffled continuous MIC / Rewind all weights | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Shuffled continuous MIC / Rewind eight blocks | cation / Ec_MBC | 5 / 105 | 1.926 ± 0.059 | 1.550 ± 0.057 / 0.149 / 0.367 |
| Shuffled continuous MIC / Rewind eight blocks | cation / Ec_MIC | 5 / 105 | 1.773 ± 0.042 | 1.366 ± 0.045 / 0.190 / 0.421 |
| Shuffled continuous MIC / Rewind eight blocks | cation / Sa_MBC | 5 / 105 | 1.906 ± 0.056 | 1.423 ± 0.035 / 0.057 / 0.278 |
| Shuffled continuous MIC / Rewind eight blocks | cation / Sa_MIC | 5 / 105 | 1.774 ± 0.043 | 1.381 ± 0.052 / 0.180 / 0.415 |
| Shuffled continuous MIC / Rewind eight blocks | full-QAC105 / Ec_MBC | 5 / 16 | 2.560 ± 0.228 | 1.967 ± 0.121 / -0.686 / -0.124 |
| Shuffled continuous MIC / Rewind eight blocks | full-QAC105 / Ec_MIC | 5 / 17 | 2.616 ± 0.290 | 2.111 ± 0.196 / -1.088 / -0.165 |
| Shuffled continuous MIC / Rewind eight blocks | full-QAC105 / Sa_MBC | 5 / 17 | 2.159 ± 0.107 | 1.782 ± 0.111 / -0.042 / 0.123 |
| Shuffled continuous MIC / Rewind eight blocks | full-QAC105 / Sa_MIC | 5 / 17 | 1.760 ± 0.119 | 1.476 ± 0.086 / -0.016 / 0.155 |
| Shuffled continuous MIC / Rewind eight blocks | scaffold / Ec_MBC | 5 / 105 | 1.958 ± 0.036 | 1.578 ± 0.022 / 0.121 / 0.352 |
| Shuffled continuous MIC / Rewind eight blocks | scaffold / Ec_MIC | 5 / 105 | 1.864 ± 0.034 | 1.453 ± 0.035 / 0.105 / 0.342 |
| Shuffled continuous MIC / Rewind eight blocks | scaffold / Sa_MBC | 5 / 105 | 2.023 ± 0.060 | 1.531 ± 0.039 / -0.063 / 0.135 |
| Shuffled continuous MIC / Rewind eight blocks | scaffold / Sa_MIC | 5 / 105 | 1.902 ± 0.046 | 1.531 ± 0.019 / 0.057 / 0.273 |
| Shuffled continuous MIC / Rewind outer norm | cation / Ec_MBC | 5 / 105 | 1.971 ± 0.048 | 1.589 ± 0.042 / 0.110 / 0.311 |
| Shuffled continuous MIC / Rewind outer norm | cation / Ec_MIC | 5 / 105 | 1.809 ± 0.053 | 1.402 ± 0.055 / 0.156 / 0.376 |
| Shuffled continuous MIC / Rewind outer norm | cation / Sa_MBC | 5 / 105 | 1.909 ± 0.036 | 1.410 ± 0.033 / 0.054 / 0.278 |
| Shuffled continuous MIC / Rewind outer norm | cation / Sa_MIC | 5 / 105 | 1.791 ± 0.030 | 1.396 ± 0.021 / 0.164 / 0.389 |
| Shuffled continuous MIC / Rewind outer norm | full-QAC105 / Ec_MBC | 5 / 16 | 2.486 ± 0.072 | 1.945 ± 0.074 / -0.582 / -0.042 |
| Shuffled continuous MIC / Rewind outer norm | full-QAC105 / Ec_MIC | 5 / 17 | 2.536 ± 0.114 | 2.073 ± 0.108 / -0.946 / 0.002 |
| Shuffled continuous MIC / Rewind outer norm | full-QAC105 / Sa_MBC | 5 / 17 | 2.163 ± 0.119 | 1.802 ± 0.139 / -0.046 / 0.077 |
| Shuffled continuous MIC / Rewind outer norm | full-QAC105 / Sa_MIC | 5 / 17 | 1.869 ± 0.083 | 1.561 ± 0.058 / -0.144 / -0.110 |
| Shuffled continuous MIC / Rewind outer norm | scaffold / Ec_MBC | 5 / 105 | 1.971 ± 0.015 | 1.601 ± 0.026 / 0.110 / 0.334 |
| Shuffled continuous MIC / Rewind outer norm | scaffold / Ec_MIC | 5 / 105 | 1.859 ± 0.014 | 1.476 ± 0.019 / 0.109 / 0.322 |
| Shuffled continuous MIC / Rewind outer norm | scaffold / Sa_MBC | 5 / 105 | 2.030 ± 0.027 | 1.529 ± 0.045 / -0.069 / 0.134 |
| Shuffled continuous MIC / Rewind outer norm | scaffold / Sa_MIC | 5 / 105 | 1.916 ± 0.033 | 1.542 ± 0.052 / 0.044 / 0.240 |
| Pretrained / Pure pretrained | cation / Ec_MBC | 1 / 105 | 1.939 | 1.566 / 0.139 / 0.338 |
| Pretrained / Pure pretrained | cation / Ec_MIC | 1 / 105 | 1.800 | 1.410 / 0.165 / 0.387 |
| Pretrained / Pure pretrained | cation / Sa_MBC | 1 / 105 | 1.921 | 1.449 / 0.043 / 0.227 |
| Pretrained / Pure pretrained | cation / Sa_MIC | 1 / 105 | 1.768 | 1.393 / 0.186 / 0.394 |
| Pretrained / Pure pretrained | full-QAC105 / Ec_MBC | 1 / 16 | 2.498 | 1.993 / -0.595 / -0.340 |
| Pretrained / Pure pretrained | full-QAC105 / Ec_MIC | 1 / 17 | 2.562 | 2.066 / -0.983 / -0.466 |
| Pretrained / Pure pretrained | full-QAC105 / Sa_MBC | 1 / 17 | 2.071 | 1.756 / 0.044 / 0.240 |
| Pretrained / Pure pretrained | full-QAC105 / Sa_MIC | 1 / 17 | 1.871 | 1.610 / -0.144 / 0.298 |
| Pretrained / Pure pretrained | scaffold / Ec_MBC | 1 / 105 | 2.045 | 1.652 / 0.042 / 0.264 |
| Pretrained / Pure pretrained | scaffold / Ec_MIC | 1 / 105 | 1.958 | 1.527 / 0.013 / 0.218 |
| Pretrained / Pure pretrained | scaffold / Sa_MBC | 1 / 105 | 2.008 | 1.515 / -0.046 / 0.144 |
| Pretrained / Pure pretrained | scaffold / Sa_MIC | 1 / 105 | 1.896 | 1.524 / 0.064 / 0.281 |


Figure S26. Split violins compare direct target fine-tuning (lavender, left) with frozen guided encoder plus CatBoost (mint, right) for three real supervisory signals. Each density uses mean absolute error over the same three seed-specific predictions for each compound/endpoint; these are not residuals of an ensemble prediction. Cation/scaffold panels contain 420 endpoint summaries, OOD 67. Bars show median and IQR; all tails are retained. Dependencies between endpoints and seeds require paired cluster inference rather than tests on plotted densities. IT505 E. coli MBC >500 mg/L is excluded from exact-value densities; its separately retained minimum-error sensitivity is derived in Table S33.

S26. All new paired contrasts

Table S32. Complete exploratory paired seed/group bootstrap contrasts (5,000 draws, seed 1729). ΔRMSE is A minus B. Both predictions for an endpoint and all endpoints in the sampled group move together. Paired seed indices are resampled as one source/target unit. Cation CV is shown under cation and scaffold grouping; scaffold CV under scaffold grouping; OOD under cation and four-family grouping. Intervals are unadjusted, conditional on fitted models and do not refit training data or add independent OOD families. Source/target seeds are not crossed, so their separate variance components cannot be identified.

The primary real-label contrasts retain their archived 10,000-draw intervals in main Section 2.2 and Table 7. Table S32 repeats those contrasts using the new 5,000-draw procedure on identical predictions and point effects. Small interval-edge changes reflect Monte Carlo resampling rather than a change in measurements, predictions or the pooled-loss calculation.

| Procedure / contrast | A minus B | Regime / grouping | Seeds / groups | ΔRMSE [95% interval] |
| --- | --- | --- | --- | --- |
| direct / capacity_vs_linear | raw-molformer/compact − raw-molformer/linear | cation / cation | 3 / 103 | −0.033 [−0.110, +0.043] |
| direct / capacity_vs_linear | raw-molformer/compact − raw-molformer/linear | cation / scaffold | 3 / 29 | −0.033 [−0.118, +0.056] |
| direct / capacity_vs_linear | raw-molformer/compact − raw-molformer/linear | scaffold / scaffold | 3 / 29 | +0.023 [−0.059, +0.103] |
| direct / capacity_vs_linear | raw-molformer/compact − raw-molformer/linear | full-QAC105 / cation | 3 / 17 | +0.304 [+0.092, +0.617] |
| direct / capacity_vs_linear | raw-molformer/compact − raw-molformer/linear | full-QAC105 / scaffold | 3 / 4 | +0.304 [+0.031, +0.680] |
| direct / capacity_vs_linear | raw-molformer/lora − raw-molformer/linear | cation / cation | 3 / 103 | +0.027 [−0.077, +0.126] |
| direct / capacity_vs_linear | raw-molformer/lora − raw-molformer/linear | cation / scaffold | 3 / 29 | +0.027 [−0.088, +0.153] |
| direct / capacity_vs_linear | raw-molformer/lora − raw-molformer/linear | scaffold / scaffold | 3 / 29 | +0.103 [−0.019, +0.219] |
| direct / capacity_vs_linear | raw-molformer/lora − raw-molformer/linear | full-QAC105 / cation | 3 / 17 | +0.195 [+0.001, +0.402] |
| direct / capacity_vs_linear | raw-molformer/lora − raw-molformer/linear | full-QAC105 / scaffold | 3 / 4 | +0.195 [−0.036, +0.528] |
| direct / capacity_vs_linear | raw-molformer/partial − raw-molformer/linear | cation / cation | 3 / 103 | −0.119 [−0.253, +0.005] |
| direct / capacity_vs_linear | raw-molformer/partial − raw-molformer/linear | cation / scaffold | 3 / 29 | −0.119 [−0.290, +0.047] |
| direct / capacity_vs_linear | raw-molformer/partial − raw-molformer/linear | scaffold / scaffold | 3 / 29 | +0.011 [−0.141, +0.158] |
| direct / capacity_vs_linear | raw-molformer/partial − raw-molformer/linear | full-QAC105 / cation | 3 / 17 | +0.448 [+0.118, +0.819] |
| direct / capacity_vs_linear | raw-molformer/partial − raw-molformer/linear | full-QAC105 / scaffold | 3 / 4 | +0.448 [−0.008, +0.940] |
| direct / capacity_vs_linear | raw-molformer/full − raw-molformer/linear | cation / cation | 3 / 103 | −0.150 [−0.302, −0.009] |
| direct / capacity_vs_linear | raw-molformer/full − raw-molformer/linear | cation / scaffold | 3 / 29 | −0.150 [−0.337, +0.033] |
| direct / capacity_vs_linear | raw-molformer/full − raw-molformer/linear | scaffold / scaffold | 3 / 29 | −0.015 [−0.181, +0.157] |
| direct / capacity_vs_linear | raw-molformer/full − raw-molformer/linear | full-QAC105 / cation | 3 / 17 | +0.471 [+0.131, +0.851] |
| direct / capacity_vs_linear | raw-molformer/full − raw-molformer/linear | full-QAC105 / scaffold | 3 / 4 | +0.471 [−0.028, +1.010] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/partial | cation / cation | 3 / 103 | +0.146 [+0.080, +0.217] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/partial | cation / scaffold | 3 / 29 | +0.146 [+0.063, +0.225] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/partial | scaffold / scaffold | 3 / 29 | +0.093 [−0.006, +0.189] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/partial | full-QAC105 / cation | 3 / 17 | −0.252 [−0.594, +0.090] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/partial | full-QAC105 / scaffold | 3 / 4 | −0.252 [−0.603, +0.105] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/full | cation / cation | 3 / 103 | +0.177 [+0.094, +0.273] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/full | cation / scaffold | 3 / 29 | +0.177 [+0.071, +0.286] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/full | scaffold / scaffold | 3 / 29 | +0.119 [−0.003, +0.230] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/full | full-QAC105 / cation | 3 / 17 | −0.276 [−0.611, +0.061] |
| direct / lora_vs_backbone | raw-molformer/lora − raw-molformer/full | full-QAC105 / scaffold | 3 / 4 | −0.276 [−0.610, +0.097] |
| direct / real_vs_shuffled | expert/partial − expert-shuffled/partial | cation / cation | 3 / 103 | −0.132 [−0.283, +0.008] |
| direct / real_vs_shuffled | expert/partial − expert-shuffled/partial | cation / scaffold | 3 / 29 | −0.132 [−0.310, +0.015] |
| direct / real_vs_shuffled | expert/partial − expert-shuffled/partial | scaffold / scaffold | 3 / 29 | −0.156 [−0.311, −0.009] |
| direct / real_vs_shuffled | expert/partial − expert-shuffled/partial | full-QAC105 / cation | 3 / 17 | −0.551 [−1.169, −0.011] |
| direct / real_vs_shuffled | expert/partial − expert-shuffled/partial | full-QAC105 / scaffold | 3 / 4 | −0.551 [−1.321, +0.063] |
| direct / source_vs_raw_init | expert/partial − raw-molformer/partial | cation / cation | 3 / 103 | −0.098 [−0.256, +0.026] |
| direct / source_vs_raw_init | expert/partial − raw-molformer/partial | cation / scaffold | 3 / 29 | −0.098 [−0.290, +0.068] |
| direct / source_vs_raw_init | expert/partial − raw-molformer/partial | scaffold / scaffold | 3 / 29 | −0.162 [−0.315, −0.016] |
| direct / source_vs_raw_init | expert/partial − raw-molformer/partial | full-QAC105 / cation | 3 / 17 | −0.596 [−1.200, −0.085] |
| direct / source_vs_raw_init | expert/partial − raw-molformer/partial | full-QAC105 / scaffold | 3 / 4 | −0.596 [−1.439, +0.055] |
| ablation / real_vs_shuffled | expert/intact − expert-shuffled/intact | cation / cation | 5 / 103 | −0.120 [−0.201, −0.046] |
| ablation / real_vs_shuffled | expert/intact − expert-shuffled/intact | cation / scaffold | 5 / 29 | −0.120 [−0.221, −0.043] |
| ablation / real_vs_shuffled | expert/intact − expert-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.122 [−0.258, −0.003] |
| ablation / real_vs_shuffled | expert/intact − expert-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.282 [−0.513, −0.049] |
| ablation / real_vs_shuffled | expert/intact − expert-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.282 [−0.600, −0.031] |
| ablation / source_vs_pure_raw | expert/intact − raw-molformer/raw | cation / cation | 5 / 103 | −0.121 [−0.201, −0.041] |
| ablation / source_vs_pure_raw | expert/intact − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.121 [−0.216, −0.044] |
| ablation / source_vs_pure_raw | expert/intact − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.136 [−0.268, −0.021] |
| ablation / source_vs_pure_raw | expert/intact − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | −0.211 [−0.398, −0.051] |
| ablation / source_vs_pure_raw | expert/intact − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | −0.211 [−0.516, +0.009] |
| direct / real_vs_shuffled | quant-continuous/partial − quant-shuffled/partial | cation / cation | 3 / 103 | −0.083 [−0.172, +0.017] |
| direct / real_vs_shuffled | quant-continuous/partial − quant-shuffled/partial | cation / scaffold | 3 / 29 | −0.083 [−0.178, +0.017] |
| direct / real_vs_shuffled | quant-continuous/partial − quant-shuffled/partial | scaffold / scaffold | 3 / 29 | −0.038 [−0.163, +0.073] |
| direct / real_vs_shuffled | quant-continuous/partial − quant-shuffled/partial | full-QAC105 / cation | 3 / 17 | −0.041 [−0.235, +0.217] |
| direct / real_vs_shuffled | quant-continuous/partial − quant-shuffled/partial | full-QAC105 / scaffold | 3 / 4 | −0.041 [−0.185, +0.218] |
| direct / source_vs_raw_init | quant-continuous/partial − raw-molformer/partial | cation / cation | 3 / 103 | −0.157 [−0.285, −0.031] |
| direct / source_vs_raw_init | quant-continuous/partial − raw-molformer/partial | cation / scaffold | 3 / 29 | −0.157 [−0.285, −0.028] |
| direct / source_vs_raw_init | quant-continuous/partial − raw-molformer/partial | scaffold / scaffold | 3 / 29 | −0.128 [−0.281, +0.063] |
| direct / source_vs_raw_init | quant-continuous/partial − raw-molformer/partial | full-QAC105 / cation | 3 / 17 | +0.068 [−0.195, +0.333] |
| direct / source_vs_raw_init | quant-continuous/partial − raw-molformer/partial | full-QAC105 / scaffold | 3 / 4 | +0.068 [−0.191, +0.391] |
| ablation / real_vs_shuffled | quant-continuous/intact − quant-shuffled/intact | cation / cation | 5 / 103 | −0.157 [−0.231, −0.085] |
| ablation / real_vs_shuffled | quant-continuous/intact − quant-shuffled/intact | cation / scaffold | 5 / 29 | −0.157 [−0.243, −0.087] |
| ablation / real_vs_shuffled | quant-continuous/intact − quant-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.131 [−0.249, −0.025] |
| ablation / real_vs_shuffled | quant-continuous/intact − quant-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.040 [−0.188, +0.098] |
| ablation / real_vs_shuffled | quant-continuous/intact − quant-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.040 [−0.185, +0.103] |
| ablation / source_vs_pure_raw | quant-continuous/intact − raw-molformer/raw | cation / cation | 5 / 103 | −0.144 [−0.229, −0.063] |
| ablation / source_vs_pure_raw | quant-continuous/intact − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.144 [−0.252, −0.054] |
| ablation / source_vs_pure_raw | quant-continuous/intact − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.163 [−0.285, −0.061] |
| ablation / source_vs_pure_raw | quant-continuous/intact − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | −0.028 [−0.129, +0.063] |
| ablation / source_vs_pure_raw | quant-continuous/intact − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | −0.028 [−0.145, +0.057] |
| direct / real_vs_shuffled | quant-binary/partial − quant-binary-shuffled/partial | cation / cation | 3 / 103 | −0.200 [−0.356, −0.056] |
| direct / real_vs_shuffled | quant-binary/partial − quant-binary-shuffled/partial | cation / scaffold | 3 / 29 | −0.200 [−0.362, −0.039] |
| direct / real_vs_shuffled | quant-binary/partial − quant-binary-shuffled/partial | scaffold / scaffold | 3 / 29 | −0.126 [−0.242, −0.013] |
| direct / real_vs_shuffled | quant-binary/partial − quant-binary-shuffled/partial | full-QAC105 / cation | 3 / 17 | −0.566 [−1.356, +0.066] |
| direct / real_vs_shuffled | quant-binary/partial − quant-binary-shuffled/partial | full-QAC105 / scaffold | 3 / 4 | −0.566 [−1.604, +0.215] |
| direct / source_vs_raw_init | quant-binary/partial − raw-molformer/partial | cation / cation | 3 / 103 | −0.150 [−0.304, −0.011] |
| direct / source_vs_raw_init | quant-binary/partial − raw-molformer/partial | cation / scaffold | 3 / 29 | −0.150 [−0.303, +0.011] |
| direct / source_vs_raw_init | quant-binary/partial − raw-molformer/partial | scaffold / scaffold | 3 / 29 | −0.095 [−0.218, +0.023] |
| direct / source_vs_raw_init | quant-binary/partial − raw-molformer/partial | full-QAC105 / cation | 3 / 17 | −0.498 [−1.135, −0.035] |
| direct / source_vs_raw_init | quant-binary/partial − raw-molformer/partial | full-QAC105 / scaffold | 3 / 4 | −0.498 [−1.374, +0.137] |
| ablation / real_vs_shuffled | quant-binary/intact − quant-binary-shuffled/intact | cation / cation | 5 / 103 | −0.083 [−0.205, +0.025] |
| ablation / real_vs_shuffled | quant-binary/intact − quant-binary-shuffled/intact | cation / scaffold | 5 / 29 | −0.083 [−0.228, +0.045] |
| ablation / real_vs_shuffled | quant-binary/intact − quant-binary-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.110 [−0.243, +0.004] |
| ablation / real_vs_shuffled | quant-binary/intact − quant-binary-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.273 [−0.549, −0.021] |
| ablation / real_vs_shuffled | quant-binary/intact − quant-binary-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.273 [−0.626, +0.024] |
| ablation / source_vs_pure_raw | quant-binary/intact − raw-molformer/raw | cation / cation | 5 / 103 | −0.053 [−0.147, +0.037] |
| ablation / source_vs_pure_raw | quant-binary/intact − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.053 [−0.177, +0.059] |
| ablation / source_vs_pure_raw | quant-binary/intact − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.121 [−0.260, +0.015] |
| ablation / source_vs_pure_raw | quant-binary/intact − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | −0.166 [−0.388, +0.040] |
| ablation / source_vs_pure_raw | quant-binary/intact − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | −0.166 [−0.527, +0.123] |
| direct / human_vs_quantitative | expert/partial − quant-continuous/partial | cation / cation | 3 / 103 | +0.060 [−0.049, +0.157] |
| direct / human_vs_quantitative | expert/partial − quant-continuous/partial | cation / scaffold | 3 / 29 | +0.060 [−0.074, +0.162] |
| direct / human_vs_quantitative | expert/partial − quant-continuous/partial | scaffold / scaffold | 3 / 29 | −0.034 [−0.160, +0.080] |
| direct / human_vs_quantitative | expert/partial − quant-continuous/partial | full-QAC105 / cation | 3 / 17 | −0.664 [−1.131, −0.279] |
| direct / human_vs_quantitative | expert/partial − quant-continuous/partial | full-QAC105 / scaffold | 3 / 4 | −0.664 [−1.301, −0.166] |
| direct / human_vs_quantitative | expert/partial − quant-binary/partial | cation / cation | 3 / 103 | +0.052 [−0.015, +0.115] |
| direct / human_vs_quantitative | expert/partial − quant-binary/partial | cation / scaffold | 3 / 29 | +0.052 [−0.027, +0.138] |
| direct / human_vs_quantitative | expert/partial − quant-binary/partial | scaffold / scaffold | 3 / 29 | −0.067 [−0.136, +0.002] |
| direct / human_vs_quantitative | expert/partial − quant-binary/partial | full-QAC105 / cation | 3 / 17 | −0.098 [−0.287, +0.077] |
| direct / human_vs_quantitative | expert/partial − quant-binary/partial | full-QAC105 / scaffold | 3 / 4 | −0.098 [−0.302, +0.066] |
| ablation / weight_rewind_minus_intact | expert/rewind_outer_norm − expert/intact | cation / cation | 5 / 103 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert/rewind_outer_norm − expert/intact | cation / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert/rewind_outer_norm − expert/intact | scaffold / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert/rewind_outer_norm − expert/intact | full-QAC105 / cation | 5 / 17 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert/rewind_outer_norm − expert/intact | full-QAC105 / scaffold | 5 / 4 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert/rewind_blocks − expert/intact | cation / cation | 5 / 103 | +0.108 [+0.034, +0.192] |
| ablation / weight_rewind_minus_intact | expert/rewind_blocks − expert/intact | cation / scaffold | 5 / 29 | +0.108 [+0.038, +0.201] |
| ablation / weight_rewind_minus_intact | expert/rewind_blocks − expert/intact | scaffold / scaffold | 5 / 29 | +0.096 [−0.004, +0.228] |
| ablation / weight_rewind_minus_intact | expert/rewind_blocks − expert/intact | full-QAC105 / cation | 5 / 17 | +0.243 [−0.005, +0.484] |
| ablation / weight_rewind_minus_intact | expert/rewind_blocks − expert/intact | full-QAC105 / scaffold | 5 / 4 | +0.243 [−0.067, +0.582] |
| ablation / weight_rewind_minus_intact | expert/rewind_all − expert/intact | cation / cation | 5 / 103 | +0.109 [+0.035, +0.192] |
| ablation / weight_rewind_minus_intact | expert/rewind_all − expert/intact | cation / scaffold | 5 / 29 | +0.109 [+0.037, +0.201] |
| ablation / weight_rewind_minus_intact | expert/rewind_all − expert/intact | scaffold / scaffold | 5 / 29 | +0.097 [−0.004, +0.228] |
| ablation / weight_rewind_minus_intact | expert/rewind_all − expert/intact | full-QAC105 / cation | 5 / 17 | +0.243 [−0.005, +0.484] |
| ablation / weight_rewind_minus_intact | expert/rewind_all − expert/intact | full-QAC105 / scaffold | 5 / 4 | +0.243 [−0.067, +0.582] |
| ablation / buffer_state_vs_pure_raw | expert/rewind_all − raw-molformer/raw | cation / cation | 5 / 103 | −0.012 [−0.080, +0.054] |
| ablation / buffer_state_vs_pure_raw | expert/rewind_all − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.012 [−0.089, +0.059] |
| ablation / buffer_state_vs_pure_raw | expert/rewind_all − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.039 [−0.109, +0.033] |
| ablation / buffer_state_vs_pure_raw | expert/rewind_all − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | +0.032 [−0.145, +0.209] |
| ablation / buffer_state_vs_pure_raw | expert/rewind_all − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | +0.032 [−0.154, +0.205] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_outer_norm − quant-continuous/intact | cation / cation | 5 / 103 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_outer_norm − quant-continuous/intact | cation / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_outer_norm − quant-continuous/intact | scaffold / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_outer_norm − quant-continuous/intact | full-QAC105 / cation | 5 / 17 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_outer_norm − quant-continuous/intact | full-QAC105 / scaffold | 5 / 4 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_blocks − quant-continuous/intact | cation / cation | 5 / 103 | +0.133 [+0.048, +0.220] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_blocks − quant-continuous/intact | cation / scaffold | 5 / 29 | +0.133 [+0.042, +0.230] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_blocks − quant-continuous/intact | scaffold / scaffold | 5 / 29 | +0.124 [+0.036, +0.226] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_blocks − quant-continuous/intact | full-QAC105 / cation | 5 / 17 | +0.060 [−0.099, +0.241] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_blocks − quant-continuous/intact | full-QAC105 / scaffold | 5 / 4 | +0.060 [−0.132, +0.283] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_all − quant-continuous/intact | cation / cation | 5 / 103 | +0.132 [+0.047, +0.220] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_all − quant-continuous/intact | cation / scaffold | 5 / 29 | +0.132 [+0.042, +0.230] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_all − quant-continuous/intact | scaffold / scaffold | 5 / 29 | +0.124 [+0.036, +0.226] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_all − quant-continuous/intact | full-QAC105 / cation | 5 / 17 | +0.060 [−0.099, +0.241] |
| ablation / weight_rewind_minus_intact | quant-continuous/rewind_all − quant-continuous/intact | full-QAC105 / scaffold | 5 / 4 | +0.060 [−0.132, +0.283] |
| ablation / buffer_state_vs_pure_raw | quant-continuous/rewind_all − raw-molformer/raw | cation / cation | 5 / 103 | −0.012 [−0.080, +0.054] |
| ablation / buffer_state_vs_pure_raw | quant-continuous/rewind_all − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.012 [−0.089, +0.059] |
| ablation / buffer_state_vs_pure_raw | quant-continuous/rewind_all − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.039 [−0.109, +0.033] |
| ablation / buffer_state_vs_pure_raw | quant-continuous/rewind_all − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | +0.032 [−0.145, +0.209] |
| ablation / buffer_state_vs_pure_raw | quant-continuous/rewind_all − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | +0.032 [−0.154, +0.205] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_outer_norm − quant-binary/intact | cation / cation | 5 / 103 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_outer_norm − quant-binary/intact | cation / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_outer_norm − quant-binary/intact | scaffold / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_outer_norm − quant-binary/intact | full-QAC105 / cation | 5 / 17 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_outer_norm − quant-binary/intact | full-QAC105 / scaffold | 5 / 4 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_blocks − quant-binary/intact | cation / cation | 5 / 103 | +0.040 [−0.062, +0.146] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_blocks − quant-binary/intact | cation / scaffold | 5 / 29 | +0.040 [−0.071, +0.159] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_blocks − quant-binary/intact | scaffold / scaffold | 5 / 29 | +0.082 [−0.026, +0.208] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_blocks − quant-binary/intact | full-QAC105 / cation | 5 / 17 | +0.198 [−0.060, +0.485] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_blocks − quant-binary/intact | full-QAC105 / scaffold | 5 / 4 | +0.198 [−0.157, +0.603] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_all − quant-binary/intact | cation / cation | 5 / 103 | +0.041 [−0.061, +0.146] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_all − quant-binary/intact | cation / scaffold | 5 / 29 | +0.041 [−0.070, +0.160] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_all − quant-binary/intact | scaffold / scaffold | 5 / 29 | +0.082 [−0.026, +0.208] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_all − quant-binary/intact | full-QAC105 / cation | 5 / 17 | +0.198 [−0.060, +0.485] |
| ablation / weight_rewind_minus_intact | quant-binary/rewind_all − quant-binary/intact | full-QAC105 / scaffold | 5 / 4 | +0.198 [−0.157, +0.603] |
| ablation / buffer_state_vs_pure_raw | quant-binary/rewind_all − raw-molformer/raw | cation / cation | 5 / 103 | −0.012 [−0.080, +0.054] |
| ablation / buffer_state_vs_pure_raw | quant-binary/rewind_all − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.012 [−0.089, +0.059] |
| ablation / buffer_state_vs_pure_raw | quant-binary/rewind_all − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.039 [−0.109, +0.033] |
| ablation / buffer_state_vs_pure_raw | quant-binary/rewind_all − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | +0.032 [−0.145, +0.209] |
| ablation / buffer_state_vs_pure_raw | quant-binary/rewind_all − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | +0.032 [−0.154, +0.205] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_outer_norm − expert-shuffled/intact | cation / cation | 5 / 103 | +0.001 [−0.001, +0.004] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_outer_norm − expert-shuffled/intact | cation / scaffold | 5 / 29 | +0.001 [−0.001, +0.004] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_outer_norm − expert-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.000 [−0.002, +0.000] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_outer_norm − expert-shuffled/intact | full-QAC105 / cation | 5 / 17 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_outer_norm − expert-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_blocks − expert-shuffled/intact | cation / cation | 5 / 103 | −0.011 [−0.065, +0.045] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_blocks − expert-shuffled/intact | cation / scaffold | 5 / 29 | −0.011 [−0.070, +0.051] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_blocks − expert-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.025 [−0.087, +0.034] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_blocks − expert-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.039 [−0.191, +0.131] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_blocks − expert-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.039 [−0.193, +0.161] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_all − expert-shuffled/intact | cation / cation | 5 / 103 | −0.011 [−0.065, +0.046] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_all − expert-shuffled/intact | cation / scaffold | 5 / 29 | −0.011 [−0.070, +0.052] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_all − expert-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.025 [−0.087, +0.034] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_all − expert-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.039 [−0.191, +0.131] |
| ablation / weight_rewind_minus_intact | expert-shuffled/rewind_all − expert-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.039 [−0.193, +0.161] |
| ablation / buffer_state_vs_pure_raw | expert-shuffled/rewind_all − raw-molformer/raw | cation / cation | 5 / 103 | −0.012 [−0.080, +0.054] |
| ablation / buffer_state_vs_pure_raw | expert-shuffled/rewind_all − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.012 [−0.089, +0.059] |
| ablation / buffer_state_vs_pure_raw | expert-shuffled/rewind_all − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.039 [−0.109, +0.033] |
| ablation / buffer_state_vs_pure_raw | expert-shuffled/rewind_all − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | +0.032 [−0.145, +0.209] |
| ablation / buffer_state_vs_pure_raw | expert-shuffled/rewind_all − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | +0.032 [−0.154, +0.205] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_outer_norm − quant-shuffled/intact | cation / cation | 5 / 103 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_outer_norm − quant-shuffled/intact | cation / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_outer_norm − quant-shuffled/intact | scaffold / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_outer_norm − quant-shuffled/intact | full-QAC105 / cation | 5 / 17 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_outer_norm − quant-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_blocks − quant-shuffled/intact | cation / cation | 5 / 103 | −0.025 [−0.088, +0.041] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_blocks − quant-shuffled/intact | cation / scaffold | 5 / 29 | −0.025 [−0.085, +0.044] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_blocks − quant-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.007 [−0.078, +0.061] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_blocks − quant-shuffled/intact | full-QAC105 / cation | 5 / 17 | +0.020 [−0.198, +0.263] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_blocks − quant-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | +0.020 [−0.189, +0.336] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_all − quant-shuffled/intact | cation / cation | 5 / 103 | −0.025 [−0.088, +0.041] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_all − quant-shuffled/intact | cation / scaffold | 5 / 29 | −0.025 [−0.085, +0.044] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_all − quant-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.007 [−0.078, +0.061] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_all − quant-shuffled/intact | full-QAC105 / cation | 5 / 17 | +0.020 [−0.198, +0.263] |
| ablation / weight_rewind_minus_intact | quant-shuffled/rewind_all − quant-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | +0.020 [−0.189, +0.336] |
| ablation / buffer_state_vs_pure_raw | quant-shuffled/rewind_all − raw-molformer/raw | cation / cation | 5 / 103 | −0.012 [−0.080, +0.054] |
| ablation / buffer_state_vs_pure_raw | quant-shuffled/rewind_all − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.012 [−0.089, +0.059] |
| ablation / buffer_state_vs_pure_raw | quant-shuffled/rewind_all − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.039 [−0.109, +0.033] |
| ablation / buffer_state_vs_pure_raw | quant-shuffled/rewind_all − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | +0.032 [−0.145, +0.209] |
| ablation / buffer_state_vs_pure_raw | quant-shuffled/rewind_all − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | +0.032 [−0.154, +0.205] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_outer_norm − quant-binary-shuffled/intact | cation / cation | 5 / 103 | +0.001 [−0.003, +0.007] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_outer_norm − quant-binary-shuffled/intact | cation / scaffold | 5 / 29 | +0.001 [−0.003, +0.007] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_outer_norm − quant-binary-shuffled/intact | scaffold / scaffold | 5 / 29 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_outer_norm − quant-binary-shuffled/intact | full-QAC105 / cation | 5 / 17 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_outer_norm − quant-binary-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | +0.000 [+0.000, +0.000] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_blocks − quant-binary-shuffled/intact | cation / cation | 5 / 103 | −0.044 [−0.127, +0.039] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_blocks − quant-binary-shuffled/intact | cation / scaffold | 5 / 29 | −0.044 [−0.131, +0.038] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_blocks − quant-binary-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.027 [−0.118, +0.061] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_blocks − quant-binary-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.079 [−0.299, +0.161] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_blocks − quant-binary-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.079 [−0.311, +0.186] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_all − quant-binary-shuffled/intact | cation / cation | 5 / 103 | −0.043 [−0.124, +0.038] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_all − quant-binary-shuffled/intact | cation / scaffold | 5 / 29 | −0.043 [−0.129, +0.038] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_all − quant-binary-shuffled/intact | scaffold / scaffold | 5 / 29 | −0.028 [−0.120, +0.061] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_all − quant-binary-shuffled/intact | full-QAC105 / cation | 5 / 17 | −0.075 [−0.289, +0.164] |
| ablation / weight_rewind_minus_intact | quant-binary-shuffled/rewind_all − quant-binary-shuffled/intact | full-QAC105 / scaffold | 5 / 4 | −0.075 [−0.302, +0.192] |
| ablation / buffer_state_vs_pure_raw | quant-binary-shuffled/rewind_all − raw-molformer/raw | cation / cation | 5 / 103 | −0.012 [−0.080, +0.054] |
| ablation / buffer_state_vs_pure_raw | quant-binary-shuffled/rewind_all − raw-molformer/raw | cation / scaffold | 5 / 29 | −0.012 [−0.089, +0.059] |
| ablation / buffer_state_vs_pure_raw | quant-binary-shuffled/rewind_all − raw-molformer/raw | scaffold / scaffold | 5 / 29 | −0.039 [−0.109, +0.033] |
| ablation / buffer_state_vs_pure_raw | quant-binary-shuffled/rewind_all − raw-molformer/raw | full-QAC105 / cation | 5 / 17 | +0.032 [−0.145, +0.209] |
| ablation / buffer_state_vs_pure_raw | quant-binary-shuffled/rewind_all − raw-molformer/raw | full-QAC105 / scaffold | 5 / 4 | +0.032 [−0.154, +0.205] |
| routes / direct_minus_frozen_decoder | expert/partial − expert/intact | cation / cation | 3 / 103 | +0.054 [−0.051, +0.147] |
| routes / direct_minus_frozen_decoder | expert/partial − expert/intact | cation / scaffold | 3 / 29 | +0.054 [−0.040, +0.152] |
| routes / direct_minus_frozen_decoder | expert/partial − expert/intact | scaffold / scaffold | 3 / 29 | +0.016 [−0.117, +0.153] |
| routes / direct_minus_frozen_decoder | expert/partial − expert/intact | full-QAC105 / cation | 3 / 17 | +0.306 [−0.087, +0.692] |
| routes / direct_minus_frozen_decoder | expert/partial − expert/intact | full-QAC105 / scaffold | 3 / 4 | +0.306 [−0.278, +0.971] |
| routes / direct_minus_frozen_decoder | quant-continuous/partial − quant-continuous/intact | cation / cation | 3 / 103 | +0.021 [−0.093, +0.143] |
| routes / direct_minus_frozen_decoder | quant-continuous/partial − quant-continuous/intact | cation / scaffold | 3 / 29 | +0.021 [−0.080, +0.150] |
| routes / direct_minus_frozen_decoder | quant-continuous/partial − quant-continuous/intact | scaffold / scaffold | 3 / 29 | +0.072 [−0.069, +0.258] |
| routes / direct_minus_frozen_decoder | quant-continuous/partial − quant-continuous/intact | full-QAC105 / cation | 3 / 17 | +0.846 [+0.373, +1.284] |
| routes / direct_minus_frozen_decoder | quant-continuous/partial − quant-continuous/intact | full-QAC105 / scaffold | 3 / 4 | +0.846 [+0.182, +1.390] |
| routes / direct_minus_frozen_decoder | quant-binary/partial − quant-binary/intact | cation / cation | 3 / 103 | −0.042 [−0.179, +0.089] |
| routes / direct_minus_frozen_decoder | quant-binary/partial − quant-binary/intact | cation / scaffold | 3 / 29 | −0.042 [−0.158, +0.081] |
| routes / direct_minus_frozen_decoder | quant-binary/partial − quant-binary/intact | scaffold / scaffold | 3 / 29 | +0.077 [−0.035, +0.185] |
| routes / direct_minus_frozen_decoder | quant-binary/partial − quant-binary/intact | full-QAC105 / cation | 3 / 17 | +0.442 [+0.084, +0.884] |
| routes / direct_minus_frozen_decoder | quant-binary/partial − quant-binary/intact | full-QAC105 / scaffold | 3 / 4 | +0.442 [+0.042, +1.059] |

S27. Independent verification and limitations

Every target value, qualifier and group membership was checked against the original registry. No train/test cation or held-out scaffold overlap was found under the applicable scheme. Paired direct fits share initial linear heads, minibatch order and train-only target scale. All 93 intact/raw prediction sets agree with v14 to CSV numerical precision (<10−12); all 62 original intact/raw QAC/OOD representation arrays replay exactly. All six rewind-all prediction sets are identical within each seed and regime. The source buffers are shared within seed and unchanged by intervention. All 33 final-OOD target models were independently reloaded from saved checkpoints and reproduce their 2,244 predictions, including the bound, within CSV precision (<10−12). Server code, hashes, launch ledgers and the archived encoding layout support replay without the Mac being active.

The bound IT505 Ec_MBC >500 mg/L is excluded from exact scores and retained in every prediction file. Censor-sensitivity CSVs use max(log2(500) − prediction, 0) with the exact residuals, giving lower bounds on RMSE/MAE rather than treating 500 as the measured value. Actual concentrations above the bound remain unknown. All endpoint scores and unsuccessful predictions are retained. These results identify effects of specific label assignments and computational weight interventions; they do not identify a causal antibacterial mechanism or an independent human-information channel before annotation provenance is supplied.

Architectural correction to main Methods: the pinned MolFormer pooler uses parameter-free mean pooling. Matched source fine-tuning trained upper eight blocks, the outer encoder LayerNorm and a scalar head (28,375,297 parameters), rather than a trainable pooler. Direct partial target fits additionally use a four-output head and head LayerNorm (28,379,140 parameters). The code and every original result are unchanged by correcting this description. Bibliographic correction: ChemFM’s second author is K. Zacour, replacing the earlier erroneous K. Hanna.

Table S33. Per-seed derivation of the primary human-guided censored-endpoint sensitivity from independently replayed predictions. Each seed has its own exact residuals and its own IT505 lower-bound error. All errors use log2(mg/L). The final row averages seed-specific RMSE values, not their predictions.

| Source seed | IT505 prediction (mg/L) | Error lower bound log2 | Pooled RMSE: 67 exact → 68 lower bound | Ec MBC RMSE: 16 exact → 17 lower bound |
| --- | --- | --- | --- | --- |
| 0 | 36.980 | 3.757 | 2.027 → 2.063 | 2.136 → 2.264 |
| 1 | 21.170 | 4.562 | 2.128 → 2.184 | 2.219 → 2.420 |
| 2 | 30.823 | 4.020 | 2.164 → 2.202 | 2.388 → 2.513 |
| 3 | 30.848 | 4.019 | 1.931 → 1.978 | 2.023 → 2.192 |
| 4 | 24.124 | 4.373 | 2.022 → 2.076 | 2.208 → 2.390 |
| Mean of seed-specific RMSEs | — | — | 2.054 → 2.101 | 2.195 → 2.356 |

For seed s, let SSE_s be the sum of squared residuals on its 67 exact pooled endpoints, and h_s = max(log2(500) − prediction_s(IT505 Ec_MBC), 0). Its 68-endpoint RMSE lower bound is sqrt((SSE_s + h_s²)/68). The Ec_MBC calculation uses its 16 exact residuals and denominator 17. Averaging the five seed-specific roots yields pooled 2.100536 (reported 2.101) and Ec_MBC 2.355897 (reported 2.356). The minimum error across seeds is not used as if it applied to every fitted model. The true unknown concentration may give a larger error.

S28. Detailed discussion and methods relocated from the main text

This section preserves the detailed v16 discussion after shortening the main article. Full numerical tables already present as Tables S23 and S28 are not duplicated. References in S28 follow the renumbered main-article bibliography. The chemistry/assay records in S16 and coauthor fields are retained.

S28.1. Task descriptions and encoding

One-hot indicators and text vectors both identify the same four tasks. The fixed texts name the strain and describe MIC or MBC; their 1,536-dimensional vectors are identical for every molecule within a task. They add no new measured activity or compound-specific biological data. Text coding can alter which task partitions CatBoost selects, but any difference here cannot by itself identify semantic understanding or biological information transfer.

For human-guided representations, text coding changes pooled QAC RMSE from 1.737 to 1.723; paired text-minus-one-hot ΔRMSE is -0.015 [-0.051, +0.024]. Figure S27 shows the task-specific scores. The paired text-versus-one-hot intervals include zero for the primary trained arms on pooled QAC loss, and no consistent text-coding advantage is established on OOD. The historical no-metadata comparison is reconstructed with four separate endpoint models in Supporting Information; it changes pooling and the number of rows per fitted model as well as task metadata, and is not an isolated metadata intervention.

Endpoint-specific text effects can point in opposite directions. On the OOD raw-feature reference, text coding reduces E. coli MBC error by 0.311 log2 units but increases S. aureus MBC error by 0.123; both exploratory four-family intervals exclude zero in opposite directions. These reversals, reported with all endpoint contrasts in the computational supplement, reinforce the distinction between an occasional task-partitioning benefit and a consistent semantic advantage.


Figure S27. Task encoding on the original 105 QACs. Circles denote one-hot and open squares fixed text embeddings. Lines connect encodings applied to the same source arm and target folds. Error bars are source-seed SD; the raw representation is a single fixed run. The comparison does not establish a semantic benefit of language-model task descriptions.

S28.2. Graph and tabular decoder comparison

We evaluated Chemprop D-MPNN (7), TabPFN-V2 (8), TabFM (9), AutoGluon (10) and a CatBoost control on the same QAC-105 cation and scaffold folds and the untouched OOD-17 collection. The four tabular decoders compare RDKit descriptors with raw and guided MolFormer features. Guided features use the existing human, continuous-MIC and binary-MIC source checkpoints for seed 0. Embeddings receive training-only PCA to 32 dimensions, and each endpoint has a separate fitted decoder. Consequently, this is an exploratory decoder robustness comparison; its scores are distinct from the five-seed joint-task primary model.

Human-guided representations have lower pooled error point estimates than raw features for each of the four tabular decoders in all three evaluation regimes. They also have lower point errors than both quantitative representations under cation holdout and on OOD-17. Scaffold holdout exposes exceptions: continuous MIC gives CatBoost RMSE 1.892 versus human 1.901, and binary MIC gives AutoGluon 1.911 versus human 1.934. The results support useful transfer across decoder choices, conditional on one source realisation. They do not override the primary five-seed cation-CV result, where continuous MIC has slightly lower mean error than human supervision.

On OOD-17, human/continuous-MIC/binary-MIC/raw RMSE is 1.966/2.265/1.995/2.225 for TabPFN-V2 and 1.992/2.541/2.110/2.299 for TabFM (Figure S28). RDKit yields 1.978 and 2.027, respectively, close to the human point estimates. The paired cation-cluster intervals for human minus RDKit include zero: [−0.150, +0.149] for TabPFN-V2 and [−0.162, +0.108] for TabFM. With only four OOD families, these estimates do not establish general OOD superiority or equivalence.


Figure S28. Absolute endpoint-error distributions for TabPFN-V2 and TabFM under cation holdout, scaffold holdout and OOD evaluation. Grey, blue, lavender, mint and peach identify RDKit, raw, human, continuous-MIC and binary-MIC features, respectively. Bars indicate median and IQR. Each CV distribution contains 420 endpoint errors from 105 compounds; OOD contains 67 exact endpoint errors from 17 compounds. Endpoints from one molecule are dependent. Density shape and overlapping medians are descriptive; paired intervals resample molecular groups. All visible errors are retained.

The descriptor reference also challenges an unrestricted foundation-model claim. RDKit+CatBoost attains cation/scaffold RMSE 1.615/1.818, and RDKit+AutoGluon attains 1.716/1.828. Chemprop gives 2.031/2.003/2.375 for cation/scaffold/OOD under its fixed 100-epoch, three-seed protocol. These outcomes concern a small cohort and the declared budgets; they are not general rankings of graphs, descriptors and language models. All endpoint scores, unsuccessful predictions, model settings and paired intervals are reported in Supporting Information S21.

S28.3. Direct-target performance and adaptation capacity

Before interpreting representation changes, we tested direct four-output MIC/MBC regression on the same five cation and scaffold folds and final QAC-105→OOD-17 split. From the pretrained encoder, frozen linear, frozen MLP, query/value LoRA, partial and full fine-tuning use three paired target seeds. Partial target fine-tuning is also initialised from each real and shuffled source arm with the matching source seed. All 363 target fits use a fixed 30-epoch budget and train-only standardisation of the four endpoints. Table S28 reports every configuration; endpoint R², MAE and rank correlations are in S24.


Figure S29. Predictive error for five target-adaptation strategies starting from the same pretrained model. Dots are three seed-specific pooled errors; horizontal bars show their arithmetic mean. The compact MLP learns an external projection on fixed features; LoRA learns rank-eight updates inside query/value modules. Lower parameter count is not itself evidence of a better prediction procedure. Strategies are identified by their x-axis labels; a common neutral colour avoids reusing source-supervision colours.

From pretrained initialisation, cation-CV RMSE is 1.863 for full fine-tuning, 2.013 for a frozen linear head and 2.040 for LoRA. LoRA minus full-fine-tuning ΔRMSE is +0.177 [+0.071, +0.286] under the exploratory scaffold-group interval convention. This outcome does not favour small adapters in the tested cation-CV procedure. The OOD point ordering differs: linear/LoRA/full RMSE is 2.560/2.756/3.032. Prediction quality and the amount of adaptation must therefore be discussed with the validation regime and fixed optimisation recipe.

With human source initialisation, direct target fine-tuning gives cation/scaffold/OOD RMSE 1.797/1.834/2.412; pretrained-initialised partial target fine-tuning gives 1.894/1.996/3.008. Source guidance therefore changes the starting representation; this comparison also includes its additional source-training data and budget. Real-versus-shuffled source controls, reported with all intervals in S26, distinguish label assignment from simply adding a training stage.

The direct prediction route also retains a label-assignment effect: human minus shuffled-human scaffold-CV ΔRMSE is −0.156 [−0.311, −0.009]. Cation-CV human point error remains above both real quantitative initialisations (Table S28); the human-versus-quantitative cation intervals include zero. On OOD, direct human minus continuous-MIC ΔRMSE is −0.664 [−1.301, −0.166]. That conditional contrast favours the human arm in this four-family collection, without establishing universal superiority over numerical measurements.

The two prediction routes are compared using the same first three source checkpoints. For human guidance, direct/frozen-encoder-plus-CatBoost RMSE is 1.797/1.743 under cation holdout, 1.834/1.819 under scaffold holdout and 2.412/2.106 on OOD. The OOD direct-minus-decoder contrast is +0.306 [−0.278, +0.971]. This conditional, four-family interval addresses the declared prediction pipelines. The primary five-source-seed decoder results in Tables 2–4 remain separate. Figure S26 shows split violins for both routes under all three real source signals; density shapes do not establish causal knowledge.

Fixed epoch count does not guarantee equal optimisation difficulty, and the five strategies have different trainable capacities and learning rates. Frozen heads use the archived feature-map state; encoder training can also refresh nonpersistent feature-map buffers. This capacity comparison evaluates full computational procedures. It is not a pure intervention on parameter count or a claim about the best achievable LoRA/full-fine-tuning configuration. The separate weight controls below hold those buffers fixed.

S28.4. Label and component-weight interpretation

We use an operational definition of learned signal: the contribution of adapted encoder parameters to held-out MIC/MBC prediction after refitting a common decoder. For each of 30 matched source checkpoints, we restore the pretrained outer encoder LayerNorm, upper eight blocks, or all encoder parameters, retaining the checkpoint’s persistent and nonpersistent feature-map buffers. CatBoost is refitted for each representation, avoiding the confound of feeding modified features to a decoder trained only on the intact representation. The pure pretrained reference retains its original buffers and is evaluated separately.

All intact encodings reproduce the archived arrays exactly, and refitting reproduces all 93 intact/raw cation, scaffold and OOD prediction sets. Source arms share buffer state within seed. Restoring all encoder parameters makes all six source arms identical in representation and decoder predictions within every seed and regime. Thus their label-dependent prediction differences require the adapted encoder weights; the controls do not identify the meaning of an individual feature or a biological mechanism.

For human guidance, restoring all encoder weights changes cation/scaffold/OOD RMSE by +0.109 [+0.037, +0.201], +0.097 [−0.004, +0.228] and +0.243 [−0.067, +0.582], respectively. The rewind-all representation is not the pure raw reference: on OOD its contrast with pure raw is +0.032 [−0.154, +0.205]. This separates the learned-weight contribution from a shared post-training feature-map state. The intervention supports only a contribution to the specified prediction loss where its interval resolves an effect. Whether the label signal contains independent human chemical knowledge still depends on H1–H7, including what numerical information annotators saw.

The human rewind-all interval resolves a higher cation-held-out error after removing learned weight updates. Its scaffold and four-family OOD intervals include zero. An interval containing zero is inconclusive at the present sample size, rather than evidence that no signal was learned. The outer-normalisation rewind leaves the human decoder predictions unchanged, whereas reverting the upper eight blocks produces almost the same loss contrast as reverting all encoder weights. This locates sensitivity within the tested computational procedure, not within a named human chemical concept.

The paired intervention changes which supervision is supplied to the same algorithm while retaining source chemistry, initialisation, source split and training schedule. Real-versus-shuffled labels preserve binary class counts or the continuous value distribution while disrupting the structure–label association. Improved loss under real human labels therefore concerns the learning procedure under that assignment. Comparison against raw features is needed in addition, because a trained representation may outperform a damaged shuffled representation without improving the original features.

On the cation-held-out pooled QAC loss, both real-versus-shuffled and human-versus-raw contrasts favour human guidance under the exploratory interval convention. This supports the usefulness of the available final labels in that setting. It does not identify the causal effect of a chemical fragment, charge count or assay protocol on antibacterial activity. Human-versus-continuous MIC also changes the objective, whereas binary MIC provides an objective-matched comparator. Unresolved differences are not statistical equivalence; no equivalence margin or annotation-to-measurement exchange rate is specified.

The original geometry and attribution analyses illustrate compression and reorganisation of foundation-model features. Similarity, t-SNE separation and SHAP attribution cannot by themselves identify a distinct biological component, prove that annotation denoises heterogeneous assays, or establish generalisation. Historical encoders were trained on archives overlapping the original target structures, so their favourable v5 tables and reconstructed task-coding results are preserved separately from the strict source-excluded comparisons. Assay heterogeneity motivates richer metadata; it does not make numerical measurements intrinsically inferior. Annotation information access and adjudication remain for coauthor completion.

S28.5. Historical scores and independent replay

In the archived matched partial-fine-tuning Q-HERO comparison, human/continuous-MIC/raw RMSE was 1.529/1.453/1.607 log2 µM: continuous MIC had lower error, and the human-versus-raw interval included zero. These prior outcomes are retained alongside the original-cohort analysis so that the revised emphasis cannot be read as universal human superiority.

An independent repeat of all 30 matched partial-fine-tuning runs recovered the source initialisations, molecule order and final training losses exactly. With the archived target-encoding batch layout, all 93 historical target arrays and all 62 QAC-105/OOD-17 arrays are byte-identical. Refitting the archived v14 decoders from cached arrays also reproduces every saved cation and scaffold prediction. Re-encoding the same models with a different batch composition produces feature perturbations around 10−6 and changes some CatBoost decisions. Replaying the archived layout removes this discrepancy. The primary tables therefore retain that layout; the altered-layout sensitivity is reported separately in S22.

Recovered April–May notebooks and a July follow-up contain saved outputs supporting the historical article scores. In particular, the July OOD regression RMSE is 2.133, whereas the May snapshot gives 2.276; these are different archived analyses. Their difference does not justify replacing the original 2.13 with 2.27. Earlier endpoint-row splits can place tasks from the same molecule in both training and test, and the historical representation sources overlap target chemistry. Those scores consequently address a different validation question from the strict source-excluded, cation/scaffold comparisons here. Exact Mac-to-Linux reproduction remains incomplete for some historical frozen-feature MLP branches; we retain these as supplementary environment sensitivities.

The independent server repeats preserve source IDs, label hashes, initial weights, minibatch order, update budget and pinned MolFormer revision. Reconstructed checkpoints retain trained parameters and all persistent and nonpersistent evaluation buffers. Exact target-array comparisons distinguish the archived batch layout from a fresh 105-compound encoding layout. Historical notebook snapshots are provenance artifacts with saved outputs; finding an output is not equivalent to rerunning that entire notebook. Snapshot hashes, cell indices and the v5-number mapping are in notebook_recovery_20261012. The independent computational records are in server_models_20261012; S22 records unresolved cross-environment branches.

S28.6. Complete model configurations

All model comparisons use the original v14 target folds and log2(mg/L) endpoints. Train-only median imputation, zero-variance removal and scaling are followed by full-SVD PCA-32 for each 768-dimensional representation; RDKit descriptors use their remaining native dimensions. Preprocessors are fitted once per outer training fold and never on test or OOD rows. Four separate endpoint models are fitted for each tabular representation. The full-QAC model uses all 105 compounds to supply context or training data for OOD predictions. The source features use the archived seed-0 checkpoints, avoiding re-encoding batch changes in the decoder comparison.

The CatBoost control retains 300 iterations, depth five, learning rate 0.05 and seed 1729. AutoGluon-Tabular 1.6.3 selects among RF, XT, GBM and CAT with a 60-second budget, a fixed group-disjoint inner holdout and no bagging, stacking or weighted ensemble. Its selected model is refitted on the complete outer training fold; refitting takes additional time. In the OOD run, the inner split groups QAC training compounds by scaffold. Preprocessing uses only the outer training fold, so this is an outer-test evaluation of the declared pipeline rather than a fully nested inner-preprocessing study.

TabPFN 9.1.0 runs the publicly downloadable V2 regression checkpoint with four estimators, CUDA and seed 1729. This is a V2-weight result, not an evaluation of the newest checkpoint available in the package. TabFM 1.0.1 uses the pinned Google Research JAX regression checkpoint, four estimators, CPU float32 and seed 1729, retaining all training rows as context. Weight identifiers and hashes are recorded in S21 and the run manifests.

Chemprop 2.3.1 trains a four-target D-MPNN on full-salt SMILES with hidden dimension 300, message-passing depth three, mean aggregation, no batch normalisation, train-only target standardisation and batch size 32. Seeds 0, 1 and 2 each use 100 epochs and the final checkpoint, with no selection by outer-fold or OOD measurements. The graph model uses target activity data only, whereas guided representations also use the separate source supervision. The comparison does not equalise all pretraining data, model capacities or compute budgets.

Across the fixed models, 913 fits comprise 880 endpoint fits for the four tabular decoders and 33 four-target graph fits. Every reported RMSE, MAE and R² was independently recomputed from saved predictions. Exploratory decoder contrasts use 2,000 paired cluster-bootstrap draws at fixed source seed: cation or scaffold groups for CV, and both cation and four-family groupings for OOD. These intervals are conditional on the fitted decoders and do not include source-seed variability. They are separate from the primary 10,000-draw seed/scaffold intervals.

The direct extension uses three paired seeds (0–2), five fixed cation folds, five fixed scaffold folds and one final QAC→OOD fit per configuration. Frozen linear and compact MLP branches use archived 768-dimensional features. Each non-MLP target head is LayerNorm(768) followed by Linear(4). The MLP uses dimensions 768→256→128→4, GELU and dropout 0.1. LoRA (6) wraps query and value matrices in all 12 transformer blocks with rank 8, alpha 16 and dropout 0.1; the backbone stays frozen. Partial target fine-tuning updates upper eight blocks and the outer encoder LayerNorm; full fine-tuning updates the entire encoder. All methods fit train-only task mean/SD and minimise joint standardised MSE for 30 epochs with batch size 32, AdamW weight decay 0.01, OneCycle scheduling, gradient clipping at 1, head/LoRA learning rate 10−3 and backbone learning rate 3×10−5. Final checkpoints are scored; neither outer tests nor OOD select a checkpoint.

For source-initialised direct prediction, each target seed uses the matching source checkpoint. Head initialisation, minibatch order, stochastic schedules and target scaling are matched across source arms. The direct extension has 363 fits: 165 pretrained-initialised capacity fits and 198 source-initialised partial-target fits. Full trained weights are retained for final OOD fits; partial/full CV retains heads, buffers, encoder hashes, predictions and the deterministic replay recipe. Prediction files and ledgers are in server_finetune_causal_20261012.

Weight controls use five paired source seeds and six source arms. The 120 intact/rewound configurations plus one pure raw reference each receive 11 CatBoost fits, totalling 1,331. The decoder uses the primary species-plus-endpoint one-hot metadata, 300 trees, depth 5, learning rate 0.05, seed 1729 and two CPU threads. Weight rewinds restore 2 outer-normalisation tensors, 128 tensors from eight transformer blocks, or all 195 named encoder parameter tensors. Buffers and encoding layout are held fixed and verified by hashes. All reported scores are independently recomputed from endpoint predictions. New contrasts use 5,000 paired seed/group draws and are exploratory, unadjusted and conditional on the fitted models. The target and source seeds in direct fits are paired, not independent variance components. Three paired seeds provide a coarse estimate of stochastic variation. OOD-family inference is limited to four groups. This follow-up was chosen after earlier results; its protocol was recorded before its own predictions.

The complete decoder comparison formerly shown as main Table 5 is Table S23. The complete direct-target configuration table formerly shown as main Table 6 is Table S28. Figures S27–S29 retain the task-encoding, decoder-error and direct-adaptation plots relocated from the main article. Figure S26 compares the two prediction routes using the same first three source checkpoints.

S30. Completed v5-anchored hypothesis checks

This section is the primary computational follow-up for the v18 manuscript. Earlier SI sections preserve the original four author figures and analyses from prior revisions; their method and reference provenance remain distinct. Original v5 Tables 1–2 are now in the main article. The full quantitative multitarget checkpoint has not been recovered, and the available QAC-binned encoder is not substituted for it.

Table S34. Original v5 claims and the corresponding follow-up.

| Hypothesis | Original evidence | Follow-up | Result scope | Remaining limitation |
| --- | --- | --- | --- | --- |
| Human guidance is competitive | Main Tables 1–2 | Matched compact + partial backbone | Similar predictive values; procedure-dependent controls | Full-corpus checkpoint, H1–H7 |
| Task text improves prediction | May saved R²; Figure 3 | Categorical, one-hot, text, permuted, random | Encoding depends on split and decoder | Historical text cache missing |
| Guidance generalises to new QACs | Original Figure 5 | 105 QAC grouped CV +17 OOD | Archived human/text OOD RMSE 2.023 | One source checkpoint; archived source overlap |
| Human label content contributes | Geometry + post-hoc ablation | Six compact arms × five seeds | Compact real does not beat shuffled | Historical SMOTE protocol differs |
| Learned updates are necessary | CKA, SHAP, ablation | Weights reset and initial-state control | Compact reset intervals include zero | BatchNorm state retained in weight-only reset |
| Small adapters beat fine-tuning | Practical architecture rationale | Direct frozen, LoRA, full and guided routes | Full FT poor OOD under this budget | Different source/target objectives; no universal ranking |
| Modern models improve the pipeline | Prior graph/tabular work | 264 tabular fits on v5 features | No consistent improvement across regimes | PCA and model-specific budgets differ |

S30.1 Original-108 approximate reconstruction

The saved May R² outputs are distinct from the newly reconstructed metrics below. The reconstruction retains the archived expert checkpoint and source scaler, uses recovered CatBoost settings and the cached October four-task text vectors, and executes the task-row split. All nine configurations were run independently on both supplied servers; maximum prediction disagreement is below 1e−10. This does not reproduce the absent historical task vectors or full-corpus quantitative checkpoint.

Table S35. Reconstructed original-108 endpoint metrics; original notebook outputs are retained in S20 and the provenance archive.

| Representation / coding | Endpoint | n | RMSE | R² |
| --- | --- | --- | --- | --- |
| v5_human / categorical | Sa_MIC | 22 | 1.0741 | 0.6587 |
| v5_human / categorical | Sa_MBC | 22 | 1.6136 | 0.4823 |
| v5_human / categorical | Ec_MIC | 21 | 1.2349 | 0.6523 |
| v5_human / categorical | Ec_MBC | 22 | 1.2775 | 0.7352 |
| v5_human / separate | Sa_MIC | 22 | 1.4333 | -0.1198 |
| v5_human / separate | Sa_MBC | 22 | 1.9153 | -0.0464 |
| v5_human / separate | Ec_MIC | 22 | 1.4463 | 0.1095 |
| v5_human / separate | Ec_MBC | 22 | 1.4293 | 0.1517 |
| v5_human / text | Sa_MIC | 22 | 0.9585 | 0.7282 |
| v5_human / text | Sa_MBC | 22 | 1.7659 | 0.3799 |
| v5_human / text | Ec_MIC | 21 | 0.9927 | 0.7753 |
| v5_human / text | Ec_MBC | 22 | 1.3418 | 0.7079 |
| v5_qac_ablation / categorical | Sa_MIC | 22 | 1.1182 | 0.6301 |
| v5_qac_ablation / categorical | Sa_MBC | 22 | 1.6248 | 0.4751 |
| v5_qac_ablation / categorical | Ec_MIC | 21 | 1.2227 | 0.6591 |
| v5_qac_ablation / categorical | Ec_MBC | 22 | 1.2812 | 0.7337 |
| v5_qac_ablation / separate | Sa_MIC | 22 | 1.1520 | 0.2766 |
| v5_qac_ablation / separate | Sa_MBC | 22 | 1.6796 | 0.1953 |
| v5_qac_ablation / separate | Ec_MIC | 22 | 1.3159 | 0.2629 |
| v5_qac_ablation / separate | Ec_MBC | 22 | 1.5079 | 0.0558 |
| v5_qac_ablation / text | Sa_MIC | 22 | 1.1301 | 0.6222 |
| v5_qac_ablation / text | Sa_MBC | 22 | 1.7806 | 0.3695 |
| v5_qac_ablation / text | Ec_MIC | 21 | 1.0346 | 0.7560 |
| v5_qac_ablation / text | Ec_MBC | 22 | 1.3830 | 0.6897 |
| v5_raw / categorical | Sa_MIC | 22 | 1.0774 | 0.6566 |
| v5_raw / categorical | Sa_MBC | 22 | 1.6515 | 0.4576 |
| v5_raw / categorical | Ec_MIC | 21 | 1.2803 | 0.6262 |
| v5_raw / categorical | Ec_MBC | 22 | 1.2253 | 0.7564 |
| v5_raw / separate | Sa_MIC | 22 | 1.1892 | 0.2292 |
| v5_raw / separate | Sa_MBC | 22 | 1.6440 | 0.2290 |
| v5_raw / separate | Ec_MIC | 22 | 1.2235 | 0.3628 |
| v5_raw / separate | Ec_MBC | 22 | 1.2846 | 0.3148 |
| v5_raw / text | Sa_MIC | 22 | 1.0473 | 0.6755 |
| v5_raw / text | Sa_MBC | 22 | 1.7129 | 0.4166 |
| v5_raw / text | Ec_MIC | 21 | 1.0246 | 0.7606 |
| v5_raw / text | Ec_MBC | 22 | 1.1014 | 0.8032 |

S30.2 All archived and matched compact results

Table S36. Every compact-control and archived-representation configuration: seed-mean RMSE, without OOD-based selection. Source seed counts and endpoint-specific values are available in the machine-readable metrics and summary files.

| Arm / coding | Endpoint | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| binary_shuffled / categorical | Ec_MBC | 1.8929 | 2.0546 | 2.4307 |
| binary_shuffled / categorical | Ec_MIC | 1.7243 | 2.0121 | 2.2737 |
| binary_shuffled / categorical | Sa_MBC | 1.8650 | 2.1739 | 1.8703 |
| binary_shuffled / categorical | Sa_MIC | 1.7569 | 2.0008 | 1.7313 |
| binary_shuffled / categorical | pooled | 1.8113 | 2.0616 | 2.0939 |
| continuous_shuffled / categorical | Ec_MBC | 1.9903 | 2.1692 | 2.6393 |
| continuous_shuffled / categorical | Ec_MIC | 1.8686 | 2.1318 | 2.6086 |
| continuous_shuffled / categorical | Sa_MBC | 2.0054 | 2.3181 | 2.2961 |
| continuous_shuffled / categorical | Sa_MIC | 1.8718 | 2.1188 | 2.0641 |
| continuous_shuffled / categorical | pooled | 1.9353 | 2.1863 | 2.4185 |
| human / categorical | Ec_MBC | 1.9134 | 2.1098 | 2.5511 |
| human / categorical | Ec_MIC | 1.7590 | 2.0543 | 2.4426 |
| human / categorical | Sa_MBC | 1.9728 | 2.3132 | 2.1125 |
| human / categorical | Sa_MIC | 1.8371 | 2.1463 | 1.9183 |
| human / categorical | pooled | 1.8724 | 2.1583 | 2.2680 |
| human / onehot | Ec_MBC | 1.8723 | 2.1889 | 2.4709 |
| human / onehot | Ec_MIC | 1.7426 | 2.1361 | 2.4478 |
| human / onehot | Sa_MBC | 1.9657 | 2.1832 | 2.0925 |
| human / onehot | Sa_MIC | 1.7867 | 2.0972 | 1.9804 |
| human / onehot | pooled | 1.8438 | 2.1517 | 2.2548 |
| human / random_code | Ec_MBC | 1.8946 | 2.2442 | 2.5875 |
| human / random_code | Ec_MIC | 1.7849 | 2.1572 | 2.5778 |
| human / random_code | Sa_MBC | 1.9784 | 2.2789 | 2.1448 |
| human / random_code | Sa_MIC | 1.8167 | 2.1566 | 1.9487 |
| human / random_code | pooled | 1.8701 | 2.2099 | 2.3272 |
| human / text | Ec_MBC | 1.9276 | 2.1990 | 2.5143 |
| human / text | Ec_MIC | 1.7896 | 2.0904 | 2.4445 |
| human / text | Sa_MBC | 1.9889 | 2.2970 | 2.0912 |
| human / text | Sa_MIC | 1.8514 | 2.1801 | 1.9533 |
| human / text | pooled | 1.8912 | 2.1930 | 2.2600 |
| human / text_permuted | Ec_MBC | 1.9278 | 2.2135 | 2.5084 |
| human / text_permuted | Ec_MIC | 1.8149 | 2.1335 | 2.5010 |
| human / text_permuted | Sa_MBC | 1.9876 | 2.2479 | 2.1316 |
| human / text_permuted | Sa_MIC | 1.8320 | 2.1563 | 1.9966 |
| human / text_permuted | pooled | 1.8919 | 2.1883 | 2.2922 |
| human_shuffled / categorical | Ec_MBC | 1.9216 | 2.0319 | 2.4616 |
| human_shuffled / categorical | Ec_MIC | 1.7391 | 1.9818 | 2.3910 |
| human_shuffled / categorical | Sa_MBC | 1.8679 | 2.1617 | 2.0458 |
| human_shuffled / categorical | Sa_MIC | 1.7983 | 1.9847 | 1.7230 |
| human_shuffled / categorical | pooled | 1.8332 | 2.0414 | 2.1716 |
| human_weight_only / categorical | Ec_MBC | 1.9619 | 2.1121 | 2.6253 |
| human_weight_only / categorical | Ec_MIC | 1.7928 | 2.0586 | 2.6645 |
| human_weight_only / categorical | Sa_MBC | 1.9613 | 2.2329 | 2.2142 |
| human_weight_only / categorical | Sa_MIC | 1.8299 | 2.0203 | 1.9600 |
| human_weight_only / categorical | pooled | 1.8881 | 2.1076 | 2.3840 |
| initial / categorical | Ec_MBC | 1.9887 | 2.0858 | 2.4595 |
| initial / categorical | Ec_MIC | 1.8106 | 2.0384 | 2.5089 |
| initial / categorical | Sa_MBC | 1.9368 | 2.2038 | 2.2137 |
| initial / categorical | Sa_MIC | 1.8143 | 2.0018 | 2.0414 |
| initial / categorical | pooled | 1.8893 | 2.0840 | 2.3131 |
| matched_raw / categorical | Ec_MBC | 1.9534 | 2.1059 | 2.7320 |
| matched_raw / categorical | Ec_MIC | 1.8127 | 2.0625 | 2.9662 |
| matched_raw / categorical | Sa_MBC | 1.9114 | 2.2428 | 2.3310 |
| matched_raw / categorical | Sa_MIC | 1.7889 | 2.0459 | 1.8576 |
| matched_raw / categorical | pooled | 1.8678 | 2.1157 | 2.5038 |
| matched_raw / onehot | Ec_MBC | 1.9386 | 2.0716 | 2.1726 |
| matched_raw / onehot | Ec_MIC | 1.8198 | 2.0316 | 2.3036 |
| matched_raw / onehot | Sa_MBC | 1.9153 | 2.1245 | 2.2250 |
| matched_raw / onehot | Sa_MIC | 1.7915 | 2.0225 | 2.0318 |
| matched_raw / onehot | pooled | 1.8673 | 2.0629 | 2.1857 |
| matched_raw / text | Ec_MBC | 1.9571 | 2.1477 | 2.3348 |
| matched_raw / text | Ec_MIC | 1.8229 | 2.0978 | 2.5028 |
| matched_raw / text | Sa_MBC | 1.9015 | 2.1415 | 2.1117 |
| matched_raw / text | Sa_MIC | 1.7654 | 2.0210 | 1.9449 |
| matched_raw / text | pooled | 1.8631 | 2.1026 | 2.2321 |
| mic_binary / categorical | Ec_MBC | 1.8840 | 2.0558 | 2.5923 |
| mic_binary / categorical | Ec_MIC | 1.7417 | 2.0308 | 2.5124 |
| mic_binary / categorical | Sa_MBC | 1.9789 | 2.2656 | 2.0509 |
| mic_binary / categorical | Sa_MIC | 1.8469 | 2.0776 | 1.8802 |
| mic_binary / categorical | pooled | 1.8649 | 2.1096 | 2.2759 |
| mic_binary / text | Ec_MBC | 1.8764 | 2.0998 | 2.5049 |
| mic_binary / text | Ec_MIC | 1.7669 | 2.0205 | 2.4006 |
| mic_binary / text | Sa_MBC | 1.9773 | 2.2368 | 2.0789 |
| mic_binary / text | Sa_MIC | 1.8445 | 2.0808 | 1.8863 |
| mic_binary / text | pooled | 1.8681 | 2.1110 | 2.2340 |
| mic_continuous / categorical | Ec_MBC | 1.8763 | 2.1597 | 2.9780 |
| mic_continuous / categorical | Ec_MIC | 1.7554 | 2.1518 | 2.8449 |
| mic_continuous / categorical | Sa_MBC | 1.9814 | 2.3312 | 2.1047 |
| mic_continuous / categorical | Sa_MIC | 1.8125 | 2.0163 | 1.7707 |
| mic_continuous / categorical | pooled | 1.8584 | 2.1677 | 2.4738 |
| mic_continuous / text | Ec_MBC | 1.8488 | 2.1814 | 3.0417 |
| mic_continuous / text | Ec_MIC | 1.7629 | 2.1252 | 2.8322 |
| mic_continuous / text | Sa_MBC | 1.9282 | 2.2415 | 2.0960 |
| mic_continuous / text | Sa_MIC | 1.7851 | 2.0352 | 1.7856 |
| mic_continuous / text | pooled | 1.8326 | 2.1474 | 2.4948 |
| v5_human / categorical | Ec_MBC | 1.9442 | 2.0452 | 2.4605 |
| v5_human / categorical | Ec_MIC | 1.8169 | 2.0529 | 2.5352 |
| v5_human / categorical | Sa_MBC | 1.9894 | 2.2378 | 2.1728 |
| v5_human / categorical | Sa_MIC | 1.8177 | 2.0488 | 1.6537 |
| v5_human / categorical | pooled | 1.8936 | 2.0978 | 2.2289 |
| v5_human / onehot | Ec_MBC | 1.9911 | 2.0765 | 2.2699 |
| v5_human / onehot | Ec_MIC | 1.8605 | 2.0302 | 2.2740 |
| v5_human / onehot | Sa_MBC | 2.0148 | 2.1459 | 2.1984 |
| v5_human / onehot | Sa_MIC | 1.8025 | 2.0169 | 1.7163 |
| v5_human / onehot | pooled | 1.9193 | 2.0680 | 2.1251 |
| v5_human / separate | Ec_MBC | 2.0195 | 2.0593 | 2.1309 |
| v5_human / separate | Ec_MIC | 1.8889 | 2.0038 | 2.1412 |
| v5_human / separate | Sa_MBC | 2.0098 | 2.1809 | 2.2217 |
| v5_human / separate | Sa_MIC | 1.7933 | 2.0833 | 1.7883 |
| v5_human / separate | pooled | 1.9301 | 2.0828 | 2.0764 |
| v5_human / text | Ec_MBC | 1.9929 | 2.1198 | 2.1558 |
| v5_human / text | Ec_MIC | 1.8597 | 2.0250 | 2.0799 |
| v5_human / text | Sa_MBC | 1.9723 | 2.1909 | 2.0976 |
| v5_human / text | Sa_MIC | 1.7893 | 2.0601 | 1.7415 |
| v5_human / text | pooled | 1.9054 | 2.0999 | 2.0232 |
| v5_qac_ablation / categorical | Ec_MBC | 1.9429 | 1.9814 | 2.7519 |
| v5_qac_ablation / categorical | Ec_MIC | 1.7947 | 1.9717 | 2.8495 |
| v5_qac_ablation / categorical | Sa_MBC | 1.9241 | 2.1364 | 2.3717 |
| v5_qac_ablation / categorical | Sa_MIC | 1.7288 | 1.8976 | 1.7433 |
| v5_qac_ablation / categorical | pooled | 1.8498 | 1.9987 | 2.4631 |
| v5_qac_ablation / onehot | Ec_MBC | 2.0030 | 2.0342 | 2.5741 |
| v5_qac_ablation / onehot | Ec_MIC | 1.8471 | 1.9710 | 2.4897 |
| v5_qac_ablation / onehot | Sa_MBC | 1.9317 | 2.1273 | 2.3480 |
| v5_qac_ablation / onehot | Sa_MIC | 1.7222 | 1.9322 | 1.7026 |
| v5_qac_ablation / onehot | pooled | 1.8789 | 2.0175 | 2.2999 |
| v5_qac_ablation / separate | Ec_MBC | 2.0095 | 2.0762 | 2.4927 |
| v5_qac_ablation / separate | Ec_MIC | 1.7916 | 1.9959 | 2.6511 |
| v5_qac_ablation / separate | Sa_MBC | 1.9805 | 2.1216 | 2.3097 |
| v5_qac_ablation / separate | Sa_MIC | 1.7341 | 1.8851 | 1.6720 |
| v5_qac_ablation / separate | pooled | 1.8826 | 2.0217 | 2.3087 |
| v5_qac_ablation / text | Ec_MBC | 1.8880 | 2.0629 | 2.6845 |
| v5_qac_ablation / text | Ec_MIC | 1.7270 | 1.9762 | 2.6384 |
| v5_qac_ablation / text | Sa_MBC | 1.8869 | 2.1070 | 2.4193 |
| v5_qac_ablation / text | Sa_MIC | 1.6417 | 1.9006 | 1.8050 |
| v5_qac_ablation / text | pooled | 1.7890 | 2.0133 | 2.4081 |
| v5_raw / categorical | Ec_MBC | 1.9728 | 2.1056 | 2.9011 |
| v5_raw / categorical | Ec_MIC | 1.8227 | 2.0783 | 2.8696 |
| v5_raw / categorical | Sa_MBC | 1.9480 | 2.1998 | 2.0848 |
| v5_raw / categorical | Sa_MIC | 1.8159 | 1.9856 | 1.7175 |
| v5_raw / categorical | pooled | 1.8912 | 2.0937 | 2.4394 |
| v5_raw / onehot | Ec_MBC | 1.9805 | 2.1181 | 2.5716 |
| v5_raw / onehot | Ec_MIC | 1.8486 | 2.0396 | 2.5801 |
| v5_raw / onehot | Sa_MBC | 1.9467 | 2.1534 | 2.0615 |
| v5_raw / onehot | Sa_MIC | 1.7660 | 2.0145 | 1.5467 |
| v5_raw / onehot | pooled | 1.8873 | 2.0821 | 2.2257 |
| v5_raw / separate | Ec_MBC | 2.0275 | 2.1363 | 2.4428 |
| v5_raw / separate | Ec_MIC | 1.8478 | 1.9962 | 2.5490 |
| v5_raw / separate | Sa_MBC | 1.9906 | 2.2075 | 2.0901 |
| v5_raw / separate | Sa_MIC | 1.7869 | 1.9962 | 1.6519 |
| v5_raw / separate | pooled | 1.9158 | 2.0861 | 2.2078 |
| v5_raw / text | Ec_MBC | 1.9842 | 2.1230 | 2.5903 |
| v5_raw / text | Ec_MIC | 1.8242 | 2.0443 | 2.5779 |
| v5_raw / text | Sa_MBC | 1.9580 | 2.2034 | 2.0491 |
| v5_raw / text | Sa_MIC | 1.8037 | 2.0293 | 1.6454 |
| v5_raw / text | pooled | 1.8942 | 2.1011 | 2.2452 |

S30.3 Paired source-seed and clustered uncertainty

Table S37. All paired compact-control RMSE contrasts. Negative differences favour the first configuration; pointwise 95% intervals are not simultaneous familywise evidence. Cation and scaffold resampling are both retained; there are 17 OOD cations but only four OOD scaffolds.

| Comparison | Regime / cluster | Seeds / clusters | ΔRMSE | 95% interval |
| --- | --- | --- | --- | --- |
| human minus human_shuffled | cation / cation | 5 / 103 | +0.0393 | [-0.0574, +0.1408] |
| human minus human_shuffled | full-QAC105 / cation | 5 / 17 | +0.0963 | [-0.1085, +0.3356] |
| human minus human_shuffled | scaffold / cation | 5 / 103 | +0.1169 | [+0.0041, +0.2368] |
| human minus human_shuffled | cation / scaffold | 5 / 29 | +0.0393 | [-0.0744, +0.1589] |
| human minus human_shuffled | full-QAC105 / scaffold | 5 / 4 | +0.0963 | [-0.1433, +0.2832] |
| human minus human_shuffled | scaffold / scaffold | 5 / 29 | +0.1169 | [-0.0121, +0.2533] |
| human minus mic_continuous | cation / cation | 5 / 103 | +0.0140 | [-0.0693, +0.0990] |
| human minus mic_continuous | full-QAC105 / cation | 5 / 17 | -0.2058 | [-0.4587, +0.0023] |
| human minus mic_continuous | scaffold / cation | 5 / 103 | -0.0094 | [-0.0975, +0.0806] |
| human minus mic_continuous | cation / scaffold | 5 / 29 | +0.0140 | [-0.0575, +0.0911] |
| human minus mic_continuous | full-QAC105 / scaffold | 5 / 4 | -0.2058 | [-0.5248, +0.0193] |
| human minus mic_continuous | scaffold / scaffold | 5 / 29 | -0.0094 | [-0.1023, +0.1014] |
| human minus mic_binary | cation / cation | 5 / 103 | +0.0075 | [-0.0924, +0.1047] |
| human minus mic_binary | full-QAC105 / cation | 5 / 17 | -0.0079 | [-0.1319, +0.1320] |
| human minus mic_binary | scaffold / cation | 5 / 103 | +0.0487 | [-0.0390, +0.1481] |
| human minus mic_binary | cation / scaffold | 5 / 29 | +0.0075 | [-0.0975, +0.1080] |
| human minus mic_binary | full-QAC105 / scaffold | 5 / 4 | -0.0079 | [-0.1270, +0.1114] |
| human minus mic_binary | scaffold / scaffold | 5 / 29 | +0.0487 | [-0.0353, +0.1668] |
| mic_binary minus binary_shuffled | cation / cation | 5 / 103 | +0.0536 | [-0.0444, +0.1506] |
| mic_binary minus binary_shuffled | full-QAC105 / cation | 5 / 17 | +0.1820 | [+0.0328, +0.3671] |
| mic_binary minus binary_shuffled | scaffold / cation | 5 / 103 | +0.0480 | [-0.0316, +0.1318] |
| mic_binary minus binary_shuffled | cation / scaffold | 5 / 29 | +0.0536 | [-0.0421, +0.1473] |
| mic_binary minus binary_shuffled | full-QAC105 / scaffold | 5 / 4 | +0.1820 | [+0.0602, +0.3416] |
| mic_binary minus binary_shuffled | scaffold / scaffold | 5 / 29 | +0.0480 | [-0.0484, +0.1449] |
| mic_continuous minus continuous_shuffled | cation / cation | 5 / 103 | -0.0769 | [-0.1812, +0.0302] |
| mic_continuous minus continuous_shuffled | full-QAC105 / cation | 5 / 17 | +0.0553 | [-0.1930, +0.2999] |
| mic_continuous minus continuous_shuffled | scaffold / cation | 5 / 103 | -0.0186 | [-0.1194, +0.0817] |
| mic_continuous minus continuous_shuffled | cation / scaffold | 5 / 29 | -0.0769 | [-0.2034, +0.0482] |
| mic_continuous minus continuous_shuffled | full-QAC105 / scaffold | 5 / 4 | +0.0553 | [-0.3386, +0.3661] |
| mic_continuous minus continuous_shuffled | scaffold / scaffold | 5 / 29 | -0.0186 | [-0.1495, +0.0998] |
| human_weight_only minus human | cation / cation | 5 / 103 | +0.0156 | [-0.0763, +0.0981] |
| human_weight_only minus human | full-QAC105 / cation | 5 / 17 | +0.1160 | [-0.0588, +0.3070] |
| human_weight_only minus human | scaffold / cation | 5 / 103 | -0.0507 | [-0.1394, +0.0404] |
| human_weight_only minus human | cation / scaffold | 5 / 29 | +0.0156 | [-0.0906, +0.1140] |
| human_weight_only minus human | full-QAC105 / scaffold | 5 / 4 | +0.1160 | [-0.0562, +0.3355] |
| human_weight_only minus human | scaffold / scaffold | 5 / 29 | -0.0507 | [-0.1527, +0.0593] |
| initial minus human | cation / cation | 5 / 103 | +0.0168 | [-0.0711, +0.0995] |
| initial minus human | full-QAC105 / cation | 5 / 17 | +0.0451 | [-0.1480, +0.2214] |
| initial minus human | scaffold / cation | 5 / 103 | -0.0742 | [-0.1807, +0.0259] |
| initial minus human | cation / scaffold | 5 / 29 | +0.0168 | [-0.0904, +0.1088] |
| initial minus human | full-QAC105 / scaffold | 5 / 4 | +0.0451 | [-0.1285, +0.2741] |
| initial minus human | scaffold / scaffold | 5 / 29 | -0.0742 | [-0.1945, +0.0454] |
| human minus matched_raw | cation / cation | 5 / 103 | +0.0046 | [-0.0787, +0.0950] |
| human minus matched_raw | full-QAC105 / cation | 5 / 17 | -0.2359 | [-0.4442, -0.0307] |
| human minus matched_raw | scaffold / cation | 5 / 103 | +0.0426 | [-0.0549, +0.1409] |
| human minus matched_raw | cation / scaffold | 5 / 29 | +0.0046 | [-0.1168, +0.1250] |
| human minus matched_raw | full-QAC105 / scaffold | 5 / 4 | -0.2359 | [-0.5236, -0.0158] |
| human minus matched_raw | scaffold / scaffold | 5 / 29 | +0.0426 | [-0.0761, +0.1599] |


Figure S30. Compact-encoder performance contrasts with paired source-seed and scaffold-clustered 95% intervals. The first three rows compare supervision; the last two restore parameters only or the complete initial state. Zero is the reference. All five source seeds are included; OOD intervals have only four scaffold clusters.

S30.4 Modern decoders on the archived v5 features

Table S38. All modern-decoder per-endpoint results. Every method fits four separate endpoint predictors. PCA32 is fitted to target-training vectors only for the modern models. These runs use one archived source checkpoint, not a distribution of source-training seeds.

| Model / representation | Endpoint | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| autogluon / v5_human | Sa_MIC | 1.9724 | 2.1659 | 1.6615 |
| autogluon / v5_human | Sa_MBC | 2.1855 | 2.2042 | 2.4718 |
| autogluon / v5_human | Ec_MIC | 1.9763 | 2.0850 | 2.0745 |
| autogluon / v5_human | Ec_MBC | 2.1061 | 2.1863 | 2.0329 |
| autogluon / v5_human | pooled | 2.0621 | 2.1608 | 2.0808 |
| autogluon / v5_raw | Sa_MIC | 1.8935 | 2.0574 | 1.8706 |
| autogluon / v5_raw | Sa_MBC | 2.1421 | 2.2678 | 2.2401 |
| autogluon / v5_raw | Ec_MIC | 1.8637 | 2.0927 | 2.3404 |
| autogluon / v5_raw | Ec_MBC | 2.0363 | 2.0983 | 2.1735 |
| autogluon / v5_raw | pooled | 1.9871 | 2.1306 | 2.1631 |
| tabfm / v5_human | Sa_MIC | 1.9027 | 2.1068 | 1.8181 |
| tabfm / v5_human | Sa_MBC | 2.0946 | 2.1954 | 2.1583 |
| tabfm / v5_human | Ec_MIC | 1.9629 | 2.0253 | 2.4253 |
| tabfm / v5_human | Ec_MBC | 2.1032 | 2.0834 | 2.2691 |
| tabfm / v5_human | pooled | 2.0177 | 2.1036 | 2.1778 |
| tabfm / v5_raw | Sa_MIC | 1.7758 | 2.0668 | 1.6176 |
| tabfm / v5_raw | Sa_MBC | 1.9680 | 2.1751 | 2.1125 |
| tabfm / v5_raw | Ec_MIC | 1.8643 | 2.0036 | 2.3931 |
| tabfm / v5_raw | Ec_MBC | 1.9943 | 2.0705 | 2.2761 |
| tabfm / v5_raw | pooled | 1.9026 | 2.0799 | 2.1181 |
| tabpfn / v5_human | Sa_MIC | 1.9610 | 2.0908 | 1.6764 |
| tabpfn / v5_human | Sa_MBC | 2.0105 | 2.2591 | 2.1569 |
| tabpfn / v5_human | Ec_MIC | 1.9641 | 2.0339 | 2.2627 |
| tabpfn / v5_human | Ec_MBC | 2.1329 | 2.1393 | 2.5022 |
| tabpfn / v5_human | pooled | 2.0183 | 2.1324 | 2.1651 |
| tabpfn / v5_raw | Sa_MIC | 1.9081 | 2.0745 | 1.6874 |
| tabpfn / v5_raw | Sa_MBC | 1.9618 | 2.0914 | 2.1162 |
| tabpfn / v5_raw | Ec_MIC | 1.9431 | 2.0288 | 2.2208 |
| tabpfn / v5_raw | Ec_MBC | 2.0570 | 2.0923 | 2.1703 |
| tabpfn / v5_raw | pooled | 1.9683 | 2.0719 | 2.0579 |

S30.5 Execution, checkpoint and feature provenance

The new compact experiment completed 30 source fits and 920 CatBoost decoder fits; TabPFN, TabFM and AutoGluon each completed 88 endpoint fits. The independent server performed 18 additional CatBoost fits for the nine original-108 configurations. Server1 used Python 3.11.16, torch 2.6.0+cu124, numpy 2.2.6, pandas 2.2.3, scikit-learn 1.7.2 and CatBoost 1.2.10. All OpenRouter task embedding and Kimi/Claude review calls were executed on the local Mac. Raw predictions, completed job manifests and timestamps are preserved in the read-only snapshot archive.

Task-code controls include a fixed permutation of the four cached vectors and a seeded random vector set matched to their norms. These controls change the task-code association while keeping the numerical target records fixed. They can challenge a semantic-meaning interpretation; with only four tasks and one compact seed for the extra substitutions, they cannot establish transfer to unseen descriptions.

Table S39. Task-code controls with the same human compact checkpoint, seed 0. Every row uses the same encoder and targets; pooled exact-endpoint RMSE is shown. Text codes are the cached October vectors, not a recovered historical cache.

| Task coding | Source seed | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| categorical | 0 | 1.8592 | 2.2147 | 2.2978 |
| onehot | 0 | 1.8438 | 2.1517 | 2.2548 |
| text | 0 | 1.8876 | 2.2079 | 2.3141 |
| text_permuted | 0 | 1.8919 | 2.1883 | 2.2922 |
| random_code | 0 | 1.8701 | 2.2099 | 2.3272 |

The censored IT505 E. coli MBC endpoint is retained for every relevant prediction. Its minimum absolute error is max(log2(500)−prediction,0), and it is excluded from exact-endpoint RMSE/R². The machine-readable censored_predictions.csv preserves all bound predictions. No figure silently caps error tails, and no OOD row is discarded based on residual size.

S31. References for archived earlier computational sections

The bibliographic items below preserve the numbered reference list used by the earlier v17 computational sections, including S28. They are separate from the original v5 bibliography retained in S17 and from the v18 main-paper references; compound numbers in chemistry are not citation remappings.

1. World Health Organization. Antimicrobial resistance. Fact sheet, 16 July 2026. https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance (accessed 2026-10-13).

2. Ilin, E. A.; Frolov, N. A.; Seferyan, M. A.; Valeev, A. B.; Vinokurov, A. D.; Detusheva, E. V.; Son, E.; Medvedev, M. G.; Vereshchagin, A. N., Tackling the challenge of ML-assisted antibacterial activity prediction: One step closer to controlled quaternary ammonium compounds design via neural networks model. Bioorganic Chemistry 2025, 167, 109175.

3. Choung, O.-H.; Vianello, R.; Segler, M.; Stiefl, N.; Jiménez-Luna, J. Extracting medicinal chemistry intuition via preference machine learning. Nature Communications 2023, 14, 6651. https://doi.org/10.1038/s41467-023-42242-1.

4. Ross, J.; Belgodere, B.; Chenthamarakshan, V.; Padhi, I.; Mroueh, Y.; Das, P. Large-scale chemical language representations capture molecular structure and properties. Nature Machine Intelligence 2022, 4, 1256–1264. https://doi.org/10.1038/s42256-022-00580-7.

5. Cai, F.; Zacour, K.; Zhu, T.; et al. ChemFM as a scaling law guided foundation model pre-trained on informative chemicals. Communications Chemistry 2026, 9, 3 (published online 18 December 2025). https://doi.org/10.1038/s42004-025-01793-8.

6. Hu, E. J.; Shen, Y.; Wallis, P.; Allen-Zhu, Z.; Li, Y.; Wang, S.; Wang, L.; Chen, W. LoRA: Low-Rank Adaptation of Large Language Models. arXiv 2021, arXiv:2106.09685. https://doi.org/10.48550/arXiv.2106.09685.

7. Heid, E.; et al. Chemprop: A Machine Learning Package for Chemical Property Prediction. J. Chem. Inf. Model. 2024, 64 (1), 9–17. https://doi.org/10.1021/acs.jcim.3c01250.

8. Hollmann, N.; Müller, S.; Purucker, L.; Krishnakumar, A.; Körfer, M.; Hoo, S. B.; Schirrmeister, R. T.; Hutter, F. Accurate predictions on small data with a tabular foundation model. Nature 2025, 637, 319–326. https://doi.org/10.1038/s41586-024-08328-6.

9. Google Research. TabFM: Tabular Foundation Models. https://github.com/google-research/tabfm (accessed 2026-10-12); code revision fbb665569425fd2f490c6576b3af967876fe11ff904; JAX regression checkpoint google/tabfm-1.0.0-jax, revision d5e74033fcf257699fab013e2cdd7edf424ff904.

10. Erickson, N.; Mueller, J.; Shirkov, A.; Zhang, H.; Larroy, P.; Li, M.; Smola, A. AutoGluon-Tabular: Robust and Accurate AutoML for Structured Data. arXiv 2020, arXiv:2003.06505. https://doi.org/10.48550/arXiv.2003.06505.

11. Schölkopf, B.; Locatello, F.; Bauer, S.; Ke, N. R.; Kalchbrenner, N.; Goyal, A.; Bengio, Y. Towards Causal Representation Learning. 2021. https://arxiv.org/abs/2102.11107.

12. Ghaemi, S.; Consylman, A.; Pan, B.; Wu, A.; Petersen, A.; Chang, G.; McDonough, D.; Forman, M.; Bezold, E. L.; Wuest, W. M.; Shehu, A.; Zhao, L.; Minbiole, K. P. C., Topology-Aware Generation and Activity-Based Filtering: A Computational-Experimental Framework for Data-Scarce Quaternary Ammonium Compound Discovery. Journal of Chemical Information and Modeling 2026, 66, 3117-3128.

13. Singh, R.; Barsainyan, A. A.; Irfan, R.; et al. ChemBERTa-3: an open source training framework for chemical foundation models. Digital Discovery 2026, 5, 662–685. https://doi.org/10.1039/D5DD00348B.

14. Toukach, P. V.; Arakelyan, L. A.; Egorova, K. S. ILToxDB: A Database on Cytotoxicity of Ionic Liquids. Environmental Science & Technology Letters 2025, 12, 1631–1635. https://doi.org/10.1021/acs.estlett.5c00860.

S32. CV, seed variability and continuity with the author workflow

Original reported single-holdout results remain unchanged. The new row-CV experiment uses the saved human encoder, preserving its historical source SMOTE state, and the original 108 worksheet records representing 105 unique full salts. It does not retrain the encoder or use any OOD compound. The missing historical text cache makes the text variant an approximate reconstruction. All six raw/human coding combinations and 30 fits are retained; no configuration was selected by OOD performance.

Table S40. New five-fold reconstruction of the author’s row-wise multitask evaluation. Mean ± SD of five fold scores, ddof=0; these are not recovered uncertainty for the historical Tables 1–2 holdout values.

| Representation / coding | Endpoint | Folds | RMSE mean ± SD | R² mean ± SD |
| --- | --- | --- | --- | --- |
| v5_human / categorical_org_met | Ec_MBC | 5 | 1.1622 ± 0.1107 | 0.6573 ± 0.0718 |
| v5_human / categorical_org_met | Ec_MIC | 5 | 0.9744 ± 0.1351 | 0.7238 ± 0.0624 |
| v5_human / categorical_org_met | Sa_MBC | 5 | 1.4703 ± 0.3031 | 0.4076 ± 0.2529 |
| v5_human / categorical_org_met | Sa_MIC | 5 | 1.3364 ± 0.3599 | 0.4810 ± 0.2240 |
| v5_human / categorical_org_met | pooled | 5 | 1.2786 ± 0.1695 | 0.6625 ± 0.0368 |
| v5_human / categorical_task_id | Ec_MBC | 5 | 1.3152 ± 0.1902 | 0.5210 ± 0.2740 |
| v5_human / categorical_task_id | Ec_MIC | 5 | 1.0657 ± 0.3161 | 0.6540 ± 0.1856 |
| v5_human / categorical_task_id | Sa_MBC | 5 | 1.5240 ± 0.3385 | 0.3126 ± 0.3901 |
| v5_human / categorical_task_id | Sa_MIC | 5 | 1.3802 ± 0.2650 | 0.4548 ± 0.1390 |
| v5_human / categorical_task_id | pooled | 5 | 1.3450 ± 0.2158 | 0.6238 ± 0.0752 |
| v5_human / text | Ec_MBC | 5 | 1.1977 ± 0.1637 | 0.6434 ± 0.0508 |
| v5_human / text | Ec_MIC | 5 | 0.9827 ± 0.1811 | 0.7174 ± 0.0807 |
| v5_human / text | Sa_MBC | 5 | 1.4159 ± 0.2527 | 0.4493 ± 0.2132 |
| v5_human / text | Sa_MIC | 5 | 1.3019 ± 0.1867 | 0.5120 ± 0.1004 |
| v5_human / text | pooled | 5 | 1.2489 ± 0.1450 | 0.6765 ± 0.0376 |
| v5_raw / categorical_org_met | Ec_MBC | 5 | 1.1122 ± 0.1215 | 0.6856 ± 0.0722 |
| v5_raw / categorical_org_met | Ec_MIC | 5 | 0.8950 ± 0.1332 | 0.7645 ± 0.0655 |
| v5_raw / categorical_org_met | Sa_MBC | 5 | 1.4123 ± 0.2906 | 0.4540 ± 0.2356 |
| v5_raw / categorical_org_met | Sa_MIC | 5 | 1.3124 ± 0.4014 | 0.4972 ± 0.2409 |
| v5_raw / categorical_org_met | pooled | 5 | 1.2312 ± 0.1800 | 0.6863 ± 0.0473 |
| v5_raw / categorical_task_id | Ec_MBC | 5 | 1.3303 ± 0.1976 | 0.5027 ± 0.3062 |
| v5_raw / categorical_task_id | Ec_MIC | 5 | 1.0497 ± 0.3368 | 0.6644 ± 0.1863 |
| v5_raw / categorical_task_id | Sa_MBC | 5 | 1.4934 ± 0.3429 | 0.3277 ± 0.4000 |
| v5_raw / categorical_task_id | Sa_MIC | 5 | 1.3869 ± 0.3139 | 0.4499 ± 0.1719 |
| v5_raw / categorical_task_id | pooled | 5 | 1.3455 ± 0.2286 | 0.6220 ± 0.0872 |
| v5_raw / text | Ec_MBC | 5 | 1.1797 ± 0.1264 | 0.6438 ± 0.0942 |
| v5_raw / text | Ec_MIC | 5 | 0.9077 ± 0.1538 | 0.7589 ± 0.0650 |
| v5_raw / text | Sa_MBC | 5 | 1.3434 ± 0.2063 | 0.4939 ± 0.2149 |
| v5_raw / text | Sa_MIC | 5 | 1.3739 ± 0.2021 | 0.4626 ± 0.0876 |
| v5_raw / text | pooled | 5 | 1.2286 ± 0.1389 | 0.6848 ± 0.0475 |

Row-level KFold does not enforce molecule separation: different endpoint records of the same salt can occur in training and validation. The per-fold overlap counts are preserved in each configuration manifest. This estimates the declared row-level problem, not strict transfer to a new molecule. The cation/scaffold tests and OOD-17 remain distinct.

Table S41. Mean ± sample SD over complete compact source-seed runs, ddof=1. At least two source runs are required; single-seed task-code substitutions are not assigned an SD.

| Arm / coding | Regime / endpoint | Seeds | RMSE mean ± SD | R² mean ± SD |
| --- | --- | --- | --- | --- |
| binary_shuffled / categorical | full-QAC105 / Ec_MBC | 5 | 2.4307 ± 0.1901 | -0.5178 ± 0.2440 |
| binary_shuffled / categorical | full-QAC105 / Ec_MIC | 5 | 2.2737 ± 0.2194 | -0.5733 ± 0.3139 |
| binary_shuffled / categorical | full-QAC105 / Sa_MBC | 5 | 1.8703 ± 0.0526 | 0.2192 ± 0.0437 |
| binary_shuffled / categorical | full-QAC105 / Sa_MIC | 5 | 1.7313 ± 0.1133 | 0.0167 ± 0.1282 |
| binary_shuffled / categorical | full-QAC105 / pooled | 5 | 2.0939 ± 0.0877 | — |
| binary_shuffled / categorical | cation / Ec_MBC | 5 | 1.8929 ± 0.0497 | 0.1787 ± 0.0433 |
| binary_shuffled / categorical | cation / Ec_MIC | 5 | 1.7243 ± 0.0439 | 0.2338 ± 0.0394 |
| binary_shuffled / categorical | cation / Sa_MBC | 5 | 1.8650 ± 0.0484 | 0.0972 ± 0.0467 |
| binary_shuffled / categorical | cation / Sa_MIC | 5 | 1.7569 ± 0.0434 | 0.1957 ± 0.0398 |
| binary_shuffled / categorical | cation / pooled | 5 | 1.8113 ± 0.0369 | — |
| binary_shuffled / categorical | scaffold / Ec_MBC | 5 | 2.0546 ± 0.0354 | 0.0327 ± 0.0334 |
| binary_shuffled / categorical | scaffold / Ec_MIC | 5 | 2.0121 ± 0.0236 | -0.0429 ± 0.0245 |
| binary_shuffled / categorical | scaffold / Sa_MBC | 5 | 2.1739 ± 0.0297 | -0.2261 ± 0.0335 |
| binary_shuffled / categorical | scaffold / Sa_MIC | 5 | 2.0008 ± 0.0218 | -0.0426 ± 0.0227 |
| binary_shuffled / categorical | scaffold / pooled | 5 | 2.0616 ± 0.0168 | — |
| continuous_shuffled / categorical | full-QAC105 / Ec_MBC | 5 | 2.6393 ± 0.2234 | -0.7909 ± 0.2988 |
| continuous_shuffled / categorical | full-QAC105 / Ec_MIC | 5 | 2.6086 ± 0.1932 | -1.0645 ± 0.3121 |
| continuous_shuffled / categorical | full-QAC105 / Sa_MBC | 5 | 2.2961 ± 0.1962 | -0.1829 ± 0.2024 |
| continuous_shuffled / categorical | full-QAC105 / Sa_MIC | 5 | 2.0641 ± 0.4075 | -0.4363 ± 0.6186 |
| continuous_shuffled / categorical | full-QAC105 / pooled | 5 | 2.4185 ± 0.1503 | — |
| continuous_shuffled / categorical | cation / Ec_MBC | 5 | 1.9903 ± 0.0722 | 0.0915 ± 0.0645 |
| continuous_shuffled / categorical | cation / Ec_MIC | 5 | 1.8686 ± 0.0356 | 0.1004 ± 0.0339 |
| continuous_shuffled / categorical | cation / Sa_MBC | 5 | 2.0054 ± 0.0802 | -0.0446 ± 0.0831 |
| continuous_shuffled / categorical | cation / Sa_MIC | 5 | 1.8718 ± 0.0408 | 0.0873 ± 0.0399 |
| continuous_shuffled / categorical | cation / pooled | 5 | 1.9353 ± 0.0505 | — |
| continuous_shuffled / categorical | scaffold / Ec_MBC | 5 | 2.1692 ± 0.0831 | -0.0792 ± 0.0823 |
| continuous_shuffled / categorical | scaffold / Ec_MIC | 5 | 2.1318 ± 0.0862 | -0.1721 ± 0.0952 |
| continuous_shuffled / categorical | scaffold / Sa_MBC | 5 | 2.3181 ± 0.0593 | -0.3947 ± 0.0711 |
| continuous_shuffled / categorical | scaffold / Sa_MIC | 5 | 2.1188 ± 0.0536 | -0.1697 ± 0.0592 |
| continuous_shuffled / categorical | scaffold / pooled | 5 | 2.1863 ± 0.0558 | — |
| human / categorical | full-QAC105 / Ec_MBC | 5 | 2.5511 ± 0.1522 | -0.6684 ± 0.1992 |
| human / categorical | full-QAC105 / Ec_MIC | 5 | 2.4426 ± 0.1988 | -0.8118 ± 0.2883 |
| human / categorical | full-QAC105 / Sa_MBC | 5 | 2.1125 ± 0.0554 | 0.0040 ± 0.0528 |
| human / categorical | full-QAC105 / Sa_MIC | 5 | 1.9183 ± 0.0812 | -0.2048 ± 0.1042 |
| human / categorical | full-QAC105 / pooled | 5 | 2.2680 ± 0.0774 | — |
| human / categorical | cation / Ec_MBC | 5 | 1.9134 ± 0.0361 | 0.1610 ± 0.0318 |
| human / categorical | cation / Ec_MIC | 5 | 1.7590 ± 0.0228 | 0.2030 ± 0.0207 |
| human / categorical | cation / Sa_MBC | 5 | 1.9728 ± 0.0475 | -0.0101 ± 0.0485 |
| human / categorical | cation / Sa_MIC | 5 | 1.8371 ± 0.0503 | 0.1205 ± 0.0482 |
| human / categorical | cation / pooled | 5 | 1.8724 ± 0.0339 | — |
| human / categorical | scaffold / Ec_MBC | 5 | 2.1098 ± 0.0646 | -0.0205 ± 0.0630 |
| human / categorical | scaffold / Ec_MIC | 5 | 2.0543 ± 0.0646 | -0.0878 ± 0.0693 |
| human / categorical | scaffold / Sa_MBC | 5 | 2.3132 ± 0.0417 | -0.3884 ± 0.0501 |
| human / categorical | scaffold / Sa_MIC | 5 | 2.1463 ± 0.0724 | -0.2007 ± 0.0808 |
| human / categorical | scaffold / pooled | 5 | 2.1583 ± 0.0496 | — |
| human / text | full-QAC105 / Ec_MBC | 5 | 2.5143 ± 0.1143 | -0.6186 ± 0.1442 |
| human / text | full-QAC105 / Ec_MIC | 5 | 2.4445 ± 0.1575 | -0.8111 ± 0.2246 |
| human / text | full-QAC105 / Sa_MBC | 5 | 2.0912 ± 0.0482 | 0.0241 ± 0.0453 |
| human / text | full-QAC105 / Sa_MIC | 5 | 1.9533 ± 0.0700 | -0.2486 ± 0.0907 |
| human / text | full-QAC105 / pooled | 5 | 2.2600 ± 0.0768 | — |
| human / text | cation / Ec_MBC | 5 | 1.9276 ± 0.0537 | 0.1482 ± 0.0470 |
| human / text | cation / Ec_MIC | 5 | 1.7896 ± 0.0474 | 0.1746 ± 0.0436 |
| human / text | cation / Sa_MBC | 5 | 1.9889 ± 0.0655 | -0.0270 ± 0.0671 |
| human / text | cation / Sa_MIC | 5 | 1.8514 ± 0.1042 | 0.1051 ± 0.0985 |
| human / text | cation / pooled | 5 | 1.8912 ± 0.0579 | — |
| human / text | scaffold / Ec_MBC | 5 | 2.1990 ± 0.0389 | -0.1081 ± 0.0392 |
| human / text | scaffold / Ec_MIC | 5 | 2.0904 ± 0.0495 | -0.1259 ± 0.0533 |
| human / text | scaffold / Sa_MBC | 5 | 2.2970 ± 0.0641 | -0.3695 ± 0.0770 |
| human / text | scaffold / Sa_MIC | 5 | 2.1801 ± 0.0360 | -0.2380 ± 0.0410 |
| human / text | scaffold / pooled | 5 | 2.1930 ± 0.0395 | — |
| human_shuffled / categorical | full-QAC105 / Ec_MBC | 5 | 2.4616 ± 0.1228 | -0.5521 ± 0.1543 |
| human_shuffled / categorical | full-QAC105 / Ec_MIC | 5 | 2.3910 ± 0.1937 | -0.7360 ± 0.2769 |
| human_shuffled / categorical | full-QAC105 / Sa_MBC | 5 | 2.0458 ± 0.1086 | 0.0643 ± 0.0994 |
| human_shuffled / categorical | full-QAC105 / Sa_MIC | 5 | 1.7230 ± 0.0283 | 0.0292 ± 0.0319 |
| human_shuffled / categorical | full-QAC105 / pooled | 5 | 2.1716 ± 0.1120 | — |
| human_shuffled / categorical | cation / Ec_MBC | 5 | 1.9216 ± 0.0280 | 0.1540 ± 0.0246 |
| human_shuffled / categorical | cation / Ec_MIC | 5 | 1.7391 ± 0.0610 | 0.2202 ± 0.0540 |
| human_shuffled / categorical | cation / Sa_MBC | 5 | 1.8679 ± 0.0649 | 0.0940 ± 0.0619 |
| human_shuffled / categorical | cation / Sa_MIC | 5 | 1.7983 ± 0.0568 | 0.1571 ± 0.0528 |
| human_shuffled / categorical | cation / pooled | 5 | 1.8332 ± 0.0495 | — |
| human_shuffled / categorical | scaffold / Ec_MBC | 5 | 2.0319 ± 0.0763 | 0.0531 ± 0.0709 |
| human_shuffled / categorical | scaffold / Ec_MIC | 5 | 1.9818 ± 0.0870 | -0.0131 ± 0.0879 |
| human_shuffled / categorical | scaffold / Sa_MBC | 5 | 2.1617 ± 0.1004 | -0.2143 ± 0.1126 |
| human_shuffled / categorical | scaffold / Sa_MIC | 5 | 1.9847 ± 0.0806 | -0.0272 ± 0.0826 |
| human_shuffled / categorical | scaffold / pooled | 5 | 2.0414 ± 0.0846 | — |
| human_weight_only / categorical | full-QAC105 / Ec_MBC | 5 | 2.6253 ± 0.1591 | -0.7670 ± 0.2108 |
| human_weight_only / categorical | full-QAC105 / Ec_MIC | 5 | 2.6645 ± 0.2457 | -1.1592 ± 0.3886 |
| human_weight_only / categorical | full-QAC105 / Sa_MBC | 5 | 2.2142 ± 0.1285 | -0.0966 ± 0.1254 |
| human_weight_only / categorical | full-QAC105 / Sa_MIC | 5 | 1.9600 ± 0.2042 | -0.2668 ± 0.2565 |
| human_weight_only / categorical | full-QAC105 / pooled | 5 | 2.3840 ± 0.1197 | — |
| human_weight_only / categorical | cation / Ec_MBC | 5 | 1.9619 ± 0.0261 | 0.1181 ± 0.0234 |
| human_weight_only / categorical | cation / Ec_MIC | 5 | 1.7928 ± 0.0325 | 0.1720 ± 0.0300 |
| human_weight_only / categorical | cation / Sa_MBC | 5 | 1.9613 ± 0.0164 | 0.0021 ± 0.0167 |
| human_weight_only / categorical | cation / Sa_MIC | 5 | 1.8299 ± 0.0232 | 0.1279 ± 0.0222 |
| human_weight_only / categorical | cation / pooled | 5 | 1.8881 ± 0.0198 | — |
| human_weight_only / categorical | scaffold / Ec_MBC | 5 | 2.1121 ± 0.0412 | -0.0222 ± 0.0399 |
| human_weight_only / categorical | scaffold / Ec_MIC | 5 | 2.0586 ± 0.0456 | -0.0919 ± 0.0483 |
| human_weight_only / categorical | scaffold / Sa_MBC | 5 | 2.2329 ± 0.0351 | -0.2936 ± 0.0409 |
| human_weight_only / categorical | scaffold / Sa_MIC | 5 | 2.0203 ± 0.0380 | -0.0633 ± 0.0405 |
| human_weight_only / categorical | scaffold / pooled | 5 | 2.1076 ± 0.0352 | — |
| initial / categorical | full-QAC105 / Ec_MBC | 5 | 2.4595 ± 0.2411 | -0.5582 ± 0.3034 |
| initial / categorical | full-QAC105 / Ec_MIC | 5 | 2.5089 ± 0.2147 | -0.9125 ± 0.3370 |
| initial / categorical | full-QAC105 / Sa_MBC | 5 | 2.2137 ± 0.1192 | -0.0956 ± 0.1177 |
| initial / categorical | full-QAC105 / Sa_MIC | 5 | 2.0414 ± 0.1644 | -0.3694 ± 0.2181 |
| initial / categorical | full-QAC105 / pooled | 5 | 2.3131 ± 0.1619 | — |
| initial / categorical | cation / Ec_MBC | 5 | 1.9887 ± 0.0428 | 0.0937 ± 0.0391 |
| initial / categorical | cation / Ec_MIC | 5 | 1.8106 ± 0.0505 | 0.1552 ± 0.0467 |
| initial / categorical | cation / Sa_MBC | 5 | 1.9368 ± 0.0383 | 0.0266 ± 0.0385 |
| initial / categorical | cation / Sa_MIC | 5 | 1.8143 ± 0.0233 | 0.1426 ± 0.0221 |
| initial / categorical | cation / pooled | 5 | 1.8893 ± 0.0341 | — |
| initial / categorical | scaffold / Ec_MBC | 5 | 2.0858 ± 0.0686 | 0.0025 ± 0.0651 |
| initial / categorical | scaffold / Ec_MIC | 5 | 2.0384 ± 0.0828 | -0.0716 ± 0.0865 |
| initial / categorical | scaffold / Sa_MBC | 5 | 2.2038 ± 0.0560 | -0.2605 ± 0.0632 |
| initial / categorical | scaffold / Sa_MIC | 5 | 2.0018 ± 0.0764 | -0.0448 ± 0.0784 |
| initial / categorical | scaffold / pooled | 5 | 2.0840 ± 0.0627 | — |
| mic_binary / categorical | full-QAC105 / Ec_MBC | 5 | 2.5923 ± 0.2004 | -0.7260 ± 0.2713 |
| mic_binary / categorical | full-QAC105 / Ec_MIC | 5 | 2.5124 ± 0.1562 | -0.9127 ± 0.2333 |
| mic_binary / categorical | full-QAC105 / Sa_MBC | 5 | 2.0509 ± 0.0751 | 0.0608 ± 0.0692 |
| mic_binary / categorical | full-QAC105 / Sa_MIC | 5 | 1.8802 ± 0.1123 | -0.1590 ± 0.1369 |
| mic_binary / categorical | full-QAC105 / pooled | 5 | 2.2759 ± 0.0951 | — |
| mic_binary / categorical | cation / Ec_MBC | 5 | 1.8840 ± 0.0586 | 0.1863 ± 0.0511 |
| mic_binary / categorical | cation / Ec_MIC | 5 | 1.7417 ± 0.0562 | 0.2180 ± 0.0507 |
| mic_binary / categorical | cation / Sa_MBC | 5 | 1.9789 ± 0.0516 | -0.0164 ± 0.0525 |
| mic_binary / categorical | cation / Sa_MIC | 5 | 1.8469 ± 0.0812 | 0.1103 ± 0.0780 |
| mic_binary / categorical | cation / pooled | 5 | 1.8649 ± 0.0590 | — |
| mic_binary / categorical | scaffold / Ec_MBC | 5 | 2.0558 ± 0.0486 | 0.0314 ± 0.0457 |
| mic_binary / categorical | scaffold / Ec_MIC | 5 | 2.0308 ± 0.0485 | -0.0627 ± 0.0504 |
| mic_binary / categorical | scaffold / Sa_MBC | 5 | 2.2656 ± 0.0810 | -0.3329 ± 0.0947 |
| mic_binary / categorical | scaffold / Sa_MIC | 5 | 2.0776 ± 0.0377 | -0.1245 ± 0.0408 |
| mic_binary / categorical | scaffold / pooled | 5 | 2.1096 ± 0.0521 | — |
| mic_binary / text | full-QAC105 / Ec_MBC | 5 | 2.5049 ± 0.2079 | -0.6127 ± 0.2632 |
| mic_binary / text | full-QAC105 / Ec_MIC | 5 | 2.4006 ± 0.2072 | -0.7512 ± 0.3049 |
| mic_binary / text | full-QAC105 / Sa_MBC | 5 | 2.0789 ± 0.2546 | 0.0243 ± 0.2361 |
| mic_binary / text | full-QAC105 / Sa_MIC | 5 | 1.8863 ± 0.1134 | -0.1666 ± 0.1417 |
| mic_binary / text | full-QAC105 / pooled | 5 | 2.2340 ± 0.0520 | — |
| mic_binary / text | cation / Ec_MBC | 5 | 1.8764 ± 0.0745 | 0.1923 ± 0.0656 |
| mic_binary / text | cation / Ec_MIC | 5 | 1.7669 ± 0.0828 | 0.1945 ± 0.0765 |
| mic_binary / text | cation / Sa_MBC | 5 | 1.9773 ± 0.0370 | -0.0145 ± 0.0382 |
| mic_binary / text | cation / Sa_MIC | 5 | 1.8445 ± 0.0670 | 0.1131 ± 0.0655 |
| mic_binary / text | cation / pooled | 5 | 1.8681 ± 0.0554 | — |
| mic_binary / text | scaffold / Ec_MBC | 5 | 2.0998 ± 0.0616 | -0.0108 ± 0.0583 |
| mic_binary / text | scaffold / Ec_MIC | 5 | 2.0205 ± 0.0607 | -0.0522 ± 0.0625 |
| mic_binary / text | scaffold / Sa_MBC | 5 | 2.2368 ± 0.0508 | -0.2984 ± 0.0590 |
| mic_binary / text | scaffold / Sa_MIC | 5 | 2.0808 ± 0.0658 | -0.1285 ± 0.0712 |
| mic_binary / text | scaffold / pooled | 5 | 2.1110 ± 0.0571 | — |
| mic_continuous / categorical | full-QAC105 / Ec_MBC | 5 | 2.9780 ± 0.3380 | -1.2905 ± 0.4966 |
| mic_continuous / categorical | full-QAC105 / Ec_MIC | 5 | 2.8449 ± 0.2598 | -1.4611 ± 0.4440 |
| mic_continuous / categorical | full-QAC105 / Sa_MBC | 5 | 2.1047 ± 0.1054 | 0.0099 ± 0.0984 |
| mic_continuous / categorical | full-QAC105 / Sa_MIC | 5 | 1.7707 ± 0.1544 | -0.0313 ± 0.1859 |
| mic_continuous / categorical | full-QAC105 / pooled | 5 | 2.4738 ± 0.1315 | — |
| mic_continuous / categorical | cation / Ec_MBC | 5 | 1.8763 ± 0.0143 | 0.1934 ± 0.0124 |
| mic_continuous / categorical | cation / Ec_MIC | 5 | 1.7554 ± 0.0304 | 0.2062 ± 0.0275 |
| mic_continuous / categorical | cation / Sa_MBC | 5 | 1.9814 ± 0.0451 | -0.0188 ± 0.0464 |
| mic_continuous / categorical | cation / Sa_MIC | 5 | 1.8125 ± 0.0539 | 0.1438 ± 0.0506 |
| mic_continuous / categorical | cation / pooled | 5 | 1.8584 ± 0.0314 | — |
| mic_continuous / categorical | scaffold / Ec_MBC | 5 | 2.1597 ± 0.0102 | -0.0685 ± 0.0101 |
| mic_continuous / categorical | scaffold / Ec_MIC | 5 | 2.1518 ± 0.0098 | -0.1926 ± 0.0108 |
| mic_continuous / categorical | scaffold / Sa_MBC | 5 | 2.3312 ± 0.0462 | -0.4101 ± 0.0557 |
| mic_continuous / categorical | scaffold / Sa_MIC | 5 | 2.0163 ± 0.0344 | -0.0591 ± 0.0365 |
| mic_continuous / categorical | scaffold / pooled | 5 | 2.1677 ± 0.0180 | — |
| mic_continuous / text | full-QAC105 / Ec_MBC | 5 | 3.0417 ± 0.4951 | -1.4152 ± 0.7599 |
| mic_continuous / text | full-QAC105 / Ec_MIC | 5 | 2.8322 ± 0.4478 | -1.4715 ± 0.7726 |
| mic_continuous / text | full-QAC105 / Sa_MBC | 5 | 2.0960 ± 0.1678 | 0.0150 ± 0.1603 |
| mic_continuous / text | full-QAC105 / Sa_MIC | 5 | 1.7856 ± 0.1557 | -0.0487 ± 0.1804 |
| mic_continuous / text | full-QAC105 / pooled | 5 | 2.4948 ± 0.2299 | — |
| mic_continuous / text | cation / Ec_MBC | 5 | 1.8488 ± 0.0245 | 0.2169 ± 0.0207 |
| mic_continuous / text | cation / Ec_MIC | 5 | 1.7629 ± 0.0297 | 0.1993 ± 0.0269 |
| mic_continuous / text | cation / Sa_MBC | 5 | 1.9282 ± 0.0441 | 0.0352 ± 0.0446 |
| mic_continuous / text | cation / Sa_MIC | 5 | 1.7851 ± 0.0538 | 0.1695 ± 0.0496 |
| mic_continuous / text | cation / pooled | 5 | 1.8326 ± 0.0264 | — |
| mic_continuous / text | scaffold / Ec_MBC | 5 | 2.1814 ± 0.0382 | -0.0904 ± 0.0379 |
| mic_continuous / text | scaffold / Ec_MIC | 5 | 2.1252 ± 0.0183 | -0.1634 ± 0.0201 |
| mic_continuous / text | scaffold / Sa_MBC | 5 | 2.2415 ± 0.0600 | -0.3041 ± 0.0691 |
| mic_continuous / text | scaffold / Sa_MIC | 5 | 2.0352 ± 0.0355 | -0.0789 ± 0.0377 |
| mic_continuous / text | scaffold / pooled | 5 | 2.1474 ± 0.0238 | — |

Table S42. Five-fold variability of the archived-feature and modern-decoder grouped validation. Mean ± fold SD, ddof=0. These unweighted fold means can differ from pooled out-of-fold RMSE/R²; the pooled values remain in main Tables 3 and 5. No OOD-fold SD is calculated.

| Representation / decoder | Regime / endpoint | Folds | RMSE mean ± SD | R² mean ± SD |
| --- | --- | --- | --- | --- |
| v5_human / categorical | cation / Ec_MBC | 5 | 1.9246 ± 0.2750 | 0.1200 ± 0.1620 |
| v5_human / categorical | cation / Ec_MIC | 5 | 1.8014 ± 0.2371 | 0.1285 ± 0.2139 |
| v5_human / categorical | cation / Sa_MBC | 5 | 1.9373 ± 0.4522 | -0.0930 ± 0.4733 |
| v5_human / categorical | cation / Sa_MIC | 5 | 1.7863 ± 0.3368 | 0.0925 ± 0.3769 |
| v5_human / categorical | cation / pooled | 5 | 1.8784 ± 0.2391 | — |
| v5_human / categorical | scaffold / Ec_MBC | 5 | 2.0351 ± 0.2025 | -0.0225 ± 0.1265 |
| v5_human / categorical | scaffold / Ec_MIC | 5 | 2.0141 ± 0.3970 | -0.2356 ± 0.4647 |
| v5_human / categorical | scaffold / Sa_MBC | 5 | 2.1372 ± 0.6634 | -0.3942 ± 0.5879 |
| v5_human / categorical | scaffold / Sa_MIC | 5 | 2.0044 ± 0.4245 | -0.3556 ± 0.7407 |
| v5_human / categorical | scaffold / pooled | 5 | 2.0703 ± 0.3382 | — |
| v5_human / onehot | cation / Ec_MBC | 5 | 1.9712 ± 0.2803 | 0.0653 ± 0.2165 |
| v5_human / onehot | cation / Ec_MIC | 5 | 1.8555 ± 0.1374 | 0.0742 ± 0.1723 |
| v5_human / onehot | cation / Sa_MBC | 5 | 1.9908 ± 0.3101 | -0.1513 ± 0.3562 |
| v5_human / onehot | cation / Sa_MIC | 5 | 1.7666 ± 0.3576 | 0.1045 ± 0.4094 |
| v5_human / onehot | cation / pooled | 5 | 1.9067 ± 0.2191 | — |
| v5_human / onehot | scaffold / Ec_MBC | 5 | 2.0612 ± 0.2516 | -0.0641 ± 0.2603 |
| v5_human / onehot | scaffold / Ec_MIC | 5 | 2.0084 ± 0.2964 | -0.2185 ± 0.3273 |
| v5_human / onehot | scaffold / Sa_MBC | 5 | 2.0749 ± 0.5474 | -0.3006 ± 0.4226 |
| v5_human / onehot | scaffold / Sa_MIC | 5 | 1.9612 ± 0.4706 | -0.3326 ± 0.8544 |
| v5_human / onehot | scaffold / pooled | 5 | 2.0410 ± 0.3330 | — |
| v5_human / separate | cation / Ec_MBC | 5 | 1.9973 ± 0.2985 | 0.0513 ± 0.1942 |
| v5_human / separate | cation / Ec_MIC | 5 | 1.8792 ± 0.1907 | 0.0546 ± 0.1898 |
| v5_human / separate | cation / Sa_MBC | 5 | 1.9834 ± 0.3247 | -0.1422 ± 0.3423 |
| v5_human / separate | cation / Sa_MIC | 5 | 1.7677 ± 0.3016 | 0.1109 ± 0.3419 |
| v5_human / separate | cation / pooled | 5 | 1.9162 ± 0.2313 | — |
| v5_human / separate | scaffold / Ec_MBC | 5 | 2.0427 ± 0.2615 | -0.0441 ± 0.2526 |
| v5_human / separate | scaffold / Ec_MIC | 5 | 1.9808 ± 0.3025 | -0.1855 ± 0.3245 |
| v5_human / separate | scaffold / Sa_MBC | 5 | 2.1208 ± 0.5085 | -0.3584 ± 0.3871 |
| v5_human / separate | scaffold / Sa_MIC | 5 | 2.0348 ± 0.4473 | -0.4074 ± 0.8175 |
| v5_human / separate | scaffold / pooled | 5 | 2.0613 ± 0.2989 | — |
| v5_human / text | cation / Ec_MBC | 5 | 1.9710 ± 0.2945 | 0.0749 ± 0.1949 |
| v5_human / text | cation / Ec_MIC | 5 | 1.8524 ± 0.1654 | 0.0793 ± 0.1749 |
| v5_human / text | cation / Sa_MBC | 5 | 1.9441 ± 0.3323 | -0.1213 ± 0.4012 |
| v5_human / text | cation / Sa_MIC | 5 | 1.7521 ± 0.3628 | 0.1027 ± 0.4529 |
| v5_human / text | cation / pooled | 5 | 1.8906 ± 0.2373 | — |
| v5_human / text | scaffold / Ec_MBC | 5 | 2.1049 ± 0.2508 | -0.1170 ± 0.2945 |
| v5_human / text | scaffold / Ec_MIC | 5 | 2.0027 ± 0.2998 | -0.2131 ± 0.3299 |
| v5_human / text | scaffold / Sa_MBC | 5 | 2.1190 ± 0.5567 | -0.3627 ± 0.4609 |
| v5_human / text | scaffold / Sa_MIC | 5 | 2.0117 ± 0.4438 | -0.3611 ± 0.7505 |
| v5_human / text | scaffold / pooled | 5 | 2.0748 ± 0.3236 | — |
| v5_qac_ablation / categorical | cation / Ec_MBC | 5 | 1.9211 ± 0.2901 | 0.1202 ± 0.1912 |
| v5_qac_ablation / categorical | cation / Ec_MIC | 5 | 1.7841 ± 0.1946 | 0.1393 ± 0.2171 |
| v5_qac_ablation / categorical | cation / Sa_MBC | 5 | 1.8895 ± 0.3628 | -0.0363 ± 0.3734 |
| v5_qac_ablation / categorical | cation / Sa_MIC | 5 | 1.6974 ± 0.3281 | 0.1880 ± 0.3093 |
| v5_qac_ablation / categorical | cation / pooled | 5 | 1.8384 ± 0.2048 | — |
| v5_qac_ablation / categorical | scaffold / Ec_MBC | 5 | 1.9702 ± 0.2101 | 0.0330 ± 0.1768 |
| v5_qac_ablation / categorical | scaffold / Ec_MIC | 5 | 1.9411 ± 0.3460 | -0.1633 ± 0.4242 |
| v5_qac_ablation / categorical | scaffold / Sa_MBC | 5 | 2.0468 ± 0.6125 | -0.2775 ± 0.5028 |
| v5_qac_ablation / categorical | scaffold / Sa_MIC | 5 | 1.8606 ± 0.3731 | -0.1641 ± 0.6145 |
| v5_qac_ablation / categorical | scaffold / pooled | 5 | 1.9761 ± 0.2996 | — |
| v5_qac_ablation / onehot | cation / Ec_MBC | 5 | 1.9720 ± 0.3508 | 0.0849 ± 0.2033 |
| v5_qac_ablation / onehot | cation / Ec_MIC | 5 | 1.8329 ± 0.2288 | 0.1089 ± 0.1565 |
| v5_qac_ablation / onehot | cation / Sa_MBC | 5 | 1.9198 ± 0.2137 | -0.0769 ± 0.3100 |
| v5_qac_ablation / onehot | cation / Sa_MIC | 5 | 1.7000 ± 0.2757 | 0.1803 ± 0.2999 |
| v5_qac_ablation / onehot | cation / pooled | 5 | 1.8663 ± 0.2169 | — |
| v5_qac_ablation / onehot | scaffold / Ec_MBC | 5 | 2.0156 ± 0.2746 | -0.0132 ± 0.2511 |
| v5_qac_ablation / onehot | scaffold / Ec_MIC | 5 | 1.9382 ± 0.3579 | -0.1362 ± 0.3697 |
| v5_qac_ablation / onehot | scaffold / Sa_MBC | 5 | 2.0682 ± 0.4980 | -0.2975 ± 0.3746 |
| v5_qac_ablation / onehot | scaffold / Sa_MIC | 5 | 1.8933 ± 0.3858 | -0.2317 ± 0.7163 |
| v5_qac_ablation / onehot | scaffold / pooled | 5 | 1.9918 ± 0.3211 | — |
| v5_qac_ablation / separate | cation / Ec_MBC | 5 | 1.9814 ± 0.3348 | 0.0700 ± 0.2144 |
| v5_qac_ablation / separate | cation / Ec_MIC | 5 | 1.7813 ± 0.1918 | 0.1509 ± 0.1675 |
| v5_qac_ablation / separate | cation / Sa_MBC | 5 | 1.9710 ± 0.1938 | -0.1447 ± 0.3480 |
| v5_qac_ablation / separate | cation / Sa_MIC | 5 | 1.7110 ± 0.2821 | 0.1774 ± 0.2677 |
| v5_qac_ablation / separate | cation / pooled | 5 | 1.8708 ± 0.2105 | — |
| v5_qac_ablation / separate | scaffold / Ec_MBC | 5 | 2.0638 ± 0.2262 | -0.0659 ± 0.2412 |
| v5_qac_ablation / separate | scaffold / Ec_MIC | 5 | 1.9719 ± 0.3086 | -0.1893 ± 0.3798 |
| v5_qac_ablation / separate | scaffold / Sa_MBC | 5 | 2.0550 ± 0.5274 | -0.2756 ± 0.3927 |
| v5_qac_ablation / separate | scaffold / Sa_MIC | 5 | 1.8532 ± 0.3452 | -0.1601 ± 0.6056 |
| v5_qac_ablation / separate | scaffold / pooled | 5 | 1.9984 ± 0.3060 | — |
| v5_qac_ablation / text | cation / Ec_MBC | 5 | 1.8646 ± 0.2965 | 0.1777 ± 0.1671 |
| v5_qac_ablation / text | cation / Ec_MIC | 5 | 1.7158 ± 0.1960 | 0.2188 ± 0.1242 |
| v5_qac_ablation / text | cation / Sa_MBC | 5 | 1.8771 ± 0.1917 | -0.0178 ± 0.2385 |
| v5_qac_ablation / text | cation / Sa_MIC | 5 | 1.6180 ± 0.2779 | 0.2563 ± 0.2866 |
| v5_qac_ablation / text | cation / pooled | 5 | 1.7798 ± 0.1815 | — |
| v5_qac_ablation / text | scaffold / Ec_MBC | 5 | 2.0427 ± 0.2877 | -0.0558 ± 0.3273 |
| v5_qac_ablation / text | scaffold / Ec_MIC | 5 | 1.9548 ± 0.2903 | -0.1756 ± 0.3820 |
| v5_qac_ablation / text | scaffold / Sa_MBC | 5 | 2.0473 ± 0.4980 | -0.2715 ± 0.3722 |
| v5_qac_ablation / text | scaffold / Sa_MIC | 5 | 1.8612 ± 0.3849 | -0.1614 ± 0.6188 |
| v5_qac_ablation / text | scaffold / pooled | 5 | 1.9890 ± 0.3113 | — |
| v5_raw / categorical | cation / Ec_MBC | 5 | 1.9397 ± 0.3596 | 0.1124 ± 0.2106 |
| v5_raw / categorical | cation / Ec_MIC | 5 | 1.8052 ± 0.2516 | 0.1187 ± 0.2473 |
| v5_raw / categorical | cation / Sa_MBC | 5 | 1.9118 ± 0.3735 | -0.0568 ± 0.3802 |
| v5_raw / categorical | cation / Sa_MIC | 5 | 1.7839 ± 0.3395 | 0.0877 ± 0.3976 |
| v5_raw / categorical | cation / pooled | 5 | 1.8773 ± 0.2290 | — |
| v5_raw / categorical | scaffold / Ec_MBC | 5 | 2.0913 ± 0.2449 | -0.0755 ± 0.1217 |
| v5_raw / categorical | scaffold / Ec_MIC | 5 | 2.0446 ± 0.3731 | -0.2645 ± 0.3961 |
| v5_raw / categorical | scaffold / Sa_MBC | 5 | 2.1278 ± 0.5582 | -0.3669 ± 0.4343 |
| v5_raw / categorical | scaffold / Sa_MIC | 5 | 1.9419 ± 0.4146 | -0.2695 ± 0.6966 |
| v5_raw / categorical | scaffold / pooled | 5 | 2.0735 ± 0.2902 | — |
| v5_raw / onehot | cation / Ec_MBC | 5 | 1.9562 ± 0.3094 | 0.0862 ± 0.2136 |
| v5_raw / onehot | cation / Ec_MIC | 5 | 1.8401 ± 0.1778 | 0.0913 ± 0.1741 |
| v5_raw / onehot | cation / Sa_MBC | 5 | 1.9294 ± 0.2583 | -0.0796 ± 0.3101 |
| v5_raw / onehot | cation / Sa_MIC | 5 | 1.7262 ± 0.3727 | 0.1421 ± 0.4095 |
| v5_raw / onehot | cation / pooled | 5 | 1.8759 ± 0.2073 | — |
| v5_raw / onehot | scaffold / Ec_MBC | 5 | 2.0945 ± 0.3150 | -0.0847 ± 0.2436 |
| v5_raw / onehot | scaffold / Ec_MIC | 5 | 1.9976 ± 0.4116 | -0.1907 ± 0.3572 |
| v5_raw / onehot | scaffold / Sa_MBC | 5 | 2.0992 ± 0.4800 | -0.3337 ± 0.3565 |
| v5_raw / onehot | scaffold / Sa_MIC | 5 | 1.9725 ± 0.4092 | -0.3314 ± 0.7718 |
| v5_raw / onehot | scaffold / pooled | 5 | 2.0569 ± 0.3230 | — |
| v5_raw / separate | cation / Ec_MBC | 5 | 1.9960 ± 0.3558 | 0.0586 ± 0.2181 |
| v5_raw / separate | cation / Ec_MIC | 5 | 1.8350 ± 0.2172 | 0.0960 ± 0.2077 |
| v5_raw / separate | cation / Sa_MBC | 5 | 1.9711 ± 0.2784 | -0.1373 ± 0.3619 |
| v5_raw / separate | cation / Sa_MIC | 5 | 1.7501 ± 0.3610 | 0.1343 ± 0.3595 |
| v5_raw / separate | cation / pooled | 5 | 1.9014 ± 0.2344 | — |
| v5_raw / separate | scaffold / Ec_MBC | 5 | 2.1145 ± 0.3046 | -0.1211 ± 0.3059 |
| v5_raw / separate | scaffold / Ec_MIC | 5 | 1.9725 ± 0.3072 | -0.1662 ± 0.2754 |
| v5_raw / separate | scaffold / Sa_MBC | 5 | 2.1554 ± 0.4767 | -0.4052 ± 0.3560 |
| v5_raw / separate | scaffold / Sa_MIC | 5 | 1.9612 ± 0.3723 | -0.3024 ± 0.6884 |
| v5_raw / separate | scaffold / pooled | 5 | 2.0660 ± 0.2887 | — |
| v5_raw / text | cation / Ec_MBC | 5 | 1.9580 ± 0.3212 | 0.0835 ± 0.2297 |
| v5_raw / text | cation / Ec_MIC | 5 | 1.8147 ± 0.1856 | 0.1118 ± 0.2064 |
| v5_raw / text | cation / Sa_MBC | 5 | 1.9336 ± 0.3084 | -0.0892 ± 0.3600 |
| v5_raw / text | cation / Sa_MIC | 5 | 1.7604 ± 0.3931 | 0.1102 ± 0.4306 |
| v5_raw / text | cation / pooled | 5 | 1.8777 ± 0.2493 | — |
| v5_raw / text | scaffold / Ec_MBC | 5 | 2.1018 ± 0.2997 | -0.0891 ± 0.2109 |
| v5_raw / text | scaffold / Ec_MIC | 5 | 2.0084 ± 0.3814 | -0.2086 ± 0.3458 |
| v5_raw / text | scaffold / Sa_MBC | 5 | 2.1413 ± 0.5194 | -0.3859 ± 0.3942 |
| v5_raw / text | scaffold / Sa_MIC | 5 | 1.9891 ± 0.4018 | -0.3569 ± 0.7815 |
| v5_raw / text | scaffold / pooled | 5 | 2.0768 ± 0.3188 | — |
| v5_human / autogluon | cation / Ec_MBC | 5 | 2.0942 ± 0.2242 | -0.0343 ± 0.0461 |
| v5_human / autogluon | cation / Ec_MIC | 5 | 1.9664 ± 0.1985 | -0.0202 ± 0.0737 |
| v5_human / autogluon | cation / Sa_MBC | 5 | 2.1546 ± 0.3664 | -0.3023 ± 0.2711 |
| v5_human / autogluon | cation / Sa_MIC | 5 | 1.9238 ± 0.4352 | -0.0313 ± 0.4016 |
| v5_human / autogluon | cation / pooled | 5 | 2.0500 ± 0.2227 | — |
| v5_human / autogluon | scaffold / Ec_MBC | 5 | 2.1654 ± 0.3014 | -0.1586 ± 0.2266 |
| v5_human / autogluon | scaffold / Ec_MIC | 5 | 2.0572 ± 0.3396 | -0.2734 ± 0.3520 |
| v5_human / autogluon | scaffold / Sa_MBC | 5 | 2.1611 ± 0.4337 | -0.4095 ± 0.3018 |
| v5_human / autogluon | scaffold / Sa_MIC | 5 | 2.1184 ± 0.4509 | -0.5229 ± 0.8577 |
| v5_human / autogluon | scaffold / pooled | 5 | 2.1414 ± 0.2894 | — |
| v5_raw / autogluon | cation / Ec_MBC | 5 | 2.0147 ± 0.2960 | 0.0378 ± 0.1810 |
| v5_raw / autogluon | cation / Ec_MIC | 5 | 1.8537 ± 0.1929 | 0.0826 ± 0.1570 |
| v5_raw / autogluon | cation / Sa_MBC | 5 | 2.0998 ± 0.4234 | -0.2980 ± 0.5472 |
| v5_raw / autogluon | cation / Sa_MIC | 5 | 1.8481 ± 0.4120 | 0.0040 ± 0.5130 |
| v5_raw / autogluon | cation / pooled | 5 | 1.9705 ± 0.2562 | — |
| v5_raw / autogluon | scaffold / Ec_MBC | 5 | 2.0825 ± 0.2568 | -0.0929 ± 0.3014 |
| v5_raw / autogluon | scaffold / Ec_MIC | 5 | 2.0643 ± 0.3437 | -0.2765 ± 0.3285 |
| v5_raw / autogluon | scaffold / Sa_MBC | 5 | 2.2146 ± 0.4886 | -0.4819 ± 0.3718 |
| v5_raw / autogluon | scaffold / Sa_MIC | 5 | 2.0191 ± 0.3951 | -0.3821 ± 0.7496 |
| v5_raw / autogluon | scaffold / pooled | 5 | 2.1095 ± 0.2991 | — |
| v5_human / tabfm | cation / Ec_MBC | 5 | 2.0853 ± 0.2738 | -0.0242 ± 0.1162 |
| v5_human / tabfm | cation / Ec_MIC | 5 | 1.9556 ± 0.1693 | -0.0171 ± 0.1298 |
| v5_human / tabfm | cation / Sa_MBC | 5 | 2.0785 ± 0.2589 | -0.2494 ± 0.3275 |
| v5_human / tabfm | cation / Sa_MIC | 5 | 1.8467 ± 0.4581 | 0.0152 ± 0.5272 |
| v5_human / tabfm | cation / pooled | 5 | 2.0050 ± 0.2256 | — |
| v5_human / tabfm | scaffold / Ec_MBC | 5 | 2.0670 ± 0.2604 | -0.0551 ± 0.1872 |
| v5_human / tabfm | scaffold / Ec_MIC | 5 | 2.0045 ± 0.2900 | -0.1957 ± 0.2201 |
| v5_human / tabfm | scaffold / Sa_MBC | 5 | 2.1571 ± 0.4078 | -0.4012 ± 0.2614 |
| v5_human / tabfm | scaffold / Sa_MIC | 5 | 2.0815 ± 0.3259 | -0.4014 ± 0.4921 |
| v5_human / tabfm | scaffold / pooled | 5 | 2.0904 ± 0.2350 | — |
| v5_raw / tabfm | cation / Ec_MBC | 5 | 1.9663 ± 0.3326 | 0.0837 ± 0.2039 |
| v5_raw / tabfm | cation / Ec_MIC | 5 | 1.8582 ± 0.1506 | 0.0668 ± 0.2015 |
| v5_raw / tabfm | cation / Sa_MBC | 5 | 1.9501 ± 0.2648 | -0.0990 ± 0.2965 |
| v5_raw / tabfm | cation / Sa_MIC | 5 | 1.7230 ± 0.4299 | 0.1261 ± 0.4987 |
| v5_raw / tabfm | cation / pooled | 5 | 1.8884 ± 0.2320 | — |
| v5_raw / tabfm | scaffold / Ec_MBC | 5 | 2.0535 ± 0.2647 | -0.0429 ± 0.1974 |
| v5_raw / tabfm | scaffold / Ec_MIC | 5 | 1.9790 ± 0.3134 | -0.1660 ± 0.2438 |
| v5_raw / tabfm | scaffold / Sa_MBC | 5 | 2.1375 ± 0.4025 | -0.3844 ± 0.2949 |
| v5_raw / tabfm | scaffold / Sa_MIC | 5 | 2.0410 ± 0.3258 | -0.4203 ± 0.7110 |
| v5_raw / tabfm | scaffold / pooled | 5 | 2.0645 ± 0.2528 | — |
| v5_human / tabpfn | cation / Ec_MBC | 5 | 2.1155 ± 0.2713 | -0.0524 ± 0.0984 |
| v5_human / tabpfn | cation / Ec_MIC | 5 | 1.9536 ± 0.2034 | -0.0059 ± 0.0649 |
| v5_human / tabpfn | cation / Sa_MBC | 5 | 1.9840 ± 0.3254 | -0.0953 ± 0.1703 |
| v5_human / tabpfn | cation / Sa_MIC | 5 | 1.9344 ± 0.3217 | -0.0274 ± 0.2421 |
| v5_human / tabpfn | cation / pooled | 5 | 2.0090 ± 0.1941 | — |
| v5_human / tabpfn | scaffold / Ec_MBC | 5 | 2.1172 ± 0.3066 | -0.1074 ± 0.2357 |
| v5_human / tabpfn | scaffold / Ec_MIC | 5 | 2.0047 ± 0.3432 | -0.1981 ± 0.2894 |
| v5_human / tabpfn | scaffold / Sa_MBC | 5 | 2.2107 ± 0.4650 | -0.4686 ± 0.3320 |
| v5_human / tabpfn | scaffold / Sa_MIC | 5 | 2.0581 ± 0.3681 | -0.3813 ± 0.5624 |
| v5_human / tabpfn | scaffold / pooled | 5 | 2.1134 ± 0.2838 | — |
| v5_raw / tabpfn | cation / Ec_MBC | 5 | 2.0397 ± 0.2667 | 0.0255 ± 0.0514 |
| v5_raw / tabpfn | cation / Ec_MIC | 5 | 1.9344 ± 0.1839 | 0.0118 ± 0.0620 |
| v5_raw / tabpfn | cation / Sa_MBC | 5 | 1.9433 ± 0.2689 | -0.0567 ± 0.1329 |
| v5_raw / tabpfn | cation / Sa_MIC | 5 | 1.8694 ± 0.3827 | 0.0085 ± 0.4041 |
| v5_raw / tabpfn | cation / pooled | 5 | 1.9610 ± 0.1692 | — |
| v5_raw / tabpfn | scaffold / Ec_MBC | 5 | 2.0695 ± 0.3083 | -0.0730 ± 0.3074 |
| v5_raw / tabpfn | scaffold / Ec_MIC | 5 | 2.0047 ± 0.3119 | -0.2055 ± 0.2945 |
| v5_raw / tabpfn | scaffold / Sa_MBC | 5 | 2.0538 ± 0.3949 | -0.2684 ± 0.2214 |
| v5_raw / tabpfn | scaffold / Sa_MIC | 5 | 2.0450 ± 0.3483 | -0.4447 ± 0.7579 |
| v5_raw / tabpfn | scaffold / pooled | 5 | 2.0521 ± 0.2861 | — |

Table S43. Recovered original CV uncertainty for linear representation probes. These metrics concern coordinate reconstruction, not antibacterial endpoint regression.

| Probe | Folds | R² mean | Fold SD | Provenance |
| --- | --- | --- | --- | --- |
| MolFormer → human encoder | 5 | 0.891 | 0.037 | May causal_final cell5, saved output |
| Human encoder → MolFormer | 5 | 0.844 | 0.060 | May causal_final cell5, saved output |

Table S44. Relationship between the author’s method and the added calculations.

| Calculation | Representation / encoder | Target learner | Continuity | Declared changes |
| --- | --- | --- | --- | --- |
| Original Tables 1–2 | Author source models | Original reported models | Preserved original results | Rounding correction and explicit provenance |
| New original-row CV | Saved raw / human compact encoder | CatBoost 500/depth6/.05/42 | Frozen features, saved encoder, author CV coding | October text cache; recorded environment; explicit 5 folds |
| 105-QAC grouped and 17-OOD tests | Saved raw / human compact encoder | Same CatBoost budget | Original two-stage prediction route | Cation/scaffold split; exact/bound OOD registry |
| Matched compact source controls | 768→512→384→256, frozen MolFormer | Same CatBoost budget | Original architecture; human/binary contrastive objective | Common excluded-target source; no SMOTE; five paired seeds |
| Modern TabPFN/TabFM/AutoGluon | Saved raw / human encoder | New tabular decoders | Same target registers and archived features | Train-only PCA32 and model-specific budgets |
| Graph and direct fine-tuning | Chemprop / adapted backbone | Graph head / direct head | Independent benchmark against the same targets | Different architecture, objectives and adaptation budgets |

All mean±SD entries identify the source of variability and number of repeats. They are descriptive spread estimates, not automatically 95% confidence intervals. Existing paired bootstrap intervals are retained unchanged. A missing SD is not replaced by zero, a neighbouring model, an OOD bootstrap width or a different split.

S33. Before/after figure sources and graphic-only redraw

The revised main Figure2 uses exact vector marker centres from publication_tsne_before_after.pdf, with no new dimensionality reduction. The PDF contains 221 marker calls in each panel (172 Bad,49 Good) and prints silhouette 0.007/0.107. The original Word raster below instead prints 0.108 for the after panel. The archive variants are not silently equated. Display-point coordinates do not recover molecule identifiers or the original high-dimensional features, and are not used to recalculate cluster metrics. All previous predictive metrics, uncertainty intervals and tables remain unchanged.


Figure S31. Original v5 before/after contrastive-learning raster, retained byte-for-byte. Its printed silhouette after training is 0.108; the vector-PDF variant redrawn in main Figure2 prints 0.107. The old raster remains available as source provenance, not as a new calculation.

