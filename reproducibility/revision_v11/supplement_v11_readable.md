Supporting Information — Human Supervision and Controlled Quantitative Comparisons

Human versus Quantitative Supervision for Antibacterial Molecular Representation Learning

Scope and evaluation protocols

This Supporting Information accompanies the focused author draft. Partial-fine-tuning, matched frozen-feature and historical analyses use different source exclusions, cohorts and architectures. Their results are reported separately; source metadata and full prediction files accompany the computational analyses.

The main comparisons use partial backbone fine-tuning or frozen-feature adaptation as specified. MIC record counts are distinguished from unique molecules. OOD-17 is a small secondary collection, affine recalibration is exploratory and in-sample, and individual expert votes and a pre-specified equivalence criterion are unavailable in the supplied archive. The human-annotation collection protocol is reserved for coauthor completion in main Section 2.1.1.

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


Figure S1. Expert-label audit: class balance and annotation-round drift. The final labels are the available supervision artifact; individual votes are not archived.


Figure S2. Molecule-level overlap. The overlap is a design feature for a controlled supervision comparison but limits claims of independent dataset superiority.

S2. Q-HERO external benchmark and residual distributions

The historical Q-HERO collection contains 411 structures with a matched S. aureus MIC endpoint. The archived residual plots are descriptive. These analyses precede the strict evaluation-cation exclusions and matched controls used for Q-HERO-405; they do not establish equivalence or an independently identified expert advantage.


Figure S3. Historical absolute-residual distributions on Q-HERO. Similar distribution shapes are descriptive and do not establish equivalence; cohort and source exclusions differ from the matched Q-HERO-405 experiments.


Figure S4. Q-HERO benchmark results. Interpret representation differences with the reported seed variation and the controlled overlap design.

S3. Historical OOD comparison

The 17 newly synthesised compounds are structurally held out, but n = 17 limits precision. The matched-ablation result suggests no resolved mean residual advantage (expert − regression ΔRMSE = −0.086, 95% bootstrap CI [−0.227, +0.054]); it is not presented as a pre-specified statistical-equivalence result.


Figure S5. Historical residual and TOST analysis, retained for transparency. The small sample and absence of a pre-specified equivalence margin make the analysis exploratory.


Figure S6. Split-design effect. Pair-level splitting can place the same molecule in train and test; molecule-grouped splits are required for conservative inference.

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


Figure S7. Downstream representation quality, mean ± standard deviation over three seeds, after partial backbone fine-tuning. The descriptor baseline is positive on Q-HERO (R² = +0.057); absolute scores remain modest.

S5. Direct zero-shot transfer and exploratory calibration

Without target refitting, quantitative supervision produces stronger rank agreement than expert supervision on Q-HERO and OOD-17, while raw R² remains negative. The highest OOD-17 mean rank agreement is ρ = 0.75 for the 9,338-record model; this estimate has n = 17. Expert scores still carry positive potency-related rank signal despite never observing concentrations.

Table S3. Direct-transfer rank agreement and AUC, means across three seeds (from finetune/runs_direct.jsonl).

| Source | QAC-105 ρ / AUC | Q-HERO ρ / AUC | OOD-17 ρ / AUC | Interpretation |
| --- | --- | --- | --- | --- |
| Expert (740 labels) | +0.221 / 0.644 | +0.397 / 0.688 | +0.295 / 0.597 | rank signal only |
| Quant. 1,153 molecules | +0.210 / 0.652 | +0.547 / 0.780 | +0.619 / 0.852 | stronger ranking |
| Quant. 9,338 records | +0.176 / 0.630 | +0.612 / 0.814 | +0.752 / 0.866 | strongest; OOD n=17 |


Figure S8. Direct zero-shot transfer. These predictions are best interpreted as rankings, not calibrated absolute MIC estimates.

Affine recalibration was fitted and evaluated on the same target predictions. It is included only as an exploratory diagnostic of scale mismatch; it does not demonstrate generalisable target calibration.

Table S4. Exploratory in-sample affine recalibration (from finetune/recalibration.csv).

