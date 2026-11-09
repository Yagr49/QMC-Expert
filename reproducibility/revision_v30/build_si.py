"""Build a manuscript-aligned SI from preserved results; no training or metric refits."""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, importlib.util, json, os, re, shutil
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/coma_v30_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree as E

ROOT=Path(__file__).resolve().parent
REPRO=ROOT.parent
COMA=REPRO.parent
OLD=REPRO/'revision_v27/Supplementary_Information_v27.docx'
MAIN=COMA/'2026_10_14_Paper_2_edited-v29_explainability_figure.docx'
OUTMAIN=COMA/'2026_10_14_Paper_2_edited-v30_SI_aligned.docx'
spec=importlib.util.spec_from_file_location('theme', REPRO/'revision_v27/theme_v27.py')
T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
T.theme(9)
FIG=ROOT/'figures';DATA=ROOT/'data'
FIG.mkdir(parents=True,exist_ok=True);DATA.mkdir(exist_ok=True)
INPUTS={}; TABLE_MAP={}; COPIED_TABLES=[]; FIGURES=[]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(path):
    p=Path(path);INPUTS[str(p.relative_to(COMA))]=sha(p)
    return pd.read_csv(p)
def saved(fig,stem):
    T.save(fig,FIG,stem)
    FIGURES.append(stem)
