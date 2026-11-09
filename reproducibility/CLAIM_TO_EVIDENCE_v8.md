# Claim-to-evidence audit — v8

This map records the strongest permitted formulation for each central claim.  Paths
are repository-relative and values were checked against the listed artifacts.

| Claim allowed in v8 | Evidence | Qualification / claim not allowed |
|---|---|---|
| Partial fine-tuning improves the mean result relative to frozen MolFormer in the evaluated matrix. | `finetune/runs.jsonl`; mean R²: frozen `−0.105/+0.134/−0.289`; expert `+0.053/+0.269/−0.174`; quant-molecule `−0.004/+0.312/−0.191`; quant-record `+0.048/+0.308/−0.027` on QAC-105/Q-HERO/OOD-17. | Do not call it end-to-end; 16.0/44.4 M parameters are frozen. Absolute performance is modest and OOD-17 has `n=17`. |
| Expert final labels yield downstream representation quality comparable to quantitative supervision in this protocol. | Same `runs.jsonl`; on Q-HERO expert `+0.269`, quant-molecule `+0.312`, quant-record `+0.308`; three seeds. | No pre-specified non-inferiority/equivalence margin or test. Do not claim equivalence of individual labels or a universal exchange rate. |
| Quantitative supervision transfers more strongly for direct zero-shot ranking. | `finetune/runs_direct.jsonl`; Q-HERO rank agreement: expert `+0.397`, quant-molecule `+0.547`, quant-record `+0.612`; OOD-17: `+0.295/+0.619/+0.752`. | OOD-17 estimate has high variation and `n=17`. Direct R² is negative and does not predict calibrated MIC. |
| Expert labels carry potency-related signal without observing concentration. | `runs_direct.jsonl`; expert direct rank agreement `+0.221/+0.397/+0.295`, AUC `0.644/0.688/0.597`. | It is a rank signal, not an absolute MIC prediction. |
| Direct quantitative predictions have a substantial scale mismatch. | `finetune/recalibration.csv`; mean raw/recalibrated R² for record model: Q-HERO `−1.62/+0.36`, OOD-17 `−2.92/+0.49`; mean slopes `0.47/0.98`. | The affine map is fit and evaluated on the same target predictions. It is exploratory, in-sample, and not generalisable calibration evidence. |
| The Q-HERO violin plot shows near-identical residual distributions. | `figures/figS3_qhero_violins.{png,svg,pdf}`; `qhero/qhero_residuals.csv`; SI Figure S3. | It does not show a clear expert advantage; medians are close to raw MolFormer. |
| The expert and quantitative supervision comparison is controlled on related chemical space. | `FINDINGS.md`, §4; expert/QMR overlap `1035` canonical molecules; 97% of expert set falls within the quantitative corpus. | It is not a comparison of independent datasets. |
| QAC-105 historical absolute metrics are not primary external-validation evidence. | `FINDINGS.md`, §§4, 6–7; 105/105 QAC-105 molecules overlap expert labels and pair-level splitting causes molecule leakage. | Do not headline absolute R² from historical Table 2. |
| Q-HERO is the stronger external benchmark available here. | `FINDINGS.md`, Q-HERO section; 411 structures, one QAC-105 overlap; `qhero/qhero_metrics.csv`. | The expert encoder historically saw 222 Q-HERO molecules; use the unseen-expert subset when assessing that frozen-encoder analysis. |
| There is no auditable individual-vote agreement statistic. | `FINDINGS.md`, §3; only final `Annotation_Final` labels are present. | Do not state that independent three-expert majority voting was verified or report Fleiss’ κ. |
| CKA/SHAP can be described as archived, hypothesis-generating analyses only. | `FINDINGS.md`, §9–10; generating CKA script missing and SHAP aggregate differs (`2.656` in decomposition file vs `0.64` in manuscript). | Do not use SHAP for a reproducible causal decomposition or numerical mechanistic claim. |
| OOD ablation shows no resolved mean difference in this small case study. | `analysis/ablation_bootstrap.csv`; expert−regression ΔRMSE `−0.086`, 95% CI `[−0.227,+0.054]`; expert/regression RMSE `2.19/2.27`. | This is not proof of statistical equivalence. A margin was not pre-specified and the test has 17 compounds. |

## Required pre-submission checks

1. Perform a targeted literature search before retaining any “first”, “none has asked”,
   or priority claim.
2. If possible, recover original individual annotation records; otherwise retain the
   final-label-only limitation.
3. Run a target-held-out calibration experiment before making calibration claims.
4. Rebuild CKA/SHAP from a pinned encoder checkpoint and archived script, or omit them.
5. Regenerate a fixed-test molecule-grouped few-shot analysis before discussing few-shot
   performance.
