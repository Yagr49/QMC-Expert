"""New graph/tabular baselines on fixed QAC105 folds and untouched OOD17."""
import os
from pathlib import Path
import argparse
import hashlib
import importlib.metadata as metadata
import inspect
import json
import platform
import time
import traceback
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import spearmanr
import joblib

ROOT = Path(__file__).resolve().parent
OLD = Path('/home/yagr/coma_revision_v14_20261011')
TASKS = ['Sa_MIC', 'Sa_MBC', 'Ec_MIC', 'Ec_MBC']
REPRESENTATIONS = ['rdkit', 'raw-molformer', 'expert_seed0',
                   'quant-continuous_seed0', 'quant-binary_seed0']


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, default=str))
    tmp.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def registry():
    r = pd.read_csv(OLD / 'data/endpoint_registry.csv')
    q = r[r.cohort == 'QAC105'].copy()
    o = r[r.cohort == 'OOD17'].copy()
    qm = q.drop_duplicates('molecule_index').sort_values('molecule_index')
    om = o.drop_duplicates('molecule_index').sort_values('molecule_index')
    assert qm.molecule_index.tolist() == list(range(105))
    assert om.molecule_index.tolist() == list(range(17))
    assert len(q) == 420 and len(o) == 68 and (q.qualifier == '=').all()
    assert (o.qualifier == '=').sum() == 67
    assert not set(q.cation) & set(o.cation)
    assert not set(q.scaffold) & set(o.scaffold)
    source = pd.read_csv(ROOT / 'core_ft/data/matched-pooled_expert.csv')
    assert not set(source.cation) & (set(q.cation) | set(o.cation))
    assert not set(source.scaffold) & set(o.scaffold)
    scaffold = pd.read_csv(OLD / 'scaffold_sensitivity/data/endpoint_registry.csv')
    sf = scaffold[scaffold.cohort == 'QAC105'].drop_duplicates('molecule_index').set_index('molecule_index').fold
    folds = {'cation': qm.fold.to_numpy(), 'scaffold': sf.loc[range(105)].to_numpy()}
    y = q.pivot(index='molecule_index', columns='task', values='y').loc[range(105), TASKS].to_numpy()
    assert np.isfinite(y).all()
    for schema, f in folds.items():
        groups = qm.cation if schema == 'cation' else qm.scaffold
        for fold in sorted(set(f)):
            assert not set(groups[f != fold]) & set(groups[f == fold])
    return q, o, qm, om, folds, y


def splits(folds):
    for schema, assignments in folds.items():
        for fold in sorted(set(assignments)):
            yield schema, int(fold), np.flatnonzero(assignments != fold), np.flatnonzero(assignments == fold), False
    yield 'full-QAC105', -1, np.arange(105), np.arange(17), True


def features(name, qm, om):
    if name != 'rdkit':
        return (np.load(OLD / 'representations' / (name + '_QAC105.npy')),
                np.load(OLD / 'representations' / (name + '_OOD17.npy')))
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    def describe(smiles):
        rows = []
        for smi in smiles:
            mol = Chem.MolFromSmiles(smi)
            assert mol is not None
            values = []
            for _, fun in Descriptors._descList:
                try:
                    value = float(fun(mol))
                    values.append(value if np.isfinite(value) else np.nan)
                except Exception:
                    values.append(np.nan)
            rows.append(values)
        return np.asarray(rows, dtype=np.float64)
    return describe(qm.can), describe(om.can)


def transform_train_only(x, xt, use_pca):
    x = np.asarray(x, dtype=np.float64).copy()
    xt = np.asarray(xt, dtype=np.float64).copy()
    x[~np.isfinite(x)] = np.nan
    xt[~np.isfinite(xt)] = np.nan
    imputer = SimpleImputer(strategy='median', keep_empty_features=True)
    a = imputer.fit_transform(x)
    b = imputer.transform(xt)
    variance = VarianceThreshold()
    a = variance.fit_transform(a)
    b = variance.transform(b)
    scaler = StandardScaler()
    a = scaler.fit_transform(a)
    b = scaler.transform(b)
    pca = None
    if use_pca:
        pca = PCA(n_components=min(32, len(a) - 1, a.shape[1]), svd_solver='full')
        a = pca.fit_transform(a)
        b = pca.transform(b)
    return a, b, dict(imputer=imputer, variance=variance, scaler=scaler, pca=pca)