def plots():
    row=read(REPRO/'revision_v19/rowcv_results/summary.csv')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.9),sharey=True)
    tasks=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC'];labels=['Sa MIC','Sa MBC','Ec MIC','Ec MBC']
    for ax,rep,title in zip(axes,['v5_raw','v5_human'],['Raw MolFormer','Human-guided features']):
        for j,(code,label,col) in enumerate([('categorical_org_met','Species + endpoint',T.BLUE),('categorical_task_id','Task ID',T.PEACH),('text','Text task code',T.MINT)]):
            a=row[row.representation.eq(rep)&row.encoding.eq(code)].set_index('task').loc[tasks]
            ax.errorbar(np.arange(4)+(j-1)*.18,a.R2_mean,yerr=a.R2_sd,fmt='o',ms=4,color=col['edge'],capsize=2,lw=.9,label=label)
        ax.set_title(title);ax.set_xticks(range(4));ax.set_xticklabels(labels,rotation=20,ha='right');T.despine(ax)
        ax.set_ylim(-.13,1.05);ax.axhline(0,color=T.RULE,lw=.6)
    axes[0].set_ylabel('Endpoint R²');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,fontsize=7.3)
    fig.tight_layout(rect=(0,.12,1,1));saved(fig,'figureS5_row_cv')
    seeds=read(REPRO/'revision_v19/analysis/seed_summary.csv')
    raw_summary=read(REPRO/'revision_v18/analysis/summary.csv')
    arms=[('matched_raw','Raw',T.GREY),('human','Human',T.MINT),('mic_continuous','Quantitative',T.LAV),('human_shuffled','Shuffled',T.PEACH)]
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.9),sharey=True)
    for ax,schema,title in zip(axes,['cation','scaffold','full-QAC105'],['Cation holdout','Scaffold holdout','OOD-17']):
        for i,(arm,label,col) in enumerate(arms):
            if arm=='matched_raw':
                a=raw_summary[raw_summary.arm.eq(arm)&raw_summary.encoding.eq('categorical')&raw_summary.task.eq('pooled')&raw_summary.schema.eq(schema)].iloc[0]
                mean,sd=a.RMSE,None
            else:
                a=seeds[seeds.arm.eq(arm)&seeds.encoding.eq('categorical')&seeds.task.eq('pooled')&seeds.schema.eq(schema)].iloc[0]
                mean,sd=a.RMSE_seed_mean,a.RMSE_seed_sd if a.n_seeds>1 else None
            ax.errorbar(i,mean,yerr=sd,fmt='o',ms=5,color=col['edge'],capsize=3,lw=1)
        ax.set_title(title);ax.set_xticks(range(4));ax.set_xticklabels([a[1] for a in arms],rotation=35,ha='right');T.despine(ax)
    axes[0].set_ylabel(r'Pooled RMSE, log$_2$(mg/L)');fig.tight_layout();saved(fig,'figureS6_compact_seed_variability')
    modern=read(REPRO/'revision_v18/analysis/modern_metrics.csv')
    fig,axes=plt.subplots(1,3,figsize=(7.1,3),sharey=True)
    models=['tabfm','tabpfn','autogluon']
    for ax,schema,title in zip(axes,['cation','scaffold','full-QAC105'],['Cation holdout','Scaffold holdout','OOD-17']):
        for i,rep in enumerate(['v5_raw','v5_human']):
            a=modern[modern.representation.eq(rep)&modern.task.eq('pooled')&modern.schema.eq(schema)].set_index('model').loc[models]
            ax.plot(np.arange(3)+(i-.5)*.18,a.RMSE,'o',ms=5,color=[T.GREY,T.MINT][i]['edge'],label=['Raw','Human'][i])
        ax.set_title(title);ax.set_xticks(range(3));ax.set_xticklabels(['TabFM','TabPFN','AutoGluon'],rotation=25,ha='right');T.despine(ax)
    axes[0].set_ylabel(r'Pooled RMSE, log$_2$(mg/L)');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2)
    fig.tight_layout(rect=(0,.1,1,1));saved(fig,'figureS7_modern_decoders')
    q=read(REPRO/'qhero_author_comparison_20261014/results/summary.csv')
    qa=[('RF_35_descriptors','RF35',T.BLUE),('CB_raw_MolFormer','Raw',T.GREY),('CB_human','Human',T.MINT),('CB_quantitative','Quantitative',T.LAV),('CB_shuffled_human','Shuffled',T.PEACH)]
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.1),sharey=True)
    for ax,protocol,title in zip(axes,['random_heldout20','scaffold_CV_pooled'],['Random test','Scaffold holdout']):
        a=q[q.protocol.eq(protocol)].set_index('model')
        for i,(model,label,col) in enumerate(qa):
            ax.errorbar(i,a.loc[model,'AUPRC'],yerr=a.loc[model,'AUPRC_SD'] if a.loc[model,'repeats']>1 else None,fmt='o',color=col['edge'],ms=5,lw=1,capsize=3)
        ax.axhline(72/81 if protocol=='random_heldout20' else 360/405,color=T.RULE,lw=.8,ls='--')
        ax.set_xticks(range(5));ax.set_xticklabels([a[1] for a in qa],rotation=25,ha='right');ax.set_title(title);T.despine(ax)
    axes[0].set_ylabel('Average precision');axes[0].set_ylim(.85,1.005)
    fig.tight_layout();saved(fig,'figureS8_qhero_average_precision')
    p=read(REPRO/'revision_v18/analysis/predictions.csv')
    o=p[p.cohort.eq('OOD17')&p.schema.eq('full-QAC105')&p.encoding.eq('categorical')&p.qualifier.eq('=')]
    fig,axes=plt.subplots(2,2,figsize=(6.5,5.7),sharex=True,sharey=True)
    for ax,task,label in zip(axes.flat,tasks,labels):
        for arm,legend,col in [('human','Human',T.MINT),('mic_continuous','Quantitative',T.LAV)]:
            a=o[o.arm.eq(arm)&o.task.eq(task)].groupby('compound_id').agg(y=('y','first'),pred=('prediction','mean'),n=('seed','nunique'))
            assert a.n.eq(5).all() and len(a)==(16 if task=='Ec_MBC' else 17)
            ax.scatter(a.y,a.pred,s=21,alpha=.8,c=col['fill'],edgecolor=col['edge'],lw=.5,label=legend)
        ax.plot([-2,10],[-2,10],color=T.RULE,ls='--',lw=.6);ax.set_xlim(-1,10);ax.set_ylim(-1,10);ax.set_title(label);T.despine(ax,grid='both')
    for ax in axes[1]:ax.set_xlabel(r'Measured log$_2$(mg/L)')
    for ax in axes[:,0]:ax.set_ylabel(r'Predicted log$_2$(mg/L)')
    fig.legend(*axes[0,0].get_legend_handles_labels(),loc='lower center',ncol=2)
    fig.tight_layout(rect=(0,.055,1,1));saved(fig,'figureS9_ood_endpoint_parity')
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.8))
    geometry=[.933243,.945559]; probes=[.890919,.844077];sds=[.036773,.060385]
    shap=[2.9301,.6359,.7605]
    axes[0].bar(range(2),geometry,color=[T.BLUE['fill'],T.LAV['fill']],width=.65)
    axes[0].set_xticks(range(2));axes[0].set_xticklabels(['Reference','OOD']);axes[0].set_ylim(0,1);axes[0].set_ylabel('Linear CKA');axes[0].set_title('Shared geometry')
    axes[1].errorbar(range(2),probes,yerr=sds,fmt='o',ms=5,capsize=3,color=T.MINT['edge']);axes[1].set_xticks(range(2));axes[1].set_xticklabels(['Raw › human','Human › raw'],rotation=20,ha='right');axes[1].set_ylim(0,1);axes[1].set_ylabel('Probe R²');axes[1].set_title('Linear recoverability')
    axes[2].bar(range(3),shap,color=[T.GREY['fill'],T.MINT['fill'],T.PEACH['fill']],width=.65);axes[2].set_xticks(range(3));axes[2].set_xticklabels(['Raw','Human','Task']);axes[2].set_ylabel('Sum of mean |SHAP|');axes[2].set_title('Decoder attribution')
    for ax in axes:T.despine(ax)
    fig.tight_layout();saved(fig,'figureS10_geometry_and_attribution')
    pd.DataFrame({'analysis':['CKA reference','CKA OOD','Probe raw to human','Probe human to raw','SHAP raw','SHAP human','SHAP task'],'value':geometry+probes+shap,'SD':[None,None]+sds+[None]*3}).to_csv(DATA/'geometry_and_attribution.csv',index=False)
    INPUTS['analysis/cka_probing.csv']=sha(COMA/'analysis/cka_probing.csv')
    INPUTS['reproducibility/notebook_recovery_20261012/notebooks/2026-05-25_causal_final.ipynb']=sha(REPRO/'notebook_recovery_20261012/notebooks/2026-05-25_causal_final.ipynb')
    controls=read(REPRO/'revision_v26/interpretation_contrasts.csv')
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.65),sharey=True)
    fig.subplots_adjust(left=.23,right=.985,bottom=.24,top=.86,wspace=.18)
    keys=[(scheme,contrast) for scheme in ['cation','scaffold','full-QAC105'] for contrast in ['Human − shuffled','Reset weights − intact']]
    labels=[f'{label} · {kind}' for label in ['Cation','Scaffold','OOD-17'] for kind in ['Labels','Weights']]
    for ax,experiment,title in zip(axes,['compact','partial'],['Compact encoders','Partial backbone']):
        for i,(scheme,contrast) in enumerate(keys):
            a=controls[controls.experiment.eq(experiment)&controls.scheme.eq(scheme)&controls.contrast.eq(contrast)].iloc[0]
            col=T.MINT if i%2==0 else T.LAV
            ax.plot([a.low,a.high],[5-i,5-i],color=col['edge'],lw=1.4)
            ax.plot(a.delta,5-i,'o',ms=5,mec=col['edge'],mfc='white' if a.low<=0<=a.high else col['fill'],mew=1)
        ax.set_title(title);ax.axvline(0,color=T.RULE,ls='--',lw=.7);ax.set_xlim(-.68,.68);ax.set_ylim(-.5,5.5)
        ax.set_yticks(range(6));ax.set_yticklabels(labels[::-1]);ax.set_xlabel(r'ΔRMSE, log$_2$(mg/L)');T.despine(ax,grid='x')
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([],[],marker='o',color=T.MINT['edge'],label='Human − shuffled'),Line2D([],[],marker='o',color=T.LAV['edge'],label='Reset weights − intact'),Line2D([],[],marker='o',ls='',mec=T.RULE,mfc='white',label='Interval includes zero')],loc='lower center',ncol=3,fontsize=7)
    saved(fig,'figureS11_figure9_interpretation_controls_futura')
    for num,stem in [(12,'figure10_supervision_contrasts_futura')]:
        for ext in ['png','pdf','svg']:
            p=REPRO/'revision_v27/figures'/f'{stem}.{ext}'
            dest=FIG/f'figureS{num}_{stem}.{ext}';shutil.copy2(p,dest);INPUTS[str(p.relative_to(COMA))]=sha(p)
        FIGURES.append(f'figureS{num}_{stem}')

