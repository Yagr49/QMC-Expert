"""Build a revised manuscript and SI while retaining existing DOCX media and styles."""
from pathlib import Path
import copy, json, zipfile, html, struct
from xml.etree import ElementTree as E
import pandas as pd
ROOT=Path(__file__).resolve().parent
COMA=ROOT.parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
PIC='http://schemas.openxmlformats.org/drawingml/2006/picture'
NS={'w':W,'r':R,'wp':WP,'a':A}
for prefix,uri in {'w':W,'r':R,'wp':WP,'a':A,'pic':PIC,'rel':PKG,
                   'mc':'http://schemas.openxmlformats.org/markup-compatibility/2006'}.items():
    E.register_namespace(prefix,uri)
def serialize(tree):
    # ElementTree omits declarations referenced only by mc:Ignorable values.
    compat='http://schemas.openxmlformats.org/markup-compatibility/2006'
    known={'w14':'http://schemas.microsoft.com/office/word/2010/wordml',
           'w15':'http://schemas.microsoft.com/office/word/2012/wordml',
           'w16se':'http://schemas.microsoft.com/office/word/2015/wordml/symex',
           'w16cid':'http://schemas.microsoft.com/office/word/2016/wordml/cid',
           'w16':'http://schemas.microsoft.com/office/word/2018/wordml',
           'w16cex':'http://schemas.microsoft.com/office/word/2018/wordml/cex',
           'w16sdtdh':'http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash',
           'w16sdtfl':'http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock',
           'w16du':'http://schemas.microsoft.com/office/word/2023/wordml/word16du',
           'wp14':'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing'}
    used={el.tag.split('}')[0][1:] for el in tree.iter() if el.tag.startswith('{')}
    for prefix in tree.get(f'{{{compat}}}Ignorable','').split():
        if prefix in known and known[prefix] not in used:tree.set('xmlns:'+prefix,known[prefix])
    return E.tostring(tree,xml_declaration=True,encoding='UTF-8')
META=json.loads((ROOT/'analysis/analysis_meta.json').read_text())
assert META['complete'], 'Do not build final documents from incomplete experiments'
S=pd.read_csv(ROOT/'analysis/summary.csv')
P=pd.read_csv(ROOT/'analysis/paired_bootstrap.csv')
D=json.loads((ROOT/'data/meta.json').read_text())
OUTPUT=COMA/'2026_10_11_Paper_2_edited-v9_supervision_controls.docx'
SI=ROOT/'Supplementary_Information_v9.docx'
TITLE='Human Binary Annotations Compete with Quantitative MIC Supervision: Controlled Tests of Molecular Representation Learning for QAC Biocides'

def text(p):return ''.join(t.text or '' for t in p.findall('.//w:t',NS)).strip()
def find(body,prefix):
    found=[p for p in body.findall(f'{{{W}}}p') if text(p).startswith(prefix)]
    if len(found)!=1:raise ValueError((prefix,len(found)))
    return found[0]
def replace(p,t,marked=False):
    for el in list(p):
        if el.tag!=f'{{{W}}}pPr':p.remove(el)
    r=E.SubElement(p,f'{{{W}}}r')
    if marked:E.SubElement(E.SubElement(r,f'{{{W}}}rPr'),f'{{{W}}}highlight').set(f'{{{W}}}val','yellow')
    E.SubElement(r,f'{{{W}}}t').text=t
def clone(template,t):
    p=copy.deepcopy(template);replace(p,t);return p
def add_sequence(body,anchor,elements):
    pos=list(body).index(anchor)
    for i,el in enumerate(elements):body.insert(pos+i,el)
def table(template,rows):
    t=copy.deepcopy(template)
    templates=t.findall(f'{{{W}}}tr')
    for r in templates:t.remove(r)
    for i,values in enumerate(rows):
        r=copy.deepcopy(templates[0 if i==0 else 1]);cells=r.findall(f'{{{W}}}tc')
        rp=r.find(f'{{{W}}}trPr')
        if rp is not None:
            for height in rp.findall(f'{{{W}}}trHeight'):rp.remove(height)
        if i==0:
            if rp is None:rp=E.SubElement(r,f'{{{W}}}trPr')
            if rp.find(f'{{{W}}}tblHeader') is None:E.SubElement(rp,f'{{{W}}}tblHeader')
        assert len(cells)==len(values)
        for c,v in zip(cells,values):
            pp=c.findall(f'{{{W}}}p')
            for p in pp[1:]:c.remove(p)
            replace(pp[0],str(v))
            for run in pp[0].findall(f'{{{W}}}r'):
                props=E.Element(f'{{{W}}}rPr');run.insert(0,props)
                E.SubElement(props,f'{{{W}}}sz').set(f'{{{W}}}val','18')
                if i==0:E.SubElement(props,f'{{{W}}}b')
        t.append(r)
    return t
