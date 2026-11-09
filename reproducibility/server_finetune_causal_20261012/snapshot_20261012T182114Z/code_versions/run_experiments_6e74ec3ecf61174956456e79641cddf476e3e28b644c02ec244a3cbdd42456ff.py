"""Direct-target FT and weight-rewind controls on fixed QAC105/OOD17 cohorts."""
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
OLD = Path('/home/yagr/coma_models_check_20261012')
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
sys.path.insert(0, str(OLD / 'core_ft'))
import run_matched_finetuning as ft
import argparse
import hashlib
import json
import time
import copy
import platform
import numpy as np
import pandas as pd
import torch
from torch import nn
from catboost import CatBoostRegressor
from sklearn.metrics import r2_score
from scipy.stats import spearmanr

TASKS = ['Sa_MIC', 'Sa_MBC', 'Ec_MIC', 'Ec_MBC']
VARIANTS = ['intact', 'rewind_pooler', 'rewind_blocks', 'rewind_all']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tensor_sha(values):
    digest = hashlib.sha256()
    for name, tensor in sorted(values.items()):
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, default=str))
    tmp.replace(path)


def csv(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    value.to_csv(tmp, index=False)
    tmp.replace(path)


def seed_code(seed, schema, fold):
    return 1729 + seed * 100000 + {'cation': 0, 'scaffold': 10000, 'full-QAC105': 20000}[schema] + (fold + 1) * 100


def setup(device):
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    if device.type == 'cuda':
        torch.cuda.set_per_process_memory_fraction(.38)


def read_data():
    q = pd.read_csv(ROOT / 'data/QAC105.csv')
    o = pd.read_csv(ROOT / 'data/OOD17.csv')
    registry = pd.read_csv(ROOT / 'data/endpoint_registry.csv')
    scaffold = pd.read_csv(ROOT / 'data/scaffold_endpoint_registry.csv')
    qm = registry[registry.cohort == 'QAC105'].drop_duplicates('molecule_index').sort_values('molecule_index')
    om = registry[registry.cohort == 'OOD17'].drop_duplicates('molecule_index').sort_values('molecule_index')
    assert qm.compound_id.tolist() == q.compound_id.tolist()
    assert om.compound_id.tolist() == o.code.tolist()
    assert len(qm) == 105 and len(om) == 17
    assert (registry[registry.cohort == 'QAC105'].qualifier == '=').all()
    assert len(registry[(registry.cohort == 'OOD17') & (registry.qualifier == '=')]) == 67
    y = registry[registry.cohort == 'QAC105'].pivot(index='molecule_index', columns='task', values='y')[TASKS].to_numpy()
    sf = scaffold[scaffold.cohort == 'QAC105'].drop_duplicates('molecule_index').sort_values('molecule_index').fold.to_numpy()
    folds = {'cation': qm.fold.to_numpy(), 'scaffold': sf}
    for schema, ids in folds.items():
        group = qm.cation if schema == 'cation' else qm.scaffold
        assert pd.DataFrame(dict(group=group.to_numpy(), fold=ids)).groupby('group').fold.nunique().max() == 1
    source = pd.read_csv(OLD / 'core_ft/data/matched-pooled_expert.csv')
    assert not set(source.cation) & (set(qm.cation) | set(om.cation))
    assert not set(om.scaffold) & (set(source.scaffold) | set(qm.scaffold))
    return q, o, registry, qm, om, y, folds


def iter_splits(folds):
    for schema, ids in folds.items():
        for fold in sorted(set(ids)):
            yield schema, int(fold), np.flatnonzero(ids != fold), np.flatnonzero(ids == fold), False
    yield 'full-QAC105', -1, np.arange(105), np.arange(17), True


def restored_net(arm, seed, device):
    # The pure pretrained reference uses the same seed-0 feature-map state.
    net, _ = ft.load_net(0, device)
    checkpoint = None
    if arm != 'raw-molformer':
        checkpoint = OLD / 'core_ft/results/checkpoints' / f'{arm}_seed{seed}.pt'
        saved = torch.load(checkpoint, map_location='cpu', weights_only=False)
        assert saved['includes_all_buffers']
        live = net.state_dict()
        auxiliary = {n: value for n, value in saved['state_dict'].items() if n not in live}
        result = net.load_state_dict({n: value for n, value in saved['state_dict'].items() if n in live}, strict=False)
        frozen = {n for n, parameter in net.named_parameters() if not parameter.requires_grad}
        assert set(result.missing_keys) == frozen and not result.unexpected_keys
        buffers = dict(net.named_buffers())
        assert set(auxiliary).issubset(buffers)
        with torch.no_grad():
            for name, value in auxiliary.items():
                buffers[name].copy_(value.to(device=buffers[name].device, dtype=buffers[name].dtype))
    return net, checkpoint


def registry_predictions(registry, pred, te, is_ood, metadata):
    out = registry[(registry.cohort == ('OOD17' if is_ood else 'QAC105')) & registry.molecule_index.isin(te)].copy()
    lookup = {(int(index), task): float(pred[k, j]) for k, index in enumerate(te) for j, task in enumerate(TASKS)}
    out['prediction'] = [lookup[(int(row.molecule_index), row.task)] for row in out.itertuples()]
    for key, value in metadata.items():
        out[key] = value
    assert out.prediction.notna().all() and np.isfinite(out.prediction).all()
    return out


class TargetModel(nn.Module):
    def __init__(self, encoder, mode):
        super().__init__()
        self.enc = encoder
        for parameter in self.enc.parameters():
            parameter.requires_grad = mode in ['partial', 'full']
        if mode == 'partial':
            for name, parameter in self.enc.named_parameters():
                if name.startswith('embeddings') or any(f'layer.{i}.' in name for i in range(4)):
                    parameter.requires_grad = False
        self.norm = nn.LayerNorm(768)
        self.head = (nn.Sequential(nn.Linear(768, 256), nn.GELU(), nn.Dropout(.1),
                     nn.Linear(256, 128), nn.GELU(), nn.Dropout(.1), nn.Linear(128, 4))
                     if mode == 'compact' else nn.Linear(768, 4))

    def from_features(self, features):
        return self.head(self.norm(features))

    def forward(self, **tokens):
        return self.from_features(self.enc(**tokens).pooler_output)


def direct(args):
    device = torch.device('cuda')
    setup(device)
    _, _, registry, qm, om, y, folds = read_data()
    tokenizer = ft.AutoTokenizer.from_pretrained(ft.MODEL, revision=ft.REVISION,
                 code_revision=ft.REVISION, trust_remote_code=True)
    tokenizer.padding_side = 'right'
    assert max(map(len, tokenizer(qm.can.tolist() + om.can.tolist(), truncation=False)['input_ids'])) <= 202
    qt = ft.tokenise(tokenizer, qm.can)
    ot = ft.tokenise(tokenizer, om.can)
    out = ROOT / 'direct'
    configurations = [(arm, mode, seed) for seed in range(3)
                      for arm in ['raw-molformer'] + ft.ARMS
                      for mode in (['linear', 'compact', 'partial', 'full'] if arm == 'raw-molformer' else ['partial'])]
    work = [(arm, mode, seed, split) for arm, mode, seed in configurations for split in iter_splits(folds)]
    if args.smoke:
        first_split = next(iter_splits(folds))
        work = [(arm, mode, 0, first_split) for arm, mode in
                [('raw-molformer', 'linear'), ('raw-molformer', 'compact'),
                 ('raw-molformer', 'partial'), ('raw-molformer', 'full'),
                 ('expert', 'partial'), ('expert-shuffled', 'partial')]]
    for index, (arm, mode, seed, split) in enumerate(work):
        if index % args.workers != args.worker:
            continue
        schema, fold, tr, te, is_ood = split
        name = f'{arm}_{mode}_s{seed}_{schema}_f{fold}'
        chunk = out / 'chunks' / (name + '.csv')
        ledger = chunk.with_suffix('.json')
        if chunk.exists() and ledger.exists():
            continue
        start = time.time()
        print('FIT', name, 'train', len(tr), 'test', len(te), flush=True)
        net, checkpoint = restored_net(arm, seed, device)
        stochastic_seed = seed_code(seed, schema, fold)
        torch.manual_seed(stochastic_seed)
        model = TargetModel(net.enc, mode).to(device)
        del net
        initial_head_sha = tensor_sha({n: value for n, value in model.state_dict().items() if not n.startswith('enc.')})
        initial_encoder_sha = tensor_sha(dict(model.enc.named_parameters()))
        trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
        count = sum(parameter.numel() for parameter in trainable)
        initial_target_mean = y[tr].mean(axis=0).astype('float32')
        initial_target_sd = y[tr].std(axis=0).astype('float32')
        assert (initial_target_sd > 0).all()
        targets = torch.tensor((y[tr] - initial_target_mean) / initial_target_sd, dtype=torch.float32, device=device)
        order_generator = torch.Generator().manual_seed(stochastic_seed + 7)
        encoder = [p for p in model.enc.parameters() if p.requires_grad]
        head = [p for name, p in model.named_parameters() if not name.startswith('enc.')]
        groups = [{'params': head, 'lr': .001}]
        max_lrs = [.001]
        if encoder:
            groups.append({'params': encoder, 'lr': .00003})
            max_lrs.append(.00003)
        optimizer = torch.optim.AdamW(groups, weight_decay=.01)
        epochs = 2 if args.smoke else 30
        steps = int(np.ceil(len(tr) / 32)) * epochs
        scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=max_lrs, total_steps=steps)
        cached = None
        if mode in ['linear', 'compact']:
            qx = np.load(OLD / 'core_v14/representations/raw-molformer_QAC105.npy')
            ox = np.load(OLD / 'core_v14/representations/raw-molformer_OOD17.npy')
            cached = torch.tensor(qx[tr], dtype=torch.float32, device=device)
        batches = hashlib.sha256()
        curves = []
        update = 0
        for epoch in range(epochs):
            model.train()
            if cached is not None:
                model.enc.eval()
            order = torch.randperm(len(tr), generator=order_generator)
            batches.update(order.numpy().tobytes())
            total = 0.
            for pos in range(0, len(tr), 32):
                ix = order[pos:pos + 32]
                torch.manual_seed(stochastic_seed + 1000 + update)
                if cached is None:
                    batch = {key: value[tr[ix.numpy()]].to(device) for key, value in qt.items()}
                    predictions = model(**batch)
                else:
                    predictions = model.from_features(cached[ix.to(device)])
                optimizer.zero_grad(set_to_none=True)
                loss = nn.functional.mse_loss(predictions, targets[ix.to(device)])
                assert torch.isfinite(loss)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(trainable, 1.)
                optimizer.step()
                scheduler.step()
                total += float(loss.detach()) * len(ix)
                update += 1
            curves.append(dict(epoch=epoch + 1, loss=total / len(tr), updates=update))
            write_json(out / 'status' / f'worker{args.worker}.json', dict(current=name, epoch=epoch + 1,
                       epochs=epochs, seconds=time.time() - start, completed_chunks=len(list((out / 'chunks').glob('*.csv')))))
        model.eval()
        with torch.no_grad():
            if cached is not None:
                features = torch.tensor((ox if is_ood else qx)[te], dtype=torch.float32, device=device)
                pred = model.from_features(features).cpu().numpy()
            else:
                tokens = ot if is_ood else qt
                parts = []
                for pos in range(0, len(te), 32):
                    batch = {key: value[te[pos:pos + 32]].to(device) for key, value in tokens.items()}
                    parts.append(model(**batch).cpu().numpy())
                pred = np.vstack(parts)
        pred = pred * initial_target_sd + initial_target_mean
        metadata = dict(arm=arm, mode=mode, seed=seed, schema=schema, fold=fold)
        result = registry_predictions(registry, pred, te, is_ood, metadata)
        artifact = out / 'checkpoints' / (name + '.pt')
        artifact.parent.mkdir(parents=True, exist_ok=True)
        buffers = dict(model.named_buffers())
        state = {n: parameter.detach().cpu() for n, parameter in model.named_parameters() if parameter.requires_grad}
        state.update({n: value.detach().cpu() for n, value in buffers.items()})
        torch.save(dict(state_dict=state, parameters=count, metadata=metadata,
                        mean=initial_target_mean, sd=initial_target_sd, source_checkpoint=str(checkpoint),
                        pretrained_revision=ft.REVISION, includes_all_buffers=True), artifact)
        write_json(ledger, dict(**metadata, train_ids=qm.compound_id.iloc[tr].tolist(),
                   test_ids=(om if is_ood else qm).compound_id.iloc[te].tolist(), trainable_parameters=count,
                   initial_head_sha256=initial_head_sha, initial_encoder_sha256=initial_encoder_sha,
                   batch_order_sha256=batches.hexdigest(), updates=update, epochs=epochs,
                   target_mean=initial_target_mean.tolist(), target_sd=initial_target_sd.tolist(),
                   curves=curves, source_checkpoint_sha256=sha(checkpoint) if checkpoint else None,
                   checkpoint_sha256=sha(artifact), seconds=time.time() - start,
                   script_sha256=sha(Path(__file__)), protocol_sha256=sha(ROOT / 'PROTOCOL_RU.md')))
        csv(chunk, result)
        print('DONE', name, 'seconds', round(time.time() - start, 2), flush=True)
        del model, optimizer, scheduler, trainable, encoder, head, cached, targets, state, buffers
        del groups, loss, predictions
        torch.cuda.empty_cache()
    write_json(out / 'status' / f'worker{args.worker}.json', dict(completed=True, worker=args.worker,
               expected_total_fits=len(work), completed_chunks=len(list((out / 'chunks').glob('*.csv')))))


