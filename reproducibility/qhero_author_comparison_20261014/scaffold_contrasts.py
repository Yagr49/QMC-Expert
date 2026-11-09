"""Conditional paired bootstrap of completed OOF predictions, not model refits."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT=Path(__file__).resolve().parent


def main():
    d=pd.read_csv(ROOT/'data/target.csv')
    p=pd.read_csv(ROOT/'results/predictions.csv')
    p=p[p.protocol.eq('scaffold_CV_fold')]
    y=d.sa_mic_um.le(8).astype(int).to_numpy()
    names=['CB_human','CB_shuffled_human','CB_quantitative','RF_35_descriptors']
    arrays={}
    for name in names:
        frame=p[p.model.eq(name)].pivot(index='row_index',columns='seed',values='probability').reindex(range(405))
        assert frame.notna().all().all()
        arrays[name]=frame.to_numpy().T
    clusters=[np.flatnonzero(d.scaffold.eq(s).to_numpy()) for s in sorted(d.scaffold.unique())]
    assert len(clusters)==29
    assert d.groupby('scaffold').scaffold_fold.nunique().max()==1
    assert d.groupby('cation').scaffold_fold.nunique().max()==1
    functions={'AUROC':roc_auc_score,'AUPRC':average_precision_score}
    contrasts=[('CB_human','CB_shuffled_human'),('CB_human','CB_quantitative'),
               ('CB_human','RF_35_descriptors'),('CB_quantitative','RF_35_descriptors')]
    values={(a,b,metric):[] for a,b in contrasts for metric in functions}
    rng=np.random.RandomState(20261014)
    repeats=2000
    skipped=0
    for trial in range(repeats):
        idx=np.concatenate([clusters[i] for i in rng.randint(len(clusters),size=len(clusters))])
        if len(np.unique(y[idx]))!=2:
            skipped+=1
            continue
        seeds=rng.randint(5,size=5)
        metrics={}
        for name,arr in arrays.items():
            chosen=seeds if len(arr)==5 else np.zeros(5,dtype=int)
            for metric,fn in functions.items():
                cache={int(s):fn(y[idx],arr[s,idx]) for s in np.unique(chosen)}
                metrics[name,metric]=np.mean([cache[int(s)] for s in chosen])
        for a,b in contrasts:
            for metric in functions:
                values[a,b,metric].append(metrics[a,metric]-metrics[b,metric])
        if (trial+1)%500==0:
            print('bootstrap',trial+1,'/',repeats,flush=True)
    rows=[]
    for (a,b,metric),draws in values.items():
        fn=functions[metric]
        point=np.mean([fn(y,prob) for prob in arrays[a]])-np.mean([fn(y,prob) for prob in arrays[b]])
        low,high=np.percentile(draws,[2.5,97.5])
        rows.append(dict(model=a,reference=b,metric=metric,difference=float(point),
                         ci_low=float(low),ci_high=float(high),bootstrap_repeats=len(draws),
                         unit='paired source/decoder seeds + 29 scaffold clusters; conditional on fixed OOF fits'))
    out=pd.DataFrame(rows)
    out.to_csv(ROOT/'results/paired_scaffold_contrasts.csv',index=False)
    meta=dict(completed=True,repeats=repeats,skipped_single_class=skipped,scaffold_clusters=29,
              source_seed_pairing=True,source_and_target_models_refit=False,
              overlapping_training_sets_in_OOF_not_resampled=True,
              limitation='Exploratory conditional intervals; not full training uncertainty or biological causality',
              manuscript_or_SI_updated=False)
    (ROOT/'results/scaffold_contrast_validation.json').write_text(json.dumps(meta,indent=2))
    print(out.to_string(index=False))


if __name__=='__main__':
    main()
