"""Author-based main text, vertical figures, and detailed tables in the retained SI."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import base64, copy, hashlib, html, importlib.util, json, re
import ast
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
SOURCE=COMA/'2026_10_14_Paper_2_edited-v23_grouped_adaptation_only.docx'
OLD_SI=ROOT.parent/'revision_v20/Supplementary_Information_v20.docx'
MAIN=COMA/'2026_10_14_Paper_2_edited-v24_section2_2_vertical_figures.docx'
SI=ROOT/'Supplementary_Information_v24.docx'
spec=importlib.util.spec_from_file_location('v22',ROOT.parent/'revision_v22/build_revision.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
b=v.b;NS=v.NS;W=b.W

def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):
    with ZipFile(path) as z:return z.infolist(),{n:z.read(n) for n in z.namelist()}
def write(path,infos,files):
    with ZipFile(path,'w') as z:
        for info in infos:z.writestr(info,files[info.filename])
        for key in files:
            if key not in {i.filename for i in infos}:z.writestr(key,files[key])
def rows(table):
    return [[b.text(c) for c in r.findall('w:tc',NS)] for r in table.findall('w:tr',NS)]
def paragraph(template,label,value,highlight=True):
    p=b.paragraph(template,label,value)
    if not highlight:
        for r in p.findall('w:r',NS):
            props=r.find('w:rPr',NS)
            for n in props.findall('w:highlight',NS):props.remove(n)
    return p
def add_image(files,template,path,rid,uid):
    partname='v24_'+path.name
    assert 'word/media/'+partname not in files
    files['word/media/'+partname]=path.read_bytes()
    rel=E.tostring(E.Element('{'+v.REL+'}Relationship',{
        'Id':rid,'Type':v.R+'/image','Target':'media/'+partname}),encoding='utf-8')
    name='word/_rels/document.xml.rels'
    closing=files[name].rfind(b'</')
    assert closing>=0
    files[name]=files[name][:closing]+rel+files[name][closing:]
    return v.figure(template,path,rid,uid)
def simple_table(template,headers,values):
    table=E.Element('{'+W+'}tbl')
    props=E.SubElement(table,'{'+W+'}tblPr')
    E.SubElement(props,'{'+W+'}tblStyle',{'{'+W+'}val':'ad'})
    E.SubElement(props,'{'+W+'}tblW',{'{'+W+'}w':'0','{'+W+'}type':'auto'})
    for i,row in enumerate([headers]+values):
        tr=E.SubElement(table,'{'+W+'}tr')
        for j,value in enumerate(row):
            cell=E.SubElement(tr,'{'+W+'}tc')
            cp=E.SubElement(cell,'{'+W+'}tcPr')
            if i==0:E.SubElement(cp,'{'+W+'}shd',{'{'+W+'}fill':'EEF2F3'})
            p=paragraph(template,'v24_table_%s_%s_%s'%(len(values),i,j),str(value),False)
            # IDs are unnecessary on generated table paragraphs and may collide across tables.
            p.attrib.clear()
            for rp in p.findall('w:r/w:rPr',NS):
                for sz in rp.findall('w:sz',NS):rp.remove(sz)
                E.SubElement(rp,'{'+W+'}sz',{'{'+W+'}val':'18'})
            cell.append(p)
    return table

def si_spacing(value):
    for old,new in {
        'Section2.2':'Section 2.2','Tables1–2':'Tables 1–2',
        'Table1':'Table 1','Table2':'Table 2','Figure3':'Figure 3',
        'Figure4':'Figure 4','Figure5':'Figure 5',
        'J. Chem. Inf. Model.2026,66,':'J. Chem. Inf. Model. 2026, 66, ',
        'DOI:10':'DOI: 10','code:https':'code: https','commit52':'commit 52',
        'original421':'original 421','the405':'the 405','the81':'the 81',
        'conditional95%bootstrap':'conditional 95% bootstrap',
        'interval[':'interval [','Conditional95%CI':'Conditional 95% CI'
    }.items():value=value.replace(old,new)
    return value

def main_paragraphs():
    return [
    ('opening','Having obtained the embeddings, we next evaluated them on the MIC and MBC '
        'regression tasks for the 105 quaternary ammonium compounds introduced in our previous '
        'work. Each molecule is represented together with the bacterial species and activity '
        'type, allowing a shared CatBoost model to predict four quantitative endpoints. '
        'Expert Good/Bad labels train the representation; measured MIC/MBC values still '
        'train the downstream quantitative decoder. Complete reference results are provided '
        'in Tables S45–S46.'),
    ('reference_results','The original reference comparison shows the value of this task-aware '
        'formulation. With human-guided molecular features and text-encoded task descriptions, '
        'the recovered endpoint R² values are 0.75, 0.68, 0.59 and 0.77 for S. aureus MIC, '
        'S. aureus MBC, E. coli MIC and E. coli MBC, respectively. One-hot and categorical '
        'task coding provide simpler alternatives. Text descriptions are encoded with '
        'OpenAI text-embedding-3-small, giving one fixed 1,536-dimensional vector for '
        'each of the four species–endpoint combinations; exact inputs and cache provenance '
        'are provided in SI Section S34. The original comparison also reports '
        'close point estimates for the expert-guided and full-corpus quantitative encoders '
        '(Table S46), suggesting that coarse expert supervision can produce useful molecular '
        'features. Similar scores do not by themselves establish equivalence of the two '
        'sources or demonstrate a unique semantic benefit of text task descriptions.'),
    ('row_cv','To assess variability separately from these historical holdout results, we '
        'reconstructed five-fold row-wise cross-validation using the saved human-guided '
        'features and recovered decoder budget. Mean endpoint R² ranges from 0.449 to '
        '0.717 with text task coding; complete mean ± fold SD values and raw-feature '
        'controls are in Table S40. This protocol predicts withheld task rows and may '
        'retain other measurements of the same molecule in training. Cation and scaffold '
        'holdouts address the different question of prediction for new molecular groups.'),
    ('matched_compact','Figure 4 makes the supervision comparison explicit under a matched '
        'design. External compact encoders use the same 681 source molecules, identical '
        'source partitions and five paired seeds, with target cations excluded. Human labels '
        'train a contrastive encoder and continuous MIC values train a regression encoder; '
        'the backbone remains frozen. Independently fitted quantitative decoders use the '
        'same CatBoost budget and native categorical task codes. This no-SMOTE follow-up '
        'retains the v5 encoder architecture while controlling source exposure, rather '
        'than replaying the historical full-corpus quantitative checkpoint.'),
    ('matched_interpretation','The resulting vertical violins show the observed endpoint-error '
        'distributions on the same 105 salts. Human and quantitative guidance give similar '
        'pooled errors, with their ordering depending on the holdout scheme. Shuffled-human '
        'guidance remains competitive in this compact-encoder experiment, limiting claims '
        'that human-label meaning uniquely explains the result. Detailed seed statistics '
        'and controls are in Table S41. These comparisons assess representation-learning '
        'procedures; an expert label is not assumed to be informationally equivalent to '
        'an individual concentration measurement.'),
    ('modern_decoders','Modern molecular and tabular models provide additional checks on the '
        'choice of decoder. Chemprop, TabPFN, TabFM and AutoGluon were evaluated on the '
        'same target registers. TabFM improves the separate-endpoint raw CatBoost pipeline '
        'in the grouped point comparisons, illustrating that the best procedure depends '
        'on both representation and decoder. Different PCA treatments and optimisation '
        'budgets make these practical pipeline comparisons. Full endpoint results and '
        'fold variability are provided in Tables S38 and S42.'),
    ('qhero','We additionally tested transfer of source-trained representations to the '
        'independent Q-HERO activity-classification collection (Figure 5). After deduplication '
        'and exclusion of conflicting records, 405 molecules were classified by S. aureus '
        'MIC ≤8 µM using fixed five-fold scaffold holdouts. Source cations were excluded '
        'from this target cohort. Human-guided partial-backbone features with a newly '
        'trained CatBoost classifier give AUROC 0.675 ± 0.033, versus 0.595 for raw '
        'MolFormer and 0.565 for the authors’ RF architecture refitted on the same cohort '
        'and folds. Quantitative guidance gives 0.716 ± 0.010. These human and quantitative '
        'models use partial-backbone adaptation, distinct from the compact encoders in '
        'Figure 4; the external task therefore extends the supervision comparison across '
        'another representation-learning procedure.'),
    ('qhero_control','On Q-HERO, human guidance also exceeds shuffled-human guidance '
        '(AUROC 0.567 ± 0.070). The paired difference is +0.108, with conditional 95% '
        'bootstrap interval [0.031, 0.237] over source/decoder seeds and scaffold clusters. '
        'The human−RF contrast is positive under scaffold evaluation (+0.110 '
        '[0.026, 0.201]), while its random-test interval includes zero [−0.066, 0.297]. '
        'This supports a contribution from label assignment in the stated procedure, '
        'without establishing a biological mechanism or superiority over quantitative '
        'guidance. The ± values denote sample SD of five complete runs. Since 360 of '
        '405 molecules are active, precision–recall results are interpreted against '
        'the high positive-class prevalence. Full metrics, controls and provenance are '
        'in Tables S47–S48. The matched RF comparison concerns our cleaned cohort and '
        'scaffold protocol, rather than the authors’ original 421-row random test.'),
    ]

def main():
    ROOT.mkdir(exist_ok=True)
    infos,files=read(SOURCE);raw=files['word/document.xml']
    body=list(E.fromstring(raw).find('w:body',NS));spans=b.body_ranges(raw)
    start=next(i for i,n in enumerate(body) if b.text(n)=='2.2 Training on QACs')
    end=next(i for i,n in enumerate(body) if b.text(n)=='2.3 Out of domain inference')
    template=next(n for n in body[start:end] if b.text(n).startswith('Having obtained'))
    tables=[n for n in body[start:end] if n.tag=='{'+W+'}tbl'];assert len(tables)==2
    parity_cap=next(i for i in range(start,end) if b.text(body[i]).startswith('Figure 4.'))
    parity=body[parity_cap-1]
    cap3=next(i for i,n in enumerate(body) if b.text(n).startswith('Figure 3.'))
    graphic_template=body[cap3-1]
    p=lambda label,text:paragraph(template,'v24_'+label,text)
    cap3text=(ROOT/'figure3_caption_EN.txt').read_text().strip()
    f3=add_image(files,graphic_template,ROOT/'figures/figure3_backbone_route_error_violins.png','rIdV24FT',244003)
    edits=[(spans[cap3-1]['start'],spans[cap3-1]['end'],E.tostring(f3,encoding='utf-8')),
        (spans[cap3]['start'],spans[cap3]['end'],E.tostring(p('figure3_caption',cap3text),encoding='utf-8'))]
    additions=[]
    for label,text in main_paragraphs():
        additions.append(p(label,text))
        if label=='matched_interpretation':
            additions.append(add_image(files,graphic_template,ROOT/'figures/figure4_human_quantitative_compact.png','rIdV24Compact',244004))
            additions.append(p('figure4_caption',(ROOT/'figure4_caption_EN.txt').read_text().strip()))
        if label=='qhero_control':
            additions.append(add_image(files,graphic_template,ROOT/'figures/figure5_qhero_real_roc.png','rIdV24QHERO',244005))
            additions.append(p('figure5_caption',(ROOT/'figure5_caption_EN.txt').read_text().strip()))
    replacement=b''.join(E.tostring(n,encoding='utf-8') for n in additions)
    edits.append((spans[start]['end'],spans[end]['start'],replacement))
    # Figure4 parity is archived in SI; new4/5 precede existing molecular classes and OOD.
    for i in range(end,len(body)):
        texts=body[i].findall('.//w:t',NS)
        full=b.text(body[i]);matches=list(re.finditer(r'\bFigure\s+([5-7])\b',full))
        if not matches:continue
        node=copy.deepcopy(body[i]);texts=node.findall('.//w:t',NS)
        offsets=[];at=0
        for t in texts:offsets.append((at,at+len(t.text or ''),t));at+=len(t.text or '')
        for match in reversed(matches):
            for a,z,t in offsets:
                if a<=match.start(1)<z:
                    k=match.start(1)-a;t.text=t.text[:k]+str(int(match[1])+1)+t.text[k+1:];break
        edits.append((spans[i]['start'],spans[i]['end'],E.tostring(node,encoding='utf-8')))
    updated=raw
    for a,z,blob in sorted(edits,reverse=True):updated=updated[:a]+blob+updated[z:]
    E.fromstring(updated);files['word/document.xml']=updated;write(MAIN,infos,files)
    build_SI(tables,parity,files,template,graphic_template)
    manifest=dict(source=str(SOURCE),source_sha256=sha(SOURCE.read_bytes()),main=str(MAIN),main_sha256=sha(MAIN.read_bytes()),
        SI_source=str(OLD_SI),SI_source_sha256=sha(OLD_SI.read_bytes()),SI=str(SI),SI_sha256=sha(SI.read_bytes()),
        tables_moved={'Table1':'TableS45','Table2':'TableS46'},original_parity_moved='FigureS32',
        main_figures={'Figure3':'vertical backbone-route errors','Figure4':'matched compact supervision schematic + real vertical errors',
            'Figure5':'QHERO405 scaffold ROC'},original_figures5_to7_renumbered_to6_to8=True,
        OOD_absent_from_section2_1_and_main_new_violins=True,section2_3_scientific_text_unchanged=True,
        source_v5_and_prior_versions_unmodified=True,new_main_text_highlighted_yellow=True)
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,indent=2))
    (ROOT/'SECTION_2_2_EN.md').write_text('\n\n'.join(text for _,text in main_paragraphs())+'\n')
    export_html(files,ROOT/'MANUSCRIPT_REVIEW.html')
    print('Saved v24 main and retained/expanded SI; two original tables moved intact.')

def build_SI(tables,parity,main_files,main_template,graphic_template):
    infos,files=read(OLD_SI);raw=files['word/document.xml']
    body=list(E.fromstring(raw).find('w:body',NS));spans=b.body_ranges(raw)
    sec=next(i for i,n in enumerate(body) if n.tag=='{'+W+'}sectPr')
    template=next(n for n in body if b.text(n).startswith('The expert archive contains'))
    p=lambda label,text:paragraph(template,'si_v24_'+label,si_spacing(text),False)
    nodes=[p('scope','S34. Main-section tables and source-controlled supervision figures, revision v24'),
        p('scope_note','This section accompanies the v5-based main manuscript v24. All previous '
            'SI material, including the four original author-supplied figures, is retained. '
            'Earlier main-table references refer to their archived revision. Current main '
            'Section2.2 uses Tables S45–S48 below and the existing Tables S38–S42. Original '
            'Tables1–2 are moved here without changing their numerical cells; the human/text '
            'E. coli MIC cell printed as 0.60 has recovered value 0.5918 (0.59 at two decimals). '
            'The historical full-corpus quantitative encoder checkpoint has not been recovered; '
            'its table entries remain author-reported point estimates, separately from the '
            'completed matched compact controls.'),
        p('text_model','Text task embeddings: OpenAI text-embedding-3-small. '
            'The recovered April and May 2026 notebooks specify this model and four fixed '
            'CLASS_DESCRIPTIONS. The new computations use a cached 4×1536 float32 array '
            'retrieved through OpenRouter on the local Mac, with requested model '
            'openai/text-embedding-3-small and returned model text-embedding-3-small. '
            'The descriptions match the recovered May notebook exactly. The original '
            'historical vector cache is unavailable, so this regenerated cache is not '
            'claimed to be byte-identical to the historical one. Descriptions contain '
            'species and assay definitions; molecular structures and measured target '
            'concentrations were not sent to the embedding service. Fixed task vectors '
            'are reused across folds; main Figure 4 uses categorical codes instead.'),
        p('table45','Table S45. Original v5 Table1: quantitative MIC/MBC prediction comparison. '
            'Historical point values are preserved; the new row-wise CV and its own fold '
            'SD are in Table S40. They are not uncertainty attached to this holdout table.'),
        copy.deepcopy(tables[0]),
        p('table46','Table S46. Original v5 Table2: expert-guided versus full-corpus quantitative '
            'representations. Numerical entries and layout are preserved. These point '
            'comparisons do not establish equivalence. The available QAC-only encoder '
            'ablation and new source-matched encoders are different models.'),copy.deepcopy(tables[1])]
    cache=ROOT.parent/'v5_hypotheses_20261013/data/task_text_embeddings.npy'
    metadata_path=cache.with_suffix('.json')
    metadata=json.loads(metadata_path.read_text())
    vectors=np.load(cache,allow_pickle=False)
    assert vectors.shape==(4,1536) and vectors.dtype==np.float32
    assert metadata['requested_model']=='openai/text-embedding-3-small'
    assert metadata['returned_model']=='text-embedding-3-small'
    assert sha(cache.read_bytes())==metadata['sha256']
    notebook=ROOT.parent/'notebook_recovery_20261012/notebooks/2026-05-24_descriptors_and_embeddings_comparison_with_labels_to_git.ipynb'
    descriptions=None
    for cell in json.loads(notebook.read_text()).get('cells',[]):
        code=''.join(cell.get('source',[]))
        if 'text-embedding-3-small' not in code:continue
        try:tree=ast.parse(code)
        except SyntaxError:continue
        for n in ast.walk(tree):
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CLASS_DESCRIPTIONS' for t in n.targets):
                descriptions=ast.literal_eval(n.value)
    assert list(descriptions.values())==[d['text'] for d in metadata['tasks']]
    position=next(i for i,n in enumerate(nodes) if b.text(n).startswith('Text task embeddings:'))+1
    descnodes=[p('text_input_'+d['id'],d['id']+': '+d['text']) for d in metadata['tasks']]
    nodes[position:position]=descnodes
    record=dict(model='text-embedding-3-small',provider='OpenAI',requested_via='OpenRouter',
        shape=list(vectors.shape),dtype=str(vectors.dtype),tasks=metadata['tasks'],
        cache=str(cache),cache_sha256=sha(cache.read_bytes()),metadata=str(metadata_path),
        metadata_sha256=sha(metadata_path.read_bytes()),historical_notebook=str(notebook),
        historical_notebook_sha256=sha(notebook.read_bytes()),
        descriptions_exactly_match_recovered_May_notebook=True,
        original_historical_vector_cache_unavailable=True,execution='local Mac')
    (ROOT/'task_text_embedding_provenance.json').write_text(json.dumps(record,indent=2))
    q=pd.read_csv(ROOT.parent/'qhero_author_comparison_20261014/results/summary.csv')
    labels={'RF_35_descriptors':'Author-style RF35','CB_35_descriptors':'CatBoost35',
        'CB_raw_MolFormer':'Raw MolFormer → CB','CB_human':'Human partial → CB',
        'CB_shuffled_human':'Shuffled human partial → CB','CB_quantitative':'Quantitative partial → CB'}
    data=[]
    for protocol in ['random_heldout20','scaffold_CV_pooled']:
        for model,label in labels.items():
            selected=q[(q.model==model)&(q.protocol==protocol)]
            if selected.empty:continue
            a=selected.iloc[0]
            fmt=lambda key:'%.4f ± %.4f'%(a[key],a[key+'_SD']) if pd.notna(a[key+'_SD']) else '%.4f'%a[key]
            data.append([label,protocol,str(int(a.repeats)),fmt('AUROC'),fmt('AUPRC')])
    assert len(data)==12, q.protocol.unique()
    nodes.extend([p('table47','Table S47. Q-HERO405 classification on a common cleaned cohort. '
        'Mean ± sample SD of five paired source/decoder runs; fixed RF, raw-feature and '
        'descriptor baselines have one fit and no invented SD. Random heldout81 and pooled '
        'five-fold scaffold OOF are different evaluations. Positive class: S. aureus MIC '
        '≤8 µM, 360/405 active. Source cations are excluded. These partial-backbone '
        'representations are distinct from the compact Figure4 experiment.'),
        simple_table(template,['Model','Protocol','Runs','AUROC','AUPRC'],data)])
    contrasts=pd.read_csv(ROOT.parent/'qhero_author_comparison_20261014/results/paired_scaffold_contrasts.csv')
    cdata=[]
    for _,a in contrasts.iterrows():
        cdata.append([labels[a.model]+' − '+labels[a.reference],a.metric,
            '%+.4f'%a.difference,'[%+.4f, %+.4f]'%(a.ci_low,a.ci_high)])
    nodes.extend([p('table48','Table S48. Exploratory paired Q-HERO scaffold contrasts: '
        '2,000 resamples of paired source/decoder seeds and 29 scaffold clusters, conditional '
        'on the fixed OOF fits. Each resample averages seed-specific metrics, rather than '
        'ensemble predictions. Training is not refitted, and overlapping OOF training sets '
        'are not fully resampled; intervals do not establish biological causality or '
        'non-inferiority to quantitative guidance.'),
        simple_table(template,['Contrast','Metric','Difference','Conditional 95% CI'],cdata),
        p('qhero_provenance','Q-HERO source: Ghaemi et al. Topology-Aware Generation and '
            'Activity-Based Filtering: A Computational-Experimental Framework for Data-Scarce '
            'Quaternary Ammonium Compound Discovery. J. Chem. Inf. Model.2026,66,3117–3128. '
            'DOI:10.1021/acs.jcim.6c00390. Public code:https://github.com/pb0316/Q-HERO, '
            'commit52ab433a4abc626e164cf72d1a39f02eda260b52. The authors’ original421-row '
            'random split is not the405-molecule scaffold test used for the matched comparison. '
            'Code-replay discrepancies are documented without attributing an unverified cause.'),
        p('random_test_limit','On the81-molecule random test, human minus RF35 AUROC is '
            '+0.1052 with conditional95%bootstrap interval[−0.0664,+0.2969]. The small '
            'test contains only nine inactive molecules; this interval does not establish '
            'a reliable random-test advantage. MainFigure5 shows both protocols while '
            'its principal generalisation claim concerns the common scaffold evaluation.'),
        p('original_parity','Original v5 parity figure, retained for reference')])
    # Copy the original parity image, with a unique part and drawing ID.
    rels={n.get('Id'):n.get('Target') for n in E.fromstring(main_files['word/_rels/document.xml.rels'])}
    blip=parity.find('.//a:blip',NS);imagebytes=main_files['word/'+rels[blip.get('{'+v.R+'}embed')]]
    archived=ROOT/'figures/figureS32_original_v5_parity.jpg';archived.write_bytes(imagebytes)
    nodes.extend([add_image(files,parity,archived,'rIdV24OriginalParity',244032),
        p('parity_caption','Figure S32. Original v5 experimental-versus-predicted '
            'MIC/MBC plots, retained with the original raster bytes. These are historical '
            'reference plots and are distinct from the newly executed source-matched '
            'grouped validation in main Figure4.'),
        p('figure_protocol','For main Figures3–4, violin densities use actual compound–endpoint '
            'absolute-error summaries, averaged within runs, rather than densities over '
            'three or five RMSE values. Main Figure3 uses three runs per backbone route; '
            'Figure4 uses five source runs for each compact guided arm and one raw-feature '
            'reference. All endpoint errors and tails are retained. Molecule endpoints '
            'and repeated runs are dependent. Complete predictions, derived values, '
            'fonts, model budgets and artifact hashes are in reproducibility/revision_v24.')])
    insertion=b''.join(E.tostring(n,encoding='utf-8') for n in nodes)
    files['word/document.xml']=raw[:spans[sec]['start']]+insertion+raw[spans[sec]['start']:]
    E.fromstring(files['word/document.xml']);write(SI,infos,files)
    export_html(files,ROOT/'Supplementary_Information_v24.html')

def export_html(files,path):
    body=E.fromstring(files['word/document.xml']).find('w:body',NS)
    rels={n.get('Id'):n.get('Target') for n in E.fromstring(files['word/_rels/document.xml.rels'])}
    out=[]
    for n in body:
        if n.tag=='{'+W+'}tbl':
            out.append('<table>'+''.join('<tr>'+''.join('<td>'+html.escape(c)+'</td>' for c in r)+'</tr>' for r in rows(n))+'</table>');continue
        t=b.text(n)
        if t:
            mark=n.find('.//w:highlight',NS) is not None
            out.append('<p'+(' class="added"' if mark else '')+'>'+html.escape(t)+'</p>')
        for image in n.findall('.//a:blip',NS):
            part='word/'+rels[image.get('{'+v.R+'}embed')]
            mime='image/png' if part.endswith('.png') else 'image/jpeg'
            out.append('<img src="data:'+mime+';base64,'+base64.b64encode(files[part]).decode()+'">')
    path.write_text('<!doctype html><meta charset="utf-8"><style>body{font-family:Aptos,Arial;max-width:1100px;margin:40px auto;line-height:1.55;color:#42434b}img{width:100%;height:auto}p.added{background:#fff2a8;padding:8px}table{border-collapse:collapse;font-size:13px;width:100%}td{border:1px solid #ddd;padding:7px}</style>'+''.join(out))

if __name__=='__main__':main()
