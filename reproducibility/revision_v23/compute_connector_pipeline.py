"""Real numbers for the section 2.2 pipeline figure.

Two frozen connectors (expert Good/Bad contrastive encoder; multi-regression encoder),
each feeding a multitask CatBoost with one-hot endpoint labels:

  trained       fitted on 80 in-domain compounds (molecule-level split of the 105 unique
                QACs in Data_biocides.xlsx)
    -> panel 1  in-domain test, the remaining compounds
    -> panel 2  out-of-domain, zero-shot, all 17 new compounds
  post-trained  refitted on those 80 + 6 randomly drawn out-of-domain compounds
    -> panel 3  the 11 out-of-domain compounds not drawn

Repeated over 20 seeds (split and draw). Metric: RMSE of log2 MIC/MBC (mg/L) per endpoint.
A predict-the-training-mean baseline is computed alongside every evaluation.
The OpenAI-encoded-label configuration is not reproduced: its cached label embeddings
are not on disk.
"""
from pathlib import Path
import os, pickle, json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, torch, torch.nn as nn
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from sklearn.model_selection import GroupShuffleSplit
from catboost import CatBoostRegressor

ROOT = Path(__file__).resolve().parent
D = Path('/Users/egorilin/Desktop'); V = D / 'Veresh_paper'; C = D / 'COMA'
OUT = ROOT / 'connector_pipeline_results.csv'
OUT_RES = ROOT / 'connector_pipeline_residuals.csv'
SEEDS = range(20); N_TRAIN = 80; N_POST = 6
EP = ['S. aureus MIC', 'S. aureus MBC', 'E. coli MIC', 'E. coli MBC']


def num(v):
    return float(str(v).replace('>', '').replace('<', '').strip())


# ---------------- data ----------------
tgt = pd.read_excel(V / 'Data_biocides.xlsx')
mf_in = pd.read_excel(V / 'Test_molformer_original_biocides.xlsx').drop(columns=['Unnamed: 0']).to_numpy(np.float32)
TC = [c for c in tgt.columns if 'Activity' in c]
assert len(TC) == 4 and len(mf_in) == len(tgt)
can = tgt['General formula'].map(lambda s: Chem.MolToSmiles(Chem.MolFromSmiles(s)) if Chem.MolFromSmiles(str(s)) else s)
Y_in = np.log2(tgt[TC].applymap(num).to_numpy(float))

ood = pd.read_excel(V / 'QACs_SMILES_MIC_MBC.xlsx', 'Лист1')
mf_ood = pd.read_excel(V / 'Test_molformer_ood.xlsx').drop(columns=['Unnamed: 0']).to_numpy(np.float32)
Y_ood = np.log2(ood[['MIC Sa', 'MBC Sa', 'MIC Ec', 'MBC Ec']].applymap(num).to_numpy(float))
assert len(mf_ood) == len(ood) == 17


# ---------------- frozen connectors ----------------
class Enc(nn.Module):
    def __init__(s, inp=768, h=(512, 384, 256), pd_=128, dr=0.3):
        super().__init__(); L = []; p = inp
        for d in h:
            L += [nn.Linear(p, d), nn.BatchNorm1d(d), nn.ReLU(), nn.Dropout(dr)]; p = d
        s.encoder = nn.Sequential(*L)
        s.projection_head = nn.Sequential(nn.Linear(h[-1], pd_), nn.BatchNorm1d(pd_), nn.ReLU(),
                                          nn.Dropout(dr * .5), nn.Linear(pd_, pd_), nn.BatchNorm1d(pd_))

    def forward(s, x):
        return s.encoder(x)


sc = pickle.load(open(V / 'scaler_classification.pkl', 'rb'))


def connector(path):
    e = Enc(); e.load_state_dict(torch.load(path, map_location='cpu')); e.eval()
    with torch.no_grad():
        return (e(torch.FloatTensor(sc.transform(mf_in))).numpy(),
                e(torch.FloatTensor(sc.transform(mf_ood))).numpy())


ARMS = {'intuition': connector(V / 'encoder_borderline_smote.pth'),
        'data': connector(C / 'analysis' / 'encoder_reg_only.pth')}


