"""Update v21 graphics and add the completed adaptation figure in Section 2.1."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import base64, copy, hashlib, html, importlib.util, json, re
from PIL import Image

ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
SOURCE=COMA/'2026_10_14_Paper_2_edited-v21_v5_intro_2_1_yellow.docx'
OUTPUT=COMA/'2026_10_14_Paper_2_edited-v22_pastel_adaptation_figures.docx'
spec=importlib.util.spec_from_file_location('v21',ROOT.parent/'revision_v21/build_revision.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
NS=dict(b.NS,a='http://schemas.openxmlformats.org/drawingml/2006/main',
    wp='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    pic='http://schemas.openxmlformats.org/drawingml/2006/picture')
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'

def sha(data): return hashlib.sha256(data).hexdigest()

def figure(template,path,rid,uid):
    node=copy.deepcopy(template)
    node.set('{'+b.W14+'}paraId',sha(rid.encode())[:8].upper())
    for n in node.findall('.//a:blip',NS): n.set('{'+R+'}embed',rid)
    for n in node.findall('.//wp:docPr',NS)+node.findall('.//pic:cNvPr',NS):
        n.set('id',str(uid));n.set('name',path.stem)
    width=5731510
    with Image.open(path) as im: height=round(width*im.height/im.width)
    for n in node.findall('.//wp:extent',NS)+node.findall('.//a:xfrm/a:ext',NS):
        n.set('cx',str(width));n.set('cy',str(height))
    for n in node.findall('.//w:lastRenderedPageBreak',NS):
        for parent in node.iter():
            if n in list(parent): parent.remove(n);break
    return node

def main():
    with ZipFile(SOURCE) as z:
        infos=z.infolist();files={i.filename:z.read(i.filename) for i in infos}
    original=files['word/document.xml']
    body=E.fromstring(original).find('w:body',NS);old=list(body)
    spans=b.body_ranges(original);edits=[];records=[]
    f2_index=next(i for i,n in enumerate(old) if b.text(n).startswith('Figure 2.'))
    image_template=old[f2_index-1]
    tsne=ROOT/'figures/figure2_contrastive_enhanced.png'
    violins=ROOT/'figures/figure3_backbone_route_error_violins.png'
    assert tsne.exists() and violins.exists()
    replacements={f2_index-1:figure(image_template,tsne,'rIdV22TSNE',224001)}
    cap2=('Figure 2. Before (a) and after (b) expert-guided contrastive learning. '
        'All 221 marker positions and expert Good/Bad assignments per panel are retained '
        'from the archived vector PDF; typography and colours are updated. The PDF reports '
        'silhouette 0.007/0.107, whereas the original v5 raster reports 0.108 after training. '
        'Panel coordinates are independently scaled and are not aligned across embeddings. '
        'This display describes representation geometry, rather than quantitative predictive performance.')
    replacements[f2_index]=b.paragraph(old[f2_index],'v22_figure2_caption',cap2)
    paragraph_index=next(i for i,n in enumerate(old) if b.text(n).startswith('Figure 2 presents t-SNE'))
    description=('Figure 2 presents the archived t-SNE projections before and after contrastive '
        'refinement, preserving all display coordinates rather than rerunning the embedding. '
        'The vector source reports a silhouette score of 0.007 before and 0.107 after learning; '
        'the original manuscript raster reports 0.108 after learning. The original analysis also '
        'reports a Davies–Bouldin index of 6.54 versus 2.58 and a Calinski–Harabasz score of '
        '3.60 versus 22.08. These summaries describe label-associated geometry and are not '
        'recomputed from the plotted coordinates or used as evidence of quantitative or causal performance.')
    replacements[paragraph_index]=b.paragraph(old[paragraph_index],'v22_figure2_description',description)
    # Rename original Figure3–6 in every text run, including body cross-references.
    rename=lambda s:re.sub(r'\b(Figure\s+)([3-6])\b',lambda m:m[1]+str(int(m[2])+1),s)
    for i,n in enumerate(old):
        if i in replacements: continue
        if rename(b.text(n))!=b.text(n):
            changed=copy.deepcopy(n)
            # Match references spanning multiple runs without rewriting unrelated text.
            texts=changed.findall('.//w:t',NS)
            complete=''.join(t.text or '' for t in texts)
            matches=list(re.finditer(r'\bFigure\s+([3-6])\b',complete))
            offsets=[];at=0
            for t in texts:
                offsets.append((at,at+len(t.text or ''),t));at+=len(t.text or '')
            for match in reversed(matches):
                pos=match.start(1)
                for start,end,t in offsets:
                    if start<=pos<end:
                        local=pos-start;t.text=t.text[:local]+str(int(match[1])+1)+t.text[local+1:];break
            assert b.text(changed)==rename(b.text(n))
            replacements[i]=changed
    for i,node in replacements.items():
        value=E.tostring(node,encoding='utf-8')
        edits.append((spans[i]['start'],spans[i]['end'],value))
        records.append({'body_index':i,'text':b.text(node),'replacement_sha256':sha(value)})
    start2=next(i for i,n in enumerate(old) if b.text(n)=='2.2 Training on QACs')
    opening=('Figure 3 compares the distributions of absolute MIC/MBC prediction errors '
        'for frozen-head, LoRA, full-backbone and human-guided adaptation across cation, '
        'scaffold and independent OOD evaluation. The two human-guided routes use partial '
        'backbone adaptation and share source checkpoints; they are distinct from the '
        'external compact feature encoder described above.')
    caption=(ROOT/'figure3_caption_EN.txt').read_text().strip()
    assert caption.startswith('Figure 3.')
    insert_nodes=[b.paragraph(old[paragraph_index],'v22_figure3_link',opening),
        figure(image_template,violins,'rIdV22Violins',224002),
        b.paragraph(old[f2_index],'v22_figure3_caption',caption)]
    added=b''.join(E.tostring(n,encoding='utf-8') for n in insert_nodes)
    edits.append((spans[start2]['start'],spans[start2]['start'],added))
    updated=original
    for start,end,blob in sorted(edits,reverse=True): updated=updated[:start]+blob+updated[end:]
    E.fromstring(updated);files['word/document.xml']=updated
    relbytes=files['word/_rels/document.xml.rels']
    relationships=[]
    for path,rid in [(tsne,'rIdV22TSNE'),(violins,'rIdV22Violins')]:
        part='word/media/'+path.name;files[part]=path.read_bytes()
        relationships.append(E.tostring(E.Element('{'+REL+'}Relationship',{
            'Id':rid,'Type':R+'/image','Target':'media/'+path.name}),encoding='utf-8'))
    assert b'</Relationships>' in relbytes
    files['word/_rels/document.xml.rels']=relbytes.replace(b'</Relationships>',b''.join(relationships)+b'</Relationships>')
    with ZipFile(OUTPUT,'w') as z:
        for info in infos:z.writestr(info,files.pop(info.filename))
        for key,value in files.items():z.writestr(key,value)
    manifest={'source':str(SOURCE),'source_sha256':sha(SOURCE.read_bytes()),
        'output':str(OUTPUT),'output_sha256':sha(OUTPUT.read_bytes()),
        'replaced_body_nodes':records,'new_figure':'Figure3, Section2.1',
        'original_figure1_preserved':True,'original_figures3_to6_renumbered_to4_to7':True,
        'section2_2_and_later_scientific_content_unchanged':True,
        'source_v5_unmodified':True,'yellow_additions_retained':True,
        'new_or_revised_caption_and_explanation_highlighted_yellow':True,
        'no_new_training_or_QHERO_results_added':True}
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    with ZipFile(OUTPUT) as z:
        final={key:z.read(key) for key in z.namelist()}
    blocks=[]
    rels={n.get('Id'):n.get('Target') for n in E.fromstring(final['word/_rels/document.xml.rels'])}
    for node in E.fromstring(updated).find('w:body',NS):
        value=b.text(node)
        if value=='1. Introduction':blocks.append('<h1>'+value+'</h1>')
        elif value=='2.1 Training guidance NN models':blocks.append('<h2>'+value+'</h2>')
        elif value=='2.2 Training on QACs':break
        elif blocks and value:
            highlight=node.find('.//w:highlight',NS) is not None
            blocks.append('<p'+(' class="added"' if highlight else '')+'>'+html.escape(value)+'</p>')
        elif blocks:
            for blip in node.findall('.//a:blip',NS):
                path='word/'+rels[blip.get('{'+R+'}embed')]
                mime='image/png' if path.endswith('.png') else 'image/jpeg'
                blocks.append('<img src="data:'+mime+';base64,'+base64.b64encode(final[path]).decode()+'">')
    page='<!doctype html><meta charset="utf-8"><title>v22 Introduction and 2.1</title><style>body{font-family:Aptos,Arial,sans-serif;max-width:1000px;margin:40px auto;line-height:1.6;color:#42434b}img{width:100%;height:auto}p.added{background:#fff2a8;padding:8px}h1,h2{font-weight:500}</style>'+''.join(blocks)
    (ROOT/'INTRO_2_1_REVIEW.html').write_text(page)
    print('Saved v22 DOCX with enhanced Figure2 and new Figure3; source Figure1 retained.')

if __name__=='__main__':main()
