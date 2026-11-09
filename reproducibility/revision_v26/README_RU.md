v26: обновление OOD (§2.3) и интерпретации (§2.4) на основе v25.

Файлы: 2026_10_14_Paper_2_edited-v26_OOD_and_interpretation.docx в корне COMA; Supplementary_Information_v26.docx; MANUSCRIPT_REVIEW.html. Все новые и переработанные абзацы/подписи выделены жёлтым. Исходные файлы не перезаписаны.

§2.3
Описание четырёх химических семейств, синтез, молекулярные классы и схемы сохранены буквально. Уточнён ввод: четыре scaffold families, 17 новых QAC, mono/bis/multi. Количественная проверка использует 67 точных MIC/MBC записей; IT505/Ec_MBC >500 mg/L сохранён как граница и не превращён в точное измерение500.

В §2.3.5 различены три ветки:
1. Archived v5: human/text RMSE2.023 против raw/text2.245, один checkpoint, без выдуманного SD.
2. Source-matched compact: пять seeds, categorical task codes, human2.268±0.077, binaryMIC2.276±0.095, continuousMIC2.474±0.131, shuffledhuman2.172±0.112, raw2.504. Human улучшает raw в условной четырёхсемейной оценке; meaningful-label advantage не установлен.
3. Backbone routes: три runs, frozenhead2.560±0.206, LoRA2.756±0.172, fullFT3.032±0.408, humanpartialdirect2.412±0.088, frozenhumanpartial→CB2.106±0.071. Direct-minus-decoder interval пересекает ноль; lower point loss не объявляется доказанной победой.

Новая Fig. 9 — мягкие вертикальные violin с реальными endpoint error summaries: отдельные панели compact и backbone, медианы/IQR и все67точек/хвосты. Старая zero/few-shot картинка v5 перенесена в SI как Fig. S33 с исходными raster bytes. Её протокол использовал часть OOD labels для адаптации и отличается от текущего внешнего теста.

§2.4
Переписан вокруг трёх вопросов: геометрия, использование feature blocks количественным декодером и влияние label/weight interventions. CKA0.933/0.946 и probes0.891±0.037 /0.844±0.060 проверены по CSV и May notebook. SHAP scores2.930/0.636/0.761 подтверждены сохранённым выводом May cell4. Они больше не интерпретируются как установленная структурно-биологическая декомпозиция.

Основной текст теперь различает compact null/competitive-shuffle controls и partial-backbone contrasts, где эффект label assignment/learned weights разрешается для некоторых split-проверок. Старые утверждения biological causal channel и statistically proven equivalence удалены из основного текста. Прежняя conceptual Fig. 10 сохранена в SI как Fig. S34 с явной оговоркой. Там же сохранён полный исходный интерпретационный текст как historical provenance, а его сильные каузальные/эквивалентностные выводы обозначены как superseded.

Новая SI Fig. S35 — реальные conditional loss contrasts (human−shuffle и reset−intact) для двух разных архитектур. В SI добавлены Tables S49 (полные OOD scores по протоколам) и S50 (контрасты с интервалами). Всего SI51native tables/35figures; прежние49tables/32figures и все их Office parts/media сохранены.

Conclusion согласован с §2.3/§2.4: убраны повторяющиеся неподтверждённые заявления эквивалентности, универсального превосходства и отдельной biological component. Сохранена центральная идея полезности человеческой супервизии с явными границами evidence.

Introduction, §2.1, §2.2, химия, Experimental и библиография сохранены буквально. Новых model fits не запускалось. Числа пересчитаны/проверены по завершённым predictions, mean±sampleSD относится к source/runs; conditional bootstrap intervals не являются full retraining uncertainty. Все проверки: document_validation.json и figure_validation.json. PDF/SVG/PNG600dpi/Aptos.