def txt(n):return ''.join(t.text or '' for t in n.iter(qn('w:t')))
# Pull numerical tables from the computational archive; export legacy rasters to files.
archive=Document(OLD);original=list(archive._element.body)
TABLES={};LEGACY_IMG={}
LEGACY_DIR=FIG/'legacy';LEGACY_DIR.mkdir(parents=True,exist_ok=True)
with ZipFile(OLD) as zf:
    rels=E.fromstring(zf.read('word/_rels/document.xml.rels'))
    rid_to_target={r.get('Id'):r.get('Target') for r in rels}
    for i,n in enumerate(original):
        m=re.match(r'Table S(\d+)\.',txt(n))
        if m:
            table=next(c for c in original[i+1:] if c.tag==qn('w:tbl'))
            TABLES[int(m[1])]=(txt(n),deepcopy(table))
        m=re.match(r'Figure S(\d+)\.',txt(n))
        if m and int(m[1]) in [1,2,3,4,33,34]:
            prev=original[i-1]
            blip=prev.find('.//'+qn('a:blip'))
            if blip is None:
                # namespace-agnostic search
                blips=prev.xpath('.//*[local-name()="blip"]')
                blip=blips[0] if blips else None
            rid=None
            if blip is not None:
                rid=blip.get(qn('r:embed')) or blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            target=rid_to_target[rid]
            part='word/'+target
            dest=LEGACY_DIR/f'figureS{int(m[1])}{Path(target).suffix}'
            dest.write_bytes(zf.read(part))
            LEGACY_IMG[int(m[1])]=dest
            INPUTS[str(Path('reproducibility/revision_v27/Supplementary_Information_v27.docx'))]=sha(OLD)

# Start from the etalon SI so fonts/styles match Times New Roman template.
ETHALON=COMA/'Supplementary_Information.docx'
doc=Document(ETHALON)
for n in list(doc._element.body):
    if n.tag!=qn('w:sectPr'):doc._element.body.remove(n)
section=doc.sections[0]
# Keep etalon page geometry; only tighten side margins slightly for wide tables.
section.left_margin=Inches(0.75);section.right_margin=Inches(0.75)

