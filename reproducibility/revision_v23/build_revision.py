"""Remove external OOD results from Section2.1; stage them for Section2.3."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import hashlib, html, importlib.util, json, base64, re

ROOT=Path(__file__).resolve().parent; COMA=ROOT.parents[1]
SOURCE=COMA/'2026_10_14_Paper_2_edited-v22_pastel_adaptation_figures.docx'
OUTPUT=COMA/'2026_10_14_Paper_2_edited-v23_grouped_adaptation_only.docx'
spec=importlib.util.spec_from_file_location('v22',ROOT.parent/'revision_v22/build_revision.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
b=v.b;NS=v.NS

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    with ZipFile(SOURCE) as z:
        infos=z.infolist();files={i.filename:z.read(i.filename) for i in infos}
    original=files['word/document.xml'];body=list(E.fromstring(original).find('w:body',NS))
    spans=b.body_ranges(original)
    start=next(i for i,n in enumerate(body) if b.text(n)=='2.1 Training guidance NN models')
    end=next(i for i,n in enumerate(body) if b.text(n)=='2.2 Training on QACs')
    edits=[];records=[];staged=[]
    def replace(prefix,value,label):
        index=next(i for i in range(start,end) if b.text(body[i]).startswith(prefix))
        staged.append(dict(original_body_index=index,text=b.text(body[index])))
        node=b.paragraph(body[index],label,value)
        edits.append((spans[index]['start'],spans[index]['end'],E.tostring(node,encoding='utf-8')))
        records.append(dict(body_index=index,label=label,text=value))
    replace('The new adaptation comparison',
        'The adaptation comparison uses the original 105-QAC target cohort, with MIC and MBC '
        'against S. aureus and E. coli. Fixed five-fold cation and scaffold holdouts assess '
        'prediction for held-out molecular groups. The pretrained frozen-head, LoRA and '
        'full-fine-tuning branches each use three target-training seeds. The two human-guided '
        'prediction routes additionally share source checkpoints 0–2, holding their starting '
        'representation fixed.', 'v23_grouped_setup')
    replace('In a separate completed backbone experiment',
        'In a separate completed backbone experiment, a frozen pretrained backbone with a '
        'linear prediction head gave cation/scaffold RMSE 2.013 ± 0.006/1.986 ± 0.003. '
        'Direct LoRA gave 2.040 ± 0.049/2.089 ± 0.012, while direct full fine-tuning gave '
        '1.863 ± 0.045/1.970 ± 0.026. These comparisons assess the stated prediction '
        'pipelines under the tested optimisation budgets; they do not establish a universal '
        'preference for full or parameter-efficient fine-tuning.', 'v23_grouped_backbone_results')
    replace('Using the same three human-guided',
        'Using the same three human-guided partial-backbone source checkpoints, direct target '
        'prediction gave cation/scaffold RMSE 1.797 ± 0.057/1.834 ± 0.058, compared with '
        '1.743 ± 0.031/1.819 ± 0.044 when the source representation was frozen and decoded '
        'with CatBoost. These human-guided backbones are separate follow-up models, rather '
        'than the external compact encoder described above. All values use log₂(mg/L); '
        '± denotes sample SD across three complete runs, rather than CV-fold SD or a '
        '95% confidence interval.', 'v23_grouped_human_results')
    replace('The route comparison changes adaptation',
        'The route comparison changes adaptation and decoding together and therefore does '
        'not isolate a causal effect of human-label meaning. A separate controlled '
        'follow-up retains the compact v5 architecture and uses the same 681 source '
        'molecules (377 training and 304 validation), with target cations excluded and five '
        'paired source seeds. This follow-up fixes source exposure and training updates '
        'and omits SMOTE; it is distinct from the archived SMOTE training procedure.',
        'v23_grouped_comparison_scope')
    replace('Figure 3 compares',
        'Figure 3 compares the distributions of absolute MIC/MBC prediction errors for '
        'frozen-head, LoRA, full-backbone and human-guided adaptation in cation and scaffold '
        'holdouts. The two human-guided routes use partial backbone adaptation and share '
        'source checkpoints; they are distinct from the external compact feature encoder '
        'described above.', 'v23_figure3_link')
    caption=(ROOT/'figure3_caption_EN.txt').read_text().strip()
    assert caption.startswith('Figure 3.') and not re.search(r'OOD|out.of.distribution|67',caption,re.I)
    replace('Figure 3.',caption,'v23_figure3_caption')
    capindex=next(i for i in range(start,end) if b.text(body[i]).startswith('Figure 3.'))
    graphic=ROOT/'figures/figure3_backbone_route_error_violins.png'
    image=v.figure(body[capindex-1],graphic,'rIdV23GroupedViolin',224002)
    edits.append((spans[capindex-1]['start'],spans[capindex-1]['end'],E.tostring(image,encoding='utf-8')))
    updated=original
    for at,until,blob in sorted(edits,reverse=True):updated=updated[:at]+blob+updated[until:]
    newbody=list(E.fromstring(updated).find('w:body',NS))
    section='\n'.join(b.text(n) for n in newbody[start:end])
    assert not re.search(r'\bOOD\b|out.of.distribution|17 newly|67 exact|IT505',section,re.I)
    # Keep every subsequent section literally intact, not merely text-identical.
    assert updated[updated.index(b'<w:p',b.body_ranges(updated)[end]['start']):] == original[spans[end]['start']:]
    files['word/document.xml']=updated
    rel=E.tostring(E.Element('{'+v.REL+'}Relationship',{
        'Id':'rIdV23GroupedViolin','Type':v.R+'/image','Target':'media/'+graphic.name}),encoding='utf-8')
    files['word/_rels/document.xml.rels']=files['word/_rels/document.xml.rels'].replace(b'</Relationships>',rel+b'</Relationships>')
    files['word/media/'+graphic.name]=graphic.read_bytes()
    with ZipFile(OUTPUT,'w') as z:
        for info in infos:z.writestr(info,files.pop(info.filename))
        for key,value in files.items():z.writestr(key,value)
    manifest=dict(source=str(SOURCE),source_sha256=sha(SOURCE.read_bytes()),output=str(OUTPUT),
        output_sha256=sha(OUTPUT.read_bytes()),revised_paragraphs=records,
        removed_OOD_from_section2_1=True,figure3_panels=['cation','scaffold'],
        all_sections_from_2_2_unchanged_verbatim=True,figure2_and_figure1_unchanged=True,
        OOD_staged_for_future_section2_3_not_yet_inserted=True)
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    # Save complete previous text for a later reviewed OOD rewrite, without inserting it now.
    note=('# OOD для будущей правки §2.3\n\n'
        '§2.3 в v23 не менялся. Исходные полные абзацы ниже содержат и grouped-результаты, '
        'которые остаются в §2.1. В §2.3 переносим только соответствующие OOD-части.\n\n')
    note+='\n\n'.join('## Архивный абзац '+str(r['original_body_index'])+'\n\n'+r['text'] for r in staged)
    note+='\n\n## Смысл нового OOD-блока\n\n'
    note+='17 соединений, 67 точных endpoints и отдельно сохранённая граница IT505/Ec_MBC >500 mg/L. '
    note+='RMSE ± sample SD трёх запусков: frozen head 2.560 ± 0.206; LoRA 2.756 ± 0.172; '
    note+='full FT 3.032 ± 0.408; human partial direct 2.412 ± 0.088; frozen human partial → '
    note+='CatBoost 2.106 ± 0.071. Компактный matched v5 human/shuffled контроль — отдельный '
    note+='пятиseed эксперимент: 2.268 ± 0.077 / 2.172 ± 0.112, без human-content преимущества. '
    note+='OOD-панель prepared в figures; не объявляем её compact v5 encoder и не делаем '
    note+='каузальный вывод по распределению ошибок.\n'
    (ROOT/'OOD_TRANSFER_FOR_2_3.md').write_text(note)
    with ZipFile(OUTPUT) as z:final={n:z.read(n) for n in z.namelist()}
    rels={n.get('Id'):n.get('Target') for n in E.fromstring(final['word/_rels/document.xml.rels'])}
    blocks=[]
    for node in newbody:
        text=b.text(node)
        if text in ['1. Introduction','2.1 Training guidance NN models']:blocks.append('<h2>'+text+'</h2>')
        elif text=='2.2 Training on QACs':break
        elif blocks and text:
            added=node.find('.//w:highlight',NS) is not None
            blocks.append('<p'+(' class="added"' if added else '')+'>'+html.escape(text)+'</p>')
        elif blocks:
            for blip in node.findall('.//a:blip',NS):
                part='word/'+rels[blip.get('{'+v.R+'}embed')]
                mime='image/png' if part.endswith('.png') else 'image/jpeg'
                blocks.append('<img src="data:'+mime+';base64,'+base64.b64encode(final[part]).decode()+'">')
    (ROOT/'INTRO_2_1_REVIEW.html').write_text('<!doctype html><meta charset="utf-8"><title>v23</title><style>body{font-family:Aptos,Arial;max-width:1000px;margin:40px auto;line-height:1.6;color:#42434b}img{width:100%}p.added{background:#fff2a8;padding:8px}</style>'+''.join(blocks))
    print('v23 built: Section2.1 and Figure3 contain grouped evaluation only; later sections untouched.')

if __name__=='__main__':main()
