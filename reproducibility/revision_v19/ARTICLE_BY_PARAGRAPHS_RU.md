Что добавлено в v19.

Tables 1–2: три отдельные новые строки пятифолдовой CV сохранённого человеческого encoder: task_id, organism+endpoint и text codes. Каждая RMSE/R² имеет собственное среднее ± SD по пяти фолдам. Это 30 новых CatBoost fit с вашим бюджетом 500/depth6/lr0.05/seed42. Сохранённое обучение encoder с SMOTE не изменялось; для текста используется восстановленный октябрьский кэш. Первые строки таблиц остаются вашими исходными holdout-числами; CV-разброс к ним не приписывается.

Table 4: среднее ± SD по пяти полным source-seed запускам. Например, Human: cation 1.872±0.034, scaffold 2.158±0.050, OOD 2.268±0.077. Это разброс обучения моделей, а не разброс CV-фолдов.

Table 6: среднее ± SD по трём парным source/target запускам. Оба маршрута human partial сравниваются на seed 0–2.

Исходный probing: восстановлены ваши сохранённые R² 0.891±0.037 и 0.844±0.060 по пяти CV-фолдам. Это восстановление координат embedding, а не MIC/MBC performance.

SI Tables S40–S44: полные fold metrics, source-seed variability, grouped fold variability, original probing и соответствие новых опытов вашим подходам. Fold SD используется с numpy.std ddof=0, как в вашем CV-коде; SD повторных source-run — sample SD ddof=1. Оба вида ± не являются автоматически 95% доверительными интервалами; прежние bootstrap CI сохранены отдельно.

Новые вычислительные данные получены на ваших целевых наборах: 105 QAC и 17 OOD. Для реконструкции исходной CV используется прежний spreadsheet-view из 108 строк, представляющих 105 уникальных солей. В row-wise CV разные задачи одной молекулы могут быть по обе стороны разбиения; grouped evaluation остаётся отдельной проверкой новых молекул.

Основа новых расчётов — ваш frozen MolFormer → compact encoder → task-aware CatBoost. Matched source-control сохраняет архитектуру, но меняет source panel и не использует SMOTE; direct fine-tuning и новые графовые/табличные модели — самостоятельные сравнения. Точное соответствие находится в SI Table S44.

Краткий разбор содержательных абзацев.

1. Introduction — абзац (12)
Вводим проблему антибиотикорезистентности и ограниченного инновационного pipeline. Отделяем системные антибиотики из отчётов WHO от исследуемых топических биоцидов.

1. Introduction — абзац (13)
Показываем, почему ML полезен для поиска антибактериальных соединений и оптимизации их свойств; сохраняем литературный вход исходного v5.

1. Introduction — абзац (14)
Объясняем разные способы внесения domain knowledge: физические ограничения, химические признаки и биологические связи. Это мотивирует сравнение видов информации.

1. Introduction — абзац (15)
Переходим от ограничений модели к человеческому суждению как метке обучения. MolSkill и другие работы мотивируют проверку Good/Bad для последующей количественной регрессии.

1. Introduction — абзац (16)
Связанные виды бактерий и MIC/MBC можно моделировать совместно. Текстовые коды задач проверяем отдельно от простого указания task identity.

1. Introduction — абзац (17)
Численные данные неоднородны по протоколам. Эксперт потенциально может их обобщать, но это не установленный факт без записей о сборе разметки.

1. Introduction — абзац (18)
Обосновываем выбранную химическую задачу: катионные биоциды QAC и предыдущие ML-подходы в этой области.

1. Introduction — абзац (19)
Связываем предыдущую QAC-работу с новым вопросом: откуда приходит полезная информация для представления. Обозначаем последовательность исходных результатов и новых проверок.

1. Introduction — абзац (21)
Подробно объясняем три объекта: frozen MolFormer выдаёт 768 признаков; внешний encoder создаёт 256; количественный decoder использует эти признаки и код задачи. Source-метки не нужны для inference новой молекулы.

1. Introduction — абзац (22)
Определяем внешний адаптер признаков и отличаем его от LoRA, partial и full fine-tuning. Меньшая модель не гарантирует лучшее качество; это проверяем.

2.1 Learning the guided molecular representation — абзац (28)
В финальном архиве 1103 Good/Bad. Старые утверждения про 1500 соединений, три голоса и blind collection должны подтвердить соавторы.

2.1 Learning the guided molecular representation — абзац (29)
Классификационный screen мотивирует MolFormer. Цитируем именно F1=0.665 на сохранённом SI-графике; 0.655 и accuracy 0.856 из текста имеют отдельный исторический статус.

2.1 Learning the guided molecular representation — абзац (30)
Возвращаем contrastive encoder v5 с BatchNorm, ReLU, dropout и историческим Borderline SMOTE. Отличаем encoder output от projection head и регрессионного decoder.

2.1 Learning the guided molecular representation — абзац (31)
Сохраняем t-SNE и cluster metrics как геометрический анализ. Это не доказательство качества регрессии или причинного знания механизма.

