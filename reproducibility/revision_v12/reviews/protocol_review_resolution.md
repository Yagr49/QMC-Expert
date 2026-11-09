# Kimi protocol review resolution

- Leakage, shared initialisation/batches/updates, train-only transformations and permutation, and direct/refit orientations: confirmed by the read-only review; numerical audits are separately required.
- Native stochastic feature-map refresh: documented in the preserved implementation note and corrected manuscript wording; training behaviour and original outcomes are unchanged.
- Replay epochs: corrected to use the recorded manifest epoch count and batch size, with per-checkpoint consistency assertions. The original reconstruction script is retained in protocol_history/reconstruct_checkpoints_v1.py. The five-seed experiment remains exactly 30 epochs.
- Original parameter-only checkpoints: preserved. New checkpoints contain trained parameters plus final persistent buffers; restore frozen parameters from the pinned pretrained base. Once these verified reconstruction files exist, loading them does not require RNG replay.
- GPU determinism warn_only: no universal bitwise portability is claimed. One same-environment human seed is independently retrained as a further check.
- Cation normalisation: already audited upstream in revision_v9/revision_v10; source-target scaffold overlap is explicitly allowed.
- Target-median AUC: secondary descriptive metric. Fixed-fold bootstrap, small OOD and five-seed limits remain explicit.

The review did not inspect outcomes and is a methodological critique, not an independent replication.
