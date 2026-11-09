Human Judgement as Molecular Supervision: Matched Quantitative Comparisons and Scaffold Transfer in Quaternary Ammonium Biocides

Egor A. Ilin<sup>a</sup>, Nikita A. Frolov<sup>a</sup>, Mary A. Seferyan<sup>a</sup>, Anvar B. Valeev<sup>a</sup>, Egor V. Sinikin<sup>a</sup><sup>,</sup><sup>b</sup>, Taygib M. Iliyasov<sup>a</sup>, Andrey D. Vinokurov<sup>a</sup>, Elena V. Detusheva<sup>a,c</sup>, Elizabeth Son<sup>c</sup>, Michael G. Medvedev<sup>*a</sup><sup>,d</sup>, Anatoly N. Vereshchagin<sup>*a</sup>

a N. D. Zelinsky Institute of Organic Chemistry, Russian Academy of Sciences, Leninsky prospect 47, Moscow 119991, Russian Federation; vereshchagin@ioc.ac.ru (A. N. V.); egor22366@gmail.com (E.A.I.); nfrolov@ioc.ac.ru (N. A. F.)

b Mendeleev University of Chemical Technology of Russia, Miusskaya square 9, Moscow, 125047, Russian Federation

c State Research Center for Applied Microbiology and Biotechnology, Territory “Quarter A”, no. 24, Obolensk, 142279 Serpukhov, Moscow Region, Russian Federation.

d National Research University Higher School of Economics, 101000 Moscow, Russian Federation

Corresponding authors: Anatoly N. Vereshchagin (vereshchagin@ioc.ac.ru); Michael G. Medvedev ([COAUTHORS A1 — insert the corresponding-author email or confirm the final corresponding-author designation]).

Abstract

Human Good/Bad judgements offer coarse supervision for molecular learning. We compare human, continuous-MIC and binary-MIC signals on identical source molecules using matched partial MolFormer fine-tuning, five paired source seeds and common decoders for four antibacterial endpoints in 105 quaternary ammonium compounds. Cation-held-out pooled RMSE is 1.737, 1.715 and 1.806 log2(mg/L), respectively, versus 1.858 for raw features. Real-versus-shuffled labels support a contribution from human supervision. Scaffold holdout and 17 compounds from four new scaffold families expose limits to absolute concentration prediction. Graph, tabular and descriptor comparisons test decoder dependence. A further 363-fit extension compares direct target prediction by frozen heads, LoRA, partial and full fine-tuning with the representation-plus-decoder route. Encoder-weight rewinds preserve feature-map buffers and refit the decoder, separating learned updates from computational state. Reverting all weights removes label-dependent differences across source arms. Independent repeats recover the matched representations and predictions under the archived encoding layout. Human annotation is useful supervision under controlled computational interventions; equivalence to measurements, universal adapter superiority, independent chemical intuition and biological causality are not established.

Keywords

Quaternary ammonium compounds; expert annotations; molecular representation learning; MIC; MBC; multitask learning; scaffold transfer

1. Introduction

Antimicrobial resistance remains a major challenge for healthcare, while the limited pipeline of new antimicrobial medicines sustains the need for reliable experimental and computational discovery strategies (1). Quaternary ammonium compounds (QACs) provide a chemically diverse class of cationic biocides relevant to infection prevention. Predicting their antibacterial activity offers a focused setting in which to examine how molecular learning can guide the evaluation of candidate structures (2).

Machine learning can support compound prioritisation, but the quality of the available supervision remains central to the modelling workflow. In a specialised chemical series, activity data can be sparse and distributed across organisms, strains and assay protocols. Repeated literature records are not independent molecules, and a larger record count does not directly measure the amount of new information supplied to a representation. The question is therefore which supervisory signal transfers to measurements on compounds excluded from source training.

Domain knowledge can enter molecular models through structural constraints, task descriptions or evaluations supplied by chemists. We focus on human evaluations as supervision. Preference-learning work such as MolSkill shows that medicinal chemists’ judgements can be learned for compound prioritisation and design (3). Here we ask whether coarse Good/Bad calls also guide a representation used to predict quantitative antibacterial endpoints. A call may summarise several observations, but its information access, aggregation and independence from numerical measurements require a documented annotation protocol. We do not infer assay denoising from categorical labels alone.

The choice of supervision should be separated from the amount of model adaptation. Molecular foundation models supply reusable features, and fine-tuning can improve property prediction (4). Low-rank adaptation provides another way to learn task-specific updates with fewer trainable parameters (5,6). These alternatives motivate an experimental comparison of frozen heads, LoRA, partial and full fine-tuning. Their performance under a declared budget, rather than parameter count alone, determines which adaptation procedure is useful for this small cohort.

Our previous QAC framework used MolFormer-derived embeddings to predict MIC and MBC against S. aureus and E. coli (2). The present work asks where useful representation guidance comes from. We compare human calls, continuous pooled MIC and binarised MIC on identical source molecules using paired initialisations, splits and training budgets. Raw pretrained features and source-training-only shuffled labels provide complementary controls. The binary-MIC arm shares the human arm’s binary objective, helping separate quantitative resolution from the generic effect of an added training stage.

We retain the original 105 QACs and 17 named compounds from four new scaffold families as the target setting. We first report predictive performance under cation and scaffold holdout, then compare graph and tabular models (7–10) and both direct target prediction and a guided encoder followed by a decoder. Finally, restoring selected encoder weights while retaining feature-map buffers tests the contribution of learned updates to held-out loss. This computational intervention does not identify a molecular antibacterial mechanism or semantic understanding (11). The focus was selected after earlier analyses; Q-HERO and backbone/context results (12,13,5,14), including quantitative advantages in those settings, remain in the supplement.


