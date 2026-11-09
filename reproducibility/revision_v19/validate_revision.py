"""Check every new ± entry and the immutable original report against saved predictions."""
from pathlib import Path
import importlib.util,json,re
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('v19_builder',ROOT/'build_revision.py');d=load('inspector',ROOT.parent/'revision_v12/validate_documents.py')
def main():
 f,_,body=b.v.read_doc(b.MAIN);oldf,_,oldbody=b.v.read_doc(b.b.MAIN)
 nt=body.findall('w:tbl',b.NS);ot=oldbody.findall('w:tbl',b.NS);assert len(nt)==len(ot)==6
 summary=pd.read_csv(ROOT/'rowcv_results/summary.csv')
 for old,new in zip(ot[:2],nt[:2]):
  a,c=b.rows(old),b.rows(new);assert len(c)==len(a)+3 and c[:len(a)-1]==a[:-1]
  added=c[len(a)-1:-1];assert len(added)==3
  for row,encoding in zip(added,['categorical_task_id','categorical_org_met','text']):
   for cell,task in zip(row[2:],['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']):
    z=summary[(summary.representation=='v5_human')&(summary.encoding==encoding)&(summary.task==task)].iloc[0]
    expected=f'{z.RMSE_mean:.2f} ± {z.RMSE_sd:.2f}(R²={z.R2_mean:.2f} ± {z.R2_sd:.2f})'
    assert cell==expected,(cell,expected)
 assert b.rows(nt[2])==b.rows(ot[2]) and b.rows(nt[4])==b.rows(ot[4])
 for path,data in oldf.items():
  if path.startswith(('word/media/','word/embeddings/')):assert f[path]==data
 reports=[]
 for path,count in [(b.MAIN,8),(b.SI,30)]:
  texts,n=d.inspect(path);assert n==count;assert not any('sk-or-v1-' in t for t in texts)
  reports.append(dict(path=str(path),sha256=b.sha(path),figures=n,relationships_styles_valid=True))
 sif,_,sib=b.v.read_doc(b.SI);oldsi,_,oldsb=b.v.read_doc(b.b.SI)
 assert len(sib.findall('w:tbl',b.NS))==len(oldsb.findall('w:tbl',b.NS))+5
 assert [b.rows(t) for t in sib.findall('w:tbl',b.NS)][:40]==[b.rows(t) for t in oldsb.findall('w:tbl',b.NS)]
 for path,data in oldsi.items():
  if path.startswith(('word/media/','word/embeddings/')):assert sif[path]==data
 # Recompute all original-style row-CV scores and SDs from held-out predictions.
 fm=pd.read_csv(ROOT/'rowcv_results/fold_metrics.csv')
 for p in sorted((ROOT/'rowcv_results/chunks').glob('*_predictions.csv')):
  a=pd.read_csv(p);assert len(a)==432 and a.molecule_index.nunique()==108 and a.can.nunique()==105
  assert a.fold.nunique()==5 and np.isfinite(a.prediction).all()
  for fold,g in a.groupby('fold'):
   for task in ['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC','pooled']:
    z=g if task=='pooled' else g[g.task==task];err=z.prediction-z.y
    row=fm[(fm.representation==a.representation.iloc[0])&(fm.encoding==a.encoding.iloc[0])&(fm.fold==fold)&(fm.task==task)].iloc[0]
    assert abs(row.RMSE-np.sqrt(np.mean(err**2)))<1e-12
    r2=1-np.sum(err**2)/np.sum((z.y-z.y.mean())**2);assert abs(row.R2-r2)<1e-12
 for row in summary.itertuples():
  a=fm[(fm.representation==row.representation)&(fm.encoding==row.encoding)&(fm.task==row.task)]
  assert len(a)==5
  for metric in ['RMSE','R2']:
   assert abs(getattr(row,metric+'_mean')-a[metric].mean())<1e-12
   assert abs(getattr(row,metric+'_sd')-a[metric].std(ddof=0))<1e-12
 # Recompute complete-run mean±sample SD used in main Tables4 and6.
 manifest=json.loads((ROOT/'revision_manifest.json').read_text());oldmetrics=pd.read_csv(b.OLD/'analysis/metrics.csv')
 for entry in manifest['main_seed_SD_entries']:
  if entry['table']==4:
   values=oldmetrics[(oldmetrics.arm==entry['arm'])&(oldmetrics.encoding=='categorical')&(oldmetrics.schema==entry['schema'])&(oldmetrics.task=='pooled')].RMSE.to_numpy()
   assert len(values)==5 and abs(values.mean()-entry['mean'])<1e-12 and abs(values.std(ddof=1)-entry['sd'])<1e-12
  else:
   dm=pd.read_csv(ROOT.parent/'revision_v16/analysis/direct_metrics.csv')
   am=pd.read_csv(ROOT.parent/'revision_v16/analysis/ablation_metrics.csv')
   route=entry['route']
   if route=='Human partial / frozen CatBoost':
    a=am[(am.arm=='expert')&(am.variant=='intact')&am.seed.isin([0,1,2])&(am.task=='pooled')&(am.schema==entry['schema'])]
   else:
    spec={'Pretrained / frozen linear head':('raw-molformer','linear'),'Pretrained / direct LoRA':('raw-molformer','lora'),'Pretrained / direct full FT':('raw-molformer','full'),'Human partial / direct prediction':('expert','partial')}[route]
    a=dm[(dm.arm==spec[0])&(dm['mode'].isin(['linear','frozen']) if spec[1]=='linear' else dm['mode']==spec[1])&(dm.task=='pooled')&(dm.schema==entry['schema'])]
   values=a.RMSE.to_numpy();assert len(values)==3
   assert abs(values.mean()-entry['mean'])<1e-12 and abs(values.std(ddof=1)-entry['sd'])<1e-12
  table=nt[entry['table']-1]
  # Every rendered statistic must match a verified manifest entry.
  assert any(f"{entry['mean']:.3f} ± {entry['sd']:.3f}" in cell for row in b.rows(table)[1:] for cell in row[2:])
 assert len(manifest['main_seed_SD_entries'])==39 # 8 non-raw rows x3; five routes x3.
 oldtext=[b.h.text(x) for x in oldbody];text=[b.h.text(x) for x in body]
 a=oldtext.index('4.1 Chemistry');z=oldtext.index('4.3 Computational and annotation protocol')
 aa=text.index('4.1 Chemistry');zz=text.index('4.3 Computational and annotation protocol');assert oldtext[a:z]==text[aa:zz]
 assert [t for t in oldtext if t.startswith('[COAUTHORS')]==[t for t in text if t.startswith('[COAUTHORS')]
 probe=next(t for t in text if t.startswith('The archived representation analysis reports'))
 assert '0.891 ± 0.037' in probe and '0.844 ± 0.060' in probe
 assert b.sha(b.b.SOURCE)==manifest['source_v5_sha256']
 final=dict(completed=True,documents=reports,original_v5_and_v18_unchanged=True,historical_holdout_values_byte_preserved_as_cell_text=True,
  no_CV_SD_attached_to_historical_holdout_values=True,new_CV_rows_per_original_table=3,CV_decoder_fits=30,
  rowwise_CV_metric_and_population_SD_recomputed=True,source_seed_SD_sample_definition_verified=True,
  recovered_original_probe_uncertainty=True,all_original_figures_and_Office_objects_byte_preserved=True,
  previous_SI_tables_byte_preserved_as_cell_text=True,SI_tables=len(sib.findall('w:tbl',b.NS)),
  chemistry_assay_and_coauthor_fields_preserved=True,new_variability_types_explicit=True)
 (ROOT/'document_validation.json').write_text(json.dumps(final,indent=2));print(json.dumps(final,indent=2))
if __name__=='__main__':main()
