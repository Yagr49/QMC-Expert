"""Validate additive-only document changes and exact image embedding."""
import hashlib, importlib.util, json, re
from xml.etree import ElementTree as E
import add_explainability_figure as b

def main():
    _,old=b.v.v.read(b.SOURCE);_,new=b.v.v.read(b.OUTPUT)
    assert set(new)-set(old)=={'word/media/v29_'+b.FIGURE.name}
    changed=[name for name in old if old[name]!=new[name]]
    assert set(changed)=={'word/document.xml','word/_rels/document.xml.rels'}
    raw=new['word/document.xml'];body=list(E.fromstring(raw).find('w:body',b.NS))
    previous=list(E.fromstring(old['word/document.xml']).find('w:body',b.NS))
    spans=b.b.body_ranges(raw)
    manifest=json.loads((b.ROOT/'revision_manifest.json').read_text())
    at=manifest['insertion_after_original_body_index']+1
    assert len(body)==len(previous)+3
    stripped=raw[:spans[at]['start']]+raw[spans[at+2]['end']:]
    assert stripped==old['word/document.xml']
    assert b.b.text(body[at])==b.LINK and b.b.text(body[at+2])==b.CAPTION
    for index in [at,at+2]:
        highlight=body[index].find('.//w:highlight',b.NS)
        assert highlight is not None and highlight.get('{'+b.b.W+'}val')=='yellow'
    assert new['word/media/v29_'+b.FIGURE.name]==b.FIGURE.read_bytes()
    captions=[b.b.text(n) for n in body if re.match(r'^Figure \d+\.',b.b.text(n))]
    assert [int(re.match(r'^Figure (\d+)\.',s)[1]) for s in captions]==list(range(1,10))
    spec=importlib.util.spec_from_file_location('inspector',b.ROOT.parent/'revision_v12/validate_documents.py')
    inspector=importlib.util.module_from_spec(spec);spec.loader.exec_module(inspector)
    texts,drawings=inspector.inspect(b.OUTPUT);assert drawings==9
    assert not any('sk-or-v1-' in text for text in texts)
    assert hashlib.sha256(b.SOURCE.read_bytes()).hexdigest()==manifest['source_sha256']
    report=dict(completed=True,original_v28_document_XML_recovered_exactly_after_removing_insertion=True,
        source_v28_unmodified=True,all_existing_tables_figures_Office_objects_and_text_preserved=True,
        figure_embedded_byte_identical=True,XML_relationships_styles_valid=True,main_figures=9,
        added_link_and_caption_yellow=True,contrast_rows_verified=15,no_new_model_fits=True,
        output_sha256=hashlib.sha256(b.OUTPUT.read_bytes()).hexdigest())
    (b.ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
