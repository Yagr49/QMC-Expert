"""Independently encode all 105 QAC and 17 OOD molecules after the new FT."""
import os
from pathlib import Path
import sys
import json
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'core_ft'))
import run_matched_finetuning as ft
import numpy as np
import pandas as pd
import torch


def main():
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device('cuda')
    torch.cuda.set_per_process_memory_fraction(.70)
    dest = ROOT / 'retrained_v14'
    q = pd.read_csv(dest / 'data/QAC105.csv')
    o = pd.read_csv(dest / 'data/OOD17.csv')
    source = pd.read_csv(ROOT / 'core_ft/data/matched-pooled_expert.csv')
    assert len(q) == 105 and len(o) == 17
    assert not set(source.cation) & (set(q.cation) | set(o.cation))
    assert not set(o.scaffold) & (set(q.scaffold) | set(source.scaffold))
    tokenizer = ft.AutoTokenizer.from_pretrained(ft.MODEL, revision=ft.REVISION,
                         code_revision=ft.REVISION, trust_remote_code=True)
    tokenizer.padding_side = 'right'
    tokens = {}
    for cohort, frame in [('QAC105', q), ('OOD17', o)]:
        assert max(map(len, tokenizer(list(frame.can), truncation=False)['input_ids'])) <= 202
        tokens[cohort] = ft.tokenise(tokenizer, frame.can)
    checks = []
    configurations = []
    for seed in range(5):
        net, _ = ft.load_net(seed, device)
        for arm in (['raw-molformer'] if seed == 0 else []) + ft.ARMS:
            name = arm if arm == 'raw-molformer' else f'{arm}_seed{seed}'
            if arm != 'raw-molformer':
                saved = torch.load(ROOT / 'core_ft/results/checkpoints' / (name + '.pt'),
                                   map_location='cpu', weights_only=False)
                assert saved['includes_all_buffers']
                live_state = net.state_dict()
                auxiliary = {n: v for n, v in saved['state_dict'].items() if n not in live_state}
                buffers = dict(net.named_buffers())
                assert set(auxiliary).issubset(buffers), list(auxiliary)
                result = net.load_state_dict({n: v for n, v in saved['state_dict'].items() if n in live_state}, strict=False)
                frozen = {n for n, p in net.named_parameters() if not p.requires_grad}
                assert not result.unexpected_keys and set(result.missing_keys) == frozen
                # PyTorch omits nonpersistent buffers from state_dict. Our new
                # snapshots deliberately include them; restore these explicitly.
                with torch.no_grad():
                    for n, value in auxiliary.items():
                        buffers[n].copy_(value.to(device=buffers[n].device, dtype=buffers[n].dtype))
            for cohort, tok in tokens.items():
                emb, _ = ft.outputs(net, tok, device)
                assert np.isfinite(emb).all()
                filename = f'{name}_{cohort}.npy'
                np.save(dest / 'representations' / filename, emb)
                old = np.load(ROOT / 'core_v14/representations' / filename)
                checks.append(dict(name=name, cohort=cohort,
                                   max_abs_difference=float(np.max(np.abs(old - emb))),
                                   allclose=bool(np.allclose(old, emb, rtol=2e-5, atol=1e-5))))
            configurations.append(dict(name=name, arm=arm, seed=-1 if arm == 'raw-molformer' else seed,
                        provenance='matched-source-excluded',
                        encodings=['onehot', 'text'] if arm in ['raw-molformer', 'expert',
                                      'quant-continuous', 'quant-binary'] else ['onehot']))
            print('ENCODED', name, checks[-2:], flush=True)
        del net
        torch.cuda.empty_cache()
    (dest / 'data/configurations.json').write_text(json.dumps(configurations, indent=2))
    (dest / 'data/retraining_vector_audit.json').write_text(json.dumps(checks, indent=2))
    (ROOT / 'status/retrained_vectors.ready').write_text('complete\n')


if __name__ == '__main__':
    main()
