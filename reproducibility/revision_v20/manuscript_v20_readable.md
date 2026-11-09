Expert Judgement as Supervision: Human and Quantitative Guidance for Antibacterial Molecular Representations

Egor A. Ilin<sup>a</sup>, Nikita A. Frolov<sup>a</sup>, Mary A. Seferyan<sup>a</sup>, Anvar B. Valeev<sup>a</sup>, Egor V. Sinikin<sup>a</sup><sup>,</sup><sup>b</sup>, Taygib M. Iliyasov<sup>a</sup>, Andrey D. Vinokurov<sup>a</sup>, Elena V. Detusheva<sup>a,c</sup>, Elizabeth Son<sup>c</sup>, Michael G. Medvedev<sup>*a</sup><sup>,d</sup>, Anatoly N. Vereshchagin<sup>*a</sup>

a N. D. Zelinsky Institute of Organic Chemistry, Russian Academy of Sciences, Leninsky prospect 47, Moscow 119991, Russian Federation; vereshchagin@ioc.ac.ru (A. N. V.); egor22366@gmail.com (E.A.I.); nfrolov@ioc.ac.ru (N. A. F.)

b Mendeleev University of Chemical Technology of Russia, Miusskaya square 9, Moscow, 125047, Russian Federation

c State Research Center for Applied Microbiology and Biotechnology, Territory “Quarter A”, no. 24, Obolensk, 142279 Serpukhov, Moscow Region, Russian Federation.

d National Research University Higher School of Economics, 101000 Moscow, Russian Federation

Abstract

Human judgements may offer a compact supervisory signal for quantitative molecular prediction, but their contribution must be separated from model adaptation and evaluation design. We study a frozen MolFormer representation followed by a 768→512→384→256 encoder guided by expert Good/Bad calls and a task-aware CatBoost decoder for four antibacterial endpoints. The original analysis reports human-guided R² values of 0.75, 0.68, 0.59 and 0.77, comparable to the corresponding reported quantitative-guidance results of 0.78, 0.68, 0.58 and 0.77. We retain those findings and their notebook provenance, then test the associated hypotheses on 105 QACs and 17 compounds from four new scaffold families. Paired compact-encoder controls, task-code substitutions, modern tabular models and separate backbone-adaptation experiments reveal dependence on the representation, split and prediction route. Human-guided features improve OOD loss relative to raw features in several configurations, while compact-encoder shuffled-label controls do not establish a human-specific benefit. These results motivate inexpensive human guidance as a candidate source of representation supervision and define the additional evidence needed to attribute its predictive value to annotation content.

Keywords

Quaternary ammonium compounds; antibacterial activity; human supervision; molecular representation; contrastive learning; task encoding; out-of-distribution prediction


1. Introduction

Antimicrobial resistance is a crucial challenge for modern society, compounded by the difficulty of discovering and developing new antibacterial agents (1,2). Historical WHO analyses documented a limited innovative pipeline (3,4), and the 2024 Bacterial Priority Pathogens List identifies organisms requiring sustained research attention (5). In the WHO analysis with a February 2025 cutoff, 90 antibacterial products were in clinical development; among the 27 antibiotics targeting bacterial priority pathogens, 11 met at least one innovation criterion (6,7). These figures describe the systemic antibacterial pipeline rather than the topical biocides studied here. They nevertheless underline the broader need for reliable experimental and computational strategies for antibacterial discovery.

The twenty-first-century tool to boost innovation in antimicrobial pipelines is machine learning (ML) which is increasingly used to accelerate discovery, optimize efficacy–toxicity trade‑offs, and understand resistance mechanisms 8-17. Moreover, global trends indicate rapid ML incorporation in antimicrobial stewardship practices bringing innovative approaches to antimicrobial use optimization, personalized therapy and AMR reduction 18. There are now several case studies where ML has measurably shortened timelines for antimicrobial‑class discovery, including biocide‑related scaffolds and peptide‑based agents 19-21.

A compelling strategy for molecular prediction is to incorporate domain knowledge and expert guidance into the modelling workflow. Physics-informed neural networks illustrate how physical constraints can restrict a model’s admissible solutions (22,23). Related molecular approaches use chemical substructures, physicochemical priors or biological relationships to shape architectures and objectives (24–26). These mechanisms differ from human annotation, yet they motivate the same practical question: which form of prior information helps a model learn from a limited chemical series? For antibacterial prediction, the relevant information may concern structural patterns, organism-dependent responses or the way heterogeneous measurements should be interpreted.

A distinct line of work treats human expertise as supervision. Expert judgements of drug-likeness helped motivate QED (27), while studies of medicinal-chemist agreement and selection bias show why the collection and aggregation of such judgements require documentation (28,29). MolSkill learns medicinal-chemist preferences for compound evaluation (30), and human feedback has also been used in molecular design and dedicated evaluation interfaces (31,32). Preference learning outside chemistry provides further examples of models trained from categorical feedback (33,34). Here we ask whether coarse Good/Bad assessments can guide a molecular representation subsequently used to predict continuous antibacterial measurements. The comparison is with quantitative guidance on the same endpoint setting, rather than only with an untrained scoring rule.

Transfer learning and multitask approaches offer another route for sharing information between related biological endpoints, including antimicrobial-peptide classification and MIC regression (35,36). In QAC prediction, the species and endpoint type define related but distinct tasks. A shared predictor can learn their statistical relationships when the task identifier is supplied alongside the molecular representation. Text embeddings provide an alternative to categorical identifiers, as demonstrated by assay-description modelling (78). With only four endpoint descriptions, however, successful prediction does not itself show that the model understands their biological meaning; arbitrary and permuted task-code controls can test this interpretation.

The nature of the supervision remains a central limitation. Bioactivity corpora assembled from the literature are sparse and heterogeneous across organisms, laboratories and assay protocols. Studies of mixed IC50 and Ki data demonstrate that pooling measurements from different sources can introduce substantial uncertainty (37–39). The same concern motivates careful treatment of antibacterial corpora, although the uncertainty observed for those other endpoints cannot be assigned numerically to MIC/MBC without additional evidence. An expert call may summarise several measurements or practical criteria; whether it actually harmonises assays, and whether it contributes information unavailable in the quantitative data, depends on the annotation records and information shown to the annotators.

In this paper, we will mainly focus on development and property predictions of cationic biocides, particularly membrane-targeting quaternary ammonium compounds (QACs), as antiseptics and disinfectants which are essential for prevention and treatment of microbial infections, especially healthcare-associated infections (HAIs). The main applications include variety of target objects from hand hygiene and surgical site preparation to surface cleaning providing rapid persistent antimicrobial action 40, 41. Previously, ML procedures were implemented in the chemistry workflow for antimicrobial activity estimation of cationic biocides derived from pyridine, cinchonine, imidazole, and bis-imidazole 42-48. Predictive ML model was developed for conjugated oligoelectrolytes utilizing domain-agnostic framework with a limited database of bis- and multi-QACs 49. Associative Neural Network was successfully employed to predict the MIC of ionic liquids 50, 51. Recent progress in QACs discovery was imbued by topology-aware generative model further highlighting practical validity of ML application 52.

Our previous work established a framework for QAC MIC and MBC prediction using MolFormer-derived representations and biology-informed stacking (53). The present study asks where the useful representation guidance comes from. We first retain the original comparison between expert-guided and quantitatively guided encoders, the task-aware prediction results and the synthesis and evaluation of 17 new QACs. We then test the associated hypotheses with reconstructed v5 decoding, grouped evaluation on the original 105-molecule cohort, matched supervision and shuffled-label controls, graph and tabular alternatives, and direct versus representation-mediated adaptation. Finally, similarity, attribution and weight interventions examine which aspects of the learned representation contribute to prediction. These analyses have different evidence scopes: reported original performance, newly executed follow-ups and computational interventions are identified explicitly.


The workflow separates three objects (Figure 1). First, frozen MolFormer maps the SMILES string s to a 768-dimensional vector h0=fθ(s), supplying reusable molecular features (77). Second, an external encoder gψ transforms h0 into a 256-dimensional vector z. Human or quantitative labels determine how ψ is trained; they are not required when z is computed for a new molecule. Third, a decoder D combines z with a task code t and predicts y=D(z,t), where y is log2 MIC or MBC. The auxiliary source-training head and the numerical target decoder serve different purposes. This separation lets us compare guidance signals while inspecting both representation formation and final prediction.

The compact encoder acts as a feature adapter: it learns new transformations outside the frozen backbone. This differs from partial or full fine-tuning of MolFormer and from low-rank updates inserted within its layers (79). Fewer trainable parameters can be attractive for a small target cohort, but do not guarantee better generalisation. We therefore treat the claim that compact guidance is preferable to backbone fine-tuning as an empirical question, and evaluate both direct backbone→prediction and guided representation→decoder routes under stated budgets.


Figure 1. Formation and use of guided molecular embeddings. A SMILES structure is encoded by frozen MolFormer into 768 features; a separate trainable encoder produces a 256-dimensional vector. Human and quantitative supervision denote alternative training objectives. The downstream decoder combines the learned vector with a species/endpoint code to predict log2 concentrations. The coloured strips display the first 24 coordinates of actual archived vectors with independently rescaled opacity; they are not a structural/biological variance partition. The ACS 1996 example is target_29136ba3d6e0 from the complete QAC register in Table S19.

2. Results and Discussion

2.1 Learning the guided molecular representation


The expert-guidance archive contains final Good/Bad calls for 1,103 compounds before the exclusions used in the new matched comparison. These calls are intended to summarise expert assessment of antibacterial suitability. The earlier draft described an approximately 1,500-compound collection and a three-expert blind majority-vote procedure; those collection-stage details require confirmation from the contributors. The final-label archive establishes the available supervisory outcomes, while the collection process, visible information and agreement are reserved for coauthor completion in Section 4.3.1. No unrecorded votes, blinding or annotation costs are assumed.

The original descriptor screen compared MolFormer (768 dimensions), ChemBERTa, Morgan and MACCS representations using stratified classification cross-validation (Supporting Information, Figures S1–S4). The preserved SI plot reports F1=0.665 for MolFormer with an MLP and StandardScaler; we quote this as a figure-reported screening result, not an independently replayed benchmark. The original text instead gave 0.655 and reported accuracy 0.856. The numerical discrepancy remains recorded in SI pending the underlying classification runs. This screen motivated the use of MolFormer features, but aggregate F1 and accuracy alone do not establish that other representations lack antibacterial information or that the selected backbone recognises membrane-disruption mechanisms.

The original guidance stage uses a separate MLP encoder taking the 768-dimensional MolFormer vector through hidden widths 512, 384 and 256. Linear transformations, batch normalisation, ReLU activations and dropout allow the encoder to select and reorganise the pretrained features. The archived expert model was trained with supervised contrastive guidance, a hard-negative term and Borderline SMOTE with sampling strategy 0.8. Its auxiliary projection is used to compute the training loss; the 256-dimensional encoder output, rather than the auxiliary projection or the Good/Bad classifier output, is passed to the quantitative decoder. We call this output the human-guided embedding. The source classification loss does not train a numerical MIC/MBC prediction directly.

The archived t-SNE visualisation illustrates the molecular representation before and after expert-guided refinement (Figure 2). The figure is redrawn from the exact scatter-marker centres in the original vector PDF, preserving all 221 observations and their class assignments. That PDF prints silhouette 0.007→0.107, while the original manuscript raster prints 0.108 after training; both source versions are documented, and the raster is retained in Figure S31. The original analysis also reports Davies–Bouldin index 6.54→2.58 and Calinski–Harabasz score 3.60→22.08. Those reported values are not recomputed from display coordinates. They describe class-associated geometry, rather than quantitative regression performance or acquisition of an antibacterial mechanism. Figure 6 uses the different 105-QAC cohort and colours structural classes rather than activity labels.


Figure 2. Soft redraw of the archived before/after contrastive-learning visualisation. All 221 scatter-marker positions per panel are recovered directly from publication_tsne_before_after.pdf: 172 Bad and 49 Good observations. Only typography, marker styling and layout are changed; no t-SNE is rerun. The PDF reports silhouette 0.007→0.107; the original manuscript raster reports 0.108 after training and is retained in Figure S31. These are archive-specific classification-geometry summaries, not quantitative regression or causal-performance metrics.


2.2 Training on QACs

We next use the learned embeddings to predict log2(MIC) and log2(MBC) for S. aureus ATCC 43300 and E. coli ATCC 25922 on the QAC dataset introduced previously (53). Table 1 retains the original model comparison. The task-aware models receive both the molecular representation and the identity of the organism/endpoint pair. The recovered May notebook uses CatBoost’s native categorical task_id for the row described originally as one-hot multitask CatBoost. Literal four-coordinate one-hot codes are therefore treated separately in the new checks. The shared model uses four measurement rows per molecule, which can improve statistical sharing; this design also requires molecule-level splitting when the claim concerns new compounds.

The original text-code variant concatenates an OpenAI task-description vector with the molecular embedding. Recovered May 24 notebook outputs give R²=0.7494, 0.6752, 0.5918 and 0.7708 for the four endpoints, supporting the positive results reported in v5. E. coli MIC is displayed here as 0.59, correcting the original rounding to 0.60. The corresponding native categorical model outputs are 0.7102, 0.6403, 0.4269 and 0.7394. These saved outputs document those original R² values; they do not by themselves reproduce every Table 1 RMSE, descriptor row or Table 2 quantitative-source model. The missing historical task-vector cache and the split structure are addressed in the follow-up checks rather than used to replace these original numbers.


Table 1. Original reported prediction comparison, followed by newly reconstructed five-fold CV of the saved human-guided representation. The upper block retains the original holdout values and rounding correction; the three lower rows give RMSE and R² as mean ± fold SD (five row-wise folds, ddof=0). These CV means are new calculations and do not supply error bars for the upper block. Full fold scores and raw-feature controls are in Table S40.

| ML models | RMSE |
| --- | --- |
|  | S. aureus ATCC 43300 | E. coli ATCC 25922 |
|  | log2(MIC) | log2(MBC) | log2(MIC) | log2(MBC) |
| MLP | descriptors | 1.01 (R2=0.68) | 1.57 (R2=0.25) | 1.40 (R2=0.32) | 1.37 (R2=0.40) |
| MLP + stacking |  | - | 1.51 (R2=0.30) | 1.29 (R2=0.43) | 1.36 (R2=0.41) |
| Multitask MLP |  | 0.87 (R2=0.70) | 1.43 (R2=0.41) | 1.31 (R2=0.41) | 1.33 (R2=0.46) |
| MLP | embeddings | 1.36(R2=0.20) | 1.89 (R2=0.35) | 1.35 (R2=0.31) | 1.45 (R2=0.33) |
| Multitask Catboost |  | 0.91 (R2=0.71) | 0.95 (R2=0.64) | 1.31 (R2=0.43) | 1.08 (R2=0.74) |
| Multitask + encodedclasses Catboost |  | 0.92 (R2=0.75) | 0.85 (R2=0.68) | 0.95 (R2=0.59) | 1.00 (R2=0.77) |
| Human / new CV: task_id | 5-fold mean ± SD | 1.38 ± 0.26(R²=0.45 ± 0.14) | 1.52 ± 0.34(R²=0.31 ± 0.39) | 1.07 ± 0.32(R²=0.65 ± 0.19) | 1.32 ± 0.19(R²=0.52 ± 0.27) |
| Human / new CV: organism + endpoint | 5-fold mean ± SD | 1.34 ± 0.36(R²=0.48 ± 0.22) | 1.47 ± 0.30(R²=0.41 ± 0.25) | 0.97 ± 0.14(R²=0.72 ± 0.06) | 1.16 ± 0.11(R²=0.66 ± 0.07) |
| Human / new CV: text code | 5-fold mean ± SD | 1.30 ± 0.19(R²=0.51 ± 0.10) | 1.42 ± 0.25(R²=0.45 ± 0.21) | 0.98 ± 0.18(R²=0.72 ± 0.08) | 1.20 ± 0.16(R²=0.64 ± 0.05) |
| MIC and MBC in mg/L, modelled on log2 scale. Multitask supplies a species/endpoint task code; recovered CatBoost code uses native categorical task_id. Encoded classes supplies OpenAI task-description vectors. Original reported values; see text for provenance and rounding correction. Separate new CV rows report unweighted mean ± SD of five fold scores (numpy.std, ddof=0), on the original 108 worksheet rows / 105 unique salts. They reconstruct the author’s row-wise KFold approach with saved human features and reconstructed task vectors; they are not uncertainty attached to the historical holdout rows. No CV rows for the unresolved full-corpus quantitative checkpoint are substituted. |


