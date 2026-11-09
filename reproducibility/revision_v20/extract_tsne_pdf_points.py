"""Recover exact scatter-marker positions from the author's vector PDF, not pixels."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json
import numpy as np
from pypdf import PdfReader
from pypdf.generic import ContentStream
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parents[1]/'publication_tsne_before_after.pdf'
def matrix(values):
 a,b,c,d,e,f=map(float,values);return np.array([[a,c,e],[b,d,f],[0,0,1.]])
def main():
 reader=PdfReader(SOURCE);page=reader.pages[0];stream=ContentStream(page.get_contents(),reader)
 transform=np.eye(3);stack=[];records=[];order=Counter()
 mapping={'/M0':('before','Bad'),'/M1':('before','Good'),'/M2':('after','Bad'),'/M3':('after','Good')}
 for operands,operator in stream.operations:
  if operator==b'q':stack.append(transform.copy())
  elif operator==b'Q':transform=stack.pop()
  elif operator==b'cm':transform=transform@matrix(operands)
  elif operator==b'Do' and str(operands[0]) in mapping:
   name=str(operands[0]);panel,label=mapping[name];form=page['/Resources']['/XObject'][name].get_object()
   local=matrix(form.get('/Matrix',[1,0,0,1,0,0]));xy=(transform@local@np.array([0.,0.,1.]))[:2]
   records.append(dict(panel=panel,label=label,index_within_class=order[(panel,label)],x_pdf=float(xy[0]),y_pdf=float(xy[1])))
   order[(panel,label)]+=1
 assert not stack
 assert order==Counter({('before','Bad'):172,('before','Good'):49,('after','Bad'):172,('after','Good'):49})
 target=ROOT/'tsne_pdf_marker_coordinates.csv'
 with target.open('w') as out:
  writer=csv.DictWriter(out,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 text=page.extract_text();assert 'Silhouette = 0.007' in text and 'Silhouette = 0.107' in text
 manifest=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
  extraction='PDF Form XObject marker centres, exact graphics-state affine transforms',
  points_per_panel=221,classes={'Bad':172,'Good':49},source_reported_silhouette={'before':.007,'after':.107},
  manuscript_raster_reported_after=.108,archive_variant_discrepancy=True,
  no_TSNE_recomputation=True,no_points_selected_or_added=True,coordinate_units='PDF display points, not original high-dimensional features',
  molecular_identity_not_recovered=True,original_filename='publication_tsne_before_after.pdf',
  coordinate_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
 (ROOT/'tsne_source_provenance.json').write_text(json.dumps(manifest,indent=2));print('Recovered all 442 PDF scatter-marker centres, with original class counts.')
if __name__=='__main__':main()
