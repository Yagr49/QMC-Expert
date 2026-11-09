from pathlib import Path
import shutil,json,hashlib
import pandas as pd
R=Path(__file__).resolve().parent;V=R.parent/'revision_v9'
for p in (V/'data').glob('*'):
 if p.is_file(): shutil.copy2(p,R/'data'/p.name)
e=pd.read_csv(R/'data/matched-sa_expert.csv');p=pd.read_csv(R/'data/source_quant-pooled-full.csv').set_index('can').loc[e.can].reset_index()
s=pd.read_csv(R/'data/matched-sa_quant.csv')
assert p.can.tolist()==s.can.tolist()==e.can.tolist()
p.to_csv(R/'data/context_quant-pooled.csv',index=False);s.to_csv(R/'data/context_quant-sa.csv',index=False);e.to_csv(R/'data/context_expert.csv',index=False)
for name in ['pooled','sa']:
 x=pd.read_csv(R/'data'/('matched-'+name+'_quant.csv'))
 print(name,len(x),x.n_records.describe().to_dict())
meta={'common_context_molecules':len(e),'context_scaffolds':int(e.scaffold.nunique()),'context_expert_good':int(e.y.sum()),'pooled_records_same_molecules':int(p.n_records.sum()),'sa_exact_records_same_molecules':int(s.n_records.sum()),'new_label_columns':'pooled median versus exact S. aureus median; identical ordered molecules','limitations':'Pooling also changes organism, censoring treatment, record count, and aggregation. Not an isolated laboratory-heterogeneity intervention.'}
(R/'data/extension_meta.json').write_text(json.dumps(meta,indent=2))
shutil.copy2(V/'results_matched-pooled_matched-sa_full/target_folds.csv',R/'data/target_folds.csv')