| Target | Raw R² | In-sample affine R² | Mean slope | Mean offset log₂ |
| --- | --- | --- | --- | --- |
| QAC-105 | −0.83 | +0.03 | 0.23 | +1.20 |
| Q-HERO | −1.62 | +0.36 | 0.47 | +2.11 |
| OOD-17 | −2.92 | +0.49 | 0.98 | +3.01 |


Figure S9. Exploratory in-sample affine recalibration. A held-out or nested target-calibration protocol is required before reporting calibrated generalisation.

S6. Reproducibility inventory and limitations

Primary artifacts: reproducibility/finetune/runs.jsonl (partial-fine-tuning matrix), runs_direct.jsonl (direct transfer), recalibration.csv (exploratory recalibration), qhero/qhero_metrics.csv and qhero_residuals.csv (Q-HERO), analysis/ablation_bootstrap.csv (matched OOD ablation), and FINDINGS.md (audit). CKA/probing and SHAP summary provenance is incomplete, so they are not used for causal or mechanistic claims in v8.

S7. New controlled supervision experiments

The new experiment holds source molecules, source cation-scaffold split, frozen MolFormer features, initial weights and training budget constant within each matched panel. Source sizes: 681 pooled-MIC common molecules (4,938 underlying records) and 529 exact S. aureus-MIC common molecules (855 records). Evaluation sizes: QAC-104 = 104, Q-HERO-405 = 405, OOD-17 = 17. Every evaluation cation, including counterion variants, is absent from all new sources. Binary source labels use BCE-with-logits; quantitative source targets use source-training standardised MSE. A 768→256→128 neural encoder is trained for 80 epochs with five paired seeds. Target decoders refit on fixed target folds, so this is representation evaluation rather than direct transfer. Bootstrap intervals condition on those folds and trained seeds. The Ridge decoder with target-training standardisation can extrapolate unstably; all extreme results remain available. No non-inferiority or equivalence margin is introduced.


Figure S10. Earlier supervision comparisons, retained as supplementary context. Partial-fine-tuning and frozen-feature panels have different cohorts and architectures. Error bars are conditional-scaffold intervals; the main text reports the nested seed/scaffold sensitivity.

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

Figure S11. Chemical-space illustration from frozen MolFormer features, with per-molecule L2 normalisation and PCA fitted on source-training molecules. Joint t-SNE uses held-out structures solely for illustration; proximity does not establish transferability or causal mechanisms. Source validation reserves 15% of scaffold groups rather than 15% of molecules: in the pooled panel, 377 molecules are in training and 304 in validation.


Figure S12. (a) Measured external MIC distributions by the predicted Good/Bad class of one archived direct expert checkpoint, threshold logit=0 fixed without target labels; Q-HERO-405 subset, descriptive and conditional on seed 0. These are model-predicted classes, not human annotations of external compounds. (b) Three-seed direct rank agreement from the original Q-HERO-411 cohort, with mean and seed standard deviation. No downstream target refitting in either panel; cohorts differ, and raw direct MIC calibration remains unvalidated.


S15. Historical contrastive, in-domain and geometric analyses

These historical branches are supplementary descriptive material. They use a contrastive architecture distinct from the matched 256→128 encoder, and some source exclusions or generating scripts are incomplete. They are not used to identify the main supervision-intervention effects. Citation numbers in Sections S15–S16 follow the supplementary reference list in S17.


Figure S13. Historical expert-guidance diagram. This branch is distinct from the matched source-label interventions in the main article.

S15.1. Historical contrastive encoder


The expert-guidance dataset contains 1,103 final Good/Bad annotations. Repository artifacts retain the final label but not the individual annotator votes or adjudication records. The historical description of three independent experts and majority resolution therefore cannot be independently verified from the archived files, and inter-rater agreement cannot be calculated. We analyse the final labels as the available supervision signal. The class balance is 859 Bad and 244 Good; annotation-round drift and SMILES quality-control limitations are reported in the Supporting Information.