Figure 1. Matched supervision and target evaluation. The same source chemistry supplies real and shuffled human, continuous-MIC and binary-MIC arms, with paired initialisations and training budgets. The original 105 salts supply cation-held-out validation and the training data for a final decoder applied to the named OOD compounds. Cation-held-out validation permits scaffold overlap; a separate scaffold-held-out sensitivity uses all 105 salts. Text vectors describe only the four tasks. OOD measurements never enter fitting or selection. Source representations use five paired seeds; the supplementary direct-target comparison uses the same first three source checkpoints.

2. Results and Discussion

2.1. Learning guidance under matched source chemistry

The expert archive contains 1,103 final annotation entries, comprising 244 Good and 859 Bad calls before standardisation and exclusions. After matching eligible expert and quantitative records and excluding all evaluation cations, the common panel contains 681 source molecules with 4,938 underlying MIC records and 96 positive human calls. The fixed scaffold-disjoint source split contains 377 training and 304 validation molecules; 52 training calls are positive. Records repeat molecules and are not independent training compounds (Table 1).

| Collection | Unit | Total | Used for learning | Use |
| --- | --- | --- | --- | --- |
| Expert archive | Final annotation entries | 1103 | 244 Good / 859 Bad | Curation source |
| Matched source | Molecules / MIC records | 681 / 4,938 | 377 train; 304 validation | Representation learning |
| Original QAC | Full salts / cations | 105 / 103 | 420 measured endpoints | Decoder CV and OOD training |
| Own OOD | Named molecules / scaffolds | 17 / 4 | No target fitting | 67 exact values; 1 bound |

Table 1. Source and evaluation counts. The 681-source panel is the matched eligibility panel, not a count of training molecules; only 377 source molecules are used for gradient updates. Original QAC structures are excluded from the source. The original 108 target rows collapse to 105 full-salt identities and 103 cations. One conflicting duplicate is retained by the documented historical median rule, with a 104-molecule exclusion sensitivity.

The primary controlled comparison uses the same partial MolFormer adaptation for each source arm. Human and binary-MIC targets share a binary objective, while continuous MIC uses regression. Shuffling occurs only within source training and preserves the marginal label distribution. Within seed, initial weights, molecule order, stochastic schedule and 360 gradient-update budget are shared. These controls isolate a replacement of supervision within a specified algorithm; they do not turn the labels into randomised biological treatments.

2.2. Prediction on the original 105 QACs

The original four targets are MIC and MBC against S. aureus ATCC 43300 and E. coli ATCC 25922. A fixed CatBoost decoder produces one out-of-fold prediction per compound and endpoint under five cation-grouped folds. Different counterion forms of the same cation remain together. The main comparison uses shared one-hot task metadata (Figure 2; Table 2).

| Endpoint | Human | Continuous MIC | Binary MIC | Raw MolFormer |
| --- | --- | --- | --- | --- |
| S. aureus MIC | 1.707 ± 0.025 (R² 0.241) | 1.669 ± 0.052 (R² 0.274) | 1.741 ± 0.092 (R² 0.208) | 1.768 (R² 0.186) |
| S. aureus MBC | 1.832 ± 0.045 (R² 0.129) | 1.831 ± 0.055 (R² 0.129) | 1.925 ± 0.076 (R² 0.038) | 1.921 (R² 0.043) |
| E. coli MIC | 1.640 ± 0.051 (R² 0.307) | 1.615 ± 0.051 (R² 0.327) | 1.706 ± 0.048 (R² 0.250) | 1.800 (R² 0.165) |
| E. coli MBC | 1.763 ± 0.055 (R² 0.288) | 1.735 ± 0.041 (R² 0.310) | 1.841 ± 0.049 (R² 0.223) | 1.939 (R² 0.139) |

Table 2. Original QAC-105 cation-held-out prediction. Each cell gives RMSE in log2(mg/L), as mean ± source-seed SD, followed by mean seed-specific R². Raw features have one fixed decoder run. All 105 structures and 420 endpoint values are retained. Cation-held-out folds allow members of the same scaffold family in both training and test and assess interpolation to a new cation within the sampled chemistry.


Figure 2. QAC-105 parity plots with the common one-hot decoder. Rows correspond to the four species/endpoint tasks; columns compare human, continuous-MIC and binary-MIC guidance. Points show mean predictions over source seeds, while Table 2 reports mean seed-specific scores rather than ensemble scores. The dashed line is y = x; no target-fitted calibration line is applied. All concentration axes use log2(mg/L).

Across all four endpoint losses, human-guided representations yield mean pooled RMSE 1.737, compared with 1.715 for continuous MIC, 1.806 for binary MIC and 1.858 for raw features. Human minus shuffled-human ΔRMSE is -0.120 [-0.217, -0.043]; human minus raw is -0.121 [-0.214, -0.044]. These exploratory, unadjusted seed/scaffold intervals support a contribution from the real label assignment and an improvement over raw features in this cation-held-out, pooled-loss setting.

The quantitative controls also carry signal: continuous-MIC minus shuffled-continuous ΔRMSE is -0.157 [-0.242, -0.086], and binary-MIC minus shuffled-binary is -0.083 [-0.231, +0.046]. The continuous real-versus-shuffled improvement has a larger point magnitude than the human improvement; the binary-MIC interval includes zero. Real-label benefits therefore do not uniquely privilege human supervision.

Human minus continuous MIC is +0.022 [-0.053, +0.101], and human minus binary MIC is -0.069 [-0.157, +0.009]. Their intervals include zero, so the point estimates show practical proximity under this protocol without establishing statistical equivalence. The result concerns prediction losses on measured endpoints, not replacement of experimental assays by annotations. Pooled R² is not used to claim within-task accuracy because differences between species and MIC/MBC can inflate a pooled score. Endpoint-specific R² and errors are reported throughout.

