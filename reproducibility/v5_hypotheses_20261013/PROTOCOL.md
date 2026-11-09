# Checks anchored to v5 — 13 October 2026

The v5 manuscript, its original compact-encoder method, reported Tables 1–2,
chemistry, named OOD collection and stored notebook outputs define the starting
point. Existing v14–v17 experiments test follow-up questions; they are not relabelled
as reproductions of v5. This protocol is exploratory and follows all earlier results.

H1: preserve and reconstruct the original performance. Load the archived human
encoder and scaler, use the original 108 worksheet rows, decoder 500/depth6/.05/42
and stratified 80/20 molecule–task row split. Report every prediction. The old
OpenAI cache is absent: the existing reconstructed cell-8 task vectors are used,
explicitly different from the cell-17 descriptions behind some saved outputs.
Matching an old number is not a selection criterion. These are approximate
reconstructions, and source-corpus overlap is disclosed.

H2: check validation demands using the same saved representations and decoder.
Retain the full 105 salts, five cation/scaffold folds and all 17 named OOD molecules.
Categorical task ID, four one-hot indicators, reconstructed text and separate
endpoint decoders are compared. Never use OOD for fitting or parameter selection.

H3: check supervision in the v5 compact architecture. Reuse the common 681-molecule
source panel, 377 training/304 validation, exclusion of evaluation cations and
five paired seeds. Train 768→512→384→256 encoder and 128-dimensional contrastive
projection. Human/binary-MIC use the recovered hard-negative objective; continuous
MIC uses source-training-standardised MSE. Include three shuffled controls.
All source batches, initial states and final 80-epoch budgets are paired; no SMOTE,
noise augmentation or early stopping in this controlled follow-up. It tests the
v5 architecture with declared changes, not exact historical source retraining.

H4: representation versus semantics. Compare categorical/one-hot/text task codes,
and for source seed 0 also random unit-normalised 1536-d codes and a fixed
permutation of the text codes. Four codes are fixed before target outcomes.
They test encoding-dependent prediction, not independent language understanding.

H5: parameter/buffer contributions. Compare intact compact encoders with their
identical untrained initial state; human controls also restore encoder parameters
while retaining learned BatchNorm buffers. A full initial-state restore removes
both weights and buffers. Distinguish geometry/CKA/probing from predictive loss.

H6: decoder/model dependence. Apply the already defined TabPFN-V2, TabFM and
AutoGluon budgets to archived v5 human/raw features on the same target folds.
Chemprop and RDKit are independent structural references from the completed
comparison. Prior direct-target full/partial/LoRA runs are procedure comparisons;
different source chemistry or capacity is not labelled a pure architecture effect.

Units: log2(mg/L). Score 420 exact QAC endpoints and 67 exact OOD endpoints.
IT505 E. coli MBC >500 mg/L remains a bound, with separate minimum-error
sensitivity. Do not replace it by an exact 500. Paired intervals resample whole
scaffold groups and paired source seeds; four OOD families limit interpretation.

The saved QAC-binned activity-only encoder is not the unlocated checkpoint trained
on the larger quantitative corpus in original Table 2. Keep these provenance
branches distinct. Human collection fields H1–H7/C1 remain for coauthors.

All API/model-review calls execute only on the Mac. Server payloads contain no
credentials or API calls. New outputs use separate directories; prior artifacts
are read-only inputs. Failed and unfavourable results are retained.
