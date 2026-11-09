# Implementation clarification during the run, 2026-10-11

The original PROTOCOL.md remains immutable and its checksum remains in the run
manifest. Inspection of the pinned MolFormer implementation during execution
identified an imprecise description and a checkpoint-storage limitation:

* `deterministic_eval=True` fixes attention feature maps **in evaluation**. Native
  MolFormer refreshes the random orthogonal feature-map buffers on each training
  forward pass even when the deterministic flag is true. The actual experiment
  retains this native stochastic training behaviour; paired seeds and identical
  forward-call/minibatch schedules match the draws across supervision arms.
  No model behaviour, optimisation setting, dataset or evaluation rule is changed.
* The original saved checkpoints contain trainable parameters and source-target
  transforms, but omit the final refreshed feature-map buffers. They remain as
  originally written, with their original hashes. A separate reconstruction step
  replays the paired training-forward RNG schedule, records final persistent
  buffers and writes complete reconstruction checkpoints to another directory.
  Each reconstruction must reproduce saved target embeddings and direct scores
  before being accepted. Its checksums and discrepancies are archived separately.

Manuscript descriptions use the verified distinction between stochastic training
and deterministic evaluation. The reconstruction script changes storage, not
training, predictions or reported metrics. The original checkpoint and prediction
files are never overwritten. This note is an implementation audit, not a
post-outcome change to a scientific hypothesis or hyperparameter choice.
