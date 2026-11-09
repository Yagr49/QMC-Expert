# Scientific revision v8 — changelog

Base document: `2026_07_09_Paper_2_edited-v7_finetuning.docx` (unchanged).

Outputs created by `build_v8_submission.py`:

- `2026_07_09_Paper_2_edited-v8_scientifically_revised.docx`
- `Supplementary_Information_v8_scientifically_revised.docx`
- `Supplementary_Information_v8_scientifically_revised.html`

## Central claim

The v8 claim is deliberately narrower: **final binary expert supervision produced
representation quality comparable to quantitative MIC supervision under the evaluated
downstream-refitting protocol.** It does not claim that an individual binary label is
equivalent to an MIC measurement, that 740 labels replace 9,338 independent compounds,
or that a pre-specified non-inferiority/equivalence criterion was met.

## Corrections applied

- Populated the previously empty Abstract with a bounded, number-checked summary and
  updated the keywords.
- Repaired the static contents page and Methods hierarchy: 4.1 computational protocol,
  4.2 chemistry, and 4.3 microbiological assay.
- Replaced “end-to-end fine-tuning” with **partial fine-tuning**.  The embedding layer
  and four lower encoder layers remained frozen: 16.0 M of 44.4 M parameters.
- Everywhere distinguished **9,338 MIC records** from **1,153 unique molecules**.
- Added that expert and quantitative collections have substantial molecule-level overlap:
  this makes their comparison controlled, not independent.
- Corrected the null-baseline statement: the six-descriptor baseline has Q-HERO
  R² = **+0.057**, so both baselines are not non-positive throughout.
- Recast partial-fine-tuning results as comparable downstream representation quality,
  with seed variation reported, rather than as label equivalence or a numerical
  label-to-measurement exchange rate.
- Made the direct-transfer result explicit: quantitative supervision is stronger for
  zero-shot ranking on Q-HERO and OOD-17; raw direct R² is negative.
- Reclassified affine recalibration as **exploratory and in-sample**.  It is no longer
  presented as evidence of generalisable target calibration or as proof that calibration
  is the sole source of error.
- Marked OOD-17 as a small (`n = 17`) case study throughout.
- Replaced the historical majority-vote description with the auditable fact: final labels
  are available, individual expert votes and adjudication records are not.
- Removed claims of statistical equivalence from the text and conclusion.  The historical
  TOST figure remains in SI as an explicitly exploratory transparency item.
- Removed SHAP-based causal/mechanistic interpretation because the published aggregate
  cannot be reproduced from the archived decomposition file and the generating pipeline
  is incomplete.
- Removed the main-text historical architecture table whose RMSE/R² pairs came from
  incompatible pipelines and splits. Replaced the central in-domain comparison with an
  audited molecule-grouped Table 2 (10 seeds) that includes raw MolFormer.
- Removed stale internal-SI figure citations, corrected the main-text cross-reference to
  Tables S2–S4, and removed main Figures 3 and 5: Figure 3 carried heterogeneous,
  non-comparable annotations and Figure 5 depended on the known-bug few-shot scan.
- Retained the Q-HERO violin plot and changed its interpretation to the one supported by
  the figure: near-identical residual distributions, not a decisive expert advantage.
- Added an explicit computational-provenance and limitations subsection to the manuscript.
- Made the submission SI self-contained with four numerical tables (collection overlap,
  full fine-tuning matrix, direct ranking/AUC, and in-sample recalibration) and new v8
  variants of Figures S7–S9; original figures remain untouched.

## Deliberately not resolved in v8

- Priority/novelty assertions need an external literature search before submission.
- Individual annotation votes are not recoverable from the current repository.
- A fixed-test, molecule-grouped few-shot rerun is needed before any few-shot claim.
- Calibration needs a target-held-out or nested validation protocol.
- CKA and SHAP need a versioned, rerunnable source pipeline.
