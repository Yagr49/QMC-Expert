"""Build the focused JCIM author draft, with explicit coauthor fields.

Existing results and source documents are immutable. Main-body image parts remain
in the new package; moved content is imported into SI with remapped relationships.
"""
from pathlib import Path
import copy, importlib.util, json, re, zipfile, posixpath, html
import xml.etree.ElementTree as E
import pandas as pd

ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
OLD=ROOT.parent/'revision_v10'
spec=importlib.util.spec_from_file_location('v9_doc_helpers',ROOT.parent/'revision_v9/build_revision.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
W,R,PKG,NS=h.W,h.R,h.PKG,h.NS
TITLE='Human versus Quantitative Supervision for Antibacterial Molecular Representation Learning'
MAIN=COMA/'2026_10_11_Paper_2_edited-v11_JCIM_author_draft.docx'
SI=ROOT/'Supplementary_Information_v11.docx'
FIGURES={'design':'figure1_study_design.png','competition':'figure2_partial_finetuning_and_direct.png',
         'contrasts':'figure3_paired_context_contrasts.png','violins':'figure4_MIC_error_violins.png'}


def read_doc(path):
    with zipfile.ZipFile(path) as z: files={n:z.read(n) for n in z.namelist()}
    tree=E.fromstring(files['word/document.xml'])
    return files,tree,tree.find('w:body',NS)


def paragraph(template,text,level=None,marked=False):
    p=copy.deepcopy(template);h.replace(p,text,marked=marked)
    props=p.find('w:pPr',NS)
    if props is None: props=E.Element('{'+W+'}pPr');p.insert(0,props)
    for tag in ['numPr','sectPr','outlineLvl','pStyle']:
        for node in props.findall('w:'+tag,NS):props.remove(node)
    E.SubElement(props,'{'+W+'}pStyle').set('{'+W+'}val','Heading'+str(level) if level else 'Normal')
    return p


def add_styles(files):
    styles=E.fromstring(files['word/styles.xml'])
    ids={x.get('{'+W+'}styleId') for x in styles.findall('w:style',NS)}
    if 'Normal' not in ids:
        base=next((x.get('{'+W+'}styleId') for x in styles.findall('w:style',NS)
                   if x.get('{'+W+'}type')=='paragraph' and x.get('{'+W+'}default')=='1'),None)
        node=E.SubElement(styles,'{'+W+'}style',{'{'+W+'}type':'paragraph','{'+W+'}styleId':'Normal'})
        E.SubElement(node,'{'+W+'}name').set('{'+W+'}val','V11 Body')
        if base:E.SubElement(node,'{'+W+'}basedOn').set('{'+W+'}val',base)
        pp=E.SubElement(node,'{'+W+'}pPr')
        E.SubElement(pp,'{'+W+'}spacing',{'{'+W+'}after':'120','{'+W+'}line':'360','{'+W+'}lineRule':'auto'})
        rp=E.SubElement(node,'{'+W+'}rPr')
        E.SubElement(rp,'{'+W+'}rFonts',{'{'+W+'}ascii':'Times New Roman','{'+W+'}hAnsi':'Times New Roman'})
        E.SubElement(rp,'{'+W+'}sz').set('{'+W+'}val','22')
    for level,size in [(1,28),(2,24),(3,22)]:
        sid='Heading'+str(level)
        if sid in ids: continue
        node=E.SubElement(styles,'{'+W+'}style',{'{'+W+'}type':'paragraph','{'+W+'}styleId':sid})
        E.SubElement(node,'{'+W+'}name').set('{'+W+'}val','heading '+str(level))
        E.SubElement(node,'{'+W+'}basedOn').set('{'+W+'}val','Normal')
        pp=E.SubElement(node,'{'+W+'}pPr')
        E.SubElement(pp,'{'+W+'}keepNext')
        E.SubElement(pp,'{'+W+'}outlineLvl').set('{'+W+'}val',str(level-1))
        rp=E.SubElement(node,'{'+W+'}rPr');E.SubElement(rp,'{'+W+'}b')
        E.SubElement(rp,'{'+W+'}sz').set('{'+W+'}val',str(size))
    files['word/styles.xml']=h.serialize(styles)


def embed(files,path,rid):
    rels=E.fromstring(files['word/_rels/document.xml.rels'])
    assert not any(n.get('Id')==rid for n in rels)
    name='v11_'+path.name
    E.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=R+'/image',Target='media/'+name)
    files['word/media/'+name]=path.read_bytes()
    files['word/_rels/document.xml.rels']=h.serialize(rels)
    return h.image_paragraph(rid,path)


