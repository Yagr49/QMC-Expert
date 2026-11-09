### intro_01

Pre-trained molecular models offer a reusable description of chemical structure, but adapting that description to a small antibacterial dataset still requires two choices: which information should guide the representation, and which parts of the prediction pipeline should be trained. Full backbone fine-tuning, low-rank updates inside transformer layers and an external feature encoder make different use of the available supervision. Their relative performance must therefore be tested under the intended validation regime, rather than inferred from the number of trainable parameters alone.

### intro_02

Our approach separates representation guidance from quantitative decoding. Frozen MolFormer first maps each molecular structure to a 768-dimensional vector. A compact external neural encoder then learns a 256-dimensional representation from expert Good/Bad judgements, while CatBoost learns the quantitative relationship between that representation and the MIC/MBC endpoints. Human labels guide source training; a new molecule does not require a human label when its representation or predicted activity is computed. This separation provides a concrete way to examine whether coarse expert supervision can organise useful molecular features for a distinct quantitative task.

### intro_03

We also test whether a frozen representation followed by a decoder is preferable to direct backbone adaptation in this setting. The completed follow-up compares frozen prediction heads, LoRA and full fine-tuning, and evaluates both prediction routes from human-guided partial-backbone initialisation. Full fine-tuning improves cation-holdout prediction in the tested procedure but has higher error on the independently measured OOD compounds; freezing the human-guided partial-backbone representation and fitting CatBoost gives lower OOD error than direct prediction from the same source initialisations. These results motivate a conditional choice of prediction route, rather than a general claim that fine-tuning is harmful or that a smaller adapter is necessarily superior. Matched source panels and label-shuffling controls assess whether the assignment of supervisory labels contributes beyond an added training stage.

### fig1_caption

This is a conceptual illustration of the modelling workflow. Its ascending accuracy curves are schematic; the numerical comparisons are defined by the reported training and evaluation protocols. The trainable feature encoder and the quantitative decoder are described in Section 2.1.

### annotation_count

The recovered computational archive contains 1,103 final molecule-level Good/Bad calls. These final outcomes are distinguished from the earlier collection count reported above, which requires confirmation from the annotation records. The new matched-source panels are constructed from the recovered outcomes after standardisation and target-cation exclusion.

### coauthor_fields

[COAUTHORS — annotation provenance: confirm collection and final counts; annotators and information shown to them; blinding and voting; handling of uncertain calls; inter-annotator agreement; collection dates; and access to quantitative activity measurements.]

### section2_1_01

The reference encoder operates outside MolFormer. For a SMILES string s, the frozen backbone produces h₀ = fθ(s) ∈ R⁷⁶⁸. The archived StandardScaler normalises these input features before an external MLP produces z ∈ R²⁵⁶ through layers of width 512, 384 and 256. Expert labels train the MLP parameters ψ without updating the backbone parameters θ. A subsequent decoder predicts quantitative MIC/MBC from z and a task code. This feature adapter is distinct from LoRA updates inside the transformer and from partial or full backbone fine-tuning. The external encoder contains 691,584 trainable parameters. Its source-training contrastive projection head is removed when the 256-dimensional features are passed to the quantitative decoder.

### section2_1_setup

The new adaptation comparison uses the original 105-QAC target cohort, with MIC and MBC against S. aureus and E. coli, and the 17 newly synthesised compounds from four scaffold families. Fixed five-fold cation and scaffold holdouts assess new-compound prediction; the OOD decoder is fitted on the 105 compounds. The pretrained frozen-head, LoRA and full-fine-tuning branches each use three target-training seeds. The two human-guided prediction routes additionally share source checkpoints 0–2, allowing their starting representation to be held fixed.

### section2_1_02

In a separate completed backbone experiment, direct full fine-tuning gave cation/scaffold RMSE 1.863 ± 0.045/1.970 ± 0.026, but OOD RMSE 3.032 ± 0.408. Direct LoRA gave OOD RMSE 2.756 ± 0.172, while a frozen pretrained backbone with a linear head gave 2.560 ± 0.206. These results demonstrate that improved grouped-validation performance need not produce lower error on the new chemical families under the tested optimisation budget.

### section2_1_03

Using the same three human-guided partial-backbone source checkpoints, direct target prediction gave OOD RMSE 2.412 ± 0.088, compared with 2.106 ± 0.071 when the source representation was frozen and decoded with CatBoost. The latter route gave cation/scaffold RMSE 1.743 ± 0.031/1.819 ± 0.044. These human-guided backbones are separate follow-up models, not the external compact encoder described above. All values use log₂(mg/L);  ±  denotes sample SD across three complete paired runs, not CV-fold SD or a 95% confidence interval. OOD scores include 67 exact endpoints, with the remaining bound retained separately.

### section2_1_04

The route comparison changes adaptation and decoding together and therefore does not isolate a causal effect of human-label meaning. To retain the compact v5 architecture when testing supervisory content, a separate controlled follow-up trained encoders on the same 681 source molecules (377 training and 304 validation), with target cations excluded and five paired source seeds. This follow-up fixes source exposure and training updates and omits SMOTE; it is not an exact replay of the archived SMOTE procedure. Human and shuffled-human guidance give OOD RMSE 2.268 ± 0.077 and 2.172 ± 0.112, respectively, where ± is sample SD over the five source runs. This compact-encoder control does not establish a human-content advantage. We consequently interpret the route results as evidence about the stated prediction procedures, without attributing them to a uniquely human semantic mechanism.
