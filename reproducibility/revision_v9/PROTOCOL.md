# Exploratory controlled supervision experiment (v9)

Protocol fixed on 11 October 2026 before inspecting its new prediction results.
It follows earlier exploratory experiments; this is not a preregistered trial.

Primary outcome: paired difference in scaffold-held-out Q-HERO-405 RMSE,
in log2 micromolar S. aureus MIC. QAC-104 and OOD-17 are secondary.
Source-split variation and molecular-sample uncertainty are different quantities.

1. Remove the conflicting expert structure. Canonicalise full salts and cations.
   Remove every evaluation cation, including counterion variants, from all sources.
   Drop the archived target/Q-HERO label-conflict rows. Preserve the original v8 data.
2. Build two common-molecule panels: expert vs median pooled MIC, and expert vs
   median exact S. aureus MIC. The former aggregates organisms/strains deliberately;
   the latter requires aureus and a non-censored MIC qualifier.
3. On each panel use exactly the same molecules, frozen MolFormer inputs,
   source scaffold split (seed 1729), input scaler and paired initial weights.
   A 768→256→128 encoder plus linear source head is trained for 80 epochs,
   batch 64, AdamW lr 0.001, weight decay 0.01. All arms get the same minibatch
   ordering for a given seed. Continuous labels are standardised on source train only.
   Five initialisation seeds are 0–4. Source validation is diagnostic; it does not
   select a checkpoint or hyperparameters.
4. Arms: real expert labels, continuous quantitative MIC, MIC binary labels
   with a threshold set using source-training MIC and expert positive prevalence,
   shuffled expert labels, shuffled continuous MIC, and an untrained encoder.
   Permutations are restricted to the source-training partition. Test labels never
   enter source supervision. Ties can prevent exact prevalence matching.
5. A separate unequal-source-size comparison trains on each full eligible source:
   expert labels, pooled MIC, S. aureus exact MIC and ILToxDB 24h MTT cytotoxicity.
   This is a practical source comparison, not an identified endpoint or provenance effect.
6. Freeze the learned encoder and fit fresh Ridge (alpha 10) and CatBoost
   (300 iterations, depth 5, lr 0.05, seed 1729) on shared target folds. Target folds
   are saved explicitly. Fold groups are cation Murcko scaffolds. OOD-17 uses a
   decoder trained only on QAC-104. This is downstream refitting, not zero-shot.
7. Retain predictions per molecule and seed. Bootstrap paired molecule-level loss
   differences using common resamples; combine results across seeds by averaging
   squared errors before RMSE. On Q-HERO also bootstrap whole scaffold clusters.
   Report the estimand and both uncertainty units; do not label multiple correlated
   predictions of one molecule as independent observations.
8. No non-inferiority margin is imposed after seeing results. Shuffled-label arms
   are diagnostic controls rather than a calibrated multi-permutation hypothesis test.
   A computational intervention concerns supervision content and training objective
   within this fixed algorithm; it does not identify molecular antibacterial mechanisms,
   the effect of human expertise as such, or the effect of assay provenance.

Existing partial fine-tuning results remain a separate architecture/protocol analysis.
The new frozen-backbone head experiment must not be merged with them into one table.
