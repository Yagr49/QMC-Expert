# Прямой fine-tuning и проверка вклада обученных весов

Все 363 direct target fit и 1,331 decoder fit завершены на сервере. Все метрики пересчитаны из сохранённых endpoint predictions. Все 33 final-OOD модели независимо загружены повторно; совпали 2,244 предсказания, включая bound.

QAC: 105 salts / 103 cations / 29 scaffolds, 420 точных endpoint values. OOD: 17 compounds / 4 scaffold families, 67 точных значений и IT505 Ec_MBC >500 mg/L. RMSE — log2(mg/L), mean seed-specific score, не ensemble.

## Прямое предсказание: backbone + target head

Три пары source/target seeds (0,1,2), одинаковые folds, 30 epochs. Разный source objective и capacity — явно обозначенные различия. No OOD tuning.

| Initialisation | Target adaptation | Cation CV | Scaffold CV | OOD-17 |
|---|---|---:|---:|---:|
| expert | partial | 1.797 | 1.834 | 2.412 |
| expert-shuffled | partial | 1.929 | 1.990 | 2.963 |
| quant-binary | partial | 1.745 | 1.901 | 2.510 |
| quant-binary-shuffled | partial | 1.945 | 2.027 | 3.076 |
| quant-continuous | partial | 1.737 | 1.869 | 3.075 |
| quant-shuffled | partial | 1.820 | 1.907 | 3.116 |
| raw-molformer | compact | 1.981 | 2.009 | 2.864 |
| raw-molformer | full | 1.863 | 1.970 | 3.032 |
| raw-molformer | linear | 2.013 | 1.986 | 2.560 |
| raw-molformer | lora | 2.040 | 2.089 | 2.756 |
| raw-molformer | partial | 1.894 | 1.996 | 3.008 |

## Обученное представление + decoder и возврат весов

Пять source seeds; отдельно сохраняются checkpoint buffers. Decoder refit для каждого представления. Шесть source arms после rewind-all дают одинаковые representations и predictions внутри seed. Pure raw reference имеет исходные buffers.

| Source | Encoder intervention | Cation CV | Scaffold CV | OOD-17 |
|---|---|---:|---:|---:|
| expert | intact | 1.737 | 1.842 | 2.054 |
| expert | rewind_all | 1.846 | 1.938 | 2.297 |
| expert | rewind_blocks | 1.846 | 1.938 | 2.297 |
| expert | rewind_outer_norm | 1.737 | 1.842 | 2.054 |
| expert-shuffled | intact | 1.857 | 1.963 | 2.336 |
| expert-shuffled | rewind_all | 1.846 | 1.938 | 2.297 |
| expert-shuffled | rewind_blocks | 1.847 | 1.938 | 2.297 |
| expert-shuffled | rewind_outer_norm | 1.858 | 1.963 | 2.336 |
| quant-binary | intact | 1.806 | 1.856 | 2.099 |
| quant-binary | rewind_all | 1.846 | 1.938 | 2.297 |
| quant-binary | rewind_blocks | 1.846 | 1.938 | 2.297 |
| quant-binary | rewind_outer_norm | 1.806 | 1.856 | 2.099 |
| quant-binary-shuffled | intact | 1.889 | 1.966 | 2.373 |
| quant-binary-shuffled | rewind_all | 1.846 | 1.938 | 2.297 |
| quant-binary-shuffled | rewind_blocks | 1.845 | 1.939 | 2.294 |
| quant-binary-shuffled | rewind_outer_norm | 1.890 | 1.966 | 2.373 |
| quant-continuous | intact | 1.715 | 1.814 | 2.237 |
| quant-continuous | rewind_all | 1.846 | 1.938 | 2.297 |
| quant-continuous | rewind_blocks | 1.847 | 1.938 | 2.297 |
| quant-continuous | rewind_outer_norm | 1.715 | 1.814 | 2.237 |
| quant-shuffled | intact | 1.872 | 1.945 | 2.277 |
| quant-shuffled | rewind_all | 1.846 | 1.938 | 2.297 |
| quant-shuffled | rewind_blocks | 1.846 | 1.938 | 2.297 |
| quant-shuffled | rewind_outer_norm | 1.872 | 1.945 | 2.277 |
| raw-molformer | raw | 1.858 | 1.978 | 2.265 |

