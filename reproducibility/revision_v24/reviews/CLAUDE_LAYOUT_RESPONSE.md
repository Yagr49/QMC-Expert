Фактический Claude Sonnet4.6 на Mac предложил Figure 4: компактная top-схема двух source arms и bottom vertical Cation/Scaffold violins, мягкие цвета, прямые короткие labels, без чисел performance в схеме. Его текст сохранён целиком; Kimi-agent получил его для реализации.

Приняты: два внешних compact encoders, Frozen MolFormer, общий количественный decoding recipe, понятный конец source guidance, реальные paired-seed endpoint errors и видимый shuffled control. No SMOTE / matched681 follow-up явно отделены от не найденного historical full-quant checkpoint.

Исправлены ошибки предложения:

- Диапазон Y1.5–2.6 был выдуман из RMSE вместо распределения endpoint errors; его не используем, хвосты сохраняем целиком.
- Same decoder означает одинаковый протокол независимых fit, не общий экземпляр обученных весов и не слияние embeddings.
- Нуль human-vs-shuffle не выводим из формы KDE и не называем формальной эквивалентностью.
- Flame/Σ icons и hyperparameters внутри схемы не нужны.

Агент Figure 4 дополнительно уведомлён: следует явно показать, что source-trained encoders применяются к 105 target structures, а CatBoost обучается только на их train folds независимо для каждой representation. Это не zero-shot decoder trained on681 source.