def table_prediction(model_name, x, y, xt, groups, artifact, seed, shared):
    artifact.mkdir(parents=True, exist_ok=True)
    info = {}
    if model_name == 'catboost':
        from catboost import CatBoostRegressor
        model = CatBoostRegressor(iterations=300, depth=5, learning_rate=.05,
                 random_seed=1729, thread_count=2, verbose=False, allow_writing_files=False)
        model.fit(x, y)
        model.save_model(str(artifact / 'model.cbm'))
        pred = model.predict(xt)
    elif model_name == 'autogluon':
        from autogluon.tabular import TabularPredictor
        tr, va = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=1729)
                      .split(x, groups=groups))
        assert not set(groups[tr]) & set(groups[va])
        columns = [f'x{i}' for i in range(x.shape[1])]
        frame = pd.DataFrame(x, columns=columns)
        frame['__target__'] = y
        predictor = TabularPredictor(label='__target__', problem_type='regression',
                           eval_metric='root_mean_squared_error', path=str(artifact / 'predictor'), verbosity=2)
        predictor.fit(frame.iloc[tr], tuning_data=frame.iloc[va],
                      hyperparameters={'RF': {}, 'XT': {}, 'GBM': {}, 'CAT': {}},
                      time_limit=60, num_bag_folds=0, num_stack_levels=0,
                      num_cpus=2, num_gpus=0, fit_weighted_ensemble=False)
        best = predictor.model_best
        mapping = predictor.refit_full(model=best)
        full = mapping[best]
        pred = predictor.predict(pd.DataFrame(xt, columns=columns), model=full).to_numpy()
        info = dict(inner_train_n=len(tr), inner_val_n=len(va), selected_model=best,
                    refitted_model=full, selection_budget_s=60, refit_extra_budget=True)
        predictor.leaderboard().to_csv(artifact / 'inner_leaderboard.csv', index=False)
    elif model_name == 'tabpfn':
        from tabpfn import TabPFNRegressor
        from tabpfn.constants import ModelVersion
        kw = dict(n_estimators=4, device='cuda', random_state=1729)
        if 'n_preprocessing_jobs' in inspect.signature(TabPFNRegressor).parameters:
            kw['n_preprocessing_jobs'] = 1
        # V3/V2.6 require browser license acceptance; this unattended baseline
        # uses the supported publicly downloadable V2 regression checkpoint.
        model = TabPFNRegressor.create_default_for_version(ModelVersion.V2, **kw)
        model.fit(x, y)
        pred = model.predict(xt)
        model_paths = getattr(model, 'model_path', None)
        path_list = model_paths if isinstance(model_paths, list) else [model_paths]
        info = dict(constructor=kw, model_path=str(model_paths), model_version='v2',
                    checkpoint_sha256={str(p): sha(Path(p)) for p in path_list if p and Path(str(p)).is_file()})
        shared['tabpfn_identity'] = info
    elif model_name == 'tabfm':
        from tabfm import TabFMRegressor
        from tabfm import tabfm_v1_0_0_jax
        if 'tabfm_model' not in shared:
            import jax.numpy as jnp
            shared['tabfm_model'] = tabfm_v1_0_0_jax.load(model_type='regression',
                col_attention_impl='jax', row_attention_impl='jax', icl_attention_impl='jax', dtype=jnp.float32)
        signature = inspect.signature(TabFMRegressor).parameters
        kw = dict(model=shared['tabfm_model'])
        if 'n_estimators' in signature:
            kw['n_estimators'] = 4
        if 'random_state' in signature:
            kw['random_state'] = 1729
        model = TabFMRegressor(**kw)
        columns = [f'x{i}' for i in range(x.shape[1])]
        model.fit(pd.DataFrame(x, columns=columns), y)
        pred = np.asarray(model.predict(pd.DataFrame(xt, columns=columns))).reshape(-1)
        info = dict(backend='jax-cpu', constructor={k: v for k, v in kw.items() if k != 'model'},
                    estimator_parameters={k: str(v) for k, v in model.get_params(deep=False).items() if k != 'model'},
                    checkpoint_snapshots=[str(p) for p in (ROOT / 'runtime/hf').glob('hub/models--*/snapshots/*')])
        shared['tabfm_identity'] = info
    else:
        raise ValueError(model_name)
    pred = np.asarray(pred).reshape(-1)
    assert len(pred) == len(xt) and np.isfinite(pred).all()
    return pred, info