The conflicting duplicate is target_25e7bff606cb (original rows 75 and 76). Its supplied S. aureus MIC values are 0.25/0.5 mg/L, S. aureus MBC values 2/0.5 mg/L, and E. coli MBC values 8/2 mg/L; E. coli MIC is 2 mg/L in both rows. The historical full-salt median rule yields 0.375, 1.25, 5 and 2 mg/L, respectively. Retaining it makes the full original cohort traceable rather than asserting that the median is a new measurement. Excluding its already-held-out predictions changes the main-arm pooled RMSE by at most 0.0044 log2 units; this post-exclusion score sensitivity does not retrain folds and is distinguished from the independently curated QAC-104 analysis in Supporting Information.

2.3. Transfer to held-out scaffolds

New-cation interpolation and new-scaffold transfer are different demands. An additional five-fold validation groups all 105 structures by their 29 cation Murcko scaffolds, keeping entire families outside each decoder training fold (Table 3). It was added after inspecting this extension and receiving protocol reviews, with fixed source checkpoints, hyperparameters and one-hot encoding. Human endpoint R² values under scaffold holdout are 0.129, -0.017, 0.235 and 0.236, respectively. These results delimit how far the gains in cation-held-out prediction transfer. The complete source arms, adverse results and fold assignments are retained.

Under scaffold holdout, pooled RMSE is 1.842 for human supervision, 1.814 for continuous MIC, 1.856 for binary MIC and 1.978 for raw features. The human-minus-raw contrast is -0.136 [-0.269, -0.019], retaining an exploratory pooled-loss benefit. The real-minus-shuffled-human interval is [-0.2591, -0.0001], with its upper limit only just below zero. This boundary result is especially sensitive to the fixed folds, five seeds and unadjusted comparisons and is not an independent confirmation.

| Endpoint | Human | Continuous MIC | Binary MIC | Raw MolFormer |
| --- | --- | --- | --- | --- |
| S. aureus MIC | 1.829 ± 0.042 (R² 0.129) | 1.767 ± 0.029 (R² 0.187) | 1.806 ± 0.109 (R² 0.148) | 1.896 (R² 0.064) |
| S. aureus MBC | 1.980 ± 0.020 (R² -0.017) | 1.949 ± 0.027 (R² 0.015) | 1.993 ± 0.078 (R² -0.032) | 2.008 (R² -0.046) |
| E. coli MIC | 1.722 ± 0.075 (R² 0.235) | 1.726 ± 0.058 (R² 0.232) | 1.766 ± 0.048 (R² 0.196) | 1.958 (R² 0.013) |
| E. coli MBC | 1.825 ± 0.062 (R² 0.236) | 1.807 ± 0.058 (R² 0.251) | 1.851 ± 0.052 (R² 0.215) | 2.045 (R² 0.042) |

Table 3. QAC-105 scaffold-held-out sensitivity, using the same endpoints, units, source representations and one-hot decoder as Table 2. Cells give mean RMSE ± source-seed SD (log2 mg/L), followed by mean seed-specific R². Entire cation-scaffold families remain together. This exploratory follow-up is separate from the cation-held-out primary analysis and from the earlier QAC-104 single-task micromolar analysis.

2.4. Named out-of-domain compounds

The 17 newly synthesised QACs form four scaffold families (Figure 3), with no cation or cation-scaffold overlap with either the matched source panel or QAC-105. The CF3-dihydropyran mono-QACs are IT505, IT502 and IT499; kojic-acid-derived bis-QACs are DA253, PDD13, PDD14 and PDD11; tetrahydropyridine bis-QACs are IT442, IT469, IT452, IT493 and IT380; and glycoluril tetra-QACs are SEV-0338, SEV-035, SEV-036, SEV-030 and SEV-033. Codes follow the source spreadsheet, including SEV-0338.

This collection preserves the chemical scope of the original work. Kojic-acid-linked precursors are converted to bis-pyridinium salts through chlorination and quaternisation. A multicomponent tetrahydropyridine preparation supplies another bis-pyridinium family; the source synthesis records also describe competing pyran formation and epimerisation. The fluorinated dihydropyran precursors yield mono-QACs after N-alkylation, while a glycoluril-based multistep route supplies four-cation products. Reaction schemes, available characterisation and microbiological procedures are retained in Supporting Information Section S16, with missing primary spectra and assay provenance reserved for the chemistry coauthors. Scaffold novelty is verified from supplied structures and does not establish an independently blinded prospective discovery trial.


Figure 3. The four OOD scaffold families, represented by exact named compounds and depicted in ACS 1996 style. The panel identifies mono-, bis- and tetra-cationic compounds and includes counterions. Full structures and codes for all 17 compounds, and a complete structure registry for the original 105 compounds, accompany the reproducibility files.

A final decoder trained on all 105 QACs predicts every OOD endpoint without using OOD activities in fitting or hyperparameter selection. Exact-value scoring retains 17 values for each task except E. coli MBC, where IT505 is reported as >500 mg/L and supplies only a lower bound. Table 4 reports endpoint MAE; RMSE, R², seed dispersion, per-family losses and every named prediction remain in Supporting Information. Averaging across the 67 exact pairs gives human MAE 1.649 and RMSE 2.054, versus continuous-MIC MAE 1.744/RMSE 2.237, binary-MIC 1.706/2.099, and raw-feature 1.854/2.265, all in log2(mg/L).

