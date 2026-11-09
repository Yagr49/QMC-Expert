Figure 3 перерисована в классическом вертикальном формате: пять маршрутов по X, средняя абсолютная ошибка трёх запусков по Y. Cation и scaffold holdout остаются двумя отдельными панелями. Формат180×92мм, Aptos, прежняя пастельная палитра, короткие прямые labels с переносами; белая точка—медиана, вертикальная полоска—IQR. Все хвосты сохранены на общей линейной оси0–8.05.

Изменена только ориентация и расположение графических объектов. Все420 endpoint summaries на route/панель и численныеmean/sampleSD RMSE сохранены изv23 до1e−14. Meanabsoluteerror рассчитан внутри трёх seed для каждого molecule×endpoint, не какошибка ансамбля и не KDE трёх RMSE. Новыхmodel fits не было. MainFigure3 иcaption не содержатOOD.

Основные файлы: `figures/figure3_backbone_route_error_violins.pdf`, `.svg`, `.png`(600dpi); `figure3_caption_EN.txt`/`RU.txt`, `figure3_FT_manifest.json`, `figure3_validation.json`. Humanroutes вэтойFigure3 являются partial-backbone follow-ups, не внешним компактнымv5MLP.

Вертикальная singlepanelOOD подготовлена отдельно: `figures/figure_OOD_routes_for_section2_3.*`,110×92мм,67exact endpoint summaries наroute, boundIT505 сохранён отдельно. Она не вставлена агентом вDOCX и предназначена для будущего§2.3.

Фактический Claude Sonnet4.6 наMac сначала предложил layout human-vs-quantitative Figure4. Его идеи переданыKimi-agent, а ошибочный Yrange изRMSE отклонён. ДляFigure4 используется общий decodingrecipe с независимымиCatBoostfit, необщиеобученныевеса. ИсторическийfullquantTable2checkpoint не восстановлен; matched681/noSMOTE follow-up указан отдельно.

Фактический Claude завершил visual audits Figures3–4 и финальных600dpi Figures4–5 вместе с §2.2. Figure3 принята без правок, Figure4 label/freeze исправлены; технические подробности и отклонённые ошибочные замечания разобраны в reviews/CLAUDE_FINAL_RESPONSE.md. Invocationлоги находятся вreviews. DOCX/SI/§2.2 редактируетroot, агент этихфайлов не меняет.