The original multitask comparison shows why both representation guidance and task information merit investigation. Figure 3 retains the original parity panels and their printed metrics. Their relative performance motivates the subsequent checks; prediction on unseen organisms or activity types was not evaluated by the four-endpoint experiment and is not inferred from it.


Figure 3. Original parity panels for quantitative antibacterial prediction. This is a preserved historical figure. The panel labelled one-hot refers to the original categorically coded comparison; the recovered May CatBoost cell uses native categorical task_id. Printed performance labels and the historical test split belong to the original analysis, whereas the newly reconstructed and grouped results are reported separately in Section 2.5.


A central question is whether expert Good/Bad supervision can compete with quantitative activity measurements in shaping the molecular representation. The original study trained an architecturally related encoder using multi-output regression on a larger activity collection. Table 2 retains the resulting reported comparison. This full-corpus quantitative model is distinct from the QAC-only binned contrastive ablation in Section 2.4 and from the new matched source panel. Its exact saved multitarget checkpoint has not yet been located, so that original comparison has reported-result status rather than a completed execution replay. The missing checkpoint is not evidence that the original Table 2 was generated by the QAC-binned ablation.

The broad quantitative collection described in the original corpus account contains 1,559 unique molecules and more than 18,000 activity records across approximately 400 strains, including MIC, MBC, MBIC and MBEC. S. aureus and E. coli comprise approximately 40% of the reported measurements. The recovered MIC-only computational export contains 9,338 records for 1,153 molecules. These counts describe different units and subsets, and are therefore reported separately. Repeated records supply assay observations rather than the same number of independent molecular structures. Assay context is retained where available; its heterogeneity motivates a harmonisation hypothesis but does not establish that the expert calls perform that harmonisation.

In the original text-code configuration, the reported human-guided and quantitative-guided R² values are 0.75 versus 0.78 for S. aureus MIC, 0.68 versus 0.68 for S. aureus MBC, 0.59 versus 0.58 for E. coli MIC and 0.77 versus 0.77 for E. coli MBC (Table 2). Thus the original human-guided model is competitive in these reported results despite its coarser supervisory labels. The small difference for E. coli MIC is descriptive and is not a demonstrated superiority or statistical equivalence result. Comparing roughly 1,100 final calls with roughly 10,000 MIC records also does not establish a tenfold reduction in independent data or annotation cost. New matched checks ask whether the label assignment contributes beyond architecture, exposure to source molecules and the quantitative objective.

A possible explanation is that a Good/Bad call summarises multiple aspects of a compound’s antibacterial profile. If annotators integrated activity measurements and practical criteria, the resulting call would be a compact human interpretation of those inputs. If they saw the same quantitative measurements used by the comparison model, it would be a compressed measurement-derived channel rather than independent human information. Whether either account describes the actual collection depends on H1–H7; the predictive comparison does not establish annotation information access, implicit assay harmonisation or lower acquisition cost.


Table 2. Original reported expert versus full-corpus quantitative comparison, followed by separate new CV rows for the saved human-guided encoder. The lower rows give mean ± SD over five row-wise folds, with no matched full-corpus quantitative CV available. Original source comparison, new CV and QAC-only ablation remain different evidence branches.

| ML models | RMSE |
| --- | --- |
|  | S. aureus ATCC 43300 | E. coli ATCC 25922 |
|  | log2(MIC) | log2(MBC) | log2(MIC) | log2(MBC) |
| Catboost | classified embeddings | 1.36 (R2=0.20) | 1.89 (R2=0.35) | 1.35 (R2=0.31) | 1.45 (R2=0.33) |
| Multitask Catboost |  | 0.91 (R2=0.71) | 0.95 (R2=0.64) | 1.31 (R2=0.43) | 1.08 (R2=0.74) |
| Multitask + encoded classes Catboost |  | 0.92 (R2=0.75) | 0.85 (R2=0.68) | 0.95 (R2=0.59) | 1.00 (R2=0.77) |
| Catboost | multi regression embeddings | 1.19 (R2=0.23) | 1.64 (R2=0.38) | 1.22 (R2=0.37) | 1.29 (R2=0.37) |
| Multitask Catboost |  | 0.86 (R2=0.81) | 0.96 (R2=0.64) | 1.28 (R2=0.32) | 1.08 (R2=0.73) |
| Multitask + encoded classes Catboost |  | 0.92 (R2=0.78) | 0.89 (R2=0.68) | 1.01 (R2=0.58) | 1.01 (R2=0.77) |
| Human / new CV: task_id | 5-fold mean ± SD | 1.38 ± 0.26(R²=0.45 ± 0.14) | 1.52 ± 0.34(R²=0.31 ± 0.39) | 1.07 ± 0.32(R²=0.65 ± 0.19) | 1.32 ± 0.19(R²=0.52 ± 0.27) |
| Human / new CV: organism + endpoint | 5-fold mean ± SD | 1.34 ± 0.36(R²=0.48 ± 0.22) | 1.47 ± 0.30(R²=0.41 ± 0.25) | 0.97 ± 0.14(R²=0.72 ± 0.06) | 1.16 ± 0.11(R²=0.66 ± 0.07) |
| Human / new CV: text code | 5-fold mean ± SD | 1.30 ± 0.19(R²=0.51 ± 0.10) | 1.42 ± 0.25(R²=0.45 ± 0.21) | 0.98 ± 0.18(R²=0.72 ± 0.08) | 1.20 ± 0.16(R²=0.64 ± 0.05) |
| MIC and MBC in mg/L, modelled on log2 scale. Multitask supplies a species/endpoint task code; recovered CatBoost code uses native categorical task_id. Encoded classes supplies OpenAI task-description vectors. Original reported values; see text for provenance and rounding correction. The full-corpus quantitative multitarget checkpoint remains unresolved. Separate new CV rows report unweighted mean ± SD of five fold scores (numpy.std, ddof=0), on the original 108 worksheet rows / 105 unique salts. They reconstruct the author’s row-wise KFold approach with saved human features and reconstructed task vectors; they are not uncertainty attached to the historical holdout rows. No CV rows for the unresolved full-corpus quantitative checkpoint are substituted. |


2.3 Out of domain inference

The independent target collection comprises 17 newly synthesised QACs from four scaffold families: kojic-acid bis-QACs, tetrahydropyridine bis-QACs, CF3-dihydropyran mono-QACs and glycoluril multi-QACs (Figure 4). They cover three charge-multiplicity classes, but four chemical families. Their named identities and all measured endpoint records are retained in Supporting Information. These compounds provide a fixed OOD evaluation set for the new calculations, with no target compound used for model selection. IT505 E. coli MBC is reported as >500 mg/L and remains a right-censored endpoint, leaving 67 exact values and one bound.


Figure 4. The four OOD chemical families represented by exact archived structures redrawn with ACS 1996 bond and atom-label settings. The complete 17-compound register and counterion treatment are given in Supporting Information.

The QAC's architecture follows the principle of core, tail and linker interconnection. While QACs can be classified in variety of ways, the usual approach is division by quantity of charged cores. Within the framework of current study, we sought to utilize three main subclasses of QACs (mono-, bis-, and multi-QACs) for a thorough assessment of predictive potential of the developed ML model.

Heterocycles are among the most well-known and diverse classes of compounds in organic chemistry, forming the basic structural backbones of most modern drugs, including QACs, which often have a heterocyclic nature 54-57. For the purposes of this study, we selected four suitable scaffolds to obtain the target structures: kojic acid, tetrahydropyridine, dihydropyran, and glycoluril derivatives. All 17 novel obtained compounds were subjected to MIC and MBC evaluation via broth microdilution assay. Detailed representation of the synthesis methodologies, microbiological results and compounds description can be found in the experimental section and supplementary materials. The synthetic approaches are described below.

2.3.1 Kojic acid-based bis-QACs

Kojic acid (KA) is a multifunctional natural low toxic organic compound used in cosmetics as skin-depigmenting agent 58, 59. KA itself possesses moderate antibacterial activity, but several synthetically derived classes show significantly enhanced potency against a broad spectrum of bacteria 60-65. Here we used the functionalization of KA to obtain bis-QAСs architectures in similar fashion to the commercially available antiseptic octenidine with alkylaminopyridine pharmacophore group. First, dimerization of KA with 1,5-dibromopentane afforded the dihydroxy-platform. Chlorination of dimer 1 and subsequent quaternization with 4-(alkylamino)pyridines occurred at the pyridine nitrogen atom led to the target bis-QACs 1-4 (Scheme 1). The required 4-(alkylamino)pyridines were obtained separately in three steps from carboxylic acids as reported previously 66.


Scheme 1. Synthesis of KA-based bis-QACs.


2.3.2 Tetrahydropyridine-based bis-QACs

Tetrahydropyridine (THP) scaffold is a versatile nitrogen-containing heterocycle widely used in medicinal chemistry as a bioactive ring system and pharmacophore 67. One of the key features of THP-based drug design is efficient and fast synthesis through multicomponent reactions (MCR) 68. Previously, we found that 1,4,5,6-THP are produced through a MCR between aromatic aldehydes, malononitrile, methyl acetoacetate, and ammonium acetate in methanol at 64 ℃ for 2 h 69. When using 3-pyridinecarboxaldehyde as the aromatic moiety, MСR is a convenient method for creating bis-pyridine platforms which are known precursors of bis-QACs. The followed Menshutkin reaction yielded the second set of bis-QACs 5-9 (Scheme 2).


Scheme 2. Synthesis of THP-based bis-QACs.

However, despite the well-known nature of the method, we encountered several unexpected difficulties during the implementation of the process requiring optimization of the MCR synthesis conditions. First, the desired THP was produced in mixture with 4H-pyran as a result of a competitive process of intramolecular cyclization via the attack of carbonyl on the nitrile group after Michael addition (Scheme S5). The MCR conditions for a 3-pyridinecarboxaldehyde, malononitrile, methyl acetoacetate and ammonium acetate were optimized by varying the solvent, temperature, and the equivalents of ammonium acetate (Table S10). 4H-Pyran was the primary product during the reaction at room temperature, while at 64 ℃ and increased solvent load the quantity of the by-product slightly decreased (Table S10 entry 3). As the amount of NH4OAc increases to 4.0 mol. equiv., the reaction’s sole product is desired THP. Consequently, we attempted to conduct the reaction using ethanol, which is less hazardous to human health and is classified as a green solvent 70. Carrying out a similar reaction in ethanol at 78 ℃ resulted in 62% yield of the desired THP (Table S10 entry 7). Second, the Menshutkin reaction led to the formation of bis-QAC in the form of a pair of diastereoisomers (Scheme S6). In our previous study, we found that 4SR,6RS-THP convert to more stable epimers when heated in DMSO. Thus, we carried out additional epimerization step in order to obtain a more diastereoselectively pure product. The subsequent Menshutkin reaction yielded bis-pyridinium salts in the form of a single diastereomer.

2.3.3 Dihydropyran-based mono-QACs

Next, we decided to use the obtained data on the pyran derivatives formation during the MCR to optimize the synthesis of dihydropyrans with trifluoro-substituted groups as a basis for the mono-QACs. The trifluoromethyl group serves as a crucial structural component in numerous fluorinated compounds that possess significant biological and pharmaceutical relevance. As a result, fluorine-containing heterocyclic compounds are now acknowledged as organic molecules exhibiting noteworthy biological activity, with potential utility in both medical and agricultural fields 71, 72. The CF3-dihydropyran was synthesized through a similar MCR involving ethyl 4,4,4-trifluoroacetoacetate as Michael addition component. The method is simple to operate, since the reaction can be carried out at room temperature, and the target product is isolated by simple filtration. N-alkylation of dihydropyran via Menshutkin reaction led to mono-QACs 10-12 (Scheme 3).


Scheme 3. Synthesis of dihydropyrans -based mono-QACs.


2.3.4 Glycoluril-based multi-QACs

Finally, a series of glycoluril-based multi-QACs was synthesized through a four-step synthetic route starting from 2-(2-aminoethoxy)ethan-1-ol (AmEtO). Glycoluril (GU) is a rigid bicyclic bis-urea heterocycle that serves as a key industrial and pharmaceutical building block — most notably as the classical precursor of cucurbituril macrocycles and as the core of the clinically used tranquilizer/nootropic drug mebicar (N,N,N′,N′-tetramethylglycoluril) 73. Its compact tetra-nitrogen bicyclic core represents an attractive, still largely unexplored scaffold for constructing multivalent QACs architectures. In addition, functionalized GU derivatives have attracted growing interest as biologically active molecules, highlighting the potential of the GU scaffold for medicinal chemistry 74, 75. Direct alkylation of GU backbone is problemating, so the heterocyclic linker was assembled synthetically from an amino alcohol, dimethyl carbonate, and glyoxal. Initially, a urea intermediate was prepared and subjected to condensation with glyoxal to afford the tetrahydroxyglycoluril scaffold. The obtained tetrahydroxyglycoluril was converted into a tetrachloride, which was reacted with 4-alkylaminopyridines in a final Menshutkin quaternization step to afford the target multi-QACs 13-17 (Scheme 4).


Scheme 4. Synthesis of glycoluril-based multi-QACs.


2.3.5 Out-of-domain performance verification

The original OOD comparison examines human-guided embeddings, raw MolFormer features and descriptor-based models (Figure 5). In that archived analysis, human-guided embeddings provide the strongest numerical performance among the compared representations in the label-free setting. Here label-free denotes the absence of a species/endpoint code as an input feature, not the absence of numerical target training. Reported classification and ±1-class agreement are retained as historical analyses. They address different losses from quantitative RMSE and are not interchangeable with regression accuracy.

The original zero-shot/few-shot comparison also evaluates adaptation with approximately 40% of the OOD data. In this terminology, zero-shot means that a QAC-trained predictor is evaluated without fitting on the new 17 compounds; it does not mean direct MIC prediction from a source Good/Bad classifier. The few-shot analysis is an exploratory target-adaptation experiment and no longer an untouched OOD test. Its original figure and learning curves are preserved. All new OOD results in Sections 2.5–2.8 instead fit on the 105-QAC cohort and keep all 17 new compounds out of training and selection.


Figure 5. Preserved original OOD and few-shot comparisons. Zero-shot denotes no OOD-target adaptation of the QAC-trained predictor; few-shot uses part of the OOD collection and is exploratory. Historical treatment of the censored measurement is not assumed to match the exact/bound treatment in the new endpoint registry.

2.4 Understanding the new embeddings

How much of the guided representation reflects pretrained geometry, and which of its changes matter for prediction? These questions require separate measurements. Figure 6 combines the representation pathway with actual PCA projections for the 105 QACs. It illustrates the reorganisation of the coordinates; it does not divide the embedding into experimentally identified structural and biological components.


Figure 6. Actual archived raw and human-guided representations of all 105 QACs. The two panels use independent PCA after per-molecule L2 normalisation; their axes are not aligned. Colours and markers denote mono-, bis- and multi-QAC structural classes, not Good/Bad activity. The projections are unsupervised visualisations of archived representations whose source corpora overlap this cohort; they are not held-out predictive or causal evidence.