| Endpoint | Human | Continuous MIC | Binary MIC | Raw MolFormer |
| --- | --- | --- | --- | --- |
| S. aureus MIC | 1.535 ± 0.130 | 1.545 ± 0.126 | 1.711 ± 0.061 | 1.610 |
| S. aureus MBC | 1.704 ± 0.094 | 1.729 ± 0.118 | 1.815 ± 0.152 | 1.756 |
| E. coli MIC | 1.669 ± 0.111 | 1.902 ± 0.104 | 1.637 ± 0.163 | 2.066 |
| E. coli MBC | 1.690 ± 0.013 | 1.803 ± 0.056 | 1.656 ± 0.121 | 1.993 |

Table 4. OOD endpoint MAE in log2(mg/L), mean ± source-seed SD. The fixed decoder is trained only on QAC-105. S. aureus MIC/MBC and E. coli MIC each have 17 exact values; E. coli MBC has 16 exact values and one separately reported >500 bound. Raw features have one run. Differences across five seeds describe optimisation variability, not uncertainty across independent chemical families.

Human representations have lower pooled error point estimates than the numerical and raw references in this small collection, but endpoint concentration accuracy remains limited: three of four human endpoint R² means are negative, with S. aureus MBC close to zero. The S. aureus MIC task-median reference has lower mean absolute error than the human-guided decoder. Moreover, all five human-guided E. coli MBC predictions for IT505 lie below its >500 mg/L bound (21.2–37.0 mg/L), an explicit extrapolation failure retained in the named prediction table.

The censored observation also bounds its error: IT505's E. coli MBC absolute error exceeds 3.76–4.56 log2 units across the human-guided seeds. Using its bound only as a minimum error contribution raises the human mean E. coli MBC RMSE lower bound to 2.356 and pooled 68-pair RMSE lower bound to 2.101. The true errors can be larger; this sensitivity does not replace >500 by an exact measurement. All arms' minimum-error sensitivities are retained. Each source seed combines its own exact squared residuals and its own bound-error contribution before taking the square root; the reported values then average the five seed-specific roots. The complete derivation is given in Table S33.


Figure 4. Human-versus-continuous-MIC absolute-error distributions for each endpoint in QAC-105 and OOD-17. Each value is a molecule's mean absolute error over five source seeds. Left and right half-violins use the same exact-valued compounds; horizontal bars indicate medians and vertical bars IQR. OOD points are also shown individually. Density shape and median similarity do not establish equivalence or independent significance. Sa and Ec denote S. aureus and E. coli, respectively.

Four OOD scaffold groups provide little basis for stable interval estimation. The paired pooled human-minus-continuous ΔRMSE is -0.183 [-0.415, -0.004], and human-minus-shuffled is -0.282 [-0.611, -0.024]. These are exploratory percentile intervals conditional on the four observed families, not confirmatory population bounds; their apparent separation from zero cannot resolve general OOD superiority. A supplementary sensitivity omits each family in turn. Individual compounds and endpoint failures carry more practical information here than a single pooled score.

Direct source-only scoring asks a different question. The earlier matched human head, with no QAC decoder fitting, has mean OOD S. aureus MIC potency-rank agreement 0.667 ± 0.120 across five source seeds, compared with 0.399 ± 0.192 for continuous MIC. The paired human-minus-continuous and human-minus-shuffled rank intervals include zero. This is a suggestive ordering signal in 17 compounds, not an absolute concentration prediction: a binary human logit has no MIC units. Its outcomes are reported separately from the target-trained decoder and are not counted as replication.

2.5. Transfer across graph and tabular models

Chemprop D-MPNN, TabPFN-V2, TabFM and AutoGluon provide additional checks of decoder dependence (7–10). In the fixed one-source-seed comparison, human-guided features have lower pooled point errors than raw features for each tabular decoder in all three regimes. Quantitative guidance has some scaffold-CV advantages, and RDKit descriptors remain a strong independent reference. The complete 21-row comparison, endpoint scores and model budgets are in Table S23, S21 and Figure S28.

On OOD-17, human/RDKit RMSE is 1.966/1.978 for TabPFN-V2 and 1.992/2.027 for TabFM; their paired intervals include zero. Chemprop gives 2.031/2.003/2.375 under cation/scaffold/OOD evaluation. These exploratory fixed-budget results support useful transfer across decoder choices and retain competing descriptor and quantitative outcomes; they do not establish a general ranking of model classes.

2.6. Direct prediction and model adaptation

We tested direct MIC/MBC prediction with frozen linear and MLP heads, query/value LoRA, partial and full fine-tuning, plus all real and shuffled source initialisations. All 363 fits use three paired target seeds, train-only target standardisation and a fixed 30-epoch budget. Complete scores and parameter counts are in Tables S28–S29 and Figure S29. From pretrained initialisation, cation-CV RMSE is 1.863 for full fine-tuning, 2.013 for a frozen linear head and 2.040 for LoRA. LoRA minus full ΔRMSE is +0.177 [+0.071, +0.286]; this procedure does not support universal small-adapter superiority.

| Prediction route | Paired source seeds | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| Direct partial target FT | 0–2 | 1.797 | 1.834 | 2.412 |
| Frozen guided encoder + CatBoost | 0–2 | 1.743 | 1.819 | 2.106 |

Table 5. Both prediction routes using the same first three human-guided source checkpoints. Values are means of seed-specific pooled RMSE in log2(mg/L), rather than ensemble errors. The primary five-source-seed decoder scores remain in Tables 2–4; the complete route comparisons are in S24–S26 and Figure S26.

Human source initialisation yields direct cation/scaffold/OOD RMSE 1.797/1.834/2.412. Real numerical initialisations have lower cation point errors (continuous MIC 1.737; binary MIC 1.745), while human guidance has lower scaffold and OOD point errors. The direct human-minus-shuffled scaffold contrast is −0.156 [−0.311, −0.009]. On OOD, human direct prediction versus the frozen-encoder route differs by +0.306 [−0.278, +0.971]. The observed benefit of source guidance and the choice of target predictor remain conditional on the declared budget and evaluation regime.

