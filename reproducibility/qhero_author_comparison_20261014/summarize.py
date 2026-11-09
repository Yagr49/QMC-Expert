"""Recompute classification scores and describe the scope of the comparisons."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path(__file__).resolve().parent


def main():
    out = ROOT / 'results'
    done = json.loads((out/'completion.json').read_text())
    assert done['completed'] and done['configurations'] == 18
    metrics = pd.read_csv(out/'metrics.csv')
    pred = pd.read_csv(out/'predictions.csv')
    target = pd.read_csv(ROOT/'data'/'target.csv')
    expected = target.sa_mic_um.le(8).astype(int)
    assert len(metrics) == 156 and len(pred) == 10692
    checked = 0
    for key, group in pred.groupby(['model','seed','protocol','fold']):
        assert group.row_index.is_unique
        i = group.row_index.to_numpy()
        assert np.array_equal(group.label.values, expected.iloc[i].values)
        assert np.array_equal(group.can.values, target.can.iloc[i].values)
        row = metrics[(metrics.model==key[0]) & (metrics.seed==key[1]) &
                      (metrics.protocol==key[2]) & (metrics.fold==key[3])].iloc[0]
        assert abs(roc_auc_score(group.label,group.probability)-row.AUROC)<1e-12
        assert abs(average_precision_score(group.label,group.probability)-row.AUPRC)<1e-12
        checked += 1
    for key, group in pred[pred.protocol.eq('scaffold_CV_fold')].groupby(['model','seed']):
        assert len(group)==405 and group.row_index.is_unique
        row=metrics[(metrics.model==key[0]) & (metrics.seed==key[1]) &
                    metrics.protocol.eq('scaffold_CV_pooled')].iloc[0]
        assert abs(roc_auc_score(group.label,group.probability)-row.AUROC)<1e-12
        assert abs(average_precision_score(group.label,group.probability)-row.AUPRC)<1e-12
        checked += 1
    rows=[]
    for protocol in ('random_heldout20','scaffold_CV_pooled','inner_random_CV_train80'):
        for model,group in metrics[metrics.protocol.eq(protocol)].groupby('model'):
            rows.append(dict(model=model,protocol=protocol,
                             uncertainty='fold SD ddof0' if protocol.startswith('inner') else
                             ('paired source/decoder seed SD ddof1' if len(group)>1 else 'single fixed fit'),
                             repeats=len(group),
                             AUROC=float(group.AUROC.mean()),
                             AUROC_SD=float(group.AUROC.std(ddof=0 if protocol.startswith('inner') else 1)) if len(group)>1 else None,
                             AUPRC=float(group.AUPRC.mean()),
                             AUPRC_SD=float(group.AUPRC.std(ddof=0 if protocol.startswith('inner') else 1)) if len(group)>1 else None))
    summary=pd.DataFrame(rows)
    summary.to_csv(out/'summary.csv',index=False)
    print(summary.to_string(index=False,float_format=lambda x:'%.4f'%x))

    # Paired, class-stratified test bootstrap. These are conditional intervals:
    # fitted models and test class counts stay fixed; target training is not refit.
    held=pred[pred.protocol.eq('random_heldout20')]
    rf=held[held.model.eq('RF_35_descriptors')].sort_values('row_index')
    index=rf.row_index.values
    labels=rf.label.to_numpy()
    rf_p=rf.probability.to_numpy()
    positive=np.flatnonzero(labels==1); negative=np.flatnonzero(labels==0)
    rng=np.random.RandomState(20261014)
    boot=[np.concatenate([rng.choice(positive,len(positive),replace=True),
                          rng.choice(negative,len(negative),replace=True)])
          for _ in range(2000)]
    contrasts=[]
    for name in ('CB_raw_MolFormer','CB_human','CB_shuffled_human','CB_quantitative'):
        frame=held[held.model.eq(name)].pivot(index='row_index',columns='seed',values='probability').loc[index]
        ps=frame.to_numpy().T
        for metric_name,fn in [('AUROC',roc_auc_score),('AUPRC',average_precision_score)]:
            point=np.mean([fn(labels,p) for p in ps])-fn(labels,rf_p)
            values=[]
            for idx in boot:
                sampled=rng.randint(len(ps),size=len(ps))
                values.append(np.mean([fn(labels[idx],ps[s][idx]) for s in sampled])-fn(labels[idx],rf_p[idx]))
            low,high=np.percentile(values,[2.5,97.5])
            contrasts.append(dict(model=name,reference='RF_35_descriptors',
                                  metric=metric_name,difference=float(point),
                                  ci_low=float(low),ci_high=float(high),
                                  bootstrap_repeats=len(boot),
                                  unit='paired source/decoder seed + class-stratified test molecules; conditional'))
    pd.DataFrame(contrasts).to_csv(out/'paired_test_contrasts.csv',index=False)
    validation=dict(completed=True,metric_rows=checked,prediction_rows=len(pred),
                    target_molecules=405,test_molecules=81,test_positives=72,
                    test_negatives=9,source_target_cation_overlap=0,
                    published_421_row_scores_are_not_a_paired_405_row_comparison=True,
                    manuscript_or_SI_updated=False)
    (out/'validation.json').write_text(json.dumps(validation,indent=2))
    public=json.loads((out/'public_RF_reproduction.json').read_text())
    def table(protocol):
        lines=['| Модель | AUROC | AUPRC |','|---|---:|---:|']
        for row in summary[summary.protocol.eq(protocol)].itertuples():
            au='%.4f'%row.AUROC
            ap='%.4f'%row.AUPRC
            if row.repeats>1:
                au+=' ± %.4f'%row.AUROC_SD
                ap+=' ± %.4f'%row.AUPRC_SD
            lines.append('| %s | %s | %s |'%(row.model,au,ap))
        return '\n'.join(lines)
    report=[
        '# Сравнение с авторами Q-HERO, 14 октября 2026',
        '',
        'Это самостоятельный расчёт, статья v20 и SI не менялись. Tiihonen COE — другой датасет.',
        '',
        'Опубликованный Q-HERO RF: CV AUROC 0.8036 ± 0.0552, AUPRC 0.9672 ± 0.0079; '
        'отложенный тест AUROC 0.5592, AUPRC 0.9121. Источник: '
        'https://doi.org/10.1021/acs.jcim.6c00390. Код: https://github.com/pb0316/Q-HERO.',
        '',
        '## Воспроизведение открытого кода на авторских 421 строках',
        '',
        'На сервере sklearn %s: CV AUROC %.4f, AUPRC %.4f; test AUROC %.4f, AUPRC %.4f. '
        'Это не совпадает с опубликованными значениями. Полная конфигурация и версии сохранены.'%
        (done['sklearn'],public['cv_mean']['AUROC'],public['cv_mean']['AUPRC'],
         public['heldout20']['AUROC'],public['heldout20']['AUPRC']),
        '',
        'Рабочая книга содержит исходные MIC в µM. Порог 8 применяется корректно; '
        'предварительное предположение об ошибке log2 не подтвердилось. '
        '375/421 исходных строк активны; высокая AUPRC требует сравнения с долей положительного класса.',
        '',
        '## Общий очищенный набор: 405 молекул',
        '',
        'Классификация S. aureus MIC ≤ 8 µM. Удалены дубли и шесть групп с конфликтующими MIC. '
        '360/405 активны. Внешняя source-панель содержит 681 молекулу; '
        'пересечений с target по полным солям и катионам нет. '
        'Использованы сохранённые matched partial-fine-tuning представления v12, '
        'а не компактный исторический адаптер v5. '
        'CatBoostClassifier800/depth6/lr0.05; выбор по target-test не проводится.',
        '',
        '### Случайный тест 80/20, стратифицированный, seed0',
        '',
        '324 train/81 test. В test 72 активных и 9 неактивных. '
        'Дедупликация полных солей исключает повтор одной соли, но один катион встречается '
        'и в train, и в test с разными противоионами. '
        'Далее отдельная scaffold-проверка разделяет эти соединения.',
        '', table('random_heldout20'), '',
        '### Пятифолдовая scaffold-CV: объединённые OOF-предсказания',
        '', table('scaffold_CV_pooled'), '',
        '± — выборочное SD пяти полных запусков, где сопряжены seed внешнего '
        'fine-tuning и seed CatBoost. RF и исходные фиксированные представления имеют '
        'один заранее заданный seed0; их SD не оценивалась. '
        'Стандартное отклонение пяти внутренних CV-фолдов сохранено отдельно в summary.csv.',
        '',
        'Нельзя вычитать наши 405-row метрики из опубликованного 421-row теста и объявлять '
        'парную победу: состав и тестовые молекулы различаются. Корректное парное сравнение '
        'здесь — с RF35, заново обученным на тех же 405 молекулах и разбиениях. '
        'Новый классификационный decoder не сопоставляется напрямую с прежними R²/RMSE регрессии.',
        '',
        'paired_test_contrasts.csv содержит условные 95% bootstrap-интервалы разностей '
        'на 81 тестовой молекуле: ресэмплируются сопряжённые seed и молекулы внутри классов; '
        'target-обучение не повторяется. Это не биологическая каузальность и не доказательство эквивалентности.',
        '',
        'Проверены все 156 строк метрик и 10692 предсказания. Исходные файлы, SHA, '
        'скрипты и версии сохранены в этой папке и на сервере. '
        'Время первоначального запуска и изменение числа процессов сохранены в rescale.json.',
    ]
    (ROOT/'README_RU.md').write_text('\n'.join(report)+'\n')
    print(json.dumps(validation))


if __name__=='__main__':
    main()
