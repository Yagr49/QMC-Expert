# Новые сравнения моделей — все расчёты завершены

913 новых fit на фиксированных разбиениях QAC-105 и OOD-17. Метрики независимо пересчитаны из предсказаний.

RMSE в log2(mg/L); меньше — лучше. Cation/scaffold CV: 420 точных конечных точек у 105 молекул. OOD: 67 точных конечных точек у 17 молекул; одно значение >500 mg/L сохранено как bound.

## Полная таблица (без выбора по OOD)

| Модель | Представление | Cation CV | Scaffold CV | OOD-17 |
|---|---|---:|---:|---:|
| autogluon | expert_seed0 | 1.810 | 1.934 | 2.148 |
| autogluon | quant-binary_seed0 | 1.852 | 1.911 | 2.197 |
| autogluon | quant-continuous_seed0 | 1.886 | 1.955 | 2.289 |
| autogluon | raw-molformer | 1.953 | 1.938 | 2.208 |
| autogluon | rdkit | 1.716 | 1.828 | 2.222 |
| catboost | expert_seed0 | 1.767 | 1.901 | 2.124 |
| catboost | quant-binary_seed0 | 1.856 | 1.971 | 2.224 |
| catboost | quant-continuous_seed0 | 1.872 | 1.892 | 2.349 |
| catboost | raw-molformer | 1.890 | 1.956 | 2.295 |
| catboost | rdkit | 1.615 | 1.818 | 2.066 |
| chemprop | graph | 2.031 | 2.003 | 2.375 |
| tabfm | expert_seed0 | 1.730 | 1.814 | 1.992 |
| tabfm | quant-binary_seed0 | 1.814 | 1.936 | 2.110 |
| tabfm | quant-continuous_seed0 | 1.772 | 1.888 | 2.541 |
| tabfm | raw-molformer | 1.900 | 1.952 | 2.299 |
| tabfm | rdkit | 1.619 | 1.909 | 2.027 |
| tabpfn | expert_seed0 | 1.822 | 1.833 | 1.966 |
| tabpfn | quant-binary_seed0 | 1.838 | 1.920 | 1.995 |
| tabpfn | quant-continuous_seed0 | 1.853 | 1.932 | 2.265 |
| tabpfn | raw-molformer | 1.948 | 1.984 | 2.225 |
| tabpfn | rdkit | 1.725 | 1.909 | 1.978 |

## Что можно утверждать

Человеческое source-обучение конкурентоспособно с количественным source-обучением при смене декодера. Для TabPFN-V2 на OOD: Human 1.966, Quant-continuous 2.265, Quant-binary 1.995, Raw 2.225; для TabFM: 1.992, 2.541, 2.110 и 2.299 соответственно.

RDKit descriptors — сильный самостоятельный baseline: CatBoost даёт 1.615 в cation CV и 1.818 в scaffold CV. Human+TabPFN и RDKit+TabPFN на OOD почти равны (1.966 против 1.978). Утверждение «human лучше всех» эти данные не поддерживают.

Chemprop D-MPNN: средний RMSE по 3 seeds — 2.031 / 2.003 / 2.375 (cation / scaffold / OOD). Это конкретный фиксированный протокол на небольшой выборке, а не доказательство общей слабости графовых сетей.

Табличные сравнения используют один source seed0, PCA-32 для 768-dimensional embeddings и отдельные endpoint модели. Они дополняют основной 5-seed matched causal тест, а не заменяют его. AutoGluon: RF/XT/GBM/CAT, 60 s selection + refit; TabPFN: публичные V2 weights с библиотекой 9.1.0; TabFM: официальный JAX checkpoint. OOD не использовался для выбора настроек.

95% paired bootstrap intervals находятся в paired_cluster_bootstrap.csv. Cation/scaffold grouping согласована с CV; OOD дополнительно проверен по четырём новым scaffold families. При четырёх группах intervals следует считать описательными.

## Проверка прежних расчётов

Полный повтор основных v14 таблиц на прежних векторах совпал по всем предсказаниям. Все 30 matched partial-FT повторов совпали по initial state, IDs, batch order, labels, final loss и историческим предсказаниям; все 93 исторических target arrays совпали побитово.

При кодировании всех 105 молекул другими батчами векторы отличились на ~1e-6. CatBoost оказался чувствителен к этому для отдельных arms: например, mean OOD RMSE Quant-binary изменился с 2.099 до 2.068. Новые значения не заменяют прежние молча. Повтор прежнего batch layout с независимыми checkpoint восстановил ВСЕ 62 QAC105/OOD17 arrays побитово (layout_audit.json). Эффект связан с численной чувствительностью нового порядка кодирования; повтор source-обучения воспроизвёл исходные модели.

c3-MolFormer и ChemFM повторы совпали с архивными общими предсказаниями точно. Для ChemBERTa, MolFormer MLP и context-панели переход Mac/Torch 2.4.1 → Linux/Torch 2.14 дал разные losses/предсказания при совпадающих initial state и training IDs. Это перенос между окружениями, не точное воспроизведение. Некоторые Ridge результаты крайне нестабильны; причина не локализована полностью. Архивные цифры от этого не становятся выдуманными.

## Фигура

new_decoder_error_violins.pdf: абсолютные ошибки по endpoint наблюдениям, медиана и IQR; 105 QAC и 17 OOD молекул. Наблюдения четырёх задач у одной молекулы зависимы. Диапазон оси включает все ошибки.

Ключи/API вызовы OpenRouter на сервер не переносились. Все исходные архивы оставлены без изменения.