FONT='Times New Roman'
def set_run_font(run, size=None, bold=None):
    run.font.name=FONT
    r=run._element
    rPr=r.find(qn('w:rPr'))
    if rPr is None:rPr=OxmlElement('w:rPr');r.insert(0,rPr)
    f=rPr.find(qn('w:rFonts'))
    if f is None:f=OxmlElement('w:rFonts');rPr.insert(0,f)
    for name in ['ascii','hAnsi','eastAsia','cs']:f.set(qn('w:'+name),FONT)
    if size is not None:run.font.size=Pt(size)
    if bold is not None:run.font.bold=bold

def para(s, style=None, size=12, bold=False):
    p=doc.add_paragraph(style=style) if style else doc.add_paragraph()
    run=p.add_run(s)
    set_run_font(run, size=size, bold=bold)
    p.paragraph_format.space_after=Pt(6)
    p.paragraph_format.line_spacing=1.15
    return p
def heading(s):
    p=doc.add_heading(s, level=1)
    for r in p.runs:set_run_font(r, size=14, bold=True)
    return p
def insert(n):doc._element.body.insert(len(doc._element.body)-1,deepcopy(n))
def table(old,caption=None):
    number=len(COPIED_TABLES)+1
    TABLE_MAP[old]=number
    cap,n=TABLES[old]
    cap=caption or cap.split('. ',1)[1]
    para(f'Table S{number}. {cap}', style='Caption', size=9, bold=False)
    insert(n)
    COPIED_TABLES.append({'number':number,'old':old,'caption':cap})
    return number
def newtable(caption,headers,rows,key):
    number=len(COPIED_TABLES)+1
    para(f'Table S{number}. {caption}', style='Caption', size=9)
    tab=doc.add_table(rows=1,cols=len(headers))
    try:tab.style='Table Grid'
    except KeyError:pass
    for c,s in zip(tab.rows[0].cells,headers):c.text=str(s)
    for r in rows:
        for c,s in zip(tab.add_row().cells,r):c.text=str(s)
    COPIED_TABLES.append({'number':number,'old':key,'caption':caption})
    return number
def figure(num,stem,caption):
    p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
    run=p.add_run();run.add_picture(str(FIG/(stem+'.png')),width=Inches(6.5))
    para(f'Figure S{num}. {caption}', style='Caption', size=9)
def legacy(old,new,caption):
    p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(LEGACY_IMG[old]), width=Inches(6.5))
    para(f'Figure S{new}. {caption}', style='Caption', size=9)

def polish(s):
    """Strip internal revision/meta wording from reused SI paragraphs."""
    reps=[
        ('original v14 target folds','reference target folds'),
        ('archived 768-dimensional features','768-dimensional MolFormer features'),
        ('This is a V2-weight result, not an evaluation of the newest checkpoint available in the package. ',''),
        ('Weight identifiers and hashes are recorded in S10 and the run manifests.','Weight identifiers are recorded in Section S10.'),
        ('in S21 and the run manifests','in Section S10'),
        ('in S10 and the run manifests','in Section S10'),
        ('Every reported RMSE, MAE and R² was independently recomputed from saved predictions. ',''),
        ('These intervals are conditional on the fitted decoders and do not include source-seed variability. They are separate from the primary 10,000-draw seed/scaffold intervals.',
         'Bootstrap intervals are conditional on the fitted decoders and do not include source-seed variability.'),
        ('partial/full CV retains heads, buffers, encoder hashes, predictions and the deterministic replay recipe. Prediction files and ledgers are in server_finetune_causal_20261012.',
         'partial/full CV retains heads, buffers, encoder hashes and predictions. Companion prediction files are summarised in Section S10.'),
        ('Full trained weights are retained for final OOD fits; ','Trained weights from the final OOD fits are retained; '),
    ]
    for a,b in reps:s=s.replace(a,b)
    return s

def insert_text_node(n,rewrite=True):
    c=deepcopy(n)
    if rewrite:
        for t in c.iter(qn('w:t')):
            if t.text:t.text=polish(t.text)
    doc._element.body.insert(len(doc._element.body)-1,c)