The archived representation analysis reports linear CKA of 0.933 in-domain and 0.946 on OOD compounds. A linear probe predicts the human-guided coordinates from MolFormer features with R²=0.891 ± 0.037 over five CV folds (mean ± SD). These values show substantial geometric alignment and linear recoverability. Because the guided encoder is itself a function of the MolFormer features, high recoverability is compatible with useful nonlinear reorganisation. The unexplained portion cannot be labelled biological knowledge, and CKA does not establish how much unique activity information either representation contains. The reverse probe gives R²=0.844 ± 0.060 in the same saved five-fold calculation; these are representation-reconstruction scores, not MIC/MBC prediction metrics.

The original combined-feature SHAP analysis reports block attribution totals of 2.93 [2.89,2.97] for MolFormer, 0.76 [0.63,0.89] for the task identifier and 0.64 [0.62,0.65] for the guided embedding, with an embedding-to-MolFormer ratio of 0.22 [0.21,0.22]. These are retained as archive-specific descriptive results. Correlated feature blocks can redistribute attribution, so the ratio is not a causal information fraction and division by the number of coordinates does not make the blocks independent. Predictive ablations and controls are needed to determine whether the representation or its supervisory labels contribute to held-out loss.

The original QAC-only ablation uses quantitative MIC/MBC binned into contrastive classes and is distinct from the full-corpus multi-output model in Table 2. The July notebook reports OOD RMSE of 2.314 for raw features, 2.189 for human-guided embeddings and 2.133 for this QAC-binned ablation. A different May version gives 2.276 for the latter; both are retained in the provenance record. Table 3 instead evaluates vectors reconstructed from the available analysis/encoder_reg_only.pth checkpoint, under the declared new 105-QAC training and 67-exact-endpoint protocol, giving RMSE 2.408 with fresh text codes. Neither that checkpoint’s identity with the July model nor the exact origin of the archive-version gap is established, so these are distinct calculations rather than replacement values. The original post-hoc CausalForestDML analysis reports a residual-based average contrast of −0.015 log2 units with interval [−0.43,+0.32]. It describes the chosen model comparisons under its assumptions, rather than identifying a biological intervention. It is also different from the archived endpoint-resampling bootstrap ΔRMSE analysis. An interval covering zero and the use of assay dilution units do not by themselves prove formal equivalence or absence of a meaningful subgroup effect.

The original conditional-effect summary reports no clearly resolved subgroup advantage on the small OOD set. That observation motivates further work on heterogeneous effects, but 17 compounds from four families provide limited independent support for subgroup claims. Whether measured protocol heterogeneity explains any difference between the supervisory sources remains a hypothesis. Testing it would require context-matched comparisons, annotation information-access records and appropriate resampling of independent molecules or assay contexts.

The original findings therefore motivate a focused predictive interpretation: a compact encoder can reshape pretrained molecular features into a representation useful to a downstream antibacterial predictor, and coarse expert guidance can be competitive with quantitative guidance in the reported configuration. Stronger attribution to the semantic content of human judgement requires controls beyond geometry and attribution. We next examine these controls while keeping the reference architecture and original positive results explicit.

2.5 Reconstructing the reference analysis and defining the generalisation question

The recovered May 24 notebook saves the original multitask R² values, while its split is applied to molecule×task rows with 20% held out, random_state=42 and stratification by task. Other measurements of a test-row molecule can therefore remain in decoder training. This evaluates a different problem from predicting a wholly unseen molecule. It does not invalidate the existence of the saved outputs, and the difference from later grouped scores is not attributed solely to this split: feature extraction, checkpoint state, source exclusions, text vectors and software versions also changed.

We reconstructed nine original-108 configurations from the saved raw, human and QAC-binned features with CatBoost 500 iterations, depth 6 and learning rate 0.05. The two supplied servers independently executed these jobs and reproduced each other’s predictions to within 1e−10. This establishes reproducibility of the declared new reconstruction, not an exact replay of every historical cell. The historical OpenAI vectors were not located; the reconstruction uses the separately documented cached October task vectors. For example, the reconstructed human/text endpoint R² values are 0.728,0.380,0.775 and 0.708, rather than the saved May values. Both sets remain identified in Supporting Information.

To restore the author’s uncertainty-reporting approach, we additionally executed five-fold row-wise KFold with shuffle=True and random_state=42, retaining the saved raw and human features and the recovered CatBoost budget. Six representation/coding combinations required 30 fits. Separate organism and endpoint categorical columns reproduce the April CV coding; native task_id follows the May variant. The text-code human endpoint R² means ± fold SD are 0.512 ± 0.100, 0.449 ± 0.213, 0.717 ± 0.081 and 0.643 ± 0.051. These approximate-reconstruction CV results differ from the historical single-holdout outputs and are shown as their own rows in Tables 1–2. The original task-vector cache remains absent. Row-wise CV can share a molecule across tasks and does not replace the 105-molecule grouped tests or the untouched 17-molecule OOD evaluation.

For new-compound evaluation, we retain all 105 QACs and use fixed five-fold cation and scaffold holdouts, yielding 420 exact endpoint predictions in each regime. The cohort includes 103 distinct cations and 29 cation scaffolds. No target cation or scaffold crosses its corresponding training/test boundary. The archived expert source corpus contains structures from all 105 QAC salts; corpus membership is not proof of training membership for every old checkpoint, and this archived-feature test is not claimed to be source-excluded transfer. The new matched panel in Section 2.6 excludes target cations and their related records before source training.

Table 3 shows the follow-up on archived reference representations. Human/text features give OOD RMSE 2.023 versus 2.245 for raw/text features, whereas their cation/scaffold losses are similar. Literal one-hot, native categorical and text codes have different results; a text-code advantage on OOD is not a universal advantage across splits. The complete endpoint-specific values, including negative R² where present, are retained in SI.

Table 3. Pooled exact-endpoint RMSE for newly executed grouped and OOD validation of archived reference representations. Human features use encoder_borderline_smote.pth; the QAC-binned ablation uses analysis/encoder_reg_only.pth and is not the full-corpus model from Table 2. Per-fold means and SD are reported separately in Table S42; they are not attached to the pooled scores here.

| Representation / coding | Source seeds | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| Raw / categorical | one archived | 1.891 | 2.094 | 2.439 |
| Human / categorical | one archived | 1.894 | 2.098 | 2.229 |
| Raw / text | one archived | 1.894 | 2.101 | 2.245 |
| Human / text | one archived | 1.905 | 2.100 | 2.023 |
| Raw / literal one-hot | one archived | 1.887 | 2.082 | 2.226 |
| Human / literal one-hot | one archived | 1.919 | 2.068 | 2.125 |
| QAC-binned ablation / text | one archived | 1.789 | 2.013 | 2.408 |

2.6 Matched guidance in the compact reference architecture

To test label assignment while retaining the reference encoder widths, we trained six source arms on the same 681 source molecules: 377 training and 304 validation compounds, with QAC/OOD target cations excluded. Human calls, prevalence-matched binary MIC and continuous pooled MIC each have a source-training-only shuffled control. Five paired seeds share initial states, minibatch order and 80 epochs (480 updates). Human and binary MIC share the hard-negative contrastive objective; continuous MIC uses standardised MSE and therefore changes both supervision and objective. No SMOTE, augmentation, early stopping or target-based selection is used in this controlled follow-up; it is not a replay of historical SMOTE training.

The encoder has 691,584 trainable parameters. Including the active contrastive projection gives 741,504 parameters for the binary arms; the encoder plus scalar regression head gives 691,841 for the continuous arms. The source-only auxiliary heads are removed from target decoding. The fixed CatBoost decoder uses the recovered decoder budget across arms, and no OOD outcomes are used for tuning. Table 4 reports the mean of per-seed RMSE rather than the RMSE of an ensemble prediction.

Human, binary-MIC and continuous-MIC cation RMSE values are 1.872,1.865 and 1.858; their OOD values are 2.268,2.276 and 2.474. Human minus continuous MIC on OOD is -0.206 [-0.525, +0.019] under paired source-seed/scaffold resampling, which leaves the direction unresolved at this interval level. Human minus the fixed raw reference is -0.236 [-0.524, -0.016]. These contrasts address prediction under this protocol, not formal equivalence of supervisory sources.

The primary content control is human versus shuffled human labels. Its cation/scaffold/OOD ΔRMSE values are +0.039 [-0.074, +0.159], +0.117 [-0.012, +0.253], +0.096 [-0.143, +0.283]. Human guidance does not beat its shuffled control here. Compression, exposure to the same source feature distribution and BatchNorm running statistics may contribute to the benefit relative to raw features. Noise-induced regularisation and the fit of the chosen encoder/objective are additional candidate explanations, not identified mechanisms. The earlier source-excluded partial-MolFormer experiment resolves a cation benefit for real human labels (ΔRMSE −0.120 [−0.217,−0.043]), but it changes the adaptation procedure and is retained as a separate supporting experiment rather than proof about this compact encoder.

A supplementary task-code check fixes human compact seed 0 and substitutes only the four task vectors. OOD RMSE is 2.314 with the cached text codes, 2.292 with a fixed permutation of those codes and 2.327 with norm-matched random codes; literal one-hot coding gives 2.255. The complete three-regime comparison is in Table S39. With four repeatedly observed tasks and one seed, these point estimates do not establish a semantic advantage of the task descriptions. Generalisation to unseen task descriptions was not tested.

Table 4. Compact reference-architecture controls with native categorical target coding. Mean ± sample SD of complete seed-specific pooled RMSE (five paired source seeds, ddof=1), including the fixed OOD-17 cohort. This is source-seed variability, not fold SD or a 95% CI. Raw features are a single fixed reference without an invented SD.

| Representation / coding | Source seeds | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| Raw reference | fixed raw | 1.868 | 2.116 | 2.504 |
| Untrained compact encoder | five paired | 1.889 ± 0.034 | 2.084 ± 0.063 | 2.313 ± 0.162 |
| Human | five paired | 1.872 ± 0.034 | 2.158 ± 0.050 | 2.268 ± 0.077 |
| Shuffled human | five paired | 1.833 ± 0.049 | 2.041 ± 0.085 | 2.172 ± 0.112 |
| Binary MIC | five paired | 1.865 ± 0.059 | 2.110 ± 0.052 | 2.276 ± 0.095 |
| Shuffled binary MIC | five paired | 1.811 ± 0.037 | 2.062 ± 0.017 | 2.094 ± 0.088 |
| Continuous MIC | five paired | 1.858 ± 0.031 | 2.168 ± 0.018 | 2.474 ± 0.131 |
| Shuffled continuous MIC | five paired | 1.935 ± 0.051 | 2.186 ± 0.056 | 2.419 ± 0.150 |
| Human weights reset; BN retained | five paired | 1.888 ± 0.020 | 2.108 ± 0.035 | 2.384 ± 0.120 |


Figure 7. Absolute-error distributions for the compact encoder with real and shuffled source labels, using a shared y-axis. Each value is a compound/endpoint mean absolute error over five source seeds; distributions contain 420 QAC or 67 uncensored OOD endpoints. Dots denote medians; all tails are retained. The violins are descriptive, while clustered performance contrasts are given in the text and SI.

2.7 Decoder and direct-adaptation alternatives

We tested TabPFN v2, Google TabFM and AutoGluon on the saved raw and human-guided representations (80–82). Each endpoint is fitted separately on the same target folds and untouched OOD collection. The modern models use training-only PCA with 32 components and their declared model-specific budgets; the CatBoost reference uses the full vectors. These are practical pipeline comparisons rather than identical-capacity or identical-compute experiments. The completed 264 fits comprise three decoders × two representations × four endpoints × eleven regimes (five cation folds, five scaffold folds and one full-QAC/OOD fit). Table 5 includes all raw/guided outcomes, rather than selecting the preferred representation from OOD performance.

Relative to archived human/text CatBoost (Table 3), no tested tabular pipeline has lower point-estimate loss in all three regimes. Against the separate-endpoint raw CatBoost reference in Table 5 and Figure 8, however, TabFM gives lower cation/scaffold/OOD RMSE (1.903/2.080/2.118 versus 1.916/2.086/2.208). Modern decoders can therefore improve that specific pipeline, while human/text CatBoost retains the lower OOD point estimate of 2.023. TabPFN with raw features gives OOD RMSE 2.058 versus 2.165 with human-guided features; AutoGluon gives 2.163 versus 2.081, showing decoder-dependent ordering. These are point comparisons, not tests of statistical superiority. Chemprop’s graph benchmark (84) and RDKit alternatives on the same 105/17 target registers remain in SI and are not relabelled as compact-encoder experiments.

Table 5. Separate-endpoint decoders on archived reference representations. Values are pooled exact-endpoint RMSE from one source checkpoint. Modern pipelines include train-only PCA32. Five-fold score means and SD are reported separately in Table S42; the single OOD fit has no fold or source-seed SD.

| Separate-endpoint decoder | Representation | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| CatBoost | Raw | 1.916 | 2.086 | 2.208 |
| CatBoost | Human-guided | 1.930 | 2.083 | 2.076 |
| TabPFN v2 | Raw | 1.968 | 2.072 | 2.058 |
| TabPFN v2 | Human-guided | 2.018 | 2.132 | 2.165 |
| TabFM | Raw | 1.903 | 2.080 | 2.118 |
| TabFM | Human-guided | 2.018 | 2.104 | 2.178 |
| AutoGluon | Raw | 1.987 | 2.131 | 2.163 |
| AutoGluon | Human-guided | 2.062 | 2.161 | 2.081 |


Figure 8. Modern decoder comparisons on the saved reference features, with separate endpoint models for every method. Points show pooled RMSE on exact endpoints only (67 uncensored OOD values); raw and human-guided representations are shown for all methods. Each pipeline uses one archived source checkpoint; source-seed variability is not estimated and no uncertainty bars are shown. The x-axis starts above zero to show the observed range. Differences between preprocessing and model budgets are described in the text.

To assess fine-tuning rather than assume it is undesirable, the separate direct-prediction experiment compares a pretrained frozen linear head, LoRA, full backbone fine-tuning and source-human-guided partial fine-tuning (79). The same three source/target seeds are used for the two human-guided prediction routes in Table 6. Full direct fine-tuning gives cation RMSE 1.863 but OOD RMSE 3.032. The partial-human direct predictor gives OOD 2.412, versus 2.106 when that guided representation is frozen and decoded with CatBoost. This supports the two-stage route under the declared budget. It does not show that full fine-tuning is generally poor, nor is the partial backbone the external compact reference encoder.

Table 6. Separate completed backbone-adaptation comparison: mean ± sample SD of complete seed-specific pooled RMSE over three paired source/target runs (ddof=1). The two human prediction routes use the same source seeds 0–2. Variability is over repeated training runs, not CV folds or a 95% CI.

| Backbone experiment / route | Paired seeds | Cation CV | Scaffold CV | OOD-17 |
| --- | --- | --- | --- | --- |
| Pretrained / frozen linear head | three paired | 2.013 ± 0.006 | 1.986 ± 0.003 | 2.560 ± 0.206 |
| Pretrained / direct LoRA | three paired | 2.040 ± 0.049 | 2.089 ± 0.012 | 2.756 ± 0.172 |
| Pretrained / direct full FT | three paired | 1.863 ± 0.045 | 1.970 ± 0.026 | 3.032 ± 0.408 |
| Human partial / direct prediction | three paired | 1.797 ± 0.057 | 1.834 ± 0.058 | 2.412 ± 0.088 |
| Human partial / frozen CatBoost | same seeds 0–2 | 1.743 ± 0.031 | 1.819 ± 0.044 | 2.106 ± 0.071 |

2.8 Learned updates, label content and the scope of causality

