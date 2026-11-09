# Additional all-endpoint scaffold sensitivity

Added after examining the cation-held-out QAC-105 and OOD-17 extension. This is
an exploratory follow-up requested by independent protocol reviewers, not a
pre-registered independent replication. Retain all 105 original salts, duplicate
handling, units, encoders, decoder hyperparameters and one-hot task encoding.
Reassign QAC folds with deterministic five-fold GroupKFold on the 29 canonical
cation Murcko scaffolds rather than the 103 cation identities. Compare the raw
reference and all six matched source arms with all five paired source seeds.
Every task of every scaffold remains in a single fold. No OOD data enters fitting.
OOD predictions are identical in design to the preceding full-QAC fit and are
recomputed only as a consistency check. Existing results are immutable.
