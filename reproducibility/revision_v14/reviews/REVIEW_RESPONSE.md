# Response to the authorised internal Kimi / Claude reviews

Both reviewers were actual external models, invoked from the local computer.
Prompts, completions and process metadata are retained. These are internal model
critiques, not human peer review or independent scientific certification.

## Implemented changes

- Post-hoc narrative selection is stated in the abstract, introduction and methods.
  The direction and magnitude of the demoted Q-HERO comparison are briefly given
  in the introduction; its entire prior analysis remains in SI.
- Historical overlapping-source encoders are isolated in SI provenance sections;
  main figures compare only the source-excluded matched representations.
- Cation holdout is labelled interpolation. All-four-task scaffold holdout was
  added on all 105 structures after protocol review; its timing is explicit.
- Both numerical real-versus-shuffled contrasts accompany the human contrast.
  The continuous-MIC real-label gain is not claimed to be uniquely human.
- Text embeddings are constant per task; pooling, dimensionality, task-partition
  geometry and semantic interpretation are distinguished. Opposite-direction raw
  OOD text effects are explicitly reported. No uniform-null claim is made.
- IT505's >500 endpoint is retained as a bound, with hinge-error lower bounds
  on its error and all-arm minimum-RMSE/MAE sensitivities. No bound is called exact.
- OOD sample/group limits, endpoint failures, task-median outcomes, individual
  predictions and leave-one-family-out score sensitivity remain visible.
- Annotation-method fields stay for coauthors per the author's instruction.
  Conclusions explicitly make the independent-human-information interpretation
  provisional pending information-access and adjudication records.
- Source training is specified as 377 equally weighted molecule examples in every
  arm; quantitative values are within-molecule medians of pooled log2 µM records.
  The 4,938 records are aggregated and do not become repeated gradient examples.
- Paired bootstrap mechanics and fixed decoder randomness are explicit; the
  borderline scaffold real-versus-shuffled interval is hypothesis-generating.

## Corrections to reviewer assertions

1. The initial manuscript already disclosed post-hoc selection in its abstract
   and introduction; Claude's assertion that both were absent was inaccurate.
   Chronology and earlier Q-HERO outcomes were nevertheless made more explicit.
2. Legacy rows exist in the complete machine-readable table, but primary figures
   never mix legacy and matched-source arms. Separate SI sections state provenance.
3. The OOD case comprises 67 exact endpoint values over 17 compounds (16 exact
   values only for Ec MBC), not 16 pooled pairs or 3–5 values per endpoint. The
   four families contain 3–5 compounds each and remain the resampling groups.
4. Text vectors need not act only as a task intercept: a tree can interact task
   selectors with molecular features. The defensible limitation is that four
   constant task vectors add no new compound data and cannot identify semantics.
5. Kimi's statement that 105 salts / 103 cations cannot yield five 21-salt grouped
   folds is mathematically incorrect. Folds 0/1 have 20 cations each and one paired
   salt identity; folds 2/3/4 have 21 cations. Both paired salts stay in one fold.
   Per-cation fold uniqueness is asserted in numerical validation, and the exact
   20/20/21/21/21 group counts are stated in Methods.
6. The source was already molecule-aggregated, so a hypothetical repeated-record
   weighting confound does not apply to the matched v12 training. Methods now
   state this explicitly.
7. Main OOD superiority was already disclaimed, including the instability of the
   four-family interval. Conditional negative intervals are descriptive rather
   than confirmatory. The endpoint failures and bound-aware sensitivity further
   strengthen that distinction.

## Optional work left outside the current claim

A random 1536-d task-code control, repeated decoder seeds, standardised endpoint
losses, more source seeds/permutations and a new blinded prospective chemical
panel would address different questions. They are not reported as completed.
No semantic text advantage, general adapter superiority, statistical equivalence
or biological causal mechanism is claimed. The coauthor provenance fields still
require real records before submission.
