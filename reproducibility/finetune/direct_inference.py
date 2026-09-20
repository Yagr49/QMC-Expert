"""Zero-shot inference: fine-tune on a source, then predict the test sets directly.

run_matrix.py discards the fine-tuned head and trains a fresh CatBoost on
target-domain data, which measures representation quality. This script keeps the
head: the model fine-tuned on a source predicts QAC-105, Q-HERO and OOD-17 with
nothing fitted on the target. That is the setting the manuscript's framing implies.

The quantitative sources and all three targets are log2 MIC in uM, so direct
regression transfers. The expert source emits a Good/Bad logit instead, so the two
arms are compared on rank agreement with the true MIC (Spearman) and on ROC-AUC
against MIC binarised at the target's median.

Controls: predict-the-training-mean, and frozen MolFormer with a CatBoost head
fitted on the same source (isolating the effect of fine-tuning itself).
"""
import os, sys, json, time, argparse, warnings, traceback
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
import numpy as np, pandas as pd, torch
warnings.filterwarnings('ignore')
from scipy.stats import spearmanr
from sklearn.metrics import r2_score, mean_squared_error, roc_auc_score
from catboost import CatBoostRegressor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_matrix as RM

DATA = f'{HERE}/data'
PROG = f'{HERE}/progress_direct.json'
RUNS = f'{HERE}/runs_direct.jsonl'
CKPT = f'{HERE}/checkpoints'; os.makedirs(CKPT, exist_ok=True)

_state = {'started': None, 'updated': None, 'stage': 'boot', 'done': 0, 'total': 0,
          'current': None, 'epoch': None, 'epochs': None, 'eta_s': None,
          'results': [], 'log': [], 'finished': False, 'error': None}


def emit(**kw):
    _state.update(kw); _state['updated'] = time.time()
    tmp = PROG + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(_state, f)
    os.replace(tmp, PROG)


def log(msg):
    line = f'{time.strftime("%H:%M:%S")}  {msg}'
    print(line, flush=True)
    _state['log'] = (_state['log'] + [line])[-40:]
    emit()


RM.emit = emit          # let the shared fine-tune loop report epochs here
RM.log = log


@torch.no_grad()
def predict(net, tokenizer, smis, dev, bs=64):
    net.eval()
    out = []
    for i in range(0, len(smis), bs):
        b = RM.tok_all(tokenizer, smis[i:i + bs]).to(dev)
        out.append(net(**b).float().cpu().numpy())
    return np.concatenate(out)


def score(tag, source, target_name, y, pred, kind, seed):
    """kind: 'reg' -> pred is log2 MIC; 'score' -> pred is a goodness logit."""
    rho = spearmanr(y, pred).statistic
    row = dict(representation=tag, source=source, seed=seed, target=target_name,
               n=len(y), kind=kind,
               spearman=float(rho),
               # a higher Good/Bad logit should mean a LOWER MIC
               rank_agreement=float(-rho if kind == 'score' else rho))
    if kind == 'reg':
        row['R2'] = float(r2_score(y, pred))
        row['RMSE'] = float(np.sqrt(mean_squared_error(y, pred)))
    else:
        row['R2'] = None; row['RMSE'] = None
    active = (y < np.median(y)).astype(int)          # below-median MIC = more active
    s = pred if kind == 'score' else -pred           # higher score = more active
    try:
        row['AUC'] = float(roc_auc_score(active, s))
    except Exception:
        row['AUC'] = None
    return row


def append(rows):
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
        for k in RM.SOURCES:
            RM.SOURCES[k]['epochs'] = 2
        a.seeds = 1

    from transformers import AutoTokenizer
    dev = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained(RM.MODEL, trust_remote_code=True, revision=RM.REV)
    evals = {n: pd.read_csv(f'{DATA}/eval_{n}.csv') for n in RM.EVALS}
    seeds = list(range(a.seeds))

    emit(started=time.time(), total=len(RM.SOURCES) * len(seeds) + 1, done=0,
         stage='controls', finished=False, device=str(dev), smoke=a.smoke)
    open(RUNS, 'a').close()

    # ---------- controls ----------
    rows = []
    net0 = RM.Net(RM.load_backbone(), 'reg').to(dev)
    frozen_eval = {n: RM.embed_all(net0, tokenizer, evals[n].can.values, dev) for n in RM.EVALS}
    for src in ['quant-molecule', 'quant-record']:
        df = pd.read_csv(f'{DATA}/src_{src}.csv')
        Xs = RM.embed_all(net0, tokenizer, df.can.values, dev)
        cb = CatBoostRegressor(random_seed=0, **RM.CB); cb.fit(Xs, df.y.values)
        for n in RM.EVALS:
            d = evals[n]
            rows.append(score('frozen MolFormer + CatBoost', src, n, d.y.values,
                              cb.predict(frozen_eval[n]), 'reg', 0))
        for n in RM.EVALS:
            d = evals[n]
            rows.append(score('predict source mean', src, n, d.y.values,
                              np.full(len(d), df.y.mean()), 'reg', 0))
    del net0
    if dev.type == 'mps':
        torch.mps.empty_cache()
    append(rows); emit(done=1, stage='fine-tune + direct inference')
    log('controls done')

    # ---------- fine-tune, then predict the targets directly ----------
    done = 1
    for src, cfg in RM.SOURCES.items():
        kind = 'score' if cfg['task'] == 'binary' else 'reg'
        for s in seeds:
            emit(current=f'{src} seed={s}', epoch=0, epochs=cfg['epochs'])
            log(f'  start {src} seed={s}')
            try:
                net = RM.finetune(src, s, tokenizer, dev)
                torch.save(net.state_dict(), f'{CKPT}/{src}_seed{s}.pt')
                rows = []
                for n in RM.EVALS:
                    d = evals[n]
                    p = predict(net, tokenizer, d.can.values, dev)
                    rows.append(score(f'FT {src} (direct)', src, n, d.y.values, p, kind, s))
                append(rows)
                for r in rows:
                    log(f'    {r["target"]:8s} rank_agr={r["rank_agreement"]:+.3f} '
                        f'AUC={r["AUC"]:.3f}' + (f' R2={r["R2"]:+.3f}' if r['R2'] is not None else ''))
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
