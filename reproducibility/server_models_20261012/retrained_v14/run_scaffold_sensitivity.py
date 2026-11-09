from pathlib import Path
import os, json, shutil
import pandas as pd
from sklearn.model_selection import GroupKFold
import run_comparisons as comparisons
ROOT=Path(__file__).resolve().parent

def main():
    sub=ROOT/'scaffold_sensitivity';(sub/'data').mkdir(parents=True,exist_ok=True)
    registry=pd.read_csv(ROOT/'data/endpoint_registry.csv')
    q=registry[registry.cohort=='QAC105'].drop_duplicates('can')
    folds={}
    for fold,(tr,te) in enumerate(GroupKFold(n_splits=5).split(q,groups=q.scaffold)):
        assert not set(q.scaffold.iloc[tr])&set(q.scaffold.iloc[te])
        folds.update({can:fold for can in q.can.iloc[te]})
    registry.loc[registry.cohort=='QAC105','fold']=registry.loc[registry.cohort=='QAC105','can'].map(folds)
    registry.to_csv(sub/'data/endpoint_registry.csv',index=False)
    configs=[dict(c,encodings=['onehot']) for c in json.loads((ROOT/'data/configurations.json').read_text()) if c['provenance']=='matched-source-excluded']
    (sub/'data/configurations.json').write_text(json.dumps(configs,indent=2))
    shutil.copyfile(ROOT/'SCaffold_SENSITIVITY.md',sub/'PROTOCOL.md')
    if not (sub/'representations').exists():(sub/'representations').symlink_to(ROOT/'representations',target_is_directory=True)
    comparisons.ROOT=sub;comparisons.main()

if __name__=='__main__':main()
