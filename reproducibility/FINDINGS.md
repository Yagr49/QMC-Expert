# Reproducibility audit — QMC-Expert

Audit of the manuscript *"Expert Judgement as Supervision"* against the artifacts in this
repository. Every number below is produced by a script in `reproducibility/`.

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
  expert-labelled training set, and 99/105 are inside the quantitative corpus. Both
  encoders saw every test molecule during representation learning. Tables 1–2 are
  in-domain and contaminated **for both arms symmetrically**, so the *comparison*
  survives but the absolute R² values do not.
* **The 17-compound OOD set is clean** (zero overlap with everything). §2.3–2.4 are the
  trustworthy part of the paper and should carry the headline claim.

Also: 97 % of the expert set is inside the quantitative corpus. The two supervision
sources are not independent collections — they are coarse vs fine labels on the *same*
molecules. That is a cleaner controlled experiment than the manuscript describes and
should be stated as such.

## 5. Out-of-domain RMSE

`analysis/ablation_bootstrap.csv` (paired bootstrap, ∆RMSE):

| pair | ∆ | 95 % CI |
|---|---|---|
| expert − MolFormer | −0.123 | [−0.277, +0.029] |
| regression − MolFormer | −0.037 | [−0.134, +0.065] |
| expert − regression | −0.086 | [−0.227, +0.054] |

With MolFormer = 2.31 these give expert = **2.19** and regression = **2.27**.
The manuscript printed 2.13 for the regression encoder, which both contradicts the
bootstrap file and inverts the sign of the effect the surrounding sentence describes.
Corrected to 2.27 in the revised manuscript.

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

1. **The three representations are indistinguishable.** Every difference is far inside one
   standard deviation across seeds. The paper's claim "expert labels ≍ quantitative
   labels" reproduces — but *raw MolFormer matches both*, which the paper does not report
   for this benchmark. On QAC-105 the contrastive encoder adds nothing measurable; the
   evidence that it adds a "biological component" rests on the OOD set alone.
2. **Splitting by pair inflates every number.** The same molecule supplies up to four rows
   with an identical feature vector, so a random split over pairs puts it in train and
   test at once. Moving to a molecule-level split roughly halves R².

This re-run omits the OpenAI class embeddings and does not tune CatBoost, so absolute
values are not expected to equal the published table; the *relative* ordering is the
point.

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
0.92 (R²=0.75) — higher RMSE *and* higher R² on the same endpoint, which cannot happen on
a common test set. The plain rows and the multitask rows come from different pipelines
and different splits; the table presents them as comparable.

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
