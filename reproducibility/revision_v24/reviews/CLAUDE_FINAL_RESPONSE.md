# Ответ на фактические Claude layout и visual audits

Claude Sonnet4.6 реально выполнялся через локальный Mac CLI:

- Layout proposal:31.2s, supplied-text review; `claude_layout_review.txt`/`process.json`. Идея схемы передана Kimi-agent.
- Figures3–4 audit:93.1s,8 Read calls, включая обе PNG; `claude_vertical_review.txt`/`process.json`.
- Final600dpi Figures4–5 + §2.2 audit:97.7s,7 Read calls, включая обе final PNG, обе подписи, provenance и `SECTION_2_2_EN.md`; `claude_final_roc_review.txt`/`process.json`.

Приняты и проверены:

- Оба violin-графика вертикальные, прямые короткие labels, общие линейные оси и все фактические хвосты. Figure3 полностью приемлема без правок;420 endpoint summaries/route/panel и three-run sample statistics сохранены.
- Source-guided compact Figure4 явно отделена от partial-backbone Figure3/Q-HERO. Frozen source encoders затем применяются к105 target structures; CatBoost refit независим поrepresentation/seed/trainfold. В итоговой схеме показаны target inputs, separate fits и held-out predictions.
- Figure4 Ylabel уточнён до **Mean absolute error**; подпись прямо указывает, что source-encoder weights заморожены во время target-fold decoder training. Raw — один фиксированный reference, остальные arms — five source runs.
- Figure4/5 PNG подняты до600dpi; последняя actualClaude проверка подтвердила эти финальные версии. Предыдущее замечание о360dpi относится к более раннему снимку.
- Figure5 построена из настоящих individual ROC и их pointwise mean; shading — sampleSD, неCI, не ensemble probabilities. RF35 dashed, сырые иRFreference фиксированы seed0. 405 cleaned targets, scaffold иrandom протоколы разделены; historical421row score не назван парной победой.
- §2.2 различает historical holdout R², reconstructed row-CV foldSD, three-/five-run seedSD и conditional scaffold bootstrap; root предоставляет полные contrasts вSI.

Ошибочные/чрезмерные требования итогового обзора не принимаются автоматически:

1. **Разные H−RF интервалы не противоречат друг другу.** Scaffold Human−RF: **+0.1104 [0.0262,0.2012]**; Random Human−RF: **+0.1052 [−0.0664,0.2969]**. Первый и второй относятся к разным evaluation protocols. Никакого исправления данных не требуется.
2. Обязательства перечислять каждый вычисленный CI вmain нет; полная таблицаSI предотвращает потерю информации. Root может добавить короткую корректную фразу Human−RF/scaffold иуказать, что random interval включаетноль. Это полезное уточнение, не устранение «противоречия».
3. **RF local dips below chance line не доказывают scaffold imbalance.** Понижение отдельных участков ROC — реальное эмпирическое свойство при AUROC0.565; причина не установлена. Не добавляем выдуманный causal explanation или лишний performancebox в рисунок. AUROC ужедан вmain/SI.
4. Figure4 optional tinylabel **“Source-trained, then frozen”** может сделать diagram ещёяснее; caption ужекорректен. Выбор этого косметического уточнения передан root. Данные и fitted models не меняются.

Новых model fits не запускалось, DOCX/SI агент не менял. Все реальные invocation logs и хеши прочитанных файлов сохранены. Если после review root добавляет одну поясняющую надпись, это следует назвать локально проверенной cosmetic change после external review, не выдавая изменённый PNG за ещёразпрочитанныйClaude.