## Интерпретация

В tested cation CV full FT (1.863) лучше по point estimate, чем frozen linear (2.013) и LoRA (2.040). LoRA minus full ΔRMSE +0.177 [0.071, 0.286] при exploratory paired seed/scaffold bootstrap. На OOD frozen linear 2.560, LoRA 2.756, full 3.032. Эти fixed-budget процедуры не поддерживают универсальную необходимость малых адаптеров; ранжирование меняется с validation regime.

Direct human-source FT: 1.797 / 1.834 / 2.412. Real quantitative guidance имеет меньшие cation point errors (continuous 1.737, binary 1.745), а human — меньшие scaffold/OOD point errors. Human versus quantitative cation intervals включают ноль; это не доказанная эквивалентность.

После возврата всех обученных human encoder weights ΔRMSE +0.109 [0.037, 0.201] в cation CV, +0.097 [-0.004, 0.228] в scaffold CV, +0.243 [-0.067, 0.582] на OOD. Только cation contrast здесь имеет интервал полностью выше нуля. Все intervals unadjusted, 5,000 draws, conditional on fitted models; OOD scaffold intervals опираются всего на четыре families.

Возврат outer LayerNorm не меняет human decoder predictions; возврат верхних восьми блоков почти воспроизводит эффект rewind-all. Это sensitivity конкретной pipeline. Аффинные/геометрические изменения могут быть невидимы выбранному decoder; отсутствие изменения prediction не означает отсутствие изменения representation.

При одинаковых первых трёх source checkpoints human direct/frozen-decoder RMSE: 1.797/1.743 (cation), 1.834/1.819 (scaffold), 2.412/2.106 (OOD). OOD difference +0.306 [-0.278, 0.971] не устанавливает превосходство decoder route. Для continuous и binary прямой route хуже на OOD по условным four-family intervals; полные contrasts сохранены без выбора выгодных.

Контроли показывают contribution real human label assignment и learned weight updates к held-out prediction. Они не локализуют человеческое понятие и не доказывают причинность molecular fragment → antibacterial activity. Независимость human information от численных измерений остаётся соавторам в H1–H7.

## Воспроизводимость и источники

93 intact/raw cation/scaffold/OOD prediction sets воспроизведены с точностью CSV (<1e-12). Intact representation replay byte-exact; buffer states совпадают между source arms внутри seed. Head initialisations, batch orders и train-only scales matched. Все adverse scores сохранены; pooled R² не используется.

Final snapshot: snapshot_20261012T182114Z. Code/protocol hashes, source/target IDs, parameter counts, curves и model hashes сохранены. Final-OOD checkpoints находятся в /home/yagr/coma_finetune_causal_20261012/direct/checkpoints. Для partial/full CV архивируются heads/buffers, hashes и deterministic replay recipe; полные CV backbone веса не сохранялись.

Опубликованные benchmark метрики проверены отдельно в literature/METRIC_AUDIT_RU.md и published_metrics.csv. Notebook recovery сохраняет provenance исходных апрельских/майских и июльских цифр, включая OOD regression 2.133. Публикационные benchmark scores, историческая row-level validation и новые grouped predictions — разные протоколы.

## Артефакты

direct_predictions.csv / ablation_predictions.csv — все endpoint predictions и qualifiers; *_metrics.csv / *_summary.csv — полные метрики; paired_bootstrap.csv — все contrasts; *_censor_sensitivity.csv — lower-bound ошибки для censored observation; verification.json — machine-readable checks; figure7/figure8/figureS22 — PDF/PNG/SVG.
