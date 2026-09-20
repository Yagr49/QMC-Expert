"""2x2 experiment: {frozen MolFormer, end-to-end fine-tuned} x {expert binary, quantitative MIC}.

All evaluation molecules are held out of every fine-tuning source (see data_prep.py),
so no representation has seen a test compound. Downstream heads are CatBoost on the
resulting embeddings, under scaffold-grouped CV. Null baselines (predict-the-mean and
six SwissADME-style descriptors) are reported alongside every cell.

Writes live state to progress.json and one line per finished run to runs.jsonl.
"""
import os, sys, json, time, math, argparse, warnings, traceback
# these must be set before torch is imported: the MPS fallback flag is read at import time
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
import numpy as np, pandas as pd, torch, torch.nn as nn
warnings.filterwarnings('ignore')

from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from catboost import CatBoostRegressor
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from rdkit.Chem import Descriptors

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = f'{HERE}/data'
PROG = f'{HERE}/progress.json'
RUNS = f'{HERE}/runs.jsonl'
REV = "7b12d946c181a37f6012b9dc3b002275de070314"
MODEL = "ibm/MoLFormer-XL-both-10pct"

SOURCES = {
    'expert-binary':  dict(task='binary', epochs=30, bs=32),
    'quant-molecule': dict(task='reg',    epochs=30, bs=32),
    'quant-record':   dict(task='reg',    epochs=10, bs=32),
}
EVALS = ['QAC-105', 'Q-HERO', 'OOD-17']
CB = dict(iterations=800, learning_rate=0.05, depth=6, verbose=0)

# ----------------------------------------------------------------- progress
_state = {'started': None, 'updated': None, 'stage': 'boot', 'done': 0, 'total': 0,
          'current': None, 'epoch': None, 'epochs': None, 'eta_s': None,
          'results': [], 'log': [], 'finished': False, 'error': None}


def emit(**kw):
    _state.update(kw)
    _state['updated'] = time.time()
    tmp = PROG + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(_state, f)
    os.replace(tmp, PROG)


def log(msg):
    line = f'{time.strftime("%H:%M:%S")}  {msg}'
    print(line, flush=True)
    _state['log'] = (_state['log'] + [line])[-40:]
    emit()


# ----------------------------------------------------------------- features
_DESC = ['MolWt', 'MolLogP', 'TPSA', 'NumRotatableBonds', 'NumHAcceptors', 'RingCount']


def descriptors(smis):
    out = []
    for s in smis:
        m = Chem.MolFromSmiles(s)
        out.append([getattr(Descriptors, d)(m) if m else np.nan for d in _DESC])
    return np.nan_to_num(np.array(out, dtype=float))


class Net(nn.Module):
    def __init__(self, enc, task):
        super().__init__()
        self.enc, self.task = enc, task
        self.drop = nn.Dropout(0.1)
        self.fc = nn.Linear(768, 1)

    def embed(self, **kw):
        return self.enc(**kw).pooler_output

    def forward(self, **kw):
        return self.fc(self.drop(self.embed(**kw))).squeeze(-1)


def load_backbone():
    from transformers import AutoModel
    return AutoModel.from_pretrained(MODEL, deterministic_eval=True,
                                     revision=REV, trust_remote_code=True)


def tok_all(tokenizer, smis, maxlen=202):
    return tokenizer(list(smis), padding='max_length', truncation=True,
                     max_length=maxlen, return_tensors='pt')


@torch.no_grad()
def embed_all(net, tokenizer, smis, dev, bs=64):
    net.eval()
    out = []
    for i in range(0, len(smis), bs):
        b = tok_all(tokenizer, smis[i:i + bs]).to(dev)
        out.append(net.embed(**b).float().cpu().numpy())
    return np.vstack(out)


