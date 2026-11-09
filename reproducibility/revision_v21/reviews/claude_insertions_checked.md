# Checked English additions for v5 — do not replace author prose

The actual Claude Sonnet4.6 response is in `claude_review.txt`. The text below incorporates its numerical audit and corrects its overbroad framing. Root can insert these paragraphs with yellow highlighting. Section 2.2 is unchanged.

## Introduction — three optional consecutive paragraphs

Pre-trained molecular models offer a reusable description of chemical structure, but adapting that description to a small antibacterial dataset still requires two choices: which information should guide the representation, and which parts of the prediction pipeline should be trained. Full backbone fine-tuning, low-rank updates inside transformer layers and an external feature encoder make different use of the available supervision. Their relative performance must therefore be tested under the intended validation regime, rather than inferred from the number of trainable parameters alone.

Our approach separates representation guidance from quantitative decoding. Frozen MolFormer first maps each molecular structure to a 768-dimensional vector. A compact external neural encoder then learns a 256-dimensional representation from expert Good/Bad judgements, while CatBoost learns the quantitative relationship between that representation and the MIC/MBC endpoints. Human labels guide source training; a new molecule does not require a human label when its representation or predicted activity is computed. This separation provides a concrete way to examine whether coarse expert supervision can organise useful molecular features for a distinct quantitative task.

We also test whether a frozen representation followed by a decoder is preferable to direct backbone adaptation in this setting. The completed follow-up compares frozen prediction heads, LoRA and full fine-tuning, and evaluates both prediction routes from human-guided partial-backbone initialisation. Full fine-tuning improves cation-holdout prediction in the tested procedure but has higher error on the independently measured OOD compounds; freezing the human-guided partial-backbone representation and fitting CatBoost gives lower OOD error than direct prediction from the same source initialisations. These results motivate a conditional choice of prediction route, rather than a general claim that fine-tuning is harmful or that a smaller adapter is necessarily superior.

## Section 2.1 — four short paragraphs, append near Figure 2

The reference encoder operates outside MolFormer. For a SMILES string s, the frozen backbone produces h₀ = fθ(s) ∈ R⁷⁶⁸, and the external MLP produces z = gψ(h₀) ∈ R²⁵⁶ through layers of width 512, 384 and 256. Expert labels train ψ without updating θ. A subsequent decoder predicts quantitative MIC/MBC from z and a task code. This feature adapter is distinct from LoRA updates inside the transformer and from partial or full backbone fine-tuning.

In a separate completed backbone experiment, direct full fine-tuning gave cation/scaffold RMSE 1.863 ± 0.045/1.970 ± 0.026, but OOD RMSE 3.032 ± 0.408. Direct LoRA gave OOD RMSE 2.756 ± 0.172, while a frozen pretrained backbone with a linear head gave 2.560 ± 0.206. These results demonstrate that improved grouped-validation performance need not produce lower error on the new chemical families under the tested optimisation budget.

Using the same three human-guided partial-backbone source checkpoints, direct target prediction gave OOD RMSE 2.412 ± 0.088, compared with 2.106 ± 0.071 when the source representation was frozen and decoded with CatBoost. The latter route gave cation/scaffold RMSE 1.743 ± 0.031/1.819 ± 0.044. These human-guided backbones are separate follow-up models, not the external compact encoder described above. All values use log₂(mg/L);  ±  denotes sample SD across three complete paired runs, not CV-fold SD or a 95% confidence interval. OOD scores include 67 exact endpoints, with the remaining bound retained separately.

The route comparison changes adaptation and decoding together and therefore does not isolate a causal effect of human-label meaning. Matched label-shuffling controls are assessed separately; the five-run compact-encoder experiment does not resolve an advantage of real human labels over shuffled labels. We consequently interpret the route results as evidence about the stated prediction procedures, without attributing them to a uniquely human semantic mechanism.

## Checks and corrections applied to Claude draft

- Removed unsupported blanket statement that cross-validation routinely overstates OOD accuracy and unmeasured charge-geometry explanation.
- Pretrained frozen/LoRA/full branches use three target seeds; only the two human routes share source checkpoints 0–2. Do not call every branch identically source-trained.
- Frozen human route RMSE 2.106 belongs to partial-backbone guidance, not v5 external MLP. The stronger OOD point estimate cannot establish that the external compact architecture beats full fine-tuning.
- Direct target fine-tuning updates the source-initialised backbone; the CatBoost route freezes its source state. They start from matched source checkpoints but are not the same final trained representation.
- Whole-run sampleSD is not foldSD/95% CI. Four target endpoints and67 exact OOD values are explicit.
- Human-vs-shuffle compact null remains explicit; no biological causality, universal FT failure or guaranteed advantage of fewer parameters.
- Tiihonen results and new Q-HERO classification are not inserted here; Section 2.2 remains for discussion.
