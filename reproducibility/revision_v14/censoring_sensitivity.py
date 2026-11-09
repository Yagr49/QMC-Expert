from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent

def main():
    p=pd.read_csv(ROOT/'results/predictions.csv');p=p.query("cohort=='OOD17'")
    rows=[]
    for (arm,encoding,seed),d in p.groupby(['arm','encoding','seed']):
        for task in ['Ec_MBC','pooled']:
            sub=d if task=='pooled' else d[d.task==task]
            error=np.where(sub.qualifier.values=='=',np.abs(sub.y-sub.prediction),np.maximum(sub.y-sub.prediction,0))
            rows.append(dict(arm=arm,encoding=encoding,seed=seed,task=task,n_values=len(sub),
                exact_values=int((sub.qualifier=='=').sum()),censored_values=int((sub.qualifier!='=').sum()),
                minimum_RMSE=float(np.sqrt(np.mean(error**2))),minimum_MAE=float(np.mean(error))))
    result=pd.DataFrame(rows);result.to_csv(ROOT/'analysis/censoring_minimum_error.csv',index=False)
    summary=result.groupby(['arm','encoding','task']).agg(seeds=('seed','size'),minimum_RMSE=('minimum_RMSE','mean'),
        minimum_RMSE_sd=('minimum_RMSE','std'),minimum_MAE=('minimum_MAE','mean')).reset_index().fillna(0)
    summary.to_csv(ROOT/'analysis/censoring_minimum_error_summary.csv',index=False)
    print(summary.query("encoding=='onehot' and arm=='expert'").to_string(index=False))

if __name__=='__main__':main()
