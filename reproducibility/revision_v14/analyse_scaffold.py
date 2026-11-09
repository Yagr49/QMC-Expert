from pathlib import Path
import json
import numpy as np
import pandas as pd
import analyse_results as analysis
ROOT=Path(__file__).resolve().parent

def main():
    directory=ROOT/'scaffold_sensitivity'
    manifest=json.loads((directory/'results/manifest.json').read_text());assert manifest['completed']
    p=pd.read_csv(directory/'results/predictions.csv');m,s=analysis.summaries(p)
    registry=pd.read_csv(directory/'data/endpoint_registry.csv')
    q=registry[registry.cohort=='QAC105']
    for fold in q.fold.unique():assert not set(q[q.fold==fold].scaffold)&set(q[q.fold!=fold].scaffold)
    s.to_csv(ROOT/'analysis/scaffold_summary.csv',index=False)
    analysis.contrasts(p).to_csv(ROOT/'analysis/scaffold_contrasts.csv',index=False)
    original=pd.read_csv(ROOT/'results/predictions.csv')
    old=original[(original.cohort=='OOD17')&(original.encoding=='onehot')&(original.provenance=='matched-source-excluded')].sort_values(['name','can','task'])
    fresh=p[(p.cohort=='OOD17')&(p.provenance=='matched-source-excluded')].sort_values(['name','can','task'])
    assert old.shape==fresh.shape
    diff=float(np.max(np.abs(old.prediction.values-fresh.prediction.values)));assert diff<1e-12
    report=dict(completed=True,jobs=31,QAC105=105,QAC_scaffolds=29,scaffold_train_test_overlap=0,
        fold_compounds=q.drop_duplicates('can').groupby('fold').size().to_dict(),OOD_prediction_max_difference=diff,
        protocol_timing='Exploratory follow-up after initial extension outcomes and protocol reviews')
    (ROOT/'scaffold_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    print(s.query("cohort=='QAC105' and arm=='expert'")[['task','RMSE','R2']].to_string(index=False))

if __name__=='__main__':main()
