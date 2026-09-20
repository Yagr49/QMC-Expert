# QMC-Expert

Expert judgement as supervision for molecular representation learning of quaternary
ammonium biocides (QACs).

Code, data and experiment artifacts behind the manuscript *"Expert Judgement as
Supervision: Binary Human Labels Match Quantitative Measurements for Representation
Learning for Rational Design of Highly Efficient Biocides"*.

## What is here

| path | contents |
|---|---|
| `expert_labels/` | the expert Good/Bad annotation set, cleaned and canonicalised |
| `2025-12-15_QACs SMILES_Final.xls` | annotation batch A (ids 1–518), as delivered |
| `2026-02-11_QACs SMILES_NF_MS_519-1103.xls` | annotation batch B (ids 519–1103), as delivered |
| `reproducibility/` | audit scripts and `FINDINGS.md` |
| `analysis/`, `decomposition/`, `extended_ood/`, `interpretability_results/` | experiment outputs |
| `*.pth` | trained encoders and downstream models |
| `*.ipynb` | training / evaluation notebooks |

## Datasets

| dataset | n | role |
|---|---|---|
| expert Good/Bad | 1103 labelled compounds (859 Bad / 244 Good) | supervision for the contrastive encoder |
| QMR (QAC-AMR) | 13,404 activity records, 1,515 structures, 371 strains | quantitative supervision |
| QAC-105 | 105 compounds × 4 endpoints | in-domain regression benchmark |
| Q-HERO | 411 structures, matched *S. aureus* MIC | external benchmark |
| OOD-17 | 17 newly synthesised QACs | out-of-domain test set |

The quantitative corpus is published separately:
**QAC-AMR**, Zenodo, [10.5281/zenodo.22286669](https://doi.org/10.5281/zenodo.22286669) (CC BY 4.0).

## Read this first

`reproducibility/FINDINGS.md` documents an audit of the manuscript against these
artifacts. It records, among other things, that all 105 molecules of the in-domain
regression benchmark are inside the expert-labelled training set, that ~10 % of the
expert SMILES needed repair before they parse, and that on that benchmark the expert
embeddings, the regression embeddings and raw MolFormer are statistically
indistinguishable. The 17-compound out-of-domain set is free of overlap and is where the
claims are supported.

## Credentials

Nothing in this repository should contain an API key. The OpenRouter client reads
`OPENROUTER_API_KEY` from the environment:

```bash
export OPENROUTER_API_KEY="..."
```

## Requirements

```
pandas numpy scikit-learn catboost torch rdkit openpyxl xlrd shap econml openai
```