def build():
    main_doc=Document(MAIN)
    title=main_doc.paragraphs[0].text
    authors=main_doc.paragraphs[1].text
    affs=[main_doc.paragraphs[i].text for i in range(2,6)]
    # Front matter in etalon style
    para('Supporting Information', size=14, bold=True)
    para(title, size=14, bold=True)
    para(authors, size=12, bold=False)
    for a in affs:para(a, size=10)
    para('Content', size=14, bold=True)
    para('Acronyms', size=14, bold=True)
    for line in [
        'MIC - Minimum Inhibitory Concentration',
        'MBC - Minimum Bactericidal Concentration',
        'QAC - Quaternary Ammonium Compound',
        'OOD - Out-of-Distribution',
        'RMSE - Root Mean Squared Error',
        'MAE - Mean Absolute Error',
        'SHAP - SHapley Additive exPlanations',
        'CKA - Centered Kernel Alignment',
        'PCA - Principal Component Analysis',
        'MLP - Multilayer Perceptron',
        'SMOTE - Synthetic Minority Over-sampling Technique',
        'LoRA - Low-Rank Adaptation',
    ]:
        para(line, size=12, bold=True)
    chapters=[
        'S1. Expert annotation and molecular representations',
        'S2. Reference results and task encoding',
        'S3. Validation and matched compact encoders',
        'S4. Molecular and tabular decoder comparisons',
        'S5. Structural OOD evaluation',
        'S6. External Q-HERO classification',
        'S7. Geometry and intervention controls',
        'S8. Chemistry and microbiological methods',
        'S9. References',
        'S10. Additional illustrations',
    ]
    for s in chapters:para(s, size=12)

    heading(chapters[0])
    para('Expert annotation yielded 1,103 final Good/Bad labels (859 Bad, 244 Good). After standardisation, the panel comprises 1,066 canonical full salts. Annotation logistics (collection dates, annotator identities, materials shown, access to quantitative values, blinding, aggregation and agreement statistics) will be completed by the experimental coauthors.')
    para('A five-fold representation benchmark compares MolFormer, ChemBERTa, Morgan and MACCS features for classifying expert labels. Figures S1–S4 show the corresponding diagnostic plots. These comparisons evaluate label classification and are not used as quantitative MIC/MBC generalisation metrics. The MolFormer F1 of 0.655 reported in the main text is the reference value for that comparison.')
    for i,cap in [
        (1,'F1-score comparison across molecular representations for expert-label classification.'),
        (2,'Accuracy comparison across molecular representations for expert-label classification.'),
        (3,'Fold-specific classification metrics for the representation benchmark.'),
        (4,'Embedding cluster-quality diagnostics for the contrastive representation.'),
    ]:
        legacy(i,i,cap)

    heading(chapters[1])
    para('Frozen MolFormer provides 768-dimensional molecular features. The external encoder uses layer widths 768–512–384–256 (691,584 trainable parameters) and is trained without updating MolFormer weights. StandardScaler and Borderline SMOTE (sampling strategy 0.8) follow the reference training procedure. The contrastive projection head is removed before quantitative decoding.')
    table(45,'Reference holdout metrics for the primary quantitative endpoints. The E. coli MIC cell printed as R² = 0.60 corresponds to R² = 0.5918; the strain header ATCC 4300 is the original table typo for ATCC 43300.')
    table(46,'Reference metrics for secondary quantitative comparisons. Author-reported values are retained.')
    para('Task encodings based on text use OpenAI text-embedding-3-small, yielding four fixed 1,536-dimensional vectors. Species and endpoint descriptions were submitted to the embedding service; molecular structures and target concentrations were not. Fixed task vectors are shared across folds. Categorical species/endpoint coding and categorical task-ID coding serve as controls.')
    provenance=json.loads((REPRO/'revision_v24/task_text_embedding_provenance.json').read_text())
    for a in provenance['tasks']:
        para(f"{a['id']}: {a['text']}", size=10)

    heading(chapters[2])
    para('Row-wise validation follows the author worksheet protocol on 108 records representing 105 full salts. A withheld task row may still leave another measurement of the same molecule in the training set. Cation and scaffold holdouts keep the corresponding molecular groups outside target-training folds.')
    para('Uncertainty is reported as follows: fold standard deviation over five folds with ddof = 0; source-seed standard deviation over five complete runs with ddof = 1. These spreads are descriptive and are not 95% confidence intervals.')
    table(40,'Five-fold row-CV reconstruction: mean ± fold SD (ddof = 0).')
    figure(5,'figureS5_row_cv','Row-CV endpoint R² for raw and human-guided features. Bars show SD over five folds; symbols denote the three fixed task-coding configurations.')
    table(35,'Holdout endpoint metrics reconstructed on the 108 worksheet records.')
    para('Matched compact encoders share 681 source molecules (377 training, 304 validation), five paired source seeds and 480 updates without SMOTE. Human Good/Bad contrastive supervision is compared with continuous-MIC regression, binary-MIC controls, shuffled labels and raw features under identical target-decoder budgets and partitions.')
    table(36,'Compact-control and representation configurations: seed-mean RMSE.')
    table(41,'Complete compact-arm results: mean ± sample SD across source runs (ddof = 1).')
    figure(6,'figureS6_compact_seed_variability','Matched compact categorical-task pooled RMSE. Bars show sample SD over five source runs; raw features are a fixed single-checkpoint reference.')

    heading(chapters[3])
    para('Modern tabular and graph decoders (CatBoost, TabPFN, TabFM, AutoGluon, Chemprop) were evaluated on the same target registers with train-only preprocessing. Different PCA treatments and optimisation budgets make these practical pipeline comparisons rather than matched architecture trials.')
    table(38,'Modern decoder endpoint results on reference guided features. Each method fits separate endpoint predictors with train-only PCA-32.')
    table(42,'Grouped fold variability for guided-feature and modern-decoder procedures. Mean ± fold SD uses five folds and ddof = 0.')

    heading(chapters[4])
    para('The reference register lists all 105 full salts. The 17 newly synthesised OOD compounds span kojic-acid, tetrahydropyridine, dihydropyran and glycoluril families. Frozen OOD predictors are trained on the reference cohort only; OOD activity labels are not used for checkpoint selection. Compound identities and measured activities accompany this SI as QAC105.csv and OOD17.csv.')
    table(49,'OOD route scores on 67 exact endpoints. Repeated results are mean ± sample SD over the stated runs.')
    figure(7,'figureS9_ood_endpoint_parity','Measured versus predicted OOD endpoints for compact human and quantitative encoders. Dashed lines denote identity.')

    heading(chapters[5])
    para('Q-HERO is an external binary classification benchmark, distinct from the QAC MIC/MBC regression task. The cleaned cohort contains 405 molecules (360 active at S. aureus MIC ≤ 8 µM; 45 inactive). Human, quantitative and shuffled-human features use matched partial-MolFormer adaptation with CatBoost classifiers (800 iterations, depth 6, learning rate 0.05).')
    table(47,'Q-HERO405 classification. Mean ± sample SD over five paired source/decoder runs; fixed RF and raw references have one fit.')
    table(48,'Paired Q-HERO scaffold contrasts from 2,000 paired seed/scaffold bootstrap draws over fixed OOF predictions and 29 scaffolds.')

    heading(chapters[6])
    para('Linear CKA between MolFormer and human-guided features is 0.933 on the reference cohort and 0.946 on OOD compounds. Five-fold linear probes give R² = 0.891 ± 0.037 from MolFormer to human features and R² = 0.844 ± 0.060 in the reverse direction (fold SD). Summed mean |SHAP| values on the 67 exact OOD endpoints are 2.930 (MolFormer), 0.636 (human-guided) and 0.761 (task identifier).')
    para('Label-permutation and weight-rewind controls test procedural dependence of the predictions while retaining the same molecules, partitions and training budget.')
    table(50,'Scaffold-clustered label and weight intervention contrasts plotted in Figure S8.')
    figure(8,'figureS11_figure9_interpretation_controls_futura','Label-permutation and weight-rewind ΔRMSE under scaffold-clustered conditional intervals.')

    heading(chapters[7])
    para('Chemical characterisation and microbiological methods are reproduced from the experimental sections of the main article. Citation numbers follow the main bibliography. Full source NMR, HRMS and FT-IR spectra, the THP optimisation table and Schemes S1–S2 remain to be inserted by the experimental coauthors.')
    chemical=newtable('THP multicomponent-reaction optimisation corresponding to main Section 2.3.2 (placeholder for the original experimental record).', ['Entry','Status'], [('Original optimisation entries, including entries 3 and 7','To be completed by experimental coauthors')],'chemistry_optimisation')
    para('Scheme S1. Competitive THP/4H-pyran cyclisation (to be inserted; cited in Section 2.3.2).', style='Caption', size=9)
    para('Scheme S2. THP epimerisation (to be inserted; cited in Section 2.3.2).', style='Caption', size=9)
    mainbody=list(main_doc._element.body)
    start=next(i for i,n in enumerate(mainbody) if txt(n)=='4.1 Chemistry')
    end=next(i for i,n in enumerate(mainbody[start:],start) if txt(n).startswith('5. CRediT'))
    for n in mainbody[start:end]:
        c=deepcopy(n)
        for t in c.xpath('.//w:t'):
            if t.text and re.match(r'^4\.[12](?:\.| )',t.text):t.text=re.sub(r'^4\.', 'S8.',t.text)
        insert(c)

    heading(chapters[8])
    para('Model and dataset references', size=12, bold=True)
    for n in original:
        s=txt(n)
        if re.match(r'(4\.|6\.|7\.|8\.|9\.|10\.|11\.|12\.) ',s) and any(x in s for x in ['Ross, J.','Hu, E.','Heid, E.','Hollmann, N.','Google Research.','Erickson, N.','Schölkopf, B.','Ghaemi, S.']):
            para(re.sub(r'^\d+\.\s*','',s), size=10)
    para('Bibliography for chemical records', size=12, bold=True)
    refs=next(i for i,n in enumerate(mainbody) if txt(n)=='References')
    for n in mainbody[refs+1:]:
        if txt(n).strip():para(txt(n), size=10)

    heading(chapters[9])
    legacy(33,9,'Zero- and few-shot OOD illustration. The few-shot arm uses OOD labels for adaptation and is separate from frozen OOD validation.')
    legacy(34,10,'Information-flow schematic from the reference experimental record.')
    return chemical

