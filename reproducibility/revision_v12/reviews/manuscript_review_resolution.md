# Kimi manuscript review resolution

1. Marginal distributions: corrected Methods to distinguish binary class counts
   from continuous empirical values, with source-training permutation specified.
2. Continuous-MIC differences: Conclusions explicitly state that matched
   continuous MIC has lower target-refit error and stronger direct ranking under
   exploratory unadjusted intervals; human-vs-binary and human-vs-raw remain
   unresolved.
3. Equivalence wording: Section 3.6 distinguishes the continuous-MIC difference
   from the unresolved binary comparison and states that no equivalence test or
   pre-specified margin is used.
4. Binary comparator in abstract: added mean RMSE 1.525 alongside human 1.529,
   continuous MIC 1.453 and fresh raw 1.607.

Additional consistency updates: the earlier statement that the strictest
controls use frozen features now includes both matched adaptation protocols.
Secondary human R² (QAC-104 −0.103; OOD-17 −0.118) and the negative mean R² of
all matched arms on both secondary collections are stated in Section 3.6.
The direct human real-vs-shuffled interval crossing zero is explicit. Frozen
lower layers means frozen parameters; stochastic feature-map buffers are
documented in the implementation note and reproducibility section.

Annotation access/provenance, exploratory multiplicity, five-seed/fixed-fold
inference, non-independent MolFormer checkpoints, modest direct ranking and
uncalibrated direct concentration predictions remain limits. Author fields are
intentional and unchanged. Kimi supplied internal criticism and did not replicate
experiments. Claude is not authenticated locally and was unavailable on the
provided servers; no Claude review is claimed.
