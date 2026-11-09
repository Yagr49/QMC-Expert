"""Q-HERO binary endpoint: published RF and fixed-budget target refits.

No model selection uses the held-out test set. Source-trained representations
are the archived, cation-excluded, matched partial MolFormer fine-tuning runs.
This experiment does not update the manuscript or supporting information.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import platform
import time

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from catboost import CatBoostClassifier
import catboost


def scores(y, probability):
    return dict(AUROC=float(roc_auc_score(y, probability)),
                AUPRC=float(average_precision_score(y, probability)),
                n=int(len(y)), positives=int(np.sum(y)),
                prevalence=float(np.mean(y)))


def fit_predict(kind, seed, x, y, train, test):
    if kind == 'RF_35_descriptors':
        model = RandomForestClassifier(random_state=seed, n_jobs=2)
    else:
        model = CatBoostClassifier(iterations=800, depth=6,
                                  learning_rate=0.05, random_seed=seed,
                                  thread_count=2, verbose=False,
                                  allow_writing_files=False)
    model.fit(x[train], y[train])
    return model.predict_proba(x[test])[:, 1]


def run_one(job):
    root, tag, seed = job
    root = Path(root)
    d = pd.read_csv(root / 'data' / 'target.csv')
    y = (d.sa_mic_um.to_numpy() <= 8).astype(int)
    desc = np.load(root / 'data' / 'descriptors.npy')
    if tag in ('RF_35_descriptors', 'CB_35_descriptors'):
        x = desc
    elif tag == 'CB_raw_MolFormer':
        x = np.load(root / 'data' / 'raw-molformer_Q-HERO-405.npy')
    else:
        arm = dict(CB_human='expert', CB_shuffled_human='expert-shuffled',
                   CB_quantitative='quant-continuous')[tag]
        x = np.load(root / 'data' / (arm + '_seed' + str(seed) + '_Q-HERO-405.npy'))
    assert len(x) == len(y) == 405 and np.isfinite(x).all()
    outer_train = np.flatnonzero(d.random_split.eq('train').to_numpy())
    outer_test = np.flatnonzero(d.random_split.eq('test').to_numpy())
    predictions, metrics = [], []

    def register(protocol, fold, idx, p):
        row = dict(model=tag, seed=seed, protocol=protocol, fold=fold)
        metrics.append(dict(row, **scores(y[idx], p)))
        for i, value in zip(idx, p):
            predictions.append(dict(row, row_index=int(i),
                                    can=d.can.iloc[i], label=int(y[i]),
                                    probability=float(value)))

    if seed == 0:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        for fold, (tr, va) in enumerate(cv.split(x[outer_train], y[outer_train])):
            tr, va = outer_train[tr], outer_train[va]
            p = fit_predict(tag, seed, x, y, tr, va)
            register('inner_random_CV_train80', fold, va, p)
    p = fit_predict(tag, seed, x, y, outer_train, outer_test)
    register('random_heldout20', -1, outer_test, p)
    pooled = np.full(len(y), np.nan)
    for fold in sorted(d.scaffold_fold.unique()):
        tr = np.flatnonzero(d.scaffold_fold.ne(fold).to_numpy())
        te = np.flatnonzero(d.scaffold_fold.eq(fold).to_numpy())
        p = fit_predict(tag, seed, x, y, tr, te)
        register('scaffold_CV_fold', int(fold), te, p)
        pooled[te] = p
    assert np.isfinite(pooled).all()
    metrics.append(dict(model=tag, seed=seed, protocol='scaffold_CV_pooled',
                        fold=-1, **scores(y, pooled)))
    return metrics, predictions


def reproduce_public_rf(root):
    df = pd.read_csv(root / 'data' / 'author_features_MIC.csv')
    x = df.iloc[:, :-1].to_numpy()
    # The public workbook contains untransformed MIC in micromolar.
    y = (df.iloc[:, -1].to_numpy() <= 8).astype(int)
    tr, te = train_test_split(np.arange(len(y)), test_size=0.2,
                             stratify=y, random_state=0)
    cv_rows = []
    for a, b in StratifiedKFold(5, shuffle=True, random_state=0).split(x[tr], y[tr]):
        p = fit_predict('RF_35_descriptors', 0, x, y, tr[a], tr[b])
        cv_rows.append(scores(y[tr[b]], p))
    p = fit_predict('RF_35_descriptors', 0, x, y, tr, te)
    return dict(n=len(y), cutoff_uM=8, positive_fraction=float(np.mean(y)),
                cv_mean={k:float(np.mean([r[k] for r in cv_rows]))
                         for k in ('AUROC', 'AUPRC')},
                cv_fold_sd_ddof0={k:float(np.std([r[k] for r in cv_rows]))
                                  for k in ('AUROC', 'AUPRC')},
                heldout20=scores(y[te], p),
                reported=dict(cv_AUROC=0.8036, cv_AUPRC=0.9672,
                              test_AUROC=0.5592, test_AUPRC=0.9121))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(Path(__file__).resolve().parent))
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    root = Path(args.root)
    out = root / 'results'
    out.mkdir(exist_ok=True)
    started = time.time()
    public = reproduce_public_rf(root)
    (out / 'public_RF_reproduction.json').write_text(json.dumps(public, indent=2))
    jobs = [(str(root), tag, seed)
            for tag in ('RF_35_descriptors', 'CB_35_descriptors', 'CB_raw_MolFormer',
                        'CB_human', 'CB_shuffled_human', 'CB_quantitative')
            for seed in (range(5) if tag in ('CB_human', 'CB_shuffled_human',
                                           'CB_quantitative') else [0])]
    all_metrics, all_predictions = [], []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, job):job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            metrics, predictions = future.result()
            all_metrics.extend(metrics)
            all_predictions.extend(predictions)
            pd.DataFrame(all_metrics).to_csv(out / 'metrics.csv', index=False)
            pd.DataFrame(all_predictions).to_csv(out / 'predictions.csv', index=False)
            print('finished', job[1], 'seed', job[2],
                  'elapsed', round(time.time()-started), flush=True)
    pd.DataFrame(all_metrics).sort_values(['model','seed','protocol','fold']).to_csv(
        out / 'metrics.csv', index=False)
    pd.DataFrame(all_predictions).sort_values(['model','seed','protocol','fold','row_index']).to_csv(
        out / 'predictions.csv', index=False)
    done = dict(completed=True, configurations=len(jobs),
                elapsed_seconds=time.time()-started,
                python=platform.python_version(), sklearn=sklearn.__version__,
                catboost=catboost.__version__, numpy=np.__version__,
                protocol='Fixed 800/depth6/lr0.05 CatBoostClassifier; no target-test selection',
                manuscript_changed=False)
    (out / 'completion.json').write_text(json.dumps(done, indent=2))
    print(json.dumps(done), flush=True)


if __name__ == '__main__':
    main()
