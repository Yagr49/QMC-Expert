"""Paired uncertainty and independent consistency audit for matched partial FT."""
from pathlib import Path
import importlib.util, hashlib, json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results'
OUT = ROOT / 'analysis'
OUT.mkdir(exist_ok=True)
B = 10000
spec = importlib.util.spec_from_file_location('v10_contrasts', ROOT.parent / 'revision_v10' / 'analyse_extension.py')
v10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v10)


def weighted_ranks(values, weights):
    """Midranks in an expanded bootstrap sample without materialising repeats."""
    order = np.argsort(values, kind='stable')
    sorted_values = values[order]
    starts = np.r_[0, np.flatnonzero(sorted_values[1:] != sorted_values[:-1]) + 1]
    counts = np.diff(np.r_[starts, len(values)])
    mass = np.add.reduceat(weights[:, order], starts, axis=1)
    ranks = np.repeat(np.cumsum(mass, axis=1) - .5 * mass + .5, counts, axis=1)
    return ranks[:, np.argsort(order)]


def weighted_spearman(x, y, weights):
    rx = weighted_ranks(x, weights); ry = weighted_ranks(y, weights)
    count = weights.sum(axis=1, keepdims=True)
    rx -= (rx * weights).sum(axis=1, keepdims=True) / count
    ry -= (ry * weights).sum(axis=1, keepdims=True) / count
    cov = (weights * rx * ry).sum(axis=1)
    den = np.sqrt((weights * rx**2).sum(axis=1) * (weights * ry**2).sum(axis=1))
    return np.divide(cov, den, out=np.full(len(weights), np.nan), where=den > 0)


def audit_weighted_rank():
    # Independent oracle: physically expand samples and call SciPy, including ties.
    rng = np.random.default_rng(614)
    for _ in range(12):
        x = rng.integers(-3, 4, 30); y = rng.integers(0, 5, 30)
        w = rng.integers(0, 5, 30); ix = np.repeat(np.arange(30), w)
        exact = spearmanr(x[ix], y[ix]).statistic
        assert np.isclose(weighted_spearman(x, y, w[None, :])[0], exact, atol=1e-12)


def direct_contrasts(predictions):
    audit_weighted_rank(); rows = []
    pairs = [('expert', 'expert-shuffled'), ('expert', 'quant-continuous'),
             ('expert', 'quant-binary'), ('quant-continuous', 'quant-shuffled'),
             ('quant-binary', 'quant-binary-shuffled')]
    for target, d in predictions.groupby('target'):
        info = d.drop_duplicates('can').set_index('can').sort_index()
        molecules = info.index; y = info.y.values; groups = info.scaffold.values
        ids, group_index = np.unique(groups, return_inverse=True)
        rng = np.random.default_rng(1729)
        sampled = rng.integers(len(ids), size=(B, len(ids)))
        counts = np.zeros((B, len(ids)), dtype='float64')
        for j in range(len(ids)): counts[:, j] = (sampled == j).sum(axis=1)
        weights = counts[:, group_index]
        seed_draws = rng.integers(5, size=(B, 5))
        bootstrap = {}; point = {}
        for arm, sub in d.groupby('arm'):
            matrix = sub.pivot(index='seed', columns='can', values='rank_score').reindex(columns=molecules)
            assert matrix.shape == (5, len(molecules)) and not matrix.isna().any().any()
            bootstrap[arm] = np.stack([weighted_spearman(score, y, weights) for score in matrix.values], axis=1)
            point[arm] = float(np.mean([spearmanr(score, y).statistic for score in matrix.values]))
        for aa, bb in pairs:
            first = np.take_along_axis(bootstrap[aa], seed_draws, axis=1).mean(axis=1)
            second = np.take_along_axis(bootstrap[bb], seed_draws, axis=1).mean(axis=1)
            delta = first - second; valid = np.isfinite(delta)
            lo, hi = np.quantile(delta[valid], [.025, .975])
            rows.append(dict(target=target, comparison=aa + ' minus ' + bb, n=len(molecules),
                scaffolds=len(ids), seeds=5, unit='seed+scaffold', delta_rank=point[aa] - point[bb],
                ci_low=float(lo), ci_high=float(hi), valid_bootstrap_draws=int(valid.sum())))
    return pd.DataFrame(rows)


