# OOD для будущей правки §2.3

§2.3 в v23 не менялся. Исходные полные абзацы ниже содержат и grouped-результаты, которые остаются в §2.1. В §2.3 переносим только соответствующие OOD-части.

## Архивный абзац 40

The new adaptation comparison uses the original 105-QAC target cohort, with MIC and MBC against S. aureus and E. coli, and the 17 newly synthesised compounds from four scaffold families. Fixed five-fold cation and scaffold holdouts assess new-compound prediction; the OOD decoder is fitted on the 105 compounds. The pretrained frozen-head, LoRA and full-fine-tuning branches each use three target-training seeds. The two human-guided prediction routes additionally share source checkpoints 0–2, allowing their starting representation to be held fixed.

## Архивный абзац 41

In a separate completed backbone experiment, direct full fine-tuning gave cation/scaffold RMSE 1.863 ± 0.045/1.970 ± 0.026, but OOD RMSE 3.032 ± 0.408. Direct LoRA gave OOD RMSE 2.756 ± 0.172, while a frozen pretrained backbone with a linear head gave 2.560 ± 0.206. These results demonstrate that improved grouped-validation performance need not produce lower error on the new chemical families under the tested optimisation budget.

## Архивный абзац 42

Using the same three human-guided partial-backbone source checkpoints, direct target prediction gave OOD RMSE 2.412 ± 0.088, compared with 2.106 ± 0.071 when the source representation was frozen and decoded with CatBoost. The latter route gave cation/scaffold RMSE 1.743 ± 0.031/1.819 ± 0.044. These human-guided backbones are separate follow-up models, not the external compact encoder described above. All values use log₂(mg/L);  ±  denotes sample SD across three complete paired runs, not CV-fold SD or a 95% confidence interval. OOD scores include 67 exact endpoints, with the remaining bound retained separately.

## Архивный абзац 43

The route comparison changes adaptation and decoding together and therefore does not isolate a causal effect of human-label meaning. To retain the compact v5 architecture when testing supervisory content, a separate controlled follow-up trained encoders on the same 681 source molecules (377 training and 304 validation), with target cations excluded and five paired source seeds. This follow-up fixes source exposure and training updates and omits SMOTE; it is not an exact replay of the archived SMOTE procedure. Human and shuffled-human guidance give OOD RMSE 2.268 ± 0.077 and 2.172 ± 0.112, respectively, where ± is sample SD over the five source runs. This compact-encoder control does not establish a human-content advantage. We consequently interpret the route results as evidence about the stated prediction procedures, without attributing them to a uniquely human semantic mechanism.

## Архивный абзац 45

Figure 3 compares the distributions of absolute MIC/MBC prediction errors for frozen-head, LoRA, full-backbone and human-guided adaptation across cation, scaffold and independent OOD evaluation. The two human-guided routes use partial backbone adaptation and share source checkpoints; they are distinct from the external compact feature encoder described above.

## Архивный абзац 47

Figure 3. Absolute prediction-error distributions for (a) cation holdout, (b) scaffold holdout and (c) OOD-17. Each density uses the mean absolute error across three runs (seeds 0–2) for each molecule–endpoint pair: 420 exact observations in (a,b) and 67 in (c). These are not errors of ensemble predictions. White markers show medians; bars show interquartile ranges; faint OOD points represent individual endpoint summaries. Common linear axes retain all tails. Frozen head, LoRA and full FT start from pretrained MolFormer. Human direct and Human → CB share human-guided partial-backbone source checkpoints; the former further fine-tunes on targets, whereas the latter freezes source features and fits CatBoost. These human models are separate follow-ups, not the external v5 compact encoder. The IT505 E. coli MBC >500 mg/L bound is retained separately. Correlated endpoints and runs preclude interpreting density differences as significance or causal human-label effects.

## Смысл нового OOD-блока

17 соединений, 67 точных endpoints и отдельно сохранённая граница IT505/Ec_MBC >500 mg/L. RMSE ± sample SD трёх запусков: frozen head 2.560 ± 0.206; LoRA 2.756 ± 0.172; full FT 3.032 ± 0.408; human partial direct 2.412 ± 0.088; frozen human partial → CatBoost 2.106 ± 0.071. Компактный matched v5 human/shuffled контроль — отдельный пятиseed эксперимент: 2.268 ± 0.077 / 2.172 ± 0.112, без human-content преимущества. OOD-панель prepared в figures; не объявляем её compact v5 encoder и не делаем каузальный вывод по распределению ошибок.
