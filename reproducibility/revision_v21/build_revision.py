"""Add yellow paragraphs to immutable v5 without reserialising its original XML."""
from pathlib import Path
from zipfile import ZipFile
from xml.parsers import expat
from xml.etree import ElementTree as E
import copy
import hashlib
import html
import json

ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
SOURCE=COMA/'2026_07_09_Paper_2_edited-v5_NF_3.docx'
OUTPUT=COMA/'2026_10_14_Paper_2_edited-v21_v5_intro_2_1_yellow.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W14='http://schemas.microsoft.com/office/word/2010/wordml'
NS={'w':W}
E.register_namespace('w',W)
E.register_namespace('w14',W14)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def text(node):
    return ''.join(t.text or '' for t in node.findall('.//w:t',NS))


def body_ranges(data):
    parser=expat.ParserCreate()
    stack=[];ranges=[]
    def start(name,attrs):
        if stack and stack[-1]=='w:body':
            ranges.append(dict(name=name,start=parser.CurrentByteIndex))
        stack.append(name)
    def end(name):
        if len(stack)==3 and stack[-2]=='w:body':
            at=parser.CurrentByteIndex
            ranges[-1]['end']=data.find(b'>',at)+1 if data[at:at+2]==b'</' else at
        stack.pop()
    parser.StartElementHandler=start
    parser.EndElementHandler=end
    parser.Parse(data,True)
    return ranges


def additions():
    checked=(ROOT/'reviews'/'claude_insertions_checked.md').read_text()
    intro=checked.split('## Introduction — three optional consecutive paragraphs\n\n')[1].split('\n\n## Section 2.1')[0].strip().split('\n\n')
    section=checked.split('## Section 2.1 — four short paragraphs, append near Figure 2\n\n')[1].split('\n\n## Checks and corrections')[0].strip().split('\n\n')
    assert len(intro)==3 and len(section)==4
    section[0]=('The reference encoder operates outside MolFormer. For a SMILES string s, '
                'the frozen backbone produces h₀ = fθ(s) ∈ R⁷⁶⁸. The archived StandardScaler '
                'normalises these input features before an external MLP produces '
                'z ∈ R²⁵⁶ through layers of width 512, 384 and 256. Expert labels train '
                'the MLP parameters ψ without updating the backbone parameters θ. '
                'A subsequent decoder predicts quantitative MIC/MBC from z and a task code. '
                'This feature adapter is distinct from LoRA updates inside the transformer '
                'and from partial or full backbone fine-tuning.')
    section[0]+=(' The external encoder contains 691,584 trainable parameters. '
                 'Its source-training contrastive projection head is removed when '
                 'the 256-dimensional features are passed to the quantitative decoder.')
    intro[2]+=(' Matched source panels and label-shuffling controls assess whether '
               'the assignment of supervisory labels contributes beyond an added training stage.')
    setup=('The new adaptation comparison uses the original 105-QAC target cohort, with '
           'MIC and MBC against S. aureus and E. coli, and the 17 newly synthesised compounds '
           'from four scaffold families. Fixed five-fold cation and scaffold holdouts assess '
           'new-compound prediction; the OOD decoder is fitted on the 105 compounds. '
           'The pretrained frozen-head, LoRA and full-fine-tuning branches each use three '
           'target-training seeds. The two human-guided prediction routes additionally '
           'share source checkpoints 0–2, allowing their starting representation to be held fixed.')
    section[3]=('The route comparison changes adaptation and decoding together and therefore '
                'does not isolate a causal effect of human-label meaning. To retain the compact '
                'v5 architecture when testing supervisory content, a separate controlled follow-up '
                'trained encoders on the same 681 source molecules (377 training and 304 validation), '
                'with target cations excluded and five paired source seeds. This follow-up fixes '
                'source exposure and training updates and omits SMOTE; it is not an exact replay '
                'of the archived SMOTE procedure. Human and shuffled-human guidance give OOD '
                'RMSE 2.268 ± 0.077 and 2.172 ± 0.112, respectively, where ± is sample SD '
                'over the five source runs. This compact-encoder control does not establish '
                'a human-content advantage. We consequently interpret the route results as '
                'evidence about the stated prediction procedures, without attributing them '
                'to a uniquely human semantic mechanism.')
    final_count=('The recovered computational archive contains 1,103 final molecule-level '
                 'Good/Bad calls. These final outcomes are distinguished from the earlier '
                 'collection count reported above, which requires confirmation from the '
                 'annotation records. The new matched-source panels are constructed from '
                 'the recovered outcomes after standardisation and target-cation exclusion.')
    placeholder=('[COAUTHORS — annotation provenance: confirm collection and final counts; '
                 'annotators and information shown to them; blinding and voting; handling of '
                 'uncertain calls; inter-annotator agreement; collection dates; and access '
                 'to quantitative activity measurements.]')
    return {
        14:[('intro_01',intro[0])],
        18:[('intro_02',intro[1])],
        20:[('intro_03',intro[2])],
        23:[('fig1_caption','This is a conceptual illustration of the modelling workflow. '
             'Its ascending accuracy curves are schematic; the numerical comparisons are '
             'defined by the reported training and evaluation protocols. The trainable '
             'feature encoder and the quantitative decoder are described in Section 2.1.')],
        27:[('annotation_count',final_count),('coauthor_fields',placeholder)],
        29:[('section2_1_01',section[0])],
        32:[('section2_1_setup',setup)]+[('section2_1_%02d'%(j+2),p) for j,p in enumerate(section[1:])],
    }


