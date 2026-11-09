"""Matched source-supervision interventions; fixed final partial-FT checkpoint."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('OMP_NUM_THREADS', '4')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '4')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
os.environ.setdefault('HF_HOME', str(ROOT / 'runtime' / 'hf'))
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import sys
# Isolated optional server libraries, with the server's existing torch installation.
if (ROOT / 'deps').exists(): sys.path.insert(0, str(ROOT / 'deps'))
if Path('/home/yagr/.local/lib/python3.12/site-packages').exists():
    sys.path.append('/home/yagr/.local/lib/python3.12/site-packages')
sys.modules['torchvision'] = None
import argparse, hashlib, json, math, time, platform, traceback, multiprocessing
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from scipy.stats import spearmanr
from catboost import CatBoostRegressor
from transformers import AutoTokenizer, AutoModel

MODEL = 'ibm/MoLFormer-XL-both-10pct'
REVISION = '7b12d946c181a37f6012b9dc3b002275de070314'
ARMS = ['expert', 'quant-continuous', 'quant-binary', 'expert-shuffled',
        'quant-shuffled', 'quant-binary-shuffled']
TARGETS = ['QAC-104', 'Q-HERO-405', 'OOD-17']


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def object_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
def weights_sha(net):
    h = hashlib.sha256()
    for name, tensor in net.state_dict().items():
        h.update(name.encode()); h.update(tensor.detach().cpu().numpy().tobytes())
    return h.hexdigest()
def write_json(path, value):
    tmp = Path(str(path) + '.tmp'); tmp.write_text(json.dumps(value, indent=2, default=str)); tmp.replace(path)


class Net(nn.Module):
    def __init__(self, backbone):
        super().__init__(); self.enc = backbone; self.drop = nn.Dropout(.1); self.fc = nn.Linear(768, 1)
    def embed(self, **kw): return self.enc(**kw).pooler_output
    def forward(self, **kw): return self.fc(self.drop(self.embed(**kw))).squeeze(-1)


def load_net(seed, device):
    torch.manual_seed(seed); np.random.seed(seed)
    enc, loading = AutoModel.from_pretrained(MODEL, revision=REVISION,
        code_revision=REVISION, trust_remote_code=True, deterministic_eval=True,
        output_loading_info=True)
    # AutoModel intentionally omits the pretrained masked-language-model head.
    allowed_unused = {'lm_head.decoder.weight', 'lm_head.transform.LayerNorm.bias',
        'lm_head.transform.LayerNorm.weight', 'lm_head.transform.dense.bias',
        'lm_head.transform.dense.weight'}
    if (loading['missing_keys'] or set(loading['unexpected_keys']) - allowed_unused
            or loading['mismatched_keys'] or loading.get('error_msgs')):
        raise RuntimeError(('backbone loading mismatch', loading))
    for module in enc.modules():
        if hasattr(module, 'deterministic'): module.deterministic = True
    net = Net(enc)
    for name, p in net.enc.named_parameters():
        if name.startswith('embeddings') or any(f'layer.{i}.' in name for i in range(4)):
            p.requires_grad = False
    return net.to(device), loading


def tokenise(tokenizer, smiles):
    return tokenizer(list(smiles), padding='max_length', truncation=False,
                     max_length=202, return_tensors='pt')


@torch.no_grad()
def outputs(net, tokens, device, batch_size=32):
    net.eval(); reps = []; scores = []
    for start in range(0, len(tokens['input_ids']), batch_size):
        batch = {k: v[start:start + batch_size].to(device) for k, v in tokens.items()}
        emb = net.embed(**batch)
        reps.append(emb.float().cpu().numpy()); scores.append(net.fc(emb).squeeze(-1).float().cpu().numpy())
    return np.vstack(reps), np.concatenate(scores)


def decoder_predict(xtr, ytr, xte):
    model = CatBoostRegressor(iterations=300, depth=5, learning_rate=.05,
        random_seed=1729, thread_count=4, verbose=False, allow_writing_files=False)
    model.fit(xtr, ytr); return model.predict(xte)


def evaluate(reps, targets, folds):
    result = {}
    for name in TARGETS[:2]:
        d = targets[name]; pred = np.zeros(len(d))
        for tr, te in folds[name]:
            pred[te] = decoder_predict(reps[name][tr], d.y.values[tr], reps[name][te])
        result[name] = pred
    result['OOD-17'] = decoder_predict(reps['QAC-104'], targets['QAC-104'].y.values, reps['OOD-17'])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--seeds', type=int, default=5)
    parser.add_argument('--arms', nargs='+', choices=ARMS, default=ARMS)
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if args.smoke: args.epochs = 1; args.seeds = 1
    out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    if (out / 'metrics.csv').exists(): raise RuntimeError('Use a fresh output directory; existing results are immutable.')
    (out / 'representations').mkdir(exist_ok=True); (out / 'checkpoints').mkdir(exist_ok=True)
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device(args.device)
    if device.type == 'cuda': torch.cuda.set_per_process_memory_fraction(.70)
    data = ROOT / 'data'
    expert = pd.read_csv(data / 'matched-pooled_expert.csv')
    quant = pd.read_csv(data / 'matched-pooled_quant.csv')
    targets = {n: pd.read_csv(data / f'target_{n}.csv') for n in TARGETS}
    for col in ['can', 'cation', 'scaffold']: assert expert[col].tolist() == quant[col].tolist()
    assert expert.can.is_unique and len(expert) == 681
    target_cations = set().union(*(set(d.cation) for d in targets.values()))
    assert not set(expert.cation) & target_cations
    tr, va = next(GroupShuffleSplit(n_splits=1, test_size=.15, random_state=1729).split(expert, groups=expert.scaffold))
    assert (len(tr), len(va)) == (377, 304)
    assert not set(expert.scaffold.iloc[tr]) & set(expert.scaffold.iloc[va])
    split = expert[['can', 'cation', 'scaffold']].copy(); split['partition'] = 'validation'; split.loc[tr, 'partition'] = 'train'
    split.to_csv(out / 'source_split.csv', index=False)
    assignments = pd.read_csv(data / 'target_folds.csv'); folds = {}
    for name in TARGETS[:2]:
        d = targets[name]; f = assignments[assignments.target == name].set_index('can')
        assert f.index.is_unique and set(f.index) == set(d.can)
        labels = f.loc[d.can, 'fold'].values
        folds[name] = [(np.flatnonzero(labels != k), np.flatnonzero(labels == k)) for k in sorted(set(labels))]
        for train, test in folds[name]: assert not set(d.scaffold.iloc[train]) & set(d.scaffold.iloc[test])
    (out / 'target_folds.csv').write_bytes((data / 'target_folds.csv').read_bytes())
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION,
        code_revision=REVISION, trust_remote_code=True)
    tokenizer.padding_side = 'right'
    lengths = {name: [len(v) for v in tokenizer(list(d.can), truncation=False)['input_ids']]
               for name, d in dict(source=expert, **targets).items()}
    assert max(max(v) for v in lengths.values()) <= 202
    tok_source = tokenise(tokenizer, expert.can)
    tok_targets = {name: tokenise(tokenizer, d.can) for name, d in targets.items()}
    tokens_tr = {k: v[tr] for k, v in tok_source.items()}; tokens_va = {k: v[va] for k, v in tok_source.items()}
    import transformers, sklearn, catboost, scipy
    manifest = dict(model=MODEL, revision=REVISION, remote_code_revision=REVISION,
        device=str(device), gpu=torch.cuda.get_device_name() if device.type == 'cuda' else None,
        python=platform.python_version(), packages=dict(torch=torch.__version__, numpy=np.__version__,
            pandas=pd.__version__, transformers=transformers.__version__, sklearn=sklearn.__version__,
            catboost=catboost.__version__, scipy=scipy.__version__),
        script_sha256=sha(__file__), protocol_sha256=sha(ROOT / 'PROTOCOL.md'),
        input_sha256={p.name: sha(p) for p in data.glob('*.csv')},
        seeds=args.seeds, epochs=args.epochs, batch_size=32, steps_per_epoch=math.ceil(len(tr) / 32),
        arms=args.arms, smoke=args.smoke, train_n=len(tr), validation_n=len(va),
        source_n=len(expert), source_groups=expert.scaffold.nunique(),
        target_n={n: len(d) for n, d in targets.items()},
        target_scaffolds={n: d.scaffold.nunique() for n, d in targets.items()},
        max_tokens={n: max(v) for n, v in lengths.items()}, truncated=0,
        source_target_cation_overlap=0, checkpoint_policy='final; fixed budget; diagnostic validation only',
        decoder=dict(iterations=300, depth=5, learning_rate=.05, random_seed=1729),
        started=time.time(), completed=False)
    write_json(out / 'manifest.json', manifest)
    progress = dict(started=time.time(), done=0, total=args.seeds * len(args.arms), completed=False)
    def emit(**values): progress.update(values); progress['updated'] = time.time(); write_json(out / 'progress.json', progress)
    metrics = []; predictions = []; direct_metrics = []; direct_predictions = []; training = []; epochs = []
    def flush():
        for name, rows in [('metrics', metrics), ('predictions', predictions), ('direct_metrics', direct_metrics),
                           ('direct_predictions', direct_predictions), ('training', training), ('epochs', epochs)]:
            if rows: pd.DataFrame(rows).to_csv(out / f'{name}.csv', index=False)
    def record(arm, seed, reps=None, pp=None):
        if pp is None: pp = evaluate(reps, targets, folds)
        for name, pred in pp.items():
            d = targets[name]
            assert np.isfinite(pred).all()
            metrics.append(dict(panel='matched-pooled-ft', arm=arm, seed=seed, head='catboost', target=name,
                n=len(d), R2=r2_score(d.y, pred), RMSE=np.sqrt(mean_squared_error(d.y, pred))))
            predictions.extend(dict(panel='matched-pooled-ft', arm=arm, seed=seed, head='catboost',
                target=name, can=d.can.iloc[i], scaffold=d.scaffold.iloc[i], y=float(d.y.iloc[i]), pred=float(pred[i]))
                for i in range(len(d)))
        flush()
        print('RESULT', arm, seed, [(r['target'], round(r['RMSE'], 4)) for r in metrics[-3:]], flush=True)
    emit(stage='raw backbone')
    net, loading = load_net(0, device)
    manifest['parameters'] = sum(p.numel() for p in net.enc.parameters())
    manifest['trainable_parameters_including_head'] = sum(p.numel() for p in net.parameters() if p.requires_grad)
    manifest['trainable_names'] = [name for name, p in net.named_parameters() if p.requires_grad]
    manifest['backbone_loading'] = loading
    write_json(out / 'manifest.json', manifest)
    raw = {n: outputs(net, t, device)[0] for n, t in tok_targets.items()}
    for name, emb in raw.items(): np.save(out / 'representations' / f'raw-molformer_{name}.npy', emb)
    record('raw-molformer', 0, raw)
    del net; torch.cuda.empty_cache() if device.type == 'cuda' else None
    # Decoder fitting never feeds information back into source training. A single
    # independent CPU worker overlaps this fixed evaluation with the next GPU run.
    pool = ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context('spawn'))
    pending = []
    for seed in range(args.seeds):
        for arm in args.arms:
            emit(stage='training', arm=arm, seed=seed, epoch=0)
            started = time.time(); net, loading = load_net(seed, device); initial_hash = weights_sha(net)
            binary = arm.startswith('expert') or arm.startswith('quant-binary')
            y = (expert.y if arm.startswith('expert') else quant.y).values.astype('float32').copy()
            cutoff = None; mu = 0.; sd = 1.
            if arm.startswith('quant-binary'):
                cutoff = float(np.quantile(y[tr], float(expert.y.iloc[tr].mean())))
                y = (y <= cutoff).astype('float32')
            if not binary: mu = float(y[tr].mean()); sd = max(float(y[tr].std()), 1e-6); y = (y - mu) / sd
            before = y[tr].copy()
            if arm.endswith('shuffled'): y[tr] = np.random.default_rng(100000 + seed).permutation(y[tr])
            assert np.array_equal(np.sort(before), np.sort(y[tr]))
            torch.manual_seed(300000 + seed)
            params = [p for p in net.parameters() if p.requires_grad]
            opt = torch.optim.AdamW(params, lr=3e-5, weight_decay=.01)
            scheduler = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-5,
                total_steps=manifest['steps_per_epoch'] * args.epochs, pct_start=.1)
            lossfn = nn.BCEWithLogitsLoss() if binary else nn.MSELoss()
            yt = torch.tensor(y[tr], dtype=torch.float32, device=device)
            yv = torch.tensor(y[va], dtype=torch.float32, device=device)
            generator = torch.Generator().manual_seed(200000 + seed)
            batches_hash = hashlib.sha256(); updates = 0
            for epoch in range(args.epochs):
                net.train(); order = torch.randperm(len(tr), generator=generator)
                batches_hash.update(order.numpy().tobytes()); train_loss = 0.
                for start in range(0, len(tr), 32):
                    idx = order[start:start + 32]; batch = {k: v[idx].to(device) for k, v in tokens_tr.items()}
                    opt.zero_grad(set_to_none=True); loss = lossfn(net(**batch), yt[idx.to(device)])
                    if not torch.isfinite(loss): raise RuntimeError(('nonfinite training loss', arm, seed, epoch))
                    loss.backward(); torch.nn.utils.clip_grad_norm_(params, 1.)
                    opt.step(); scheduler.step(); updates += 1; train_loss += float(loss.detach()) * len(idx)
                net.eval(); validation_loss = 0.
                with torch.no_grad():
                    for start in range(0, len(va), 32):
                        batch = {k: v[start:start + 32].to(device) for k, v in tokens_va.items()}
                        pred = net(**batch); validation_loss += float(lossfn(pred, yv[start:start + 32])) * len(pred)
                epochs.append(dict(arm=arm, seed=seed, epoch=epoch + 1, updates=updates,
                    train_loss=train_loss / len(tr), val_loss=validation_loss / len(va),
                    seconds=time.time() - started, learning_rate=opt.param_groups[0]['lr']))
                pd.DataFrame(epochs).to_csv(out / 'epochs.csv', index=False)
                emit(epoch=epoch + 1, updates=updates, seconds=time.time() - started)
                if epoch == 0 or (epoch + 1) % 5 == 0:
                    print('EPOCH', arm, seed, epoch + 1, round(train_loss / len(tr), 5),
                          round(validation_loss / len(va), 5), round(time.time() - started, 1), flush=True)
            emit(stage='extract and decode')
            reps = {}; scores = {}
            for name, tokens in tok_targets.items():
                reps[name], scores[name] = outputs(net, tokens, device)
                assert np.isfinite(reps[name]).all() and np.isfinite(scores[name]).all()
                np.save(out / 'representations' / f'{arm}_seed{seed}_{name}.npy', reps[name])
                d = targets[name]; p = scores[name] if binary else scores[name] * sd + mu
                rho = float(spearmanr(d.y, p).statistic); agreement = -rho if binary else rho
                active = (d.y.values < np.median(d.y.values)).astype(int)
                direct_metrics.append(dict(arm=arm, seed=seed, target=name, n=len(d), kind='binary' if binary else 'continuous',
                    rank_agreement=agreement, AUC=roc_auc_score(active, p if binary else -p),
                    R2=None if binary else r2_score(d.y, p), RMSE=None if binary else np.sqrt(mean_squared_error(d.y, p))))
                direct_predictions.extend(dict(arm=arm, seed=seed, target=name, can=d.can.iloc[i],
                    scaffold=d.scaffold.iloc[i], y=float(d.y.iloc[i]), score=float(p[i]),
                    rank_score=float(-p[i] if binary else p[i])) for i in range(len(d)))
            checkpoint = out / 'checkpoints' / f'{arm}_seed{seed}.pt'
            # Frozen parameters are reconstructed from the immutable pretrained checkpoint.
            torch.save(dict(state_dict={n: p.detach().cpu() for n, p in net.named_parameters() if p.requires_grad},
                arm=arm, seed=seed, model=MODEL, revision=REVISION, target_mean=mu, target_sd=sd,
                binary_cutoff=cutoff, epochs=args.epochs, updates=updates), checkpoint)
            training.append(dict(arm=arm, seed=seed, train_n=len(tr), val_n=len(va),
                epochs=args.epochs, updates=updates, initial_sha256=initial_hash,
                batch_order_sha256=batches_hash.hexdigest(), train_id_sha256=object_sha(expert.can.iloc[tr].tolist()),
                label_sha256=hashlib.sha256(y[tr].tobytes()).hexdigest(),
                positive_prevalence=float(y[tr].mean()) if binary else None,
                cutoff=cutoff, target_mean=mu, target_sd=sd, checkpoint_sha256=sha(checkpoint),
                checkpoint_file=str(checkpoint), seconds=time.time() - started,
                final_train_loss=epochs[-1]['train_loss'], final_val_loss=epochs[-1]['val_loss']))
            del net, opt, scheduler, params; torch.cuda.empty_cache() if device.type == 'cuda' else None
            pending.append((arm, seed, pool.submit(evaluate, reps, targets, folds)))
            flush(); emit(done=progress['done'] + 1, pending_decoders=len(pending))
            still_pending = []
            for tag, paired_seed, future in pending:
                if future.done(): record(tag, paired_seed, pp=future.result())
                else: still_pending.append((tag, paired_seed, future))
            pending = still_pending
    emit(stage='finish fixed target decoders', pending_decoders=len(pending))
    for arm, seed, future in pending: record(arm, seed, pp=future.result())
    pool.shutdown()
    flush(); manifest['completed'] = True; manifest['finished'] = time.time()
    manifest['output_sha256'] = {p.name: sha(p) for p in out.glob('*.csv')}
    write_json(out / 'manifest.json', manifest); emit(stage='complete', completed=True)


if __name__ == '__main__':
    main()