For the compact encoder, a parameter-only reset restores the initial learned parameters while keeping the trained BatchNorm running means and variances. A complete initial-state reference also restores those buffers. With the downstream decoder refitted under the same folds, parameter-only reset minus intact human cation/scaffold/OOD ΔRMSE is +0.016 [-0.091, +0.114], -0.051 [-0.153, +0.059], +0.116 [-0.056, +0.336]. All these scaffold-clustered intervals include zero. Thus this experiment does not resolve a necessary contribution of the compact encoder’s learned parameter updates. The retained BatchNorm state can still carry source-training information, so parameter-only reset is not described as removal of all learned knowledge.

The distinct partial-backbone rewind experiment reports a cation loss increase of +0.109 [+0.037,+0.201] on restoring learned weights. Its OOD interval is +0.243 [−0.067,+0.582]. These results concern an intervention on a computational prediction pipeline: they can test whether a particular learned update contributes to held-out loss under fixed controls. They do not identify antibacterial mechanisms or demonstrate that a named chemical concept was learned (83). Real-versus-shuffled source labels test supervisory assignment; weight resets test update dependence; source exclusions test transfer. Evidence for independent human knowledge additionally depends on annotation information access in H1–H7.

A causal claim is consequently restricted to the declared computational intervention and the contrasts its uncertainty resolves. The full-corpus quantitative model, original assay-context heterogeneity and 17-compound subgroup analysis remain distinct evidence streams. Neither pointwise intervals covering zero nor comparison with a twofold dilution justify a formal equivalence conclusion without a justified equivalence margin and appropriate design. All hypotheses and unresolved provenance items are mapped to their analyses in Supporting Information.

3. Conclusion

This study combines expert-guided molecular representation learning with quantitative prediction and the synthesis and evaluation of 17 new QACs. The original multitask results remain a substantive part of the evidence: the human-guided text-code model reports R² of 0.75,0.68,0.59 and 0.77 and is competitive with the reported full-corpus quantitative-guided model. These values have partial saved-notebook provenance and are retained alongside, rather than replaced by, new validation results.

First, the compact external encoder gives a concrete route for adapting frozen molecular features. Its predictive usefulness depends on the source supervision, task encoding and downstream decoder. The new OOD comparison of archived human-guided and raw text-code features gives RMSE 2.023 versus 2.245. That fixed-checkpoint result supports predictive utility in this setting, while grouped evaluation demonstrates that the original task-row holdout answers a different generalisation question from prediction on new cations and scaffolds.

Second, the controlled compact-encoder experiment does not establish that human label content is responsible for its predictive benefit. Human guidance improves OOD loss relative to the fixed raw reference, but does not outperform shuffled human labels, and parameter-reset intervals cover zero. Separate partial-backbone experiments resolve a benefit under a different adaptation procedure. These findings support a conditional research programme for human guidance, not universal superiority, a guaranteed measurement-replacement rate or a proof of biological causality.

Third, modern decoders and direct fine-tuning provide necessary context for the practical choice of model. Relative to the archived human/text CatBoost reference, none of the tested tabular pipelines improves all three point-estimate losses; TabFM nevertheless improves the separate-endpoint raw CatBoost baseline. Full fine-tuning is competitive on cation holdout but performs poorly on OOD compounds in the declared direct-prediction budget. The central conclusion is therefore about the usefulness and limits of representation guidance in a small antibacterial dataset. Establishing an independent human-information channel, confirming the full-corpus quantitative model and assessing unseen assay contexts remain essential next steps.

4. Experimental protocol

4.1 Chemistry

4.1.1 General information

Аll starting reagents were obtained from commercial suppliers and were used without further purification. All solvents used were reagent grade and distilled prior to application. Air sensitive reactions were performed under high purity argon atmosphere. Thin-layer chromatography was performed using silica gel 60 F254 aluminum sheets under UV light. IR spectra were recorded with a Bruker ALPHA-T FT-IR spectrometer in KBr pellets. HR-ESI-MS were recorded on a Bruker microTOF II instrument (Bruker Daltonik GmbH, Bremen, Germany); external or internal calibration was performed with electrospray calibrant solution (Fluka). All melting points were measured with a Stuart SMP30 melting point apparatus and are uncorrected. 1H and 13C NMR spectra were recorded with a Bruker AM300 at ambient temperature in Dimethyl sulfoxide-d₆ (DMSO-d6) or Chloroform-d (CDCl3) solutions. The NMR, HRMS and FT-IR spectra of the newly synthesized compounds can be found in the supporting information.

4.1.2 Synthesis and Characterization of Substrates and Products

Synthesis of 5,5'-(pentane-1,5-diylbis(oxy))bis(2-(hydroxymethyl)-4H-pyran-4-one) A:

To a solution of kojic acid (1.847 g, 13 mmol) in anhydrous DMF (25 mL) was added K2CO3 (1.794 g, 13 mmol). The suspension was stirred at 60 oC for 1 h. 1,5-Dibromopentane (1.356 g, 5.9 mmol) was added and the mixture was stirred at 80 oC for 24 h. Result of reaction was confirmed by TLC (MeOH/CHCl3 1:10). The solvent was removed under reduced pressure. Distilled water (20 mL) was added to the crude residue, and the mixture was stirred at RT for 2 h. Formed precipitates were filtrated through a glass filter, washed with acetone (20 mL), and dried under a vacuum to afford sand yellow solid product X (1.46 g, 4.1 mmol, 70% yield).

C17H20O8; M. w. 352.339; Sand yellow solid; M. p. 143–145°C; 1H NMR (300 MHz, DMSO-d6): δ 8.10 (s, 2H, 2CH), 6.30 (s, 2H, 2CH), 5.69 (br s, 2H, 2OH), 4.30 (s, 4H, 2CH2), 3.83 (t, J = 6.3 Hz, 4H, 2CH2), 1.73 (p, J = 7.0 Hz, 4H, 2CH2), 1.58-1.44 (m, 2H, CH2) ppm; 13C NMR (75 MHz, DMSO-d6): δ 173.1, 167.9, 147.1, 140.1, 110.9, 68.7, 59.3, 28.2, 21.9 ppm; HRMS (ESI): calcd for C17H20O8 375.1050, found 375.1051.

Synthesis of 1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(alkylamino)pyridin-1-ium) dichlorides 1-4:

Compound A (1.33 g, 3.77 mmol) was dissolved in 25 ml of chloroform. The resulting suspension was cooled in an ice bath, and a solution of thionyl chloride (1.094 mL, 15.08 mmol) in 7 mL of CHCl3 was added dropwise under stirring. The reaction mixture was then heated under reflux with stirring for 24 hours. Progress of the reaction was monitored by TLC (MeOH:CHCl3, 1:10). Upon completion, the reaction mixture was concentrated and dried using a rotary evaporator. The residue was resuspended in 5 mL of chloroform and filtered through a Schott filter. After solvent evaporation, brown powder was obtained. The obtained brown powder (0.2 g, 0.5 mmol) and 4-alkylaminopyridine (1.1 mmol) were dissolved in 7 ml of acetonitrile. The resulting mixture was heated under reflux with stirring for 24 hours. Upon completion, the reaction was cooled to room temperature, and the solvent was evaporated under vacuum. The crude residue was washed with acetone (15 ml) and dried under a vacuum to afford light brown solid.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(octylamino)pyridin-1-ium) dichloride (1):

C43H62Cl2N4O6; M. w. 730.989; light brown solid (0.346 g, 0.474 mmol, 94% yield); M. p. 165–168°C; IR (neat/cm−1): 3429, 3212, 2927, 2855, 1652, 1591, 1189; 1H NMR (300 MHz, DMSO-d6): δ 9.32 (t, J = 5.7 Hz, 2H, 2NH), 8.38 (d, J = 7.4 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.09-6.95 (m, 4H, 2CHpy), 6.46 (s, 2H, 2CH), 5.39 (s, 4H, 2CH2), 3.80 (t, J = 6.4 Hz, 4H, 2CH2N+), 3.32-3.24 (m, 4H, 2CH2), 1.78-1.18 (m, 30H, 15CH2), 0.85 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.6, 160.3, 157.0, 147.3, 143.9, 141.5, 140.6, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.1, 28.6, 28.0, 27.8, 26.2, 22.0, 21.9, 13.9 ppm; HRMS (ESI): calcd for C43H62N4O6 365.2329, found 365.2339.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(nonylamino)pyridin-1-ium) dichloride (2):

C45H66Cl2N4O6; M. w. 759.044; light brown solid (0.357 g, 0.47 mmol, 94% yield); M. p. 207–210°C; IR (neat/cm−1): 3432, 3211, 2926, 2855, 1653, 1591, 1190; 1H NMR (300 MHz, DMSO-d6): δ 9.33 (t, J = 5.4 Hz, 2H, 2NH), 8.38 (d, J = 7.3 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.010-6.96 (m, 4H, 2CHpy), 6.47 (s, 2H, 2CH), 5.40 (s, 4H, 2CH2), 3.81 (t, J = 6.3 Hz, 4H, 2CH2N+), 3.33-3.24 (m, 4H, 2CH2), 1.80-1.17 (m, 34H, 17CH2), 0.86 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.5, 160.3, 157.0, 147.2, 143.9, 141.4, 140.6, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.2, 28.8, 28.6, 28.5, 28.0, 27.8, 26.2, 22.0, 21.9, 13.8 ppm; HRMS (ESI): calcd for C45H66N4O6 379.2486, found 379.2493.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(decylamino)pyridin-1-ium) dichloride (3):

