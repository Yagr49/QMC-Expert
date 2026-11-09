"""Reload all final-OOD target checkpoints and independently replay predictions."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from bootstrap import ENV, PYTHON

ROOT = Path(__file__).resolve().parent
if '--launch' in sys.argv:
    environment = dict(os.environ)
    for key in ['OPENAI_API_KEY','OPENROUTER_API_KEY','ANTHROPIC_API_KEY','MOONSHOT_API_KEY']:
        environment.pop(key,None)
    args = ['systemd-run','--user','--collect','--unit','coma-ftcausal-20261012-verify',
        '--property','WorkingDirectory='+str(ROOT),
        '--property','StandardOutput=append:'+str(ROOT/'logs/verify.log'),
        '--property','StandardError=append:'+str(ROOT/'logs/verify.log')]
    for key,value in ENV.items():
        args += ['--setenv',key+'='+value]
    args += [PYTHON,'-s',str(Path(__file__).resolve())]
    subprocess.run(args,check=True,env=environment)
    sys.exit(0)

import run_experiments as experiment
import numpy as np
import pandas as pd
import torch

while len(list((ROOT/'direct/chunks').glob('*.csv'))) < 363:
    time.sleep(15)
device = torch.device('cuda')
experiment.setup(device)
_,_,registry,qm,om,_,_ = experiment.read_data()
tokenizer = experiment.ft.AutoTokenizer.from_pretrained(experiment.ft.MODEL,
    revision=experiment.ft.REVISION,code_revision=experiment.ft.REVISION,trust_remote_code=True)
tokenizer.padding_side = 'right'
tokens = experiment.ft.tokenise(tokenizer,om.can)
raw = np.load(experiment.OLD/'core_v14/representations/raw-molformer_OOD17.npy')
records = []
for path in sorted((ROOT/'direct/checkpoints').glob('*_full-QAC105_f-1.pt')):
    saved = torch.load(path,map_location='cpu',weights_only=False)
    meta = saved['metadata']
    assert saved['includes_all_buffers'] and saved['retains_all_trainable_parameters']
    net,_ = experiment.restored_net(meta['arm'],meta['seed'],device)
    seed = experiment.seed_code(meta['seed'],meta['schema'],meta['fold'])
    model = experiment.TargetModel(net.enc,meta['mode'],seed).to(device)
    del net
    live = model.state_dict()
    auxiliary = {n:t for n,t in saved['state_dict'].items() if n not in live}
    result = model.load_state_dict({n:t for n,t in saved['state_dict'].items() if n in live},strict=False)
    frozen = {n for n,p in model.named_parameters() if not p.requires_grad}
    assert not result.unexpected_keys and set(result.missing_keys).issubset(frozen)
    buffers = dict(model.named_buffers())
    assert set(auxiliary).issubset(buffers)
    with torch.no_grad():
        for name,value in auxiliary.items():
            buffers[name].copy_(value.to(device=buffers[name].device,dtype=buffers[name].dtype))
    assert experiment.tensor_sha(dict(model.enc.named_parameters())) == saved['final_encoder_sha256']
    model.eval()
    with torch.no_grad():
        if meta['mode'] in ['linear','compact']:
            pred = model.from_features(torch.tensor(raw,dtype=torch.float32,device=device)).cpu().numpy()
        else:
            pred = model(**{key:value.to(device) for key,value in tokens.items()}).cpu().numpy()
    pred = pred*saved['sd']+saved['mean']
    replay = experiment.registry_predictions(registry,pred,np.arange(17),True,meta)
    old = pd.read_csv(ROOT/'direct/chunks'/(path.stem+'.csv'))
    merged = replay.merge(old,on=['cohort','compound_id','task'],suffixes=['_replay','_saved'],validate='one_to_one')
    assert len(merged) == 68
    difference = float(np.max(np.abs(merged.prediction_replay-merged.prediction_saved)))
    assert difference < 1e-12,(path.name,difference)
    records.append(dict(name=path.stem,max_prediction_difference=difference,predictions=68,
                        encoder_hash_matches=True,checkpoint_sha256=experiment.sha(path)))
    print('REPLAYED',path.stem,difference,flush=True)
    del model,buffers,auxiliary,saved
    torch.cuda.empty_cache()
assert len(records) == 33
experiment.write_json(ROOT/'checkpoint_replay.json',dict(completed=True,final_models=33,checks=records))