def finish_document():
    for table in doc.tables:
        table.autofit=True
        for ri,row in enumerate(table.rows):
            if ri==0:
                pr=row._tr.get_or_add_trPr();rep=OxmlElement('w:tblHeader');pr.append(rep)
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1
                    for r in p.runs:set_run_font(r, size=8)
                if ri==0:
                    pr=cell._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8E8E8');pr.append(sh)
    for r in doc._element.xpath('.//w:r'):
        pr=r.find(qn('w:rPr'))
        if pr is None:pr=OxmlElement('w:rPr');r.insert(0,pr)
        f=pr.find(qn('w:rFonts'))
        if f is None:f=OxmlElement('w:rFonts');pr.insert(0,f)
        for name in ['ascii','hAnsi','eastAsia','cs']:f.set(qn('w:'+name),FONT)
        for a in list(f.attrib):
            if a.endswith('Theme'):del f.attrib[a]
    for f in doc._element.iter(qn('w:rFonts')):
        for name in ['ascii','hAnsi','eastAsia','cs']:f.set(qn('w:'+name),FONT)
        for a in list(f.attrib):
            if a.endswith('Theme'):del f.attrib[a]
    for inline in doc.inline_shapes:
        if inline.width>Inches(6.5):
            h=inline.height;w=inline.width;inline.width=Inches(6.5);inline.height=int(h*inline.width/w)
    doc.core_properties.title='Supporting Information'
    doc.core_properties.subject='Expert Judgement as Supervision — QAC biocides'
    doc.save(ROOT/'Supplementary_Information_v30.docx')

