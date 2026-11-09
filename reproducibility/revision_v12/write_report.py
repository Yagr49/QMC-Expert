"""Russian evidence summary, populated only from completed audited outcomes."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parent

def main():
    validation=json.loads((ROOT/'validation.json').read_text());assert validation['completed']
    s=pd.read_csv(ROOT/'analysis/summary.csv').query("target == 'Q-HERO-405'").set_index('arm')
    c=pd.read_csv(ROOT/'analysis/contrasts.csv').query("target == 'Q-HERO-405' and unit == 'seed+scaffold'").set_index('comparison')
    d=pd.read_csv(ROOT/'analysis/direct_summary.csv').query("target == 'Q-HERO-405'").set_index('arm')
    rank=pd.read_csv(ROOT/'analysis/direct_contrasts.csv').query("target == 'Q-HERO-405'").set_index('comparison')
    def interval(frame,key,field='delta_RMSE'):
        r=frame.loc[key];return f'{r[field]:+.3f} [{r.ci_low:+.3f}; {r.ci_high:+.3f}]'
    lines=['# Результат matched partial fine-tuning','',
           'Эксперимент выполнен, а не только запланирован. Источник: одни и те же 681 молекула; 377 train / 304 validation; 52 положительные train-метки у человека и бинарного MIC. Верхние восемь слоёв MolFormer, pooler и скалярная голова обучаются; нижние четыре слоя и embeddings заморожены. 28 375 297 обучаемых параметров; пять парных seeds, шесть arms, 30 эпох / 360 обновлений каждого arm. Validation диагностическая, используется конечный checkpoint. Строго исключены все target-катионы.','',
           '## Q-HERO-405: общий CatBoost на фиксированных scaffold-fold','',
           '| Разметка | RMSE, log2 µM | R² | Прямое ранжирование ρ |','|---|---:|---:|---:|']
    for arm,label in [('raw-molformer','Исходный MolFormer'),('expert','Человеческая'),('quant-continuous','Непрерывный MIC'),('quant-binary','Бинарный MIC'),('expert-shuffled','Перемешанная человеческая'),('quant-shuffled','Перемешанный MIC'),('quant-binary-shuffled','Перемешанный бинарный MIC')]:
        r=s.loc[arm];direct='—' if arm=='raw-molformer' else f"{d.loc[arm].rank_agreement:.3f} ± {d.loc[arm].rank_sd:.3f}"
        value=f'{r.RMSE:.3f}' if arm=='raw-molformer' else f'{r.RMSE:.3f} ± {r.RMSE_sd:.3f}'
        lines.append(f'| {label} | {value} | {r.R2:.3f} | {direct} |')
    lines+=['','± обозначает SD между пятью обучениями, а не доверительный интервал. Прямое ранжирование сохраняет исходную голову и не обучается на MIC Q-HERO.','',
            '## Парные эффекты','',
            f"- Human − shuffled human ΔRMSE: **{interval(c,'expert minus expert-shuffled')}**.",
            f"- Human − raw ΔRMSE: **{interval(c,'expert minus raw-molformer')}**.",
            f"- Human − continuous MIC ΔRMSE: **{interval(c,'expert minus quant-continuous')}**.",
            f"- Human − binary MIC ΔRMSE: **{interval(c,'expert minus quant-binary')}**.",
            f"- Human − shuffled human Δρ: **{interval(rank,'expert minus expert-shuffled','delta_rank')}**.",'',
            'Интервалы: 10 000 парных bootstrap по seeds и целым scaffold-группам, фиксированные target-fold; exploratory, без поправки на множественные сравнения. Отрицательный ΔRMSE выгоден первому arm, положительный Δρ выгоден первому arm. Каузальность относится к замене разметки внутри зафиксированного алгоритма. Пять перемешиваний не являются полноценным permutation significance test. Эквивалентность, замена измерений и биологический механизм не установлены.','',
            '## Воспроизводимость','',
            f"Пересчитаны {validation['recomputed_metric_rows']} downstream-метрик и {validation['recomputed_direct_metric_rows']} прямых метрик; {validation['prediction_rows']} + {validation['direct_prediction_rows']} строк предсказаний. Проверены одинаковые initial weights, порядок batches, число updates, исходные идентичности и отсутствие source-target cation overlap. Все 30 реконструированных чекпойнтов воспроизводят признаки и прямые головы; максимальное расхождение признаков {validation['max_reconstructed_feature_difference']:.3g}, прямых scores {validation['max_reconstructed_score_difference']:.3g}.",'',
            'MolFormer обновляет случайные feature-map buffers во время training даже при deterministic_eval=True. Их восстановление и сохранение описаны в PROTOCOL_IMPLEMENTATION_NOTE.md; первоначальные файлы и hashes сохранены. Полные восстановительные чекпойнты лежат на первом сервере в coma_revision_v12_20261011/results/reproducible_checkpoints, индекс — analysis/checkpoint_reconstruction.csv. Для загрузки нужны pinned base checkpoint + trained parameters + final buffers.','',
            '## Файлы статьи','',
            '- ../../2026_10_11_Paper_2_edited-v12_matched_finetuning.docx — основной текст с новой секцией 3.6, таблицей 4 и Figure 5.',
            '- Supplementary_Information_v12.docx — полные исходы, интервалы, learning curves и новые matched-виолины.',
            '- figures/figure5_matched_finetuning.pdf — главное matched-сравнение.',
            '- figures/figureS18_matched_finetuning_error_violins.pdf — matched-виолины ошибок.',
            '- ../revision_v11/Human_annotation_methods_for_coauthors.docx — форма для соавторов; H1–H7 сохранены в новой статье.',
            '- BASELINES_NEXT_RU.md — приоритетный план Chemprop/CheMeleon, TabPFN, TabFM и AutoGluon; он не выдаётся за выполненные эксперименты.','',
            'Тезис «fine-tuning плох и нужны только маленькие адаптеры» не заявляется. Нынешняя малая MLP — проекция frozen-признаков, а не LoRA; сравнение с partial fine-tuning меняет также архитектуру, график оптимизации и среду. Происхождение человеческих меток, доступная аннотаторам информация и первичная химическая SI остаются полями для соавторов.']
    (ROOT/'README_RU.md').write_text('\n'.join(lines)+'\n')
    print(ROOT/'README_RU.md')

if __name__=='__main__':main()