2.7. What label and weight interventions identify

Learned signal is defined here as the contribution of adapted encoder parameters to held-out MIC/MBC loss. We restore the pretrained outer LayerNorm, upper eight blocks or all encoder parameters, retain source feature-map buffers, and refit the same decoder for every representation. Within seed, buffers are shared across source arms; restoring all weights makes their representations and predictions identical. The pure raw reference retains its original buffers and is evaluated separately.

| Source supervision | All weights: cation CV | All weights: scaffold CV | All weights: OOD-17 | Real − shuffled: cation CV |
| --- | --- | --- | --- | --- |
| Human | +0.109 [+0.037, +0.201] | +0.097 [−0.004, +0.228] | +0.243 [−0.067, +0.582] | −0.120 [−0.217, −0.043] |
| Continuous MIC | +0.132 [+0.042, +0.230] | +0.124 [+0.036, +0.226] | +0.060 [−0.132, +0.283] | −0.157 [−0.242, −0.086] |
| Binary MIC | +0.041 [−0.070, +0.160] | +0.082 [−0.026, +0.208] | +0.198 [−0.157, +0.603] | −0.083 [−0.231, +0.046] |

Table 6. Encoder-weight contribution and label assignment. Columns 2–4 give rewind-all minus intact ΔRMSE; positive values mean higher error after restoring pretrained weights while retaining source-checkpoint buffers. Column 5 gives real minus shuffled ΔRMSE, where negative values favour real labels. All entries are mean seed-specific pooled contrasts with unadjusted 95% paired seed/scaffold bootstrap intervals and five source seeds. Columns 2–4 use the new 5,000-draw weight-control analysis; column 5 retains the primary 10,000-draw intervals from Section 2.2. CV groups are 29 target scaffolds; OOD has four families. These are conditional interventions in the learning procedure.


Figure 5. Error after component-specific weight rewind relative to the intact encoder. Points show pooled ΔRMSE and bars show paired seed/scaffold intervals for human, continuous-MIC and binary-MIC supervision. Each modified representation receives a refitted common decoder; source-checkpoint buffers remain fixed. Component effects may interact and cannot be added to allocate causal credit. The four-family OOD intervals have limited generalisation scope.

For human guidance, restoring all weights raises cation-CV RMSE by +0.109 [+0.037, +0.201]. Scaffold and OOD contrasts are +0.097 [−0.004, +0.228] and +0.243 [−0.067, +0.582], respectively, and include zero. The numerical arms and component-specific controls are reported alongside the human arm in Table 6, Figure 5 and S25–S26. The supported result is a learned-weight contribution to the specified cation-held-out prediction procedure, with unresolved scaffold/OOD effects.

Real-versus-shuffled labels test supervision assignment; weight rewinds test sensitivity to learned parameter updates. Neither identifies the causal action of a chemical fragment or a named human concept. Whether the labels constitute an independent human-information channel remains conditional on the collection and information-access records in H1–H7. Geometry and attribution analyses, earlier overlapping-source encoders and further component interpretation remain separately documented in S15, S22 and S28.

2.8. Reproducibility and historical-score provenance

Independent repeats recover all 30 matched source-training runs and the archived target representations under the original encoding layout. All 93 intact/raw prediction sets and all 33 reloaded final-OOD target models reproduce saved predictions. Changed encoding batches expose numerical sensitivity; some historical Mac-to-Linux branches remain unresolved. Recovered notebook outputs support earlier scores under different validation protocols. Full audit results, historical numbers and replay conditions are retained in S22, S27 and S28.

3. Conclusions

Human Good/Bad calls can serve as molecular supervision for antibacterial QAC prediction. Under identical source chemistry and matched partial MolFormer training, their pooled cation-held-out QAC loss improves over raw features and shuffled-human controls, while remaining close to the continuous- and binary-MIC competitors. The exploratory scaffold-held-out follow-up retains a pooled-loss benefit over raw features, with a borderline real-versus-shuffled interval. This preserves the original question of economical human guidance without claiming that a label substitutes for a fixed number of assays.

Interpretation of the final labels as independent human knowledge remains provisional pending the annotation information-access and adjudication records in H1–H7. If annotators saw the quantitative endpoints, the comparison must be described as learning from human-compressed measurement information rather than an independent channel. The post-hoc scaffold follow-up and its borderline interval are hypothesis-generating.

Changing the target decoder retains competitive human-guided predictions in the one-source-seed extension, while descriptor models remain strong competitors and Chemprop provides a graph-based reference. Holding out entire scaffold families is harder than holding out new cations; the 17-compound OOD collection does not establish accurate absolute concentrations. Text embeddings of four fixed task descriptions provide no consistently resolved advantage over one-hot metadata. Compact projections merit evaluation as a lower-parameter design choice, but the current comparisons do not identify a generally superior adaptation strategy. The contribution is a controlled comparison of supervisory signals, supported by independent training repeats and explicitly delimited by validation regime, decoder and chemical scope. The new direct-target comparison tests LoRA and backbone fine-tuning explicitly, while weight rewinds delimit the contribution of learned encoder updates from feature-map state. These additions strengthen the controlled computational interpretation; they do not establish general adapter superiority or semantic and biological causality.

4. Experimental protocol

4.1. Human annotation collection and source curation

The final expert archive supplies 1,103 entries (244 Good, 859 Bad). Structure repairs, duplicate handling, eligibility counts, source-target exclusions and hashes are retained in the reproducibility manifests. Individual votes and adjudication logs are absent from the supplied computational archive; no inter-rater agreement is inferred from final calls. The following collection-method fields are reserved for the coauthors.