def references(oldbody):
    refs={}
    for p in oldbody.findall('w:p',NS):
        m=re.match(r'^(\d+)\.(.+)',h.text(p))
        if m: refs[int(m[1])]=m[2].strip()
    selected=[refs[77],refs[53],refs[52],
      'Ross, J.; Belgodere, B.; Chenthamarakshan, V.; Padhi, I.; Mroueh, Y.; Das, P. Large-scale chemical language representations capture molecular structure and properties. Nature Machine Intelligence 2022, 4, 1256–1264. https://doi.org/10.1038/s42256-022-00580-7.',
      refs[81],refs[80],refs[79],refs[78]]
    return [str(i+1)+'. '+text for i,text in enumerate(selected)]


def tables():
    s=pd.read_csv(OLD/'analysis/summary.csv')
    def metric(backbone,arm,panel):
        m=s[(s.backbone==backbone)&(s.panel==panel)&(s.arm==arm)&(s.target=='Q-HERO-405')]
        assert len(m)==1
        return m.iloc[0]
    protocols=[['Protocol','Source molecules','Supervision','Q-HERO cohort','Source seeds'],
      ['Partial fine-tuning',740,'Expert binary',411,3],
      ['Partial fine-tuning',1153,'Molecule MIC',411,3],
      ['Partial fine-tuning',1153,'Record MIC (9,338 records)',411,3],
      ['Frozen-feature intervention',681,'Pooled matched panel + controls',405,5],
      ['Frozen-feature intervention',529,'Exact S. aureus panel + controls',405,5],
      ['Frozen-feature context comparison',529,'Pooled / exact MIC + controls',405,5]]
    backbones=[['Frozen backbone','Raw RMSE','Human RMSE','Continuous MIC RMSE','Shuffled human RMSE']]
    for model,name in [('molformer','MolFormer-XL'),('c3-molformer','c3-MoLFormer'),
                       ('chemberta100m','ChemBERTa-100M'),('chemfm1b','ChemFM-1B')]:
        vals=[name,f'{metric(model,"raw-"+model,"baseline").RMSE:.3f}']
        for arm in ['expert','quant-continuous','expert-shuffled']:
            m=metric(model,arm,'matched-pooled');vals.append(f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}')
        backbones.append(vals)
    context=[['Source on same 529 molecules','Molecules','Underlying records','Q-HERO R²','Q-HERO RMSE']]
    for arm,name,records in [('expert','Final expert calls','—'),('quant-pooled','Pooled MIC',4049),
                             ('quant-sa','Exact S. aureus MIC',855),
                             ('quant-pooled-shuffled','Shuffled pooled MIC',4049),
                             ('quant-sa-shuffled','Shuffled exact S. aureus MIC',855)]:
        m=metric('molformer',arm,'context')
        context.append([name,529,records,f'{m.R2:+.3f}',f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}'])
    return {'protocols':protocols,'backbones':backbones,'context':context}


def unique_ids(tree):
    for i,node in enumerate(tree.findall('.//wp:docPr',NS),1):node.set('id',str(i))
    # No inherited bookmark links are used in the rebuilt document.
    for parent in tree.iter():
        for node in list(parent):
            if node.tag in ['{'+W+'}bookmarkStart','{'+W+'}bookmarkEnd']:parent.remove(node)


def exports(files,tree,mdpath,htmlpath):
    lines=[];out=[]
    rels={x.get('Id'):x.get('Target') for x in E.fromstring(files['word/_rels/document.xml.rels'])}
    body=tree.find('w:body',NS)
    for node in body:
        t=h.text(node)
        if node.tag=='{'+W+'}tbl':
            rows=[[h.text(c) for c in r.findall('w:tc',NS)] for r in node.findall('w:tr',NS)]
            if rows:
                lines.extend(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+
                             ['| '+' | '.join(row)+' |' for row in rows[1:]])
                out.append('<table>'+''.join('<tr>'+''.join('<'+('th' if i==0 else 'td')+'>'+html.escape(v)+'</'+('th' if i==0 else 'td')+'>' for v in row)+'</tr>' for i,row in enumerate(rows))+'</table>')
        elif t:
            style=node.find('w:pPr/w:pStyle',NS)
            name=style.get('{'+W+'}val','') if style is not None else ''
            tag={'Heading1':'h2','Heading2':'h3','Heading3':'h4'}.get(name,'p')
            content=html.escape(t)
            reading=t
            # Preserve author/affiliation superscripts in readable copies too.
            if t.startswith('Egor A. Ilin') and 'Writing' not in t:
                display=[];readingparts=[]
                for run in node.findall('w:r',NS):
                    value=''.join(x.text or '' for x in run.findall('.//w:t',NS))
                    va=run.find('w:rPr/w:vertAlign',NS)
                    sup=va is not None and va.get('{'+W+'}val')=='superscript'
                    display.append('<sup>'+html.escape(value)+'</sup>' if sup else html.escape(value))
                    readingparts.append('<sup>'+value+'</sup>' if sup else value)
                content=''.join(display);reading=''.join(readingparts)
            lines.append(reading)
            out.append('<'+tag+(' class="author-field"' if t.startswith('[COAUTHORS') else '')+'>'+content+'</'+tag+'>')
        # Embed native image parts for a portable, self-contained reading copy.
        import base64
        for el in node.iter():
            rid=el.get('{'+R+'}embed') or (el.get('{'+R+'}id') if el.tag.endswith('imagedata') else None)
            if rid and rid in rels:
                part=posixpath.normpath(posixpath.join('word',rels[rid]))
                if part in files:
                    suffix=Path(part).suffix.lower();mime={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif'}.get(suffix)
                    if mime:out.append('<img src="data:'+mime+';base64,'+base64.b64encode(files[part]).decode()+'" alt="Research figure">')
                    else:out.append('<p class="media-note">Vector/Office graphic retained in DOCX: '+html.escape(Path(part).name)+'</p>')
        lines.append('')
    mdpath.write_text('\n'.join(lines))
    htmlpath.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>'+html.escape(TITLE)+'</title><style>body{max-width:1000px;margin:40px auto;padding:0 28px;font:16px/1.6 Georgia,serif;color:#202b35}h2,h3,h4{font-family:Arial,sans-serif;line-height:1.3}img{width:100%;height:auto;margin:20px 0}table{border-collapse:collapse;font:13px/1.4 Arial,sans-serif;width:100%;margin:20px 0}td,th{border:1px solid #ccd3d8;padding:8px;text-align:left}.author-field{background:#fff3b0;padding:12px;border-left:4px solid #b78a23}.media-note{color:#6b7280;font-size:13px}@media print{body{margin:0;padding:0}table,img{break-inside:avoid}}</style><body>'+''.join(out)+'</body></html>')


def import_blocks(destination,source,blocks):
    rels=E.fromstring(destination['word/_rels/document.xml.rels'])
    oldrels={x.get('Id'):x for x in E.fromstring(source['word/_rels/document.xml.rels'])}
    mapped={};parts={};copied=[]
    for block in blocks:
        block=copy.deepcopy(block)
        for el in block.iter():
            for key,value in list(el.attrib.items()):
                if key.startswith('{'+R+'}') and value in oldrels:
                    if value not in mapped:
                        new=copy.deepcopy(oldrels[value]);rid='rIdV11Imported'+str(len(mapped)+1)
                        new.set('Id',rid);mapped[value]=rid
                        if new.get('TargetMode')!='External':
                            path=posixpath.normpath(posixpath.join('word',new.get('Target')))
                            assert path in source, path
                            name='word/media/v11_import_'+Path(path).name
                            if path not in parts: destination[name]=source[path];parts[path]=name
                            new.set('Target',posixpath.relpath(parts[path],'word'))
                        rels.append(new)
                    el.set(key,mapped[value])
        copied.append(block)
    destination['word/_rels/document.xml.rels']=h.serialize(rels)
    # Preserve formats used by moved synthesis graphics.
    ct=E.fromstring(destination['[Content_Types].xml']);other=E.fromstring(source['[Content_Types].xml'])
    extensions={x.get('Extension') for x in ct if x.tag.endswith('Default')}
    for el in other:
        if el.tag.endswith('Default') and el.get('Extension') not in extensions:
            ct.append(copy.deepcopy(el));extensions.add(el.get('Extension'))
    destination['[Content_Types].xml']=h.serialize(ct)
    styles=E.fromstring(destination['word/styles.xml']);other=E.fromstring(source['word/styles.xml'])
    ids={x.get('{'+W+'}styleId') for x in styles}
    for el in other:
        sid=el.get('{'+W+'}styleId')
        if sid and sid not in ids:styles.append(copy.deepcopy(el));ids.add(sid)
    destination['word/styles.xml']=h.serialize(styles)
    return copied


def main():
    files,tree,oldbody=read_doc(COMA/'2026_10_11_Paper_2_edited-v10_modern_models_QHERO.docx')
    source_files={k:v for k,v in files.items()}
    old=list(oldbody);normal=h.find(oldbody,'The bottleneck in this domain')
    template=next(t for t in oldbody.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
    sec=copy.deepcopy(oldbody.find('w:sectPr',NS))
    refs=references(oldbody)
    credit=copy.deepcopy(h.find(oldbody,'Egor A. Ilin: Conceptualization'))
    ack=copy.deepcopy(h.find(oldbody,'This work was supported by the Russian Science Foundation'))
    body=E.Element('{'+W+'}body')
    tree.remove(oldbody);tree.append(body)
    text=(ROOT/'main_draft.md').read_text()
    blocks=text.strip().split('\n\n');tabledata=tables();author_blocks=[]
    for i,block in enumerate(blocks):
        if block.startswith('# '):
            body.append(paragraph(normal,block[2:],1))
            for el in old[1:6]:body.append(copy.deepcopy(el))
            body.append(paragraph(normal,'Corresponding authors: Anatoly N. Vereshchagin (vereshchagin@ioc.ac.ru); Michael G. Medvedev ([COAUTHORS A1 — insert the corresponding-author email or confirm the final corresponding-author designation]).',marked=True))
        elif block.startswith('#'):
            hashes=len(block)-len(block.lstrip('#'))
            body.append(paragraph(normal,block[hashes:].strip(),min(hashes-1,3)))
        elif block.startswith('[FIGURE:'):
            key=block[8:-1];body.append(embed(files,ROOT/'figures'/FIGURES[key],'rIdV11'+key.title()))
        elif block.startswith('[TABLE:'):
            body.append(h.table(template,tabledata[block[7:-1]]))
        elif block=='[EXISTING:credit]':body.append(credit)
        elif block=='[EXISTING:acknowledgments]':body.append(ack)
        elif block=='[REFERENCES]':
            for ref in refs:body.append(paragraph(normal,ref))
        else:
            marked=block.startswith('[COAUTHORS')
            p=paragraph(normal,block,marked=marked);body.append(p)
            if block.startswith('[COAUTHORS H'):author_blocks.append(copy.deepcopy(p))
    body.append(sec);add_styles(files);unique_ids(tree)
    h.write(files,tree,MAIN)
    exports(files,tree,ROOT/'manuscript_v11_readable.md',ROOT/'manuscript_v11.html')
    build_si(source_files,old,normal)
    build_author_template(files,tree,normal,author_blocks)
    print(MAIN)


def build_author_template(sourcefiles,sourcetree,normal,blocks):
    files={k:v for k,v in sourcefiles.items()};tree=copy.deepcopy(sourcetree)
    old=tree.find('w:body',NS);sec=copy.deepcopy(old.find('w:sectPr',NS));tree.remove(old)
    body=E.SubElement(tree,'{'+W+'}body')
    body.append(paragraph(normal,'Human annotation methods — section for coauthors',1))
    body.append(paragraph(normal,'Complete fields H1–H7 and return this document. The completed text will replace Section 2.1.1 in the article. Distinguish documented records from recollection and identify any recoverable original instructions, votes or adjudication files.'))
    body.append(paragraph(normal,'Verified archive counts: 1,103 final annotation entries, 244 Good and 859 Bad, before structure standardisation and exclusions. Individual votes are not present in the supplied computational archive.'))
    for el in blocks:body.append(el)
    body.append(sec);unique_ids(tree)
    # This standalone form contains text only: discard unused document images.
    rels=E.fromstring(files['word/_rels/document.xml.rels'])
    for rel in list(rels):
        if rel.get('Type')==R+'/image':rels.remove(rel)
    files['word/_rels/document.xml.rels']=h.serialize(rels)
    referenced=set()
    for name,data in files.items():
        if not name.endswith('.rels'):continue
        base=posixpath.dirname(posixpath.dirname(name))
        for rel in E.fromstring(data):
            if rel.get('TargetMode')!='External':
                referenced.add(posixpath.normpath(posixpath.join(base,rel.get('Target'))))
    removed={name for name in files if name.startswith('word/media/') and name not in referenced}
    for name in removed:del files[name]
    ct=E.fromstring(files['[Content_Types].xml'])
    for item in list(ct):
        if item.get('PartName','').lstrip('/') in removed:ct.remove(item)
    files['[Content_Types].xml']=h.serialize(ct)
    h.write(files,tree,ROOT/'Human_annotation_methods_for_coauthors.docx')
    exports(files,tree,ROOT/'Human_annotation_methods_for_coauthors.md',ROOT/'Human_annotation_methods_for_coauthors.html')


def build_si(sourcefiles,old,normal):
    files,tree,body=read_doc(OLD/'Supplementary_Information_v10.docx')
    add_styles(files)
    for p in body.findall('w:p',NS):
        text=h.text(p)
        if text.startswith('Expert Judgement as Supervision:'):h.replace(p,TITLE)
        elif text=='Scope and submission note':h.replace(p,'Scope and evaluation protocols')
        elif text.startswith('This supporting-information version accompanies'):
            h.replace(p,'This Supporting Information accompanies the focused author draft. Partial-fine-tuning, matched frozen-feature and historical analyses use different source exclusions, cohorts and architectures. Their results are reported separately; source metadata and full prediction files accompany the computational analyses.')
        elif text.startswith('Key corrections:'):
            h.replace(p,'The main comparisons use partial backbone fine-tuning or frozen-feature adaptation as specified. MIC record counts are distinguished from unique molecules. OOD-17 is a small secondary collection, affine recalibration is exploratory and in-sample, and individual expert votes and a pre-specified equivalence criterion are unavailable in the supplied archive. The human-annotation collection protocol is reserved for coauthor completion in main Section 2.1.1.')
        elif text.startswith('Q-HERO provides 411 structures'):
            h.replace(p,'The historical Q-HERO collection contains 411 structures with a matched S. aureus MIC endpoint. The archived residual plots are descriptive. These analyses precede the strict evaluation-cation exclusions and matched controls used for Q-HERO-405; they do not establish equivalence or an independently identified expert advantage.')
        elif text.startswith('Figure S3.'):
            h.replace(p,'Figure S3. Historical absolute-residual distributions on Q-HERO. Similar distribution shapes are descriptive and do not establish equivalence; cohort and source exclusions differ from the matched Q-HERO-405 experiments.')
        elif text.startswith('Figure S5.'):
            h.replace(p,'Figure S5. Historical residual and TOST analysis, retained for transparency. The small sample and absence of a pre-specified equivalence margin make the analysis exploratory.')
        elif text.startswith('Figure S10. Supervision comparisons.'):
            h.replace(p,'Figure S10. Earlier supervision comparisons, retained as supplementary context. Partial-fine-tuning and frozen-feature panels have different cohorts and architectures. Error bars are conditional-scaffold intervals; the main text reports the nested seed/scaffold sensitivity.')
        elif text.startswith('Figure S10. Chemical-space'):
            h.replace(p,text.replace('Figure S10.','Figure S11.',1))
        elif text.startswith('Figure S11. (a)'):
            h.replace(p,text.replace('Figure S11.','Figure S12.',1))
        elif text.startswith('S11. Reproducibility'):
            h.replace(p,'S11. Reproducibility and artifact inventory')
        elif text.startswith('Figure S7.'):
            h.replace(p,'Figure S7. Downstream representation quality, mean ± standard deviation over three seeds, after partial backbone fine-tuning. The descriptor baseline is positive on Q-HERO (R² = +0.057); absolute scores remain modest.')
    for p in body.findall('.//w:tc/w:p',NS):
        if h.text(p)=='Role in v8':h.replace(p,'Source/evaluation role')
    # Rebuild heading styles for the new supplementary appendices.
    sec=body.find('w:sectPr',NS)
    def append(el):body.insert(list(body).index(sec),el)
    def add(text,level=None):append(paragraph(normal,text,level))
    add('S15. Historical contrastive, in-domain and geometric analyses',1)
    add('These historical branches are supplementary descriptive material. They use a contrastive architecture distinct from the matched 256→128 encoder, and some source exclusions or generating scripts are incomplete. They are not used to identify the main supervision-intervention effects. Citation numbers in Sections S15–S16 follow the supplementary reference list in S17.')
    sourcebody=E.Element('{'+W+'}body')
    for el in old:sourcebody.append(copy.deepcopy(el))
    def idx(prefix):
        candidates=[i for i,x in enumerate(old) if h.text(x).startswith(prefix)]
        assert len(candidates)==1,(prefix,candidates)
        return candidates[0]
    selected=[old[idx('Figure 1.')-1],old[idx('Figure 1.')]]
    selected+=old[idx('2.2 Training guidance'):idx('2.4 Out of domain')]
    selected+=old[idx('2.5 Understanding'):idx('2.6 Controlled')]
    moved=import_blocks(files,sourcefiles,selected)
    for el in moved:
        text=h.text(el)
        new=text
        if text.startswith('2.2 '):new='S15.1. Historical contrastive encoder'
        elif text.startswith('2.3 '):new='S15.2. Audited in-domain comparison'
        elif text.startswith('2.5 '):new='S15.3. Archived representation geometry and attribution'
        elif text.startswith('Figure 1.'):new='Figure S13. Historical expert-guidance diagram. This branch is distinct from the matched source-label interventions in the main article.'
        elif text.startswith('Figure 2.'):new='Figure S14. Historical t-SNE class-separation illustration for the contrastive encoder. Class separation does not establish external potency-prediction performance.'
        elif text.startswith('Figure 6.'):new='Figure S15. Historical conceptual information flow in the contrastive encoder. The diagram is not a quantitative causal decomposition.'
        elif text.startswith('Table 2.'):new='Table S9. Audited QAC-105 molecule-grouped comparison: CatBoost R², mean ± seed standard deviation over ten seeds. Molecules are held out of the target-regressor training fold; representation-training source overlap remains a limitation. Values are retained from the archived audit.'
        new=new.replace('Figure 2 presents','Figure S14 presents')
        new=new.replace('Table 2','Table S9').replace('Table 3','Tables S5–S6')
        new=new.replace('Section 2.1','Supporting Information Section S4').replace('Section 2.6','main Sections 3.2–3.3')
        if el.tag=='{'+W+'}p' and new!=text:h.replace(el,new)
        if el.tag=='{'+W+'}p' and new.startswith('S15.'):el=paragraph(normal,new,2)
        append(el)
    add('S16. Synthesis, characterisation and microbiological protocols',1)
    add('This section preserves the chemical descriptions and available protocols from the source manuscript. OOD-17 is a small secondary case study. The original text refers to additional NMR/HRMS/IR spectra, an optimisation Table S1 and auxiliary Schemes S1–S2, which are not present as primary spectrum files in the current computational folder. Those chemical supplements must be supplied by the chemistry coauthors; their identifiers below are reserved separately as Table S10 and Schemes S5–S6.')
    chemistry=old[idx('To examine out-of-domain'):idx('2.4.5 Out-of-domain')]
    chemistry+=old[idx('4.2 Chemistry'):idx('5. CRediT')]
    moved=import_blocks(files,sourcefiles,chemistry)
    for el in moved:
        text=h.text(el);new=text
        # Source chemistry citations use supplementary reference numbers 1–81.
        new=re.sub(r'\bTable S1\b','Table S10',new)
        new=new.replace('(Scheme S1)','(Scheme S5)').replace('(Scheme S2)','(Scheme S6)')
        new=re.sub(r'\bScheme ([1-4])\b',r'Scheme S\1',new)
        new=new.replace('small confirmatory case study','small descriptive case study')
        if text.startswith('Figure 4.'):new='Figure S16. Molecular classes in the historical QAC, Q-HERO and OOD collections.'
        elif text.startswith('Scheme 4.'):new='Scheme S4. Synthesis of glycoluril-based multi-QACs.'
        elif text.startswith('Scheme '):new=re.sub(r'^Scheme (\d+)\.',r'Scheme S\1.',new)
        heading=re.match(r'^(2\.4\.[1-4]|4\.2(?:\.[12])?|4\.3(?:\.[1-4])?)\s+(.+)',new)
        if heading:
            numbers={'2.4.1':'S16.1','2.4.2':'S16.2','2.4.3':'S16.3','2.4.4':'S16.4',
                     '4.2':'S16.5','4.2.1':'S16.5.1','4.2.2':'S16.5.2',
                     '4.3':'S16.6','4.3.1':'S16.6.1','4.3.2':'S16.6.2','4.3.3':'S16.6.3','4.3.4':'S16.6.4'}
            new=numbers[heading[1]]+'. '+heading[2]
            el=paragraph(normal,new,3 if numbers[heading[1]].count('.')==2 else 2)
        elif el.tag=='{'+W+'}p' and new!=text:h.replace(el,new)
        append(el)
    append(paragraph(normal,'[COAUTHORS C1 — Supply the original compound spectra and evidence of identity/purity, the optimisation table and auxiliary reaction schemes cited above; describe the final assay conditions, controls, replicate counts and endpoint conversions. Chemical Table S10 and Schemes S5–S6 are reserved for this material.]',marked=True))
    add('S17. Supplementary references for historical and chemical descriptions',1)
    add('References below preserve the source numbering used in Sections S15–S16 and other historical material. Main-article references use a separate, shorter sequence. Duplicate references 30 and 77 refer to the same MolSkill publication and are retained solely to resolve the source numbering.')
    for el in old[idx('References')+1:]:
        if h.text(el):append(copy.deepcopy(el))
    unique_ids(tree);h.write(files,tree,SI)
    exports(files,tree,ROOT/'supplement_v11_readable.md',ROOT/'Supplementary_Information_v11.html')


if __name__=='__main__':main()