def long(E, Y, rows, ids=None):
    X, y, ep, cid = [], [], [], []
    for i in rows:
        for j in range(4):
            if np.isfinite(Y[i, j]):
                X.append(np.concatenate([E[i], np.eye(4)[j]])); y.append(Y[i, j]); ep.append(j)
                cid.append(ids[i] if ids is not None else i)
    long.cid = np.array(cid)
    return np.array(X), np.array(y), np.array(ep)


res = []


def keep(seed, arm, panel, y, p, ep):
    for c, j, e in zip(long.cid, ep, np.abs(y - p)):
        res.append(dict(seed=seed, arm=arm, panel=panel, compound=c, endpoint=EP[j], abs_err=float(e)))


def rmse_by_ep(y, p, ep):
    return {EP[j]: float(np.sqrt(np.mean((y[ep == j] - p[ep == j]) ** 2))) for j in range(4)}


rows = []
groups = can.values
for s in SEEDS:
    gss = GroupShuffleSplit(n_splits=1, train_size=N_TRAIN, random_state=s)
    tr_g, te_g = next(gss.split(np.zeros(len(groups)), groups=groups))
    rng = np.random.default_rng(1000 + s)
    post = rng.choice(17, N_POST, replace=False)
    rest = np.setdiff1d(np.arange(17), post)
    for arm, (E_in, E_ood) in ARMS.items():
        Xtr, ytr, eptr = long(E_in, Y_in, tr_g)
        m = CatBoostRegressor(iterations=600, learning_rate=0.05, depth=6, random_seed=s, verbose=0)
        m.fit(Xtr, ytr)
        mean_ep = {j: ytr[eptr == j].mean() for j in range(4)}

        for panel, (E, Y, idx, ids) in {'in-domain test': (E_in, Y_in, te_g, can.values),
                                        'out-of-domain zero-shot': (E_ood, Y_ood, np.arange(17), None)}.items():
            X, y, ep = long(E, Y, idx, ids)
            pr = m.predict(X); keep(s, arm, panel, y, pr, ep)
            if arm == 'intuition':
                keep(s, 'mean baseline', panel, y, np.array([mean_ep[j] for j in ep]), ep)
            for k, v in rmse_by_ep(y, pr, ep).items():
                rows.append(dict(seed=s, arm=arm, panel=panel, endpoint=k, rmse=v))
            for k, v in rmse_by_ep(y, np.array([mean_ep[j] for j in ep]), ep).items():
                rows.append(dict(seed=s, arm='mean baseline', panel=panel, endpoint=k, rmse=v))

        Xp, yp, epp = long(E_ood, Y_ood, post)
        m2 = CatBoostRegressor(iterations=600, learning_rate=0.05, depth=6, random_seed=s, verbose=0)
        m2.fit(np.vstack([Xtr, Xp]), np.concatenate([ytr, yp]))
        X, y, ep = long(E_ood, Y_ood, rest)
        pr2 = m2.predict(X); keep(s, arm, 'out-of-domain post-trained', y, pr2, ep)
        for k, v in rmse_by_ep(y, pr2, ep).items():
            rows.append(dict(seed=s, arm=arm, panel='out-of-domain post-trained', endpoint=k, rmse=v))
        ally = np.concatenate([ytr, yp]); allep = np.concatenate([eptr, epp])
        mean2 = {j: ally[allep == j].mean() for j in range(4)}
        if arm == 'intuition':
            keep(s, 'mean baseline', 'out-of-domain post-trained', y, np.array([mean2[j] for j in ep]), ep)
        for k, v in rmse_by_ep(y, np.array([mean2[j] for j in ep]), ep).items():
            rows.append(dict(seed=s, arm='mean baseline', panel='out-of-domain post-trained', endpoint=k, rmse=v))
    print(f'seed {s}: train {len(tr_g)} cpds, test {len(te_g)}, post-train draw {sorted(post.tolist())}', flush=True)

df = pd.DataFrame(rows)
df = df.drop_duplicates(['seed', 'arm', 'panel', 'endpoint'])   # baseline is arm-independent
df.to_csv(OUT, index=False)
pd.DataFrame(res).to_csv(OUT_RES, index=False)
print('\n', df.groupby(['panel', 'endpoint', 'arm']).rmse.median().unstack().round(2).to_string())