def paragraph(template,label,value):
    p=E.Element('{'+W+'}p',{'{'+W14+'}paraId':sha(label.encode())[:8].upper(),
                          '{'+W14+'}textId':sha(value.encode())[:8].upper()})
    prop=template.find('w:pPr',NS)
    if prop is not None:p.append(copy.deepcopy(prop))
    run=E.SubElement(p,'{'+W+'}r')
    prop=template.find('w:r/w:rPr',NS)
    prop=copy.deepcopy(prop) if prop is not None else E.Element('{'+W+'}rPr')
    for n in list(prop):
        if n.tag in ('{'+W+'}highlight','{'+W+'}vertAlign','{'+W+'}b','{'+W+'}i'):
            prop.remove(n)
    E.SubElement(prop,'{'+W+'}highlight',{'{'+W+'}val':'yellow'})
    run.append(prop)
    t=E.SubElement(run,'{'+W+'}t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'})
    t.text=value
    return p


def main():
    ROOT.mkdir(exist_ok=True)
    with ZipFile(SOURCE) as z:
        files={i.filename:z.read(i.filename) for i in z.infolist()}
        infos=z.infolist()
    original=files['word/document.xml']
    tree=E.fromstring(original);body=tree.find('w:body',NS);old=list(body)
    ranges=body_ranges(original)
    assert len(ranges)==len(old)
    assert text(old[12])=='1. Introduction' and text(old[25])=='2.1 Training guidance NN models'
    assert text(old[34])=='2.2 Training on QACs'
    added=additions();insertions=[];records=[]
    for index,blocks in added.items():
        blob=b''
        for label,value in blocks:
            node=paragraph(old[13],label,value)
            blob+=E.tostring(node,encoding='utf-8')
            records.append(dict(label=label,after_original_body_index=index,text=value,
                                highlight='yellow',paragraph_sha256=sha(E.tostring(node))))
        insertions.append((ranges[index]['end'],blob))
    new=original
    for at,blob in sorted(insertions,reverse=True):new=new[:at]+blob+new[at:]
    E.fromstring(new)
    files['word/document.xml']=new
    with ZipFile(OUTPUT,'w') as z:
        for info in infos:z.writestr(info,files[info.filename])
    manifest=dict(source=str(SOURCE),source_sha256=sha(SOURCE.read_bytes()),
                  output=str(OUTPUT),output_sha256=sha(OUTPUT.read_bytes()),
                  added_paragraphs=records,all_original_paragraphs_retained=True,
                  original_body_XML_preserved_verbatim=True,
                  original_figure1_preserved=True,section2_2_unchanged=True,
                  no_new_QHERO_or_Tiihonen_metrics_in_manuscript=True,
                  source_based_draft_not_a_replacement_of_v20_SI=True)
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    (ROOT/'ADDITIONS_EN.md').write_text('\n\n'.join(
        '### '+r['label']+'\n\n'+r['text'] for r in records)+'\n')
    new_body=E.fromstring(new).find('w:body',NS)
    highlighted={r['text'] for r in records}
    sections=[]
    for node in new_body:
        value=text(node)
        if value=='1. Introduction':sections.append('<h1>1. Introduction</h1>');active=True;continue
        if value=='2. Results and Discussion':continue
        if value=='2.1 Training guidance NN models':sections.append('<h1>'+html.escape(value)+'</h1>');continue
        if value=='2.2 Training on QACs':break
        if not sections:continue
        if value:
            sections.append('<p'+(' class="added"' if value in highlighted else '')+'>'+html.escape(value)+'</p>')
        elif node.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            import base64
            rels={r.get('Id'):r.get('Target') for r in E.fromstring(files['word/_rels/document.xml.rels'])}
            for image in node.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                rid=image.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                target='word/'+rels[rid];mime='image/png' if target.endswith('.png') else 'image/jpeg'
                sections.append('<img src="data:'+mime+';base64,'+base64.b64encode(files[target]).decode()+'">')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><title>v5 + yellow additions</title><style>body{max-width:900px;margin:40px auto;padding:0 24px;font:19px/1.65 Georgia,serif}h1{font:600 28px/1.4 system-ui}p{text-align:justify}.added{background:#fff59d;padding:12px 16px;border-radius:4px}img{max-width:100%;height:auto}</style>'+''.join(sections)+'</html>'
    (ROOT/'INTRO_2_1_REVIEW.html').write_text(page)
    print(json.dumps(dict(output=str(OUTPUT),new_paragraphs=len(records),
                         source_sha256=manifest['source_sha256']),ensure_ascii=False))


if __name__=='__main__':main()
