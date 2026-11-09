# Reproducibility audit — QMC-Expert

Audit of the manuscript *"Expert Judgement as Supervision"* against the artifacts in this
repository. This is a historical audit, not the latest matched results. Sections 4–7 were
clarified on 2026-10-11: corpus overlap and diagnostic re-runs do not establish that all
original metrics were computed incorrectly; the previously inferred OOD RMSE 2.27 is
withdrawn. See `revision_v14/METRIC_AUDIT_CLARIFICATION_RU.md`.

**Update, 2026-10-12:** dated April/May notebooks and their saved outputs have now been
recovered from VS Code history. The generating code for the bootstrap CSV is in the
May `causal_final.ipynb`; July `shap_causal_analysis.ipynb` explicitly prints the original
regression RMSE 2.133. See `notebook_recovery_20261012/README_RU.md` for provenance.
The original 2.13 has a saved-output source and must not be replaced by the different
May regression result simply because that experiment also has archived contrasts.

**Completed reproduction and article update, 2026-10-12:** all 30 matched partial
fine-tuning training runs were independently repeated. All 93 historical target
arrays and all 62 QAC-105/OOD-17 arrays reproduce byte-for-byte with the archived
encoding batch layout. Re-encoding with a changed batch composition perturbs
features around 1e-6 and changes some CatBoost predictions; replaying the original
layout with the independently trained models resolves this discrepancy. Cached
v14 cation and scaffold refits are exact. Some historical Mac-to-Linux MLP/context
branches remain unresolved environment sensitivities, and extreme Ridge outputs
remain unstable. See `server_models_20261012/analysis/RESULTS_RU.md` and the audit
JSON files; this is not a claim that every historical branch is now reproduced.

The current article is
`2026_10_12_Paper_2_edited-v16_finetuning_and_weight_interventions.docx`.
It retains the 913 completed graph/tabular fits and adds 363 direct-target
fine-tuning fits plus 1,331 decoder fits after encoder-weight controls. All
33 final-OOD target models were reloaded and reproduce their predictions.
The original five article tables, annotation fields and chemistry records
are preserved. Reverting human-guided weights increases cation-CV pooled
RMSE by 0.109 [0.037, 0.201] under the new conditional seed/scaffold interval
convention; scaffold/OOD intervals include zero. LoRA does not outperform
full fine-tuning in the tested cation-CV protocol. See
`server_finetune_causal_20261012/analysis/RESULTS_RU.md` and
`revision_v16/document_validation.json`. QAC-105/OOD-17 remains the
main evaluation. Historical recommendations about Q-HERO below are archival,
not the present study design. Notebook recovery locates generating code for
selected CKA/SHAP analyses; exact encoder/execution-state provenance for every
published attribution summary remains unresolved. Earlier statements that no
generating code is available should be read with this recovery update.

## 1. Size of the expert-labelled set

Source files: `2025-12-15_QACs SMILES_Final.xls` (ids 1–518) and
`2026-02-11_QACs SMILES_NF_MS_519-1103.xls` (ids 519–1103).

| | value |
|---|---|
| rows | **1103** |
| Bad / Good | 859 / 244 (22.1 % positive) |
| duplicate rows | 0 |

This matches `interpretability_results/embedding_analysis_full/run.log`
(`MoLFormer X: (1103, 768) | метки Good/Bad: {0: 859, 1: 244}`).
The manuscript said 1,500 in four places and 1,100 in one; corrected to 1,103.

**Class balance is not stated in the manuscript.** It explains the accuracy/F1 gap
(acc 0.856 vs F1 0.655) reported in §2.1 — a majority-class baseline already scores 0.779.

## 2. SMILES quality in the expert set

| | count |
|---|---|
| parse with RDKit as supplied | 997 / 1103 |
| **fail to parse** | **106 (9.6 %)** — 104 of them in batch B |
| recoverable by counterion repair (`[Br]-` → `[Br-]`) | 91 |
| still unparseable (truncated strings) | 15 |
| canonical duplicates | 22 |
| duplicates with **conflicting** expert labels | 1 (ids 235 / 337) |

The dominant failure is a systematic data-entry pattern: counterions written as
`.[Br]-.[Br]-` instead of `.[Br-].[Br-]`. MolFormer tokenises these strings without
validation, so the encoder was trained on ~10 % chemically malformed inputs.
`expert_labels/expert_labels_1103.csv` carries the repaired and canonicalised columns.

## 3. Annotation-round drift

| batch | n | Good-rate |
|---|---|---|
| A (2025-12-15) | 518 | **29.5 %** |
| B (2026-02-11) | 585 | **15.6 %** |

