# Реализация замечаний фактического Kimi

Внешний Kimi через локальный CLI завершил визуальный аудит первоначального
Figure 4: 149.7 с, четыре вызова ReadMediaFile. SHA просмотренной версии
зафиксирован в kimi_figure4_process.json. Финальные изменения после этого
аудита перечислены ниже; финальная версия передана фактическому Claude для
отдельного визуального аудита. Kimi повторно финальную версию не рецензировал.

- Source-count 681 перенесён к обучению compact encoders. На входе frozen
  MolFormer теперь явно показаны 105 target QAC; source/target не сливаются.
- Уточнено Separate CatBoost fits и Same target protocol: представления
  не конкатенируются, общих обученных весов decoder нет. В caption явно
  указан отдельный fit каждой arm/seed/target-training fold.
- Raw оставлен как фиксированная reference с более светлой заливкой;
  все 420 endpoint-errors сохранены. Остальные arms имеют равные параметры
  насыщенности и ширины, без подчёркивания преимущества human.
- Медианные горизонтальные черты и вертикальные IQR стали тоньше/короче.
  Интерпретация этих элементов сохранена в caption.
- Обе панели имеют одинаковые y-limits от 0 до фактического максимума с
  небольшим запасом. Все длинные хвосты до примерно 7 сохранены; OOD нет.
- Caption сокращён до 128 слов, с обычными пробелами и без бюджетов внутри
  диаграммы. Полная версия и source-SHA/derived-data доступны рядом.

Замечание «raw выглядит пятой рукой» понимаем как указание на fixed-reference,
а не число arms: фактически показаны четыре (Human, Quantitative, Shuffled
human, Raw). Крест медиана/IQR соответствует выбранному автором классическому
вертикальному violin-стилю и не заменён статистической uncertainty-bar.

Для всех четырёх arms выбран одинаковый native categorical task code.
Shuffled-human text-code predictions отсутствуют, поэтому смешивать его
categorical decoder с human/quantitative text decoder было бы некорректно.
Новые matched 681 source/no-SMOTE controls не выдаются за историческую
полную quantitative Table 2 модель; её checkpoint пока не найден.

Optional Figure 5 использует другую, явно указанную архитектуру: matched
partial-MolFormer source adaptation и target CatBoost classification на 405
Q-HERO молекулах. Показано среднее individual ROC по пяти seeds, не ROC
ансамблевого среднего вероятностей. Shade — sample SD, не доверительный
интервал. Raw/RF имеют один фиксированный seed, без искусственного SD.