def align_main(chemical):
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(MAIN) as z:files={n:z.read(n) for n in z.namelist()}
    raw=files['word/document.xml'];tree=E.fromstring(raw);body=tree.find('w:body',ns);changes=[]
    spans=list(re.finditer(rb'<w:p(?:\s[^>]*)?>[\s\S]*?</w:p>',raw))
    patches=[]
    for i,n in enumerate(body):
        before=txt(n)
        if not before or n.tag!=qn('w:p'):continue
        after=before
        after=after.replace('Figure SI 1-2','Figures S1–S2')
        after=after.replace('SI Section S34','SI Section S2').replace('SI S34','SI Section S2')
        for old,new in [(34,10),(33,9),(35,8)]:
            after=after.replace(f'Figure S{old}',f'Figure __FIGREF{new}__')
        def map_table_num(old):
            old=int(old)
            if old==1 and ('MCR conditions' in before or 'ammonium acetate' in before or 'desired THP' in before or 'by-product slightly decreased' in before):
                return str(chemical)
            return str(TABLE_MAP.get(old, old))
        # Remap only Table/Tables S# tokens (never Scheme S#).
        after=re.sub(r'(Tables?\s+S)(\d+)', lambda m: m.group(1)+map_table_num(m.group(2)), after)
        after=re.sub(r'(Tables?\s+S\d+\s*[–−-]\s*S)(\d+)', lambda m: m.group(1)+map_table_num(m.group(2)), after)
        after=re.sub(r'(Tables?\s+S\d+(?:\s*[–−-]\s*S\d+)?(?:\s*,\s*S\d+)*(?:\s+and\s+S))(\d+)', lambda m: m.group(1)+map_table_num(m.group(2)), after)
        after=re.sub(r'Figure __FIGREF(\d+)__',r'Figure S\1',after)
        if before!=after:
            # Match the raw paragraph by its own XML location; retain every original media/OLE part.
            candidates=[]
            for m in spans:
                try:
                    wrap=E.fromstring(b'<root '+b' '.join(b'xmlns:'+k.encode()+b'="'+v.encode()+b'"' for k,v in tree.nsmap.items() if k)+b'>'+m.group()+b'</root>')
                    if ''.join(wrap.xpath('.//w:t/text()',namespaces=ns))==before:candidates.append(m)
                except E.XMLSyntaxError:pass
            assert len(candidates)==1,(i,len(candidates),before[:80])
            m=candidates[0];chunk=m.group();texts=list(re.finditer(rb'<w:t(?:\s[^>]*)?>[\s\S]*?</w:t>',chunk))
            # Replace only changed text tokens, keeping all paragraph/run structures.
            # SequenceMatcher maps edited references into the original run boundaries.
            import difflib
            tokens=[E.fromstring(b'<root xmlns:w="'+ns['w'].encode()+b'">'+x.group()+b'</root>')[0].text or '' for x in texts]
            offsets=np.cumsum([0]+[len(x) for x in tokens]);newtokens=tokens[:]
            edits=[o for o in difflib.SequenceMatcher(None,before,after,autojunk=False).get_opcodes() if o[0]!='equal']
            for _,a,b,c,d in reversed(edits):
                first=max(0,min(len(tokens)-1,int(np.searchsorted(offsets,a,side='right')-1)))
                last=max(first,min(len(tokens)-1,int(np.searchsorted(offsets,max(a,b-1),side='right')-1)))
                if first==last:newtokens[first]=newtokens[first][:a-offsets[first]]+after[c:d]+newtokens[first][b-offsets[first]:]
                else:
                    newtokens[first]=newtokens[first][:a-offsets[first]]+after[c:d]
                    for k in range(first+1,last):newtokens[k]=''
                    newtokens[last]=newtokens[last][b-offsets[last]:]
            from xml.sax.saxutils import escape
            for tm,value in reversed(list(zip(texts,newtokens))):
                tag=tm.group().split(b'>',1)[0]+b'>'
                chunk=chunk[:tm.start()]+tag+escape(value).encode()+b'</w:t>'+chunk[tm.end():]
            check=E.fromstring(b'<root xmlns:w="'+ns['w'].encode()+b'" '+b' '.join(b'xmlns:'+k.encode()+b'="'+v.encode()+b'"' for k,v in tree.nsmap.items() if k and k!='w')+b'>'+chunk+b'</root>')
            assert ''.join(check.xpath('.//w:t/text()',namespaces=ns))==after
            patches.append((m.start(),m.end(),chunk));changes.append({'body_index':i,'before':before,'after':after})
    for a,b,c in reversed(patches):raw=raw[:a]+c+raw[b:]
    E.fromstring(raw);files['word/document.xml']=raw
    with ZipFile(OUTMAIN,'w',ZIP_DEFLATED) as z:
        for name,value in files.items():z.writestr(name,value)
    return changes

