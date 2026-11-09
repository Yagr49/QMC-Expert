# Прямой fine-tuning и интервенции в обученные веса

Расширение выбрано после предыдущих результатов; это exploratory follow-up,
не preregistration. Протокол фиксируется до предсказаний нового расширения.

## A. Качество перед интерпретацией

Исходные 105 QAC/103 cations/29 scaffolds, четыре MIC/MBC задачи;
те же пять cation folds, пять scaffold folds, final-QAC→17 OOD.
420 точных QAC endpoints; OOD 67 exact + один `IT505 Ec_MBC >500 mg/L`.
Все новые концентрационные ошибки в log2(mg/L). OOD не используется в выборе.

1. Из одной исходной MolFormer-XL модели: frozen linear head,
   frozen compact MLP (256→128→4), LoRA rank8/alpha16 в query/value всех 12 слоёв,
   partial FT верхних восьми блоков + внешняя encoder LayerNorm, full backbone FT.
   Три парных target seeds (0,1,2), 11 target fits каждый.
   Это 165 fit для сравнения capacity. MLP — внешняя проекция; LoRA — внутренний
   low-rank adapter. В конкретной HF модели pooler — mean pooling без параметров.
2. Для partial target FT дополнительно шесть source-initialisation arms:
   human/continuous MIC/binary MIC и их matched shuffled controls.
   Source checkpoint seed совпадает с target seed (0,1,2). 198 дополнительных fit.
   Все source cations исключают QAC/OOD; source dataset, начальные веса,
   порядок и бюджет уже matched. Всего 363 direct target fits.

Общая четырёхвыходная regression head: LayerNorm(768)→Linear(4).
Compact branch: LayerNorm→Linear(256)→GELU→Dropout(.1)→Linear(128)→GELU
→Dropout(.1)→Linear(4). Train-only стандартизация четырёх target задач.
30 фиксированных epochs, batch32, MSE, AdamW weight_decay .01,
head/LoRA LR .001 / backbone LR .00003, OneCycle, clip norm1.
Final checkpoint без early stopping. Одинаковый порядок примеров и seed
stochastic forward для парных source arms. Считаются фактические parameters,
updates, init/order/label/input hashes. Head-only не использует test labels.
Бюджеты не оптимизированы для каждого метода: вывод касается объявленных
процедур и не устанавливает лучшую возможную конфигурацию full FT.

## B. Что требуется назвать усвоенным сигналом

Operational definition: вклад адаптированных encoder parameters в prediction
held-out MIC/MBC после refit общего декодера. Это не утверждение о понимании,
независимой химической интуиции или биологическом механизме.

Шесть source arms × пять paired source seeds × четыре состояния:
intact, rewind внешней encoder LayerNorm, rewind upper-eight-block weights,
rewind всех encoder parameters к pretrained. Исходные feature-map buffers
из source checkpoint сохраняются при weight rewind; они хешируются.
Таким образом, rewind-all служит контролем raw weights + post-training
buffer state. Проверяется одинаковость buffers и rewind-all representations
между шестью source arms внутри seed; дедупликация до проверки запрещена.
Чистый raw pretrained reference с исходными buffers приводится отдельно.

120 adapted/rewound configurations + один чистый raw reference.
Для каждой: общий one-hot CatBoost300/depth5/LR.05/seed1729 на прежних
cation/scaffold folds и final QAC→OOD. 1,331 fit одного joint-task decoder.
Декодер каждый раз refit на соответствующем представлении, поэтому удаление
весов не смешивается с подачей изменённого представления в старый декодер.
Fixed target encoding layout воспроизводит v14: QAC104, один отсутствующий
compound вместе с тремя reference structures, OOD в прежнем порядке.
Нет изменения структуры молекул или labels при этой интервенции.

Проверки: real vs shuffled; intact vs rewound; matched binary vs human;
rewind-all vs pure raw для влияния buffers; прямое target FT vs decoder.
Парные bootstrap intervals: общие molecule/scaffold clusters и seed indexes,
5,000 draws; OOD всего четыре families, поэтому bounds descriptive.
Primary endpoint losses и pooled RMSE/MAE; pooled R² не используется для
вывода о внутри-task точности. Все adverse outcomes сохраняются.

Weights/components вмешательство меняет computational pipeline. Оно не
локализует конкретное человеческое понятие и не доказывает причинность
структуры для antibacterial activity. Annotation H1–H7 остаются соавторам.

## Сервер и воспроизводимость

Только уже разрешённый сервер yagr@100.76.26.71, отдельный каталог
/home/yagr/coma_finetune_causal_20261012; исходные результаты read-only.
Pinned ibm/MoLFormer-XL-both-10pct revision
7b12d946c181a37f6012b9dc3b002275de070314, cached source checkpoints из
независимого 30-run повтора. CUDA float32, TF32 выключен.
Службы systemd user с Linger=yes; вычисление не зависит от Mac/SSH.
Ключи/OpenRouter/OpenAI на сервер не передаются и API не вызываются.
Полные trained weights direct-моделей сохраняются для final-QAC→OOD fits.
Для partial/full CV остаются head/buffers, хеши encoder weights, init/order,
curves и predictions; backbone можно повторить из source checkpoint и recipe.
Это ограничивает дополнительное хранение несколькими GB, а не десятками GB.