2.2 Training on QACs — абзац (36)
Исходные embeddings предсказывают четыре log2 endpoint. В восстановленном CatBoost task_id — native categorical; literal one-hot имеет отдельную новую проверку.

2.2 Training on QACs — абзац (37)
Показываем подтверждённые сохранённым майским выводом сильные R² human/text и human/categorical. Исправляем округление 0.5918→0.59; не заявляем воспроизведение всех старых RMSE.

2.2 Training on QACs — абзац (42)
Сохраняем исходные parity-панели. Их выигрыш мотивирует проверки, но не устанавливает перенос на новые бактерии или новые виды активности.

2.2 Training on QACs — абзац (46)
Возвращаем сравнение с большой количественной multitarget моделью. Её checkpoint пока не найден; это не доказательство, что старая таблица использовала другую модель.

2.2 Training on QACs — абзац (47)
Разводим 1559 молекул, >18000 смешанных activity records и MIC-only экспорт 9338 записей/1153 молекулы. Число записей не равно числу независимых структур.

2.2 Training on QACs — абзац (48)
Старые human/text R² конкурентоспособны с количественными. Разница 0.59 vs 0.58 описательная; формальной эквивалентности или десятикратной экономии она не доказывает.

2.2 Training on QACs — абзац (49)
Интерпретация Good/Bad как обобщения измерений условна. Если эксперты видели те же числа, разметка является человеческим сжатием этих данных, а не независимым каналом.

2.3 Out of domain inference — абзац (55)
Новые 17 соединений относятся к четырём семействам. В untouched OOD остаются 67 точных значений и одна граница IT505 E. coli MBC >500.

2.3 Out of domain inference — абзац (58)
Описываем архитектуру QAC: core, tail, linker и три класса по количеству катионных центров.

2.3 Out of domain inference — абзац (59)
Вводим четыре выбранных гетероциклических scaffold и их экспериментальную оценку MIC/MBC.

2.3.1 Kojic acid-based bis-QACs — абзац (61)
Сохраняем путь синтеза kojic-acid bis-QACs: димеризация, хлорирование и кватернизация с алкиламинопиридинами.

2.3.2 Tetrahydropyridine-based bis-QACs — абзац (66)
Сохраняем multicomponent synthesis tetrahydropyridine-платформ и дальнейшую реакцию Menshutkin.

2.3.2 Tetrahydropyridine-based bis-QACs — абзац (69)
Объясняем оптимизацию синтеза, конкурирующий pyran и эпимеризацию. Вспомогательные химические SI-материалы зарезервированы для соавторов.

2.3.3 Dihydropyran-based mono-QACs — абзац (71)
Сохраняем синтез CF3-dihydropyran mono-QACs и последующее N-алкилирование.

2.3.4 Glycoluril-based multi-QACs — абзац (76)
Сохраняем четырёхстадийный путь glycoluril multi-QACs. Исправляем подпись схемы, которая ошибочно называла их mono-QACs.

2.3.5 Out-of-domain performance verification — абзац (81)
Сохраняем исходный OOD benchmark и различаем regression, classification и ±1-class agreement. Label-free там означает отсутствие task-code, а не отсутствие target training.

2.3.5 Out-of-domain performance verification — абзац (82)
Уточняем старые zero-shot/few-shot термины. Few-shot использует часть OOD и является отдельным exploratory опытом; новые проверки не обучаются на этих 17 молекулах.

2.4 Understanding the new embeddings — абзац (86)
Ставим вопрос о геометрии и предсказательной роли embeddings. Новая PCA-картинка показывает реальные 105 молекул, не причинное разделение знания.

2.4 Understanding the new embeddings — абзац (89)
CKA и probing показывают геометрическую связь с MolFormer. Возвращены исходные пятьфолдовые R²±SD: 0.891±0.037 и 0.844±0.060; они не являются MIC/MBC метриками.

2.4 Understanding the new embeddings — абзац (90)
Сохраняем старый SHAP, но не трактуем отношение вкладов 0.22 как причинную долю информации. Коррелированные блоки могут перераспределять attribution.

2.4 Understanding the new embeddings — абзац (91)
Разделяем QAC-only binned ablation, полную quantitative модель, майский/июльский архив и новый расчёт. CausalForest и bootstrap ΔRMSE — разные анализы.

2.4 Understanding the new embeddings — абзац (92)
На 17 молекулах subgroup effects ограниченно оцениваются. Отсутствие resolved advantage не доказывает отсутствия гетерогенности.

2.4 Understanding the new embeddings — абзац (93)
Сохраняем исходную идею полезного направленного представления. Для вывода о содержании человеческих меток нужны более сильные контроли.

2.5 Reconstructing the reference analysis and defining the generalisation question — абзац (95)
Майский split разбивал строки molecule×task. Это другая задача, чем предсказание нового соединения; не объясняем весь разрыв метрик одним split.

2.5 Reconstructing the reference analysis and defining the generalisation question — абзац (96)
Девять реконструированных конфигураций совпадают на двух серверах. Новые task-векторы и среда отличаются от исторических, поэтому это approximate reconstruction.

