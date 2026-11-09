"""Independent metrics check, complete tables, paired uncertainty and figures."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error

ROOT = Path(__file__).resolve().parent
MODELS = ['catboost', 'autogluon', 'tabpfn', 'tabfm', 'chemprop']
REPS = ['rdkit', 'raw-molformer', 'expert_seed0', 'quant-continuous_seed0', 'quant-binary_seed0']


def paired_ci(a, b, group_column, repetitions=2000):
    keys = ['cohort', 'compound_id', 'task']
    d = a.merge(b, on=keys, suffixes=['_human', '_comparator'], validate='one_to_one')
    assert np.allclose(d.y_human, d.y_comparator, rtol=0, atol=1e-12)
    assert (d.qualifier_human == '=').all()
    d['human_squared_error'] = (d.prediction_human - d.y_human) ** 2
    d['comparator_squared_error'] = (d.prediction_comparator - d.y_comparator) ** 2
    blocks = d.groupby(group_column + '_human').agg(human=('human_squared_error', 'sum'),
                  comparator=('comparator_squared_error', 'sum'), n=('human_squared_error', 'size'))
    rng = np.random.default_rng(1729)
    idx = rng.integers(len(blocks), size=(repetitions, len(blocks)))
    n = blocks.n.to_numpy()[idx].sum(axis=1)
    delta = np.sqrt(blocks.human.to_numpy()[idx].sum(axis=1)/n) - np.sqrt(blocks.comparator.to_numpy()[idx].sum(axis=1)/n)
    point = np.sqrt(d.human_squared_error.mean()) - np.sqrt(d.comparator_squared_error.mean())
    return dict(delta_RMSE_human_minus_comparator=float(point), low=float(np.quantile(delta, .025)),
                high=float(np.quantile(delta, .975)), grouping=group_column, groups=len(blocks),
                n_exact=len(d), repetitions=repetitions)


def figure(tables, out):
    import os
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.plot_cache'))
    os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'sans-serif', 'font.sans-serif':['Arial','DejaVu Sans'],
        'font.size':8, 'axes.linewidth':.8, 'pdf.fonttype':42, 'ps.fonttype':42,
        'xtick.direction':'out', 'ytick.direction':'out'})
    fig, axes = plt.subplots(2, 3, figsize=(7.1, 4.7), sharey=True)
    colors = ['#858585', '#4B79A3', '#329465', '#C38239', '#A46DA0']
    labels = ['RDKit','Raw','Human','Quant.\ncontinuous','Quant.\nbinary']
    specs = [('cation','QAC105','Cation CV'),('scaffold','QAC105','Scaffold CV'),('full-QAC105','OOD17','OOD-17')]
    maximum = max(float(np.max(np.abs(tables[m].y - tables[m].prediction))) for m in ['tabpfn','tabfm'])
    for row, model in enumerate(['tabpfn','tabfm']):
        for col, (schema, cohort, title) in enumerate(specs):
            ax = axes[row, col]
            d = tables[model]
            distributions = []
            for rep in REPS:
                subset = d[(d.representation == rep) & (d.schema == schema) & (d.cohort == cohort) & (d.qualifier == '=')]
                distributions.append(np.abs(subset.y.to_numpy() - subset.prediction.to_numpy()))
            violins = ax.violinplot(distributions, positions=np.arange(5), widths=.75,
                                  showmeans=False, showmedians=False, showextrema=False)
            for body, color in zip(violins['bodies'], colors):
                body.set_facecolor(color); body.set_edgecolor(color); body.set_alpha(.38)
            for i, (values, color) in enumerate(zip(distributions, colors)):
                lo, med, hi = np.quantile(values, [.25,.5,.75])
                ax.vlines(i, lo, hi, color=color, linewidth=1.7)
                ax.plot([i-.12,i+.12],[med,med],color=color,linewidth=2.2)
            ax.set_xticks(np.arange(5)); ax.set_xticklabels(labels,rotation=35,ha='right',fontsize=7)
            ax.set_title(('TabPFN-V2' if model == 'tabpfn' else 'TabFM') + ' — ' + title)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.set_ylim(0,np.ceil(maximum+.25))
            if col == 0:ax.set_ylabel(r'Absolute error, $\log_2$(mg/L)')
            ax.text(.98,.97,'n = ' + str(len(distributions[0])),ha='right',va='top',transform=ax.transAxes,fontsize=7)
    fig.tight_layout(pad=1.1)
    fig.savefig(out/'new_decoder_error_violins.pdf',bbox_inches='tight')
    fig.savefig(out/'new_decoder_error_violins.png',dpi=300,bbox_inches='tight')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser();ap.add_argument('snapshot', type=Path);args = ap.parse_args()
    out = ROOT/'analysis';out.mkdir(exist_ok=True)
    tables = {};all_metrics=[];verified=[];fits=0
    for model in MODELS:
        directory = args.snapshot/'new_baselines'/model
        manifest=json.loads((directory/'manifest.json').read_text())
        assert manifest['completed'] and not manifest['errors']
        predictions=pd.read_csv(directory/'predictions.csv');tables[model]=predictions
        metrics=pd.read_csv(directory/'metrics.csv');metrics['model']=model
        for row in metrics.itertuples():
            subset=predictions[(predictions.representation==row.representation)&(predictions.seed==row.seed)&
                     (predictions.schema==row.schema)&(predictions.cohort==row.cohort)&(predictions.qualifier=='=')]
            if row.task!='pooled':subset=subset[subset.task==row.task]
            assert len(subset)==row.n
            assert np.isclose(np.sqrt(np.mean((subset.y-subset.prediction)**2)),row.RMSE,rtol=0,atol=1e-12)
            assert np.isclose(r2_score(subset.y,subset.prediction),row.R2,rtol=0,atol=1e-12)
            assert np.isclose(mean_absolute_error(subset.y,subset.prediction),row.MAE,rtol=0,atol=1e-12)
        fits+=manifest['fits'];all_metrics.append(metrics)
        verified.append(dict(model=model,prediction_rows=len(predictions),verified_metric_rows=len(metrics),fits=manifest['fits']))
    pd.concat(all_metrics,ignore_index=True).to_csv(out/'all_model_metrics.csv',index=False)
    pooled=pd.concat(all_metrics,ignore_index=True);pooled=pooled[pooled.task=='pooled']
    summary=pooled.groupby(['model','representation','schema','cohort']).agg(RMSE=('RMSE','mean'),
                         R2=('R2','mean'),runs=('seed','nunique'),n_exact=('n','first')).reset_index()
    summary.to_csv(out/'comparison_pooled.csv',index=False)
    pivot=summary.pivot(index=['model','representation'],columns='schema',values='RMSE').reset_index()
    pivot.to_csv(out/'comparison_rmse.csv',index=False)
    ci=[]
    for model in MODELS[:-1]:
        d=tables[model];d=d[d.qualifier=='=']
        for schema in ['cation','scaffold','full-QAC105']:
            human=d[(d.representation=='expert_seed0')&(d.schema==schema)]
            for rep in [r for r in REPS if r!='expert_seed0']:
                comparator=d[(d.representation==rep)&(d.schema==schema)]
                for grouping in (['cation','scaffold'] if schema=='full-QAC105' else ['cation' if schema=='cation' else 'scaffold']):
                    ci.append(dict(model=model,schema=schema,comparator=rep,**paired_ci(human,comparator,grouping)))
    pd.DataFrame(ci).to_csv(out/'paired_cluster_bootstrap.csv',index=False)
    checks=dict(snapshot=str(args.snapshot.resolve()),new_model_fits=fits,checks=verified,
                primary_CV_molecules=105,OOD_molecules=17,OOD_exact_endpoints=67,OOD_bounds=1,
                comparison_source_seed=0,bootstrap_seed=1729,
                bootstrap_warning='OOD scaffold interval uses only four families; descriptive, small-group uncertainty.')
    (out/'verification.json').write_text(json.dumps(checks,indent=2))
    figure(tables,out)
    lines=['# Новые сравнения моделей — все расчёты завершены',
           '',f'{fits} новых fit на фиксированных разбиениях QAC-105 и OOD-17. Метрики независимо пересчитаны из предсказаний.',
           '', 'RMSE в log2(mg/L); меньше — лучше. Cation/scaffold CV: 420 точных конечных точек у 105 молекул. OOD: 67 точных конечных точек у 17 молекул; одно значение >500 mg/L сохранено как bound.',
           '', '## Полная таблица (без выбора по OOD)', '',
           '| Модель | Представление | Cation CV | Scaffold CV | OOD-17 |',
           '|---|---|---:|---:|---:|']
    for row in pivot.itertuples(index=False,name=None):
        # Columns are model, representation, cation, full-QAC105, scaffold.
        model,rep,cat,ood,scaffold=row
        lines.append(f'| {model} | {rep} | {cat:.3f} | {scaffold:.3f} | {ood:.3f} |')
    lines += ['', '## Что можно утверждать', '',
        'Человеческое source-обучение конкурентоспособно с количественным source-обучением при смене декодера. Для TabPFN-V2 на OOD: Human 1.966, Quant-continuous 2.265, Quant-binary 1.995, Raw 2.225; для TabFM: 1.992, 2.541, 2.110 и 2.299 соответственно.',
        '', 'RDKit descriptors — сильный самостоятельный baseline: CatBoost даёт 1.615 в cation CV и 1.818 в scaffold CV. Human+TabPFN и RDKit+TabPFN на OOD почти равны (1.966 против 1.978). Утверждение «human лучше всех» эти данные не поддерживают.',
        '', 'Chemprop D-MPNN: средний RMSE по 3 seeds — 2.031 / 2.003 / 2.375 (cation / scaffold / OOD). Это конкретный фиксированный протокол на небольшой выборке, а не доказательство общей слабости графовых сетей.',
        '', 'Табличные сравнения используют один source seed0, PCA-32 для 768-dimensional embeddings и отдельные endpoint модели. Они дополняют основной 5-seed matched causal тест, а не заменяют его. AutoGluon: RF/XT/GBM/CAT, 60 s selection + refit; TabPFN: публичные V2 weights с библиотекой 9.1.0; TabFM: официальный JAX checkpoint. OOD не использовался для выбора настроек.',
        '', '95% paired bootstrap intervals находятся в paired_cluster_bootstrap.csv. Cation/scaffold grouping согласована с CV; OOD дополнительно проверен по четырём новым scaffold families. При четырёх группах intervals следует считать описательными.',
        '', '## Проверка прежних расчётов', '',
        'Полный повтор основных v14 таблиц на прежних векторах совпал по всем предсказаниям. Все 30 matched partial-FT повторов совпали по initial state, IDs, batch order, labels, final loss и историческим предсказаниям; все 93 исторических target arrays совпали побитово.',
        '', 'При кодировании всех 105 молекул другими батчами векторы отличились на ~1e-6. CatBoost оказался чувствителен к этому для отдельных arms: например, mean OOD RMSE Quant-binary изменился с 2.099 до 2.068. Новые значения не заменяют прежние молча. Повтор прежнего batch layout с независимыми checkpoint восстановил ВСЕ 62 QAC105/OOD17 arrays побитово (layout_audit.json). Следовательно, эффект связан с численной чувствительностью нового порядка кодирования; повтор source-обучения воспроизвёл исходные модели.',
        '', 'c3-MolFormer и ChemFM повторы совпали с архивными общими предсказаниями точно. Для ChemBERTa, MolFormer MLP и context-панели переход Mac/Torch 2.4.1 → Linux/Torch 2.14 дал разные losses/предсказания при совпадающих initial state и training IDs. Это перенос между окружениями, не точное воспроизведение. Некоторые Ridge результаты крайне нестабильны; причина не локализована полностью. Архивные цифры от этого не становятся выдуманными.',
        '', '## Фигура', '',
        'new_decoder_error_violins.pdf: абсолютные ошибки по endpoint наблюдениям, медиана и IQR; 105 QAC и 17 OOD молекул. Наблюдения четырёх задач у одной молекулы зависимы. Диапазон оси включает все ошибки.',
        '', 'Ключи/API вызовы OpenRouter на сервер не переносились. Все исходные архивы оставлены без изменения.']
    (out/'RESULTS_RU.md').write_text('\n'.join(lines)+'\n')
    print('Verified',fits,'new fits; tables, confidence intervals, vector PDF and report:',out.resolve())


if __name__=='__main__':main()
