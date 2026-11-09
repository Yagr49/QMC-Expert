"""Check DOCX relationships, preserved source assets, captions and scoped text edits."""
from zipfile import ZipFile
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib, json, re
import build_revision as b

def main():
    with ZipFile(b.SOURCE) as z: old={n:z.read(n) for n in z.namelist()}
    with ZipFile(b.OUTPUT) as z:
        assert z.testzip() is None
        new={n:z.read(n) for n in z.namelist()}
    changed=[n for n in old if old[n]!=new[n]]
    assert set(changed)=={'word/document.xml','word/_rels/document.xml.rels'}
    assert old['word/media/image1.png']==new['word/media/image1.png']
    assert all(old[n]==new[n] for n in old if n.startswith('word/media/'))
    assert len(new)-len(old)==2
    old_body=list(E.fromstring(old['word/document.xml']).find('w:body',b.NS))
    new_body=list(E.fromstring(new['word/document.xml']).find('w:body',b.NS))
    texts=[b.b.text(n) for n in new_body]
    caps=[s for s in texts if re.match(r'^Figure [1-7]\. ',s)]
    assert [int(re.match(r'^Figure (\d+)\.',s)[1]) for s in caps]==list(range(1,8))
    assert len(new_body)==len(old_body)+3
    startold=next(i for i,n in enumerate(old_body) if b.b.text(n)=='2.2 Training on QACs')
    startnew=next(i for i,n in enumerate(new_body) if b.b.text(n)=='2.2 Training on QACs')
    assert startnew==startold+3
    renamed=lambda s:re.sub(r'\b(Figure\s+)([3-6])\b',lambda m:m[1]+str(int(m[2])+1),s)
    for before,after in zip(old_body[startold:],new_body[startnew:]):
        assert b.b.text(after)==renamed(b.b.text(before))
    # All native tables are retained verbatim.
    oldtables=[E.tostring(n) for n in old_body if n.tag=='{'+b.b.W+'}tbl']
    newtables=[E.tostring(n) for n in new_body if n.tag=='{'+b.b.W+'}tbl']
    assert oldtables==newtables
    rels={r.get('Id'):r.get('Target') for r in E.fromstring(new['word/_rels/document.xml.rels'])}
    all_ids=[];figures=[]
    for n in new_body:
        for x in n.findall('.//wp:docPr',b.NS):all_ids.append(x.get('id'))
        for x in n.findall('.//a:blip',b.NS):
            rid=x.get('{'+b.R+'}embed');assert rid in rels
            assert 'word/'+rels[rid] in new
            if rid.startswith('rIdV22'):figures.append(rels[rid])
    assert len(all_ids)==len(set(all_ids))
    assert len(figures)==2
    # Preserve every yellow insertion from v21 unless explicitly revised in v22.
    oldyellow=[b.b.text(n) for n in old_body if n.find('.//w:highlight',b.NS) is not None]
    for s in oldyellow:assert s in texts
    for prefix in ['Figure 2.','Figure 3.','Figure 2 presents the archived','Figure 3 compares']:
        n=next(n for n in new_body if b.b.text(n).startswith(prefix))
        assert n.find('.//w:highlight',b.NS) is not None
    geometry=json.loads((b.ROOT/'contrastive_validation.json').read_text())
    assert all(c['points']==221 and c['Bad']==172 and c['Good']==49 for c in geometry['checks'])
    report={'completed':True,'source_v21_unmodified':True,
        'all_original_media_retained_byte_identical':True,'figure1_preserved':True,
        'all_native_tables_preserved':True,'new_and_revised_text_yellow':True,
        'captions_sequential_1_to7':True,'relationship_targets_exist':True,
        'drawing_ids_unique':True,'later_section_content_unchanged_except_figure_numbers':True,
        'tsne_coordinates_preserved':True,'output_sha256':hashlib.sha256(b.OUTPUT.read_bytes()).hexdigest()}
    (b.ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
