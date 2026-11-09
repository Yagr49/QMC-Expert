# Что изменено в v17

Вход восстановлен по логике вашего `2026_07_09_Paper_2_edited-v5_NF_3.docx`: AMR → поиск антимикробных соединений → ограничения измерений и ML → человеческое знание → контролируемая проверка на QAC. Fine-tuning появляется после постановки задачи, как отдельный вопрос о способе адаптации. Текст различает источник supervision, представление молекулы и target predictor.

Из исходного Intro использованы мотивация и ход мысли. Исторические числа WHO, заявления о гарантированном денойзинге экспертами, фиксированной замене измерений метками и биологической каузальности не перенесены как установленные результаты. Современный fine-tuning протестирован; при нашем бюджете full fine-tuning лучше LoRA в cation-CV, поэтому утверждения об универсальном преимуществе маленьких адаптеров нет.

Ваш `/Users/egorilin/Downloads/Supporting_Info.docx` включён в расширенный SI. Его четыре исходные PNG сохранены побитово как Figures S1–S4. Они относятся к историческим classification/embedding экспериментам; captions явно отличают их от новых matched MIC/MBC regression и weight interventions. Ошибки отображения стрелок в историческом footer не исправлялись рисованием поверх исходных данных.

Основная статья содержит 5 рисунков и 6 таблиц. Расширенный SI содержит 29 рисунков и 34 таблицы, включая исходные табличные объекты. Из основного текста перенесены подробности task encoding, graph/tabular decoders, full direct-adaptation comparison и reproduction history. Полные numerical tables уже были в SI и сохранены без дублирования; Section S28 объединяет перенесённое обсуждение и методы.

| Объект v16 | Место в v17 |
|---|---|
| Figure 3, task encoding | Figure S27 |
| Figure 6, decoder error violins | Figure S28 |
| Figure 7, direct adaptation | Figure S29 |
| Полная Table 5, graph/tabular scores | Table S23 |
| Полная Table 6, direct-target strategies | Table S28 |
| Figure S22, prediction routes | Figure S26 |
| Основные Figures 1, 2, 4, 5, 8 | Основные Figures 1–5 |
| Первые 22 supplementary figures | Figures S5–S26 |

Новая основная Table 5 коротко сравнивает оба prediction routes на одних и тех же первых трёх source checkpoints. Первичные five-source-seed Tables 2–4 сохранены. Полная таблица weight controls остаётся основной Table 6. Библиография основного текста перенумерована по первому упоминанию; исторический SI сохраняет собственную исходную библиографию, а ссылки Section S28 следуют новой основной.

Перерисованы 23 воспроизводимых графика: Aptos, лавандовые/мятные/персиковые цвета, светлая сетка, тонкие линии, короткие labels. Статистика, численность, зависимость endpoints и censoring остаются в captions и таблицах. Структуры используют геометрию RDKit ACS 1996. Старые source docs, предсказания, метрики и поля H1–H7/C1 сохранены.

Одинаковые виолины доступны в `font_previews/Aptos` и `font_previews/Segoe_UI`. Оба действительных внешних рецензента, Kimi и Claude, выбрали Aptos после чтения изображений; задания выполнялись только на Mac. Протоколы и responses находятся в `reviews/`. Шрифтовые файлы не распространяются с пакетом.

Полный короткий пересказ каждого из 52 содержательных абзацев — `ARTICLE_BY_PARAGRAPHS_RU.md`. Проверка целостности DOCX, исходных PNG, numerical tables, реестров 105/17 соединений и plotted distributions — `document_validation.json`.
