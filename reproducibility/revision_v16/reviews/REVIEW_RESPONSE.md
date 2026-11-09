# Resolution of the authorised Kimi / Claude v16 critiques

Both reviews were completed by actual external services from the local Mac. Kimi Code CLI 2.1.1 used its configured model; the CLI output does not expose a model identifier, so no specific Kimi version is inferred. Claude Code 2.1.87 reports `claude-sonnet-4-6`. Claude tools, MCP integrations and session persistence were disabled; both prompts requested a read-only critique of the supplied material. Prompts, completions, timing, hashes and process metadata are retained here. These are internal model critiques, not human peer review or scientific certification.

The reviewed text and document validation are preserved as `manuscript_v16_reviewed.md` and `reviewed_document_validation.json`. The final v16 contains the following clarifications. No new fitting or outcome selection was performed after the reviews.

## Implemented clarifications

1. **Source and target parameter counts.** The identical partial encoder has 28,374,528 trainable parameters. A scalar source head adds 769: source total 28,375,297. Direct target prediction discards that head and adds a LayerNorm and Linear(768→4), totalling 4,612 head parameters: target total 28,379,140. Main Methods now show this arithmetic explicitly. The same-stage counts remain identical across source arms; different heads are not a mismatch in the matched supervision design.
2. **Duplicate primary intervals.** Primary real-versus-shuffled intervals used 10,000 bootstrap draws; the new audit used 5,000 on identical predictions. The point effects coincide. Main Table 7 now retains the primary 10,000-draw real-versus-shuffled intervals from Section 2.2; its new weight-rewind columns retain their 5,000-draw intervals. The caption specifies both. Table S32 preserves the complete new 5,000-draw recalculations and explains the Monte Carlo differences. Primary tables and prediction files are unchanged.
3. **Pooled RMSE.** Main Methods state that each seed pools squared residuals over exact compound–endpoint pairs before taking a square root; the reported score then averages these seed-specific roots. Averaging four endpoint RMSEs is a different calculation. Thus the binary pooled value 1.806 versus a simple endpoint-RMSE mean of about 1.803 is not an arithmetic defect.
4. **Censoring derivation.** New Table S33 gives all five human source seeds. Their pooled 68-endpoint RMSE lower bounds are 2.062819, 2.183768, 2.202188, 1.978088 and 2.075820. Their mean is 2.100536, supporting the reported 2.101. The corresponding Ec_MBC mean is 2.355897, supporting 2.356. Each seed uses its own exact residuals and its own IT505 lower-bound residual. Substituting the smallest residual across all seeds into an already averaged RMSE does not reproduce this estimator. Every value was checked from the independently replayed endpoint predictions.
5. **Three paired seeds.** Direct-fit stochastic variability and route intervals remain explicitly coarse, exploratory and conditional. Source/target seeds are paired one-to-one, not crossed; separate variance components are not identified.

## Reviewer assertions that do not imply data errors

- Claude describes the negative lower bound of the human interval as barely clearing zero. For a negative-effect interval, exclusion of zero is controlled by its upper bound (−0.043); the lower-bound change from −0.217 to −0.221 reflects resampling, not a reversal of the inference.
- Both reviewers reconciled the parameter difference themselves. The source/target distinction was present in the methods and supplement; the extra arithmetic now makes it easier to follow.
- Kimi's claim that pooled scores match arithmetic endpoint means is too imprecise. Exact loss pooling is nonlinear, as the independent predictions and the new formula show.
- Claude suggests five seeds would narrow the OOD interval. More seeds improve the description of stochastic variability but do not guarantee a narrower interval; no such promise is adopted.

## Optional experiments left outside the current claims

Crossed source/target seeds, additional target seeds, LoRA rank/LR searches, formal equivalence testing and more independent OOD families would address further questions. They are not reported as completed. Current claims remain about specific supervision assignments, weight interventions and prediction procedures. Independent human information still requires the coauthor H1–H7 records; chemical concepts and biological causal mechanisms are not identified.
