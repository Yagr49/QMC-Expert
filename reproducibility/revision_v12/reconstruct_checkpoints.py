"""Recover final native feature-map buffers and independently reproduce outputs.

Training checkpoints and predictions remain immutable. Accept reconstructed
checkpoints only after numerical agreement with both embeddings and direct heads.
"""
from pathlib import Path
import argparse,json,time
import run_matched_finetuning as ft
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import GroupShuffleSplit

ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,default=ROOT/'results')
    ap.add_argument('--seeds',nargs='+',type=int,default=list(range(5)));a=ap.parse_args()
    r=a.results;out=r/'reproducible_checkpoints';out.mkdir(exist_ok=True)
    manifest=json.loads((r/'manifest.json').read_text());epoch_count=manifest['epochs'];batch_size=manifest['batch_size']
    torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True,warn_only=True);device=torch.device('cuda')
    torch.cuda.set_per_process_memory_fraction(.30)
    source=pd.read_csv(ROOT/'data/matched-pooled_expert.csv')
    tr,va=next(GroupShuffleSplit(n_splits=1,test_size=.15,random_state=1729).split(source,groups=source.scaffold))
    tokenizer=ft.AutoTokenizer.from_pretrained(ft.MODEL,revision=ft.REVISION,code_revision=ft.REVISION,trust_remote_code=True)
    tokenizer.padding_side='right';tokens=ft.tokenise(tokenizer,source.can.iloc[tr])
    targets={n:pd.read_csv(ROOT/'data'/f'target_{n}.csv') for n in ft.TARGETS}
    target_tokens={n:ft.tokenise(tokenizer,d.can) for n,d in targets.items()}
    predictions=pd.read_csv(r/'direct_predictions.csv');train=pd.read_csv(r/'training.csv')
    records=[]
    for seed in a.seeds:
        started=time.time();net,loading=ft.load_net(seed,device)
        # Only shapes and the stochastic forward schedule determine feature-map
        # draws; no gradient or optimiser operation consumes a random draw.
        torch.manual_seed(300000+seed);generator=torch.Generator().manual_seed(200000+seed)
        net.train()
        with torch.no_grad():
            for epoch in range(epoch_count):
                order=torch.randperm(len(tr),generator=generator)
                for start in range(0,len(tr),batch_size):
                    idx=order[start:start+batch_size]
                    batch={k:v[idx].to(device) for k,v in tokens.items()}
                    net(**batch)
        state_names=set(net.state_dict())
        buffers={name:b.detach().cpu().clone() for name,b in net.named_buffers() if name in state_names}
        projection_count=sum('feature_map' in name and name.endswith('weight') for name in buffers)
        assert projection_count==12,(projection_count,list(buffers))
        for arm in ft.ARMS:
            original=r/'checkpoints'/f'{arm}_seed{seed}.pt'
            saved=torch.load(original,map_location='cpu',weights_only=False)
            assert saved['epochs']==epoch_count and saved['updates']==epoch_count*manifest['steps_per_epoch']
            digest=train.set_index(['arm','seed']).loc[(arm,seed)].checkpoint_sha256
            assert ft.sha(original)==digest
            combined=dict(saved['state_dict'],**buffers)
            missing=net.load_state_dict(combined,strict=False)
            assert not missing.unexpected_keys
            frozen={name for name,p in net.named_parameters() if not p.requires_grad}
            assert set(missing.missing_keys)==frozen,(set(missing.missing_keys)-frozen)
            binary=arm.startswith('expert') or arm.startswith('quant-binary')
            checks=[]
            for name,tok in target_tokens.items():
                emb,score=ft.outputs(net,tok,device)
                archived_emb=np.load(r/'representations'/f'{arm}_seed{seed}_{name}.npy')
                sub=predictions[(predictions.arm==arm)&(predictions.seed==seed)&(predictions.target==name)].set_index('can').loc[targets[name].can]
                restored_score=score if binary else score*saved['target_sd']+saved['target_mean']
                feature_diff=float(np.max(np.abs(emb-archived_emb)))
                score_diff=float(np.max(np.abs(restored_score-sub.score.values)))
                assert np.allclose(emb,archived_emb,rtol=1e-5,atol=1e-6),(seed,arm,name,'embedding',feature_diff)
                assert np.allclose(restored_score,sub.score.values,rtol=1e-5,atol=1e-6),(seed,arm,name,'score',score_diff)
                checks.append(dict(target=name,max_feature_difference=feature_diff,max_score_difference=score_diff))
            path=out/f'{arm}_seed{seed}.pt';assert not path.exists()
            torch.save(dict(saved,state_dict=combined,buffer_replay='paired native forward RNG schedule; verified against original outputs'),path)
            records.append(dict(arm=arm,seed=seed,original_checkpoint_sha256=digest,
                reconstructed_checkpoint_sha256=ft.sha(path),checkpoint_file=str(path),
                persistent_buffer_count=len(buffers),feature_map_count=projection_count,
                max_feature_difference=max(c['max_feature_difference'] for c in checks),
                max_score_difference=max(c['max_score_difference'] for c in checks)))
            pd.DataFrame(records).to_csv(r/f'checkpoint_reconstruction_seeds_{"_".join(map(str,a.seeds))}.csv',index=False)
            print('REPRODUCED',seed,arm,checks,flush=True)
        del net;torch.cuda.empty_cache();print('SEED BUFFER REPLAY',seed,round(time.time()-started,1),'seconds',flush=True)
    ft.write_json(r/f'checkpoint_reconstruction_seeds_{"_".join(map(str,a.seeds))}.json',dict(complete=True,
        script_sha256=ft.sha(__file__),implementation_note_sha256=ft.sha(ROOT/'PROTOCOL_IMPLEMENTATION_NOTE.md'),
        original_checkpoints_preserved=True,checkpoints=len(records),max_feature_difference=max(d['max_feature_difference'] for d in records),
        max_score_difference=max(d['max_score_difference'] for d in records)))

if __name__=='__main__':main()