def graph_prediction(qm, om, y, tr, te, is_ood, artifact, seed, epochs, progress_path):
    import torch
    from chemprop import data, featurizers, models, nn
    from lightning import pytorch as pl
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    pl.seed_everything(seed, workers=True)
    train = [data.MoleculeDatapoint.from_smi(qm.can.iloc[i], y[i].copy()) for i in tr]
    test_smiles = (om if is_ood else qm).can.iloc[te]
    test = [data.MoleculeDatapoint.from_smi(smi, np.full(4, np.nan)) for smi in test_smiles]
    featurizer = featurizers.SimpleMoleculeMolGraphFeaturizer()
    train_data = data.MoleculeDataset(train, featurizer)
    scaler = train_data.normalize_targets()
    test_data = data.MoleculeDataset(test, featurizer)
    train_loader = data.build_dataloader(train_data, batch_size=32, num_workers=0, shuffle=True, seed=seed)
    test_loader = data.build_dataloader(test_data, batch_size=32, num_workers=0, shuffle=False)
    predictor = nn.RegressionFFN(n_tasks=4, output_transform=nn.UnscaleTransform.from_standard_scaler(scaler))
    model = models.MPNN(nn.BondMessagePassing(d_h=300, depth=3), nn.MeanAggregation(), predictor,
                        batch_norm=False)
    class Progress(pl.Callback):
        def on_train_epoch_end(self, trainer, pl_module):
            write_json(progress_path, dict(model='chemprop', seed=seed, fit=str(artifact.name),
                       epoch=trainer.current_epoch + 1, total_epochs=epochs, updated=time.time()))
    trainer = pl.Trainer(logger=False, enable_checkpointing=False, enable_progress_bar=False,
              accelerator='gpu', devices=1, max_epochs=epochs, limit_val_batches=0,
              deterministic=True, callbacks=[Progress()], enable_model_summary=False)
    trainer.fit(model, train_loader)
    pred = torch.cat(trainer.predict(model, test_loader)).cpu().numpy()
    artifact.mkdir(parents=True, exist_ok=True)
    trainer.save_checkpoint(artifact / 'final.ckpt')
    joblib.dump(scaler, artifact / 'target_scaler.joblib')
    assert pred.shape == (len(te), 4) and np.isfinite(pred).all()
    del model, trainer
    torch.cuda.empty_cache()
    return pred, dict(epochs=epochs, checkpoint='final', hidden=300, depth=3,
                      batch_norm=False, n_tasks=4, target_transform='train-only StandardScaler')