2.5 Reconstructing the reference analysis and defining the generalisation question — абзац (97)
Добавлен отдельный пятифолдовый повтор вашего подхода. Собственные CV-mean±SD стоят рядом с исходными holdout-значениями; свежий text-cache и среда делают это approximate reconstruction.

2.5 Reconstructing the reference analysis and defining the generalisation question — абзац (98)
На всех 105 солях считаем grouped CV: 103 катиона и 29 scaffold. Старые source-корпусы пересекаются с QAC; matched source исключает target cations.

2.5 Reconstructing the reference analysis and defining the generalisation question — абзац (99)
В новом archived-feature OOD human/text RMSE 2.023 против raw/text 2.245. На grouped CV аналогичного выигрыша нет; разные task codes сравниваются отдельно.

2.6 Matched guidance in the compact reference architecture — абзац (103)
Шесть matched compact arms на одной source-выборке, пять paired seeds и 480 updates. No-SMOTE контроль отличается от исторического v5; continuous objective отличается от binary.

2.6 Matched guidance in the compact reference architecture — абзац (104)
Показываем действительное число параметров: 691584 encoder, 741504 contrastive route, 691841 regression route. Усредняем метрики отдельных seed, не ошибки ансамбля.

2.6 Matched guidance in the compact reference architecture — абзац (105)
Human/binary/continuous дают близкую cation CV. На OOD human лучше raw, но human–continuous интервал не устанавливает превосходства.

2.6 Matched guidance in the compact reference architecture — абзац (106)
Главный semantic-content контроль real vs shuffled human не выигрывает. Альтернативные объяснения остаются гипотезами; положительный partial-backbone результат — отдельный опыт.

2.6 Matched guidance in the compact reference architecture — абзац (107)
С одним compact checkpoint заменяем только task codes. Text, permutation и random codes не устанавливают semantic advantage на четырёх знакомых задачах.

2.7 Decoder and direct-adaptation alternatives — абзац (113)
264 tabular fit на старых raw/human v5 embeddings. PCA32 и бюджеты объявлены; OOD не выбирает лучший representation.

2.7 Decoder and direct-adaptation alternatives — абзац (114)
TabPFN, TabFM и AutoGluon не улучшают одновременно все regimes. Chemprop и RDKit сохранены как отдельные структурные сравнения в SI.

2.7 Decoder and direct-adaptation alternatives — абзац (119)
Full fine-tuning хорош на cation CV, но слаб на OOD при этом бюджете. Human partial frozen representation + CatBoost лучше прямого prediction на тех же трёх seed.

2.8 Learned updates, label content and the scope of causality — абзац (123)
Compact weight-only reset сохраняет BatchNorm state; full initial-state reset удаляет и его. Интервалы compact reset включают ноль.

2.8 Learned updates, label content and the scope of causality — абзац (124)
Отдельный partial-backbone опыт обнаруживает вклад весов на cation CV. Это вычислительное вмешательство, а не обнаруженный биологический механизм.

2.8 Learned updates, label content and the scope of causality — абзац (125)
Ограничиваем causal claim конкретным intervention и измеряемым loss. Независимость human knowledge требует H1–H7; statistical equivalence не следует из interval covering zero.

3. Conclusion — абзац (127)
Главные исходные положительные R² остаются частью статьи. У них частичная notebook provenance, а новые проверки идут рядом.

3. Conclusion — абзац (128)
Полезность внешнего адаптера зависит от task encoding и decoder. OOD и molecule×task holdout отвечают на разные вопросы.

3. Conclusion — абзац (129)
Новый compact контроль не доказывает вклад содержания human labels. Частично положительные backbone результаты поддерживают условную, а не универсальную интерпретацию.

3. Conclusion — абзац (130)
Современные модели и direct fine-tuning дают практический контекст. Дальнейшие необходимые данные: annotation information access, quantitative checkpoint и перенос между assay contexts.

4.3.1 Human annotation: contributor fields — абзац (214)
H1–H7 оставлены для восстановления сбора разметки. Итоговые calls доступны; индивидуальные голоса не выдумываем.

4.3.2 Historical model and new reconstruction — абзац (223)
Фиксируем историческую архитектуру, reconstructed CatBoost budget, splits, версии task descriptions и кодовые контроли.

4.3.3 Matched compact-encoder follow-up — абзац (225)
Фиксируем matched training split, train-only preprocessing, AdamW schedule, 80 epochs, 480 updates и paired state/batch hashes.

4.3.3 Matched compact-encoder follow-up — абзац (226)
Различаем fold SD, source-seed SD и 95% bootstrap intervals. У одного OOD запуска нет фолдового или межseedового разброса.

4.3.4 Target cohorts, uncertainty and modern models — абзац (228)
Все 420 QAC endpoint точные; OOD 67 exact +1 bound. Описываем seed-mean scores и paired cluster bootstrap; четыре OOD scaffold ограничивают выводы.