Pooled quantitative source MIC follows the archive's unified cross-organism field, including encoded censoring bounds, before molecule-level aggregation. It is not a homogeneous strain-specific measurement or the four target endpoints. This source definition is retained across real and shuffled quantitative arms and is separate from the explicit exact/bound treatment of the target workbooks.

[COAUTHORS H1 — Annotators and collection period: insert the number of annotators, their relevant scientific backgrounds and experience, how they were recruited, and the dates or rounds of annotation. Confirm whether the same annotators participated in every round.]

[COAUTHORS H2 — Compound selection: describe how compounds were selected and presented for annotation, the unit being rated (molecule, salt, assay record or another unit), the treatment of repeated structures and counterions, and any exclusions made before annotation.]

[COAUTHORS H3 — Task and decision criteria: insert the exact question/instructions given to annotators and the operational definitions of Good and Bad. State which endpoints or practical considerations were relevant, whether numerical cutoffs were prescribed, and how uncertain or unrateable compounds were handled.]

[COAUTHORS H4 — Information visible to annotators: specify whether annotators saw molecular structures, identifiers, measured MIC/MBC, cytotoxicity, organism/strain information, assay conditions, literature reports or model predictions. State explicitly whether the measurements subsequently used for quantitative supervision were available during annotation and whether Q-HERO or OOD evaluation information was visible.]

[COAUTHORS H5 — Collection workflow: describe the interface or files used, the number of ratings requested per compound, whether ratings were independent, any discussion between annotators, presentation order, repeated checks and revisions between rounds. Attach the original instructions or a representative annotation form to Supporting Information if available.]

