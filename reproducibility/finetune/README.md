# Fine-tuning matrix

2x2 experiment: {frozen MolFormer, end-to-end fine-tuned} x {expert binary labels,
quantitative MIC}, with null baselines. Every evaluation molecule (QAC-105, Q-HERO,
OOD-17 — 532 structures) is held out of all three training sources.

| source | rows | molecules | task |
|---|---|---|---|
| `expert-binary` | 740 | 740 | Good/Bad |
| `quant-molecule` | 1153 | 1153 | log2 MIC, uM |
| `quant-record` | 9338 | 1153 | log2 MIC, uM |

## Run

```bash
python data_prep.py             # builds data/ (already done)
python run_matrix.py --seeds 3       # representation quality  (~2.2 h)
python direct_inference.py --seeds 3 # zero-shot inference     (~2.2 h)
./chain.sh                           # runs the second after the first
```

The two runs answer different questions:

| script | what the fine-tuned model is used for | head fitted on target? |
|---|---|---|
| `run_matrix.py` | feature extractor; a fresh CatBoost is fitted on target data | yes |
| `direct_inference.py` | the fine-tuned head predicts the target itself | **no** |

`direct_inference.py` is the zero-shot setting. The quantitative sources and all three
targets are log2 MIC in uM, so regression transfers directly; the expert head emits a
Good/Bad logit instead, so the two arms are compared on rank agreement with the true MIC
(Spearman, signed so positive is correct for both) and on ROC-AUC against MIC binarised
at the target's median.

## Watch it

```bash
python -m http.server 8765 --directory .
```

then open http://localhost:8765/dashboard.html — it polls `progress.json` every 3 s.

## Files

- `run_matrix.py` — the harness
- `data_prep.py` — builds the sources, holding out all evaluation molecules
- `progress.json` / `progress_direct.json` — live state (overwritten)
- `runs.jsonl` / `runs_direct.jsonl` — one line per finished evaluation (append-only)
- `train.log` / `direct.log` — stdout
- `checkpoints/` — fine-tuned weights, saved by `direct_inference.py`
- `data/` — prepared sources and evaluation targets

## Notes

- `PYTORCH_ENABLE_MPS_FALLBACK=1` must be set **before** torch is imported: MolFormer's
  linear attention calls `torch.linalg.qr`, which MPS does not implement.
- In training mode MolFormer redraws its random attention feature map on every forward
  pass in all 12 layers, so each forward is stochastic. Seeds are set per run.
- The bottom 4 encoder layers and the embeddings are frozen (16.0M of 44.4M parameters);
  early stopping is on a scaffold-disjoint 15% validation split.
