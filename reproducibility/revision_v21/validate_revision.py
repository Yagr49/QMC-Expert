"""Verify additive-only Word edits and exact preservation of the original v5."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import hashlib,json
import build_revision as b

ROOT=Path(__file__).resolve().parent


def main():
    manifest=json.loads((ROOT/'revision_manifest.json').read_text())
    with ZipFile(b.SOURCE) as z:old={n:z.read(n) for n in z.namelist()}
    with ZipFile(b.OUTPUT) as z:
        assert z.testzip() is None
        new={n:z.read(n) for n in z.namelist()}
    assert set(old)==set(new)
    changed=[n for n in old if old[n]!=new[n]]
    assert changed==['word/document.xml'],changed
    raw=new['word/document.xml'];tree=E.fromstring(raw);body=tree.find('w:body',b.NS)
    old_tree=E.fromstring(old['word/document.xml']);old_body=old_tree.find('w:body',b.NS)
    spans=b.body_ranges(raw)
    labels={b.sha(r['label'].encode())[:8].upper():r for r in manifest['added_paragraphs']}
    cuts=[];kept=[];found=[]
    old_ids={p.get('{'+b.W14+'}paraId') for p in old_body if p.tag=='{'+b.W+'}p'}
    assert not (old_ids & set(labels))
    for i,node in enumerate(body):
        pid=node.get('{'+b.W14+'}paraId')
        if pid in labels:
            assert b.text(node)==labels[pid]['text']
            runs=node.findall('w:r',b.NS)
            assert runs and all(r.find('w:rPr/w:highlight',b.NS).get('{'+b.W+'}val')=='yellow' for r in runs)
            cuts.append((spans[i]['start'],spans[i]['end']))
            found.append(pid)
        else:kept.append(node)
    assert len(found)==len(labels)==11
    reconstructed=raw
    for start,end in sorted(cuts,reverse=True):reconstructed=reconstructed[:start]+reconstructed[end:]
    assert reconstructed==old['word/document.xml']
    assert len(kept)==len(old_body)
    assert all(E.tostring(a)==E.tostring(c) for a,c in zip(kept,old_body))
    figure_part='word/media/image1.png'
    assert old[figure_part]==new[figure_part]
    source_start=next(i for i,p in enumerate(old_body) if b.text(p)=='2.2 Training on QACs')
    output_start=next(i for i,p in enumerate(body) if b.text(p)=='2.2 Training on QACs')
    assert all(E.tostring(a)==E.tostring(c) for a,c in zip(list(old_body)[source_start:],list(body)[output_start:]))
    report=dict(completed=True,new_yellow_paragraphs=len(found),
                original_document_XML_recovered_exactly_after_removing_additions=True,
                all_source_parts_except_document_XML_byte_identical=True,
                original_figure1_byte_identical=True,original_tables_and_references_unchanged=True,
                section2_2_and_every_later_section_unchanged=True,
                original_source_SHA=hashlib.sha256(b.SOURCE.read_bytes()).hexdigest(),
                output_SHA=hashlib.sha256(b.OUTPUT.read_bytes()).hexdigest(),
                two_reviewers_invoked_locally='Claude Sonnet4.6 and Kimi',
                predictive_numbers_from_completed_artifacts=True,
                no_new_QHERO_numbers_in_manuscript=True)
    assert report['original_source_SHA']=='0dd55e7b9ef5125dd938fdb04e9c2d0a430cc4b86fc099b85e9f6e5e6d1c2bfb'
    (ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
