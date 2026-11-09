"""Independent endpoint metrics, paired interventions and publication figures."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import r2_score

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parents[1]
TASKS = ['Sa_MIC', 'Sa_MBC', 'Ec_MIC', 'Ec_MBC']
ARMS = ['expert', 'quant-continuous', 'quant-binary', 'expert-shuffled',
        'quant-shuffled', 'quant-binary-shuffled']
MODES = ['linear', 'compact', 'lora', 'partial', 'full']
VARIANTS = ['intact', 'rewind_outer_norm', 'rewind_blocks', 'rewind_all']
SCHEMES = ['cation', 'scaffold', 'full-QAC105']
KEYS = ['cohort', 'compound_id', 'task']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_chunks(snapshot, branch, partial):
    paths = sorted((snapshot / branch / 'chunks').glob('*.csv'))
    expected = 363 if branch == 'direct' else 1331
    if not partial:
        assert len(paths) == expected, (branch, len(paths), expected)
    frames, ledgers = [], []
    registry = pd.read_csv(ROOT / 'data/endpoint_registry.csv').set_index(KEYS)
    molecule = registry.reset_index().drop_duplicates(['cohort', 'compound_id']).set_index('compound_id')
    for path in paths:
        record = json.loads(path.with_suffix('.json').read_text())
        d = pd.read_csv(path)
        assert np.isfinite(d.prediction).all()
        assert not d.duplicated(KEYS).any()
        original = registry.loc[pd.MultiIndex.from_frame(d[KEYS])]
        assert np.allclose(d.y, original.y, rtol=0, atol=1e-12)
        assert np.array_equal(d.qualifier.to_numpy(), original.qualifier.to_numpy())
        assert set(d.compound_id) == set(record['test_ids'])
        train_ids, test_ids = set(record['train_ids']), set(record['test_ids'])
        assert not train_ids & test_ids
        grouping = 'scaffold' if record['schema'] in ['scaffold', 'full-QAC105'] else 'cation'
        assert not set(molecule.loc[list(train_ids), grouping]) & set(molecule.loc[list(test_ids), grouping])
        if branch == 'direct':
            assert record['epochs'] == 30
            assert record['updates'] == 30 * int(np.ceil(len(train_ids) / 32))
            y_train = registry.reset_index().query('cohort == "QAC105"').pivot(
                index='compound_id', columns='task', values='y').loc[record['train_ids'], TASKS].to_numpy()
            assert np.allclose(record['target_mean'], y_train.mean(axis=0).astype('float32'), atol=1e-7, rtol=0)
            assert np.allclose(record['target_sd'], y_train.std(axis=0).astype('float32'), atol=1e-7, rtol=0)
        frames.append(d)
        ledgers.append(record)
    result = pd.concat(frames, ignore_index=True)
    ids = ['arm', 'mode' if branch == 'direct' else 'variant', 'seed', 'schema']
    assert not result.duplicated(ids + KEYS).any()
    # A partial snapshot cannot contribute an incomplete out-of-fold cohort.
    kept = []
    for key, group in result.groupby(ids):
        is_ood = key[-1] == 'full-QAC105'
        if len(group) != (68 if is_ood else 420):
            assert partial
            continue
        assert group.compound_id.nunique() == (17 if is_ood else 105)
        assert (group.qualifier == '=').sum() == (67 if is_ood else 420)
        if not is_ood:
            assert set(group.fold) == set(range(5))
        kept.append(group)
    result = pd.concat(kept, ignore_index=True)
    return result, ledgers


def metric_tables(d, branch):
    category = 'mode' if branch == 'direct' else 'variant'
    rows = []
    for key, group in d[d.qualifier == '='].groupby(['arm', category, 'seed', 'schema']):
        metadata = dict(zip(['arm', category, 'seed', 'schema'], key))
        for task in ['pooled'] + TASKS:
            g = group if task == 'pooled' else group[group.task == task]
            error = g.prediction.to_numpy() - g.y.to_numpy()
            rows.append(dict(**metadata, task=task, n=len(g), RMSE=float(np.sqrt(np.mean(error ** 2))),
                MAE=float(np.mean(np.abs(error))),
                R2=float(r2_score(g.y, g.prediction)) if task != 'pooled' else np.nan,
                Spearman=float(spearmanr(g.y, g.prediction).statistic) if task != 'pooled' else np.nan))
    metrics = pd.DataFrame(rows)
    summary = metrics.groupby(['arm', category, 'schema', 'task']).agg(
        RMSE=('RMSE', 'mean'), RMSE_SD=('RMSE', 'std'), MAE=('MAE', 'mean'),
        MAE_SD=('MAE', 'std'), R2=('R2', 'mean'), R2_SD=('R2', 'std'),
        Spearman=('Spearman', 'mean'), runs=('seed', 'nunique'), n_exact=('n', 'first')).reset_index()
    return metrics, summary


def censor_sensitivity(d, branch):
    category = 'mode' if branch == 'direct' else 'variant'
    rows = []
    for key, group in d[d.schema == 'full-QAC105'].groupby(['arm', category, 'seed']):
        metadata = dict(zip(['arm', category, 'seed'], key))
        for task in ['pooled', 'Ec_MBC']:
            g = group if task == 'pooled' else group[group.task == task]
            exact = g[g.qualifier == '=']
            bounded = g[g.qualifier == '>']
            assert len(bounded) == 1 and bounded.compound_id.iloc[0] == 'IT505'
            errors = np.concatenate([(exact.y - exact.prediction).to_numpy(),
                                     np.maximum(bounded.y - bounded.prediction, 0).to_numpy()])
            rows.append(dict(**metadata, task=task, exact=len(exact), right_censored=1,
                RMSE_lower_bound=float(np.sqrt(np.mean(errors**2))),
                MAE_lower_bound=float(np.abs(errors).mean()),
                bound=500, prediction_log2=float(bounded.prediction.iloc[0]),
                violates_lower_bound=bool(bounded.prediction.iloc[0] < bounded.y.iloc[0])))
    return pd.DataFrame(rows)


def paired_bootstrap(a, b, grouping, draws=5000):
    a, b = a[a.qualifier == '='].copy(), b[b.qualifier == '='].copy()
    seeds = sorted(set(a.seed) & set(b.seed))
    if not seeds:
        if set(a.seed) == {-1}:
            a = pd.concat([a.assign(seed=s) for s in sorted(set(b.seed))], ignore_index=True)
        elif set(b.seed) == {-1}:
            b = pd.concat([b.assign(seed=s) for s in sorted(set(a.seed))], ignore_index=True)
        seeds = sorted(set(a.seed) & set(b.seed))
    assert seeds
    a, b = a[a.seed.isin(seeds)], b[b.seed.isin(seeds)]
    merged = a.merge(b, on=['seed'] + KEYS, suffixes=['_a', '_b'], validate='one_to_one')
    assert len(merged) == len(a) == len(b)
    assert np.allclose(merged.y_a, merged.y_b, rtol=0, atol=1e-12)
    assert np.array_equal(merged[grouping + '_a'], merged[grouping + '_b'])
    groups = sorted(set(merged[grouping + '_a']))
    sums_a, sums_b, sizes = [], [], []
    for seed in seeds:
        subset = merged[merged.seed == seed].copy()
        subset['e_a'] = (subset.y_a - subset.prediction_a) ** 2
        subset['e_b'] = (subset.y_b - subset.prediction_b) ** 2
        blocks = subset.groupby(grouping + '_a').agg(a=('e_a', 'sum'), b=('e_b', 'sum'), n=('e_a', 'size')).loc[groups]
        sums_a.append(blocks.a.to_numpy()); sums_b.append(blocks.b.to_numpy()); sizes.append(blocks.n.to_numpy())
    sums_a, sums_b, sizes = map(np.asarray, [sums_a, sums_b, sizes])
    assert (sizes == sizes[0]).all()
    point = (np.sqrt(sums_a.sum(axis=1) / sizes.sum(axis=1)) -
             np.sqrt(sums_b.sum(axis=1) / sizes.sum(axis=1))).mean()
    rng = np.random.default_rng(1729)
    ix_s = rng.integers(len(seeds), size=(draws, len(seeds)))
    ix_g = rng.integers(len(groups), size=(draws, len(groups)))
    n = sizes[0][ix_g].sum(axis=1)[:, None]
    a_draw = sums_a[ix_s[:, :, None], ix_g[:, None, :]].sum(axis=2)
    b_draw = sums_b[ix_s[:, :, None], ix_g[:, None, :]].sum(axis=2)
    values = (np.sqrt(a_draw / n) - np.sqrt(b_draw / n)).mean(axis=1)
    return dict(delta_RMSE_a_minus_b=float(point), low=float(np.quantile(values, .025)),
                high=float(np.quantile(values, .975)), grouping=grouping, groups=len(groups),
                seeds=len(seeds), n_exact_per_seed=int(sizes[0].sum()), draws=draws)


def contrasts(direct, ablation):
    rows = []
    def add(branch, d, akey, bkey, kind):
        category = 'mode' if branch == 'direct' else 'variant'
        for schema in SCHEMES:
            a = d[(d.arm == akey[0]) & (d[category] == akey[1]) & (d.schema == schema)]
            b = d[(d.arm == bkey[0]) & (d[category] == bkey[1]) & (d.schema == schema)]
            if a.empty or b.empty:
                continue
            for grouping in (['scaffold'] if schema == 'scaffold' else ['cation', 'scaffold']):
                rows.append(dict(branch=branch, contrast=kind, a='/'.join(akey), b='/'.join(bkey),
                                 schema=schema, **paired_bootstrap(a, b, grouping)))
    for mode in MODES[1:]:
        add('direct', direct, ('raw-molformer', mode), ('raw-molformer', 'linear'), 'capacity_vs_linear')
    for mode in ['partial', 'full']:
        add('direct', direct, ('raw-molformer', 'lora'), ('raw-molformer', mode), 'lora_vs_backbone')
    for real, shuffled in zip(ARMS[:3], ARMS[3:]):
        add('direct', direct, (real, 'partial'), (shuffled, 'partial'), 'real_vs_shuffled')
        add('direct', direct, (real, 'partial'), ('raw-molformer', 'partial'), 'source_vs_raw_init')
        add('ablation', ablation, (real, 'intact'), (shuffled, 'intact'), 'real_vs_shuffled')
        add('ablation', ablation, (real, 'intact'), ('raw-molformer', 'raw'), 'source_vs_pure_raw')
    for comparator in ['quant-continuous', 'quant-binary']:
        add('direct', direct, ('expert', 'partial'), (comparator, 'partial'), 'human_vs_quantitative')
    for arm in ARMS:
        for variant in VARIANTS[1:]:
            add('ablation', ablation, (arm, variant), (arm, 'intact'), 'weight_rewind_minus_intact')
        add('ablation', ablation, (arm, 'rewind_all'), ('raw-molformer', 'raw'), 'buffer_state_vs_pure_raw')
    # Both prediction routes use the same first three source checkpoints.
    for arm in ARMS[:3]:
        for schema in SCHEMES:
            a = direct[(direct.arm == arm) & (direct['mode'] == 'partial') & (direct.schema == schema)]
            b = ablation[(ablation.arm == arm) & (ablation.variant == 'intact') &
                         ablation.seed.isin([0, 1, 2]) & (ablation.schema == schema)]
            if a.empty or b.empty:
                continue
            b = b[b.seed.isin(a.seed)]
            for grouping in (['scaffold'] if schema == 'scaffold' else ['cation', 'scaffold']):
                rows.append(dict(branch='routes', contrast='direct_minus_frozen_decoder',
                    a=arm+'/partial', b=arm+'/intact', schema=schema, **paired_bootstrap(a, b, grouping)))
    return pd.DataFrame(rows)


def audits(snapshot, direct, ablation, ledgers, partial):
    paired = []
    records = pd.DataFrame(ledgers)
    for key, group in records.groupby(['seed', 'schema', 'fold']):
        for column in ['batch_order_sha256', 'target_mean', 'target_sd']:
            assert len({json.dumps(value) for value in group[column]}) == 1, (key, column)
        linear_heads = group[group['mode'] != 'compact']
        assert linear_heads.initial_head_sha256.nunique() == 1
        paired.append(dict(seed=int(key[0]), schema=key[1], fold=int(key[2]), fits=len(group),
                           same_batch_order=True, same_linear_head=True, same_train_only_scale=True))
    vectors = json.loads((snapshot/'ablation/vector_status.json').read_text())
    assert vectors['completed'] and vectors['configurations'] == 121
    assert vectors['intact_all_exact'] and vectors['buffer_state_shared_within_seed']
    assert all(r['rewind_all_equal_across_arms'] for r in vectors['rewind_all_audit'])
    comparisons = []
    for (arm, seed, schema), group in ablation[ablation.variant.isin(['intact', 'raw'])].groupby(['arm', 'seed', 'schema']):
        name = arm if arm == 'raw-molformer' else arm + '_seed' + str(seed)
        base = COMA / 'reproducibility/revision_v14'
        if schema == 'scaffold':
            old = pd.read_csv(base / 'scaffold_sensitivity/results' / (name + '_onehot_predictions.csv'))
        else:
            old = pd.read_csv(base / 'results' / (name + '_onehot_predictions.csv'))
        old = old[old.cohort == ('OOD17' if schema == 'full-QAC105' else 'QAC105')]
        merged = group.merge(old, on=KEYS, suffixes=['_new', '_old'], validate='one_to_one')
        assert len(merged) == len(group) == len(old)
        delta = float(np.max(np.abs(merged.prediction_new - merged.prediction_old)))
        assert delta < 1e-12, (arm, seed, schema, delta)
        comparisons.append(dict(arm=arm, seed=int(seed), schema=schema, n=len(merged), max_prediction_difference=delta))
    identical = []
    rewind = ablation[ablation.variant == 'rewind_all']
    for (seed, schema), group in rewind.groupby(['seed', 'schema']):
        arms = sorted(set(group.arm))
        reference = group[group.arm == arms[0]].set_index(KEYS).prediction.sort_index()
        for arm in arms[1:]:
            other = group[group.arm == arm].set_index(KEYS).prediction.sort_index()
            assert np.array_equal(reference.to_numpy(), other.to_numpy())
        identical.append(dict(seed=int(seed), schema=schema, arms=len(arms), predictions_identical=True))
    if not partial:
        assert len(comparisons) == 93 and len(identical) == 15
        assert all(row['arms'] == 6 for row in identical)
        checkpoint_replay = json.loads((snapshot/'checkpoint_replay.json').read_text())
        assert checkpoint_replay['completed'] and checkpoint_replay['final_models'] == 33
        assert len(checkpoint_replay['checks']) == 33
        assert all(r['max_prediction_difference'] < 1e-12 and r['encoder_hash_matches']
                   for r in checkpoint_replay['checks'])
    else:
        checkpoint_replay = None
    return dict(completed=not partial, partial_snapshot=partial, snapshot=str(snapshot),
                direct_fits=len(ledgers), ablation_fits=len(list((snapshot/'ablation/chunks').glob('*.csv'))),
                direct_pairing_checks=paired, original_prediction_replays=comparisons,
                weight_rewind_shared_buffer_audit=vectors, rewind_all_predictions_equal=identical,
                saved_final_models_replay=checkpoint_replay,
                script_sha256=sha(ROOT/'run_experiments.py'),
                interval_convention='5000 paired seed/group draws, unadjusted, conditional on fitted models; four OOD families')


def plots(direct, ablation, ci, out):
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'.plot_cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'sans-serif', 'font.sans-serif':['Arial', 'DejaVu Sans'],
        'font.size':8, 'axes.linewidth':.8, 'pdf.fonttype':42, 'ps.fonttype':42,
        'xtick.direction':'out', 'ytick.direction':'out'})
    titles = ['Cation holdout', 'Scaffold holdout', 'OOD-17']
    color = ['#4B79A3', '#858585', '#A46DA0', '#C38239', '#329465']
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.5), sharey=True)
    pooled = direct[(direct.task == 'pooled') & (direct.arm == 'raw-molformer')]
    for ax, schema, title in zip(axes, SCHEMES, titles):
        for j, mode in enumerate(MODES):
            g = pooled[(pooled['mode'] == mode) & (pooled.schema == schema)]
            ax.scatter(np.full(len(g), j) + np.linspace(-.13, .13, len(g)), g.RMSE,
                       color=color[j], s=15, alpha=.6)
            ax.plot([j-.2, j+.2], [g.RMSE.mean()]*2, color=color[j], linewidth=2)
        ax.set_xticks(range(5)); ax.set_xticklabels(['Linear', 'MLP', 'LoRA', 'Partial', 'Full'], rotation=38, ha='right', fontsize=7)
        ax.set_title(title); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    axes[0].set_ylabel(r'Pooled RMSE, $\log_2$(mg/L)')
    fig.tight_layout(pad=1)
    for extension in ['pdf', 'svg', 'png']:
        fig.savefig(out/('figure7_direct_adaptation.'+extension), dpi=300, bbox_inches='tight')
    plt.close(fig)


def route_violins(direct, ablation, out):
    import matplotlib.pyplot as plt
    blue, orange = '#4B79A3', '#C38239'
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.7), sharey=True)
    upper = 0.
    for ax, schema, title in zip(axes, SCHEMES, ['Cation holdout', 'Scaffold holdout', 'OOD-17']):
        for j, arm in enumerate(ARMS[:3]):
            for left, d, color in [(True, direct, blue), (False, ablation, orange)]:
                g = d[(d.arm == arm) & (d.schema == schema) & (d.qualifier == '=') & d.seed.isin([0,1,2])].copy()
                if not left:
                    g = g[g.variant == 'intact']
                g['absolute_error'] = np.abs(g.y - g.prediction)
                values = g.groupby(KEYS).absolute_error.mean().to_numpy()
                assert len(values) == (67 if schema == 'full-QAC105' else 420)
                upper = max(upper, float(values.max()))
                violin = ax.violinplot(values, positions=[j], widths=.8, showextrema=False)
                for body in violin['bodies']:
                    vertices = body.get_paths()[0].vertices
                    vertices[:,0] = (np.minimum(vertices[:,0], j) if left else np.maximum(vertices[:,0], j))
                    body.set_facecolor(color); body.set_edgecolor(color); body.set_alpha(.38)
                lo, med, hi = np.quantile(values, [.25,.5,.75])
                x = j + (-.13 if left else .13)
                ax.vlines(x, lo, hi, color=color, linewidth=1.4)
                ax.plot([x-.06, x+.06], [med, med], color=color, linewidth=2)
        ax.set_title(title); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        ax.set_xticks(range(3)); ax.set_xticklabels(['Human','Continuous\nMIC','Binary\nMIC'], fontsize=7)
        ax.text(.98,.97,'n = '+str(67 if schema == 'full-QAC105' else 420),
                transform=ax.transAxes,ha='right',va='top',fontsize=7)
    axes[0].set_ylabel(r'Mean absolute error, $\log_2$(mg/L)')
    for ax in axes:
        ax.set_ylim(0, np.ceil(upper + .2))
    from matplotlib.patches import Patch
    axes[1].legend(handles=[Patch(facecolor=blue,alpha=.38,label='Direct target FT'),
                  Patch(facecolor=orange,alpha=.38,label='Frozen encoder + decoder')],
                  frameon=False,fontsize=7,ncol=2,loc='upper center',bbox_to_anchor=(.5,-.27))
    fig.tight_layout(pad=1)
    for extension in ['pdf', 'svg', 'png']:
        fig.savefig(out/('figureS22_prediction_route_violins.'+extension), dpi=300, bbox_inches='tight')
    plt.close(fig)


def weight_plot(ci, out):
    import matplotlib.pyplot as plt
    titles = ['Cation holdout', 'Scaffold holdout', 'OOD-17']
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.8), sharey=True)
    labels = ['Outer norm', 'Eight blocks', 'All weights']
    arms = ['expert', 'quant-continuous', 'quant-binary']
    colors = ['#329465', '#C38239', '#A46DA0']
    for ax, schema, title in zip(axes, SCHEMES, titles):
        for j, variant in enumerate(VARIANTS[1:]):
            for k, arm in enumerate(arms):
                r = ci[(ci.branch == 'ablation') & (ci.contrast == 'weight_rewind_minus_intact') &
                       (ci.a == arm+'/'+variant) & (ci.schema == schema) & (ci.grouping == 'scaffold')].iloc[0]
                x = j + (k-1)*.22
                ax.errorbar(x, r.delta_RMSE_a_minus_b, yerr=[[r.delta_RMSE_a_minus_b-r.low],
                    [r.high-r.delta_RMSE_a_minus_b]], fmt='o', markersize=3.5, capsize=2,
                    color=colors[k], linewidth=1.1, label=['Human','Continuous MIC','Binary MIC'][k] if j == 0 else None)
        ax.axhline(0, color='#777777', linewidth=.6, linestyle='--')
        ax.set_xticks(range(3)); ax.set_xticklabels(labels, rotation=28, ha='right', fontsize=7)
        ax.set_title(title); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    axes[0].set_ylabel(r'Rewind minus intact $\Delta$RMSE')
    axes[1].legend(frameon=False, fontsize=7, loc='upper center', bbox_to_anchor=(.5, -.36), ncol=3)
    fig.tight_layout(pad=1)
    for extension in ['pdf', 'svg', 'png']:
        fig.savefig(out/('figure8_weight_rewind.'+extension), dpi=300, bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    out = ROOT / ('partial_analysis' if args.partial else 'analysis')
    out.mkdir(exist_ok=True)
    direct, ledgers = read_chunks(args.snapshot, 'direct', args.partial)
    ablation, _ = read_chunks(args.snapshot, 'ablation', args.partial)
    report = audits(args.snapshot, direct, ablation, ledgers, args.partial)
    for branch, d in [('direct',direct), ('ablation',ablation)]:
        metrics, summary = metric_tables(d, branch)
        metrics.to_csv(out/(branch+'_metrics.csv'), index=False)
        summary.to_csv(out/(branch+'_summary.csv'), index=False)
        d.to_csv(out/(branch+'_predictions.csv'), index=False)
        censor_sensitivity(d, branch).to_csv(out/(branch+'_censor_sensitivity.csv'), index=False)
    if not args.partial:
        ci = contrasts(direct, ablation)
        ci.to_csv(out/'paired_bootstrap.csv', index=False)
        parameters = pd.DataFrame(ledgers).groupby(['arm','mode']).agg(
            parameters=('trainable_parameters','first'), fits=('epochs','size'),
            median_fit_seconds=('seconds','median')).reset_index()
        parameters.to_csv(out/'parameters_and_budgets.csv', index=False)
        plots(pd.read_csv(out/'direct_metrics.csv'), pd.read_csv(out/'ablation_metrics.csv'), ci, out)
        weight_plot(ci, out)
        route_violins(direct, ablation, out)
    (out/'verification.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({key:report[key] for key in ['completed','snapshot','direct_fits','ablation_fits']}, indent=2))


if __name__ == '__main__':
    main()
