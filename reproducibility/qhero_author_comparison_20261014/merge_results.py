"""Merge fully completed configurations; preserve and compare duplicate runs."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent


def main():
    sources=[]
    for name in ('primary_results','secondary_results'):
        p=ROOT/name
        if (p/'metrics.csv').exists() and (p/'predictions.csv').exists():
            sources.append((name,pd.read_csv(p/'metrics.csv'),pd.read_csv(p/'predictions.csv')))
    expected={(tag,seed)
              for tag in ('RF_35_descriptors','CB_35_descriptors','CB_raw_MolFormer',
                          'CB_human','CB_shuffled_human','CB_quantitative')
              for seed in (range(5) if tag in ('CB_human','CB_shuffled_human','CB_quantitative') else [0])}
    chosen={};checks=[]
    metrics=[];predictions=[]
    for source,m,p in sources:
        for (tag,seed),a in m.groupby(['model','seed']):
            b=p[(p.model==tag)&(p.seed==seed)]
            em,ep=(12,810) if seed==0 else (7,486)
            if len(a)!=em or len(b)!=ep:
                continue
            key=(tag,int(seed))
            a=a.sort_values(['protocol','fold']).reset_index(drop=True)
            b=b.sort_values(['protocol','fold','row_index']).reset_index(drop=True)
            if key in chosen:
                previous=chosen[key]
                delta=float(np.max(np.abs(previous['pred'].probability.values-b.probability.values)))
                assert np.array_equal(previous['pred'].row_index.values,b.row_index.values)
                assert np.array_equal(previous['pred'].label.values,b.label.values)
                metric_delta=float(np.max(np.abs(previous['metrics'][['AUROC','AUPRC']].values-a[['AUROC','AUPRC']].values)))
                checks.append(dict(model=tag,seed=int(seed),source1=previous['source'],source2=source,
                                   max_prediction_difference=delta,max_metric_difference=metric_delta))
                assert delta<1e-10 and metric_delta<1e-10,checks[-1]
            else:
                chosen[key]=dict(source=source,pred=b,metrics=a)
                metrics.append(a);predictions.append(b)
    missing=expected-set(chosen)
    if missing:
        print(json.dumps(dict(completed=False,ready=len(chosen),missing=sorted(missing))))
        return
    out=ROOT/'results';out.mkdir(exist_ok=True)
    m=pd.concat(metrics,ignore_index=True);p=pd.concat(predictions,ignore_index=True)
    assert len(m)==156 and len(p)==10692
    m.to_csv(out/'metrics.csv',index=False);p.to_csv(out/'predictions.csv',index=False)
    public=ROOT/'primary_results'/'public_RF_reproduction.json'
    (out/public.name).write_bytes(public.read_bytes())
    done=dict(completed=True,configurations=18,
              sklearn='1.7.2',catboost='1.2.10',
              servers=['100.76.26.71','100.118.123.26'],
              primary_threads_per_fit=2,secondary_threads_per_fit=4,
              selection=[dict(model=k[0],seed=k[1],source=v['source']) for k,v in chosen.items()],
              duplicate_checks=checks,manuscript_changed=False)
    (out/'completion.json').write_text(json.dumps(done,indent=2))
    print(json.dumps(done,indent=2))


if __name__=='__main__':
    main()