def image_paragraph(rid,path):
    b=path.read_bytes();width,height=struct.unpack('>II',b[16:24]);cx=5943600;cy=int(cx*height/width)
    xml=f'''<w:p xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="{WP}" xmlns:a="{A}" xmlns:pic="{PIC}">
    <w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>
    <wp:docPr id="9907" name="Supervision controls" descr="Partial fine-tuning and paired label-intervention results"/>
    <a:graphic><a:graphicData uri="{PIC}"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="figure7_supervision_controls.png"/><pic:cNvPicPr/></pic:nvPicPr>
    <pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
    <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
    </pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''
    return E.fromstring(xml)
def embed(files,tree):
    rels=E.fromstring(files['word/_rels/document.xml.rels'])
    ids={r.get('Id') for r in rels};rid='rIdV9Figure7';assert rid not in ids
    r=E.SubElement(rels,f'{{{PKG}}}Relationship',Id=rid,Type=f'{R}/image',Target='media/figure7_supervision_controls.png')
    files['word/media/figure7_supervision_controls.png']=(ROOT/'figures/figure7_supervision_controls.png').read_bytes()
    files['word/_rels/document.xml.rels']=serialize(rels)
    return image_paragraph(rid,ROOT/'figures/figure7_supervision_controls.png')
def write(files,tree,path):
    files['word/document.xml']=serialize(tree)
    if 'word/settings.xml' in files:
        settings=E.fromstring(files['word/settings.xml'])
        update=settings.find(f'{{{W}}}updateFields')
        if update is None:update=E.SubElement(settings,f'{{{W}}}updateFields')
        update.set(f'{{{W}}}val','true')
        files['word/settings.xml']=serialize(settings)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
def metric(panel,arm,head,target):
    return S[(S.panel==panel)&(S.arm==arm)&(S['head']==head)&(S.target==target)].iloc[0]
def number(panel,arm,target='Q-HERO-405',col='RMSE'):
    return f'{metric(panel,arm,"catboost",target)[col]:.3f}'

ABSTRACT='''Binary human annotations can provide useful supervision for molecular activity modelling, but useful signal, competitive prediction and causal attribution require different tests. We compare final expert Good/Bad labels with molecule-level and record-level quantitative MIC supervision, organism-matched MIC, and quantitative mammalian-cell cytotoxicity for quaternary ammonium compounds. In an archived partial-fine-tuning experiment excluding evaluation structures from all sources, downstream Q-HERO R² was 0.269 with 740 expert labels and 0.312/0.308 with 1,153 molecule-level MIC values/9,338 MIC records. New frozen-backbone interventions use identical source molecules, scaffold splits, initial weights and training budgets. On 681 common molecules, real expert labels improved external Q-HERO RMSE relative to shuffled expert labels by 0.175 log2 µM (95% scaffold-bootstrap interval −0.258 to −0.058), while continuous pooled MIC was stronger by 0.109 (0.007 to 0.210). This expert-label benefit was not reproduced on the smaller 529-molecule organism-matched panel. Direct expert scores also ranked measured potency without numerical concentrations as model targets. The evidence establishes a useful, protocol-dependent human supervision signal and practical competition under partial fine-tuning. The controlled intervention identifies an effect of supervision within the specified algorithm; it does not identify an antibacterial mechanism, a general effect of human expertise, or equivalence between individual labels and measurements.'''
INTRO_EXPERT='''Expert knowledge can also enter a model as a supervision target. Human preference learning has already shown that chemists’ decisions can be captured and used in molecular prioritisation and design (77). The question addressed here is more specific: can coarse Good/Bad judgements compete with numerical biological measurements when learning a representation for antibacterial QAC modelling? We distinguish three propositions: the labels contain transferable activity-related information; the resulting representation is practically competitive with quantitative supervision; and changing the supervision causes a performance change under a fixed computational protocol. These propositions require separate evidence. In particular, a controlled intervention on a training procedure is distinct from identifying causal variables in molecular antibacterial action (78).'''
INTRO_DATA='''The bottleneck in this domain includes the definition and context of supervision. A pooled MIC value can combine different organisms, strains and assay conditions; repeated records are not independent molecules. A binary expert judgement may compress multiple observations and other considerations, but that possibility is a hypothesis rather than a demonstrated denoising mechanism. We therefore compare broad quantitative MIC, exact S. aureus MIC and 24h MTT mammalian-cell cytotoxicity as distinct numerical supervision sources. Cytotoxicity is represented by a merged CC50/IC50/EC50 field in the available ILToxDB export (79); it is a cross-endpoint comparison rather than an antibacterial measurement. No single scalar endpoint is assumed to contain the same information as an expert judgement.'''
INTRO_CONTRIBUTIONS='''Building on our MolFormer-based QAC modelling framework, we test expert supervision at two levels. First, the partial-fine-tuning analysis compares final expert labels with molecule-level and record-level quantitative MIC under a shared downstream-refitting protocol. Second, new matched-molecule interventions hold the source identities, input features, initial weights, scaffold partition and training budget constant while changing supervision. Continuous MIC, binary MIC, shuffled-label and untrained-encoder controls separate label content from quantitative resolution and architecture. A further comparison of full eligible sources assesses practical performance, while explicitly retaining the effects of source size and composition. The study therefore tests the value and limits of human supervision without treating predictive attribution as a molecular causal explanation.'''
SECTION=[
('heading','2.6 Controlled supervision interventions and quantitative-source comparisons'),
('normal','''The partial-fine-tuning results demonstrate practical competition, but they do not isolate supervision content because the sources differ in molecule count and training objective. We therefore ran an additional frozen-MolFormer experiment with a 768→256→128 neural encoder and identical source molecules within each comparison panel. All target cations, including counterion variants, were excluded from every source. Conflicting expert labels were removed. The new evaluation cohorts comprise 104 non-conflicting in-domain salts, 405 non-conflicting Q-HERO salts after target-cation overlap removal, and the 17-compound OOD set. These stricter cohorts and the frozen-backbone architecture differ from the partial-fine-tuning experiment and are reported separately.'''),
('normal','''The pooled-MIC panel contains 681 common molecules with 4,938 underlying records; the exact S. aureus panel contains 529 common molecules with 855 records. Within each panel we compare real expert labels, continuous MIC, MIC binarised at a source-training threshold targeting the expert positive prevalence, permuted expert labels, permuted continuous MIC and an untrained encoder. MIC ties prevent exact prevalence matching. Five paired initialisation seeds, one shared scaffold-disjoint source split and 80 fixed training epochs are used. Target scaffold folds and downstream decoder settings are identical across arms. The source validation partition is diagnostic and does not select a checkpoint.'''),
('normal','''For the pooled panel, mean Q-HERO-405 CatBoost RMSE is 1.607 for expert labels, 1.497 for continuous MIC, 1.646 for binary MIC and 1.780 for shuffled expert labels (Table 3). The paired expert-minus-shuffled-expert difference is −0.175 log2 µM, with a 95% whole-scaffold bootstrap interval of [−0.258, −0.058]. This control shows that the real label assignment matters in this panel. Expert supervision is not measurably better than raw MolFormer: ΔRMSE = +0.005 [−0.092, +0.109]. Nor does it outperform continuous MIC: expert minus continuous MIC is +0.109 [+0.007, +0.210]. The expert-versus-binary-MIC interval includes zero (−0.039 [−0.139, +0.136]); it is not an equivalence result.'''),
('normal','''On the smaller S. aureus-matched panel, the expert-label benefit does not reproduce. Mean Q-HERO RMSE is 1.785 for real expert labels, 1.761 for shuffled expert labels and 1.617 for continuous MIC. Expert minus shuffled labels is +0.025 [−0.139, +0.311], and expert minus continuous MIC is +0.169 [−0.004, +0.454]. Restricting the panel changes the selected chemical collection as well as its size; this contrast cannot identify an organism-matching effect. The result sets a clear limit: transferable expert information and practical competition do not imply a consistent benefit from every expert-trained encoder.'''),
('table','matched'),
('normal','''Table 3. New matched-molecule supervision experiment on Q-HERO-405 with a CatBoost decoder, mean ± standard deviation over five source-training seeds. Pooled MIC and exact S. aureus MIC use separate common-molecule panels. Reported seed variation is not a confidence interval across independent chemical datasets. Paired molecule- and scaffold-bootstrap contrasts, all secondary targets, and the Ridge sensitivity analysis are supplied in Supporting Information Section S7.'''),
('normal','''The practical full-source comparison uses 712 expert-labelled molecules, 1,120 pooled-MIC molecules, 888 exact S. aureus-MIC molecules and 273 ILToxDB cytotoxicity molecules. Mean Q-HERO R² is 0.095, 0.246, 0.185 and 0.083, respectively (Figure 7d). These results extend the comparison to several numerical supervision definitions, including an independent cytotoxicity source, but show that expert supervision does not uniformly match the best quantitative arm in the frozen-head setting. Because source size, coverage, label definition and experimental context differ, the ranking is a practical observation rather than a causal effect of endpoint or provenance.'''),
('figure',''),
('normal','''Figure 7. Protocol dependence of expert supervision. (a) Archived partial fine-tuning yields competitive downstream representation quality on Q-HERO (three seeds). (b,c) New matched-molecule frozen-backbone interventions on pooled and exact S. aureus MIC panels; bars show 95% paired whole-scaffold bootstrap intervals conditional on five trained seeds and fixed target folds. Negative ΔRMSE favours human labels. (d) New full-source comparison has unequal source sizes and cannot isolate endpoint or provenance. Panels use different cohorts and architectures and must not be interpreted as one interchangeable leaderboard.'''),
('normal','''The causal estimand is the change in external predictive loss when a supervision assignment/objective is replaced within this fixed training pipeline. Both predictions are observed for each held-out molecule under paired runs, so a paired loss contrast is sufficient; a causal forest fitted to duplicated prediction rows would add no identification. Real-versus-permuted expert labels preserve molecule identities, class counts, architecture and training budget while disrupting the structure–label relation. The five shuffled runs are diagnostic controls, not a calibrated multi-permutation hypothesis test. The experiment supplies bounded evidence about algorithmic supervision content; it does not show that experts identify membrane-disruption mechanisms or remove laboratory bias.'''),
('normal','''Quantitative-source interpretation also requires care. The local QMR same-compound/same-strain audit contains 38 replicate strata over only 23 compounds and five strains: median log2 range is zero, with 94.7% within one dilution. Within-group variation across S. aureus strains has median range 1 log2 unit over 279 strata. These selectively available replicates do not establish universal assay reproducibility, but they do prevent the pooled conflict rate from being interpreted as a pure inter-laboratory error rate. Likewise, the Q-HERO/QMR/ILToxDB transfer contrasts remain confounded by source selection, chemical composition, assay context and aggregation. Human labels as robust compression of heterogeneous evidence remain an explanation to test, rather than an established cause of their performance.'''),
]

def build_main():
    source=COMA/'2026_07_09_Paper_2_edited-v8_scientifically_revised.docx'
    files={n:zipfile.ZipFile(source).read(n) for n in zipfile.ZipFile(source).namelist()}
    tree=E.fromstring(files['word/document.xml']);body=tree.find(f'{{{W}}}body')
    normal=copy.deepcopy(find(body,'The bottleneck in this domain'))
    heading=copy.deepcopy(find(body,'2.5 Understanding'))
    changes=[]
    replacements={
        'Expert Judgement as Supervision:':TITLE,
        'Binary expert annotations may offer':ABSTRACT,
        'Cationic biocides;':'Cationic biocides; quaternary ammonium compounds; human supervision; quantitative MIC; controlled ablation; molecular representation learning; transfer learning',
        'A distinct and older line of work treats':INTRO_EXPERT,
        'The bottleneck in this domain':INTRO_DATA,
        'In our previous work, we established':INTRO_CONTRIBUTIONS,
        'An extension of this idea that is particularly':'Transfer across biological tasks can be informative when the relevant signals are aligned, but shared charge or a membrane-active phenotype alone does not guarantee transferability. Antimicrobial peptide fine-tuning and BERT-based MIC regression illustrate quantitative supervision strategies (35,36). Here cross-endpoint cytotoxicity supervision is evaluated empirically rather than assumed to encode antibacterial potency. Numerical performance, direct potency ranking and a causal explanation of transfer are treated as separate outcomes.',
        'The original architecture comparison is omitted from v8':'The historical architecture table is not used for comparative inference because its RMSE and R² entries combine different pipelines and split definitions. Table 2 retains the audited molecule-grouped comparison; the new cation-clean supervision interventions are reported separately in Table 3.',
        'Historical analyses of one-hot and text-encoded':'Historical analyses of one-hot and text-encoded task labels are exploratory because the corresponding metrics were generated under incompatible pipelines and splits. They are not evidence for the controlled supervision comparisons reported here.',
        'For exploratory model selection, we benchmarked':'For exploratory model selection, we benchmarked MolFormer, ChemBERTa, Morgan, and MACCS representations under a five-fold stratified protocol. MolFormer produced the highest archived mean F1-score (0.655 with an MLP and StandardScaler) and accuracy (0.856). Because the expert-label set is imbalanced, accuracy alone is not interpreted as a performance claim; these internal model-selection diagnostics are separate from external validation.',
        'For understanding how the resulting embeddings work':'Representational similarity and matched prediction contrasts answer different questions. Archived CKA/probing describes geometry, whereas the new interventions in Section 2.6 manipulate supervision within a fixed algorithm. Neither a similarity score nor SHAP attribution identifies molecular antibacterial mechanisms (78).',
        'Taken together, the archived analyses suggest':'The archived analyses describe preservation of pretrained geometry and similar downstream behaviour under some protocols. Their incomplete provenance precludes a quantitative causal decomposition. Section 2.6 supplies a stronger test of supervision content through paired interventions, while retaining the distinction between an algorithmic effect and antibacterial causality.',
        'In this work we examined whether':'Final human Good/Bad annotations contain activity-related information that can be learned and transferred to quantitative QAC modelling. This study establishes useful signal and practical competition under a specified partial-fine-tuning protocol, then tests their limits using matched-molecule interventions and several numerical supervision definitions.',
        'First, under downstream refitting':'Under partial fine-tuning and downstream refitting, 740 expert-labelled molecules yield Q-HERO R² = 0.269 compared with 0.312/0.308 for 1,153 molecule-level MIC values/9,338 MIC records. This is the principal evidence that coarse human supervision can compete in representation learning. The new frozen-backbone experiment sharpens the conclusion: real expert labels outperform shuffled labels on the pooled common-molecule panel, but continuous MIC is stronger and the expert-label benefit does not reproduce on the smaller organism-matched panel. Competition is therefore protocol-dependent, and does not establish measurement replacement, statistical equivalence or a label-to-record exchange rate.',
        'Second, the transfer protocol matters':'Direct transfer provides complementary evidence: the expert model receives binary training targets rather than concentrations, yet its scores rank measured potency on the evaluation collections. Quantitative MIC supervision gives stronger direct ranking on Q-HERO and OOD-17. Numerical MIC calibration and ranking are distinct tasks; the archived affine recalibration is in-sample and exploratory, and the 17-compound OOD estimates remain imprecise.',
        'Third, archived representational analyses':'The defensible causal claim concerns changing supervision within a fixed computational procedure. The new real-versus-shuffled control supports this claim in one defined panel; it does not identify a biological mechanism or prove that human judgement removes assay heterogeneity. Individual annotation votes, annotation cost, prospective performance and a pre-specified non-inferiority criterion are unavailable. The results motivate testing human labels as a compact supervision signal while specifying the task, source chemistry, training procedure and transfer regime in which they are competitive.',
        'The final expert labels are archived':'The final expert labels are archived, whereas individual votes and adjudication records are not; no inter-rater agreement is reported. The historical QAC-105 analyses contain source overlap, while the partial-fine-tuning experiment removes all evaluation full-salt identities and the new frozen-head experiment removes evaluation cation identities including counterion variants. The latter additionally excludes conflicting target and expert labels. The two experiments therefore have different cohorts and cannot be pooled. OOD-17 is a small case study. In-sample recalibration, incomplete CKA/SHAP provenance and unavailable annotation-cost records limit calibration, mechanism and economic-efficiency claims.',
        '76.Henschel,':'76.Clinical and Laboratory Standards Institute. Methods for Dilution Antimicrobial Susceptibility Tests for Bacteria That Grow Aerobically. 12th ed.; CLSI standard M07; CLSI: Wayne, PA, 2024. https://clsi.org/shop/standards/m07/.',
    }
    for prefix,value in replacements.items():
        p=find(body,prefix);changes.append({'before':text(p),'after':value});replace(p,value)
    assay=find(body,'The synthesized QACs were dissolved')
    old=text(assay);new=old.replace('The MIC and MBC of the antimicrobials was determined by the microdilution method in culture broth, as indicated by the Clinical and Laboratory Standards Institute of the United States of America 76.','MIC and MBC were determined by broth microdilution. General broth-dilution methodology is described in CLSI M07 (76); this citation identifies the relevant methodological standard without independently verifying all details of the archived assays.')
    if old==new:raise ValueError('Assay replacement failed')
    replace(assay,new);changes.append({'before':old,'after':new})
    # Replace the inaccurate manually paginated TOC with a Word-updatable field.
    toc_container=next(el for el in body if text(el).startswith('Table of contents'))
    toc_index=list(body).index(toc_container)
    if toc_container.tag==f'{{{W}}}sdt':
        body.remove(toc_container)
        toc=clone(heading,'Table of contents');body.insert(toc_index,toc)
    else:
        toc=toc_container;abstract=find(body,'Abstract')
        i,j=list(body).index(toc),list(body).index(abstract)
        for el in list(body)[i+1:j]:body.remove(el)
    field=E.Element(f'{{{W}}}p')
    for kind,value in [('begin',None),('instruction',' TOC \\o "1-3" \\h \\z \\u '),('separate',None),('text','Update this table of contents in Word to refresh headings and page numbers.'),('end',None)]:
        r=E.SubElement(field,f'{{{W}}}r')
        if kind=='instruction':E.SubElement(r,f'{{{W}}}instrText').text=value
        elif kind=='text':E.SubElement(r,f'{{{W}}}t').text=value
        else:E.SubElement(r,f'{{{W}}}fldChar').set(f'{{{W}}}fldCharType',kind)
    body.insert(list(body).index(toc)+1,field)
    template=next(t for t in body.findall(f'{{{W}}}tbl') if len(t.find(f'{{{W}}}tr').findall(f'{{{W}}}tc'))==5)
    rows=[['Common-molecule panel','Supervision','Source n','Q-HERO R²','Q-HERO RMSE']]
    for panel in ['matched-pooled','matched-sa']:
        for arm in ['expert','quant-continuous','quant-binary','expert-shuffled','quant-shuffled','untrained']:
            m=metric(panel,arm,'catboost','Q-HERO-405');label={'expert':'Human labels','quant-continuous':'Continuous MIC','quant-binary':'Binary MIC','expert-shuffled':'Shuffled human','quant-shuffled':'Shuffled MIC','untrained':'Untrained encoder'}[arm]
            rows.append(['Pooled MIC' if panel=='matched-pooled' else 'S. aureus MIC',label,D[panel]['molecules'],f'{m.R2:+.3f} ± {m.R2_sd:.3f}',f'{m.RMSE:.3f} ± {m.RMSE_sd:.3f}'])
    els=[]
    for kind,value in SECTION:
        if kind=='table':els.append(table(template,rows))
        elif kind=='figure':els.append(embed(files,tree))
        else:els.append(clone(heading if kind=='heading' else normal,value))
    add_sequence(body,find(body,'3. Conclusion'),els)
    method='''The new controlled experiment uses deterministic frozen MolFormer features (revision 7b12d946c181a37f6012b9dc3b002275de070314; maximum token length 202; no prepared molecule is truncated). A shared cation-Murcko scaffold split with 15% source validation and seed 1729 is used within each common-molecule panel. Source input scaling and quantitative-target scaling are fitted only on source training. Encoders are trained with AdamW (learning rate 0.001, weight decay 0.01), batch size 64, 80 epochs and five paired initialisation seeds. Binary objectives use BCE-with-logits; continuous objectives use standardised MSE. The supervision replacement includes the declared objective when binary and continuous arms are compared. Shuffling permutes labels within source training only. Downstream CatBoost uses 300 iterations, depth 5, learning rate 0.05 and fixed seed 1729; a Ridge decoder with alpha 10 and target-training feature standardisation is a prespecified sensitivity analysis. Source-validation losses are recorded without checkpoint selection. QAC-104 and Q-HERO-405 use shared five-fold cation-scaffold partitions; OOD-17 uses a decoder trained on QAC-104. Pooled MIC retains the archive’s unified numerical field across organisms, including coded censoring bounds; the S. aureus source requires an exact MIC qualifier. OOD values follow the archived conversion to log2 micromolar MIC and are a secondary small-set analysis.'''
    limits='''Paired RMSE contrasts are calculated from squared losses averaged across five trained source seeds before taking square roots. Ten thousand paired bootstrap resamples use either full-salt molecule identities or entire cation-scaffold clusters. Intervals are conditional on the fixed target folds and trained seed set; seeds and individual endpoint rows are not independent chemical datasets. No equivalence margin is imposed after seeing results. These exploratory interventions follow the archived analyses and are not a preregistered confirmatory trial. The Ridge sensitivity exhibits severe extrapolation instability in some arms, and does not establish decoder-independent gains; all Ridge results, including extreme errors, are retained in the supplementary tables and machine-readable predictions.'''
    add_sequence(body,find(body,'4.2 Chemistry'),[clone(normal,method),clone(normal,limits)])
    refs=[
        '77.Choung, O.-H.; Vianello, R.; Segler, M.; Stiefl, N.; Jiménez-Luna, J. Extracting medicinal chemistry intuition via preference machine learning. Nature Communications 2023, 14, 6651. https://doi.org/10.1038/s41467-023-42242-1.',
        '78.Schölkopf, B.; Locatello, F.; Bauer, S.; Ke, N. R.; Kalchbrenner, N.; Goyal, A.; Bengio, Y. Towards Causal Representation Learning. 2021. https://arxiv.org/abs/2102.11107.',
        '79.Toukach, P. V.; Arakelyan, L. A.; Egorova, K. S. ILToxDB: A Database on Cytotoxicity of Ionic Liquids. Environmental Science & Technology Letters 2025, 12, 1631–1635. https://doi.org/10.1021/acs.estlett.5c00860.',
    ]
    for ref in refs:body.insert(len(body)-1,clone(normal,ref))
    write(files,tree,OUTPUT)
    (ROOT/'changes.json').write_text(json.dumps({'base':str(source),'output':str(OUTPUT),'replacements':changes,'added_sections':SECTION},ensure_ascii=False,indent=2))
    # Editable reading copy follows the actual DOCX paragraph/table order.
    lines=[]
    for el in body:
        if el.tag==f'{{{W}}}p':lines.append(text(el))
        elif el.tag==f'{{{W}}}tbl':
            tr=el.findall(f'{{{W}}}tr');rr=[[' / '.join(text(p) for p in c.findall(f'{{{W}}}p')) for c in r.findall(f'{{{W}}}tc')] for r in tr]
            for k,row in enumerate(rr):
                lines.append('| '+' | '.join(row)+' |')
                if k==0:lines.append('| '+' | '.join(['---']*len(row))+' |')
    (ROOT/'manuscript_v9_readable.md').write_text('\n\n'.join(lines))
    return template,normal,heading

def build_si(table_template,normal,heading):
    source=COMA/'reproducibility/Supplementary_Information_v8_scientifically_revised.docx'
    files={n:zipfile.ZipFile(source).read(n) for n in zipfile.ZipFile(source).namelist()}
    tree=E.fromstring(files['word/document.xml']);body=tree.find(f'{{{W}}}body')
    first=body.find(f'{{{W}}}p');replace(first,'Supporting Information — Human Supervision and Controlled Quantitative Comparisons')
    content=[('heading','S7. New controlled supervision experiments'),('normal',method_summary()),('figure',''),('normal','Figure S10. Supervision comparisons. This is Figure 7 from the revised manuscript; the partial-fine-tuning and frozen-head panels have different cohorts and architectures.'),('normal','Table S5. New experiment RMSE in log2 µM, mean ± SD across five source-training seeds (one raw baseline run). Both CatBoost and Ridge are reported. Extreme Ridge errors are retained as sensitivity results rather than removed.'),('table','metrics'),('heading','S8. Paired supervision contrasts'),('normal','Table S6. Q-HERO-405 CatBoost expert-minus-comparator ΔRMSE with 95% whole-scaffold bootstrap intervals. Negative values favour expert supervision. Contrasts average squared errors across seeds before forming RMSE; they therefore differ slightly from subtracting the means of seed-specific RMSE.'),('table','contrasts'),('heading','S9. Quantitative-source provenance and interpretation'),('normal','The full eligible sources contain 712 final expert-labelled molecules, 1,120 pooled-MIC molecules, 888 exact S. aureus-MIC molecules and 273 ILToxDB molecules. The QMR source is one corpus represented with different filters and aggregation, not multiple independent datasets. The three earlier Veresh workbooks are corpus versions. Q-HERO is the external antibacterial evaluation collection in the new experiment. Full-source comparisons vary chemistry and sample size and cannot identify endpoint/provenance effects.'),('normal','QMR same-compound/same-strain repeated-report audit: 38 strata over 23 compounds and five strains, median range 0 log2, 94.7% within one dilution. Within-group strain sensitivity: 279 strata, median range 1 log2. These results do not support assigning all discordant pooled records to laboratory error. The cytotoxicity export mixes CC50/IC50/EC50 in one field, even after restricting to 24h MTT. Source-comparison and repeat-range results are descriptive.'),('heading','S10. What the experiment identifies'),('normal','The manipulated variable is supervision inside a fixed training algorithm. Expert versus shuffled expert contrasts preserve sample identities, initialisation, source split, architecture, objective and training budget. Expert versus continuous MIC also changes the loss objective. The paired effect is conditional on the declared source chemistry, architecture and transfer protocol. The real-label advantage appears in the 681-molecule pooled panel, and does not replicate in the 529-molecule organism-matched panel. No antibacterial mechanism, universal denoising effect, non-inferiority margin or economic saving is identified.'),('normal','The quantitative continuous arm is stronger than expert supervision in the pooled frozen-head panel. The historical partial-fine-tuning analysis still shows practical competition. These observations answer different questions and must be reported together. A successful label-versus-shuffled-label contrast does not by itself demonstrate an improvement over the raw backbone or over the best quantitative source.'),('heading','S11. Reproducibility and artifact inventory'),('normal','Reproducibility files: revision_v9/PROTOCOL.md; prepare_experiment.py; run_interventions.py; analyse_interventions.py; data/meta.json; data/smiles.json and molformer.npy; results_*/training.csv, target_folds.csv, metrics.csv and predictions.csv; analysis/summary.csv and paired_bootstrap.csv. Input workbook hashes, feature hashes, initial-weight hashes and matched-source-identity hashes are recorded. The protocol was written before inspecting new prediction results, but follows earlier exploratory work and is not formal preregistration.'),('normal','The historical direct expert seed-0 predictions provide Spearman ρ = 0.453 on Q-HERO, with a molecule-bootstrap interval [0.373, 0.526]. This interval is conditional on one checkpoint and does not account for scaffold dependence; the manuscript therefore leads with the three-seed mean rank result and treats this additional interval as a descriptive sensitivity analysis. Corresponding OOD-17 and QAC-105 intervals are retained in analysis/archived_direct_expert_rank.csv.'),('normal','Original v8 sections remain the supporting record for the historical analyses. Their revision labels refer to the archived experiment. The new results do not retrospectively repair the historical few-shot scan, make in-sample calibration external, or recover individual expert votes.')]
    blocks=[]
    metric_rows=[['Panel','Supervision / decoder','QAC-104 RMSE','Q-HERO-405 RMSE','OOD-17 RMSE']]
    for panel in ['baseline','matched-pooled','matched-sa','full']:
        arms=S[S.panel==panel].arm.unique()
        for arm in arms:
            for head in ['catboost','ridge']:
                row=[panel,arm+' / '+head]
                for target in ['QAC-104','Q-HERO-405','OOD-17']:
                    m=metric(panel,arm,head,target);row.append(f'{m.RMSE:.3f}'+(f' ± {m.RMSE_sd:.3f}' if pd.notna(m.RMSE_sd) else ''))
                metric_rows.append(row)
    contrast_rows=[['Panel','Expert minus','ΔRMSE','95% lower','95% upper']]
    for _,r in P[(P['head']=='catboost')&(P.target=='Q-HERO-405')&(P.unit=='scaffold')].iterrows():contrast_rows.append([r.panel,r.comparison.replace('expert minus ',''),f'{r.delta_RMSE:+.3f}',f'{r.ci_low:+.3f}',f'{r.ci_high:+.3f}'])
    for kind,value in content:
        if kind=='figure':blocks.append(embed(files,tree))
        elif kind=='table':blocks.append(table(table_template,metric_rows if value=='metrics' else contrast_rows))
        else:blocks.append(clone(heading if kind=='heading' else normal,value))
    sect=body.find(f'{{{W}}}sectPr');anchor=sect if sect is not None else list(body)[-1]
    add_sequence(body,anchor,blocks);write(files,tree,SI)
    parts=['<!doctype html><meta charset="utf-8"><title>Supporting Information v9</title><style>body{font:16px/1.55 Georgia,serif;max-width:1100px;margin:40px auto;padding:20px}table{border-collapse:collapse;font:13px Arial;width:100%;margin:20px 0}td,th{border:1px solid #ccc;padding:8px}img{width:100%}</style><h1>Supporting Information v9 — new experiments</h1><p>The DOCX includes the historical v8 sections and these new S7–S11 sections.</p>']
    for kind,value in content:
        if kind=='heading':parts.append('<h2>'+html.escape(value)+'</h2>')
        elif kind=='normal':parts.append('<p>'+html.escape(value)+'</p>')
        elif kind=='figure':parts.append('<img alt="Supervision controls" src="figures/figure7_supervision_controls.png">')
        elif kind=='table':
            rr=metric_rows if value=='metrics' else contrast_rows;parts.append('<table>'+''.join('<tr>'+''.join('<'+('th' if i==0 else 'td')+'>'+html.escape(str(v))+'</'+('th' if i==0 else 'td')+'>' for v in row)+'</tr>' for i,row in enumerate(rr))+'</table>')
    (ROOT/'Supplementary_Information_v9.html').write_text('\n'.join(parts))

def method_summary():
    return 'The new experiment holds source molecules, source cation-scaffold split, frozen MolFormer features, initial weights and training budget constant within each matched panel. Source sizes: 681 pooled-MIC common molecules (4,938 underlying records) and 529 exact S. aureus-MIC common molecules (855 records). Evaluation sizes: QAC-104 = 104, Q-HERO-405 = 405, OOD-17 = 17. Every evaluation cation, including counterion variants, is absent from all new sources. Binary source labels use BCE-with-logits; quantitative source targets use source-training standardised MSE. A 768→256→128 neural encoder is trained for 80 epochs with five paired seeds. Target decoders refit on fixed target folds, so this is representation evaluation rather than direct transfer. Bootstrap intervals condition on those folds and trained seeds. The Ridge decoder with target-training standardisation can extrapolate unstably; all extreme results remain available. No non-inferiority or equivalence margin is introduced.'

if __name__=='__main__':
    template,normal,heading=build_main();build_si(template,normal,heading)
    print(OUTPUT);print(SI)
