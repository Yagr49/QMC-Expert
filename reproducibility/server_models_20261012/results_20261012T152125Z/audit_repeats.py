"""Compare prediction-level repeats and independently recalculate metrics."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error
ROOT = Path(__file__).resolve().parent


def compare(oldpath, newpath):
    old = pd.read_csv(oldpath)
    new = pd.read_csv(newpath)
    if 'prediction' in new:
        keys = ['name', 'encoding', 'cohort', 'task', 'compound_id']
        score = 'prediction'
    else:
        keys = ['panel', 'arm', 'seed', 'head', 'target', 'can']
        score = 'pred'
    assert not old.duplicated(keys).any(), oldpath
    assert not new.duplicated(keys).any(), newpath
    merged = old.merge(new, on=keys, suffixes=('_old', '_new'), validate='one_to_one')
    if not len(merged):
        return dict(old_rows=len(old), new_rows=len(new), common_rows=0)
    assert np.allclose(merged.y_old, merged.y_new, rtol=0, atol=1e-12)
    a = merged[score + '_old'].to_numpy()
    b = merged[score + '_new'].to_numpy()
    assert np.isfinite(b).all()
    groups = ['name', 'encoding', 'cohort'] if score == 'prediction' else ['panel', 'arm', 'seed', 'head', 'target']
    metrics = []
    for key, group in merged.groupby(groups):
        exact = group.qualifier_new == '=' if 'qualifier_new' in group else np.ones(len(group), dtype=bool)
        group = group[exact]
        y, p = group.y_new, group[score + '_new']
        metrics.append(dict(zip(groups, key), n=len(y),
                      recomputed_RMSE=float(np.sqrt(mean_squared_error(y, p))),
                      recomputed_R2=float(r2_score(y, p)),
                      max_prediction_difference=float(np.max(np.abs(group[score + '_old'] - p)))))
    return dict(old_rows=len(old), new_rows=len(new), common_rows=len(merged),
                max_prediction_difference=float(np.max(np.abs(a - b))),
                equal_within_1e_8=bool(np.allclose(a, b, rtol=0, atol=1e-8)), metrics=metrics)


def main():
    mapping = json.loads((ROOT / 'reference_mapping.json').read_text())
    reports = {}
    for name, paths in mapping.items():
        old, new = [ROOT / path for path in paths]
        if not new.exists():
            reports[name] = dict(status='missing_new_output')
            continue
        reports[name] = compare(old, new)
        print(name, {k: v for k, v in reports[name].items() if k != 'metrics'}, flush=True)
    old = pd.read_csv(ROOT / 'references/ft/training.csv')
    new = pd.read_csv(ROOT / 'core_ft/results/training.csv')
    paired = old.merge(new, on=['arm', 'seed'], suffixes=('_old', '_new'), validate='one_to_one')
    comparisons = {}
    for column in ['initial_sha256', 'batch_order_sha256', 'train_id_sha256', 'label_sha256',
                   'epochs', 'updates', 'final_train_loss', 'final_val_loss']:
        a, b = paired[column + '_old'], paired[column + '_new']
        if pd.api.types.is_numeric_dtype(a):
            comparisons[column] = dict(max_abs_difference=float(np.max(np.abs(a-b))),
                                      allclose=bool(np.allclose(a, b, rtol=1e-6, atol=1e-7)))
        else:
            comparisons[column] = dict(equal=int((a == b).sum()), total=len(paired))
    reports['source_training'] = dict(common_runs=len(paired), expected_runs=30, comparisons=comparisons)
    reports['notes'] = ['Frozen feature extraction uses hash-verified archives.',
                        'FT checkpoint bytes differ because the repeat includes all mutable buffers.',
                        'Compare original and new protocol identically; no OOD-based selection.']
    def numeric_json(value):
        if isinstance(value, np.generic):
            return value.item()
        raise TypeError(type(value).__name__)
    (ROOT / 'audit_repeats.json').write_text(json.dumps(reports, indent=2, default=numeric_json))


if __name__ == '__main__':
    main()
