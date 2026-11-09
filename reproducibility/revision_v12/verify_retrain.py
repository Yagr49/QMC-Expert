"""Compare one full independent retrain with the original human seed 0."""
import run_matched_finetuning as ft
from pathlib import Path
import json
import pandas as pd
import numpy as np
import torch
ROOT=Path(__file__).resolve().parent

def main():
    original=ROOT/'results';repeat=ROOT/'independent_retrain'
    assert json.loads((repeat/'manifest.json').read_text())['completed']
    a=torch.load(original/'checkpoints/expert_seed0.pt',map_location='cpu',weights_only=False)
    b=torch.load(repeat/'checkpoints/expert_seed0.pt',map_location='cpu',weights_only=False)
    assert set(a['state_dict'])==set(b['state_dict'])
    maximum=max(float((a['state_dict'][key]-b['state_dict'][key]).abs().max()) for key in a['state_dict'])
    comparisons={}
    for name,fields in [('predictions',['y','pred']),('direct_predictions',['y','score','rank_score'])]:
        x=pd.read_csv(original/(name+'.csv'));x=x[(x.arm=='expert')&(x.seed==0)].sort_values(['target','can']).reset_index(drop=True)
        y=pd.read_csv(repeat/(name+'.csv'));y=y[(y.arm=='expert')&(y.seed==0)].sort_values(['target','can']).reset_index(drop=True)
        assert x.can.tolist()==y.can.tolist() and x.target.tolist()==y.target.tolist()
        comparisons[name]=float(np.max(np.abs(x[fields].values-y[fields].values)))
    features={}
    for target in ft.TARGETS:
        x=np.load(original/'representations'/f'expert_seed0_{target}.npy')
        y=np.load(repeat/'representations'/f'expert_seed0_{target}.npy')
        features[target]=float(np.max(np.abs(x-y)))
    x=pd.read_csv(original/'training.csv').query("arm == 'expert' and seed == 0").iloc[0]
    y=pd.read_csv(repeat/'training.csv').iloc[0]
    for field in ['initial_sha256','batch_order_sha256','train_id_sha256','updates']:assert x[field]==y[field]
    report=dict(passed=maximum<=1e-6 and max(comparisons.values())<=1e-6 and max(features.values())<=1e-6,
        scope='one full 30-epoch human seed 0 retrain; same GPU and pinned environment; no portability claim',
        max_parameter_difference=maximum,max_prediction_differences=comparisons,max_feature_differences=features,
        paired_identity_initialisation_and_batches=True,script_sha256=ft.sha(__file__))
    assert report['passed'];ft.write_json(ROOT/'independent_retrain_validation.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