def encode_layout(net, q, o, tokens, device):
    original_q = pd.read_csv(OLD / 'core_ft/data/target_QAC-104.csv')
    original_o = pd.read_csv(OLD / 'core_ft/data/target_OOD-17.csv')
    small = q[~q.can.isin(original_q.can)].can.tolist() + original_q.can.iloc[:3].tolist()
    assert len(small) == 4
    q104, _ = ft.outputs(net, tokens['q104'], device)
    one, _ = ft.outputs(net, tokens['small'], device)
    od, _ = ft.outputs(net, tokens['ood'], device)
    lookup = dict(zip(original_q.can, q104))
    lookup[small[0]] = one[0]
    return np.vstack([lookup[smi] for smi in q.can]), od[[original_o.can.tolist().index(smi) for smi in o.can]]


def ablation_vectors(args):
    device = torch.device('cuda')
    setup(device)
    q, o, _, _, _, _, _ = read_data()
    tokenizer = ft.AutoTokenizer.from_pretrained(ft.MODEL, revision=ft.REVISION,
                 code_revision=ft.REVISION, trust_remote_code=True)
    tokenizer.padding_side = 'right'
    original_q = pd.read_csv(OLD / 'core_ft/data/target_QAC-104.csv')
    original_o = pd.read_csv(OLD / 'core_ft/data/target_OOD-17.csv')
    small = q[~q.can.isin(original_q.can)].can.tolist() + original_q.can.iloc[:3].tolist()
    tokens = dict(q104=ft.tokenise(tokenizer, original_q.can), small=ft.tokenise(tokenizer, small),
                  ood=ft.tokenise(tokenizer, original_o.can))
    raw, _ = restored_net('raw-molformer', 0, device)
    base = {name: value.detach().cpu().clone() for name, value in raw.enc.named_parameters()}
    del raw
    out = ROOT / 'ablation'
    (out / 'representations').mkdir(parents=True, exist_ok=True)
    for cohort in ['QAC105', 'OOD17']:
        np.save(out / 'representations' / f'raw-molformer_{cohort}.npy',
                np.load(OLD / 'core_v14/representations' / f'raw-molformer_{cohort}.npy'))
    seeds = [0] if args.smoke else range(5)
    arms = ['expert', 'expert-shuffled'] if args.smoke else ft.ARMS
    for seed in seeds:
        for arm in arms:
            tag = f'{arm}_seed{seed}'
            for variant in VARIANTS:
                name = tag + '__' + variant
                ledger = out / 'ledgers' / (name + '.json')
                if ledger.exists():
                    continue
                net, checkpoint = restored_net(arm, seed, device)
                buffer_hash = tensor_sha(dict(net.enc.named_buffers()))
                changed = []
                if variant != 'intact':
                    with torch.no_grad():
                        for parameter_name, parameter in net.enc.named_parameters():
                            match = (variant == 'rewind_all' or
                                     (variant == 'rewind_pooler' and parameter_name.startswith('pooler')) or
                                     (variant == 'rewind_blocks' and any(f'layer.{i}.' in parameter_name for i in range(4, 12))))
                            if match:
                                parameter.copy_(base[parameter_name].to(device))
                                changed.append(parameter_name)
                    assert changed
                qx, ox = encode_layout(net, q, o, tokens, device)
                assert tensor_sha(dict(net.enc.named_buffers())) == buffer_hash
                equality = {}
                for cohort, array in [('QAC105', qx), ('OOD17', ox)]:
                    np.save(out / 'representations' / f'{name}_{cohort}.npy', array)
                    if variant == 'intact':
                        old = np.load(OLD / 'core_v14/representations' / f'{tag}_{cohort}.npy')
                        equality[cohort] = bool(np.array_equal(array, old))
                        assert equality[cohort], ('intact replay differs', tag, cohort, float(np.max(np.abs(array - old))))
                write_json(ledger, dict(arm=arm, seed=seed, variant=variant, name=name,
                           encoder_buffer_sha256=buffer_hash, changed_parameter_names=changed,
                           checkpoint_sha256=sha(checkpoint), intact_replay_exact=equality,
                           script_sha256=sha(Path(__file__)), protocol_sha256=sha(ROOT / 'PROTOCOL_RU.md')))
                print('ENCODED', name, 'rewound', len(changed), flush=True)
                del net
                torch.cuda.empty_cache()
    ledgers = [json.loads(p.read_text()) for p in (out / 'ledgers').glob('*.json')]
    assert len(ledgers) == len(seeds) * len(arms) * len(VARIANTS)
    audit = []
    for seed in seeds:
        hashes = {r['encoder_buffer_sha256'] for r in ledgers if r['seed'] == seed}
        assert len(hashes) == 1, ('source arms have distinct buffer states', seed, hashes)
        for cohort in ['QAC105', 'OOD17']:
            reference = np.load(out / 'representations' / f'expert_seed{seed}__rewind_all_{cohort}.npy')
            for arm in arms:
                array = np.load(out / 'representations' / f'{arm}_seed{seed}__rewind_all_{cohort}.npy')
                assert np.array_equal(array, reference), (arm, seed, cohort)
            audit.append(dict(seed=seed, cohort=cohort, rewind_all_equal_across_arms=True))
    write_json(out / 'vector_status.json', dict(completed=True, smoke=args.smoke, configurations=len(ledgers) + 1,
               intact_all_exact=True, buffer_state_shared_within_seed=True, rewind_all_audit=audit))


