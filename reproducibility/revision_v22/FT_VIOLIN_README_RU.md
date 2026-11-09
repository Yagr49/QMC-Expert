# Figure 3: мягкие publication violin plots

Полностью новый график из сохранённых предсказаний, без новых model fits. Исходные численные результаты сохранены.

Файлы: `figures/figure3_backbone_route_error_violins.pdf`, `.svg`, `.png` (600 dpi). Размер canvas180×88mm, Aptos. Пастельная палитра: голубой, лаванда, персик, розовый, мята. Персик#E6B490 и мята#87CABA совпадают с новым Figure2. Подпись для статьи: `figure3_caption_EN.txt` (141words); подробная provenance: `figure3_FT_manifest.json`.

## Что показывает плотность

Для каждого route, режима и пары **молекула×endpoint** сначала вычислена абсолютная ошибка каждого из трёх запусков seeds0–2, затем усреднены эти три ошибки. KDE violin построен на420 полученных endpoint summaries для cation/scaffold CV или67 для OOD. Это:

- не KDE по трём итоговым RMSE;
- не ошибка ансамбля: `mean(abs(y−pred_seed))`, не `abs(y−mean(pred_seed))`;
- не1260 независимых наблюдений, полученных повторным счётом seed predictions;
- не тест значимости и не оценка эффекта человеческих меток сама по себе.

Белый круг — медиана этих endpoint summaries; тёмная полоска — межквартильный диапазон. Для OOD показаны все67 отдельные summaries бледными точками с фиксированным jitter, не связанным со значениями активности. Линейные оси одинаковые0–8.05, все наблюдаемые хвосты сохранены (максимум7.339). Никакого winsorisation, tail trimming или подбора bandwidth ради выделения результата нет; используется Scott bandwidth, KDE отображается только от фактического min доmax выборки.

## Какие модели

Первые три строки — pretrained MolFormer + frozen linear head, direct query/value LoRA и direct full fine-tuning. Две human строки используют одни и те же human-guided **partial-backbone source checkpoints** seeds0–2:

- Human direct дополнительно обновляет backbone под quantitative target prediction.
- Human→CB замораживает source representation и обучает CatBoost.

Они исходят из одинаковой source initialisation, но их конечные target pipelines и конечные состояния backbone различаются. Эти human backbone модели **не являются внешним компактным v5 MLP768→512→384→256**. Сравнение не доказывает, что внешний компактный адаптер лучше fullFT или что меньше параметров гарантируют лучшие предсказания. Human source training добавляет данные/бюджет; это сравнение практических процедур, а не изолированный эксперимент на параметризации/decoder.

## Проверка чисел

В `analysis/FT_route_seed_predictions.csv` сохранены907наблюдений×5routes×3seeds =13605 точных seed-predictions. В `FT_route_endpoint_mean_absolute_errors.csv` —4535 endpoint summaries. Каждой паре соответствует ровно три seed, её экспериментальный ответ идентичен во всех seed. Каждый route видит тот же регистр105 QAC/17 OOD и те же folds.

В каждом route сохранены три предсказания bound IT505/EcMBC>500mg/L в исходных файлах; они исключены из точных KDE. OOD содержит67 exact endpoints, а не68. Bound не подменён точным500.

RMSE каждого полного seed-запуска повторно рассчитан непосредственно из предсказаний, затем получены среднее и **sampleSD(ddof1)** по трём запускам. Это не CV-foldSD и не95%CI. Отдельная таблица: `analysis/FT_route_RMSE_mean_sample_SD.csv`. Все12 выбранных direct route/regime mean/SD совпадают с сохранённой v16 таблицей до1e−12; три frozen-human/CB mean/SD совпадают с независимой предыдущей проверкой seeds0–2.

Main DOCX и SI этим скриптом не меняются. Фактический Claude CLI работает на Mac и визуально проверяет новые Figures2–3; журнал и его заключение находятся в `reviews/claude_figures_*`.