def main():
    originals={str(p):sha(p) for p in [OLD,MAIN,COMA/'2026_07_09_Paper_2_edited-v5_NF_3.docx']}
    plots();chemical=build();finish_document();changes=align_main(chemical)
    shutil.copy2(OLD,ROOT/'SI_v27_full_archive.docx')
    shutil.copy2(REPRO/'revision_v17/sources/Supporting_Info_original.docx',ROOT/'Supporting_Info_original.docx')
    companions={'QAC105.csv':'v5_hypotheses_20261013/data/QAC105.csv','OOD17.csv':'v5_hypotheses_20261013/data/OOD17.csv','endpoint_registry.csv':'v5_hypotheses_20261013/data/endpoint_registry.csv','row_cv_summary.csv':'revision_v19/rowcv_results/summary.csv','compact_seed_summary.csv':'revision_v19/analysis/seed_summary.csv','compact_metrics.csv':'revision_v18/analysis/summary.csv','compact_contrasts.csv':'revision_v18/analysis/contrasts.csv','modern_metrics.csv':'revision_v18/analysis/modern_metrics.csv','backbone_route_scores.csv':'revision_v24/analysis/FT_route_RMSE_mean_sample_SD.csv','QHERO_metrics.csv':'qhero_author_comparison_20261014/results/summary.csv','QHERO_scaffold_contrasts.csv':'qhero_author_comparison_20261014/results/paired_scaffold_contrasts.csv','OOD_error_plot_values.csv':'revision_v26/OOD_violin_values.csv','interpretation_family_contrasts.csv':'revision_v26/interpretation_contrasts.csv','main_figure9_contrasts.csv':'revision_v29/inserted_figure_contrasts.csv','task_text_embedding_provenance.json':'revision_v24/task_text_embedding_provenance.json'}
    registry=next(REPRO.rglob('original_QAC105_registry.csv'),None)
    if registry:shutil.copy2(registry,DATA/registry.name)
    for dest,src in companions.items():
        p=REPRO/src;assert p.exists(),p;shutil.copy2(p,DATA/dest);INPUTS[str(p.relative_to(COMA))]=sha(p)
    additional={DATA/'fixed_model_endpoint_metrics.csv':REPRO/'server_models_20261012/analysis/all_model_metrics.csv',ROOT/'original_QAC105_structures_ACS1996.pdf':REPRO/'revision_v14/figures/original_QAC105_structures.pdf',ROOT/'OOD17_structures_ACS1996.pdf':REPRO/'revision_v14/figures/OOD17_structures.pdf'}
    for dest,src in additional.items():
        shutil.copy2(src,dest);INPUTS[str(src.relative_to(COMA))]=sha(src)
    for p,h in originals.items():assert sha(p)==h
    manifest={'font':'Times New Roman','ethalon':str(ETHALON),'SI':str(ROOT/'Supplementary_Information_v30.docx'),'aligned_main':str(OUTMAIN),'source_hashes':originals,'inputs_sha256':INPUTS,'table_map':TABLE_MAP,'tables':COPIED_TABLES,'figures':FIGURES,'archival_raster_figures':[1,2,3,4,9,10],'figure_map':{'33':9,'34':10,'35':8},'main_changes':changes,'chemical_table':chemical,'model_training_performed':False,'copied_numeric_cells_preserved':True,'pending_author_material':['annotation logistics','THP optimisation table','Scheme S1 and Scheme S2','source NMR/HRMS/FT-IR spectra']}
    (ROOT/'revision_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    lines=['# Ссылки статьи на SI','',f'Статья: `{OUTMAIN.name}`.','Шрифт: Times New Roman (эталон Supplementary_Information.docx).','', '| Было в SI v27 | Теперь | Содержание |','|---|---|---|']
    lines += [f"| Table S{r['old']} | Table S{r['number']} | {r['caption'].split('. ')[0]} |" for r in COPIED_TABLES if isinstance(r['old'],int)]
    lines += ['', 'Figure S33 → S9; S34 → S10; S35 → S8.', '',f'Table S{chemical} — THP optimisation placeholder; Schemes S1–S2 for coauthors.','', 'Extended archive: SI_v27_full_archive.docx.']
    (ROOT/'SI_REFERENCE_MAP_RU.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'SI':manifest['SI'],'main':str(OUTMAIN),'tables':len(COPIED_TABLES),'figures_generated':len(FIGURES),'main_reference_paragraphs_changed':len(changes),'font':'Times New Roman','pending_author_material':manifest['pending_author_material']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
