# Версия v16: сначала predictive performance, затем интервенции

Основная статья: `/Users/egorilin/Desktop/COMA/2026_10_12_Paper_2_edited-v16_finetuning_and_weight_interventions.docx`.

Supplement: `Supplementary_Information_v16.docx`. Читаемые версии: `manuscript_v16_readable.md`, `manuscript_v16.html`, `supplement_v16_readable.md`, `Supplementary_Information_v16.html`.

Добавлены оба запрошенных способа предсказания: прямой backbone + четырёхвыходная head и fine-tuned представление + общий CatBoost decoder. Новая Table 6 включает frozen linear/MLP, настоящий query/value LoRA, partial/full fine-tuning и все real/shuffled source-initialisations. Всего 363 прямых fit, три paired seeds, прежние cation/scaffold folds и все 17 OOD соединений.

Для проверки усвоенного сигнала выполнены 1,331 дополнительных fit: веса outer LayerNorm, верхних восьми блоков либо всех encoder parameters возвращаются к pretrained, служебные feature-map buffers сохраняются, decoder каждый раз обучается заново. Table 7 и Figure 8 отделяют вклад обученных весов от вычислительного состояния. Результат касается prediction pipeline; независимое человеческое знание зависит от ещё не заполненного протокола разметки.

Новая Table S33 раскрывает расчёт censored-endpoint sensitivity по каждому из пяти seeds: pooled lower bound 2.100536 → 2.101 и Ec_MBC 2.355897 → 2.356. Параметры scalar source head и четырёхвыходной target head явно разведены. Основные повторяющиеся real-versus-shuffled интервалы сохраняют прежние 10,000 draws; новые weight-контроли используют 5,000, что указано в caption.

Сначала, в S23, проверены опубликованные метрики MoLFormer, ChemBERTa-3/c3 и ChemFM по первичным источникам. Они приводятся с dataset/split/uncertainty context и не смешиваются с нашими концентрациями.

Новые графики в `figures/`:

- `figure7_direct_adaptation.pdf` — predictive performance пяти способов адаптации;
- `figure8_weight_rewind.pdf` — изменения ошибки после вмешательства в веса;
- `figureS22_prediction_route_violins.pdf` — split-виолины двух prediction routes.

Основные выводы: LoRA при данном бюджете не лучше full fine-tuning в cation CV; человеческая source-разметка конкурентоспособна с численными источниками и имеет полезный вклад, но не выигрывает во всех режимах. Возврат всех human-guided encoder weights увеличивает cation-CV ошибку на 0.109 [0.037, 0.201]; для scaffold/OOD интервалы содержат ноль. Более сильные утверждения о семантическом или биологическом знании не следуют из теста.

Все исходные 105 молекул, 17 OOD, bound IT505 Ec_MBC >500 mg/L, пять прежних основных таблиц, молекулярные рисунки и места H1–H7/C1 сохранены. Исправлены описание pooler (mean pooling без обучаемых параметров) и второй автор ChemFM (K. Zacour).

`document_validation.json` подтверждает сохранение документов и независимый пересчёт 2,310 строк метрик из 139,832 предсказаний. Все 93 intact/raw prediction sets воспроизводят v14, а все 33 сохранённые final-OOD модели проходят повторную загрузку. Большие checkpoints остаются на разрешённом сервере; локально — результаты, код, hashes и журналы. OpenRouter на сервере не использовался.

Выполнены реальные внешние рецензии Kimi Code и Claude Sonnet 4.6 с локального Mac. Замечания, поправки и проверка спорных арифметических утверждений находятся в `reviews/REVIEW_RESPONSE.md`; это модельная критика, не человеческое peer review. После рецензий вычислительные результаты не менялись.

Повтор сборки:

```sh
/opt/anaconda3/envs/COMA/bin/python reproducibility/revision_v16/build_revision.py
/opt/anaconda3/envs/COMA/bin/python reproducibility/revision_v16/validate_revision.py
```
