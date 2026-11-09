Что добавлено в v19.

Tables 1–2: три отдельные новые строки пятифолдовой CV сохранённого человеческого encoder: task_id, organism+endpoint и text codes. Каждая RMSE/R² имеет собственное среднее ± SD по пяти фолдам. Это 30 новых CatBoost fit с вашим бюджетом 500/depth6/lr0.05/seed42. Сохранённое обучение encoder с SMOTE не изменялось; для текста используется восстановленный октябрьский кэш. Первые строки таблиц остаются вашими исходными holdout-числами; CV-разброс к ним не приписывается.

Table 4: среднее ± SD по пяти полным source-seed запускам. Например, Human: cation 1.872±0.034, scaffold 2.158±0.050, OOD 2.268±0.077. Это разброс обучения моделей, а не разброс CV-фолдов.

Table 6: среднее ± SD по трём парным source/target запускам. Оба маршрута human partial сравниваются на seed 0–2.

Исходный probing: восстановлены ваши сохранённые R² 0.891±0.037 и 0.844±0.060 по пяти CV-фолдам. Это восстановление координат embedding, а не MIC/MBC performance.

SI Tables S40–S44: полные fold metrics, source-seed variability, grouped fold variability, original probing и соответствие новых опытов вашим подходам. Fold SD используется с numpy.std ddof=0, как в вашем CV-коде; SD повторных source-run — sample SD ddof=1. Оба вида ± не являются автоматически 95% доверительными интервалами; прежние bootstrap CI сохранены отдельно.

Новые вычислительные данные получены на ваших целевых наборах: 105 QAC и 17 OOD. Для реконструкции исходной CV используется прежний spreadsheet-view из 108 строк, представляющих 105 уникальных солей. В row-wise CV разные задачи одной молекулы могут быть по обе стороны разбиения; grouped evaluation остаётся отдельной проверкой новых молекул.

Основа новых расчётов — ваш frozen MolFormer → compact encoder → task-aware CatBoost. Matched source-control сохраняет архитектуру, но меняет source panel и не использует SMOTE; direct fine-tuning и новые графовые/табличные модели — самостоятельные сравнения. Точное соответствие находится в SI Table S44.

Основной файл: `../../2026_10_13_Paper_2_edited-v19_CV_and_seed_variability.docx`. SI: `Supplementary_Information_v19.docx`. Проверки: `document_validation.json`. Исходный v5 и v18 сохранены. Новые CV-результаты: `rowcv_results/`, отдельные fold/seed summaries: `analysis/`.