C47H70Cl2N4O6; M. w. 787.098; light brown solid (0.342 g, 0.434 mmol, 87% yield); M. p. 169–172°C; IR (neat/cm−1): 3432, 3210, 2926, 2854, 1653, 1591, 1190; 1H NMR (300 MHz, DMSO-d6): δ 9.25 (t, J = 5.6 Hz, 2H, 2NH), 8.37 (d, J = 7.2 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.08-6.96 (m, 4H, 2CHpy), 6.46 (s, 2H, 2CH), 5.39 (s, 4H, 2CH2), 3.81 (t, J = 6.3 Hz, 4H, 2CH2N+), 3.32-3.24 (m, 4H, 2CH2), 1.80-1.17 (m, 38H, 19CH2), 0.85 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.5, 160.3, 157.0, 147.2, 143.9, 141.4, 140.6, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.2, 28.93, 28.91, 28.6, 28.0, 27.8, 26.2, 22.0, 21.9, 13.9 ppm; HRMS (ESI): calcd for C47H70N4O6 393.2642, found 393.2633.

1,1'-(((pentane-1,5-diylbis(oxy))bis(4-oxo-4H-pyran-5,2-diyl))bis(methylene))bis(4-(dodecylamino)pyridin-1-ium) dichloride (4):

C51H78Cl2N4O6; M. w. 843.206; light brown solid (0.375 g, 0.445 mmol, 89% yield); M. p. 215–217°C; IR (neat/cm−1): 3429, 3211, 2925, 2853, 1654, 1591, 1191; 1H NMR (300 MHz, DMSO-d6): δ 9.32 (t, J = 5.7 Hz, 2H, 2NH), 8.38 (d, J = 7.4 Hz, 2H, CHpy), 8.24-8.14 (m, 4H, 2CHpy + 2CH), 7.10-6.95 (m, 4H, 2CHpy), 6.46 (s, 2H, 2CH), 5.40 (s, 4H, 2CH2), 3.81 (t, J = 6.2 Hz, 4H, 2CH2N+), 3.34-3.22 (m, 4H, 2CH2), 1.79-1.16 (m, 46H, 23CH2), 0.85 (t, J = 6.9 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 172.5, 160.3, 157.0, 147.2, 143.9, 141.4, 140.5, 114.2, 110.5, 105.5, 68.7, 55.8, 42.3, 31.2, 29.0, 28.9, 28.6, 28.0, 27.8, 26.2, 22.0, 21.9, 13.9 ppm; HRMS (ESI): calcd for C51H78N4O6 421.2955, found 421.2942.

Synthesis of Methyl (4SR,6RS)-5,5-dicyano-2-methyl-4,6-(3-pyridine)-1,4,5,6-tetrahydropyridine-3-carboxylate B:

A mixture of 3-pyridinecarboxaldehyde (6 mmol), malononitrile (3 mmol), methyl acetoacetate (3 mmol) and ammonium acetate (12 mmol, 924 mg) was refluxed in ethanol (10 ml) for 4 h. Formed precipitates were quickly filtrated through a glass filter, and dried under a vacuum to afford white solid product B (0.67 g, 1.8 mmol, 62%).

C20H17N5O2; M. w. 359.39; White solid; M. p. 200–203°C; 1H NMR (300 MHz, DMSO-d6): δ = 8.81 (d, J = 8 Hz, 1H, Ar), 8.72 (dd, J = 4.8 Hz, J1 = 1.5 Hz, 1H, Ar), 8.56–8.53 (m, 2H, Ar), 8.03 (dt, J = 8 Hz, J1 = 1.7 Hz, 1H, Ar), 7.8 (s, 1H, NH), 7.68 (dt, J = 8 Hz, J1 = 1.6 Hz, 1H, Ar), 7.6 (dd, J = 8 Hz, J1 = 4.8 Hz, 1H, Ar), 7.43 (dd, J = 8 Hz, J1 = 4.8 Hz, 1H, Ar), 5.42 (s, 1H, CH), 4.95 (s, 1H, CH), 3.16 (s, 3H, OCH3), 2.36 (s, 3H, CH3) ppm.

Synthesis of Methyl (4RS,6RS)-5,5-dicyano-2-methyl-4,6-(3-pyridine)-1,4,5,6-tetrahydropyridine-3-carboxylate C:

Tetrahydropyridine B (1.39 mmol, 500 mg) in anhydrous DMSO (20 ml) was heated to 80-85 oC for 11 h. After heating, the mixture was concentrated under reduced pressure, water (25 ml) was added to the crude residue. Formed precipitates were filtrated through a glass filter and dried under a vacuum. Compound C was purified by recrystallization in methanol (0.38 g, 1 mmol, 76%).

C20H17N5O2; M. w. 359.39; White solid; M. p. 245–248°C; 1H NMR (300 MHz, DMSO-d6): δ = 8.74-8.63 (m, 3H, Ar), 8.60 (d, J = 4.8 Hz, 1H, Ar), 8.09 (s, 1H, NH), 7.93 (d, J = 8.0 Hz, 1H, Ar), 7.80 (d, J = 7.9 Hz, 1H, Ar), 7.56 (dd, J = 8.1 Hz, J1 = 4.8 Hz, 1H, Ar), 7.47 (dd, J = 7.9 Hz, J1 = 4.8 Hz, 1H, Ar), 5.08 (s, 1H, CH), 4.67 (s, 1H, CH), 3.45 (s, 3H, OCH3), 2.52 (s, 3H, CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 166.2, 154.7, 151.2, 150.8, 149.7, 149.4, 137.3, 136.5, 134.6, 129.5, 123.6, 123.5, 113.6, 112.9, 89.0, 53.3, 50.6, 43.4, 42.4, 19.8 ppm; HRMS (ESI): calcd for C20H18N5O2 360.1455, found 360.1458.

(2'R,4'R)-3',3'-Dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-dialkyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-ium dibromides 5-9:

Halogenoalkane (2 mmol) was added to a solution of C (0.5 mmol, 0.200 g) in dry acetonitrile (3 mL). The mixture was stirred and heated to reflux for 24 h. Result of reaction was confirmed by TLC (ethyl acetate/petroleum ether 1:1). After solvent evaporation under reduced pressure, ethyl acetate (5 mL) was added to the reaction residue and the mixture was vigorously stirred for 1 h. Formed precipitates were quickly filtrated through a glass filter, and dried under a vacuum to afford white solid product.

(2'R,4'R)-3',3'-Dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-dioctyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-ium dibromide (5):

C36H51Br2N5O2; M. w. 585.83; White solid (0.258 g, 0.44 mmol, 88% yield); M. p. 213-216 °C; IR (neat/cm−1): 3438, 3188, 2927, 2856, 2250, 1668, 1252; 1H NMR (300 MHz, DMSO-d6): δ 9.55 (s, 1H, NH), 9.33 (d, J = 6.1 Hz, 1H, CHpy), 9.29-9.20 (m, 2H, 2CHpy), 8.87-8.74 (m, 2H, 2CHpy), 8.50 (s, 1H, CHpy), 8.45-8.28 (m, 2H, 2CHpy), 5.46 (s, 1H, CH), 5.27 (s, 1H, CH), 4.85-4.62 (m, 4H, 2CH2N+), 3.47 (s, 3H, OCH3), 2.57 (s, 3H, CH3), 1.97-1.91 (m, 4H, 2CH2), 1.31-1.20 (m, 20H, 10CH2), 0.92-0.80 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.5, 146.3, 145.3, 145.2, 144.8, 144.7, 139.2, 133.8, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.1, 51.7, 50.7, 42.5, 41.9, 31.08, 31.02, 30.6, 30.5, 28.38, 28.31, 25.2, 25.1, 21.98, 21.96, 20.1, 13.8 ppm; HRMS (ESI): calcd for C36H51N5O2 292.7016, found 292.7010.

(2'R,4'R)-3',3'-Dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-dinonyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-ium dibromide (6):

C38H55Br2N5O2; M. w. 613.89; White solid (0.264 g, 0.43 mmol, 86% yield); M. p. 214-217 °C; IR (neat/cm−1): 3430, 3186, 2927, 2855, 2251, 1668, 1253; 1H NMR (300 MHz, DMSO-d6): δ 9.55 (s, 1H, NH), 9.33 (d, J = 6.1 Hz, 1H, CHpy), 9.30-9.20 (m, 2H, 2CHpy), 8.87-8.74 (m, 2H, 2CHpy), 8.50 (s, 1H, CHpy), 8.45-8.28 (m, 2H, 2CHpy), 5.46 (s, 1H, CH), 5.28 (s, 1H, CH), 4.86-4.65 (m, 4H, 2CH2N+), 3.48 (s, 3H, OCH3), 2.58 (s, 3H, CH3), 1.97-1.91 (m, 4H, 2CH2), 1.32-1.16 (m, 24H, 12CH2), 0.92-0.81 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.5, 146.3, 145.3, 145.1, 144.79, 144.70, 139.2, 133.8, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.0, 51.7, 50.7, 42.4, 41.8, 31.15, 31.12, 30.6, 30.5, 28.66, 28.6, 28.5, 28.4, 28.3, 25.2, 25.1, 22.0, 21.9, 20.1, 13.8 ppm; HRMS (ESI): calcd for C38H53N5O2 306.7172, found 306.7181.

(2'R,4'R)-3',3'-Dicyano-1,1''-didecyl-5'-(methoxycarbonyl)-6'-methyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-diium bromide (7):

C40H59Br2N5O2; M. w. 641.94; White solid (0.289 g, 0.45 mmol, 90% yield); M. p. 218-221 °C; IR (neat/cm−1): 3434, 3189, 2926, 2855, 2249, 1668, 1251; 1H NMR (300 MHz, DMSO-d6): δ 9.54 (s, 1H, NH), 9.34 (d, J = 6.1 Hz, 1H, CHpy), 9.30-9.23 (m, 2H, 2CHpy), 8.88-8.76 (m, 2H, 2CHpy), 8.50 (s, 1H, CHpy), 8.46-8.32 (m, 2H, 2CHpy), 5.48 (s, 1H, CH), 5.26 (s, 1H, CH), 4.82-4.70 (m, 4H, 2CH2N+), 3.50 (s, 3H, OCH3), 2.59 (s, 3H, CH3), 1.99-1.93 (m, 4H, 2CH2), 1.36-1.19 (m, 28H, 14CH2), 0.94-0.84 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.7, 156.1, 146.6, 146.3, 145.3, 145.2, 144.7, 139.3, 133.9, 128.1, 128.0, 112.3, 111.9, 87.7, 61.3, 61.1, 51.8, 50.8, 42.5, 41.9, 31.2, 30.6, 30.5, 28.8, 28.79, 28.76, 28.70, 28.6, 28.3, 25.2, 22.0, 20.1, 13.9 ppm; HRMS (ESI): calcd for C40H59N5O2 320.7329, found 320.7327.

(2'R,4'R)-3',3'-dicyano-5'-(methoxycarbonyl)-6'-methyl-1,1''-diundecyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-diium bromide (8):

C42H63Br2N5O2; M. w. 669.99; White solid (0.281 g, 0.42 mmol, 84% yield); M. p. 215-218 °C; IR (neat/cm−1): 3433, 3187, 2926, 2854, 2249, 1669, 1251; 1H NMR (300 MHz, DMSO-d6): δ 9.55 (s, 1H, NH), 9.33 (d, J = 6.1 Hz, 1H, CHpy), 9.29-9.20 (m, 2H, 2CHpy), 8.87-8.74 (m, 2H, 2CHpy), 8.51 (s, 1H, CHpy), 8.44-8.28 (m, 2H, 2CHpy), 5.45 (s, 1H, CH), 5.28 (s, 1H, CH), 4.85-4.64 (m, 4H, 2CH2N+), 3.47 (s, 3H, OCH3), 2.56 (s, 3H, CH3), 1.98-1.90 (m, 4H, 2CH2), 1.31-1.14 (m, 32H, 16CH2), 0.91-0.81 (m, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.5, 146.3, 145.3, 145.2, 144.8, 144.7, 139.2, 133.8, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.1, 51.7, 50.7, 42.5, 41.9, 31.2, 30.6, 30.5, 28.9, 28.89, 28.83, 28.7, 28.68, 28.64, 28.3, 25.2, 25.1, 22.0, 20.1, 13.8 ppm; HRMS (ESI): calcd for C42H63N5O2 334.7485, found 334.7497.

(2'R,4'R)-3',3'-dicyano-1,1''-didodecyl-5'-(methoxycarbonyl)-6'-methyl-1',2',3',4'-tetrahydro-[3,2':4',3''-terpyridine]-1,1''-diium bromide (9):

C44H67Br2N5O2; M. w. 698.05; White solid (0.321 g, 0.46 mmol, 92% yield); M. p. 229-232 °C; IR (neat/cm−1): 3438, 3189, 2925, 2853, 2249, 1669, 1250; 1H NMR (300 MHz, DMSO-d6): δ 9.52 (s, 1H, NH), 9.31 (d, J = 6.1 Hz, 1H, CHpy), 8.85-8.72 (m, 2H, 2CHpy), 8.47 (s, 1H, CHpy), 8.44-8.26 (m, 2H, 2CHpy), 5.44 (s, 1H, CH), 5.24 (s, 1H, CH), 4.81-4.63 (m, 4H, 2CH2N+), 3.46 (s, 3H, OCH3), 2.56 (s, 3H, CH3), 1.96-1.90 (m, 4H, 2CH2), 1.36-1.13 (m, 36H, 18CH2), 0.85 (t, J = 6.5 Hz, 6H, 2CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.6, 156.0, 146.6, 146.3, 145.3, 145.2, 144.7, 139.2, 133.9, 128.1, 127.9, 112.3, 111.9, 87.7, 61.3, 61.1, 51.7, 50.7, 42.4, 41.9, 31.2, 30.6, 30.5, 28.96, 28.91, 28.8, 28.7, 28.6, 28.3, 25.27, 25.1, 22.0, 20.1, 13.9 ppm; HRMS (ESI): calcd for C44H67N5O2 348.7642, found 348.7636.

Synthesis of Ethyl 6-amino-5-cyano-2-methoxy-4-(pyridin-3-yl)-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-3-carboxylate D:

A mixture of 3-pyridinecarboxaldehyde (2 mmol), malononitrile (2 mmol), ethyl 4,4,4-trifluoroacetoacetate (2 mmol) and ammonium acetate (2 mmol, 154 mg) was stirred in methanol (5 мл) for 6 h. The compound D was isolated by simple filtration (0.47 g, 1.26 mmol, 63% yield).

C16H16F3N3O4; M. w. 371,316; White solid; M. p. 196–199°C; 1H NMR (300 MHz, DMSO-d6): δ 8.54-8.46 (m, 2H, 2CHpy), 7.82 (d, J = 7.9 Hz, 1H, CHpy), 7.38 (t, J = 5.9 Hz, 1H, CHpy), 7.11 (s, 2H, NH2), 4.00 (d, J = 11.9 Hz, 1H, CH), 3.90 (q, J = 7.1 Hz, 2H, CH2), 3.34 (s, 3H, OCH3), 3.23 (d, J = 11.9 Hz, 1H, CH), 0.90 (t, J = 7.1 Hz, 3H, CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 166.4, 159.3, 150.0, 149.1, 136.1, 134.6, 123.6, 121.3 (q, J = 291.1 Hz, CF3), 119.0, 96.1 (q, J = 31.9 Hz, C(CF3)), 60.9, 56.5, 52.5, 48.8, 36.3, 13.4 ppm; HRMS (ESI): calcd for C16H16F3N3O4 372.1166, found 372.1179.

Synthesis of 3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-alkylpyridin-1-ium bromides 10-12:

Halogenoalkane (2 mmol) was added to a solution of D (0.5 mmol, 0.200 g) in dry acetonitrile (3 mL). The mixture was stirred and heated to reflux for 24 h. Result of reaction was confirmed by TLC (ethyl acetate/petroleum ether 1:1). After solvent evaporation under reduced pressure, ethyl acetate (5 mL) was added to the reaction residue and the mixture was vigorously stirred for 1 h. Formed precipitates were quickly filtrated through a glass filter, and dried under a vacuum to afford white solid product.

3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-nonylpyridin-1-ium bromide (10):

C25H35BrF3N3O4; M. w. 578,471; White solid (0.257 g, 0.44 mmol, 89% yield); M. p. 178–180; IR (neat/cm−1): 3258, 3094, 2929, 2857, 2194, 1738, 1636, 1600; 1H NMR (300 MHz, DMSO-d6): δ 9.35 (s, 1H, CHpy), 9.13 (d, J = 6.0 Hz, 1H, CHpy), 8.80 (d, J = 8.1 Hz, 1H, CHpy), 8.29-8.19 (m, 1H, CHpy), 7.39 (s, 2H, NH2), 4.63 (t, J = 7.1 Hz, 2H, 2CH2N+), 4.32 (d, J = 11.9 Hz, 1H, CH), 4.06-3.82 (m, 2H, OCH2), 3.61-3.52 (m, 4H, CH + OCH3), 1.96-1.85 (m, 2H, CH2), 1.27-1.21 (m, 12H, 6CH2), 0.98 (t, J = 7.1 Hz, 3H, CH3), 0.87 (t, J = 6.3 Hz, CH3) ppm; 13C NMR (75 MHz, DMSO-d6): δ 165.9, 159.6, 145.8, 144.7, 144.6, 140.5, 128.1, 121.1 (q, J = 291.3 Hz, CF3), 118.7, 96.2 (q, J = 33.2 Hz, C(CF3)), 61.4, 60.9, 54.9, 52.7, 47.6, 36.1, 31.1, 30.6, 28.6, 28.4, 28.3, 25.0, 22.0, 13.8, 13.5 ppm; HRMS (ESI): calcd for C25H35F3N3O4 498.2574, found 498.2568.

3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-undecylpyridin-1-ium bromide (11):

C27H39BrF3N3O4; M. w. 606,525; White solid (0.242 g, 0.39 mmol, 84% yield); M. p. 162–165°C; IR (neat/cm−1): 3258, 3091, 2928, 2856, 2194, 1738, 1635, 1600; 1H NMR (300 MHz, DMSO-d6): δ 9.35 (s, 1H, CHpy), 9.14 (d, J = 6.0 Hz, 1H, CHpy), 8.80 (d, J = 8.1 Hz, 1H, CHpy), 8.24 (t, J = 7.1 Hz, 1H, CHpy), 7.37 (s, 2H, NH2), 4.63 (t, J = 7.1 Hz, 2H, 2CH2N+), 4.32 (d, J = 12.0 Hz, 1H, CH), 4.06-3.82 (m, 2H, OCH2), 3.62-3.50 (m, 4H, CH + OCH3), 1.96-1.85 (m, 2H, CH2), 1.36-1.13 (m, 16H, 8CH2), 0.98 (t, J = 7.1 Hz, 3H, CH3), 0.87 (t, J = 6.3 Hz, CH3); 13C NMR (75 MHz, DMSO-d6): δ 165.9, 159.5, 145.8, 144.7, 144.6, 140.5, 128.7, 121.1 (q, J = 290.4 Hz, CF3), 118.7, 96.2 (q, J = 32.8 Hz, C(CF3)), 61.4, 60.9, 54.9, 52.7, 47.6, 36.1, 31.2, 30.6, 28.9, 28.8, 28.7, 28.6, 28.3, 25.0, 22.0, 13.8, 13.5 ppm; HRMS (ESI): calcd for C27H39F3N3O4 526.2887, found 526.2879.

3-(6-amino-5-cyano-3-(ethoxycarbonyl)-2-methoxy-2-(trifluoromethyl)-3,4-dihydro-2H-pyran-4-yl)-1-dodecylpyridin-1-ium bromide (12):

C28H41BrF3N3O4; M. w. 620,552; White solid (0.251 g, 0.4 mmol, 81% yield); M. p. 175–177°C; IR (neat/cm−1): 3259, 3084, 2927, 2855, 2193, 1738, 1634, 1600; 1H NMR (300 MHz, DMSO-d6): δ 9.35 (s, 1H, CHpy), 9.13 (d, J = 6.0 Hz, 1H, CHpy), 8.80 (d, J = 8.1 Hz, 1H, CHpy), 8.29-8.18 (m, 1H, CHpy), 7.37 (s, 2H, NH2), 4.63 (t, J = 7.1 Hz, 2H, 2CH2N+), 4.32 (d, J = 12.0 Hz, 1H, CH), 4.06-3.82 (m, 2H, OCH2), 3.61-3.52 (m, 4H, CH + OCH3), 1.96-1.85 (m, 2H, CH2), 1.35-1.13 (m, 18H, 9CH2), 0.98 (t, J = 7.1 Hz, 3H, CH3), 0.88 (t, J = 6.3 Hz, CH3); 13C NMR (75 MHz, DMSO-d6): δ 166.0, 159.6, 145.8, 144.8, 144.6, 140.5, 128.1, 121.2 (q, J = 291.9 Hz, CF3), 119.0, 96.3 (q, J = 31.7 Hz, C(CF3)), 61.4, 60.9, 54.9, 52.7, 47.6, 36.1, 31.2, 30.7, 28.98, 28.95, 28.8, 28.7, 28.6, 28.3, 25.1, 22.0, 13.9, 13.5 ppm; HRMS (ESI): calcd for C28H41F3N3O4 540.3044, found 540.3022.

Synthesis of ethyl (2-(2-hydroxyethoxy)ethyl)carbamate (X)

A round-bottom flask equipped with a Dean–Stark apparatus was charged with diethyl carbonate (42 mmol) and 2-(2-aminoethoxy)ethan-1-ol (85 mmol). The reaction mixture was stirred at 125°C for 24 h and then heated under reflux at 150 °C for 4 days. The product was purified by column chromatography (EtOAc/MeOH, 8:1) and obtained as an orange oil in 75% yield (31.5 mmol, 5.58 g).

C7H15NO4; M. w. 177.200; orange oil; 1H NMR (300 MHz, DMSO-d6) δ 7.13 – 7.03 (m, 1H, NH), 4.59 (t, J = 5.5 Hz, 1H, OH), 3.99 (q, J = 7.1 Hz, 2H, СH2), 3.50 (q, J = 5.3 Hz, 2H, CH2), 3.45 – 3.37 (m, 4H, 2CH2), 3.13 (q, J = 5.9 Hz, 2H, 2CH2), 1.16 (t, J = 7.1 Hz, 3H, CH3).

1,3-bis(2-(2-hydroxyethoxy)ethyl)urea (X)

Ethyl(2-(2-hydroxyethoxy)ethyl)carbamate (9 mmol) and 2-(2-aminoethoxy)ethan-1-ol (10 mmol) were placed in a round-bottom flask equipped with a Dean–Stark apparatus. The reaction mixture was stirred at 180–190 °C for 7 days. Purification by column chromatography (EtOAc/MeOH, 8:1) afforded the desired product as an orange oil in 60% yield (5.4 mmol, 1.28 g).

C9H20N2O5; M. w. 236.268; orange oil; 1H NMR (300 MHz, DMSO-d6) δ 6.08 – 5.87 (m, 2H, 2NH), 4.58 (t, 2H, 2OH), 3.65 – 3.46 (m, 4H, 2CH2), 3.46 – 3.36 (m, 8H, 4CH2), 3.20 – 3.12 (m, 4H, 2CH2).

1,3,4,6-tetrakis(2-(2-hydroxyethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione (X)

1,3-Bis(2-(2-hydroxyethoxy)ethyl)urea (2.54 mmol) and a 45% aqueous solution of glyoxal (1.15 mmol in 0.5 mL of water) were placed in a round-bottom flask. The mixture was acidified to pH~1 with concentrated HCl and stirred at 90 °C for 6 h. The reaction progress was monitored by TLC (EtOAc/MeOH, 2:1). The reaction mixture was then neutralized with 25% aqueous NaOH and concentrated to dryness under reduced pressure. The resulting yellow oily crude product was purified by column chromatography (EtOAc/MeOH, 8:1) to afford the desired product in 53% yield (1.35 mmol, 0,668 g).

C20H38N4O10; M. w. 494.542; light yellow oil;1H NMR (300 MHz, DMSO-d6) δ 5.54 (s, 2H, 2CH), 4.63 (t, J = 5.3 Hz, 4H, 4OH), 3.64 – 3.47 (m, 20H, 10CH2), 3.47 – 3.39 (m, 8H, 4CH2), 3.34 – 3.26 (m, 4H, 2CH2). 13C NMR (75 MHz, DMSO-d6) δ 158.41, 72.26, 69.02, 68.53, 60.19, 42.17, 25.49.

1,3,4,6-tetrakis(2-(2-chloroethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione (X)

A round-bottom flask containing the compound (0.6 mmol) in chloroform (2 ml) was placed in an ice bath. Thionyl chloride (3.36 mmol) was added dropwise to the stirred solution. The reaction mixture was then heated under reflux for 12 h. The solvent was removed under reduced pressure, and the resulting yellow oily crude product was purified by column chromatography (chloroform) to afford the desired product in 70% yield (0.42 mmol, 0.238 g).

C20H34Cl4N4O6; M. w. 568.314; light yellow oil; 1H NMR (300 MHz, CDCl3) δ 5.69 (s, 2H, 2CH), 3.77 – 3.59 (m, 28H, 14CH2), 3.53 – 3.47 (m, 2H, CH2), 3.47 – 3.42 (m, 2H, CH2). 13C NMR (75 MHz, CDCl3) δ 158.87, 71.14, 70.33, 70.07, 43.25, 42.59.

1,3,4,6-tetrakis(2-(2-(4-(alkylamino)-1λ4 -pyridin-1-yl)ethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione (13-17)

1,3,4,6-Tetrakis(2-(2-chloroethoxy)ethyl)tetrahydroimidazo[4,5-d]imidazole-2,5(1H,3H)-dione and N-alkylpyridin-4-amine were placed in a round-bottom flask. Dry 1-butanol (1–2 mL) was added, and the mixture was heated under reflux for 5 days. After completion, the reaction mixture was concentrated to dryness under reduced pressure. The resulting yellow solid was purified by recrystallization from acetonitrile to afford the product.

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(heptylamino)pyridin-1-ium) tetrachloride (13)

C68H114Cl4N12O6; M. w. 1337.538; white hygroscopic solid (0.176 g, 0.13 mmol, 71% yield); IR (neat/cm−1): 3208, 3102, 3015, 2955, 2929, 2857, 1695, 1653, 1590, 1557, 1520, 1482, 1351, 1320, 1237, 1316, 1194, 1117, 1053, 905, 842, 782, 724, 664, 578, 544, 506 1H NMR (300 MHz, DMSO-d6) δ 9.19 – 8.97 (m, 4H, NH), 8.29 (d, J = 7.0 Hz, 4H, CHpy), 8.10 (d, J = 7.2 Hz, 4H, CHpy), 6.94 (dd, J = 27.7, 7.3 Hz, 8H, CHar), 5.33 (s, 2H, CHgl), 4.48 – 4.20 (m, 8H, CH2(py)), 3.79 – 3.69 (m, 8H, CH2(gl)), 3.60 – 3.37 (m, J = 29.0 Hz, 12H, CH2(alk)), 3.28 – 3.15 (m, J = 5.8 Hz, 12H, CH2(NH)), 1.63 – 1.45 (m, J = 6.9 Hz, 8H, CH2(alk)), 1.42 – 1.12 (m, 32H, CH2(alk)), 0.86 (t, J = 6.8 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 158.75, 157.19, 144.41, 142.04, 110.34, 105.35, 69.39, 68.68, 56.59, 42.72, 42.64, 31.67, 28.84, 28.40, 26.78, 22.51, 14.40. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C68H114N12O64+ 298.7229, found 298.7249.

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(octylamino)pyridin-1-ium) tetrachloride (14)

C72H122Cl4N12O6; M. w. 1393.646; white hygroscopic solid (0.162 g, 0.12 mmol, 68% yield); IR (neat/cm−1): 3207, 3100, 2926, 2855, 2326, 1695, 1652, 1590, 1556, 1482, 1352, 1318, 1237, 1193, 1117, 1064, 841, 782, 723, 508; 1H NMR (300 Мгц, DMSO-d6) δ 9.16 – 9.05 (m, 4H, NH), 8.38 – 8.24 (m, 4H, CHpy), 8.10 (dd, J = 7.3, 1.7 Hz, 4H, CHpy), 6.99 (dd, J = 7.3, 2.8 Hz, 4H, CHpy), 6.89 (dd, J = 7.5, 2.8 Hz, 4H, CHpy), 5.34 (s, 2H, CHgl), 4.38 – 4.22 (m, 8H, CH2(py)), 3.85 – 3.65 (m, 8H, CH2(gl)), 3.62 – 3.37 (m, 12H, CH2(alk)), 3.28 – 3.11 (m, 12H, CH2(NH)), 1.66 – 1.46 (m, 8H, CH2(alk)), 1.40 – 1.17 (m, 40H, CH2(alk)), 0.86 (t, J = 6.3 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 158.77, 157.20, 144.42, 142.04, 110.37, 105.35, 69.62, 69.40, 68.69, 56.60, 42.74, 31.71, 29.16, 29.12, 28.40, 26.84, 22.55, 14.41. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C72H122N12O64+ 312.7390, found 312.7397.

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(nonylamino)pyridin-1-ium) tetrachloride (15)

C76H130Cl4N12O6; M. w. 1449.754; white hygroscopic solid (0.190 g, 0.13 mmol, 75% yield); IR (neat/cm−1): 3206, 3100, 2926, 2855. 1695, 1653, 1590, 1558, 1520, 1352, 1320, 1237, 1195, 1118, 1054, 905, 842, 782, 723, 581, 507; 1H NMR (300 MHz, DMSO-d6) δ 9.14 (t, J = 5.3 Hz, 4H, NH), 8.31 (d, J = 7.8 Hz, 4H, CHpy), 8.12 (d, J = 6.1 Hz, 4H, CHpy), 7.01 (dd, J = 7.3, 2.6 Hz, 4H, CHar), 6.88 (dd, J = 7.5, 2.6 Hz, 4H, CHar), 5.35 (s, 2H, CHgl), 4.47 – 4.17 (m, 8H, CH2(py)), 3.86 – 3.62 (m, 8H, CH2(gl)), 3.62 – 3.36 (m, J = 19.9, 8.3 Hz, 12H, CH2(alk)), 3.27 – 3.14 (m, 12H, CH2(NH)), 1.66 – 1.43 (m, J = 6.8 Hz, 8H, CH2(alk)), 1.41 – 1.06 (m, 48H, CH2(alk)), 0.86 (t, J = 6.6 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 158.75, 157.18, 144.40, 142.04, 110.35, 105.36, 69.38, 68.67, 56.60, 42.73, 42.64, 31.74, 29.43, 29.20, 29.13, 28.40, 26.83, 22.56, 14.70. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C76H130N12O64+ 326.7561, found 326.7554

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(decylamino)pyridin-1-ium) tetrachloride (16)

C80H138Cl4N12O6; M. w. 1505.862; white hygroscopic solid (0.168 g, 0.11 mmol, 81% yield); IR (neat/cm−1): 3207, 3100, 2926, 2855, 1695, 1663, 1591, 1557, 1519, 1480, 1352, 1321, 1237, 1194, 1117, 1056, 844, 786, 753, 719, 545, 507; 1H NMR (300 MHz, DMSO-d6) δ 9.18 – 9.07 (m, 4H, NH), 8.30 (d, J = 7.4 Hz, 4H, CHpy), 8.11 (d, J = 7.5 Hz, 4H, CHpy), 6.99 (d, J = 7.2 Hz, 4H, CHpy), 6.89 (d, J = 6.4 Hz, 4H, CHpy), 5.34 (s, 2H, CHgl), 4.41 – 4.26 (m, 8H, CH2(py)), 3.81 – 3.66 (m, 8H, CH2(gl)), 3.57 – 3.39 (m, 12H, CH2(alk)), 3.28 – 3.17 (m, 12H, CH2(NH)), 1.65 – 1.48 (m, 8H, CH2(alk)), 1.41 – 1.17 (m, 56H, CH2(alk)), 0.86 (t, J = 6.3 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 157.20, 144.43, 142.06, 110.37, 105.37, 69.40, 68.68, 56.61, 42.75, 31.77, 29.49, 29.46, 29.22, 29.18, 28.40, 26.85, 22.57, 14.42. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C80H138N12O64+ 340.7697, found 340.7710

1,1',1'',1'''-((((2,5-dioxodihydroimidazo[4,5-d]imidazole-1,3,4,6(2H,5H)-tetrayl)tetrakis(ethane-2,1-diyl))tetrakis(oxy))tetrakis(ethane-2,1-diyl))tetrakis(4-(dodecylamino)pyridin-1-ium) tetrachloride (17)

C88H154Cl4N12O6; M. w. 1618.078; white hygroscopic solid (0.174 g, 0.11 mmol, 70% yield); IR (neat/cm−1): 3207, 3099, 2925, 2854, 1695, 1653, 1591, 1557, 1469, 1353, 1194, 1118, 1056, 842, 754, 622, 580, 505; 1H NMR (300 MHz, DMSO-d6) δ 9.40 – 9.18 (m, 4H, NH), 8.28 (d, J = 3.5 Hz, 4H, CHpy), 8.07 (d, J = 5.2 Hz, 4H, CHpy), 7.01 (d, J = 7.2 Hz, 4H, CHpy), 6.87 (d, J = 7.7 Hz, 4H, CHpy), 5.32 (s, 2H, CHgl), 4.44 – 4.14 (m, 8H, CH2(py)), 3.82 – 3.64 (m, 8H, CH2(gl)), 3.58 – 3.41 (m, 12H, CH2(alk)), 3.26 – 3.13 (m, 12H, CH2(NH)), 1.62 – 1.48 (m, 8H, CH2(alk)), 1.42 – 1.14 (m, 72H, CH2(alk)), 0.86 (t, J = 6.5 Hz, 12H, CH3(alk)). 13C NMR (75 MHz, DMSO-d6) δ 157.20, 144.42, 142.04, 110.38, 105.35, 69.40, 68.68, 56.60, 42.75, 31.78, 29.56, 29.51, 29.24, 29.20, 28.41, 26.87, 22.57, 14.41. HRMS (ESI) m/z: [M – 4Cl-]4+ calcd for C88H154N12O64+ 368.8040, found 368.8023


4.2 Microbiological assay

4.2.1 Bacterial strains

Laboratory strains of the microorganisms E. coli ATCC 25922, S. aureus ATCC 43300 were obtained from the State Collection of Pathogenic Microorganisms (Obolensk, Russia).

4.2.2 Identification of microorganisms

Species identification of microorganisms was carried out on a MALDI-TOF Biotyper mass spectrometer (Bruker, Billerica, MA, USA) according to the standard microflex User Manual. One part of the daily bacterial culture was introduced into a 2 mL tube (Eppendorf, Hamburg, Germany) containing 300 µL of deionized water and triturated until a homogeneous suspension was obtained. Then, 900 µL of 96% ethanol was added and shaken. The tube was then centrifuged at 12,000× g for 2 min. The supernatant was discarded, and the precipitate was dried in air. After drying, the precipitate was thoroughly mixed with 30 µL of 70% formic acid, incubated for 10 min at room temperature, and then mixed with 30 µL of acetonitrile (Sigma-Aldrich, St. Louis, MO, USA) and incubated for another 10 min. This mixture was centrifuged at 12,000×g for 2 min; then, 1 µL of the supernatant was transferred to an MSP 96 Polished Steel MALDI Target Plate (Bruker Daltonik GmbH, Bremen, Germany), air-dried, and covered with 1 µL of a saturated solution of α-cyano-4-hydroxycinnamic acid (Bruker Daltonik, Bremen, Germany). The MALDI target plate was placed in a MALDI-TOF microflex LRF instrument (Bruker Daltonik, Bremen, Germany). The data acquisition settings were as follows: ion source 1 at 19.50 kV, ion source 2 at 18.22 kV, lens at 7.01 kV, and a mass range of 2000 to 20,000 Da. Spectrum registration was performed automatically using MALDI Biotyper RTC 3.1 software (Bruker Daltonik, Bremen, Germany). The obtained spectra were compared with the reference spectra of the FFL v1.0 data-base. Identification scores ≥2.0 and 1.7–1.99 indicated recognition of the species and genus levels, respectively, while scores <1.7 indicated a lack of reliable data.

4.2.3 Cultivation of microorganisms.

Microorganisms were cultivated using agar and GRM broth. Cultivation of microorganisms was carried out for 20–24 h at a temperature of 37°C.

4.2.4 MIC and MBC determination.

The synthesized QACs were dissolved in the DMSO/water system at a ratio of 1/9 with a final concentration of 1000 mg/L. For better dissolution, the samples were sonicated for 15 to 60 minutes at 40°C. The MIC and MBC of the antimicrobials was determined by the microdilution method in culture broth, as indicated by the Clinical and Laboratory Standards Institute of the United States of America 76.

4.3 Computational and annotation protocol

4.3.1 Human annotation: contributor fields

The final Good/Bad calls are available, but individual votes and the full collection history have not been reconstructed. The following fields are intentionally reserved for the contributing authors; they must be completed before interpreting the calls as an independent human-information channel.

[COAUTHORS H1 — Annotators and collection period: insert the number of annotators, their relevant scientific backgrounds and experience, how they were recruited, and the dates or rounds of annotation. Confirm whether the same annotators participated in every round.]

[COAUTHORS H2 — Compound selection: describe how compounds were selected and presented for annotation, the unit being rated (molecule, salt, assay record or another unit), the treatment of repeated structures and counterions, and any exclusions made before annotation.]

[COAUTHORS H3 — Task and decision criteria: insert the exact question/instructions given to annotators and the operational definitions of Good and Bad. State which endpoints or practical considerations were relevant, whether numerical cutoffs were prescribed, and how uncertain or unrateable compounds were handled.]

[COAUTHORS H4 — Information visible to annotators: specify whether annotators saw molecular structures, identifiers, measured MIC/MBC, cytotoxicity, organism/strain information, assay conditions, literature reports or model predictions. State explicitly whether the measurements subsequently used for quantitative supervision were available during annotation and whether Q-HERO or OOD evaluation information was visible.]

[COAUTHORS H5 — Collection workflow: describe the interface or files used, the number of ratings requested per compound, whether ratings were independent, any discussion between annotators, presentation order, repeated checks and revisions between rounds. Attach the original instructions or a representative annotation form to Supporting Information if available.]

[COAUTHORS H6 — Final-label construction: state how individual ratings were combined into the final Good/Bad call, including disagreement, ties, adjudication, missing ratings and revisions. Identify which steps are documented in records and which are reconstructed from the contributors' recollection.]

[COAUTHORS H7 — Records and agreement: identify any recoverable individual votes, round identifiers and adjudication logs and their planned archive location. If votes are available, report agreement with its definition, sample size and uncertainty; otherwise confirm that agreement cannot be calculated. Annotation time or cost may be added if documented, but is not used to infer a measurement-replacement rate.]

4.3.2 Historical model and new reconstruction

The original frozen feature dimension is 768; the separate encoder widths are 512,384,256. Saved expert checkpoint and scaler identifiers, recovered April/May/July notebooks and task-description versions are listed in SI. The reconstructed decoder uses CatBoost 500 iterations, depth 6, learning rate 0.05 and seed 42. Original-108 task-row holdout uses test_size=0.2; cation and scaffold evaluations use the stored five folds. Fresh task-description vectors are cached once and reused, including fixed permutation and norm-matched random-code controls. Those four codes are task identifiers, not measured antibacterial values.

4.3.3 Matched compact-encoder follow-up

The 377/304 source train/validation split, target exclusions and source feature hashes are fixed across six arms and five seeds. The scaler and quantitative standardisation are fitted to source training only. Binary MIC uses a train-only cutoff giving the human positive prevalence. AdamW uses learning rate 0.001, weight decay 0.0001 and a cosine schedule to 0.000001 over 80 epochs; gradients are clipped at norm 1. Batch size is at most 64, with 480 updates. The contrastive settings follow the recovered hard-negative objective (temperature 0.05, hard-negative coefficient 0.3); continuous guidance uses MSE. Validation is diagnostic and does not select checkpoints. All arms, source-training permutations, paired initial-state hashes and minibatch hashes are archived.

Uncertainty notation follows the source of repetition. Reconstructed row-wise CV and grouped fold summaries use mean ± SD across five fold scores with ddof=0, matching the original numpy.std convention. Repeated source/target fits use mean ± sample SD across the specified source seeds with ddof=1. Neither quantity is a 95% confidence interval. The separately reported paired bootstrap intervals remain contrasts conditional on the declared folds and trained seeds. A single OOD fit from one archived checkpoint has no CV-fold or source-seed SD; no neighbouring configuration supplies one.

4.3.4 Target cohorts, uncertainty and modern models

All 420 QAC endpoints are exact; OOD evaluation uses 67 exact endpoints and separately retains the IT505 E. coli MBC bound. No OOD data enter model selection. Performance is calculated on log2(mg/L), with per-task R² and pooled RMSE/MAE. Five-seed summaries average seed-specific metrics. Pointwise paired 95% intervals use 10,000 resamples of source seeds and independent cation or scaffold clusters, keeping the four endpoints together within each selected cluster. OOD has only four scaffold clusters, limiting interval precision and subgroup inference. Decoder, PCA, software and checkpoint versions and all prediction routes are specified in SI; comparisons with different preprocessing or trainable capacity are labelled accordingly.

[COAUTHORS C1 — Confirm synthetic characterisation, optimisation records and microbiological protocol details against primary laboratory records. The native source experimental text is retained. Reference 76 is corrected to CLSI M07, but the exact edition used, MBC procedure, assay repeats and quality-control records require contributor confirmation.]

5. CRediT authorship contribution statement

Egor A. Ilin: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization, Project administration; Nikita A. Frolov: Conceptualization, Methodology, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization, Supervision, Project administration; Mary A. Seferyan: Conceptualization, Methodology, Validation, Investigation, Writing - Review & Editing; Anvar B. Valeev: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing; Egor V. Sinikin: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing; Taygib M. Iliyasov: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing; Andrey D. Vinokurov: Validation, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization; Elena V. Detusheva: Methodology, Validation, Formal analysis, Investigation, Resources, Writing - Review & Editing; Elizabeth Son: Methodology, Validation, Formal analysis, Investigation;  Michael G. Medvedev: Conceptualization, Methodology, Formal analysis, Resources, Data Curation, Writing - Review & Editing, Visualization, Supervision, Project administration; Anatoly N. Vereshchagin: Conceptualization, Methodology, Resources, Writing - Review & Editing, Supervision, Project administration, Funding acquisition.


6. Conflicts of interest

The authors declare no competing financial interests.


7. Data availability

The full 105-QAC and 17-OOD registers, exact/bound endpoint registry, notebook-output provenance, input hashes, split definitions, training settings and saved per-molecule predictions are assembled with the revision. Public immutable archive identifiers and redistribution conditions will be completed in the coauthor fields below.

[COAUTHORS D1 — Insert the verified public archive URL/DOI and exact version for the QAC-AMR/QMR source data and final expert labels. The earlier draft lists 10.5281/zenodo.22286669 and https://github.com/Yagr49/QMC-Expert; their public availability and inclusion of this revision's materials must be confirmed before retaining those claims.]

[COAUTHORS D2 — Insert the immutable archive URL/DOI and code revision for the analyses supporting this article, including source manifests, exclusion rules, target folds, checkpoint identifiers, training settings and per-molecule predictions. State any access or redistribution restrictions for reused sources.]


8. Acknowledgments

This work was supported by the Russian Science Foundation (project №24-13-00307). Microbiological Experiments were performed at the State Research Center for Applied Microbiology and Biotechnology (SRC AMB) using the unique research facility SRC AMB within the framework of the industry research program of Rospotrebnadzor. This research was supported in part through computational resources of HPC facilities at NRU HSE.


9. Appendix A. Supplementary data

Supporting Information contains the four original author figures, the extended experimental and computational records, the full target compound registers and endpoint predictions, and all original and subsequent hypothesis checks. Archived analyses retain their original reference numbering within explicitly labelled sections.


References

1.Iskandar, K.; Murugaiyan, J.; Hammoudi Halat, D.; Hage, S. E.; Chibabhai, V.; Adukkadukkam, S.; Roques, C.; Molinier, L.; Salameh, P.; Van Dongen, M., Antibiotic Discovery and Resistance: The Chase and the Race. Antibiotics (Basel) 2022, 11.

2.Gargate, N.; Laws, M.; Rahman, K. M., Current economic and regulatory challenges in developing antibiotics for Gram-negative bacteria. npj Antimicrobials and Resistance 2025, 3, 50.

3.Lack of innovation set to undermine antibiotic performance and health gains. https://www.who.int/news/item/22-06-2022-22-06-2022-lack-of-innovation-set-to-undermine-antibiotic-performance-and-health-gains (15.04.2026),

4.Melchiorri, D.; Rocke, T.; Alm, R. A.; Cameron, A. M.; Gigante, V., Addressing urgent priorities in antibiotic development: insights from WHO 2023 antibacterial clinical pipeline analyses. Lancet Microbe 2025, 6, 100992.

5.Sati, H.; Carrara, E.; Savoldi, A.; Hansen, P.; Garlasco, J.; Campagnaro, E.; Boccia, S.; Castillo-Polo, J. A.; Magrini, E.; Garcia-Vello, P.; Wool, E.; Gigante, V.; Duffy, E.; Cassini, A.; Huttner, B.; Pardo, P. R.; Naghavi, M.; Mirzayev, F.; Zignol, M.; Cameron, A.; Tacconelli, E.; Aboderin, A.; Al Ghoribi, M.; Al-Salman, J.; Amir, A.; Apisarnthanarak, A.; Blaser, M.; El-Sharif, A.; Essack, S.; Harbarth, S.; Huang, X.; Kapoor, G.; Knight, G.; Muhwa, J. C.; Monnet, D. L.; Ousassa, T.; Sacsaquispe, R.; Severin, J.; Sugai, M.; Taneja, N.; Umubyeyi Nyaruhirira, A., The WHO Bacterial Priority Pathogens List 2024: a prioritisation study to guide research, development, and public health strategies against antimicrobial resistance. The Lancet Infectious Diseases 2025, 25, 1033-1043.

6. World Health Organization. Antibacterial products in clinical development for bacterial priority pathogens. October 2025; data cutoff 15 February 2025. https://www.who.int/observatories/global-observatory-on-health-research-and-development/monitoring/antibacterial-products-in-clinical-development-for-priority-pathogens/ (accessed 2026-10-13).

7.Organization, W. H., Analysis of antibacterial agents in clinical and preclinical development: overview and analysis 2025. 2025.

8.Coelho, J. R.; Carriço, J. A.; Knight, D.; Martínez, J. L.; Morrissey, I.; Oggioni, M. R.; Freitas, A. T., The use of machine learning methodologies to analyse antibiotic and biocide susceptibility in Staphylococcus aureus. PLoS One 2013, 8, e55582.

9.Lin, B.; Yan, S.; Zhen, B., A machine learning method for predicting molecular antimicrobial activity. Scientific Reports 2025, 15, 6559.

10.Krishnan, R.; Howard, I. S.; Comber, S.; Jha, A. N., In silico prediction of acute chemical toxicity of biocides in marine crustaceans using machine learning. Science of The Total Environment 2023, 887, 164072.

11.Jukič, M.; Bren, U., Machine Learning in Antibacterial Drug Design. Frontiers in Pharmacology 2022, Volume 13 - 2022.

12.Shankarnarayan, S. A.; Guthrie, J. D.; Charlebois, D. A. Machine learning for antimicrobial resistance research and drug development. In The Global Antimicrobial Resistance Epidemic-Innovative Approaches and Cutting-Edge Solutions; IntechOpen: 2022.

13.Diéguez-Santana, K.; González-Díaz, H., Machine learning in antibacterial discovery and development: A bibliometric and network analysis of research hotspots and trends. Computers in Biology and Medicine 2023, 155, 106638.

14.Liu, Z.; Chen, Q.; Yao, C.; Wang, Y.; Zhu, S.; Guan, J.; Miao, Y., The chemical design of antimicrobial ionic liquids guided by machine learning: a review on balancing efficacy and toxicity. Journal of Materials Chemistry B 2026, 14, 3023-3047.

15.Sadaghiyanfam, S.; Kamberaj, H.; Isler, Y., Leveraging ChemBERTa and machine learning for accurate toxicity prediction of ionic liquids. Journal of the Taiwan Institute of Chemical Engineers 2025, 171, 106030.

16.Krishnan, A.; Anahtar, M. N.; Valeri, J. A.; Jin, W.; Donghia, N. M.; Sieben, L.; Luttens, A.; Zhang, Y.; Modaresi, S. M.; Hennes, A.; Fromer, J.; Bandyopadhyay, P.; Chen, J. C.; Rehman, D.; Desai, R.; Edwards, P.; Lach, R. S.; Aschtgen, M.-S.; Gaborieau, M.; Gaetani, M.; Palace, S. G.; Omori, S.; Khonde, L.; Moroz, Y. S.; Blough, B.; Jin, C.; Loh, E.; Grad, Y. H.; Saei, A. A.; Coley, C. W.; Wong, F.; Collins, J. J., A generative deep learning approach to <em>de novo</em> antibiotic design. Cell 2025, 188, 5962-5979.e22.

17.Olayo-Alarcon, R.; Amstalden, M. K.; Zannoni, A.; Bajramovic, M.; Sharma, C. M.; Brochado, A. R.; Rezaei, M.; Müller, C. L., Pre-trained molecular representations enable antimicrobial discovery. Nature Communications 2025, 16, 3420.

18.Taha, M. M. E.; Oraibi, B.; Abdelwahab, S. I.; Sahli, K. A.; Assiri, A.; Qadri, M.; Alarifi, A.; Khardali, A.; Farasani, A.; Moshi, J. M.; Alsaadi, K. H.; Alshahrani, S.; Shubaily, H. M.; Binjomah, A. Z., Global trends and thematic evolution in antimicrobial stewardship research: a comprehensive bibliometric and network analysis (1977–2025). Journal of Hospital Infection 2026, 171, 11-26.

19.Wang, X.; Rai, N.; Merchel Piovesan Pereira, B.; Eetemadi, A.; Tagkopoulos, I., Accelerated knowledge discovery from omics data by optimal experimental design. Nature Communications 2020, 11, 5026.

20.Sowers, A.; Wang, G.; Xing, M.; Li, B., Advances in Antimicrobial Peptide Discovery via Machine Learning and Delivery via Nanotechnology. Microorganisms 2023, 11, 1129.

21.Wang, Y.; Zhao, L.; Li, Z.; Xi, Y.; Pan, Y.; Zhao, G.; Zhang, L., A generative artificial intelligence approach for the discovery of antimicrobial peptides against multidrug-resistant bacteria. Nature Microbiology 2025, 10, 2997-3012.

22.Raissi, M.; Perdikaris, P.; Karniadakis, G. E., Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. Journal of Computational Physics 2019, 378, 686-707.

23.Cuomo, S.; Di Cola, V. S.; Giampaolo, F.; Rozza, G.; Raissi, M.; Piccialli, F., Scientific Machine Learning Through Physics–Informed Neural Networks: Where we are and What’s Next. Journal of Scientific Computing 2022, 92, 88.

24.Kuang, T.; Liu, P.; Ren, Z., Impact of Domain Knowledge and Multi-Modality on Intelligent Molecular Property Prediction: A Systematic Survey. Big Data Mining and Analytics 2024, 7, 858-888.

25.Wahyudi, A.; Sueviriyapan, N.; Suriyapraphadilok, U., Generalizable physics-informed graph neural network for CO2 solubility prediction across amine classes. Separation and Purification Technology 2026, 385, 136395.

26.Selby, D. A.; Jakhmola, R.; Sprang, M.; Großmann, G.; Raki, H.; Maani, N.; Pavliuk, D.; Ewald, J.; Vollmer, S., Visible neural networks for multi-omics integration: a critical review. Frontiers in Artificial Intelligence 2025, Volume 8 - 2025.

27.Bickerton, G. R.; Paolini, G. V.; Besnard, J.; Muresan, S.; Hopkins, A. L., Quantifying the chemical beauty of drugs. Nature chemistry 2012, 4, 90-8.

28.Lajiness, M. S.; Maggiora, G. M.; Shanmugasundaram, V., Assessment of the consistency of medicinal chemists in reviewing sets of compounds. J Med Chem 2004, 47, 4891-6.

29.Kutchukian, P. S.; Vasilyeva, N. Y.; Xu, J.; Lindvall, M. K.; Dillon, M. P.; Glick, M.; Coley, J. D.; Brooijmans, N., Inside the Mind of a Medicinal Chemist: The Role of Human Bias in Compound Prioritization during Drug Discovery. PLOS ONE 2012, 7, e48476.

30.Choung, O.-H.; Vianello, R.; Segler, M.; Stiefl, N.; Jiménez-Luna, J., Extracting medicinal chemistry intuition via preference machine learning. Nature Communications 2023, 14, 6651.

31.Sundin, I.; Voronov, A.; Xiao, H.; Papadopoulos, K.; Bjerrum, E. J.; Heinonen, M.; Patronov, A.; Kaski, S.; Engkvist, O., Human-in-the-loop assisted de novo molecular design. Journal of Cheminformatics 2022, 14, 86.

32.Menke, J.; Nahal, Y.; Bjerrum, E. J.; Kabeshov, M.; Kaski, S.; Engkvist, O., Metis: a python-based user interface to collect expert feedback for generative chemistry models. Journal of Cheminformatics 2024, 16, 100.

33.Christiano, P. F.; Leike, J.; Brown, T.; Martic, M.; Legg, S.; Amodei, D. Deep Reinforcement Learning from Human Preferences. In Advances in Neural Information Processing Systems, 2017; Curran Associates, Inc.: 2017; Vol. 30; pp 4299-4307.

34.Ouyang, L.; Wu, J.; Jiang, X.; Almeida, D.; Wainwright, C.; Mishkin, P.; Zhang, C.; Agarwal, S.; Slama, K.; Ray, A.; Schulman, J.; Hilton, J.; Kelton, F.; Miller, L.; Simens, M.; Askell, A.; Welinder, P.; Christiano, P. F.; Leike, J.; Lowe, R. Training language models to follow instructions with human feedback. In Advances in Neural Information Processing Systems, 2022; Curran Associates, Inc.: 2022; Vol. 35; pp 27730-27744.

35.Georgoulis, E.; Zervou, M. A.; Pantazis, Y., Transfer learning on protein language models improves antimicrobial peptide classification. Scientific Reports 2025, 15, 37456.

36.Cai, J.; Yan, J.; Un, C.; Wang, Y.; Campbell-Valois, F.-X.; Siu, S. W. I., BERT-AmPEP60: A BERT-Based Transfer Learning Approach to Predict the Minimum Inhibitory Concentrations of Antimicrobial Peptides for Escherichia coli and Staphylococcus aureus. Journal of Chemical Information and Modeling 2025, 65, 3186-3202.

37.Kalliokoski, T.; Kramer, C.; Vulpetti, A.; Gedeck, P., Comparability of Mixed IC50 Data – A Statistical Analysis. PLOS ONE 2013, 8, e61007.

38.Kramer, C.; Kalliokoski, T.; Gedeck, P.; Vulpetti, A., The Experimental Uncertainty of Heterogeneous Public Ki Data. Journal of Medicinal Chemistry 2012, 55, 5165-5173.

39.Landrum, G. A.; Riniker, S., Combining IC50 or Ki Values from Different Sources Is a Source of Significant Noise. Journal of Chemical Information and Modeling 2024, 64, 1560-1567.

40.Campisi, E.; Di Liberto, E.; Barchitta, M.; Maugeri, A.; Favara, G.; Magnano San Lio, R.; Vecchi, E.; D'Ancona, F.; Agodi, A., Evaluation of preventive interventions addressing healthcare-associated infections and antimicrobial resistance: a systematic review. Journal of Hospital Infection 2026, 171, 120-136.

41.Alves, P. J.; Gryson, L.; Hajjar, J.; Lepelletier, D.; Reners, M.; Rodríguez Salazar, J.; Simon, A., Role of antiseptics in the prevention and treatment of infections in nursing homes. Journal of Hospital Infection 2023, 131, 58-69.

42.Buciński, A.; Socha, A.; Wnuk, M.; Bączek, T.; Nowaczyk, A.; Krysiński, J.; Goryński, K.; Koba, M., Artificial neural networks in prediction of antifungal activity of a series of pyridine derivatives against Candida albicans. Journal of Microbiological Methods 2009, 76, 25-29.

43.Wnuk, M.; Marszałł, M.; Zapęcka, A.; Nowaczyk, A.; Krysiński, J.; Romaszko, J.; Kawczak, P.; Bączek, T.; Buciński, A., Prediction of antimicrobial activity of imidazole derivatives by artificial neural networks. 2013, 8, 1-15.

44.Badura, A.; Krysiński, J.; Nowaczyk, A.; Buciński, A., Prediction of the antimicrobial activity of quaternary ammonium salts against Staphylococcus aureus using artificial neural networks. Arabian Journal of Chemistry 2021, 14, 103233.

45.Badura, A.; Krysiński, J.; Nowaczyk, A.; Buciński, A., Application of artificial neural networks to prediction of new substances with antimicrobial activity against Escherichia coli. Journal of Applied Microbiology 2021, 130, 40-49.

46.Badura, A.; Krysiński, J.; Nowaczyk, A.; Buciński, A., Application of artificial neural networks to the prediction of antifungal activity of imidazole derivatives against Candida albicans. Chemometrics and Intelligent Laboratory Systems 2022, 222, 104501.

47.Ramić, A.; Skočibušić, M.; Odžak, R.; Čipak Gašparović, A.; Milković, L.; Mikelić, A.; Sović, K.; Primožič, I.; Hrenar, T. Antimicrobial Activity of Quasi-Enantiomeric Cinchona Alkaloid Derivatives and Prediction Model Developed by Machine Learning. Antibiotics, 10, 659, 2021.

48.Lorenc, A.; Badura, A.; Karolak, M.; Pałkowski, Ł.; Kubik, Ł.; Skrzypczak, A.; Buciński, A., Hybrid Machine Learning Model for Dual Prediction of Antimicrobial Activity against Staphylococcus aureus and Candida albicans. Journal of Pharmaceutical Innovation 2026, 21, 174.

49.Tiihonen, A.; Cox-Vazquez, S. J.; Liang, Q.; Ragab, M.; Ren, Z.; Hartono, N. T. P.; Liu, Z.; Sun, S.; Zhou, C.; Incandela, N. C.; Limwongyut, J.; Moreland, A. S.; Jayavelu, S.; Bazan, G. C.; Buonassisi, T., Predicting Antimicrobial Activity of Conjugated Oligoelectrolyte Molecules via Machine Learning. Journal of the American Chemical Society 2021, 143, 18917-18931.

50.Hodyna, D.; Kovalishyn, V.; Rogalsky, S.; Blagodatnyi, V.; Petko, K.; Metelytsia, L., Antibacterial Activity of Imidazolium-Based Ionic Liquids Investigated by QSAR Modeling and Experimental Studies. Chem Biol Drug Des 2016, 88, 422-33.

51.Makarov, D. M.; Fadeeva, Y. A.; Safonova, E. A.; Shmukler, L. E., Predictive modeling of antibacterial activity of ionic liquids by machine learning methods. Computational Biology and Chemistry 2022, 101, 107775.

52.Ghaemi, S.; Consylman, A.; Pan, B.; Wu, A.; Petersen, A.; Chang, G.; McDonough, D.; Forman, M.; Bezold, E. L.; Wuest, W. M.; Shehu, A.; Zhao, L.; Minbiole, K. P. C., Topology-Aware Generation and Activity-Based Filtering: A Computational-Experimental Framework for Data-Scarce Quaternary Ammonium Compound Discovery. Journal of Chemical Information and Modeling 2026, 66, 3117-3128.

53.Ilin, E. A.; Frolov, N. A.; Seferyan, M. A.; Valeev, A. B.; Vinokurov, A. D.; Detusheva, E. V.; Son, E.; Medvedev, M. G.; Vereshchagin, A. N., Tackling the challenge of ML-assisted antibacterial activity prediction: One step closer to controlled quaternary ammonium compounds design via neural networks model. Bioorganic Chemistry 2025, 167, 109175.

54.Ward, M.; O'Boyle, N. M., Analysis of the structural diversity of heterocycles amongst European medicines agency approved pharmaceuticals (2014–2023). RSC Medicinal Chemistry 2025, 16, 4540-4570.

55.Fedorowicz, J.; Sączewski, J. Advances in the Synthesis of Biologically Active Quaternary Ammonium Compounds. International Journal of Molecular Sciences, 25, 4649, 2024.

56.Ma, J.; Liu, N.; Huang, M.; Wang, L.; Han, J.; Qian, H.; Che, F., Synthesis, physicochemical and antimicrobial properties of cardanol-derived quaternary ammonium compounds (QACs) with heterocyclic polar head. Journal of Molecular Liquids 2019, 294, 111669.

57.Zhou, Z.; Zhou, S.; Zhang, X.; Zeng, S.; Xu, Y.; Nie, W.; Zhou, Y.; Xu, T.; Chen, P., Quaternary Ammonium Salts: Insights into Synthesis and New Directions in Antibacterial Applications. Bioconjugate Chemistry 2023, 34, 302-325.

58.Burnett, C. L.; Bergfeld, W. F.; Belsito, D. V.; Hill, R. A.; Klaassen, C. D.; Liebler, D. C.; Marks, J. G., Jr.; Shank, R. C.; Slaga, T. J.; Snyder, P. W.; Andersen, F. A., Final report of the safety assessment of Kojic acid as used in cosmetics. Int J Toxicol 2010, 29, 244s-73.

59.Aati, H. Y.; Lotfy, M. M.; Al-tweel, A.; Al-enezi, B.; Abdelkader, K.; AbouZid, S. F.; Rateb, M. E.; Hassan, H. M.; Mohammed, R.; El Amir, D., Kojic acid: A River Nile-derived fungal secondary metabolite with preservative potential against Listeria monocytogenes in milk. Microbial Pathogenesis 2025, 204, 107532.

60.Wu, Y.; Shi, Y. G.; Zeng, L. Y.; Pan, Y.; Huang, X. Y.; Bian, L. Q.; Zhu, Y. J.; Zhang, R. R.; Zhang, J., Evaluation of antibacterial and anti-biofilm properties of kojic acid against five food-related bacteria and related subcellular mechanisms of bacterial inactivation. Food Sci Technol Int 2019, 25, 3-15.

61.Sie, C.; Ngaini, Z.; Suhaili, N.; Madiahlagan, E., Synthesis of Kojic Ester Derivatives as Potential Antibacterial Agent. Journal of Chemistry 2018, 2018, 1-7.

62.Aytemir, M. D.; Özçelik, B., A study of cytotoxicity of novel chlorokojic acid derivatives with their antimicrobial and antiviral activities. European Journal of Medicinal Chemistry 2010, 45, 4089-4095.

63.Emami, S.; Ghafouri, E.; Faramarzi, M. A.; Samadi, N.; Irannejad, H.; Foroumadi, A., Mannich bases of 7-piperazinylquinolones and kojic acid derivatives: Synthesis, in vitro antibacterial activity and in silico study. European Journal of Medicinal Chemistry 2013, 68, 185-191.

64.Liu, X.; Xia, W.; Jiang, Q.; Xu, Y.; Yu, P., Effect of kojic acid-grafted-chitosan oligosaccharides as a novel antibacterial agent on cell membrane of gram-positive and gram-negative bacteria. Journal of Bioscience and Bioengineering 2015, 120, 335-339.

65.Liu, X.; Xia, W.; Jiang, Q.; Xu, Y.; Yu, P., Synthesis, Characterization, and Antimicrobial Activity of Kojic Acid Grafted Chitosan Oligosaccharide. Journal of Agricultural and Food Chemistry 2014, 62, 297-303.

66.Vereshchagin, A. N.; Frolov, N. A.; Minaeva, A. P.; Detusheva, E. V.; Derkach, Y. V.; Egorov, M. P., Synthesis and biological evaluation of novel cyanuric acid-tethered tris-pyridinium derivatives. Mendeleev Communications 2021, 31, 368-369.

67.Mateeva, N. N.; Winfield, L. L.; Redda, K. K., The chemistry and pharmacology of tetrahydropyridines. Curr Med Chem 2005, 12, 551-71.

68.Khan, M. M.; Faiz, F. A.; Khan, M. S., Tetrahydropyridines: a recent update for their multicomponent synthesis. RSC Advances 2026, 16, 2007-2029.

69.Vereshchagin, A. N.; Iliyasov, T. M.; Karpenko, K. A.; Akchurin, R. N.; Minyaev, M. E. Tetrahydropyridines’ Stereoselective Formation, How Lockdown Assisted in the Identification of the Features of Its Mechanism. Molecules, 27, 4367, 2022.

70.Tekin, K.; Hao, N.; Karagoz, S.; Ragauskas, A. J., Ethanol: A Promising Green Solvent for the Deconstruction of Lignocellulose. ChemSusChem 2018, 11, 3559-3575.

71.Zheng, Z.; Dai, A.; Jin, Z.; Chi, Y. R.; Wu, J., Trifluoromethylpyridine: An Important Active Fragment for the Discovery of New Pesticides. Journal of Agricultural and Food Chemistry 2022, 70, 11019-11030.

72.Wang, Y.; Xu, F.; Luo, D.; Guo, S.; He, F.; Dai, A.; Song, B.; Wu, J., Synthesis of Anthranilic Diamide Derivatives Containing Moieties of Trifluoromethylpyridine and Hydrazone as Potential Anti-Viral Agents for Plants. Journal of Agricultural and Food Chemistry 2019, 67, 13344-13352.

73.Ponomarenko, O. V.; Panshina, S. Y.; Bakibaev, A. A.; Erkasov, R. S.; Kenzhebaj, M. S.; Montaeva, A. S., Glycoluril and Its Chemical Properties. EURASIAN JOURNAL OF CHEMISTRY 2023, 28.

74.Kravchenko, A. N.; Baranov, V. V.; Gazieva, G. A., Synthesis of glycolurils and their analogues. Russian Chemical Reviews 2018, 87, 89.

75.Galochkin, A. A.; Baranov, V. V.; Hansford, K. A.; Friberg, L. I. M.; Strel'tzova, E. D.; Lipatov, E. S.; Nelyubina, Y. V.; Kravchenko, A. N., Synthesis, Structures and Antifungal Activity of Selenoglycolurils. ChemistrySelect 2023, 8, e202300765.

76. Clinical and Laboratory Standards Institute. Methods for Dilution Antimicrobial Susceptibility Tests for Bacteria That Grow Aerobically. CLSI M07. https://clsi.org/shop/standards/m07/ (accessed 2026-10-13). Exact edition used in the experiments to be confirmed by contributors.


77. Ross, J.; Belgodere, B.; Chenthamarakshan, V.; Padhi, I.; Mroueh, Y.; Das, P. Large-scale chemical language representations capture molecular structure and properties. Nature Machine Intelligence 2022, 4, 1256–1264. https://doi.org/10.1038/s42256-022-00580-7.

78. Schuh, M. G.; Boldini, D.; Sieber, S. A. Synergizing Chemical Structures and Bioassay Descriptions for Enhanced Molecular Property Prediction in Drug Discovery. Journal of Chemical Information and Modeling 2024, 64 (12),4640–4650. https://doi.org/10.1021/acs.jcim.4c00765.

79. Hu, E. J.; Shen, Y.; Wallis, P.; Allen-Zhu, Z.; Li, Y.; Wang, S.; Wang, L.; Chen, W. LoRA: Low-Rank Adaptation of Large Language Models. arXiv 2021, arXiv:2106.09685. https://doi.org/10.48550/arXiv.2106.09685.

80. Hollmann, N.; Müller, S.; Purucker, L.; Krishnakumar, A.; Körfer, M.; Hoo, S. B.; Schirrmeister, R. T.; Hutter, F. Accurate predictions on small data with a tabular foundation model. Nature 2025, 637, 319–326. https://doi.org/10.1038/s41586-024-08328-6.

81. Google Research. TabFM: Tabular Foundation Models. https://github.com/google-research/tabfm (accessed 2026-10-12); code revision fbb665569425fd2f490c6576b3af967876fe11ff904; JAX regression checkpoint google/tabfm-1.0.0-jax, revision d5e74033fcf257699fab013e2cdd7edf424ff904.

82. Erickson, N.; Mueller, J.; Shirkov, A.; Zhang, H.; Larroy, P.; Li, M.; Smola, A. AutoGluon-Tabular: Robust and Accurate AutoML for Structured Data. arXiv 2020, arXiv:2003.06505. https://doi.org/10.48550/arXiv.2003.06505.

83. Schölkopf, B.; Locatello, F.; Bauer, S.; Ke, N. R.; Kalchbrenner, N.; Goyal, A.; Bengio, Y. Towards Causal Representation Learning. 2021. https://arxiv.org/abs/2102.11107.

84. Heid, E.; et al. Chemprop: A Machine Learning Package for Chemical Property Prediction. J. Chem. Inf. Model. 2024, 64 (1), 9–17. https://doi.org/10.1021/acs.jcim.3c01250.