For exploratory model selection, we benchmarked MolFormer, ChemBERTa, Morgan, and MACCS representations under a five-fold stratified protocol. MolFormer produced the highest archived mean F1-score (0.655 with an MLP and StandardScaler) and accuracy (0.856). Because the expert-label set is imbalanced, accuracy alone is not interpreted as a performance claim; these internal model-selection diagnostics are separate from external validation.

Building on the MolFormer baseline, we trained a dedicated MLP-based encoder (512 → 384 → 256 neurons) with a supervised contrastive objective to distill the implicit “chemical intuition” embedded in the expert labels into a compact, task-specific latent space. To address the inherent class imbalance of the expert-annotated dataset, we employed Borderline SMOTE (sampling strategy = 0.8) during encoder training. The model was optimized with a hard-negative contrastive loss, which explicitly pushes hard misclassified negatives away from the anchor embedding, thereby sharpening inter-class boundaries. The resulting 256-dimensional representations are referred to as human embeddings hereafter.

Figure S14 presents t-SNE projections (perplexity = 30) of a held-out fold before and after contrastive refinement. The internal clustering diagnostics changed from silhouette 0.007 to 0.108, Davies–Bouldin 6.54 to 2.58, and Calinski–Harabasz 3.60 to 22.08. These visual and internal diagnostics indicate separation of the final label classes within this analysis; they are not evidence of external antibacterial-prediction performance.


Figure S14. Historical t-SNE class-separation illustration for the contrastive encoder. Class separation does not establish external potency-prediction performance.


S15.2. Audited in-domain comparison

The historical architecture table is not used for comparative inference because its RMSE and R² entries combine different pipelines and split definitions. Table S9 retains the audited molecule-grouped comparison; the new cation-clean supervision interventions are reported separately in Tables S5–S6.

Historical analyses of one-hot and text-encoded task labels are exploratory because the corresponding metrics were generated under incompatible pipelines and splits. They are not evidence for the controlled supervision comparisons reported here.



Table S9 reports the audited molecule-grouped comparison on QAC-105. Under this conservative split, expert, quantitative, and raw MolFormer representations are within seed variation. This in-domain result is descriptive and should be read with the external Q-HERO and partial-fine-tuning analyses.


A natural objection to using expert Good/Bad labels is that a larger body of quantitative data should be preferable when it is available. The original in-domain comparison is retained as a descriptive analysis, but its absolute values are not used as primary evidence: QAC-105 molecules overlap the representation-training collections and the historical table combines outputs from different pipelines and split definitions. The externally held-out and controlled partial-fine-tuning results in Supporting Information Section S4 provide the principal current comparison.

The quantitative corpus used in the historical comparison was assembled from broad QAC activity records. Its record count must not be interpreted as the number of independent molecules: the fine-tuning subset used in Supporting Information Section S4 contains 9,338 MIC records over 1,153 unique molecules. The expert and quantitative collections have substantial molecule-level overlap, which makes their comparison controlled but not independent.

Both embedding types were subsequently evaluated on the same QAC collection. This retrospective in-domain result is consistent with similar downstream behaviour of the two supervision sources, but it is not a clean external validation. The molecule-level overlap and pair-level split inflate absolute performance, and raw MolFormer is also competitive under the audited re-run. We therefore do not use this table to claim that human annotations outperform or are statistically equivalent to quantitative measurements.

Similarity in one downstream protocol does not mean that a binary label is informationally equivalent to a quantitative measurement. A final expert call may reflect multiple activity reports and additional considerations, while pooled quantitative records contain repeated molecules and heterogeneous assay contexts. The appropriate conclusion is limited to comparable representation quality under the evaluated refitting protocol.


Table S9. Audited QAC-105 molecule-grouped comparison: CatBoost R², mean ± seed standard deviation over ten seeds. Molecules are held out of the target-regressor training fold; representation-training source overlap remains a limitation. Values are retained from the archived audit.

