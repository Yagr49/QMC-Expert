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
python data_prep.py          # builds data/ (already done)
python run_matrix.py --seeds 3
python run_matrix.py --smoke # 1 seed, 2 epochs, ~7 min
```

## Watch it

```bash
python -m http.server 8765 --directory .
```

then open http://localhost:8765/dashboard.html — it polls `progress.json` every 3 s.

## Files

- `run_matrix.py` — the harness
- `data_prep.py` — builds the sources, holding out all evaluation molecules
- `progress.json` — live state (overwritten)
- `runs.jsonl` — one line per finished evaluation (append-only)
- `train.log` — stdout of the current run
- `data/` — prepared sources and evaluation targets

## Notes

- `PYTORCH_ENABLE_MPS_FALLBACK=1` must be set **before** torch is imported: MolFormer's
  linear attention calls `torch.linalg.qr`, which MPS does not implement.
- In training mode MolFormer redraws its random attention feature map on every forward
  pass in all 12 layers, so each forward is stochastic. Seeds are set per run.
- The bottom 4 encoder layers and the embeddings are frozen (16.0M of 44.4M parameters);
  early stopping is on a scaffold-disjoint 15% validation split.
