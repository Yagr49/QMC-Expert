# Original QAC-105 and named OOD-17: exploratory narrative revision

Written before this extension's predictions. Earlier QAC/OOD outcomes and v5 were
already inspected. Cohorts, figures and narrative were selected after those
analyses; this is an exploratory extension, not a preregistered confirmation.
Q-HERO is retained as an archived sensitivity study in Supporting Information.
No assertion that its measurements are erroneous is made.

## Cohorts and units

Retain all 105 canonical full-salt structures from the original 108-row workbook.
Use the previously prepared median endpoints for duplicate identities, including
one flagged conflicting duplicate. Identify it explicitly. The strict 104-molecule
analysis and original duplicate records remain a curation sensitivity.
Retain all 17 named OOD compounds (four cation-scaffold families). No OOD value is
used for model fitting, tuning or encoding selection. Four tasks: S. aureus ATCC
43300 MIC/MBC and E. coli ATCC 25922 MIC/MBC. Targets are log2 concentration in
mg/L, matching the original v5 endpoint definition. Do not mix these errors with
previous log2-micromolar results. OOD IT505 E. coli MBC is right-censored (>500
mg/L); exclude it from exact-value RMSE/R2, retain the molecule and report its
bound and prediction separately. All other OOD values are used as supplied.

## Representations and supervision

Primary matched-source representations reuse the completed v12 experiment:
681 shared molecules; strict exclusion of all evaluation cations and salts;
377 training/304 validation; five paired source seeds; human, continuous MIC,
binary MIC, and each corresponding shuffled-label control. Fixed final 30-epoch
partial MolFormer fine-tuning, common initial weights/batches/updates within seed.
Recover the omitted conflicting target's vectors from the audited reconstructed
checkpoints; verify reference molecules against saved vectors before use.
No upstream training or checkpoint selection occurs in this extension.

Historical 256-dimensional human and quantitative encoders plus their 768-d raw
features are secondary descriptive reconstructions. They had source/target overlap
on the original collection and cannot identify out-of-source supervision benefits.
Historical raw and freshly encoded raw features are distinct references.

## Decoder and task encoding

Fixed CatBoost: 300 iterations, depth 5, learning rate .05, seed 1729, two threads.
No additional hand-selected molecular descriptors or target-based tuning.
Task encodings: (1) four independent endpoint models, matching the meaningful
single-task interpretation of no task metadata; (2) a shared model with species
and MIC/MBC one-hot (four indicators); (3) a shared model with 1536-dimensional
OpenAI text-embedding-3-small vectors for four fixed archived task descriptions.
Text describes only strain and endpoint, without compounds or target values.
It is reconstructed on the local computer via OpenRouter and cached with hashes.
No claim of a generative GPT predicting MIC is made.

Primary matched arms and fresh raw use one-hot. Human/continuous/binary arms
(all five seeds) and fresh raw additionally use text encoding. Historical three
representations use all three encodings as a limited reconstruction of the v5
comparison, without claiming to reproduce its exact hyperparameters or split.

## Validation

Five fixed GroupKFold folds group all salts of each canonical cation. All four
endpoints of a compound remain in one fold. Fold assignment uses identities only,
not measured targets. Produce one out-of-fold prediction per QAC task/structure.
Fit a final decoder on all QAC-105 data only to predict the named OOD-17.
The same folds and endpoint rows are used for every representation/encoding.
Existing strict scaffold-CV QAC-104 outcomes remain a separate pre-existing
transfer sensitivity. Ordinary cation-held-out CV allows scaffold overlap.
Save every prediction, fold membership, censoring qualifier, input hash, and
per-seed R2/RMSE/MAE/Spearman rank. Display seed means rather than metrics of an
ensemble mean. Baseline predicts each task's training-fold median (full QAC median
for OOD); negative R2 remains visible.

Exploratory matched contrasts resample source seeds and entire cation-scaffold
groups, retaining fixed predictions and identical paired rows. Use 10,000 draws
and 95% percentile intervals. OOD has only four groups; intervals are unstable
and do not imply confirmatory inference. No equivalence margin or measurement
exchange rate is inferred. A binary source logit is not a concentration.
Human annotation collection fields H1-H7 remain for coauthors. Biological
causality, independent intuition and human denoising are not identified.
