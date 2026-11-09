# Версия v17: исходный Intro, расширенный SI и мягкое оформление

Основной документ: `../../2026_10_13_Paper_2_edited-v17_original_intro_and_expanded_SI.docx`.

Расширенный авторский SI: `Supplementary_Information_v17.docx`.

HTML с рисунками: `manuscript_v17.html` и `Supplementary_Information_v17.html`.

Сравнение Aptos / Segoe UI: `font_previews/compare.html`. PDF и PNG обоих вариантов лежат рядом. Использованы локальные ресурсы Microsoft Office; файлы шрифтов не входят в пакет. В PDF шрифты встроены для печати и просмотра.

Все новые статистические графики: `figures/` в PDF, PNG и SVG. По итогам реального визуального ревью выбран Aptos; 23 воспроизводимых графика перерисованы в мягкой палитре. Основной текст содержит 5 рисунков и 6 таблиц, SI — 29 рисунков и 34 исходных табличных объекта.

`sources/` хранит неизменённую копию выбранного `/Users/egorilin/Downloads/Supporting_Info.docx`, его четыре оригинальных PNG, их hashes и извлечённый исходный v5 Intro. Исторические raster diagrams сохранены; новые структуры используют ACS 1996.

`ARTICLE_BY_PARAGRAPHS_RU.md` — короткий пересказ каждого из 52 содержательных абзацев. `INTRO_AND_SI_CHANGES_RU.md` объясняет восстановленную логику вступления и перенос материала в SI. `relocation_manifest.json` задаёт точную карту рисунков, таблиц и новой основной библиографии. Табличная нумерация архивного SI сохранена, включая прежний пропуск caption S10; новые captions эту последовательность не переопределяют.

`reviews/` содержит задания, ответы Kimi/Claude, hashes переданных PNG, image-tool calls и ответ на замечания. Оба запускались на Mac, с инструментами только для чтения изображений; каждый открыл все 11 переданных PNG. Финальные мелкие правки после ревью документированы в `reviews/REVIEW_RESPONSE.md`.

`document_validation.json` проверяет XML и связи DOCX, неизменность source files, всех четырёх авторских PNG, numerical tables, полей H1–H7/C1, химических методов и полных реестров 105/17 соединений. Для двух prediction routes повторно проверены значения новой основной Table 5 и все plotted distributions из сохранённых predictions. Новые модели при этой редактуре не обучались.

Сборка: Python из `/opt/anaconda3/envs/COMA/bin/python`, последовательно `make_soft_figures.py`, `build_revision.py`, `write_walkthrough.py`, `validate_revision.py`. Segoe UI используется из локального временного plotting cache, автоматически создаваемого из установленного Office WOFF через fontTools; этот шрифт не нужен для основной Aptos-версии.