[COAUTHORS H6 — Final-label construction: state how individual ratings were combined into the final Good/Bad call, including disagreement, ties, adjudication, missing ratings and revisions. Identify which steps are documented in records and which are reconstructed from the contributors' recollection.]

[COAUTHORS H7 — Records and agreement: identify any recoverable individual votes, round identifiers and adjudication logs and their planned archive location. If votes are available, report agreement with its definition, sample size and uncertainty; otherwise confirm that agreement cannot be calculated. Annotation time or cost may be added if documented, but is not used to infer a measurement-replacement rate.]

4.2. Matched representation learning

MolFormer-XL uses revision 7b12d946c181a37f6012b9dc3b002275de070314 (4). Embeddings and layers 0–3 remain frozen; layers 4–11, the outer encoder LayerNorm and dropout-0.1 scalar head are trained, totalling 28,375,297 trainable parameters. The 681-molecule panel and fixed 377/304 scaffold-disjoint source split are identical across human, continuous pooled MIC, binary MIC and their source-training-only shuffled controls. Five paired seeds (0–4) use identical initial weights, minibatch permutations and stochastic forward schedules. Binary MIC targets use a training-only threshold chosen to match human positive prevalence; both binary training arms contain 52 positive calls. Continuous source targets are standardised on source training and inverted for direct scores. The pooler computes a parameter-free mean over token features; it is not a trained pooling layer. This architectural correction changes no source fit or numerical result. The partial encoder has 28,374,528 trainable parameters. Its scalar source head adds 769, giving 28,375,297 during source training. Direct target fitting discards that scalar head and trains a new LayerNorm plus four-output head with 4,612 parameters, giving the 28,379,140 total in Table S28.

The reused source panel follows the archived v12 eligibility rules and excludes the cations of QAC, OOD and the supplementary Q-HERO cohort. This exclusion history is part of the panel definition even though the new main narrative centres QAC-105 and OOD-17.

Every source arm trains on exactly 377 molecule-level examples per epoch, with one equally weighted target per molecule. Continuous source MIC is the within-molecule median of log2 µM values from the pooled archive; binary MIC is derived from those molecule-level values. The 4,938 records contribute to aggregation across the full eligible panel and are not presented as repeated gradient examples in this matched experiment.

AdamW uses weight decay 0.01, a one-cycle schedule with peak learning rate 3 × 10−5, batch size 32 and norm-one gradient clipping. All arms use float32 and their final checkpoint after 30 epochs/360 updates; validation is diagnostic without early stopping. Native stochastic attention feature maps are refreshed during training and deterministic in evaluation. Reconstruction checkpoints retain trained parameters and replayed final persistent buffers, with all 30 full target-vector reproductions previously audited. This extension reuses those vectors and encodes the one previously omitted conflicting target. Three reference structures verify each restored model to a maximum vector difference below 4 × 10−6. No upstream retraining or target-based checkpoint selection occurs.

The raw reference is re-encoded from the same pinned model and environment. Historical human/quantitative 256-d encoder checkpoints, their common archived scaler and original raw features are kept as a separate overlapping-source reconstruction. They are not the matched intervention, an internal adapter, or a LoRA experiment.

4.3. Task encoding, target learning and validation

Target values are log2(MIC or MBC in mg/L), matching the original endpoint tables. This differs from earlier log2 µM analyses, which remain explicitly labelled in Supporting Information. Duplicate full-salt targets use the prepared historical median rule; the conflicting identity is named in Section 2.2. All 420 QAC training values are numeric and uncensored in the supplied workbook. OOD IT505 E. coli MBC is right-censored and is excluded from exact-value metrics without removing its molecule or bound.

CatBoost uses 300 iterations, depth five, learning rate 0.05, seed 1729 and two threads, without additional hand-selected descriptors or tuning. Cation-held-out GroupKFold supplies five folds of 21 salts each, grouping all four endpoints and all counterion variants. The follow-up scaffold GroupKFold instead groups the 29 canonical cation Murcko scaffolds. Fold assignment uses identities only. The final OOD decoder fits all QAC-105 rows and no OOD measurements. A task-median reference uses each task's training-fold median, or the full QAC median for OOD.

The cation counts in folds 0–4 are 20, 20, 21, 21 and 21, respectively. Folds 0 and 1 each contain one cation represented by two salt identities, yielding 21 salts per fold while preserving all 103 cation groups. No manual fold reassignment or outcome balancing is used.

One-hot metadata uses four species/endpoint indicators. Text metadata uses four fixed archived English descriptions, freshly reconstructed with openai/text-embedding-3-small via OpenRouter on the local computer and cached as a 4 × 1,536 float32 array. The request contains no measured activities or molecular structures. The cache SHA256 is 58f5b9417d437c18f69503322aec6923d03bbf05441d53e355cc1910600c1ff6; exact texts, model response metadata and checksums are archived. All primary real-label seeds and raw features use both encodings, while matched shuffled controls use one-hot. Historical encoders also use four separate endpoint decoders as a no-pooling comparison; these are not a reconstruction of every v5 hyperparameter.

4.4. Metrics, intervals and exploratory scope

RMSE, MAE, R² and Spearman correlation are recomputed from saved out-of-fold or OOD predictions for each seed and endpoint. Trained-arm tables report mean ± source-seed SD; plotted mean predictions do not replace mean seed-specific metrics. Pooled losses combine exact endpoint errors on a common log2 mg/L scale. Pooled R² is retained only in machine-readable tables and cannot establish within-task prediction skill. Within each seed, pooled RMSE is the square root of the mean squared residual over all exact compound–endpoint pairs. The reported multi-seed pooled score averages these seed-specific roots; it does not average four endpoint RMSEs or score an ensemble prediction.

Ten thousand paired bootstrap draws sample the observed scaffold groups with replacement and the five source-seed indices with replacement. The same group weights and sampled seed indices are applied to both arms in each contrast; all endpoints within a sampled group remain together. Each draw averages seed-specific RMSE, rather than evaluating an ensemble mean. Raw-feature predictions repeat the same fixed prediction across seed draws. Intervals are exploratory, unadjusted for multiple comparisons and conditional on fixed folds; OOD has only four groups. Five shuffled runs are diagnostic controls, not a calibrated permutation test. Frozen-feature, architecture, context and direct-score studies remain separate supplementary analyses.

The decoder seed is fixed for every arm; decoder-randomness variability is not represented in these intervals. Source-seed variability applies to the adapted representations, while the raw pretrained reference is fixed. Accordingly, the reported gains are conditional on this common decoder rather than a claim over all decoder initialisations.

The QAC-105/OOD-17 narrative was selected after inspecting earlier outcomes. The first extension protocol preceded its own decoder predictions; the all-endpoint scaffold sensitivity followed inspection and protocol reviews. Neither is a confirmatory preregistration. No new OOD families were selected by optimising these scores, and the prior Q-HERO outcomes remain available in Supporting Information rather than being discarded. Annotation blinding and the chronology of design, measurement and model access remain unresolved until the coauthors complete the collection and assay records.

4.5. Chemistry and microbiological measurements

The available synthetic procedures, characterisation descriptions, bacterial-strain information and MIC/MBC protocols are preserved in Supporting Information Section S16. Newly redrawn exact structures use ACS 1996 bond and atom-label settings. Primary spectra, optimisation material, assay controls and replicate records are reserved in field C1; the computational revision does not create new chemical or microbiological observations.

4.6. Graph and tabular decoder comparison

All graph and tabular comparisons use the same target folds and concentration units. Preprocessing is fitted only on outer training data; guided tabular features use source seed 0, and Chemprop uses three graph-training seeds. The 913-fit configuration, train-only PCA, exact checkpoints, inner selection and model-specific budgets are specified in S21 and S28.

4.7. Reproduction and notebook provenance

Reproduction checks retain source identities, label and weight hashes, minibatch order and all evaluation buffers. Archived encoding layout and independently reloaded checkpoints are verified separately from recovery of historical notebook outputs. The complete records and unresolved branches are described in S22 and S27.

4.8. Direct target prediction and weight controls

Direct fits use three paired source/target seeds, a four-output head, train-only target scaling and 30 fixed epochs without OOD-based selection. LoRA uses query/value rank-eight updates (6). Weight controls use five source seeds, fixed checkpoint buffers and a refitted one-hot CatBoost decoder for each intervention. New contrasts use 5,000 paired seed/group draws; three paired seeds and four OOD families limit uncertainty estimation. All settings, 363 direct fits, 1,331 weight-control fits and checkpoint retention details are in S24–S28.

Supporting Information

The expanded Supporting Information retains the author’s four original classification/embedding figures, all archived computational and chemical records, the original 105 structures and all 17 OOD compounds, every prediction and qualifier, full graph/tabular and direct-fine-tuning tables, task-encoding and decoder figures, component interventions, censored-endpoint derivation and historical notebook provenance. Detailed discussion and configurations relocated from the main text appear in S28. Annotation and assay records remain for coauthor completion.

Data Availability Statement

[COAUTHORS D1 — Insert the verified public archive URL/DOI and exact version for the QAC-AMR/QMR source data and final expert labels. The earlier draft lists 10.5281/zenodo.22286669 and https://github.com/Yagr49/QMC-Expert; their public availability and inclusion of this revision's materials must be confirmed before retaining those claims.]

[COAUTHORS D2 — Insert the immutable archive URL/DOI and code revision for the analyses supporting this article, including source manifests, exclusion rules, target folds, checkpoint identifiers, training settings and per-molecule predictions. State any access or redistribution restrictions for reused sources.]

Author Contributions

Egor A. Ilin: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization, Project administration; Nikita A. Frolov: Conceptualization, Methodology, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization, Supervision, Project administration; Mary A. Seferyan: Conceptualization, Methodology, Validation, Investigation, Writing - Review & Editing; Anvar B. Valeev: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing; Egor V. Sinikin: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing; Taygib M. Iliyasov: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing; Andrey D. Vinokurov: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization; Elena V. Detusheva: Methodology, Validation, Formal analysis, Investigation, Resources, Writing - Review & Editing; Elizabeth Son: Methodology, Validation, Formal analysis, Investigation;  Michael G. Medvedev: Conceptualization, Methodology, Formal analysis, Resources, Data Curation, Writing - Review & Editing, Visualization, Supervision, Project administration; Anatoly N. Vereshchagin: Conceptualization, Methodology, Resources, Writing - Review & Editing, Supervision, Project administration, Funding acquisition.

Conflicts of Interest

The authors declare no competing financial interests.

Acknowledgments

This work was supported by the Russian Science Foundation (project №24-13-00307). Microbiological Experiments were performed at the State Research Center for Applied Microbiology and Biotechnology (SRC AMB) using the unique research facility SRC AMB within the framework of the industry research program of Rospotrebnadzor. This research was supported in part through computational resources of HPC facilities at NRU HSE.

OpenAI Codex assisted with analysis-code preparation, manuscript revision, figure preparation and consistency checks. Kimi Code and Claude Sonnet 4.6 supplied internal critical feedback. Text-embedding-3-small supplied four fixed task-description vectors. Numerical conclusions are supported by executable scripts and saved predictions; the human authors retain responsibility for the scientific content.

References

1. World Health Organization. Antimicrobial resistance. Fact sheet, 16 July 2026. https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance (accessed 2026-10-13).

2. Ilin, E. A.; Frolov, N. A.; Seferyan, M. A.; Valeev, A. B.; Vinokurov, A. D.; Detusheva, E. V.; Son, E.; Medvedev, M. G.; Vereshchagin, A. N., Tackling the challenge of ML-assisted antibacterial activity prediction: One step closer to controlled quaternary ammonium compounds design via neural networks model. Bioorganic Chemistry 2025, 167, 109175.

3. Choung, O.-H.; Vianello, R.; Segler, M.; Stiefl, N.; Jiménez-Luna, J. Extracting medicinal chemistry intuition via preference machine learning. Nature Communications 2023, 14, 6651. https://doi.org/10.1038/s41467-023-42242-1.

4. Ross, J.; Belgodere, B.; Chenthamarakshan, V.; Padhi, I.; Mroueh, Y.; Das, P. Large-scale chemical language representations capture molecular structure and properties. Nature Machine Intelligence 2022, 4, 1256–1264. https://doi.org/10.1038/s42256-022-00580-7.

5. Cai, F.; Zacour, K.; Zhu, T.; et al. ChemFM as a scaling law guided foundation model pre-trained on informative chemicals. Communications Chemistry 2026, 9, 3 (published online 18 December 2025). https://doi.org/10.1038/s42004-025-01793-8.

6. Hu, E. J.; Shen, Y.; Wallis, P.; Allen-Zhu, Z.; Li, Y.; Wang, S.; Wang, L.; Chen, W. LoRA: Low-Rank Adaptation of Large Language Models. arXiv 2021, arXiv:2106.09685. https://doi.org/10.48550/arXiv.2106.09685.

7. Heid, E.; et al. Chemprop: A Machine Learning Package for Chemical Property Prediction. J. Chem. Inf. Model. 2024, 64 (1), 9–17. https://doi.org/10.1021/acs.jcim.3c01250.

8. Hollmann, N.; Müller, S.; Purucker, L.; Krishnakumar, A.; Körfer, M.; Hoo, S. B.; Schirrmeister, R. T.; Hutter, F. Accurate predictions on small data with a tabular foundation model. Nature 2025, 637, 319–326. https://doi.org/10.1038/s41586-024-08328-6.

9. Google Research. TabFM: Tabular Foundation Models. https://github.com/google-research/tabfm (accessed 2026-10-12); code revision fbb665569425fd2f490c6576b3af967876fe11ff904; JAX regression checkpoint google/tabfm-1.0.0-jax, revision d5e74033fcf257699fab013e2cdd7edf424ff904.

10. Erickson, N.; Mueller, J.; Shirkov, A.; Zhang, H.; Larroy, P.; Li, M.; Smola, A. AutoGluon-Tabular: Robust and Accurate AutoML for Structured Data. arXiv 2020, arXiv:2003.06505. https://doi.org/10.48550/arXiv.2003.06505.

11. Schölkopf, B.; Locatello, F.; Bauer, S.; Ke, N. R.; Kalchbrenner, N.; Goyal, A.; Bengio, Y. Towards Causal Representation Learning. 2021. https://arxiv.org/abs/2102.11107.

12. Ghaemi, S.; Consylman, A.; Pan, B.; Wu, A.; Petersen, A.; Chang, G.; McDonough, D.; Forman, M.; Bezold, E. L.; Wuest, W. M.; Shehu, A.; Zhao, L.; Minbiole, K. P. C., Topology-Aware Generation and Activity-Based Filtering: A Computational-Experimental Framework for Data-Scarce Quaternary Ammonium Compound Discovery. Journal of Chemical Information and Modeling 2026, 66, 3117-3128.

13. Singh, R.; Barsainyan, A. A.; Irfan, R.; et al. ChemBERTa-3: an open source training framework for chemical foundation models. Digital Discovery 2026, 5, 662–685. https://doi.org/10.1039/D5DD00348B.

14. Toukach, P. V.; Arakelyan, L. A.; Egorova, K. S. ILToxDB: A Database on Cytotoxicity of Ionic Liquids. Environmental Science & Technology Letters 2025, 12, 1631–1635. https://doi.org/10.1021/acs.estlett.5c00860.