def summarize(out):
    chunks = sorted((out / 'chunks').glob('*.csv'))
    if not chunks:
        return
    predictions = pd.concat([pd.read_csv(p) for p in chunks], ignore_index=True)
    predictions.to_csv(out / 'predictions.csv', index=False)
    bounds = predictions[predictions.qualifier != '='].copy()
    if len(bounds):
        bounds['above_lower_bound'] = bounds.prediction >= bounds.y
        bounds['prediction_minus_bound'] = bounds.prediction - bounds.y
        bounds.to_csv(out / 'bound_diagnostics.csv', index=False)
    rows = []
    keys = ['model', 'representation', 'seed', 'schema', 'cohort']
    for key, group in predictions.groupby(keys):
        for task in TASKS + ['pooled']:
            subset = group[(group.task == task) & (group.qualifier == '=')] if task != 'pooled' else group[group.qualifier == '=']
            if not len(subset):
                continue
            actual, pred = subset.y.to_numpy(), subset.prediction.to_numpy()
            rows.append(dict(zip(keys, key), task=task, n=len(subset),
                         RMSE=float(np.sqrt(mean_squared_error(actual, pred))),
                         MAE=float(mean_absolute_error(actual, pred)),
                         R2=float(r2_score(actual, pred)) if len(actual) > 1 else None,
                         rho=float(spearmanr(actual, pred).statistic) if len(actual) > 1 else None,
                         status='complete' if len(group) in (420, 68) else 'partial'))
    pd.DataFrame(rows).to_csv(out / 'metrics.csv', index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, choices=['catboost', 'autogluon', 'chemprop', 'tabpfn', 'tabfm'])
    ap.add_argument('--smoke', action='store_true')
    args = ap.parse_args()
    q, o, qm, om, folds, y = registry()
    out = ROOT / 'new_baselines' / (args.model + ('_smoke' if args.smoke else ''))
    (out / 'chunks').mkdir(parents=True, exist_ok=True)
    (out / 'artifacts').mkdir(exist_ok=True)
    versions = {}
    for package in ['numpy', 'pandas', 'scipy', 'scikit-learn', 'rdkit', 'torch', 'chemprop',
                    'autogluon.tabular', 'tabpfn', 'tabfm', 'jax', 'flax', 'catboost']:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            pass
    manifest = dict(model=args.model, started=time.time(), completed=False,
               python=platform.python_version(), packages=versions, smoke=args.smoke,
               script_sha256=sha(Path(__file__)), protocol_sha256=sha(ROOT / 'PROTOCOL_RU.md'),
               input_sha256={str(p): sha(p) for p in [OLD / 'data/endpoint_registry.csv',
                           OLD / 'scaffold_sensitivity/data/endpoint_registry.csv']},
               target='log2(mg/L)', OOD_exact_n=67, OOD_censored_n=1,
               source_seed=0, external_inference_API=False)
    for rep in REPRESENTATIONS[1:]:
        for cohort in ['QAC105', 'OOD17']:
            p = OLD / 'representations' / (rep + '_' + cohort + '.npy')
            manifest['input_sha256'][str(p)] = sha(p)
    write_json(out / 'manifest.json', manifest)
    shared = {}
    reps = ['graph'] if args.model == 'chemprop' else REPRESENTATIONS
    seeds = range(3) if args.model == 'chemprop' else [1729]
    all_splits = list(splits(folds))
    if args.smoke:
        reps = reps[:1]
        seeds = [0]
        all_splits = all_splits[:1]
    errors = []
    completed = 0
    for rep in reps:
        if rep != 'graph':
            x, xo = features(rep, qm, om)
        for seed in seeds:
            for schema, fold, tr, te, is_ood in all_splits:
                job_name = f'{rep}_s{seed}_{schema}_f{fold}'
                artifact = out / 'artifacts' / job_name
                cohort_registry = o if is_ood else q
                subset = cohort_registry[cohort_registry.molecule_index.isin(te)].copy()
                if rep == 'graph':
                    target_jobs = [('all', None)]
                else:
                    a, b, preprocessor = transform_train_only(x[tr], (xo if is_ood else x)[te], rep != 'rdkit')
                    artifact.mkdir(parents=True, exist_ok=True)
                    joblib.dump(preprocessor, artifact / 'preprocessor.joblib')
                    target_jobs = list(enumerate(TASKS))
                for column, task in target_jobs:
                    chunk = out / 'chunks' / (job_name + '_' + str(task) + '.csv')
                    if chunk.exists():
                        continue
                    started = time.time()
                    print('FIT', args.model, job_name, task, 'train', len(tr), 'test', len(te), flush=True)
                    try:
                        if rep == 'graph':
                            pred, details = graph_prediction(qm, om, y, tr, te, is_ood, artifact, seed,
                                               2 if args.smoke else 100, out / 'progress.json')
                            result = subset.copy()
                            lookup = {(int(i), t): float(pred[k, j]) for k, i in enumerate(te) for j, t in enumerate(TASKS)}
                            result['prediction'] = [lookup[(int(r.molecule_index), r.task)] for r in result.itertuples()]
                        else:
                            groups = (qm.cation if schema == 'cation' else qm.scaffold).to_numpy()[tr]
                            pred, details = table_prediction(args.model, a, y[tr, column], b, groups,
                                                          artifact / task, seed, shared)
                            result = subset[subset.task == task].copy()
                            lookup = dict(zip(te.tolist(), pred.tolist()))
                            result['prediction'] = result.molecule_index.map(lookup)
                        result['fold'] = fold
                        result['model'] = args.model
                        result['representation'] = rep
                        result['seed'] = seed
                        result['schema'] = schema
                        assert result.prediction.notna().all()
                        tmp = chunk.with_suffix('.tmp')
                        result.to_csv(tmp, index=False)
                        tmp.replace(chunk)
                        write_json(chunk.with_suffix('.json'), dict(parameters=details, seconds=time.time()-started,
                                   train_ids=qm.compound_id.iloc[tr].tolist(), test_ids=(om if is_ood else qm).compound_id.iloc[te].tolist()))
                        completed += 1
                        summarize(out)
                        write_json(out / 'progress.json', dict(completed_fits=completed, current=job_name,
                                   task=task, seconds=time.time()-manifest['started'], errors=len(errors)))
                        print('DONE FIT', job_name, task, round(time.time()-started, 1), flush=True)
                    except Exception as exc:
                        traceback.print_exc()
                        errors.append(dict(job=job_name, task=task, error=repr(exc)))
                        write_json(out / 'errors.json', errors)
                        # Missing model packages or inaccessible weights affect all fits.
                        if isinstance(exc, (ImportError, ModuleNotFoundError)) or any(
                           token in str(exc).lower() for token in ['gated', '401', '403', 'authentication', 'access token']):
                            manifest.update(completed=False, failed=True, errors=errors, finished=time.time())
                            write_json(out / 'manifest.json', manifest)
                            raise
    summarize(out)
    manifest.update(completed=not errors, finished=time.time(), errors=errors,
                    fits=len(list((out / 'chunks').glob('*.csv'))),
                    model_identity={k: v for k, v in shared.items() if k.endswith('_identity')})
    write_json(out / 'manifest.json', manifest)
    if errors:
        raise RuntimeError(f'{len(errors)} model fits failed; see errors.json')


if __name__ == '__main__':
    main()
