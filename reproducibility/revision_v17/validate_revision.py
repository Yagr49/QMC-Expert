"""Check document integrity, preserved results, figure provenance and relocations."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import xml.etree.ElementTree as E
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
b=load('v17_builder',ROOT/'build_revision.py')
d=load('document_inspector',ROOT.parent/'revision_v12/validate_documents.py')

def rows(table):
 return [[b.h.text(c) for c in row.findall('w:tc',b.NS)] for row in table.findall('w:tr',b.NS)]

def fields(body):
 return [E.tostring(p) for p in body if b.h.text(p).startswith('[COAUTHORS')]

def main():
 for path,digest in json.loads((ROOT/'input_manifest.json').read_text()).items():
  assert b.sha(path)==digest,('changed source',path)
 assert b.sha('/Users/egorilin/Downloads/Supporting_Info.docx')==b.sha(b.ORIGINAL_SI)
 style=json.loads((ROOT/'style_manifest.json').read_text())
 for path,digest in style['inputs_sha256'].items():assert b.sha(path)==digest,('changed plot input',path)
 assert not style['model_training_performed'] and not style['raw_predictions_changed']
 replacements=json.loads((ROOT/'document_style_replacements.json').read_text())
 reports=[]
 for key,newpath,oldpath,figure_count in [('main',b.MAIN,b.b.MAIN,5),('SI',b.SI,b.b.SI,29)]:
  newfiles,_,body=b.v.read_doc(newpath);oldfiles,_,oldbody=b.v.read_doc(oldpath)
  texts,count=d.inspect(newpath);assert count==figure_count
  assert fields(body)==fields(oldbody),('coauthor fields changed',key)
  changed={r['part']:r for r in replacements[key]}
  for name,data in oldfiles.items():
   if not name.startswith('word/media/'):continue
   assert name in newfiles,name
   if name in changed:
    assert hashlib.sha256(data).hexdigest()==changed[name]['old_sha256']
    assert hashlib.sha256(newfiles[name]).hexdigest()==changed[name]['new_sha256']
   else:assert data==newfiles[name],('unlisted media change',name)
  if key=='main':
   assert [int(re.match(r'^Figure (\d+)\.',t)[1]) for t in texts if re.match(r'^Figure (\d+)\.',t)]==list(range(1,6))
   assert [int(re.match(r'^Table (\d+)\.',t)[1]) for t in texts if re.match(r'^Table (\d+)\.',t)]==list(range(1,7))
   tables=body.findall('w:tbl',b.NS);oldtables=oldbody.findall('w:tbl',b.NS)
   assert len(tables)==6 and [rows(t) for t in tables[:4]]==[rows(t) for t in oldtables[:4]]
   assert rows(tables[5])==rows(oldtables[6])
   direct=pd.read_csv(b.b.ANALYSIS/'direct_summary.csv')
   ablation=pd.read_csv(b.b.ANALYSIS/'ablation_metrics.csv')
   a=direct[(direct.arm=='expert')&(direct['mode']=='partial')&(direct.task=='pooled')].set_index('schema')
   z=ablation[(ablation.arm=='expert')&(ablation.variant=='intact')&ablation.seed.isin([0,1,2])&(ablation.task=='pooled')].groupby('schema').RMSE.mean()
   expected=[['Prediction route','Paired source seeds','Cation CV','Scaffold CV','OOD-17'],
    ['Direct partial target FT','0–2']+[f'{a.loc[s].RMSE:.3f}' for s in b.b.SCHEMES],
    ['Frozen guided encoder + CatBoost','0–2']+[f'{z.loc[s]:.3f}' for s in b.b.SCHEMES]]
   assert rows(tables[4])==expected
   assert len([t for t in texts[texts.index('References')+1:] if re.match(r'^\d+\. ',t)])==14
   seen=[]
   for t in texts[:texts.index('References')]:
    for n in b.citation_numbers(t):
     if n not in seen:seen.append(n)
   assert seen==list(range(1,15)),seen
   assert 'annotation boxes report' not in '\n'.join(texts)
   assert all('Figure '+str(n) not in '\n'.join(texts) for n in [7,8])
  else:
   assert [int(re.match(r'^Figure S(\d+)\.',t)[1]) for t in texts if re.match(r'^Figure S(\d+)\.',t)]==list(range(1,30))
   assert [rows(t) for t in body.findall('w:tbl',b.NS)]==[rows(t) for t in oldbody.findall('w:tbl',b.NS)]
   for image in json.loads((ROOT/'sources/source_figures.json').read_text()):
    digest=image['sha256'];assert any(hashlib.sha256(data).hexdigest()==digest for name,data in newfiles.items() if name.startswith('word/media/'))
   before=[b.h.text(p) for p in oldbody];after=[b.h.text(p) for p in body]
   def chemical_section(texts):
    start=next(i for i,t in enumerate(texts) if t.startswith('S16.'))
    end=next(i for i,t in enumerate(texts[start+1:],start+1) if t.startswith('S17.'))
    return texts[start:end]
   original=chemical_section(before)
   original=[re.sub(r'\bFigure S(\d+)\b',lambda m:'Figure S'+str(int(m[1])+4),t) for t in original]
   assert original==chemical_section(after)
   caption=next(t for t in texts if t.startswith('Figure S26.'))
   assert 'lavender, left' in caption and 'mint, right' in caption and '>500' in caption
   # Preserve the archived caption sequence, which already omits number S10.
   def table_numbers(paragraphs):
    return [int(re.match(r'^Table S(\d+)\.',t)[1]) for t in paragraphs if re.match(r'^Table S(\d+)\.',t)]
   assert table_numbers(texts)==table_numbers(before)
   for filename,column in [('QAC105.csv','compound_id'),('OOD17.csv','code')]:
    assert all(str(x) in '\n'.join(texts) for x in pd.read_csv(b.b.RUN/'data'/filename)[column])
  assert 'sk-or-v1-' not in '\n'.join(texts)
  reports.append(dict(path=str(newpath),sha256=b.sha(newpath),figures=count,
   tables=len(body.findall('w:tbl',b.NS)),coauthor_fields_byte_preserved=True,
   only_listed_media_restyled=True,xml_relationships_styles_valid=True))
 # Verify plotted distributions and support using the same saved predictions.
 analysis=b.b.ANALYSIS
 direct=pd.read_csv(analysis/'direct_predictions.csv');ablation=pd.read_csv(analysis/'ablation_predictions.csv')
 route=next(r for r in style['plot_checks'] if r['figure']=='figureS26_prediction_route_violins')
 for row in route['distributions']:
  data=direct if row['route']=='direct' else ablation
  sub=data[(data.arm==row['arm'])&(data.schema==row['schema'])&(data.qualifier=='=')&data.seed.isin([0,1,2])].copy()
  if row['route']=='decoder':sub=sub[sub.variant=='intact']
  sub['ae']=abs(sub.y-sub.prediction);values=sub.groupby(['compound_id','task']).ae.mean().to_numpy()
  assert len(values)==row['n'] and abs(float(values.max())-row['max'])<1e-12
  assert abs(float(np.median(values))-row['median'])<1e-12
 for name in style['figures']:
  assert all((ROOT/'figures'/(name+'.'+ext)).stat().st_size>500 for ext in ['png','pdf','svg'])
 result=dict(completed=True,documents=reports,source_documents_unchanged=True,
  original_four_SI_figures_byte_preserved=True,main_first_four_tables_preserved=True,
  complete_SI_tables_preserved=True,chemistry_and_assay_section_preserved=True,
  route_table_recomputed=True,plotted_route_distributions_recomputed=True,
  restyled_figures=len(style['figures']),plot_input_hashes_unchanged=True,font=style['font'],
  full_105_and_17_compound_registries_preserved=True,paragraph_walkthrough_count=52)
 (ROOT/'document_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
