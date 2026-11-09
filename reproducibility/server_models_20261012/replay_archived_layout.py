"""Replay v14's batch layout using independently retrained checkpoints."""
from pathlib import Path
import sys
import json
import shutil
import numpy as np
import pandas as pd
import torch
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'core_ft'))
import run_matched_finetuning as ft


def main():
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device('cuda')
    torch.cuda.set_per_process_memory_fraction(.70)
    dest = ROOT / 'retrained_v14_archived_layout'
    (dest / 'representations').mkdir(parents=True, exist_ok=True)
    q = pd.read_csv(ROOT / 'retrained_v14/data/QAC105.csv')
    o = pd.read_csv(ROOT / 'retrained_v14/data/OOD17.csv')
    original_q = pd.read_csv(ROOT / 'core_ft/data/target_QAC-104.csv')
    original_o = pd.read_csv(ROOT / 'core_ft/data/target_OOD-17.csv')
    missing = q[~q.can.isin(original_q.can)]
    assert len(missing) == 1
    small = missing.can.tolist() + original_q.can.iloc[:3].tolist()
    tokenizer = ft.AutoTokenizer.from_pretrained(ft.MODEL, revision=ft.REVISION,
                     code_revision=ft.REVISION, trust_remote_code=True)
    tokenizer.padding_side = 'right'
    tok = ft.tokenise(tokenizer, small)
    audit = []
    for seed in range(5):
        net, _ = ft.load_net(seed, device)
        for arm in (['raw-molformer'] if seed == 0 else []) + ft.ARMS:
            name = arm if arm == 'raw-molformer' else f'{arm}_seed{seed}'
            if arm != 'raw-molformer':
                saved = torch.load(ROOT / 'core_ft/results/checkpoints' / (name + '.pt'),
                                   map_location='cpu', weights_only=False)
                live = net.state_dict()
                auxiliary = {n: v for n, v in saved['state_dict'].items() if n not in live}
                buffers = dict(net.named_buffers())
                assert set(auxiliary).issubset(buffers)
                loaded = net.load_state_dict({n: v for n, v in saved['state_dict'].items() if n in live}, strict=False)
                frozen = {n for n, p in net.named_parameters() if not p.requires_grad}
                assert not loaded.unexpected_keys and set(loaded.missing_keys) == frozen
                with torch.no_grad():
                    for n, value in auxiliary.items():
                        buffers[n].copy_(value.to(device=buffers[n].device, dtype=buffers[n].dtype))
            small_emb, _ = ft.outputs(net, tok, device)
            repeated_q = np.load(ROOT / 'core_ft/results/representations' / (name + '_QAC-104.npy'))
            repeated_o = np.load(ROOT / 'core_ft/results/representations' / (name + '_OOD-17.npy'))
            lookup = dict(zip(original_q.can.tolist(), repeated_q))
            lookup[missing.can.iloc[0]] = small_emb[0]
            vectors = {'QAC105': np.vstack([lookup[can] for can in q.can]),
                       'OOD17': repeated_o[[original_o.can.tolist().index(can) for can in o.can]]}
            for cohort, array in vectors.items():
                filename = f'{name}_{cohort}.npy'
                np.save(dest / 'representations' / filename, array)
                original = np.load(ROOT / 'core_v14/representations' / filename)
                audit.append(dict(name=name, cohort=cohort, exact=bool(np.array_equal(array, original)),
                             max_difference=float(np.max(np.abs(array - original)))))
            print('REPLAY', name, audit[-2:], flush=True)
        del net
        torch.cuda.empty_cache()
    report = dict(training='independent 30-run repeat', layout='104 archived batch + omitted compound in four-molecule batch',
                  no_target_label_selection=True, byte_equal_all=all(x['exact'] for x in audit), comparisons=audit,
                  main_target_cached_repeat='core_v14/results and core_v14/scaffold_sensitivity/results')
    (dest / 'layout_audit.json').write_text(json.dumps(report, indent=2))
    print('All arrays byte equal:', report['byte_equal_all'], flush=True)


if __name__ == '__main__':
    main()