| Representation | S. aureus MIC | S. aureus MBC | E. coli MIC | E. coli MBC |
| --- | --- | --- | --- | --- |
| Raw MolFormer | 0.19 ± 0.19 | 0.00 ± 0.30 | 0.12 ± 0.19 | 0.08 ± 0.22 |
| Expert (Good/Bad) | 0.27 ± 0.16 | 0.06 ± 0.27 | 0.09 ± 0.19 | 0.06 ± 0.27 |
| Quantitative regression | 0.31 ± 0.13 | 0.08 ± 0.22 | 0.16 ± 0.22 | 0.08 ± 0.26 |


S15.3. Archived representation geometry and attribution

Representational similarity and matched prediction contrasts answer different questions. Archived CKA/probing describes geometry, whereas the new interventions in main Sections 3.2–3.3 manipulate supervision within a fixed algorithm. Neither a similarity score nor SHAP attribution identifies molecular antibacterial mechanisms (78).


Figure S15. Historical conceptual information flow in the contrastive encoder. The diagram is not a quantitative causal decomposition.

The archived CKA/probing table reports high alignment between MolFormer and the expert embedding (CKA 0.933 in-domain and 0.946 OOD; linear-probe R² 0.891 from MolFormer to embedding and 0.844 in reverse). These values suggest substantial preservation of the pretrained geometry. Because the generating script is absent, they are reported as archived descriptive results rather than independently regenerated evidence.

Geometric similarity does not determine how a downstream model uses each representation. The archived SHAP summary has unresolved provenance: the available decomposition file reports a different aggregate embedding attribution from the manuscript, and it is not confirmed that the same encoder generated all analyses. We therefore omit numerical SHAP attribution as a basis for mechanistic or causal claims. A fully versioned pipeline is required before interpreting feature attributions.

A matched expert-versus-regression encoder ablation was run on the OOD case-study data. It suggests similar mean absolute residuals (expert − regression ΔRMSE = −0.086, 95% bootstrap CI [−0.227, +0.054]) and point estimates of 2.19 versus 2.27 log2 units. This interval includes no difference and is based on 17 compounds. It supports a cautious descriptive statement of no resolved advantage in this dataset; it does not establish statistical equivalence or identify a causal mechanism.

The descriptive pattern does not identify a robust subgroup advantage for either supervision source in the 17-compound case study. Any finer claim would require an a priori margin, a larger independent set, and a preregistered non-inferiority or equivalence protocol.

The archived analyses describe preservation of pretrained geometry and similar downstream behaviour under some protocols. Their incomplete provenance precludes a quantitative causal decomposition. main Sections 3.2–3.3 supplies a stronger test of supervision content through paired interventions, while retaining the distinction between an algorithmic effect and antibacterial causality.

S16. Synthesis, characterisation and microbiological protocols

This section preserves the chemical descriptions and available protocols from the source manuscript. OOD-17 is a small secondary case study. The original text refers to additional NMR/HRMS/IR spectra, an optimisation Table S1 and auxiliary Schemes S1–S2, which are not present as primary spectrum files in the current computational folder. Those chemical supplements must be supplied by the chemistry coauthors; their identifiers below are reserved separately as Table S10 and Schemes S5–S6.

To examine out-of-domain behaviour, we assembled an OOD test set of 17 newly synthesized QACs from previously unrepresented structural subtypes and measured them under independent assay conditions. This set is chemically held out from the training collections, but n = 17 makes all effect estimates imprecise. It is therefore used as a small descriptive case study rather than as decisive evidence of generalisation.


Figure S16. Molecular classes in the historical QAC, Q-HERO and OOD collections.

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

80.Cai, F.; Hanna, K.; Zhu, T.; et al. ChemFM as a scaling law guided foundation model pre-trained on informative chemicals. Communications Chemistry 2026, 9, 3 (published online 18 December 2025). https://doi.org/10.1038/s42004-025-01793-8.

81.Singh, R.; Barsainyan, A. A.; Irfan, R.; et al. ChemBERTa-3: an open source training framework for chemical foundation models. Digital Discovery 2026, 5, 662–685. https://doi.org/10.1039/D5DD00348B.

