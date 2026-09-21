"""How much of the failure is calibration rather than signal?

Refits a single affine map (a + b*pred) on each target and reports the R2 that
recovers. Two intercept/slope parameters cannot create rank information, so any
recovered R2 was already present in the ordering and was lost to scale and offset.
"""
import os, sys, json
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK','1'); os.environ.setdefault('HF_HUB_OFFLINE','1')
import numpy as np, pandas as pd, torch, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import run_matrix as RM
from direct_inference import predict
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import r2_score
from transformers import AutoTokenizer

HERE=os.path.dirname(os.path.abspath(__file__))
dev=torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
tokz=AutoTokenizer.from_pretrained(RM.MODEL,trust_remote_code=True,revision=RM.REV)
evals={n:pd.read_csv(f'{HERE}/data/eval_{n}.csv') for n in RM.EVALS}
rows=[]
for src in ['quant-molecule','quant-record']:
    for seed in range(3):
        ck=f'{HERE}/checkpoints/{src}_seed{seed}.pt'
        if not os.path.exists(ck): continue
        net=RM.Net(RM.load_backbone(),'reg').to(dev)
        net.load_state_dict(torch.load(ck,map_location=dev)); net.eval()
        for n in RM.EVALS:
            d=evals[n]; y=d.y.values
            p=predict(net,tokz,d.can.values,dev)
            b,a=np.polyfit(p,y,1)
            rows.append(dict(source=src,seed=seed,target=n,
                             raw_R2=r2_score(y,p),
                             recal_R2=r2_score(y,a+b*p),
                             pearson=pearsonr(y,p).statistic,
                             spearman=spearmanr(y,p).statistic,
                             slope=b, intercept=a,
                             pred_mean=float(p.mean()), true_mean=float(y.mean()),
                             pred_sd=float(p.std()), true_sd=float(y.std())))
        del net
        if dev.type=='mps': torch.mps.empty_cache()
        print(f'  {src} seed{seed} done',flush=True)
df=pd.DataFrame(rows); df.to_csv(f'{HERE}/recalibration.csv',index=False)
g=df.groupby(['source','target'])[['raw_R2','recal_R2','pearson','spearman','slope','pred_mean','true_mean','pred_sd','true_sd']].mean()
print(); print(g.round(3).to_string())
