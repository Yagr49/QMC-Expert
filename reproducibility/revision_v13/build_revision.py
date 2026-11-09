"""Bring original QAC-105 and named OOD-17 evidence into the main article.

Preserve v12 native paragraphs, author fields, references and existing figures.
Append a cohort registry and per-molecule OOD evidence to the complete v12 SI.
"""
from pathlib import Path
import copy, importlib.util, json, re
import pandas as pd

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'revision_v12'
COMA=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('v11_doc',ROOT.parent/'revision_v11/build_revision.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
h,W,NS=d.h,d.W,d.NS
MAIN=COMA/'2026_10_11_Paper_2_edited-v13_QAC_and_OOD.docx'


def mean_sd(row,field,sd):
    return f'{row[field]:.3f} ± {row[sd]:.3f}' if row.seeds==5 else f'{row[field]:.3f}'


def prepare():
    summary=pd.read_csv(OLD/'analysis/summary.csv')
    direct=pd.read_csv(OLD/'analysis/direct_summary.csv')
    qac=pd.read_csv(ROOT/'data/original_QAC105_registry.csv')
    ood=pd.read_csv(ROOT/'data/OOD17_named_registry.csv')
    validation=json.loads((ROOT/'cohort_validation.json').read_text())
    files,tree,body=d.read_doc(OLD/'Supplementary_Information_v12.docx')
    nodes=list(body)
    caption=next(i for i,p in enumerate(nodes) if h.text(p).startswith('Table S9. Audited QAC-105 molecule-grouped'))
    original_table=next(t for t in nodes[caption+1:] if t.tag=='{'+W+'}tbl')
    history=[[h.text(c) for c in r.findall('w:tc',NS)] for r in original_table.findall('w:tr',NS)]
    assert history[0]==['Representation','S. aureus MIC','S. aureus MBC','E. coli MIC','E. coli MBC']
    assert history[2][1]=='0.27 ± 0.16' and history[3][1]=='0.31 ± 0.13'

    replacements={}
    draft=(OLD/'main_draft.md').read_text()
    def replace_paragraph(prefix,new):
        old=next(b for b in draft.split('\n\n') if b.startswith(prefix))
        replacements[old]=new
    intro=next(b for b in draft.split('\n\n') if b.startswith('We examine these questions'))
    replacements[intro]=intro.replace('Q-HERO is the principal external chemical collection;',
        'The original 105-structure QAC collection provides the initial antibacterial benchmark, retained alongside the fixed 17-compound OOD case study. Q-HERO is the larger external chemical collection;')
    replace_paragraph('The archived partial-fine-tuning protocol removes',
        'The original QAC benchmark comprises 105 unique full-salt structures from 108 source rows. All 105 structures and all four antibacterial endpoints remain in the archived analyses. The archived partial-fine-tuning protocol removes all 532 evaluation full-salt identities from each supervision source and evaluates QAC-105, Q-HERO-411 and the same 17 newly synthesised QACs. Full-salt identity exclusion does not establish exclusion of every counterion variant. The matched protocols additionally exclude evaluation cation identities and their counterion variants, and remove conflicting expert and target labels. QAC-104 is the original cohort after excluding one conflicting duplicate structure, target_25e7bff606cb (source row IDs 75 and 76), with S. aureus MIC values of 0.25 and 0.50 mg/L and conflicting S. aureus/E. coli MBC values. The original rows and historical aggregate are preserved in Supporting Information Section S19; no best-performing subset is selected. The other matched targets are Q-HERO-405 and OOD-17. Q-HERO-405 contains 386 unique cations in 29 cation-scaffold groups. Cohort sizes and exclusion rules differ across protocols, so their scores are not pooled into a single comparison.')
    replace_paragraph('For representation-quality evaluation, a fresh target regressor',
        'For representation-quality evaluation, a fresh target regressor is trained using five-fold scaffold-grouped cross-validation on QAC or Q-HERO; each reported prediction is held out of its target-regressor training fold. QAC-104 contains 102 cations in 29 cation-scaffold groups. Q-HERO is external to representation training, while its fold-training MIC values are used for downstream refitting. Source–target scaffold overlap is allowed in these CV collections; grouping applies to the source-validation partition and target-regressor folds separately. Direct transfer applies the source-trained head without target refitting. For OOD-17, the downstream MIC decoder is trained on all QAC-104 targets and receives no OOD outcomes. The same source heads are also applied directly without QAC or OOD refitting. The 17 fixed compounds have four cation-Murcko scaffold groups, all absent from both the matched 681-molecule source panel and QAC-104 under the archived scaffold definition; exact cation overlap is also zero. This is a structural extrapolation case study, not an independently prospective validation. Compound codes, measured MIC, structures and individual predictions are supplied in Section S19; synthesis, characterisation and microbiological protocols remain in Section S16.')
    negative=next(b for b in draft.split('\n\n') if b.startswith('Secondary-target accuracy remains limited:'))
    replacements[negative]='The original QAC benchmark and named OOD compounds are examined explicitly in Section 3.7, including limited absolute MIC accuracy and the distinction between direct ranking and regression.'
    abstract=next(b for b in draft.split('\n\n') if b.startswith('Human Good/Bad annotations may provide'))
    replacements[abstract]=abstract.replace('reveal dependence on supervision assignment, adaptation procedure and source composition.',
        'reveal dependence on supervision assignment, adaptation procedure and source composition; the retained original QAC cohort and fixed OOD compounds show limited absolute MIC prediction.')
    conclusion=next(b for b in draft.split('\n\n') if b.startswith('On identical source molecules, the matched partial-fine-tuning extension'))
    replacements[conclusion]=conclusion+' The original 105-structure QAC benchmark remains visible as an archived in-domain comparison; strict QAC-104 and fixed OOD-17 regression yield negative mean R², while positive OOD direct ranking remains a small-cohort descriptive result.'
    for old,new in replacements.items():
        assert draft.count(old)==1
        draft=draft.replace(old,new)

    rows=[['Target / source','Seeds','RMSE (log2 µM)','R²','Direct rank agreement']]
    for target in ['QAC-104','OOD-17']:
        for arm,label in [('raw-molformer','Raw'),('expert','Human'),('quant-continuous','Continuous MIC'),('quant-binary','Binary MIC')]:
            s=summary[(summary.target==target)&(summary.arm==arm)].iloc[0]
            dr=direct[(direct.target==target)&(direct.arm==arm)]
            rows.append([target+' / '+label,int(s.seeds),mean_sd(s,'RMSE','RMSE_sd'),mean_sd(s,'R2','R2_sd'),
                         mean_sd(dr.iloc[0],'rank_agreement','rank_sd') if len(dr) else '—'])

    section='''### 3.7. Original QAC benchmark and compound-resolved OOD transfer

The original 105-structure collection remains an explicit antibacterial benchmark, covering S. aureus MIC/MBC and E. coli MIC/MBC. In the archived molecule-grouped, ten-seed comparison, human representations give S. aureus MIC R² = 0.27 ± 0.16, versus 0.31 ± 0.13 for quantitative representations and 0.19 ± 0.19 for raw MolFormer (Table 5). This historical contrastive-encoder branch allows overlap with representation-training sources and differs from the matched partial-fine-tuning protocol. Its observed proximity is descriptive; it establishes neither external performance nor equivalence of human labels and measurements. Complete identities, endpoints and the single strict-protocol exclusion are traceable in Section S19.

[TABLE:original]

Table 5. Original QAC-105 antibacterial benchmark, retained from the audited historical comparison in Supporting Information Table S9. CatBoost R² is mean ± seed SD over ten seeds with molecule-grouped target folds. Representation-training source overlap remains a limitation. The historical architecture, source exclusions and target partitions differ from the strict matched experiments; the results cannot be pooled with Table 6.

Under the stricter matched partial-fine-tuning protocol, the same original chemistry after the documented conflict exclusion gives QAC-104 human mean R² = −0.103 and continuous-MIC R² = −0.034 (Table 6; Figure 6). For the fixed OOD-17 set, the QAC-trained decoder gives human RMSE 1.731 log2 µM and R² = −0.118, versus continuous-MIC RMSE 1.741 and R² = −0.122, and raw RMSE 1.698 and R² = −0.067. Every trained arm has negative mean R² on both collections. These absolute MIC results limit the generality of the positive Q-HERO supervision-assignment result.

[TABLE:secondary]

Table 6. Strict matched partial-fine-tuning results on the original QAC collection after curation (QAC-104) and the fixed OOD-17 compounds. QAC regression uses five-fold cation-scaffold CV; OOD regression uses a decoder fitted on QAC-104 only. Direct rank agreement uses the source head with no target fitting. Trained arms show mean ± source-seed SD over five seeds; raw is a single fixed run. Logits from binary source heads are not MIC predictions. All shuffled controls are retained in Supporting Information Tables S11–S12; the human shuffled control is also shown in Figure 6.

Direct source-only OOD ranking is more encouraging: human rank agreement is 0.667 ± 0.120, versus 0.399 ± 0.192 for continuous MIC and 0.588 ± 0.136 for binary MIC. The human-minus-continuous rank contrast is +0.268 [−0.167, +0.590], and human minus shuffled human is +0.452 [−0.100, +0.981], using the existing paired seed/scaffold intervals. Both intervals include zero. With 17 compounds in four scaffold groups, these point estimates describe potency-related ordering without establishing superiority, calibrated MIC prediction or prospective discovery success. Figures S19–S20 identify every compound and show where decoder predictions fail; all individual predictions and source-head scores are retained.

[FIGURE:cohorts]

Figure 6. Original QAC and fixed OOD evaluations under matched partial fine-tuning. (a,b) MIC regression on QAC-104 scaffold folds and OOD-17 using the QAC-trained decoder. (c,d) Direct source-head rank agreement on the same collections with no target fitting. Circles are individual seeds and diamonds with bars are mean ± seed SD; raw has one run. Human shuffled controls are shown; continuous and binary shuffled controls remain in Supporting Information. No OOD outcomes are used in model fitting. Ranking and absolute concentration accuracy are separate outcomes.

'''
    draft=draft.replace('## 4. Conclusions',section+'## 4. Conclusions',1)
    (ROOT/'main_draft.md').write_text(draft)
    return replacements,section,{'original':history,'secondary':rows},validation


def main():
    replacements,section,tables,validation=prepare()
    files,tree,body=d.read_doc(COMA/'2026_10_11_Paper_2_edited-v12_matched_finetuning.docx')
    normal=next(p for p in body if h.text(p).startswith('Supervision for molecular learning'))
    template=next(t for t in body.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
    for old,new in replacements.items():
        matches=[p for p in body if h.text(p)==old]
        assert len(matches)==1,old[:80]
        h.replace(matches[0],new)
    anchor=next(p for p in body if h.text(p)=='4. Conclusions')
    position=list(body).index(anchor)
    added=[]
    for block in section.strip().split('\n\n'):
        if block.startswith('### '):added.append(d.paragraph(normal,block[4:],2))
        elif block.startswith('[TABLE:'):added.append(h.table(template,tables[block[7:-1]]))
        elif block.startswith('[FIGURE:'):added.append(d.embed(files,ROOT/'figures/figure6_original_QAC_and_OOD.png','rIdV13Cohorts'))
        else:added.append(d.paragraph(normal,block))
    for i,node in enumerate(added):body.insert(position+i,node)
    d.unique_ids(tree);h.write(files,tree,MAIN)
    d.exports(files,tree,ROOT/'manuscript_v13_readable.md',ROOT/'manuscript_v13.html')
    build_si(normal,validation)
    print(MAIN)


def build_si(normal,validation):
    files,tree,body=d.read_doc(OLD/'Supplementary_Information_v12.docx')
    section=body.find('w:sectPr',NS)
    template=next(t for t in body.findall('w:tbl',NS) if len(t.find('w:tr',NS).findall('w:tc',NS))==5)
    def append(node):body.insert(list(body).index(section),node)
    def add(text,level=None):append(d.paragraph(normal,text,level))
    add('S19. Original QAC registry and fixed named OOD compounds',1)
    add('This section exposes the previously evaluated original QAC cohort and fixed OOD-17 set; it does not introduce new training or select favourable compounds. The computational v12 predictions and checkpoints remain unchanged. Registry generation, identity joins, metric reproduction and molecule-resolved displays are documented in reproducibility/revision_v13/analyse_cohorts.py and cohort_validation.json. Numerical evidence for the original in-domain comparison remains in Table S9; strict matched fine-tuning evidence remains in Tables S11–S15.')
    add('S19.1. Complete original QAC-105 registry and curation trace',2)
    add('The original Data_biocides.xlsx contains 108 rows that collapse to 105 canonical full-salt structures. The prepared historical table keeps the median of duplicate endpoint entries and reported molecular weights. The strict matched evaluation excludes target_25e7bff606cb, representing original zero-based row IDs 75 and 76. These two rows report S. aureus MIC 0.25/0.50 mg/L, S. aureus MBC 2.0/0.5 mg/L, E. coli MBC 8.0/2.0 mg/L and reported salt molecular weights 756.7/812.8. The conflicting original rows are exported unchanged in data/QAC_excluded_duplicate_records.csv. The historical aggregate is preserved in the complete original registry, while its MIC value is not used in QAC-104 fitting or metrics. No other original structure is lost: QAC-104 equals the other 104 canonical salts exactly.')
    add('Table S16. All 105 original QAC structures and their strict-protocol inclusion status. Source row IDs are the zero-based identifiers stored in the original spreadsheet, not synthesised compound numbers. Historical MIC values are retained in µM; conflicting duplicate medians are descriptive. Complete original endpoint fields, full-salt/cation SMILES, source identifiers and strict target folds are in data/original_QAC105_registry.csv. The matching complete structure atlas is figures/original_QAC105_structures.pdf (nine pages) and .svg.')
    original=pd.read_csv(ROOT/'data/original_QAC105_registry.csv')
    rows=[['Original row IDs','Stable compound ID','MIC (mg/L)','Historical MIC (µM)','Matched QAC-104']]
    for r in original.itertuples():rows.append([r.original_row_ids,r.compound_id,f'{r.sa_mic_mg_l:g}',f'{r.sa_mic_um:.4g}',
                                              'Retained' if r.included_in_matched_QAC104 else 'Excluded: conflict'])
    append(h.table(template,rows))
    add('S19.2. Fixed OOD-17 identities, endpoint conversion and chemical novelty',2)
    add('Original codes are recovered from Veresh_paper/QACs_SMILES_MIC_MBC.xlsx by an exact canonical full-salt identity join: IT505, IT502, IT499; DA253, PDD13, PDD14, PDD11; IT442, IT469, IT452, IT493, IT380; and SEV-0338, SEV-035, SEV-036, SEV-030, SEV-033. These groups contain 3, 4, 5 and 5 structures with cation charges +1, +2, +2 and +4, respectively. Every source-sheet S. aureus MIC is an exact positive numeric value. The archived conversion is MIC (µM) = 1000 × MIC (mg/L) / RDKit full-salt molecular weight, followed by log2. Recalculation reproduces every archived OOD target to within 10−12 log2 units. Codes are preserved exactly, including SEV-0338; no inferred renaming is applied.')
    add('All 17 cation identities and all four cation-Murcko scaffolds are absent from both the matched 681-molecule source panel (training plus validation) and QAC-104. The unchanged OOD set therefore supplies structural extrapolation under this particular scaffold definition. This does not imply chemical dissimilarity under every representation or independent prospective selection. data/OOD17_named_registry.csv records the exact cation and scaffold exclusions and descriptive nearest-neighbour Morgan fingerprints (radius two, 2048 bits; Tanimoto) against QAC-104, the 377 source-training molecules and all 681 source molecules. These similarities do not redefine the OOD set or establish a mechanism.')
    add('Table S17. Compound-resolved OOD MIC predictions from decoders fitted only on QAC-104. Concentrations are µM. For trained arms, predicted concentration is 2 raised to the mean predicted log2 MIC across five seeds (a geometric mean, not an arithmetic concentration mean). Raw has one run. Per-seed predictions, binary/shuffled arms, log-scale errors and source-seed SD are retained in analysis/OOD17_per_molecule.csv and OOD17_predictions_all_seeds.csv. Seed SD describes training variation, not biological replicates or predictive confidence intervals.')
    ood=pd.read_csv(ROOT/'analysis/OOD17_per_molecule.csv')
    rows=[['Compound','Measured MIC','Human predicted MIC','Continuous predicted MIC','Raw predicted MIC']]
    for r in ood.to_dict('records'):
        rows.append([r['code'],f"{r['measured_MIC_uM']:.4g}",
                     f"{r['expert_geometric_predicted_MIC_uM']:.4g}",
                     f"{r['quant-continuous_geometric_predicted_MIC_uM']:.4g}",
                     f"{r['raw-molformer_geometric_predicted_MIC_uM']:.4g}"])
    append(h.table(template,rows))
    append(d.embed(files,ROOT/'figures/figureS19_OOD17_per_molecule.png','rIdV13S19'))
    add('Figure S19. Fixed named OOD-17 molecules. (a) Measured log2 MIC and per-compound decoder predictions after fitting on QAC-104, with source-seed SD for trained arms. (b) Measured log2 MIC versus direct human source-head logits averaged over the five seeds, with horizontal source-seed SD and the four scaffold groups. Larger human logits denote Good; they are not predicted concentrations. The captioned rank statistic is the mean of the five seed-specific correlations, not the correlation of the displayed mean-score vector. These plots distinguish ranking signal from poor absolute MIC accuracy. OOD outcomes enter only descriptive evaluation.')
    for i,name in enumerate(validation['OOD_atlas_pngs']):
        append(d.embed(files,ROOT/'figures'/name,'rIdV13S20'+str(i)))
    add('Figure S20. Exact salt structures for all 17 fixed OOD compounds, with their original codes, cation-scaffold group, charge and measured S. aureus MIC in mg/L and µM. Three continuation panels retain all compounds. Structure rendering preserves the archived SMILES and does not add stereochemical assignments. Standalone PDF and vector SVG are provided as figures/figureS20_OOD17_structures.pdf and .svg; synthesis and characterisation descriptions remain in Section S16.')
    add('S19.3. Per-molecule prediction records and numerical checks',2)
    add('analysis/QAC104_predictions_all_seeds.csv joins every QAC-104 held-out prediction to its original source-row IDs, stable identifier and target fold. analysis/OOD17_predictions_all_seeds.csv retains every QAC-trained-decoder OOD prediction for the six trained arms and raw reference. analysis/OOD17_direct_scores_all_seeds.csv records every direct source-head score with its units: binary logits must not be interpreted as MIC, while continuous scores are source-only log2 µM predictions. All five seeds are present for every molecule and trained arm; raw has one run. Every original molecule-target value and every secondary-cohort seed-mean RMSE, R² and direct rank statistic is independently reproduced from the archived predictions with discrepancy below 10−12. Input hashes are recorded in cohort_validation.json; no original prediction or checkpoint file is replaced.')
    d.unique_ids(tree);h.write(files,tree,ROOT/'Supplementary_Information_v13.docx')
    d.exports(files,tree,ROOT/'supplement_v13_readable.md',ROOT/'Supplementary_Information_v13.html')


if __name__=='__main__':main()
