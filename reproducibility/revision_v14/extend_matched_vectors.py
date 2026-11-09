"""Encode one omitted QAC; retain all previously audited target vectors."""
from pathlib import Path
import sys, json, hashlib, os
ROOT=Path(__file__).resolve().parent
OLD=Path('/home/yagr/coma_revision_v12_20261011')
sys.path.insert(0,str(OLD))
import run_matched_finetuning as ft
import numpy as np
import pandas as pd
import torch

def main():
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True,warn_only=True)
    device=torch.device('cuda');torch.cuda.set_per_process_memory_fraction(.30)
    q=pd.read_csv(ROOT/'data/QAC105.csv');o=pd.read_csv(ROOT/'data/OOD17.csv')
    oldq=pd.read_csv(OLD/'data/target_QAC-104.csv');oldo=pd.read_csv(OLD/'data/target_OOD-17.csv')
    missing=q.loc[~q.can.isin(oldq.can)]
    assert len(missing)==1 and len(q)==105
    reference=oldq.iloc[:3]
    small=missing.can.tolist()+reference.can.tolist()
    tokenizer=ft.AutoTokenizer.from_pretrained(ft.MODEL,revision=ft.REVISION,code_revision=ft.REVISION,trust_remote_code=True)
    tokenizer.padding_side='right'
    assert max(map(len,tokenizer(small,truncation=False)['input_ids']))<=202
    tokens=ft.tokenise(tokenizer,small)
    reps=ROOT/'representations';reps.mkdir(exist_ok=True)
    configurations=[];checks=[]
    for seed in range(5):
        net,_=ft.load_net(seed,device)
        for arm in (['raw-molformer'] if seed==0 else [])+ft.ARMS:
            if arm=='raw-molformer': name=arm;saved=None
            else:
                name=f'{arm}_seed{seed}'
                checkpoint=OLD/'results/reproducible_checkpoints'/f'{name}.pt'
                saved=torch.load(checkpoint,map_location='cpu',weights_only=False)
                result=net.load_state_dict(saved['state_dict'],strict=False)
                frozen={n for n,p in net.named_parameters() if not p.requires_grad}
                assert not result.unexpected_keys and set(result.missing_keys)==frozen
            emb,_=ft.outputs(net,tokens,device)
            oldemb=np.load(OLD/'results/representations'/f'{name}_QAC-104.npy')
            diff=float(np.max(np.abs(oldemb[:3]-emb[1:])))
            assert np.allclose(oldemb[:3],emb[1:],rtol=2e-5,atol=1e-5),(name,diff)
            lookup={can:oldemb[i] for i,can in enumerate(oldq.can)};lookup[missing.can.iloc[0]]=emb[0]
            full=np.vstack([lookup[can] for can in q.can]);np.save(reps/f'{name}_QAC105.npy',full)
            oldoodemb=np.load(OLD/'results/representations'/f'{name}_OOD-17.npy')
            full_o=oldoodemb[[oldo.can.tolist().index(can) for can in o.can]]
            np.save(reps/f'{name}_OOD17.npy',full_o)
            encodings=['onehot','text'] if arm in ['raw-molformer','expert','quant-continuous','quant-binary'] else ['onehot']
            configurations.append(dict(name=name,arm=arm,seed=-1 if arm=='raw-molformer' else seed,
                provenance='matched-source-excluded',encodings=encodings))
            checks.append(dict(name=name,max_reference_vector_difference=diff,
                restored_checkpoint_sha256=ft.sha(checkpoint) if saved is not None else None))
            print('EXTENDED',name,'max reference difference',diff,flush=True)
        del net;torch.cuda.empty_cache()
    configurations+=json.loads((ROOT/'data/legacy_configurations.json').read_text())
    (ROOT/'data/configurations.json').write_text(json.dumps(configurations,indent=2))
    (ROOT/'data/vector_extension_audit.json').write_text(json.dumps(dict(completed=True,
        omitted_compound_id=missing.compound_id.iloc[0],checkpoints=30,references=checks,
        source_target_cation_overlap=0,no_upstream_training=True),indent=2))

if __name__=='__main__':main()
