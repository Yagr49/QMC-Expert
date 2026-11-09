Основная Figure 3 переработана для §2.1: только cation и scaffold holdout. Пять routes сохранены; две панели имеют одинаковые линейные оси и содержат по 420 средних абсолютных ошибок молекула×endpoint для каждого route. Усреднение выполняется внутри трёх запусков 0–2; ошибки ансамбля и KDE по трём RMSE не используются. Медианы, IQR и все хвосты сохранены. Рисунок: 180×88 мм, Aptos, пастельная палитра, PDF/SVG и PNG600dpi.

Файлы основной Figure 3 находятся в `figures/figure3_backbone_route_error_violins.*`; подпись для документа — `figure3_caption_EN.txt` (123 слова). В ней нет OOD, 67, bound или описания OOD-точек. Средние RMSE и sample SD по трём полным запускам сохранены отдельно в `analysis/FT_route_grouped_RMSE_mean_sample_SD.csv`.

Проверка source-preservation: все 4200 endpoint summaries основной Figure 3 и все mean/SD совпадают с v22 до 1e−14. Хеши source-скрипта, source-PNG и prediction CSV, число наблюдений, размер PDF и Aptos записаны в `figure3_FT_manifest.json` и `figure3_validation.json`. Новых fit не было.

Human direct и Human → CB — отдельные partial-backbone follow-up модели, не компактный внешний v5 MLP. Они начинают с одинаковых source checkpoints, но direct route затем адаптируется под target, а CB route замораживает source features. Вид плотностей не доказывает значимость, универсальное преимущество малого адаптера или причинную роль смысла человеческих меток.

Отдельно подготовлен `figures/figure_OOD_routes_for_section2_3.*`: одна панель, 105×88 мм, 67 точных endpoint summaries на route, те же стили и статистик. Bound IT505/E. coli MBC >500 mg/L остаётся отдельной записью. Подпись — `figure_OOD_caption_EN.txt`; provenance — `figure_OOD_manifest.json`. Этот файл подготовлен для будущего обсуждения §2.3 и агентом не вставлен в DOCX.

Фактический Claude Sonnet4.6 CLI на Mac проверил source PNG, новый двухпанельный PNG, отдельный OOD PNG и скрипт/подписи. Журнал и вывод — `reviews/claude_grouped_*`. Агент не редактирует основной DOCX или SI.