def finetune(src_name, seed, tokenizer, dev):
    cfg = SOURCES[src_name]
    df = pd.read_csv(f'{DATA}/src_{src_name}.csv')
    torch.manual_seed(seed); np.random.seed(seed)

    gss = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=seed)
    tr, va = next(gss.split(df, groups=df.scaffold.values))
    dtr, dva = df.iloc[tr].reset_index(drop=True), df.iloc[va].reset_index(drop=True)

    net = Net(load_backbone(), cfg['task']).to(dev)
    # freeze embeddings + the bottom 4 encoder layers
    frozen = 0
    for n_, p in net.enc.named_parameters():
        if n_.startswith('embeddings') or any(f'layer.{i}.' in n_ for i in range(4)):
            p.requires_grad = False; frozen += p.numel()
    opt = torch.optim.AdamW([p for p in net.parameters() if p.requires_grad], lr=3e-5, weight_decay=0.01)
    lossf = nn.BCEWithLogitsLoss() if cfg['task'] == 'binary' else nn.MSELoss()

    Xtr = tok_all(tokenizer, dtr.can.values); ytr = torch.tensor(dtr.y.values, dtype=torch.float32)
    Xva = tok_all(tokenizer, dva.can.values); yva = torch.tensor(dva.y.values, dtype=torch.float32)
    n, bs = len(dtr), cfg['bs']
    steps = math.ceil(n / bs)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-5,
                                                total_steps=steps * cfg['epochs'], pct_start=0.1)
    best, best_state, patience, bad = np.inf, None, 6, 0
    t0 = time.time()
    for ep in range(cfg['epochs']):
        net.train()
        perm = torch.randperm(n)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            if len(idx) < 2:
                continue
            b = {k: v[idx].to(dev) for k, v in Xtr.items()}
            opt.zero_grad()
            loss = lossf(net(**b), ytr[idx].to(dev))
            loss.backward()
            torch.nn.utils.clip_grad_norm_([p for p in net.parameters() if p.requires_grad], 1.0)
            opt.step(); sched.step()
        net.eval()
        with torch.no_grad():
            vl, m = 0.0, 0
            for i in range(0, len(dva), 64):
                b = {k: v[i:i + 64].to(dev) for k, v in Xva.items()}
                p = net(**b)
                vl += lossf(p, yva[i:i + 64].to(dev)).item() * len(p); m += len(p)
            vl /= max(m, 1)
        el = time.time() - t0
        emit(epoch=ep + 1, epochs=cfg['epochs'],
             eta_s=el / (ep + 1) * (cfg['epochs'] - ep - 1))
        if vl < best - 1e-4:
            best, bad = vl, 0
            best_state = {k: v.detach().cpu().clone() for k, v in net.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                log(f'    early stop at epoch {ep+1} (val {best:.4f})')
                break
    if best_state:
        net.load_state_dict(best_state)
    log(f'    fine-tuned {src_name} seed={seed}: {len(dtr)} train / {len(dva)} val, '
        f'best val {best:.4f}, {frozen/1e6:.1f}M params frozen, {time.time()-t0:.0f}s')
    return net


# ----------------------------------------------------------------- evaluation
def cb_cv(X, y, groups, seed):
    kf = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    pred = np.zeros(len(y))
    for tr, te in kf.split(X, y, groups=groups):
        m = CatBoostRegressor(random_seed=seed, **CB); m.fit(X[tr], y[tr]); pred[te] = m.predict(X[te])
    return r2_score(y, pred), float(np.sqrt(mean_squared_error(y, pred)))


def cb_transfer(Xtr, ytr, Xte, yte, seed):
    m = CatBoostRegressor(random_seed=seed, **CB); m.fit(Xtr, ytr)
    p = m.predict(Xte)
    return r2_score(yte, p), float(np.sqrt(mean_squared_error(yte, p)))


def evaluate(tag, feats, evals, seed):
    """feats: dict eval_name -> embedding matrix."""
    rows = []
    for name in ['QAC-105', 'Q-HERO']:
        d = evals[name]
        r2, rmse = cb_cv(feats[name], d.y.values, d.scaffold.values, seed)
        rows.append(dict(representation=tag, seed=seed, target=name,
                         protocol='scaffold 5-fold CV', n=len(d), R2=r2, RMSE=rmse))
    q, o = evals['QAC-105'], evals['OOD-17']
    r2, rmse = cb_transfer(feats['QAC-105'], q.y.values, feats['OOD-17'], o.y.values, seed)
    rows.append(dict(representation=tag, seed=seed, target='OOD-17',
                     protocol='train on QAC-105', n=len(o), R2=r2, RMSE=rmse))
    return rows


def append_runs(rows):
    with open(RUNS, 'a') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    _state['results'] = (_state['results'] + rows)[-400:]
    emit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args()

    if a.smoke:
        for k in SOURCES:
            SOURCES[k]['epochs'] = 2
        a.seeds = 1

    from transformers import AutoTokenizer
    dev = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True, revision=REV)

    evals = {n: pd.read_csv(f'{DATA}/eval_{n}.csv') for n in EVALS}
    seeds = list(range(a.seeds))
    total = len(SOURCES) * len(seeds) + 2
    emit(started=time.time(), total=total, done=0, stage='baselines', finished=False,
         smoke=a.smoke, device=str(dev))
    open(RUNS, 'a').close()

    # ---- null baselines ----
    rows = []
    for name in ['QAC-105', 'Q-HERO']:
        d = evals[name]
        rows.append(dict(representation='predict-the-mean', seed=0, target=name,
                         protocol='scaffold 5-fold CV', n=len(d),
                         R2=r2_score(d.y, np.full(len(d), d.y.mean())),
                         RMSE=float(d.y.std())))
        r2, rmse = cb_cv(descriptors(d.can.values), d.y.values, d.scaffold.values, 0)
        rows.append(dict(representation='6 descriptors', seed=0, target=name,
                         protocol='scaffold 5-fold CV', n=len(d), R2=r2, RMSE=rmse))
    q, o = evals['QAC-105'], evals['OOD-17']
    rows.append(dict(representation='predict-the-mean', seed=0, target='OOD-17',
                     protocol='train on QAC-105', n=len(o),
                     R2=r2_score(o.y, np.full(len(o), q.y.mean())),
                     RMSE=float(np.sqrt(((o.y - q.y.mean()) ** 2).mean()))))
    r2, rmse = cb_transfer(descriptors(q.can.values), q.y.values,
                           descriptors(o.can.values), o.y.values, 0)
    rows.append(dict(representation='6 descriptors', seed=0, target='OOD-17',
                     protocol='train on QAC-105', n=len(o), R2=r2, RMSE=rmse))
    append_runs(rows)
    emit(done=1, stage='frozen MolFormer')
    log('null baselines done')

    # ---- frozen MolFormer ----
    net = Net(load_backbone(), 'reg').to(dev)
    frozen_feats = {n: embed_all(net, tokenizer, evals[n].can.values, dev) for n in EVALS}
    for s in seeds:
        append_runs(evaluate('MolFormer frozen', frozen_feats, evals, s))
    del net
    if dev.type == 'mps':
        torch.mps.empty_cache()
    emit(done=2)
    log('frozen MolFormer done')

    # ---- fine-tuned cells ----
    done = 2
    for src in SOURCES:
        for s in seeds:
            emit(stage=f'fine-tune {src}', current=f'{src} seed={s}', epoch=0,
                 epochs=SOURCES[src]['epochs'])
            log(f'  start {src} seed={s}')
            try:
                net = finetune(src, s, tokenizer, dev)
                feats = {n: embed_all(net, tokenizer, evals[n].can.values, dev) for n in EVALS}
                append_runs(evaluate(f'FT {src}', feats, evals, s))
                del net
                if dev.type == 'mps':
                    torch.mps.empty_cache()
            except Exception:
                log(f'  FAILED {src} seed={s}: {traceback.format_exc().splitlines()[-1]}')
            done += 1
            emit(done=done, epoch=None, eta_s=None)
    emit(stage='finished', finished=True, current=None)
    log('ALL DONE')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        emit(error=traceback.format_exc()[-2000:], finished=True, stage='error')
        raise
