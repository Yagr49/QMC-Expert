"""Meaningful provenance, cohort, numeric and native-Office checks for v18."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('builder',ROOT/'build_revision.py');d=load('inspector',ROOT.parent/'revision_v12/validate_documents.py')
def rows(table):return [[b.h.text(c) for c in r.findall('w:tc',b.NS)] for r in table.findall('w:tr',b.NS)]
def main():
 original,_,ob=b.v.read_doc(b.SOURCE);new,_,nb=b.v.read_doc(b.MAIN)
 source_manifest=json.loads((ROOT/'sources/source_docx_sha256.json').read_text())
 # The archived provenance record is a path->digest mapping.
 for path,digest in source_manifest.items():assert b.sha(path)==digest
 for path,data in original.items():
  if path.startswith(('word/media/','word/embeddings/')):assert new[path]==data,(path,'original asset changed')
 oldchem=[b.h.text(x) for x in list(ob)[100:180]]
 texts=[b.h.text(x) for x in nb];a=texts.index('4.1 Chemistry');z=texts.index('4.3 Computational and annotation protocol')
 assert texts[a:z]==oldchem,'Native v5 experimental text changed'
 oldtables=ob.findall('w:tbl',b.NS);tables=nb.findall('w:tbl',b.NS)
 assert len(oldtables)==2 and len(tables)==6
 for old,newtable in zip(oldtables,tables[:2]):
  aa=rows(old);bb=rows(newtable);assert len(aa)==len(bb)
  for ra,rb in zip(aa[:-1],bb[:-1]):
   assert [x.replace('ATCC 4300','ATCC 43300').replace('0.95 (R2=0.60)','0.95 (R2=0.59)') for x in ra]==rb,'Unlisted historical metric change'
 f,_,previous=b.v.read_doc(b.previous.MAIN)
 assert [b.h.text(x) for x in previous if b.h.text(x).startswith(('[COAUTHORS H','[COAUTHORS D'))]==[b.h.text(x) for x in nb if b.h.text(x).startswith(('[COAUTHORS H','[COAUTHORS D'))]
 reports=[]
 for path,expected in [(b.MAIN,8),(b.SI,30)]:
  tt,n=d.inspect(path);assert n==expected
  assert not any('sk-or-v1-' in t for t in tt)
  figs=[int(re.match(r'^Figure '+('S' if path==b.SI else '')+r'(\d+)\.',t)[1]) for t in tt if re.match(r'^Figure '+('S' if path==b.SI else '')+r'(\d+)\.',t)]
  assert figs==list(range(1,expected+1))
  reports.append(dict(path=str(path),sha256=b.sha(path),figures=n,xml_relationships_styles_valid=True))
 oldsi,_,oldbody=b.v.read_doc(b.previous.SI);sif,_,sib=b.v.read_doc(b.SI)
 for name,data in oldsi.items():
  if name.startswith(('word/media/','word/embeddings/')):assert sif[name]==data
 assert [rows(t) for t in oldbody.findall('w:tbl',b.NS)]==[rows(t) for t in sib.findall('w:tbl',b.NS)][:len(oldbody.findall('w:tbl',b.NS))]
 assert len(sib.findall('w:tbl',b.NS))==40
 registry=pd.read_csv(ROOT.parent/'v5_hypotheses_20261013/data/endpoint_registry.csv')
 q=registry[registry.cohort=='QAC105'];o=registry[registry.cohort=='OOD17']
 assert q.compound_id.nunique()==105 and len(q)==420 and o.compound_id.nunique()==17 and len(o)==68
 assert (o.qualifier=='=').sum()==67 and len(o[o.qualifier!='='])==1
 p=pd.read_csv(ROOT/'analysis/predictions.csv')
 assert np.isfinite(p.prediction).all()
 for (name,encoding),frame in p[p.cohort=='OOD17'].groupby(['name','encoding']):
  assert len(frame)==68 and frame.compound_id.nunique()==17
 for (name,encoding,schema),frame in p[p.cohort=='QAC105'].groupby(['name','encoding','schema']):
  assert len(frame)==420 and frame.compound_id.nunique()==105
 # Recompute every saved per-configuration loss from actual predictions.
 metrics=pd.read_csv(ROOT/'analysis/metrics.csv')
 for (name,encoding,cohort,schema),frame in p.groupby(['name','encoding','cohort','schema']):
  exact=frame[frame.qualifier=='=']
  for task in ['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC','pooled']:
   g=exact if task=='pooled' else exact[exact.task==task]
   row=metrics[(metrics.name==name)&(metrics.encoding==encoding)&(metrics.cohort==cohort)&(metrics.schema==schema)&(metrics.task==task)].iloc[0]
   err=g.prediction-g.y;assert abs(row.RMSE-np.sqrt(np.mean(err**2)))<1e-12 and row.n==len(g)
 replay=pd.read_csv(ROOT/'analysis/independent_replay.csv');assert len(replay)==9 and replay.max_prediction_difference.max()<1e-10
 man=json.loads((ROOT/'analysis/manifest.json').read_text());assert man['decoder_fits']==920
 assert all(s['completed'] and s['done']==88 for s in man['modern_status'].values())
 mp=pd.read_csv(ROOT/'analysis/modern_predictions.csv')
 for (model,rep,schema),g in mp.groupby(['model','representation','schema']):
  assert len(g)==(68 if schema=='full-QAC105' else 420)
 # Check active capacities and paired states from actual training records.
 snapshot=Path(man['main_snapshot']);tr=pd.read_csv(snapshot/'compact/training.csv')
 assert len(tr)==30 and (tr.encoder_parameters==691584).all() and (tr.updates==480).all()
 for seed,g in tr.groupby('seed'):assert g.initial_sha256.nunique()==g.batch_sha256.nunique()==1
 assert set(tr[tr.arm.isin(['human','mic_binary'])].active_trainable_parameters)=={741504}
 assert set(tr[tr.arm=='mic_continuous'].active_trainable_parameters)=={691841}
 # Confirm actual plotted distributions, including uncapped tails.
 plot=json.loads((ROOT/'check_figure_provenance.json').read_text())
 for r in plot['violin']:
  g=p[(p.arm==r['arm'])&(p.schema==r['schema'])&(p.encoding=='categorical')&(p.qualifier=='=')].copy()
  g['ae']=abs(g.prediction-g.y);values=g.groupby(['compound_id','task']).ae.mean()
  assert len(values)==r['n'] and abs(values.median()-r['median'])<1e-12 and abs(values.max()-r['max'])<1e-12
 for name in ['figure1_v5_guided_embedding_pipeline','figure6_v5_embedding_geometry','figure7_compact_real_shuffled_violins','figure8_v5_modern_decoders','figureS30_compact_paired_contrasts']:
  for ext in ['png','pdf','svg']:assert (ROOT/'figures'/(name+'.'+ext)).stat().st_size>1000
 assert texts.index(next(t for t in texts if t.startswith('The workflow separates three objects')))<texts.index(next(t for t in texts if t.startswith('Figure 1.')))
 result=dict(completed=True,documents=reports,source_v5_unchanged=True,original_two_tables_preserved_with_documented_edits=True,
  native_chemistry_assay_text_preserved=True,all_original_media_and_Office_objects_byte_preserved=True,
  original_SI_four_figures_and_all_prior_tables_preserved=True,SI_tables=40,full_QAC105_OOD17_preserved=True,
  all_core_metrics_recomputed_from_predictions=True,all_264_modern_fits_complete=True,
  independent_9_configuration_replay=True,paired_training_states_and_batches_verified=True,all_violin_support_and_tails_verified=True,
  historical_R2_output_provenance='Eight May values; not a replay of all original Tables1–2',
  full_corpus_quantitative_checkpoint='Unresolved, not replaced by QAC-binned surrogate')
 (ROOT/'document_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