def ablation_decode(args):
    setup(torch.device('cpu'))
    _, _, registry, qm, om, y, folds = read_data()
    ready = ROOT / 'ablation/vector_status.json'
    while not ready.exists() or not json.loads(ready.read_text()).get('completed'):
        print('WAITING ablation vectors', flush=True)
        time.sleep(15)
    configurations = [('raw-molformer', -1, 'raw', 'raw-molformer')]
    configurations += [(arm, seed, variant, f'{arm}_seed{seed}__{variant}') for arm in ft.ARMS
                       for seed in range(5) for variant in VARIANTS]
    out = ROOT / 'ablation'
    for index, (arm, seed, variant, name) in enumerate(configurations):
        if index % args.workers != args.worker:
            continue
        qx = np.load(out / 'representations' / f'{name}_QAC105.npy')
        ox = np.load(out / 'representations' / f'{name}_OOD17.npy')
        for schema, fold, tr, te, is_ood in iter_splits(folds):
            tag = f'{name}_{schema}_f{fold}'
            chunk = out / 'chunks' / (tag + '.csv')
            if chunk.exists() and chunk.with_suffix('.json').exists():
                continue
            start = time.time()
            # Match v14's concatenated species and endpoint one-hot indicators.
            task_metadata = np.array([[1, 0, 1, 0], [1, 0, 0, 1],
                                      [0, 1, 1, 0], [0, 1, 0, 1]], dtype=np.float32)
            xtr = np.hstack([np.repeat(qx[tr], 4, axis=0), np.tile(task_metadata, (len(tr), 1))])
            test = (ox if is_ood else qx)[te]
            xte = np.hstack([np.repeat(test, 4, axis=0), np.tile(task_metadata, (len(te), 1))])
            model = CatBoostRegressor(iterations=300, depth=5, learning_rate=.05, random_seed=1729,
                        thread_count=2, verbose=False, allow_writing_files=False)
            model.fit(xtr, y[tr].reshape(-1))
            pred = model.predict(xte).reshape(-1, 4)
            artifact = out / 'models' / (tag + '.cbm')
            artifact.parent.mkdir(parents=True, exist_ok=True)
            model.save_model(str(artifact))
            metadata = dict(arm=arm, seed=seed, variant=variant, schema=schema, fold=fold)
            result = registry_predictions(registry, pred, te, is_ood, metadata)
            write_json(chunk.with_suffix('.json'), dict(**metadata,
                       train_ids=qm.compound_id.iloc[tr].tolist(),
                       test_ids=(om if is_ood else qm).compound_id.iloc[te].tolist(),
                       seconds=time.time()-start, script_sha256=sha(Path(__file__)),
                       model_sha256=sha(artifact), protocol_sha256=sha(ROOT / 'PROTOCOL_RU.md')))
            csv(chunk, result)
            print('DECODED', tag, round(time.time()-start, 2), flush=True)
            if args.smoke:
                return
    write_json(out / 'status' / f'worker{args.worker}.json', dict(completed=True, worker=args.worker,
               completed_chunks=len(list((out / 'chunks').glob('*.csv'))), expected_total_fits=1331))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['direct', 'ablation-vectors', 'ablation-decode'])
    parser.add_argument('--worker', type=int, default=0)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    assert 0 <= args.worker < args.workers
    if args.smoke:
        # Smoke files never mix with final experiment ledgers.
        global ROOT
        original = ROOT
        ROOT = ROOT / ('smoke_' + args.action + '_' + str(args.worker))
        ROOT.mkdir(exist_ok=True)
        for name in ['data', 'PROTOCOL_RU.md']:
            if not (ROOT / name).exists():
                (ROOT / name).symlink_to(original / name)
    if args.action == 'direct':
        direct(args)
    elif args.action == 'ablation-vectors':
        ablation_vectors(args)
    else:
        ablation_decode(args)


if __name__ == '__main__':
    main()
