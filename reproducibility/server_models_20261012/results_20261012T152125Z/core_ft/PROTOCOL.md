# Matched partial MolFormer fine-tuning

Written before this experiment's training and outcomes. This is an exploratory
extension of inspected v9–v11 results, not a confirmatory preregistration.

## Intervention and fixed conditions

Use the archived matched-pooled panel: 681 molecules, 111 cation-scaffold groups,
96 final human Good calls and 4,938 underlying MIC records. Use identical ordered
canonical full-salt SMILES, cations and scaffolds for every supervision arm.
Exclude every evaluation cation, including counterion variants, from source
training and validation. Source and target scaffolds may overlap; the source
validation split and the individual target CV folds are scaffold-disjoint.

Reuse GroupShuffleSplit(test_size=0.15, random_state=1729), yielding 377 training
and 304 validation molecules. Validation is diagnostic, without early stopping,
checkpoint selection or hyperparameter selection. Do not train on its labels.
Reuse v10 target_folds.csv exactly: QAC-104 and Q-HERO-405 scaffold 5-fold CV;
OOD-17 uses a decoder trained on QAC-104. Target MIC enters only the training
fold of a refitted decoder, never source representation training.

Load ibm/MoLFormer-XL-both-10pct at revision
7b12d946c181a37f6012b9dc3b002275de070314 with its pinned custom code. Retain the
768-dimensional pooled representation and scalar linear head with dropout 0.1.
Freeze embeddings and encoder layers 0–3; train layers 4–11, the pooler and
scalar head. This is partial backbone fine-tuning, not full fine-tuning, LoRA or
the frozen-feature MLP. Record actual trainable parameter counts and names.
Use float32, deterministic feature maps, right padding to 202 tokens, and audit
all source/target lengths without truncation before fitting.

Six arms: human binary; continuous pooled log2 MIC; binary pooled MIC;
shuffled human; shuffled continuous MIC; shuffled binary MIC. Binary MIC cutoff
is the source-training MIC quantile corresponding to human training-positive
prevalence; ties can change actual prevalence. Standardise continuous targets
using only source training (population SD), invert scaling for direct predictions.
Shuffle source-training labels only using RNG 100000 + seed, preserving their
multiset. Keep diagnostic validation labels unshuffled.

Five paired seeds 0–4. Within each seed, match backbone/scalar-head initial
weights, minibatch permutations and stochastic seed across all six arms.
AdamW lr 3e-5, weight decay 0.01; OneCycleLR maximum lr 3e-5, pct_start 0.1;
batch size 32, gradient norm clip 1, 30 fixed epochs = 360 updates per arm.
Use the final checkpoint. These matched budgets do not imply equally optimal
hyperparameters for different objectives. Record all epoch losses, update counts,
initialisation and minibatch hashes, transformed-label hashes, checkpoint hashes,
dependencies, model revision and input/fold checksums.

## Evaluation and controls

Primary: Q-HERO-405 RMSE (log2 micromolar) with the same CatBoost decoder as
v9/v10: 300 iterations, depth 5, lr 0.05, seed 1729, four CPU threads. Secondary
R², QAC-104 and OOD-17. Compare real human vs shuffled human, human vs raw
pretrained features, human vs continuous MIC, and human vs binary MIC. Include
quantitative real-vs-shuffled and quantitative-vs-raw contrasts. Raw MolFormer is
re-encoded in this environment and audited against archived features; retain both
raw predictions if numerical differences are material. Also compare to the
archived five-seed frozen-feature MLP on the same panel/folds, clearly identifying
the different architecture and training schedule.

Complementary direct transfer: keep each source-trained scalar head; no target
fitting or recalibration. Report rank agreement with target log2 MIC (negative
Spearman for Good logits, positive for numerical predictions), and target-median
AUC as a secondary descriptive metric. Report raw R²/RMSE only for continuous
MIC heads. Shuffled heads supply direct-transfer null controls. An untrained
scalar head is not an activity predictor and has no meaningful concentration
calibration; the raw representation is the downstream reference.

Paired RMSE differences: 10,000 nested seed/scaffold bootstrap draws with RNG
1729, resampling the same seeds and whole target scaffold groups in both arms.
Retain fixed target folds. Repeat scaffold-only intervals and leave-one-scaffold
contrasts as sensitivities. For raw predictions reuse the same prediction vector
in each paired seed draw. Direct rank differences use paired seed/scaffold
bootstrap with 10,000 draws. Intervals are exploratory, unadjusted and conditional
on this dataset, fixed folds and five training seeds. They do not establish
non-inferiority, equivalence, a molecular mechanism or human denoising.

## Operational separation

Smoke checks use a separate directory and one epoch; they verify execution and
matching, and are not part of the scientific result. The final protocol remains
fixed after the smoke check. A task-scoped dependency directory and model cache
protect existing server environments. Store checkpoints on the provided server,
download predictions, diagnostics, metadata and representations for local audit.
Do not modify unrelated services or datasets. Preserve v9–v11 drafts and results,
including their coauthor annotation-method fields.
