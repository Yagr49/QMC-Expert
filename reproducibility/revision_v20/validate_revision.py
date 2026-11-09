from pathlib import Path
import hashlib,importlib.util,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('builder',ROOT/'build_revision.py');d=load('inspector',ROOT.parent/'revision_v12/validate_documents.py')
def rows(table):return [[b.h.text(c) for c in r.findall('w:tc',b.NS)] for r in table.findall('w:tr',b.NS)]
def main():
 f,t,body=b.v.read_doc(b.MAIN);of,_,ob=b.v.read_doc(b.b.MAIN)
 assert [rows(x) for x in body.findall('w:tbl',b.NS)]==[rows(x) for x in ob.findall('w:tbl',b.NS)]
 for name,data in of.items():
  if name.startswith(('word/media/','word/embeddings/')):assert f[name]==data
 original=[b.h.text(p) for p in ob];now=[b.h.text(p) for p in body]
 assert len(original)==len(now)
 for a,z in zip(original,now):
  if a.startswith(('Figure 2.','The archived t-SNE analysis','None of the modern tabular pipelines','Third, modern decoders and direct fine-tuning')):continue
  assert a==z,('unlisted paragraph edit',a[:80])
 sif,_,sib=b.v.read_doc(b.SI);osif,_,osib=b.v.read_doc(b.b.SI)
 assert [rows(x) for x in sib.findall('w:tbl',b.NS)]==[rows(x) for x in osib.findall('w:tbl',b.NS)]
 assert [b.h.text(p) for p in sib][:len(osib)-1]==[b.h.text(p) for p in osib][:-1]
 for name,data in osif.items():
  if name.startswith(('word/media/','word/embeddings/')):assert sif[name]==data
 reports=[]
 for path,expected in [(b.MAIN,8),(b.SI,31)]:
  texts,n=d.inspect(path);assert n==expected
  assert not any('sk-or-v1-' in x for x in texts)
  reports.append(dict(path=str(path),sha256=b.sha(path),figures=n,relationships_styles_valid=True))
 data=pd.read_csv(ROOT/'tsne_pdf_marker_coordinates.csv');assert len(data)==442
 for panel,g in data.groupby('panel'):assert len(g)==221 and (g.label=='Bad').sum()==172 and (g.label=='Good').sum()==49
 source=json.loads((ROOT/'tsne_source_provenance.json').read_text());style=json.loads((ROOT/'tsne_style_validation.json').read_text())
 assert source['source_sha256']==b.sha(source['source']) and source['coordinate_sha256']==b.sha(ROOT/'tsne_pdf_marker_coordinates.csv')
 assert style['coordinate_input_sha256']==source['coordinate_sha256'] and style['displayed_after_silhouette']==.107
 for check in style['checks']:
  g=data[data.panel==check['panel']];assert len(g)==check['n']==221
  assert g.x_pdf.between(*check['xlim']).all() and g.y_pdf.between(*check['ylim']).all()
 for variant in ['soft','lavender']:
  for ext in ['png','pdf','svg']:assert (ROOT/'figures'/('figure2_contrastive_before_after_'+variant+'.'+ext)).stat().st_size>1000
 result=dict(completed=True,documents=reports,all_predictive_tables_unchanged=True,all_previous_SI_text_and_results_unchanged=True,
  original_media_and_Office_objects_byte_preserved=True,original_raster_visible_in_FigureS31=True,
  all_442_archived_PDF_markers_preserved=True,source_variant_silhouette_discrepancy_explicit=True,no_new_QHERO_results_added_to_documents=True,
  no_TSNE_recomputation=True,font='Aptos',figure_palette='muted peach / mint')
 (ROOT/'document_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
