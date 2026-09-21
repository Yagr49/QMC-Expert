import os,sys
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK','1'); os.environ.setdefault('HF_HUB_OFFLINE','1')
import numpy as np,pandas as pd,torch,warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import run_matrix as RM
from direct_inference import predict
from transformers import AutoTokenizer
HERE=os.path.dirname(os.path.abspath(__file__))
dev=torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
tokz=AutoTokenizer.from_pretrained(RM.MODEL,trust_remote_code=True,revision=RM.REV)
evals={n:pd.read_csv(f'{HERE}/data/eval_{n}.csv') for n in RM.EVALS}
out=[]
for src in ['quant-record','expert-binary']:
    net=RM.Net(RM.load_backbone(),'reg' if src.startswith('quant') else 'binary').to(dev)
    net.load_state_dict(torch.load(f'{HERE}/checkpoints/{src}_seed0.pt',map_location=dev)); net.eval()
    for n in RM.EVALS:
        d=evals[n]
        out.append(pd.DataFrame(dict(source=src,target=n,can=d.can.values,
                                     y=d.y.values,pred=predict(net,tokz,d.can.values,dev))))
    del net
    if dev.type=='mps': torch.mps.empty_cache()
pd.concat(out).to_csv(f'{HERE}/predictions_seed0.csv',index=False)
print('wrote predictions_seed0.csv')
