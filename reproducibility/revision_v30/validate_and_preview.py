"""Check source preservation, table/figure references and fonts; export a readable HTML."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib, html, json, re
import pymupdf

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W=NS['w'];R=NS['r']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(n):return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
def package(p):
    with ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def table_cells(n):return [[text(c) for c in row.findall('{'+W+'}tc')] for row in n.findall('{'+W+'}tr')]

m=json.loads((ROOT/'revision_manifest.json').read_text())
files=package(ROOT/'Supplementary_Information_v30.docx');root=E.fromstring(files['word/document.xml']);body=list(root.find('{'+W+'}body'))
oldfiles=package(COMA/'reproducibility/revision_v27/Supplementary_Information_v27.docx');oldbody=list(E.fromstring(oldfiles['word/document.xml']).find('{'+W+'}body'))
def tables(b):
    result={}
    for i,n in enumerate(b):
        match=re.match(r'Table S(\d+)\.',text(n))
        if match:result[int(match[1])]=next(c for c in b[i+1:] if c.tag=='{'+W+'}tbl')
    return result
current=tables(body);original=tables(oldbody)
checks=[]
for a in m['tables']:
    if isinstance(a['old'],int):
        assert table_cells(original[a['old']])==table_cells(current[a['number']]),a
        checks.append({'source_table':a['old'],'current_table':a['number'],'cells_identical':True})
tableids=set(current);figureids={int(re.match(r'Figure S(\d+)\.',text(n))[1]) for n in body if re.match(r'Figure S(\d+)\.',text(n))}
assert tableids==set(range(1,len(m['tables'])+1)),tableids
assert figureids==set(range(1,max(figureids)+1)),figureids
main=package(m['aligned_main']);source=package(COMA/'2026_10_14_Paper_2_edited-v29_explainability_figure.docx')
assert set(main)==set(source)
assert all(main[n]==source[n] for n in source if n!='word/document.xml')
sourcebody=list(E.fromstring(source['word/document.xml']).find('{'+W+'}body'));newbody=list(E.fromstring(main['word/document.xml']).find('{'+W+'}body'))
assert len(sourcebody)==len(newbody)
expected={r['body_index']:(r['before'],r['after']) for r in m['main_changes']}
for i,(a,b) in enumerate(zip(sourcebody,newbody)):
    if i in expected:assert (text(a),text(b))==expected[i]
    else:assert E.tostring(a)==E.tostring(b),i
main_refs=[]
for i,n in enumerate(newbody):
    t=text(n)
    for kind,ids in [('Table',tableids),('Figure',figureids)]:
        for match in re.finditer(kind+r's?\s+S\d+(?:\s*[–−-]\s*S?\d+)?(?:\s*(?:,|and)\s*S\d+)*',t):
            nums=[int(x) for x in re.findall(r'\bS(\d+)',match.group())]
            assert all(x in ids for x in nums),(i,t,nums)
            main_refs.append({'body_index':i,'kind':kind,'numbers':nums})
fonts=set(root.xpath('//w:rFonts/@w:ascii',namespaces=NS))
assert 'Times New Roman' in fonts,fonts
for p,h in m['source_hashes'].items():assert sha(p)==h,p
assert sha(ROOT/'SI_v27_full_archive.docx')==sha(COMA/'reproducibility/revision_v27/Supplementary_Information_v27.docx')

assets=ROOT/'preview_assets';assets.mkdir(exist_ok=True)
rels={r.get('Id'):r.get('Target') for r in E.fromstring(files['word/_rels/document.xml.rels'])}
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Supporting Information v30</title><style>body{font-family:"Times New Roman",Times,serif;color:#111;line-height:1.35;max-width:960px;margin:40px auto;padding:0 25px}h1,h2{margin-top:28px}h1{font-size:18px}h2{font-size:15px}p{font-size:12.5px}.caption{font-size:11px;color:#333}table{border-collapse:collapse;width:100%;font-size:10.5px;margin:12px 0 22px}td{padding:5px;border:1px solid #ccc;vertical-align:top}tr:first-child{background:#eee}img{max-width:100%;height:auto;display:block;margin:auto}a{color:#063}nav{padding:14px;background:#f7f7f7}</style><body><nav><strong>Supporting Information</strong><p>Times New Roman · tables cited by the main text</p>']
for n in body:
    t=text(n)
    if re.match(r'S\d+\. ',t) and len(t)<120:parts.append(f'<a href="#s{t.split(".")[0][1:]}">{html.escape(t)}</a><br>')
parts.append('</nav>')
imagecount=0
for n in body:
    if n.tag=='{'+W+'}tbl':
        parts.append('<table>')
        for row in n.findall('{'+W+'}tr'):
            parts.append('<tr>')
            for c in row.findall('{'+W+'}tc'):
                span=c.find('w:tcPr/w:gridSpan',NS);attr=''
                if span is not None:attr=' colspan="'+span.get('{'+W+'}val')+'"'
                parts.append('<td'+attr+'>'+html.escape(text(c))+'</td>')
            parts.append('</tr>')
        parts.append('</table>');continue
    if n.tag!='{'+W+'}p':continue
    for blip in n.xpath('.//a:blip',namespaces=NS):
        rid=blip.get('{'+R+'}embed')
        if not rid:continue
        target=rels[rid];part='word/'+target if not target.startswith('/') else target[1:]
        imagecount+=1;dest=assets/f'image{imagecount:02d}{Path(part).suffix}';dest.write_bytes(files[part]);parts.append(f'<img src="preview_assets/{dest.name}" alt="SI figure {imagecount}">')
    t=text(n)
    if not t:continue
    cls=' class="caption"' if re.match(r'(Figure|Table|Scheme) S\d+\.',t) else ''
    style=n.find('w:pPr/w:pStyle',NS);sty=style.get('{'+W+'}val') if style is not None else ''
    tag='h1' if sty in ['Heading1','Title'] else ('h2' if sty=='Heading2' else 'p')
    anchor=' id="s'+t.split('.')[0][1:]+'"' if tag=='h1' and re.match(r'S\d+\.',t) else ''
    parts.append(f'<{tag}{anchor}{cls}>'+html.escape(t)+f'</{tag}>')
parts.append('</body></html>');(ROOT/'Supplementary_Information_v30.html').write_text('\n'.join(parts))
assert imagecount==len(figureids), (imagecount, figureids)
report={'copied_table_numeric_cells':checks,'tables':len(tableids),'figures':sorted(figureids),'main_reference_checks':main_refs,'DOCX_run_fonts':sorted(fonts),'author_placeholders':m['pending_author_material'],'font':'Times New Roman'}
(ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'checked_tables':len(checks),'total_tables':len(tableids),'figures':len(figureids),'main_reference_checks':len(main_refs),'fonts':'Times New Roman','source_preservation':'passed','preview':str(ROOT/'Supplementary_Information_v30.html')},ensure_ascii=False,indent=2))
