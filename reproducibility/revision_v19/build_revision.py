"""Add honestly paired mean±SD rows; retain the author's original holdout values."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re,xml.etree.ElementTree as E
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1];OLD=ROOT.parent/'revision_v18'
spec=importlib.util.spec_from_file_location('old_builder',OLD/'build_revision.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
v,h,NS,W=b.v,b.h,b.NS,b.W
MAIN=COMA/'2026_10_13_Paper_2_edited-v19_CV_and_seed_variability.docx';SI=ROOT/'Supplementary_Information_v19.docx'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(table):return [[h.text(c) for c in r.findall('w:tc',NS)] for r in table.findall('w:tr',NS)]
def replace_cell(cell,text):
 paras=cell.findall('w:p',NS);template=copy.deepcopy(paras[0]);font=template.find('w:r/w:rPr',NS);lines=text.split('\n');h.replace(paras[0],lines[0])
 for extra in paras[1:]:cell.remove(extra)
 for line in lines[1:]:
  p=copy.deepcopy(template);h.replace(p,line);cell.append(p)
 if font is not None:
  for run in cell.findall('.//w:r',NS):run.insert(0,copy.deepcopy(font))
def main():
 rowcv=pd.read_csv(ROOT/'rowcv_results/summary.csv');assert len(rowcv)==30 and rowcv.n_folds.eq(5).all()
 rowmeta=json.loads((ROOT/'rowcv_results/manifest.json').read_text());assert rowmeta['completed'] and rowmeta['fits']==30
 files,tree,body=v.read_doc(b.MAIN);tables=body.findall('w:tbl',NS);assert len(tables)==6
 normal=next(p for p in body if h.text(p).startswith('The workflow separates three objects'))
 p=lambda text,level=None:v.paragraph(normal,text,level,marked=text.startswith('[COAUTHORS'))
 for i,table in enumerate(tables[:2],1):
  original_rows=table.findall('w:tr',NS);template=original_rows[-2];foot=original_rows[-1]
  assert len(template.findall('w:tc',NS))==6
  for encoding,label in [('categorical_task_id','Human / new CV: task_id'),('categorical_org_met','Human / new CV: organism + endpoint'),('text','Human / new CV: text code')]:
   r=copy.deepcopy(template);values=[label,'5-fold mean ± SD']
   props=r.find('w:trPr',NS)
   if props is not None:
    for height in props.findall('w:trHeight',NS):props.remove(height)
   for task in ['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']:
    a=rowcv[(rowcv.representation=='v5_human')&(rowcv.encoding==encoding)&(rowcv.task==task)].iloc[0]
    values.append(f'{a.RMSE_mean:.2f} ± {a.RMSE_sd:.2f}\n(R²={a.R2_mean:.2f} ± {a.R2_sd:.2f})')
   for cell,value in zip(r.findall('w:tc',NS),values):
    replace_cell(cell,value)
    for run in cell.findall('.//w:r',NS):
     properties=run.find('w:rPr',NS)
     if properties is None:properties=E.Element('{'+W+'}rPr');run.insert(0,properties)
     for existing_size in properties.findall('w:sz',NS):properties.remove(existing_size)
     E.SubElement(properties,'{'+W+'}sz').set('{'+W+'}val','18')
   table.insert(list(table).index(foot),r)
  note=h.text(foot)+' Separate new CV rows report unweighted mean ± SD of five fold scores (numpy.std, ddof=0), on the original 108 worksheet rows / 105 unique salts. They reconstruct the author’s row-wise KFold approach with saved human features and reconstructed task vectors; they are not uncertainty attached to the historical holdout rows. No CV rows for the unresolved full-corpus quantitative checkpoint are substituted.'
  replace_cell(foot.find('w:tc',NS),note)
  props=foot.find('w:trPr',NS)
  if props is not None:
   for height in props.findall('w:trHeight',NS):props.remove(height)
 # Recover the author's actual recorded probing uncertainty, with its exact scope.
 for node in body:
  text=h.text(node)
  if text.startswith('The archived representation analysis reports'):
   new=text.replace('a mean explained variance of 0.891','R²=0.891 ± 0.037 over five CV folds (mean ± SD)')
   new+=' The reverse probe gives R²=0.844 ± 0.060 in the same saved five-fold calculation; these are representation-reconstruction scores, not MIC/MBC prediction metrics.'
   h.replace(node,new)
 # Seed variability belongs to complete repeated fits, including a fixed OOD set.
 seed_summary=pd.read_csv(ROOT/'analysis/seed_summary.csv');seed_rows=[]
 arm_labels={'Raw reference':None,'Untrained compact encoder':'initial','Human':'human','Shuffled human':'human_shuffled',
  'Binary MIC':'mic_binary','Shuffled binary MIC':'binary_shuffled','Continuous MIC':'mic_continuous',
  'Shuffled continuous MIC':'continuous_shuffled','Human weights reset; BN retained':'human_weight_only'}
 for r in tables[3].findall('w:tr',NS)[1:]:
  cells=r.findall('w:tc',NS);arm=arm_labels[h.text(cells[0])]
  if arm is None:continue
  for c,schema in zip(cells[2:],['cation','scaffold','full-QAC105']):
   a=seed_summary[(seed_summary.arm==arm)&(seed_summary.encoding=='categorical')&(seed_summary.schema==schema)&(seed_summary.task=='pooled')].iloc[0]
   assert a.n_seeds==5
   replace_cell(c,f'{a.RMSE_seed_mean:.3f} ± {a.RMSE_seed_sd:.3f}')
   seed_rows.append(dict(table=4,arm=arm,schema=schema,mean=float(a.RMSE_seed_mean),sd=float(a.RMSE_seed_sd),n=5))
 direct=pd.read_csv(ROOT.parent/'revision_v16/analysis/direct_metrics.csv');frozen=pd.read_csv(ROOT.parent/'revision_v16/analysis/ablation_metrics.csv')
 route_specs=[('raw-molformer','linear'),('raw-molformer','lora'),('raw-molformer','full'),('expert','partial'),None]
 for r,specification in zip(tables[5].findall('w:tr',NS)[1:],route_specs):
  cells=r.findall('w:tc',NS)
  if specification:
   arm,mode=specification;a=direct[(direct.arm==arm)&(direct['mode']==mode)&(direct.task=='pooled')]
   if a.empty and mode=='linear':a=direct[(direct.arm==arm)&(direct['mode']=='frozen')&(direct.task=='pooled')]
  else:a=frozen[(frozen.arm=='expert')&(frozen.variant=='intact')&(frozen.task=='pooled')&frozen.seed.isin([0,1,2])]
  for c,schema in zip(cells[2:],['cation','scaffold','full-QAC105']):
   values=a[a.schema==schema].RMSE.to_numpy();assert len(values)==3
   mean,sd=float(values.mean()),float(values.std(ddof=1));replace_cell(c,f'{mean:.3f} ± {sd:.3f}')
   seed_rows.append(dict(table=6,route=h.text(cells[0]),schema=schema,mean=mean,sd=sd,n=3))
 # Captions and methods explicitly distinguish fold SD, seed SD and bootstrap CIs.
 changes={
 'Table 1.':'Table 1. Original reported prediction comparison, followed by newly reconstructed five-fold CV of the saved human-guided representation. The upper block retains the original holdout values and rounding correction; the three lower rows give RMSE and R² as mean ± fold SD (five row-wise folds, ddof=0). These CV means are new calculations and do not supply error bars for the upper block. Full fold scores and raw-feature controls are in Table S40.',
 'Table 2.':'Table 2. Original reported expert versus full-corpus quantitative comparison, followed by separate new CV rows for the saved human-guided encoder. The lower rows give mean ± SD over five row-wise folds, with no matched full-corpus quantitative CV available. Original source comparison, new CV and QAC-only ablation remain different evidence branches.',
 'Table 3.':'Table 3. Pooled exact-endpoint RMSE for newly executed grouped and OOD validation of archived reference representations. Human features use encoder_borderline_smote.pth; the QAC-binned ablation uses analysis/encoder_reg_only.pth and is not the full-corpus model from Table 2. Per-fold means and SD are reported separately in Table S42; they are not attached to the pooled scores here.',
 'Table 4.':'Table 4. Compact reference-architecture controls with native categorical target coding. Mean ± sample SD of complete seed-specific pooled RMSE (five paired source seeds, ddof=1), including the fixed OOD-17 cohort. This is source-seed variability, not fold SD or a 95% CI. Raw features are a single fixed reference without an invented SD.',
 'Table 5.':'Table 5. Separate-endpoint decoders on archived reference representations. Values are pooled exact-endpoint RMSE from one source checkpoint. Modern pipelines include train-only PCA32. Five-fold score means and SD are reported separately in Table S42; the single OOD fit has no fold or source-seed SD.',
 'Table 6.':'Table 6. Separate completed backbone-adaptation comparison: mean ± sample SD of complete seed-specific pooled RMSE over three paired source/target runs (ddof=1). The two human prediction routes use the same source seeds 0–2. Variability is over repeated training runs, not CV folds or a 95% CI.'}
 for node in body:
  text=h.text(node)
  for prefix,new in changes.items():
   if text.startswith(prefix):h.replace(node,new);break
  if text.startswith('We reconstructed nine original-108 configurations'):
   anchor=node
   extra=p('To restore the author’s uncertainty-reporting approach, we additionally executed five-fold row-wise KFold with shuffle=True and random_state=42, retaining the saved raw and human features and the recovered CatBoost budget. Six representation/coding combinations required 30 fits. Separate organism and endpoint categorical columns reproduce the April CV coding; native task_id follows the May variant. The text-code human endpoint R² means ± fold SD are 0.512 ± 0.100, 0.449 ± 0.213, 0.717 ± 0.081 and 0.643 ± 0.051. These approximate-reconstruction CV results differ from the historical single-holdout outputs and are shown as their own rows in Tables 1–2. The original task-vector cache remains absent. Row-wise CV can share a molecule across tasks and does not replace the 105-molecule grouped tests or the untouched 17-molecule OOD evaluation.')
 h.add_sequence(body,list(body)[list(body).index(anchor)+1],[extra])
 heading=next(x for x in body if h.text(x)=='4.3.4 Target cohorts, uncertainty and modern models')
 note=p('Uncertainty notation follows the source of repetition. Reconstructed row-wise CV and grouped fold summaries use mean ± SD across five fold scores with ddof=0, matching the original numpy.std convention. Repeated source/target fits use mean ± sample SD across the specified source seeds with ddof=1. Neither quantity is a 95% confidence interval. The separately reported paired bootstrap intervals remain contrasts conditional on the declared folds and trained seeds. A single OOD fit from one archived checkpoint has no CV-fold or source-seed SD; no neighbouring configuration supplies one.')
 h.add_sequence(body,heading,[note]);v.unique_ids(tree);h.write(files,tree,MAIN);v.TITLE=b.TITLE
 v.exports(files,tree,ROOT/'manuscript_v19_readable.md',ROOT/'manuscript_v19.html')
 # Keep every pre-existing SI table and figure; append a compact audit trail.
 sif,sit,sib=v.read_doc(b.SI);st=next(t for t in sib.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
 snormal=next(x for x in sib if h.text(x));sp=lambda text,level=None:v.paragraph(snormal,text,level,marked=text.startswith('[COAUTHORS'))
 h.replace(list(sib)[0],'Supporting Information — author workflows, CV and source-seed variability')
 new=[sp('S32. CV, seed variability and continuity with the author workflow',1),
 sp('Original reported single-holdout results remain unchanged. The new row-CV experiment uses the saved human encoder, preserving its historical source SMOTE state, and the original 108 worksheet records representing 105 unique full salts. It does not retrain the encoder or use any OOD compound. The missing historical text cache makes the text variant an approximate reconstruction. All six raw/human coding combinations and 30 fits are retained; no configuration was selected by OOD performance.'),
 sp('Table S40. New five-fold reconstruction of the author’s row-wise multitask evaluation. Mean ± SD of five fold scores, ddof=0; these are not recovered uncertainty for the historical Tables 1–2 holdout values.'),
 h.table(st,[['Representation / coding','Endpoint','Folds','RMSE mean ± SD','R² mean ± SD']]+[[r.representation+' / '+r.encoding,r.task,5,f'{r.RMSE_mean:.4f} ± {r.RMSE_sd:.4f}',f'{r.R2_mean:.4f} ± {r.R2_sd:.4f}'] for r in rowcv.itertuples()]),
 sp('Row-level KFold does not enforce molecule separation: different endpoint records of the same salt can occur in training and validation. The per-fold overlap counts are preserved in each configuration manifest. This estimates the declared row-level problem, not strict transfer to a new molecule. The cation/scaffold tests and OOD-17 remain distinct.'),
 sp('Table S41. Mean ± sample SD over complete compact source-seed runs, ddof=1. At least two source runs are required; single-seed task-code substitutions are not assigned an SD.'),
 h.table(st,[['Arm / coding','Regime / endpoint','Seeds','RMSE mean ± SD','R² mean ± SD']]+[[r.arm+' / '+r.encoding,r.schema+' / '+r.task,r.n_seeds,f'{r.RMSE_seed_mean:.4f} ± {r.RMSE_seed_sd:.4f}','—' if r.task=='pooled' else f'{r.R2_seed_mean:.4f} ± {r.R2_seed_sd:.4f}'] for r in seed_summary[seed_summary.n_seeds>=2].itertuples()]),
 sp('Table S42. Five-fold variability of the archived-feature and modern-decoder grouped validation. Mean ± fold SD, ddof=0. These unweighted fold means can differ from pooled out-of-fold RMSE/R²; the pooled values remain in main Tables 3 and 5. No OOD-fold SD is calculated.'),
 h.table(st,grouped_rows()),
 sp('Table S43. Recovered original CV uncertainty for linear representation probes. These metrics concern coordinate reconstruction, not antibacterial endpoint regression.'),
 h.table(st,[['Probe','Folds','R² mean','Fold SD','Provenance'],['MolFormer → human encoder',5,'0.891','0.037','May causal_final cell5, saved output'],['Human encoder → MolFormer',5,'0.844','0.060','May causal_final cell5, saved output']]),
 sp('Table S44. Relationship between the author’s method and the added calculations.'),
 h.table(st,[['Calculation','Representation / encoder','Target learner','Continuity','Declared changes'],
 ['Original Tables 1–2','Author source models','Original reported models','Preserved original results','Rounding correction and explicit provenance'],
 ['New original-row CV','Saved raw / human compact encoder','CatBoost 500/depth6/.05/42','Frozen features, saved encoder, author CV coding','October text cache; recorded environment; explicit 5 folds'],
 ['105-QAC grouped and 17-OOD tests','Saved raw / human compact encoder','Same CatBoost budget','Original two-stage prediction route','Cation/scaffold split; exact/bound OOD registry'],
 ['Matched compact source controls','768→512→384→256, frozen MolFormer','Same CatBoost budget','Original architecture; human/binary contrastive objective','Common excluded-target source; no SMOTE; five paired seeds'],
 ['Modern TabPFN/TabFM/AutoGluon','Saved raw / human encoder','New tabular decoders','Same target registers and archived features','Train-only PCA32 and model-specific budgets'],
 ['Graph and direct fine-tuning','Chemprop / adapted backbone','Graph head / direct head','Independent benchmark against the same targets','Different architecture, objectives and adaptation budgets']]),
 sp('All mean±SD entries identify the source of variability and number of repeats. They are descriptive spread estimates, not automatically 95% confidence intervals. Existing paired bootstrap intervals are retained unchanged. A missing SD is not replaced by zero, a neighbouring model, an OOD bootstrap width or a different split.')]
 sec=sib.find('w:sectPr',NS);h.add_sequence(sib,sec,new);v.unique_ids(sit);h.write(sif,sit,SI)
 v.exports(sif,sit,ROOT/'supplement_v19_readable.md',ROOT/'Supplementary_Information_v19.html')
 result=dict(base_main_sha256=sha(b.MAIN),base_SI_sha256=sha(b.SI),main=str(MAIN),main_sha256=sha(MAIN),SI=str(SI),SI_sha256=sha(SI),
  original_table_values_unchanged=True,new_CV_rows_per_original_table=3,original_probe_SD_restored=True,
  main_seed_SD_entries=seed_rows,rowcv_fits=30,grouped_variability_tables=True,
  original_historical_holdout_SD='Not identified; no SD was invented or attached from another protocol',
  methodology_continuity_table='S44',source_v5_sha256=sha(b.SOURCE))
 (ROOT/'revision_manifest.json').write_text(json.dumps(result,indent=2));print('Saved',MAIN.name,SI.name)
def grouped_rows():
 core=pd.read_csv(ROOT/'analysis/core_fold_summary.csv');modern=pd.read_csv(ROOT/'analysis/modern_fold_summary.csv')
 result=[['Representation / decoder','Regime / endpoint','Folds','RMSE mean ± SD','R² mean ± SD']]
 core=core[core.name.isin(['v5_raw','v5_human','v5_qac_ablation'])]
 for r in core.itertuples():result.append([r.name+' / '+r.encoding,r.schema+' / '+r.task,5,f'{r.RMSE_fold_mean:.4f} ± {r.RMSE_fold_sd:.4f}','—' if r.task=='pooled' else f'{r.R2_fold_mean:.4f} ± {r.R2_fold_sd:.4f}'])
 for r in modern.itertuples():result.append([r.representation+' / '+r.model,r.schema+' / '+r.task,5,f'{r.RMSE_fold_mean:.4f} ± {r.RMSE_fold_sd:.4f}','—' if r.task=='pooled' else f'{r.R2_fold_mean:.4f} ± {r.R2_fold_sd:.4f}'])
 return result
if __name__=='__main__':main()
