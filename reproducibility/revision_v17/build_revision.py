"""Restore the author's SI figures and introductory narrative; shorten the main text."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import posixpath
import re
import shutil
import struct
import xml.etree.ElementTree as E
import pandas as pd

ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
OLD=ROOT.parent/'revision_v16'
spec=importlib.util.spec_from_file_location('v16',OLD/'build_revision.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
v,h,NS,W,R,PKG=b.v,b.h,b.NS,b.v.W,b.v.R,b.v.PKG
MAIN=COMA/'2026_10_13_Paper_2_edited-v17_original_intro_and_expanded_SI.docx'
SI=ROOT/'Supplementary_Information_v17.docx'
ORIGINAL_SI=ROOT/'sources/Supporting_Info_original.docx'
WHO_REF=('14. World Health Organization. Antimicrobial resistance. Fact sheet, '
         '16 July 2026. https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance '
         '(accessed 2026-10-13).')
FIGURE_MAP={1:1,2:2,3:'S27',4:3,5:4,6:'S28',7:'S29',8:5}
TABLE_MAP={1:1,2:2,3:3,4:4,5:'S23',6:'S28',7:6}
INTRO=[
 'Antimicrobial resistance remains a major challenge for healthcare, while the limited '
 'pipeline of new antimicrobial medicines sustains the need for reliable experimental '
 'and computational discovery strategies (14). Quaternary ammonium compounds (QACs) '
 'provide a chemically diverse class of cationic biocides relevant to infection prevention. '
 'Predicting their antibacterial activity offers a focused setting in which to examine '
 'how molecular learning can guide the evaluation of candidate structures (2).',
 'Machine learning can support compound prioritisation, but the quality of the available '
 'supervision remains central to the modelling workflow. In a specialised chemical series, '
 'activity data can be sparse and distributed across organisms, strains and assay protocols. '
 'Repeated literature records are not independent molecules, and a larger record count '
 'does not directly measure the amount of new information supplied to a representation. '
 'The question is therefore which supervisory signal transfers to measurements on '
 'compounds excluded from source training.',
 'Domain knowledge can enter molecular models through structural constraints, task '
 'descriptions or evaluations supplied by chemists. We focus on human evaluations as '
 'supervision. Preference-learning work such as MolSkill shows that medicinal chemists’ '
 'judgements can be learned for compound prioritisation and design (1). Here we ask '
 'whether coarse Good/Bad calls also guide a representation used to predict quantitative '
 'antibacterial endpoints. A call may summarise several observations, but its information '
 'access, aggregation and independence from numerical measurements require a documented '
 'annotation protocol. We do not infer assay denoising from categorical labels alone.',
 'The choice of supervision should be separated from the amount of model adaptation. '
 'Molecular foundation models supply reusable features, and fine-tuning can improve '
 'property prediction (4). Low-rank adaptation provides another way to learn task-specific '
 'updates with fewer trainable parameters (6,13). These alternatives motivate an '
 'experimental comparison of frozen heads, LoRA, partial and full fine-tuning. Their '
 'performance under a declared budget, rather than parameter count alone, determines '
 'which adaptation procedure is useful for this small cohort.',
 'Our previous QAC framework used MolFormer-derived embeddings to predict MIC and MBC '
 'against S. aureus and E. coli (2). The present work asks where useful representation '
 'guidance comes from. We compare human calls, continuous pooled MIC and binarised MIC '
 'on identical source molecules using paired initialisations, splits and training budgets. '
 'Raw pretrained features and source-training-only shuffled labels provide complementary '
 'controls. The binary-MIC arm shares the human arm’s binary objective, helping separate '
 'quantitative resolution from the generic effect of an added training stage.',
 'We retain the original 105 QACs and 17 named compounds from four new scaffold families '
 'as the target setting. We first report predictive performance under cation and scaffold '
 'holdout, then compare graph and tabular models (9–12) and both direct target prediction '
 'and a guided encoder followed by a decoder. Finally, restoring selected encoder weights '
 'while retaining feature-map buffers tests the contribution of learned updates to '
 'held-out loss. This computational intervention does not identify a molecular '
 'antibacterial mechanism or semantic understanding (8). The focus was selected after '
 'earlier analyses; Q-HERO and backbone/context results (3,5–7), including quantitative '
 'advantages in those settings, remain in the supplement.'
]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def find(body,prefix):return b.find(body,prefix)
def section(body,start,end):
 a=list(body).index(find(body,start));z=list(body).index(find(body,end));return list(body)[a:z]
def replace_section(body,start,end,blocks):
 old=section(body,start,end);position=list(body).index(old[0])
 for el in old:body.remove(el)
 for j,el in enumerate(blocks):body.insert(position+j,el)
 return old
def rewrite_figure_table_refs(text):
 text=re.sub(r'\bFigure (\d+)\b',lambda m:'Figure '+str(FIGURE_MAP.get(int(m[1]),m[1])),text)
 return re.sub(r'\bTable (\d+)\b',lambda m:'Table '+str(TABLE_MAP.get(int(m[1]),m[1])),text)


def import_blocks(destination,source,blocks,prefix,distinct_styles=False):
 """Import native drawings without relationship, media or style collisions."""
 rels=E.fromstring(destination['word/_rels/document.xml.rels'])
 oldrels={n.get('Id'):n for n in E.fromstring(source['word/_rels/document.xml.rels'])}
 existing={n.get('Id') for n in rels};mapped={};copied=[]
 stylemap={}
 if distinct_styles:
  targetstyles=E.fromstring(destination['word/styles.xml'])
  oldstyles=E.fromstring(source['word/styles.xml'])
  stylemap={n.get('{'+W+'}styleId'):prefix+n.get('{'+W+'}styleId') for n in oldstyles if n.get('{'+W+'}styleId')}
  for item in oldstyles:
   if item.get('{'+W+'}styleId') not in stylemap:continue
   item=copy.deepcopy(item);item.set('{'+W+'}styleId',stylemap[item.get('{'+W+'}styleId')]);item.attrib.pop('{'+W+'}default',None)
   for node in item.iter():
    if node.tag in ['{'+W+'}basedOn','{'+W+'}next','{'+W+'}link']:
     value=node.get('{'+W+'}val')
     if value in stylemap:node.set('{'+W+'}val',stylemap[value])
   targetstyles.append(item)
  destination['word/styles.xml']=h.serialize(targetstyles)
 for original in blocks:
  block=copy.deepcopy(original)
  for el in block.iter():
   if el.tag in ['{'+W+'}pStyle','{'+W+'}rStyle','{'+W+'}tblStyle'] and el.get('{'+W+'}val') in stylemap:
    el.set('{'+W+'}val',stylemap[el.get('{'+W+'}val')])
   for key,value in list(el.attrib.items()):
    if not key.startswith('{'+R+'}') or value not in oldrels:continue
    if value not in mapped:
     new=copy.deepcopy(oldrels[value]);rid='rId'+prefix+str(len(mapped)+1)
     assert rid not in existing;existing.add(rid);new.set('Id',rid);mapped[value]=rid
     if new.get('TargetMode')!='External':
      path=posixpath.normpath(posixpath.join('word',new.get('Target')))
      assert path in source and path.startswith('word/media/'),path
      digest=hashlib.sha256(source[path]).hexdigest()[:20]
      name='word/media/'+prefix+'_'+digest+Path(path).suffix
      if name in destination:assert destination[name]==source[path]
      destination[name]=source[path];new.set('Target',posixpath.relpath(name,'word'))
     rels.append(new)
    el.set(key,mapped[value])
  copied.append(block)
 destination['word/_rels/document.xml.rels']=h.serialize(rels)
 content=E.fromstring(destination['[Content_Types].xml']);extensions={n.get('Extension') for n in content if n.tag.endswith('Default')}
 for n in E.fromstring(source['[Content_Types].xml']):
  if n.tag.endswith('Default') and n.get('Extension') not in extensions:
   content.append(copy.deepcopy(n));extensions.add(n.get('Extension'))
 destination['[Content_Types].xml']=h.serialize(content)
 return copied


def citation_numbers(text):
 out=[]
 for m in re.finditer(r'\((\d+(?:\s*[,–-]\s*\d+)*)\)',text):
  numbers=[]
  for part in m[1].split(','):
   bounds=re.split('[–-]',part.strip());numbers.extend(range(int(bounds[0]),int(bounds[-1])+1))
  if numbers and all(1<=n<=14 for n in numbers):out.extend(numbers)
 return out
def remap_citations(text,mapping):
 def replacement(m):
  numbers=citation_numbers(m[0])
  if not numbers:return m[0]
  values=[mapping[n] for n in numbers]
  if len(values)>2 and values==list(range(values[0],values[-1]+1)):
   return '('+str(values[0])+'–'+str(values[-1])+')'
  return '('+','.join(map(str,values))+')'
 return re.sub(r'\((\d+(?:\s*[,–-]\s*\d+)*)\)',replacement,text)


def apply_figure_style(files,tree):
 """Replace only explicitly regenerated media, including relocated hashed imports."""
 styles={'v11_figure1_supervision_and_transfer.png':'figure1_supervision_and_transfer',
  'v11_figure2_QAC105_parity.png':'figure2_QAC105_parity',
  'v11_figure3_task_encoding.png':'figureS27_task_encoding',
  'v11_figure4_OOD_families_ACS1996.png':'figure3_OOD_families_ACS1996',
  'v11_figure5_paired_error_violins.png':'figure4_paired_error_violins',
  'v11_figure6_decoder_error_violins.png':'figureS28_decoder_error_violins',
  'v11_figure7_direct_adaptation.png':'figureS29_direct_adaptation',
  'v11_figure8_weight_rewind.png':'figure5_weight_rewind',
  'figS1_expert_set.png':'figureS5_expert_set','figS2_overlap.png':'figureS6_overlap',
  'figS3_qhero_violins.png':'figureS7_qhero_violins','figS4_qhero_r2.png':'figureS8_qhero_r2',
  'figS5_equivalence.png':'figureS9_equivalence','figS6_split_effect.png':'figureS10_split_effect',
  'figS7_representation_quality_v8.png':'figureS11_representation_quality',
  'figS8_zeroshot_v8.png':'figureS12_zeroshot','figS9_calibration_v8.png':'figureS13_calibration',
  'v11_figureS17_matched_finetuning_learning.png':'figureS21_matched_finetuning_learning',
  'v11_figureS18_matched_finetuning_error_violins.png':'figureS22_matched_finetuning_error_violins',
  'v11_figureS19_OOD17_parity.png':'figureS23_OOD17_parity',
  'v11_figureS20_OOD17_individual_endpoints.png':'figureS24_OOD17_individual_endpoints',
  'v11_figureS21_scaffold_transfer.png':'figureS25_scaffold_transfer',
  'v11_figureS22_prediction_route_violins.png':'figureS26_prediction_route_violins'}
 byhash={}
 for doc in [b.MAIN,b.SI]:
  original,_,_=v.read_doc(doc)
  for name,data in original.items():
   key=Path(name).name
   if name.startswith('word/media/') and key in styles and (ROOT/'figures'/(styles[key]+'.png')).exists():
    byhash[hashlib.sha256(data).hexdigest()]=styles[key]
 replacements=[]
 for name,data in list(files.items()):
  oldhash=hashlib.sha256(data).hexdigest()
  if name.startswith('word/media/') and oldhash in byhash:
   image=ROOT/'figures'/(byhash[oldhash]+'.png');files[name]=image.read_bytes()
   replacements.append(dict(part=name,figure=byhash[oldhash],old_sha256=oldhash,new_sha256=sha(image)))
 # Update picture aspect ratios after shorter titles/legends and clamp to the page.
 ns=dict(NS,a='http://schemas.openxmlformats.org/drawingml/2006/main',
         wp='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
 rels={n.get('Id'):n for n in E.fromstring(files['word/_rels/document.xml.rels'])}
 sect=tree.find('.//w:body/w:sectPr',NS);page=sect.find('w:pgSz',NS);margins=sect.find('w:pgMar',NS)
 maxwidth=(int(page.get('{'+W+'}w'))-int(margins.get('{'+W+'}left'))-int(margins.get('{'+W+'}right')))*635
 for drawing in tree.findall('.//w:drawing',NS):
  blip=drawing.find('.//a:blip',ns)
  if blip is None:continue
  rel=rels[blip.get('{'+R+'}embed')];part=posixpath.normpath(posixpath.join('word',rel.get('Target')))
  data=files[part]
  if data[:8]!=b'\x89PNG\r\n\x1a\n':continue
  width,height=struct.unpack('>II',data[16:24]);extent=drawing.find('.//wp:extent',ns)
  if extent is None:continue
  cx=min(int(extent.get('cx')),maxwidth);cy=round(cx*height/width)
  extent.set('cx',str(cx));extent.set('cy',str(cy))
  for ext in drawing.findall('.//a:xfrm/a:ext',ns):ext.set('cx',str(cx));ext.set('cy',str(cy))
 return replacements


def main():
 (ROOT/'figures').mkdir(exist_ok=True);(ROOT/'analysis').mkdir(exist_ok=True)
 files,tree,body=v.read_doc(b.MAIN);sourcefiles=copy.deepcopy(files)
 normal=find(body,'Human annotations and numerical measurements');template=body.findall('w:tbl',NS)[1]
 def p(text,level=None):return v.paragraph(normal,text,level)
 intro=section(body,'1. Introduction','2. Results and Discussion')
 # Retain the study-design drawing and caption at the end of the rewritten introduction.
 design=[copy.deepcopy(n) for n in intro if n.find('.//w:drawing',NS) is not None or h.text(n).startswith('Figure 1.')]
 original_intro_detail=[copy.deepcopy(n) for n in intro if h.text(n).startswith('In the archived matched')]
 replace_section(body,'1. Introduction','2. Results and Discussion',
                 [p('1. Introduction',1)]+[p(t) for t in INTRO]+design)
 moved={}
 task=section(body,'2.3.','2.4.');split=next(i for i,n in enumerate(task) if h.text(n).startswith('New-cation interpolation'))
 moved['task']=task[1:split]
 replace_section(body,'2.3.','2.4.',[p('2.3. Transfer to held-out scaffolds',2)]+task[split:])
 moved['models']=replace_section(body,'2.5.','2.6.',[
  p('2.5. Transfer across graph and tabular models',2),
  p('Chemprop D-MPNN, TabPFN-V2, TabFM and AutoGluon provide additional checks of '
    'decoder dependence (9–12). In the fixed one-source-seed comparison, human-guided '
    'features have lower pooled point errors than raw features for each tabular decoder '
    'in all three regimes. Quantitative guidance has some scaffold-CV advantages, and '
    'RDKit descriptors remain a strong independent reference. The complete 21-row '
    'comparison, endpoint scores and model budgets are in Table S23, S21 and Figure S28.'),
  p('On OOD-17, human/RDKit RMSE is 1.966/1.978 for TabPFN-V2 and 1.992/2.027 for '
    'TabFM; their paired intervals include zero. Chemprop gives 2.031/2.003/2.375 '
    'under cation/scaffold/OOD evaluation. These exploratory fixed-budget results '
    'support useful transfer across decoder choices and retain competing descriptor '
    'and quantitative outcomes; they do not establish a general ranking of model classes.')])
 d=pd.read_csv(b.ANALYSIS/'direct_summary.csv');a=pd.read_csv(b.ANALYSIS/'ablation_metrics.csv')
 human=d[(d.arm=='expert')&(d['mode']=='partial')&(d.task=='pooled')].set_index('schema')
 decoder=a[(a.arm=='expert')&(a.variant=='intact')&a.seed.isin([0,1,2])&(a.task=='pooled')].groupby('schema').RMSE.mean()
 route_rows=[['Prediction route','Paired source seeds','Cation CV','Scaffold CV','OOD-17'],
             ['Direct partial target FT','0–2']+[f'{human.loc[s].RMSE:.3f}' for s in b.SCHEMES],
             ['Frozen guided encoder + CatBoost','0–2']+[f'{decoder.loc[s]:.3f}' for s in b.SCHEMES]]
 moved['direct']=replace_section(body,'2.6.','2.7.',[
  p('2.6. Direct prediction and model adaptation',2),
  p('We tested direct MIC/MBC prediction with frozen linear and MLP heads, query/value '
    'LoRA, partial and full fine-tuning, plus all real and shuffled source '
    'initialisations. All 363 fits use three paired target seeds, train-only target '
    'standardisation and a fixed 30-epoch budget. Complete scores and parameter '
    'counts are in Tables S28–S29 and Figure S29. From pretrained initialisation, '
    'cation-CV RMSE is 1.863 for full fine-tuning, 2.013 for a frozen linear head '
    'and 2.040 for LoRA. LoRA minus full ΔRMSE is +0.177 [+0.071, +0.286]; this '
    'procedure does not support universal small-adapter superiority.'),
  h.table(template,route_rows),
  p('Table 5. Both prediction routes using the same first three human-guided source '
    'checkpoints. Values are means of seed-specific pooled RMSE in log2(mg/L), '
    'rather than ensemble errors. The primary five-source-seed decoder scores '
    'remain in Tables 2–4; the complete route comparisons are in S24–S26 and '
    'Figure S26.'),
  p('Human source initialisation yields direct cation/scaffold/OOD RMSE '
    '1.797/1.834/2.412. Real numerical initialisations have lower cation point errors '
    '(continuous MIC 1.737; binary MIC 1.745), while human guidance has lower '
    'scaffold and OOD point errors. The direct human-minus-shuffled scaffold '
    'contrast is −0.156 [−0.311, −0.009]. On OOD, human direct prediction versus '
    'the frozen-encoder route differs by +0.306 [−0.278, +0.971]. The observed '
    'benefit of source guidance and the choice of target predictor remain '
    'conditional on the declared budget and evaluation regime.')])
 causal=section(body,'2.7.','2.8.')
 core=[copy.deepcopy(n) for n in causal if n.tag=='{'+W+'}tbl' or
       n.find('.//w:drawing',NS) is not None or h.text(n).startswith(('Table 7.','Figure 8.'))]
 moved['causal']=[n for n in causal[1:] if not (n.tag=='{'+W+'}tbl' or n.find('.//w:drawing',NS) is not None or h.text(n).startswith(('Table 7.','Figure 8.')))]
 replace_section(body,'2.7.','2.8.',[
  p('2.7. What label and weight interventions identify',2),
  p('Learned signal is defined here as the contribution of adapted encoder '
    'parameters to held-out MIC/MBC loss. We restore the pretrained outer '
    'LayerNorm, upper eight blocks or all encoder parameters, retain source '
    'feature-map buffers, and refit the same decoder for every representation. '
    'Within seed, buffers are shared across source arms; restoring all weights '
    'makes their representations and predictions identical. The pure raw '
    'reference retains its original buffers and is evaluated separately.')]+core+[
  p('For human guidance, restoring all weights raises cation-CV RMSE by '
    '+0.109 [+0.037, +0.201]. Scaffold and OOD contrasts are +0.097 '
    '[−0.004, +0.228] and +0.243 [−0.067, +0.582], respectively, and include '
    'zero. The numerical arms and component-specific controls are reported '
    'alongside the human arm in Table 7, Figure 8 and S25–S26. The supported '
    'result is a learned-weight contribution to the specified cation-held-out '
    'prediction procedure, with unresolved scaffold/OOD effects.'),
  p('Real-versus-shuffled labels test supervision assignment; weight rewinds '
    'test sensitivity to learned parameter updates. Neither identifies the '
    'causal action of a chemical fragment or a named human concept. Whether '
    'the labels constitute an independent human-information channel remains '
    'conditional on the collection and information-access records in H1–H7. '
    'Geometry and attribution analyses, earlier overlapping-source encoders '
    'and further component interpretation remain separately documented in '
    'S15, S22 and S28.')])
 moved['reproduction']=replace_section(body,'2.8.','3. Conclusions',[
  p('2.8. Reproducibility and historical-score provenance',2),
  p('Independent repeats recover all 30 matched source-training runs and '
    'the archived target representations under the original encoding layout. '
    'All 93 intact/raw prediction sets and all 33 reloaded final-OOD target '
    'models reproduce saved predictions. Changed encoding batches expose '
    'numerical sensitivity; some historical Mac-to-Linux branches remain '
    'unresolved. Recovered notebook outputs support earlier scores under '
    'different validation protocols. Full audit results, historical numbers '
    'and replay conditions are retained in S22, S27 and S28.')])
 for start,end,key,text in [
  ('4.6.','4.7.','model_methods','All graph and tabular comparisons use the same '
   'target folds and concentration units. Preprocessing is fitted only on '
   'outer training data; guided tabular features use source seed 0, and '
   'Chemprop uses three graph-training seeds. The 913-fit configuration, '
   'train-only PCA, exact checkpoints, inner selection and model-specific '
   'budgets are specified in S21 and S28.'),
  ('4.7.','4.8.','reproduction_methods','Reproduction checks retain source identities, '
   'label and weight hashes, minibatch order and all evaluation buffers. '
   'Archived encoding layout and independently reloaded checkpoints are '
   'verified separately from recovery of historical notebook outputs. '
   'The complete records and unresolved branches are described in S22 and S27.'),
  ('4.8.','Supporting Information','direct_methods','Direct fits use three paired '
   'source/target seeds, a four-output head, train-only target scaling and '
   '30 fixed epochs without OOD-based selection. LoRA uses query/value '
   'rank-eight updates (13). Weight controls use five source seeds, fixed '
   'checkpoint buffers and a refitted one-hot CatBoost decoder for each '
   'intervention. New contrasts use 5,000 paired seed/group draws; three '
   'paired seeds and four OOD families limit uncertainty estimation. '
   'All settings, 363 direct fits, 1,331 weight-control fits and checkpoint '
   'retention details are in S24–S28.')]:
  old=section(body,start,end);moved[key]=old[1:];replace_section(body,start,end,[copy.deepcopy(old[0]),p(text)])
 # Figure/table numbering is changed only in the main text and relocated main-text blocks.
 for node in body.findall('w:p',NS):
  text=h.text(node);new=rewrite_figure_table_refs(text)
  if new!=text:h.replace(node,new)
 # The newly constructed route table already has its final number and final SI cross-references.
 caption=find(body,'Table S23. Both prediction routes')
 h.replace(caption,'Table 5.'+h.text(caption)[len('Table S23.'):])
 # Reference numbers in the original main text are assigned by first appearance.
 refheading=find(body,'References');oldrefs=[n for n in list(body)[list(body).index(refheading)+1:] if re.match(r'^\d+\. ',h.text(n))]
 refs={int(re.match(r'^(\d+)\.',h.text(n))[1]):h.text(n).split('. ',1)[1] for n in oldrefs};refs[14]=WHO_REF.split('. ',1)[1]
 mapping={}
 for node in list(body)[:list(body).index(refheading)]:
  for num in citation_numbers(h.text(node)):
   if num not in mapping:mapping[num]=len(mapping)+1
 assert set(mapping)==set(range(1,15)),mapping
 for node in body.findall('w:p',NS):
  if node in oldrefs:continue
  text=h.text(node);new=remap_citations(text,mapping)
  if new!=text:h.replace(node,new)
 for n in oldrefs:body.remove(n)
 anchor=body.find('w:sectPr',NS)
 b.b.insert_before(body,anchor,[p(str(mapping[num])+'. '+refs[num]) for num in sorted(mapping,key=mapping.get)])
 statement=find(body,'Full annotation/source audits;')
 h.replace(statement,'The expanded Supporting Information retains the author’s four original '
   'classification/embedding figures, all archived computational and chemical records, '
   'the original 105 structures and all 17 OOD compounds, every prediction and qualifier, '
   'full graph/tabular and direct-fine-tuning tables, task-encoding and decoder figures, '
   'component interventions, censored-endpoint derivation and historical notebook '
   'provenance. Detailed discussion and configurations relocated from the main text '
   'appear in S28. Annotation and assay records remain for coauthor completion.')
 caption=find(body,'Figure 1.')
 h.replace(caption,h.text(caption)+' Source representations use five paired seeds; '
   'the supplementary direct-target comparison uses the same first three source checkpoints.')
 caption=find(body,'Figure 2.')
 h.replace(caption,h.text(caption).replace('while annotation boxes report mean seed-specific scores rather than ensemble scores',
   'while Table 2 reports mean seed-specific scores rather than ensemble scores'))
 caption=find(body,'Figure 4.')
 h.replace(caption,h.text(caption)+' Sa and Ec denote S. aureus and E. coli, respectively.')
 main_style=apply_figure_style(files,tree)
 v.TITLE=h.text(body[0]);v.unique_ids(tree);h.write(files,tree,MAIN)
 v.exports(files,tree,ROOT/'manuscript_v17_readable.md',ROOT/'manuscript_v17.html')
 # SI retains all v16 content; original author figures lead the expanded file.
 si_files,si_tree,si_body=v.read_doc(b.SI);oldsi=list(si_body)
 def sp(text,level=None):return v.paragraph(normal,text,level)
 for node in si_body.findall('w:p',NS):
  text=h.text(node)
  new=re.sub(r'\bFigures? S(\d+)(?:[–-]S?(\d+))?',
      lambda m:('Figures ' if m[2] else 'Figure ')+'S'+str(int(m[1])+4)+('–S'+str(int(m[2])+4) if m[2] else ''),text)
  if new!=text:h.replace(node,new)
 original_files,_,original_body=v.read_doc(ORIGINAL_SI)
 original_blocks=import_blocks(si_files,original_files,[n for n in original_body if n.tag!='{'+W+'}sectPr'],
                              'V17Original',distinct_styles=True)
 captions=['F1 scores across four representations in the original five-fold classification study.',
           'Classification accuracy across representations in the original supplementary study.',
           'Fold-specific classification scores from the original supplementary study.',
           'Geometrical cluster diagnostics before and after the historical contrastive encoder.']
 c=0
 for n in original_blocks:
  if h.text(n).startswith('Рисунок '):
   h.replace(n,'Figure S'+str(c+1)+'. '+captions[c]+' Retained from the author’s original Supporting_Info.docx; '
             'this is separate from the matched MIC/MBC regression and weight-intervention protocols.');c+=1
 assert c==4
 front=[sp('Supporting Information',1),sp(h.text(body[0])),
        sp('Original supplementary figures and expanded computational record',2),
        sp('Figures S1–S4 preserve the four original author-supplied figures. Their '
           'classification and geometrical analyses are retained as historical material '
           'with their own protocol; they do not substitute for the new source-excluded '
           'MIC/MBC regression comparisons. Earlier computational Figures S1–S22 are '
           'renumbered S5–S26. Section and table numbers retain their existing sequence.')]+original_blocks
 for j,n in enumerate(front):si_body.insert(j,n)
 anchor=si_body.find('w:sectPr',NS)
 def add(n):si_body.insert(list(si_body).index(anchor),n)
 add(sp('S28. Detailed discussion and methods relocated from the main text',1))
 add(sp('This section preserves the detailed v16 discussion after shortening the main '
        'article. Full numerical tables already present as Tables S23 and S28 are not '
        'duplicated. References in S28 follow the renumbered main-article bibliography. '
        'The chemistry/assay records in S16 and coauthor fields are retained.'))
 groups=[('S28.1. Task descriptions and encoding',moved['task']),
         ('S28.2. Graph and tabular decoder comparison',moved['models'][1:]),
         ('S28.3. Direct-target performance and adaptation capacity',moved['direct'][1:]),
         ('S28.4. Label and component-weight interpretation',moved['causal']),
         ('S28.5. Historical scores and independent replay',original_intro_detail+moved['reproduction'][1:]+moved['reproduction_methods']),
         ('S28.6. Complete model configurations',moved['model_methods']+moved['direct_methods'])]
 for j,(title,blocks) in enumerate(groups):
  add(sp(title,2));filtered=[]
  for n in blocks:
   t=h.text(n)
   if n.tag=='{'+W+'}tbl' or t.startswith(('Table 5.','Table 6.')):continue
   if t.startswith(('2.','4.')) and re.match(r'^[24]\.\d+\. ',t):continue
   filtered.append(n)
  for n in import_blocks(si_files,sourcefiles,filtered,'V17Moved'+str(j)):
   t=h.text(n)
   if t:
    t=remap_citations(rewrite_figure_table_refs(t),mapping)
    t=t.replace('Figure S22','Figure S26')
    h.replace(n,t)
   add(n)
 # Add numerical source-table pointers beside the relocated discussion.
 add(sp('The complete decoder comparison formerly shown as main Table 5 is Table S23. '
        'The complete direct-target configuration table formerly shown as main Table 6 '
        'is Table S28. Figures S27–S29 retain the task-encoding, decoder-error and '
        'direct-adaptation plots relocated from the main article. Figure S26 compares '
        'the two prediction routes using the same first three source checkpoints.'))
 caption=find(si_body,'Figure S26.')
 h.replace(caption,h.text(caption).replace('(blue, left)','(lavender, left)').replace('(orange, right)','(mint, right)')+
   ' IT505 E. coli MBC >500 mg/L is excluded from exact-value densities; '
   'its separately retained minimum-error sensitivity is derived in Table S33.')
 caption=find(si_body,'Figure S28.')
 h.replace(caption,h.text(caption).replace('Colours compare all five representations.',
   'Grey, blue, lavender, mint and peach identify RDKit, raw, human, continuous-MIC '
   'and binary-MIC features, respectively.'))
 caption=find(si_body,'Figure S29.')
 h.replace(caption,h.text(caption)+' Strategies are identified by their x-axis labels; '
   'a common neutral colour avoids reusing source-supervision colours.')
 si_style=apply_figure_style(si_files,si_tree)
 v.unique_ids(si_tree);h.write(si_files,si_tree,SI)
 v.TITLE=h.text(body[0]);v.exports(si_files,si_tree,ROOT/'supplement_v17_readable.md',ROOT/'Supplementary_Information_v17.html')
 assets=[(ROOT.parent/'revision_v14/figures/figure3_task_encoding','figureS27_task_encoding'),
         (ROOT.parent/'revision_v15/figures/figure6_decoder_error_violins','figureS28_decoder_error_violins'),
         (OLD/'figures/figure7_direct_adaptation','figureS29_direct_adaptation'),
         (OLD/'figures/figureS22_prediction_route_violins','figureS26_prediction_route_violins'),
         (OLD/'figures/figure8_weight_rewind','figure5_weight_rewind')]
 for source,name in assets:
  for ext in ['png','pdf','svg']:
   file=Path(str(source)+'.'+ext)
   destination=ROOT/'figures'/(name+'.'+ext)
   if file.exists() and not destination.exists():shutil.copyfile(file,destination)
 (ROOT/'document_style_replacements.json').write_text(json.dumps(dict(main=main_style,SI=si_style),indent=2))
 inputs=[b.MAIN,b.SI,ORIGINAL_SI,COMA/'2026_07_09_Paper_2_edited-v5_NF_3.docx',
         b.ANALYSIS/'direct_summary.csv',b.ANALYSIS/'ablation_metrics.csv']
 (ROOT/'input_manifest.json').write_text(json.dumps({str(p):sha(p) for p in inputs},indent=2))
 (ROOT/'relocation_manifest.json').write_text(json.dumps(dict(
  original_SI='/Users/egorilin/Downloads/Supporting_Info.docx',original_figures='S1–S4',
  preceding_SI_figure_offset=4,moved_main_figures={'3':'S27','6':'S28','7':'S29'},
  kept_main_figures={'1':1,'2':2,'4':3,'5':4,'8':5},
  moved_tables={'5':'S23','6':'S28'},old_main_weight_table='Table 6',
  bibliography_old_to_new=mapping,original_intro_source='2026_07_09_Paper_2_edited-v5_NF_3.docx'),indent=2))
 paragraphs=[];heading='Front matter'
 for node in body:
  t=h.text(node)
  if re.match(r'^[1-4]\. ',t) or re.match(r'^[24]\.\d+\. ',t):heading=t
  if heading=='Front matter' or not t or node.tag=='{'+W+'}tbl' or t.startswith(('[COAUTHORS','Figure ','Table ')) or re.match(r'^[1-4]\. |^[24]\.\d+\. ',t):continue
  if t=='Supporting Information':break
  paragraphs.append(dict(number=len(paragraphs)+1,section=heading,text=t))
 (ROOT/'paragraphs_for_summary.json').write_text(json.dumps(paragraphs,indent=2,ensure_ascii=False))
 print(MAIN);print(SI);print('Substantive paragraphs',len(paragraphs))


if __name__=='__main__':main()