Nearly a two-fold shift between rounds. Either the chemical space or the labelling
threshold moved; the manuscript treats the 1103 as one homogeneous set.

Per-annotator votes are **not** in the files — only `Annotation_Final`. The claim of
"independent blind classification by three domain experts … resolved by majority"
therefore cannot be verified and no inter-rater agreement (Fleiss' κ) can be computed.

## 4. Dataset overlap (`leakage_check.py`)

|  | expert-1103 | QMR-quant | QAC-105 | Q-HERO | OOD-17 |
|---|---|---|---|---|---|
| **expert-1103** | 1066 | 1035 | **105** | 222 | 0 |
| **QMR-quant** | 1035 | 1515 | 99 | 255 | 0 |
| **QAC-105** | 105 | 99 | 105 | 1 | 0 |
| **Q-HERO** | 222 | 255 | 1 | 411 | 0 |
| **OOD-17** | 0 | 0 | 0 | 0 | 17 |

Two consequences:

* **All 105** molecules of the QAC-105 regression benchmark (Tables 1–2) are inside the
  expert-labelled corpus, and 99/105 are inside the quantitative corpus. This establishes
  source-corpus overlap, not the exact checkpoint training membership of every compound.
  The original evaluation does not demonstrate source-excluded transfer. The overlap is
  unequal across arms and cannot by itself validate their comparison. The reported R²
  values may still describe the historical evaluation protocol.
* **The 17-compound OOD set has no identical canonical full-salt overlap** with these
  corpora. That is a useful independence check, not sufficient validation of every OOD
  metric or claim. Censoring, scaffold coverage and the small sample also matter.

Also: 97 % of the expert set is inside the quantitative corpus. The two supervision
sources substantially share molecules. This should be disclosed, but does not by itself
make the historical experiment matched: source membership, training objective and
training budget also need control.

## 5. Out-of-domain RMSE

`analysis/ablation_bootstrap.csv` labels its contrast column `mean_delta_rmse`:

| pair | ∆ | 95 % CI |
|---|---|---|
| expert − MolFormer | −0.123 | [−0.277, +0.029] |
| regression − MolFormer | −0.037 | [−0.134, +0.065] |
| expert − regression | −0.086 | [−0.227, +0.054] |

**Correction, 2026-10-11:** the previous audit added these differences to the manuscript's
MolFormer RMSE 2.31 and inferred expert 2.19 / regression 2.27. The baseline's membership
in that exact experiment has not been established, and the generating predictions/code
for this bootstrap CSV have not been located. The inferred 2.27 is withdrawn; this file
alone does not prove that the original 2.13 is an arithmetic error. Nor does it establish
that the column actually contains MAE differences merely because another analysis uses
absolute residuals.

The separately regenerated `causal/ood_paired_residuals.csv` yields RMSE
2.108902 / 2.395987 / 2.291288 for expert / regression / raw features by directly taking
the square root of the mean squared residual. It comes from `causal_check.py`, with its
own five-decoder ensemble and censoring-at-bound convention, and is not an exact
reproduction of the original table. These artifacts must not be combined into a single
claimed correction. Primary v14 scores are independently computed from v14 predictions.

## 6. Re-run of Table 2 (`rebuild_table2*.py`)

CatBoost on the 108-compound biocide set, 432 (molecule, endpoint) pairs, mean R² over
10 seeds, multitask setting, MolFormer/expert/regression embeddings + MW + LogP:

**Split by pair — the protocol used in the notebook and the manuscript**

| embeddings | S.a. MIC | S.a. MBC | E.c. MIC | E.c. MBC |
|---|---|---|---|---|
| expert (Good/Bad) | 0.58 ± 0.24 | 0.51 ± 0.24 | 0.77 ± 0.08 | 0.63 ± 0.11 |
| multi-regression | 0.59 ± 0.27 | 0.51 ± 0.26 | 0.80 ± 0.06 | 0.62 ± 0.12 |
| MolFormer (raw) | 0.53 ± 0.28 | 0.51 ± 0.26 | 0.78 ± 0.06 | 0.63 ± 0.12 |

**Split by molecule — no molecule in both train and test**

| embeddings | S.a. MIC | S.a. MBC | E.c. MIC | E.c. MBC |
|---|---|---|---|---|
| expert (Good/Bad) | 0.27 ± 0.16 | 0.06 ± 0.27 | 0.09 ± 0.19 | 0.06 ± 0.27 |
| multi-regression | 0.31 ± 0.13 | 0.08 ± 0.22 | 0.16 ± 0.22 | 0.08 ± 0.26 |
| MolFormer (raw) | 0.19 ± 0.19 | 0.00 ± 0.30 | 0.12 ± 0.19 | 0.08 ± 0.22 |

Two observations:

1. **The three representations have close point estimates in this diagnostic re-run.**
   Their seed standard deviations alone do not establish equivalence or absence of
   benefit. This run also includes MW and LogP and omits text embeddings, so it cannot
   resolve every original model comparison or replace the matched v14 analysis.
2. **Pair and molecule splits test different tasks.** The same molecule supplies up to
   four rows with the same molecular representation, so a random split over pairs allows
   another endpoint from a test molecule into training. The higher scores then describe
   prediction of missing endpoints for partially observed molecules, rather than
   prediction for unseen molecules. The reported molecule split uses original row
   indices; duplicate structures can still cross it. Strict cation grouping is in v14.

This re-run omits the OpenAI class embeddings and does not tune CatBoost, so absolute
values are not expected to equal the published table. It is a diagnostic comparison of
splits, not an exact reproduction or a definitive representation ranking.

## 7. RMSE / R² inconsistency in Tables 1–2

For a fixed test set R² = 1 − RMSE²/Var, so Var = RMSE²/(1−R²) must be constant down a
column. It is not:

```
TABLE 2, implied Var(y_test):      S.a.MIC  S.a.MBC  E.c.MIC  E.c.MBC
  CB classified emb                   2.31     5.50     2.64     3.14
  MT CB (cls)                         2.86     2.51     3.01     4.49
  MT+enc CB (cls)                     3.39     2.26     2.26     4.35
  CB multireg emb                     1.84     4.34     2.36     2.64
```

The clearest case: for S. aureus MIC the classified embeddings go from 0.91 (R²=0.71) to
0.92 (R²=0.75). Higher RMSE and higher ordinary predictive R² cannot both occur on the
same fixed observations with the same weights. This flags a need to trace the test sets,
metric definitions, aggregation and transcription. The identity need not hold between
separately averaged RMSE and R² across different folds/seeds. The notebook contains
different plain-versus-multitask splits, but asserts shared indices for categorical
versus OpenAI coding; different splits therefore cannot be assumed to explain every
table discrepancy. Exact original per-row provenance remains incomplete.

## 8. Suspected bug in the few-shot scan

In `extended_ood/few_shot_scan/fewshot_reg_residuals_long.csv` the `llm_mol_cls` arm
returns **bit-identical RMSE for all three representations** at all nine training
fractions (2.291 / 1.682 / 1.624 / 1.503 / 1.592 / 1.803 / 1.634 / 2.113 / 1.214).
The molecular representation cannot be reaching the model in that branch.

Also: the test set shrinks from 61 residuals at 10 % to 7 at 90 %, so points on the
scaling curve are not on a common test set.

## 9. Encoder provenance

| artifact | trunk | projection head |
|---|---|---|
| `encoder_borderline_smote.pth` (expert) | 768→512→384→256 | 128 / 128 |
| `analysis/encoder_reg_only.pth` (ablation) | 768→512→384→256 | 128 / 128 |
| `encoder_256_final.pth` (used by `run.log`) | 768→512→384→256 | **256 / 256** |

The ablation pair is correctly matched, so §2.4's "differ in exactly one respect" holds
for it. But the interpretability run logged in
`interpretability_results/embedding_analysis_full/run.log` loaded `encoder_256_final.pth`
— a different training run from the encoder behind Tables 1–2 and the OOD results. The
script that produced `analysis/cka_probing.csv` is not in the repository, so which
encoder generated the published CKA/SHAP numbers cannot be confirmed.

`decomposition/shap_by_type.csv` reports a summed SHAP of **2.656** for the 256-dim
embedding block; the manuscript reports **0.64 [0.62, 0.65]** for the same block. The
source of the published value is not reproducible from the artifacts present.

## 10. Linear probing

`analysis/cka_probing.csv`: CKA 0.933 in-domain / 0.946 OOD — matches the manuscript.
Probing R² is 0.891 MolFormer→embedding but **0.844** in the reverse direction; "and vice
versa" overstated the second number. Corrected.

## Q-HERO as an external benchmark

`prepared_qhero.csv` holds 411 unique structures with a matched *S. aureus* MIC endpoint.
It overlaps QAC-105 by exactly **1** molecule, so it is a genuinely independent test set
for the regression task — the strongest available substitute for the contaminated
in-domain evaluation. It does overlap the expert set by 222 molecules, so an encoder
trained on the expert labels must be evaluated on the 189 Q-HERO molecules outside it.