def main():
    manifest = json.loads((RESULTS / 'manifest.json').read_text())
    assert manifest['completed'] and not manifest['smoke'] and manifest['seeds'] == 5 and manifest['epochs'] == 30
    p = pd.read_csv(RESULTS / 'predictions.csv'); m = pd.read_csv(RESULTS / 'metrics.csv')
    t = pd.read_csv(RESULTS / 'training.csv'); e = pd.read_csv(RESULTS / 'epochs.csv')
    dp = pd.read_csv(RESULTS / 'direct_predictions.csv'); dm = pd.read_csv(RESULTS / 'direct_metrics.csv')
    assert len(m) == 93 and len(p) == 31 * 526 and len(t) == 30 and len(e) == 900
    assert len(dm) == 90 and len(dp) == 30 * 526
    assert not p.duplicated(['arm', 'seed', 'target', 'can']).any()
    assert not dp.duplicated(['arm', 'seed', 'target', 'can']).any()
    assert np.isfinite(p[['y', 'pred']].values).all() and np.isfinite(dp[['y', 'score', 'rank_score']].values).all()
    assert (t.train_n == 377).all() and (t.val_n == 304).all() and (t.updates == 360).all()
    for seed, d in t.groupby('seed'):
        assert len(d) == 6
        for column in ['initial_sha256', 'batch_order_sha256', 'train_id_sha256']: assert d[column].nunique() == 1
    reconstruction=pd.concat([pd.read_csv(path) for path in RESULTS.glob('checkpoint_reconstruction_seeds_*.csv')],ignore_index=True)
    assert len(reconstruction)==30 and not reconstruction.duplicated(['arm','seed']).any()
    assert (reconstruction.feature_map_count==12).all()
    assert reconstruction.max_feature_difference.max()<=1e-6
    assert reconstruction.max_score_difference.max()<=1e-6
    reconstruction.to_csv(OUT/'checkpoint_reconstruction.csv',index=False)
    keys = ['arm', 'seed', 'target']
    for key, d in p.groupby(keys):
        row = m.set_index(keys).loc[key]
        assert len(d) == row.n
        assert np.isclose(r2_score(d.y, d.pred), row.R2)
        assert np.isclose(np.sqrt(mean_squared_error(d.y, d.pred)), row.RMSE)
    for key, d in dp.groupby(keys):
        row = dm.set_index(keys).loc[key]
        assert np.isclose(spearmanr(d.y, d.rank_score).statistic, row.rank_agreement)
        assert np.isclose(roc_auc_score((d.y < np.median(d.y)).astype(int), -d.rank_score), row.AUC)
        if row.kind == 'continuous':
            assert np.isclose(r2_score(d.y, d.score), row.R2)
            assert np.isclose(np.sqrt(mean_squared_error(d.y, d.score)), row.RMSE)
    for filename, digest in manifest['output_sha256'].items():
        assert hashlib.sha256((RESULTS / filename).read_bytes()).hexdigest() == digest
    assert (RESULTS / 'target_folds.csv').read_bytes() == (ROOT / 'data' / 'target_folds.csv').read_bytes()
    source = pd.read_csv(ROOT / 'data' / 'matched-pooled_expert.csv')
    tr, va = next(GroupShuffleSplit(n_splits=1, test_size=.15, random_state=1729).split(source, groups=source.scaffold))
    split = pd.read_csv(RESULTS / 'source_split.csv')
    assert split.can.tolist() == source.can.tolist()
    assert split.iloc[tr].partition.eq('train').all() and split.iloc[va].partition.eq('validation').all()
    target_cations = set().union(*(set(pd.read_csv(ROOT / 'data' / f'target_{name}.csv').cation)
                                   for name in ['QAC-104', 'Q-HERO-405', 'OOD-17']))
    assert not set(source.cation) & target_cations
    summary = m.groupby(['arm', 'target']).agg(seeds=('seed', 'nunique'), n=('n', 'first'),
        R2=('R2', 'mean'), R2_sd=('R2', 'std'), RMSE=('RMSE', 'mean'), RMSE_sd=('RMSE', 'std')).reset_index()
    summary.to_csv(OUT / 'summary.csv', index=False)
    ds = dm.groupby(['arm', 'target', 'kind']).agg(seeds=('seed', 'nunique'), n=('n', 'first'),
        rank_agreement=('rank_agreement', 'mean'), rank_sd=('rank_agreement', 'std'),
        AUC=('AUC', 'mean'), AUC_sd=('AUC', 'std'), R2=('R2', 'mean'), RMSE=('RMSE', 'mean')).reset_index()
    ds.to_csv(OUT / 'direct_summary.csv', index=False)
    p['se'] = (p.y - p.pred)**2
    pairs = [('expert', 'expert-shuffled'), ('expert', 'raw-molformer'), ('expert', 'quant-continuous'),
             ('expert', 'quant-binary'), ('quant-continuous', 'quant-shuffled'),
             ('quant-binary', 'quant-binary-shuffled'), ('quant-continuous', 'raw-molformer'),
             ('quant-binary', 'raw-molformer')]
    contrasts = []
    for target, sub in p.groupby('target'):
        for aa, bb in pairs:
            for row in v10.contrast(sub, aa, bb): contrasts.append(dict(target=target, **row))
    pd.DataFrame(contrasts).to_csv(OUT / 'contrasts.csv', index=False)
    # Numerical reproducibility and architecture comparison against existing matched MLP.
    archived_dir = ROOT.parent / 'revision_v9' / 'results_matched-pooled_matched-sa_full'
    archived = pd.read_csv(archived_dir / 'predictions.csv')
    archived = archived[(archived['head'] == 'catboost') & archived.panel.isin(['matched-pooled', 'baseline'])].copy()
    old_features = np.load(ROOT.parent / 'revision_v9' / 'data' / 'molformer.npy')
    smiles = json.loads((ROOT.parent / 'revision_v9' / 'data' / 'smiles.json').read_text())
    index = {s: i for i, s in enumerate(smiles)}; feature_checks = []
    for target in ['QAC-104', 'Q-HERO-405', 'OOD-17']:
        d = pd.read_csv(ROOT / 'data' / f'target_{target}.csv')
        raw = np.load(RESULTS / 'representations' / f'raw-molformer_{target}.npy')
        old = old_features[[index[s] for s in d.can]]
        feature_checks.append(dict(target=target, max_absolute_difference=float(np.max(np.abs(raw - old))),
            mean_absolute_difference=float(np.mean(np.abs(raw - old))),
            allclose_rtol_1e_4_atol_1e_5=bool(np.allclose(raw, old, rtol=1e-4, atol=1e-5))))
    comparison = p.copy(); comparison['arm'] = 'ft-' + comparison.arm
    archived['arm'] = 'mlp-' + archived.arm; archived['se'] = (archived.y - archived.pred)**2
    combined = pd.concat([comparison, archived], ignore_index=True); architecture = []
    for target, sub in combined.groupby('target'):
        for aa, bb in [('ft-expert', 'mlp-expert'), ('ft-quant-continuous', 'mlp-quant-continuous'),
                       ('ft-raw-molformer', 'mlp-raw-molformer')]:
            for row in v10.contrast(sub, aa, bb): architecture.append(dict(target=target, **row))
    pd.DataFrame(architecture).to_csv(OUT / 'adaptation_contrasts.csv', index=False)
    direct_contrasts(dp).to_csv(OUT / 'direct_contrasts.csv', index=False)
    report = dict(completed=True, recomputed_metric_rows=len(m), recomputed_direct_metric_rows=len(dm),
        prediction_rows=len(p), direct_prediction_rows=len(dp), paired_initialisations_and_batches=True,
        source_target_cation_overlap=0, fixed_folds_identical=True, epochs=30, updates_per_arm=360,
        source_seeds=5, token_truncation=0, bootstrap_samples=B, weighted_rank_expansion_audit=True,
        raw_feature_comparison=feature_checks, checkpoint_storage='server; hashes in training.csv',
        reconstructed_checkpoints=30, final_feature_map_buffers_verified=True,
        max_reconstructed_feature_difference=float(reconstruction.max_feature_difference.max()),
        max_reconstructed_score_difference=float(reconstruction.max_score_difference.max()),
        limitations='Exploratory unadjusted intervals; fixed folds; five seeds; source-target scaffolds may overlap.')
    (ROOT / 'validation.json').write_text(json.dumps(report, indent=2))
    print(summary[summary.target == 'Q-HERO-405'].to_string(index=False))
    print(ds[ds.target == 'Q-HERO-405'].to_string(index=False))
    print('VALIDATED', len(m), 'downstream and', len(dm), 'direct metric rows')


if __name__ == '__main__': main()
