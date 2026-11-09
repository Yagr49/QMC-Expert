"""Restore archived correlations, split the matched figure and correct Figure1 numbers."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import copy, hashlib, importlib.util, json, re

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
SOURCE=COMA/'2026_10_14_Paper_2_edited-v24_section2_2_vertical_figures.docx'
OLD_SI=ROOT.parent/'revision_v24/Supplementary_Information_v24.docx'
MAIN=COMA/'2026_10_14_Paper_2_edited-v25_correlations_and_split_figures.docx'
SI=ROOT/'Supplementary_Information_v25.docx'
spec=importlib.util.spec_from_file_location('v24',ROOT.parent/'revision_v24/build_revision.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
b=v.b;NS=v.NS;W=v.W

def sha(data):return hashlib.sha256(data).hexdigest()
def paragraph(template,label,value):return v.paragraph(template,'v25_'+label,value)
def image(files,template,path,rid,uid):
    name='v25_'+path.name;files['word/media/'+name]=path.read_bytes()
    rel=E.tostring(E.Element('{'+v.v.REL+'}Relationship',{'Id':rid,'Type':v.v.R+'/image','Target':'media/'+name}),encoding='utf-8')
    part='word/_rels/document.xml.rels';at=files[part].rfind(b'</')
    assert at>=0
    files[part]=files[part][:at]+rel+files[part][at:]
    return v.v.figure(template,path,rid,uid)
def rename_refs(node,mapping):
    node=copy.deepcopy(node);texts=node.findall('.//w:t',NS);full=b.text(node)
    matches=list(re.finditer(r'\bFigure\s+(\d+)\b',full));offsets=[];at=0
    for t in texts:offsets.append((at,at+len(t.text or ''),t));at+=len(t.text or '')
    for match in reversed(matches):
        number=int(match[1])
        if number not in mapping:continue
        for a,z,t in offsets:
            if a<=match.start(1)<z:
                k=match.start(1)-a;t.text=t.text[:k]+str(mapping[number])+t.text[k+len(match[1]):];break
    return node

def main():
    infos,files=v.read(SOURCE);raw=files['word/document.xml']
    body=list(E.fromstring(raw).find('w:body',NS));ranges=b.body_ranges(raw);edits=[];records=[]
    def replace(index,node):
        edits.append((ranges[index]['start'],ranges[index]['end'],E.tostring(node,encoding='utf-8')))
        records.append(dict(body_index=index,text=b.text(node)))
    def idx(prefix):return next(i for i,n in enumerate(body) if b.text(n).startswith(prefix))
    cap1=idx('Figure 1.');cap4=idx('Figure 4.');cap5=idx('Figure 5.')
    template=body[idx('Having obtained')];graphic=body[cap4-1]
    replace(cap1-1,image(files,body[cap1-1],ROOT/'figures/figure1_verified_workflow.png','rIdV25Figure1',255001))
    replace(cap1,paragraph(body[cap1],'fig1_caption',(ROOT/'figure1_caption_EN.txt').read_text().strip()))
    original=ROOT.parent/'revision_v24/figures/figureS32_original_v5_parity.jpg'
    restored=image(files,graphic,original,'rIdV25Correlation',255004)
    corr_caption=('Figure 4. Original v5 experimental-versus-predicted correlations for '
        'descriptor-based models and learned molecular embeddings, with no task labels, '
        'categorical/one-hot task labels and OpenAI text-embedded task descriptions. '
        'The original raster is retained without changing its points or printed pooled '
        'R²/RMSE/MAE values. These are archived reference plots, separate from the newly '
        'reconstructed row-CV and source-excluded cation/scaffold tests. Text task '
        'descriptions use text-embedding-3-small, as specified in Section2.2 and SI S34.')
    anchor=idx('To assess variability separately')
    blob=b''.join(E.tostring(n,encoding='utf-8') for n in [
        paragraph(template,'correlation_link','Figure 4 retains the original correlation '
            'plots to illustrate the quantitative behaviour of descriptor and embedding '
            'models under the archived task-coding configurations. The reference '
            'predictions and their printed pooled metrics are preserved.'),
        restored,paragraph(template,'correlation_caption',corr_caption)])
    edits.append((ranges[anchor]['start'],ranges[anchor]['start'],blob))
    # Replace the former integrated Figure4 by two independent numbered figures.
    design=image(files,graphic,ROOT/'figures/figure5_matched_supervision_design.png','rIdV25Design',255005)
    violins=image(files,graphic,ROOT/'figures/figure6_matched_supervision_violins.png','rIdV25Violins',255006)
    blocks=[design,paragraph(body[cap4],'design_caption',(ROOT/'figure5_caption_EN.txt').read_text().strip()),
        violins,paragraph(body[cap4],'violin_caption',(ROOT/'figure6_caption_EN.txt').read_text().strip())]
    edits.append((ranges[cap4-1]['start'],ranges[cap4]['end'],b''.join(E.tostring(n,encoding='utf-8') for n in blocks)))
    mapping={5:7,6:8,7:9,8:10}
    for i,n in enumerate(body):
        if i in [cap1-1,cap1,cap4-1,cap4]:continue
        text=b.text(n)
        if text.startswith('Figure 4 makes the supervision'):
            replace(i,paragraph(n,'matched_design',text.replace('Figure 4','Figure 5',1)));continue
        if text.startswith('The resulting vertical violins'):
            replace(i,paragraph(n,'matched_results',text.replace('The resulting vertical violins','The vertical violins in Figure 6',1)));continue
        if text.startswith('We additionally tested transfer'):
            replace(i,paragraph(n,'qhero_text',text.replace('Figure 5','Figure 7').replace('Figure 4','Figures 5–6')));continue
        changed=rename_refs(n,mapping)
        if i==cap5:
            value=b.text(changed).replace('Figure 4','Figures 5–6')
            changed=paragraph(n,'qhero_caption',value)
        if E.tostring(n)!=E.tostring(changed):replace(i,changed)
    output=raw
    for a,z,blob in sorted(edits,reverse=True):output=output[:a]+blob+output[z:]
    E.fromstring(output);files['word/document.xml']=output;v.write(MAIN,infos,files)
    update_SI()
    manifest=dict(source=str(SOURCE),source_sha256=sha(SOURCE.read_bytes()),main=str(MAIN),main_sha256=sha(MAIN.read_bytes()),
        SI=str(SI),SI_source=str(OLD_SI),SI_sha256=sha(SI.read_bytes()),
        archived_correlation_restored='Figure4, original raster bytes unchanged',
        integrated_figure4_split_into=['Figure5 design','Figure6 error violins'],QHERO_renumbered='Figure7',
        source_numeric_results_unchanged=True,figure1_numbers_corrected='1103 labels, explicit descriptor/stacking/human ranges',
        old_figure1_source_bitmap_retained_in_package=True,new_molecular_depictions='ACS1996 generic bis-QAC',
        tables_remain_in_SI=True,section2_3_and_later_scientific_text_unchanged_except_figure_numbers=True,
        new_and_revised_main_paragraphs_highlighted_yellow=True,revised_body_nodes=records)
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2))
    v.export_html(files,ROOT/'MANUSCRIPT_REVIEW.html')
    (ROOT/'figure4_caption_EN.txt').write_text(corr_caption+'\n')
    print('v25 saved: verified Figure1, restored correlations, split design/errors, updated references.')

def update_SI():
    infos,files=v.read(OLD_SI);raw=files['word/document.xml']
    body=list(E.fromstring(raw).find('w:body',NS));ranges=b.body_ranges(raw)
    start=next(i for i,n in enumerate(body) if b.text(n).startswith('S34. Main-section tables'))
    edits=[]
    for i in range(start,len(body)):
        n=body[i];value=b.text(n);new=value
        if value.startswith('Text task embeddings:'):
            new=value.replace('main Figure 4','main Figures 5–6')
        elif value.startswith('Table S47.'):
            new=value.replace('compact Figure 4','compact Figures 5–6')
        elif value.startswith('On the 81-molecule'):
            new=value.replace('MainFigure5','Main Figure 7').replace('Main Figure 5','Main Figure 7')
        elif value.startswith('Figure S32.'):
            new=value.replace('main Figure4','main Figure 6').replace('main Figure 4','main Figure 6')
        elif value.startswith('For main Figures3–4') or value.startswith('For main Figures 3–4'):
            new=value.replace('Figures3–4','Figures 3 and 6').replace('Figures 3–4','Figures 3 and 6').replace('Figure4','Figure 6').replace('Figure 4','Figure 6')
        if new!=value:
            p=v.paragraph(n,'v25_si_%d'%i,new,False)
            edits.append((ranges[i]['start'],ranges[i]['end'],E.tostring(p,encoding='utf-8')))
    output=raw
    for a,z,blob in sorted(edits,reverse=True):output=output[:a]+blob+output[z:]
    files['word/document.xml']=output;v.write(SI,infos,files)
    v.export_html(files,ROOT/'Supplementary_Information_v25.html')

if __name__=='__main__':main()
