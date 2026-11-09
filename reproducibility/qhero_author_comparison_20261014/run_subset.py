"""Parallel second-server calculation of six still-pending configurations."""
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import time
import sklearn
import catboost
import run_comparison as m

ROOT=Path(__file__).resolve().parent
ORIGINAL=m.CatBoostClassifier


def classifier(**kwargs):
    kwargs['thread_count']=4
    return ORIGINAL(**kwargs)


def main():
    m.CatBoostClassifier=classifier
    out=ROOT/'results_subset'
    out.mkdir(exist_ok=True)
    jobs=[(str(ROOT),'CB_quantitative',0),
          (str(ROOT),'CB_shuffled_human',4)]+[
          (str(ROOT),'CB_quantitative',s) for s in range(1,5)]
    metrics=[];predictions=[]
    started=time.time()
    with ProcessPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(m.run_one,j):j for j in jobs}
        for future in as_completed(futures):
            job=futures[future]
            a,b=future.result();metrics+=a;predictions+=b
            m.pd.DataFrame(metrics).to_csv(out/'metrics.csv',index=False)
            m.pd.DataFrame(predictions).to_csv(out/'predictions.csv',index=False)
            print('finished',job[1],job[2],round(time.time()-started),flush=True)
    done=dict(completed=True,configurations=[[j[1],j[2]] for j in jobs],
              elapsed_seconds=time.time()-started,workers=3,threads_per_fit=4,
              sklearn=sklearn.__version__,catboost=catboost.__version__,
              model_budget='800 iterations / depth6 / lr0.05; unchanged')
    (out/'completion.json').write_text(json.dumps(done,indent=2))
    print(json.dumps(done),flush=True)


if __name__=='__main__':
    main()
