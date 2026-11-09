#!/usr/bin/env python3
"""Create submission-safe v8 manuscript and supporting-information deliverables.

This builder deliberately leaves v7 and the original HTML unchanged.  It works with
the standard library only, so that the resulting DOCX files retain the Word styles,
comments, references, and media supplied by the v7 template.
"""
from __future__ import annotations

import copy
import os
import re
import shutil
import struct
import tempfile
import zipfile
import xml.etree.ElementTree as ET


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
R = os.path.dirname(__file__)
SOURCE = os.path.join(ROOT, '2026_07_09_Paper_2_edited-v7_finetuning.docx')
MANUSCRIPT = os.path.join(ROOT, '2026_07_09_Paper_2_edited-v8_scientifically_revised.docx')
SI_HTML = os.path.join(R, 'Supplementary_Information_v8_scientifically_revised.html')
SI_DOCX = os.path.join(R, 'Supplementary_Information_v8_scientifically_revised.docx')

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
RNS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKGREL = 'http://schemas.openxmlformats.org/package/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS = {'w': W, 'r': RNS, 'wp': WP, 'a': A}
ET.register_namespace('w', W)
ET.register_namespace('r', RNS)
ET.register_namespace('wp', WP)
ET.register_namespace('a', A)


def ptext(p):
    return ''.join(t.text or '' for t in p.findall('.//w:t', NS)).strip()


def set_ptext(p, text):
    """Replace a paragraph's visible text while preserving its paragraph formatting."""
    ts = p.findall('.//w:t', NS)
    if not ts:
        run = ET.SubElement(p, f'{{{W}}}r')
        ts = [ET.SubElement(run, f'{{{W}}}t')]
    ts[0].text = text
    if text.startswith(' ') or text.endswith(' '):
        ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    for t in ts[1:]:
        t.text = ''
    # A paragraph replaced this way must not retain drawing/field objects.
    for el in list(p):
        if el.tag != f'{{{W}}}pPr' and el.find('.//w:t', NS) is None:
            p.remove(el)


def clone_text(template, text):
    q = copy.deepcopy(template)
    for el in list(q):
        if el.tag != f'{{{W}}}pPr':
            q.remove(el)
    run = ET.SubElement(q, f'{{{W}}}r')
    t = ET.SubElement(run, f'{{{W}}}t')
    t.text = text
    if text.startswith(' ') or text.endswith(' '):
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return q


def direct_paragraph(body, prefix):
    for el in list(body):
        if el.tag == f'{{{W}}}p' and ptext(el).startswith(prefix):
            return el
    raise ValueError(f'Direct paragraph starting with {prefix!r} not found')


def insert_before(root, ref, new):
    parents = {child: parent for parent in root.iter() for child in parent}
    parent = parents[ref]
    parent.insert(list(parent).index(ref), new)


def insert_after(root, ref, new):
    parents = {child: parent for parent in root.iter() for child in parent}
    parent = parents[ref]
    parent.insert(list(parent).index(ref) + 1, new)


def remove_figure_and_caption(root, caption_prefix):
    """Remove a main-text image paragraph immediately preceding its caption."""
    caption = find_para(root.findall('.//w:p', NS), caption_prefix)
    parents = {child: parent for parent in root.iter() for child in parent}
    parent = parents[caption]
    pos = list(parent).index(caption)
    if pos:
        previous = list(parent)[pos - 1]
        if previous.tag == f'{{{W}}}p' and previous.findall('.//*[@r:embed]', NS):
            parent.remove(previous)
    parent.remove(caption)


def set_table_rows(tbl, rows):
    """Turn a five-column template into a compact, auditable table."""
    tr = tbl.findall('./w:tr', NS)
    header, data = copy.deepcopy(tr[0]), copy.deepcopy(tr[1])
    for old in list(tbl.findall('./w:tr', NS)):
        tbl.remove(old)
    for row_no, values in enumerate(rows):
        row = copy.deepcopy(header if row_no == 0 else data)
        cells = row.findall('./w:tc', NS)
        if len(cells) != len(values):
            raise ValueError('five-column table template mismatch')
        for cell, value in zip(cells, values):
            p = cell.find('./w:p', NS)
            set_ptext(p, value)
        tbl.append(row)


def find_para(ps, prefix):
    for p in ps:
        if ptext(p).startswith(prefix):
            return p
    raise ValueError(f'Paragraph starting with {prefix!r} not found')


def manuscript_changes(root):
    ps = root.findall('.//w:p', NS)
    body = root.find('.//w:body', NS)
    # v7 had an empty abstract paragraph. Populate it with the bounded v8 summary.
    abstract = direct_paragraph(body, 'Abstract')
    abstract_slot = list(body)[list(body).index(abstract) + 1]
    set_ptext(abstract_slot, 'Binary expert annotations may offer an economical supervision signal for molecular representation learning, but their value must be assessed separately from quantitative prediction. We compared final Good/Bad expert labels with quantitative MIC supervision for quaternary ammonium compounds using a controlled partial-fine-tuning protocol. The MolFormer-XL embedding layer and four lower encoder layers remained frozen (16.0 of 44.4 M parameters), and all 532 evaluation molecules were removed from the fine-tuning sources. The resulting sources contained 740 expert-labelled molecules, 1,153 unique quantitative molecules, and 9,338 quantitative MIC records. After downstream refitting, mean Q-HERO R² was +0.269 for expert supervision and +0.312/+0.308 for molecule-level/record-level quantitative supervision; QAC-105 values remained close to zero. In direct transfer without target refitting, quantitative supervision gave stronger ranking on Q-HERO and OOD-17, while raw R² was negative. An affine recalibration fitted on the same target predictions is therefore exploratory only. The results support comparable representation quality under the evaluated downstream-refitting protocol, not equivalence of individual labels or calibrated zero-shot MIC prediction. Limitations include substantial overlap between supervision collections, unavailable individual expert votes, incomplete attribution provenance, and the small OOD-17 case study (n = 17).')
    keywords = find_para(ps, 'Cationic biocides;')
    set_ptext(keywords, 'Cationic biocides; quaternary ammonium compounds; expert supervision; molecular representation learning; partial fine-tuning; MIC; transfer learning; reproducibility audit')
    changes = {
        'Expert Judgement as Supervision: Binary Human Labels Match':
            'Expert Judgement as Supervision: Binary Human Labels Yield Comparable Molecular Representations under Downstream Refitting',
        'A distinct and older line of work treats human expertise':
            'A distinct and older line of work treats human expertise not as a constraint on the model but as a source of supervision in its own right. The intuition that experienced chemists possess a "gut feeling" for what constitutes a promising molecule has been formalised at least since QED, in which desirability functions were fitted to expert judgements of drug-likeness27. Such judgement is neither perfectly consistent nor bias-free, and its provenance must be recorded if annotator agreement is to be assessed. Recent work shows that human preference signals can be machine-learnable in molecular design. Here we examine a narrower, testable question: when the same chemical space is represented by binary expert labels and by quantitative MIC records, do the resulting molecular representations perform comparably after a downstream predictor is refitted? This is a controlled comparison, not a claim that a binary label is intrinsically equivalent to an individual measurement. The novelty wording in this paragraph requires a separate literature review before submission.',
        'The bottleneck in this domain, however, is not the choice of architecture':
            'The bottleneck in this domain is not only the choice of architecture but also the nature of the data. Bioactivity corpora assembled from the literature are small, sparse, and protocol-heterogeneous. Values pooled across laboratories can carry substantial experimental uncertainty, which limits the accuracy of any model trained on them37-39. We therefore investigate whether a coarse categorical signal, curated by domain experts, can yield a molecular representation comparable to one learned from pooled quantitative data under a clearly specified downstream protocol. This empirical question does not assume that categorical and quantitative labels are interchangeable.',
        'In our previous work, we established a baseline framework':
            'In our previous work, we established a baseline framework for predicting QAC antibacterial activity using MolFormer-derived embeddings. Building on that framework, the present work asks how the source of supervision affects a representation. We make three bounded contributions. First, we compare binary expert and quantitative MIC supervision on closely overlapping chemical collections, distinguishing 1,153 unique molecules from 9,338 quantitative records. Second, we evaluate partially fine-tuned representations by downstream refitting on QAC-105, Q-HERO, and a small OOD-17 set, while separating representation quality from direct zero-shot ranking. Third, we provide an audit trail for data overlap, split design, and model provenance. Claims of priority or novelty beyond this controlled comparison require external literature verification before submission.',
        'The encoder described below adapts a frozen foundation model':
            'The encoder described below adapts a frozen foundation model: MolFormer weights are held fixed and only a small contrastive head is trained on top. That configuration limits what either supervision source can express, because the head can only recombine features already computed by the frozen backbone. We therefore repeated the controlled comparison with partial fine-tuning of the upper backbone layers, while keeping the embedding layer and lowest four encoder layers frozen.',
        'MolFormer-XL was fine-tuned end-to-end on each supervision source':
            'MolFormer-XL was partially fine-tuned on each supervision source in turn: final expert "Good/Bad" annotations, quantitative MIC values aggregated to one value per molecule, and the full quantitative record collection. The embedding layer and the lowest four encoder layers remained frozen (16.0 of 44.4 M parameters); the remaining parameters were trainable. Training used a one-cycle schedule at a peak learning rate of 3e-5, with early stopping on a Bemis-Murcko-scaffold-disjoint validation split. Every molecule belonging to any evaluation set—the QAC-105 benchmark, Q-HERO, and the 17 newly synthesised compounds, 532 structures in total—was removed from all three fine-tuning sources. After this exclusion the sources contained 740 expert-labelled molecules, 1,153 unique quantitative molecules, and 9,338 quantitative MIC records. The expert and quantitative collections overlap substantially, so this is best interpreted as a controlled comparison of coarse and quantitative supervision on related chemical space. Results are averaged over three seeds and are reported against predict-the-mean and six-descriptor baselines.',
        'Fine-tuning changes the picture on every target':
            'Partial fine-tuning improves the mean R² over frozen MolFormer on all three targets in this experiment (Table 1), but the absolute results remain modest. On Q-HERO, mean R² rises from 0.134 for the frozen encoder to 0.269–0.312 after partial fine-tuning. On QAC-105 the values remain close to zero, and all OOD-17 values should be interpreted cautiously because n = 17. The descriptor baseline is positive on Q-HERO (R² = +0.057), so it is not correct to describe both baselines as non-positive throughout. These results support comparing supervision sources under the same protocol; they do not demonstrate high-accuracy absolute MIC prediction.',
        'Under this fairer setup the central comparison of this work survives':
            'Under this controlled setup, expert and quantitative supervision yield comparable downstream representation quality rather than demonstrably identical performance. The expert arm has mean R² = +0.053 on QAC-105 and +0.269 on Q-HERO; the molecule-level and record-level quantitative arms reach −0.004/+0.312 and +0.048/+0.308, respectively. The differences are small relative to the observed seed variation, but this study was not designed as a pre-specified non-inferiority trial. Accordingly, the supported claim is comparability under downstream refitting, not statistical equivalence of labels or a conversion rate between human calls and measurements.',
        'A second experiment asked what these models do when nothing at all is fitted on the target':
            'A second experiment evaluated direct transfer, with no refitting on the target. Quantitative heads output log2 MIC in micromolar units; the expert head outputs a Good/Bad score, so all arms are compared primarily by rank agreement and AUC after a target-specific median split. Quantitative supervision gives stronger direct ranking on Q-HERO and OOD-17 than expert supervision. The highest mean OOD-17 rank agreement (ρ = 0.75, AUC = 0.87) comes from the 9,338-record model, but the OOD estimate is based on only 17 compounds. The R² of the same direct predictions is negative, so direct transfer should not be interpreted as calibrated absolute MIC prediction.',
        'Refitting a single intercept and slope on each target resolves the contradiction':
            'For exploratory diagnosis only, we fit an intercept and slope on the same target predictions used for evaluation. This in-sample recalibration cannot test generalisation, but it illustrates the scale mismatch in direct quantitative transfer. For the 9,338-record model, the average in-sample recalibrated R² is 0.36 on Q-HERO and 0.49 on OOD-17, compared with raw values of −1.62 and −2.92. These fitted values should not be presented as externally validated calibration or as proof that calibration, rather than other factors, is the sole limitation. A nested or held-out target calibration protocol is required for that claim.',
        'One result deserves separate emphasis':
            'One result deserves separate emphasis. The partially fine-tuned expert model has never been shown a concentration, yet its direct score is positively associated with measured MIC ordering on the evaluated collections (mean rank agreement 0.22, 0.40, and 0.30 for QAC-105, Q-HERO, and OOD-17; AUC 0.64, 0.69, and 0.60). This is evidence that the final binary labels contain transferable potency-related signal; it does not establish quantitative MIC prediction.',
        'Two consequences follow for the sections that follow':
            'Two consequences follow for the sections that follow. First, frozen-encoder results are a lower-capacity reference, while the primary comparison is between supervision sources under the identical partially fine-tuned protocol. Second, direct predictions are best read as rankings, not as calibrated MIC estimates. Full fine-tuning, direct-transfer, and exploratory recalibration tables are supplied in the Supporting Information (Tables S2–S4; Figures S7–S9).',
        'Table 1. Variance explained on three evaluation sets by representations differing':
            'Table 1. Variance explained on three evaluation sets by representations differing in partial fine-tuning and supervision source, mean over three seeds. All 532 evaluation molecules were excluded from the fine-tuning sources. Downstream models are gradient-boosted regressors under scaffold-grouped cross-validation for QAC-105 and Q-HERO; OOD-17 is predicted from a model trained on QAC-105. OOD-17 contains 17 compounds.',
        'Expert guidance datasets were constructed through systematic literature exploration':
            'The expert-guidance dataset contains 1,103 final Good/Bad annotations. Repository artifacts retain the final label but not the individual annotator votes or adjudication records. The historical description of three independent experts and majority resolution therefore cannot be independently verified from the archived files, and inter-rater agreement cannot be calculated. We analyse the final labels as the available supervision signal. The class balance is 859 Bad and 244 Good; annotation-round drift and SMILES quality-control limitations are reported in the Supporting Information.',
        'To identify the optimal descriptor for downstream expert-guided learning':
            'For exploratory model selection, we benchmarked MolFormer, ChemBERTa, Morgan, and MACCS representations under a five-fold stratified protocol. MolFormer produced the highest archived mean F1-score (0.655 with an MLP and StandardScaler) and accuracy (0.856). Because the expert-label set is imbalanced, accuracy alone is not interpreted as a performance claim; the model-selection results are internal diagnostics and are not used as external validation in v8.',
        'Figure 2 presents t-SNE projections':
            'Figure 2 presents t-SNE projections (perplexity = 30) of a held-out fold before and after contrastive refinement. The internal clustering diagnostics changed from silhouette 0.007 to 0.108, Davies–Bouldin 6.54 to 2.58, and Calinski–Harabasz 3.60 to 22.08. These visual and internal diagnostics indicate separation of the final label classes within this analysis; they are not evidence of external antibacterial-prediction performance.',
        'A natural objection to using expert “Good/Bad” labels':
            'A natural objection to using expert Good/Bad labels is that a larger body of quantitative data should be preferable when it is available. The original in-domain comparison is retained as a descriptive analysis, but its absolute values are not used as primary evidence: QAC-105 molecules overlap the representation-training collections and the historical table combines outputs from different pipelines and split definitions. The externally held-out and controlled partial-fine-tuning results in Section 2.1 provide the principal current comparison.',
        'The quantitative values were compiled from the broad scale QAC data set':
            'The quantitative corpus used in the historical comparison was assembled from broad QAC activity records. Its record count must not be interpreted as the number of independent molecules: the fine-tuning subset used in Section 2.1 contains 9,338 MIC records over 1,153 unique molecules. The expert and quantitative collections have substantial molecule-level overlap, which makes their comparison controlled but not independent.',
        'While one-hot encoding is the simplest way to represent categorical information':
            'Historical analyses of one-hot and text-encoded task labels are not interpreted as a reproducible architecture comparison in v8 because the corresponding metrics were generated under incompatible pipelines and splits. They are retained only as exploratory context; the audited molecule-grouped representation comparison is Table 2.',
        'Figure 3. Correlation analysis of experimental versus predicted antimicrobial activities':
            'Figure 3. Historical correlation visualisation retained for context only. The embedded RMSE/R² annotations come from the original heterogeneous pipelines and are not used for comparative inference in v8; see the audited molecule-grouped Table 2 and Supporting Information for current evidence.',
        'Both embedding types were subsequently evaluated on the same set of QACs described above':
            'Both embedding types were subsequently evaluated on the same QAC collection. This retrospective in-domain result is consistent with similar downstream behaviour of the two supervision sources, but it is not a clean external validation. The molecule-level overlap and pair-level split inflate absolute performance, and raw MolFormer is also competitive under the audited re-run. We therefore do not use this table to claim that human annotations outperform or are statistically equivalent to quantitative measurements.',
        'We stress that this parity does not mean a binary label is informationally equivalent':
            'Similarity in one downstream protocol does not mean that a binary label is informationally equivalent to a quantitative measurement. A final expert call may reflect multiple activity reports and additional considerations, while pooled quantitative records contain repeated molecules and heterogeneous assay contexts. The appropriate conclusion is limited to comparable representation quality under the evaluated refitting protocol.',
        'To rigorously evaluate the generalization capability of the embeddings':
            'To examine out-of-domain behaviour, we assembled an OOD test set of 17 newly synthesized QACs from previously unrepresented structural subtypes and measured them under independent assay conditions. This set is chemically held out from the training collections, but n = 17 makes all effect estimates imprecise. It is therefore used as a small confirmatory case study rather than as decisive evidence of generalisation.',
        'To verify out-of-domain performance, we compared three representations':
            'For the OOD case study, we compared human embeddings, vanilla MolFormer features, and descriptor features. These comparisons are descriptive because the set contains 17 compounds and because several historical model branches have unresolved provenance. The results should be read alongside the external Q-HERO benchmark and the audited partial-fine-tuning matrix, not as a standalone generalisation claim.',
        'To further assess the adaptability of these molecular representations':
            'We also explored zero-shot and few-shot regimes. The historical few-shot scan is not used to support a comparative conclusion because one branch yields bit-identical values for all representations and the held-out test set changes with training fraction. A repaired, fixed-test protocol would be required before making a few-shot claim.',
        'For understanding how the resulting embeddings work':
            'For understanding how the resulting embeddings work, we use representational-similarity analyses and a matched encoder ablation as descriptive tools. The archived script that generated the published CKA/probing table and the provenance of the published SHAP summary are incomplete; SHAP is therefore not treated as independently reproducible causal evidence in this revision.',
        'Figure 6. Information flow in the contrastive encoder':
            'Figure 6. Conceptual information flow in the contrastive encoder. The diagram is an interpretation, not a quantitative decomposition: MolFormer supplies pretrained structural features and the final expert labels provide task-specific supervision.',
        'We first compare the two representations directly':
            'The archived CKA/probing table reports high alignment between MolFormer and the expert embedding (CKA 0.933 in-domain and 0.946 OOD; linear-probe R² 0.891 from MolFormer to embedding and 0.844 in reverse). These values suggest substantial preservation of the pretrained geometry. Because the generating script is absent, they are reported as archived descriptive results rather than independently regenerated evidence.',
        'Geometric similarity, however, does not reveal how a downstream model actually uses each representation':
            'Geometric similarity does not determine how a downstream model uses each representation. The archived SHAP summary has unresolved provenance: the available decomposition file reports a different aggregate embedding attribution from the manuscript, and it is not confirmed that the same encoder generated all analyses. We therefore omit numerical SHAP attribution as a basis for mechanistic or causal claims. A fully versioned pipeline is required before interpreting feature attributions.',
        'To isolate the role of the expert classification dataset':
            'A matched expert-versus-regression encoder ablation was run on the OOD case-study data. It suggests similar mean absolute residuals (expert − regression ΔRMSE = −0.086, 95% bootstrap CI [−0.227, +0.054]) and point estimates of 2.19 versus 2.27 log2 units. This interval includes no difference and is based on 17 compounds. It supports a cautious descriptive statement of no resolved advantage in this dataset; it does not establish statistical equivalence or identify a causal mechanism.',
        'The descriptive pattern supports this bound':
            'The descriptive pattern does not identify a robust subgroup advantage for either supervision source in the 17-compound case study. Any finer claim would require an a priori margin, a larger independent set, and a preregistered non-inferiority or equivalence protocol.',
        'Taken together, these analyses give a coherent picture':
            'Taken together, the archived analyses suggest that the expert embedding retains much of MolFormer geometry and that the two supervision sources can yield similar downstream behaviour. The current artifacts do not justify a causal decomposition of a biological component or a reproducible SHAP-based mechanism. We therefore treat these analyses as hypothesis-generating.',
        'In this work we studied how expert guidance and foundation-model representations':
            'In this work we examined whether final binary expert annotations and quantitative MIC supervision yield comparable molecular representations for QAC activity modelling. The evidence is strongest for a controlled partial-fine-tuning matrix with evaluation molecules excluded from every fine-tuning source, and for Q-HERO as the larger external benchmark. The 17-compound OOD collection is an informative but small case study.',
        'First, in the small-data regime that is typical of antimicrobial discovery':
            'First, under downstream refitting, representations partially fine-tuned on 740 final expert labels achieved results comparable to those from quantitative MIC supervision on the evaluated tasks. On Q-HERO, mean R² was +0.269 for expert supervision and +0.312/+0.308 for molecule-level/record-level quantitative supervision; on QAC-105 the values were near zero. This supports an efficiency hypothesis—coarse expert supervision can preserve useful representation-level signal—but it does not establish equivalence of individual labels or a universal label-to-record exchange rate. The 9,338-record corpus represents 1,153 unique molecules and substantially overlaps the expert collection.',
        'Second, embeddings trained on only 1,103 expert binary':
            'Second, the transfer protocol matters. Quantitative supervision was stronger for direct zero-shot ranking on Q-HERO and OOD-17, whereas expert supervision still supplied a positive potency-related rank signal without observing concentrations. Direct R² was negative for the quantitative models and the apparent improvement after affine recalibration was fitted on the same target predictions; it is exploratory rather than evidence of generalisable calibration. OOD-17 estimates require caution because n = 17.',
        'Third, our interpretability analysis indicates':
            'Third, archived representational analyses are consistent with substantial retention of the pretrained MolFormer geometry, but the SHAP and CKA provenance is incomplete. We therefore do not claim a quantified causal biological component. Future work should retain individual annotation votes, use molecule-grouped external splits, preregister a non-inferiority margin, and evaluate calibration on held-out target data. Priority claims about this supervision design also require an external literature review before submission.',
    }
    applied = []
    for prefix, text in changes.items():
        p = find_para(ps, prefix)
        set_ptext(p, text)
        applied.append(prefix)
    # Table labels must reflect partial, not end-to-end, fine-tuning.
    for p in ps:
        t = ptext(p)
        if t == 'MolFormer, fine-tuned':
            set_ptext(p, 'MolFormer, partially fine-tuned')
        elif t == '1153 MIC values':
            set_ptext(p, '1153 MIC values (molecules)')
        elif t == '9338 MIC values':
            set_ptext(p, '9338 MIC records (1153 molecules)')

    # Figures 3 and 5 contain historical non-comparable and known-bug outputs.
    # The surrounding limitation text is retained, but the visual evidence is removed.
    remove_figure_and_caption(root, 'Figure 3. Historical correlation')
    remove_figure_and_caption(root, 'Figure 5. Model performance transitioning')

    # Add an explicit computational-provenance section immediately before chemistry.
    chemistry = direct_paragraph(body, '4.1 Chemistry')
    idx = list(body).index(chemistry)
    htemplate = chemistry
    ntemplate = direct_paragraph(body, 'All starting reagents were obtained')
    additions = [
        clone_text(htemplate, '4.1 Computational protocol, provenance and limitations'),
        clone_text(ntemplate, 'Fine-tuning used MolFormer-XL with the embedding layer and lowest four encoder layers frozen (16.0 of 44.4 M parameters). Three random seeds were evaluated. All 532 evaluation structures were excluded from the fine-tuning sources. QAC-105 and Q-HERO downstream evaluations used scaffold-grouped five-fold cross-validation; OOD-17 was predicted after training on QAC-105. The quantitative training counts are reported both as 1,153 unique molecules and 9,338 records.'),
        clone_text(ntemplate, 'The final expert labels are archived, whereas individual votes and adjudication records are not; no inter-rater agreement is therefore reported. Expert and quantitative collections overlap substantially, so their comparison is controlled rather than independent. QAC-105 is in-domain and historically contaminated for representation learning; Q-HERO is the larger external benchmark, while OOD-17 (n = 17) is a small case study. Recalibration in this work is in-sample and exploratory. Archived CKA and SHAP summaries have incomplete pipeline provenance and are not used for causal claims. Detailed audit findings and file-level evidence are supplied in the Supporting Information.'),
    ]
    for off, p in enumerate(additions):
        body.insert(idx + off, p)

    # Repair the main Methods hierarchy after inserting computational methods.
    set_ptext(chemistry, '4.2 Chemistry')
    set_ptext(direct_paragraph(body, '4.1.1 General information'), '4.2.1 General information')
    set_ptext(direct_paragraph(body, '4.1.2 Synthesis and Characterization'), '4.2.2 Synthesis and Characterization of Substrates and Products')
    set_ptext(direct_paragraph(body, '4.2 Microbiological assay'), '4.3 Microbiological assay')
    set_ptext(direct_paragraph(body, '4.2.1 Bacterial strains'), '4.3.1 Bacterial strains')
    set_ptext(direct_paragraph(body, '4.2.2 Identification'), '4.3.2 Identification of microorganisms')
    set_ptext(direct_paragraph(body, '4.2.3 Cultivation'), '4.3.3 Cultivation of microorganisms')
    set_ptext(direct_paragraph(body, '4.2.4 MIC and MBC'), '4.3.4 MIC and MBC determination')

    # Static contents page: add the missing §2.1 and reflect the methods hierarchy.
    toc_22 = find_para(ps, '2.2 Training guidance NN models')
    insert_before(root, toc_22, clone_text(toc_22, '2.1 Frozen versus fine-tuned representations5'))
    set_ptext(find_para(ps, '4. Experimental protocol20'), '4. Experimental protocol and computational reproducibility20')
    toc_chem = find_para(ps, '4.1 Chemistry20')
    set_ptext(toc_chem, '4.1 Computational protocol, provenance and limitations20')
    insert_after(root, toc_chem, clone_text(toc_chem, '4.2 Chemistry21'))
    set_ptext(find_para(ps, '4.1.1 General information20'), '4.2.1 General information21')
    set_ptext(find_para(ps, '4.1.2 Synthesis'), '4.2.2 Synthesis and Characterization of Substrates and Products21')
    set_ptext(find_para(ps, '4.2 Microbiological assay30'), '4.3 Microbiological assay31')
    set_ptext(find_para(ps, '4.2.1 Bacterial strains30'), '4.3.1 Bacterial strains31')
    set_ptext(find_para(ps, '4.2.2 Identification'), '4.3.2 Identification of microorganisms31')
    set_ptext(find_para(ps, '4.2.3 Cultivation'), '4.3.3 Cultivation of microorganisms31')
    set_ptext(find_para(ps, '4.2.4 MIC and MBC'), '4.3.4 MIC and MBC determination31')

    # The historical architecture table has incompatible RMSE/R² values. Remove it
    # from the submission manuscript; the audit preserves its traceability. Replace
    # the central supervision table with audited molecule-grouped values including raw MolFormer.
    tables = root.findall('.//w:tbl', NS)
    h1_caption = find_para(ps, 'Table 1. Resulted metrics for prediction')
    h1_parent = next(par for par in root.iter() if h1_caption in list(par))
    h1_parent.remove(h1_caption)
    h1_table_parent = next(par for par in root.iter() if tables[1] in list(par))
    h1_table_parent.remove(tables[1])
    set_ptext(find_para(ps, 'Having obtained the embeddings, we next evaluated'), 'The original architecture comparison is omitted from v8 because its RMSE and R² entries combine different pipelines and split definitions. The audited supervision comparison is Table 2, which uses a molecule-grouped split and includes raw MolFormer as a reference.')
    set_ptext(find_para(ps, 'To clearly demonstrate the advantage of embeddings over descriptors'), 'Table 2 reports the audited molecule-grouped comparison on QAC-105. Under this conservative split, expert, quantitative, and raw MolFormer representations are within seed variation. This in-domain result is descriptive and should be read with the external Q-HERO and partial-fine-tuning analyses.')
    set_ptext(find_para(ps, 'Table 2. Resulted metrics for prediction of log2(MIC)'), 'Table 2. Audited QAC-105 molecule-grouped comparison: CatBoost R² (mean ± SD, 10 seeds). The same molecule is never present in both training and test. Values are reproduced from reproducibility/table2/table2_rebuild.csv; this table replaces the prior non-comparable central expert-versus-quantitative table.')
    audited = [
        ['Representation', 'S. aureus MIC', 'S. aureus MBC', 'E. coli MIC', 'E. coli MBC'],
        ['Raw MolFormer', '0.19 ± 0.19', '0.00 ± 0.30', '0.12 ± 0.19', '0.08 ± 0.22'],
        ['Expert (Good/Bad)', '0.27 ± 0.16', '0.06 ± 0.27', '0.09 ± 0.19', '0.06 ± 0.27'],
        ['Quantitative regression', '0.31 ± 0.13', '0.08 ± 0.22', '0.16 ± 0.22', '0.08 ± 0.26'],
    ]
    parent = next(par for par in root.iter() if tables[2] in list(par))
    replacement = copy.deepcopy(tables[0])
    set_table_rows(replacement, audited)
    parent.insert(list(parent).index(tables[2]), replacement)
    parent.remove(tables[2])
    return applied


def write_revised_manuscript():
    with zipfile.ZipFile(SOURCE) as zin:
        files = {n: zin.read(n) for n in zin.namelist()}
    root = ET.fromstring(files['word/document.xml'])
    applied = manuscript_changes(root)
    files['word/document.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(MANUSCRIPT, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    return applied


def revise_html():
    src = os.path.join(R, 'Supplementary_Information.html')
    with open(src, encoding='utf-8') as fh:
        h = fh.read()
    replacements = {
        '<title>Expert Supervision Supplement</title>': '<title>Supporting Information — scientific revision v8</title>',
        'was fine-tuned end-to-end on each source in turn.': 'was partially fine-tuned on each source in turn; the embedding layer and lowest four encoder layers remained frozen.',
        '9338 MIC values': '9338 MIC records (1153 unique molecules)',
        '9338 values': '9338 records',
        'both null baselines sit at or below zero.': 'the predict-the-mean baseline is non-positive, whereas the descriptor baseline is positive on Q-HERO (R² = +0.057).',
        'Every fine-tuned model beats the frozen encoder on every target, and both null baselines sit at or below zero. Absolute values remain low: Q-HERO is the only target on which any representation clears R² = 0.1.': 'Partial fine-tuning improves the mean result relative to frozen MolFormer on each target. The descriptor baseline is positive on Q-HERO (R² = +0.057), and Q-HERO is the only target on which any representation clears R² = 0.1.',
        'The equivalence between the two supervision sources': 'The comparison between the two supervision sources',
        'Out-of-domain equivalence of the two supervision sources': 'Out-of-domain comparison of the two supervision sources',
        'Equivalence is established at ±0.5 log₂ units and fails at ±0.25.': 'The historical TOST output is shown for transparency, but this revision does not claim equivalence because the case study has n = 17 and the margin was not pre-specified.',
        'equivalent</td>': 'exploratory</td>',
        'The equivalence conclusion of the main text is supported, and at a tighter margin than the one quoted': 'The historical equivalence analysis is retained for transparency but is treated as exploratory rather than as a conclusion of the main text',
        'The failure is calibration, not signal': 'Exploratory in-sample recalibration after direct transfer',
        'The model fine-tuned on 9338 literature MIC values': 'The model partially fine-tuned on 9338 literature MIC records (1153 molecules)',
        'rank agreement with the measured MIC is strong and grows with the amount of supervision, reaching ρ = 0.75 on the out-of-domain compounds for the model trained on 9338 values.': 'rank agreement is positive and is higher for quantitative than expert supervision on Q-HERO and OOD-17; the highest OOD-17 mean is ρ = 0.75 for the 9338-record model, but OOD-17 has n = 17.',
        'The coefficient of determination of those same predictions is negative on every target.': 'The coefficient of determination of the direct predictions is negative on every target, so these results should be read as ranking rather than calibrated absolute MIC prediction.',
        'Embeddings learned from 740 binary expert judgements\n      match those learned from 9338 quantitative measurements: the expert arm leads on QAC-105\n      (0.053 against 0.048), the quantitative arms lead on Q-HERO (0.312 against 0.269) and on the\n      out-of-domain set (−0.027 against −0.174), and no difference exceeds roughly one\n      standard deviation across seeds.': 'Embeddings learned from 740 binary expert judgements yield representation quality comparable to the quantitative arms under this downstream-refitting protocol. The expert arm leads on QAC-105 (0.053 against 0.048), whereas quantitative arms lead on Q-HERO (0.312 against 0.269) and OOD-17 (−0.027 against −0.174). These are descriptive seed-level comparisons, not a pre-specified equivalence test.',
        'Variance explained by each representation, mean ± sd over three seeds. Every fine-tuned model beats the frozen encoder on every target, and the predict-the-mean baseline is non-positive, whereas the descriptor baseline is positive on Q-HERO (R² = +0.057). Absolute values remain low: Q-HERO is the only target on which any representation clears R² = 0.1.': 'Variance explained by each representation, mean ± sd over three seeds. Partial fine-tuning improves the mean result relative to frozen MolFormer on each target; the predict-the-mean baseline is non-positive, whereas the descriptor baseline is positive on Q-HERO (R² = +0.057). Absolute values remain low: Q-HERO is the only target on which any representation clears R² = 0.1.',
        'Zero-shot transfer. <strong>Left:</strong> rank agreement with the measured MIC is strong and grows with the amount of supervision, reaching ρ = 0.75 on the out-of-domain compounds for the model trained on 9338 records. <strong>Right:</strong> the coefficient of determination of those same predictions is negative on every target.': 'Zero-shot transfer. <strong>Left:</strong> rank agreement is higher for quantitative than expert supervision on Q-HERO and OOD-17; the highest OOD-17 mean is ρ = 0.75 for the 9,338-record model, but OOD-17 has n = 17. <strong>Right:</strong> direct-prediction R² is negative on every target, so these results are rankings rather than calibrated MIC predictions.',
        'A model can rank well and still score R² = −2.9. Refitting a single affine map,\n      <em>a</em> + <em>b</em>&#183;prediction, on each target separates the two failures: two\n      parameters cannot create rank information, so whatever is recovered was already present in\n      the ordering and was lost to scale and offset alone.': 'A model can rank well and still score R² = −2.9. We fitted a single affine map, <em>a</em> + <em>b</em>&#183;prediction, on the same target predictions only as an exploratory diagnostic. Two parameters cannot create rank information, but this in-sample fit cannot establish generalisable calibration or isolate a single cause of error.',
        'Calibration of the model fine-tuned on 9338\n        MIC values, averaged over three seeds.': 'Exploratory in-sample affine recalibration of the model partially fine-tuned on 9,338 MIC records (1,153 molecules), averaged over three seeds.',
        'On the out-of-domain compounds the fitted slope is 0.98 — the scale is already correct —\n      and the whole error is an offset of +2.8 log₂ units, a seven-fold systematic\n      overestimate of MIC; recalibration lifts R² from −2.92 to +0.49. On Q-HERO the\n      slope is 0.47, so the model additionally compresses the range, and recalibration gives\n      +0.36 in place of −1.62. A model trained on literature MIC pooled across hundreds of\n      strains and dozens of protocols learns the correct ordering of compounds and the wrong\n      absolute scale for any single new assay. QAC-105 is the exception: rank agreement there is\n      weak (ρ ≈ 0.18) and recalibration recovers almost nothing, consistent with it\n      being the narrowest and most structurally homogeneous of the three sets.': 'The fitted slopes and offsets describe the observed in-sample scale mismatch: OOD-17 has mean slope 0.98 and offset about +3.0 log₂ units, whereas Q-HERO has mean slope 0.47 and offset about +2.1. In-sample R² consequently rises from −2.92 to +0.49 for OOD-17 and from −1.62 to +0.36 for Q-HERO. These values are not held-out calibration performance and must not be used to claim that the model has learned a generalisable assay-specific calibration. QAC-105 has weak rank agreement (ρ ≈ 0.18) and little in-sample recovery.',
    }
    for old, new in replacements.items():
        if old not in h:
            print(f'HTML warning: phrase not found: {old[:72]}')
        h = h.replace(old, new)
    banner = '''<div class="flag"><span class="flag-h">Scientific-revision note</span><br>
This v8 supplement distinguishes 1,153 unique quantitative molecules from 9,338 MIC records,
uses “partial fine-tuning” because 16.0 of 44.4 M parameters are frozen, and treats OOD-17
(n = 17), TOST/equivalence, SHAP provenance, and affine recalibration as limited or exploratory.
The central supported claim is comparable representation quality under downstream refitting;
quantitative supervision is stronger for direct zero-shot ranking.</div>'''
    h = h.replace('<main class="sheet">', '<main class="sheet">\n' + banner, 1)

    def inline_svg(relname):
        with open(os.path.join(R, 'figures', relname + '.svg'), encoding='utf-8') as fh:
            s = fh.read()
        s = s[s.index('<svg'):]
        s = re.sub(r'<svg([^>]*?)\swidth="[^"]*"', r'<svg\1', s, count=1)
        s = re.sub(r'<svg([^>]*?)\sheight="[^"]*"', r'<svg\1', s, count=1)
        return s.replace('<svg', '<svg preserveAspectRatio="xMidYMid meet"', 1)

    # Replace only v8 Figure S7–S9 plates; source assets are not altered.
    for section, fig_no, relname in [('s7', 'S7', 'v8/figS7_representation_quality_v8'),
                                     ('s8', 'S8', 'v8/figS8_zeroshot_v8')]:
        pattern = re.compile(rf'(<section id="{section}">.*?<div class="fig-plate">).*?(</div>\s*<figcaption><span class="fig-n">Figure {fig_no}\.)', re.S)
        h, n = pattern.subn(lambda m: m.group(1) + inline_svg(relname) + m.group(2), h, count=1)
        if n != 1:
            print(f'HTML warning: could not replace Figure {fig_no} plate')
    pattern = re.compile(r'(<h3>Where the error lives</h3>.*?<div class="fig-plate">).*?(</div>\s*<figcaption><span class="fig-n">Figure S9\.)', re.S)
    h, n = pattern.subn(lambda m: m.group(1) + inline_svg('v8/figS9_calibration_v8') + m.group(2), h, count=1)
    if n != 1:
        print('HTML warning: could not replace Figure S9 plate')
    with open(SI_HTML, 'w', encoding='utf-8') as fh:
        fh.write(h)


def png_size(path):
    with open(path, 'rb') as f:
        magic = f.read(24)
    if magic[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(path)
    return struct.unpack('>II', magic[16:24])


def build_si_docx():
    with zipfile.ZipFile(SOURCE) as zin:
        files = {n: zin.read(n) for n in zin.namelist()}
    doc = ET.fromstring(files['word/document.xml'])
    body = doc.find('.//w:body', NS)
    ps = doc.findall('.//w:p', NS)
    title_t = find_para(ps, 'Expert Judgement as Supervision:')
    head_t = find_para(ps, '2.1 Frozen versus fine-tuned representations')
    normal_t = find_para(ps, 'The encoder described below adapts')
    caption_t = find_para(ps, 'Figure 1.')
    drawing_t = next(p for p in ps if p.findall('.//*[@r:embed]', NS))
    table_t = doc.findall('.//w:tbl', NS)[0]
    sect = next(x for x in list(body) if x.tag == f'{{{W}}}sectPr')
    for child in list(body):
        if child is not sect:
            body.remove(child)
    content = [
        ('title', 'Supporting Information — Scientific Revision v8'),
        ('normal', 'Expert Judgement as Supervision: Binary Human Labels Yield Comparable Molecular Representations under Downstream Refitting'),
        ('heading', 'Scope and submission note'),
        ('normal', 'This supporting-information version accompanies the scientifically revised v8 manuscript. It preserves the available audit figures and source tables while distinguishing controlled comparisons from externally validated claims.'),
        ('normal', 'Key corrections: the model is partially fine-tuned (16.0 of 44.4 M parameters remain frozen); 9,338 quantitative MIC records correspond to 1,153 unique molecules; the descriptor baseline reaches R² = +0.057 on Q-HERO; OOD-17 contains 17 compounds; affine recalibration is in-sample and exploratory; and individual expert votes, full SHAP provenance, and a pre-specified equivalence protocol are unavailable.'),
        ('heading', 'S1. Dataset audit and annotation provenance'),
        ('normal', 'The expert archive contains 1,103 final labels (859 Bad, 244 Good). Individual votes and adjudication records are absent, so the historical three-expert majority-vote procedure cannot be independently verified and inter-rater agreement cannot be calculated. The expert and quantitative collections substantially overlap at molecule level. This produces a controlled comparison of coarse and quantitative supervision on related chemical space, not a comparison of independent datasets.'),
        ('normal', 'Table S1. Canonical-molecule overlap (from reproducibility/leakage_check.py).'),
        ('table', [
            ['Collection', 'Canonical molecules', '∩ expert', '∩ quantitative', 'Role in v8'],
            ['Expert final labels', '1,066', '1,066', '1,035', 'supervision source'],
            ['Quantitative corpus', '1,515', '1,035', '1,515', 'supervision source'],
            ['QAC-105', '105', '105', '99', 'in-domain / historical'],
            ['Q-HERO', '411', '222', '255', 'external benchmark'],
            ['OOD-17', '17', '0', '0', 'small case study'],
        ]),
        ('figure', 'figS1_expert_set', 'Figure S1. Expert-label audit: class balance and annotation-round drift. The final labels are the available supervision artifact; individual votes are not archived.'),
        ('figure', 'figS2_overlap', 'Figure S2. Molecule-level overlap. The overlap is a design feature for a controlled supervision comparison but limits claims of independent dataset superiority.'),
        ('heading', 'S2. Q-HERO external benchmark and residual distributions'),
        ('normal', 'Q-HERO provides 411 structures with a matched S. aureus MIC endpoint. The violin plot below is intentionally retained because it is visually clear and accurately shows near-identical residual distributions for expert, regression, and raw MolFormer representations. It does not show a decisive expert advantage.'),
        ('figure', 'figS3_qhero_violins', 'Figure S3. Distribution of absolute residuals on Q-HERO under scaffold-grouped five-fold CV. The three representations have near-identical distributions on the full collection and on the subset unseen by the expert encoder.'),
        ('figure', 'figS4_qhero_r2', 'Figure S4. Q-HERO benchmark results. Interpret representation differences with the reported seed variation and the controlled overlap design.'),
        ('heading', 'S3. Historical OOD comparison'),
        ('normal', 'The 17 newly synthesised compounds are structurally held out, but n = 17 limits precision. The matched-ablation result suggests no resolved mean residual advantage (expert − regression ΔRMSE = −0.086, 95% bootstrap CI [−0.227, +0.054]); it is not presented as a pre-specified statistical-equivalence result.'),
        ('figure', 'figS5_equivalence', 'Figure S5. Historical residual and TOST analysis, retained for transparency. In v8 it is exploratory because the sample is small and no equivalence margin was pre-specified.'),
        ('figure', 'figS6_split_effect', 'Figure S6. Split-design effect. Pair-level splitting can place the same molecule in train and test; molecule-grouped splits are required for conservative inference.'),
        ('heading', 'S4. Partial fine-tuning and downstream refitting'),
        ('normal', 'MolFormer-XL was partially fine-tuned: the embedding layer and four lower encoder layers remain frozen (16.0/44.4 M parameters). Evaluation molecules were excluded from all fine-tuning sources. Under downstream refitting, mean Q-HERO R² is +0.269 for 740 final expert labels, +0.312 for 1,153 molecule-level MIC values, and +0.308 for 9,338 MIC records. This supports comparable representation quality under this protocol, not equivalence of individual labels.'),
        ('normal', 'Table S2. Representation quality, mean ± SD across three seeds (from finetune/runs.jsonl).'),
        ('table', [
            ['Representation', 'QAC-105 R²', 'Q-HERO R²', 'OOD-17 R²', 'Protocol'],
            ['Predict-the-mean', '+0.000', '+0.000', '−0.058', 'null baseline'],
            ['6 descriptors', '−0.310', '+0.057', '−0.486', 'null baseline'],
            ['Frozen MolFormer', '−0.105 ± 0.03', '+0.134 ± 0.02', '−0.289 ± 0.09', 'no FT'],
            ['Partial FT expert', '+0.053 ± 0.09', '+0.269 ± 0.02', '−0.174 ± 0.19', '740 labels'],
            ['Partial FT quantitative', '−0.004 ± 0.04', '+0.312 ± 0.06', '−0.191 ± 0.21', '1,153 molecules'],
            ['Partial FT quantitative', '+0.048 ± 0.07', '+0.308 ± 0.03', '−0.027 ± 0.09', '9,338 records'],
        ]),
        ('figure', 'v8/figS7_representation_quality_v8', 'Figure S7. Downstream representation quality, mean ± SD over three seeds. This is partial—not end-to-end—fine-tuning. The descriptor baseline is positive on Q-HERO (R² = +0.057); absolute values remain modest.'),
        ('heading', 'S5. Direct zero-shot transfer and exploratory calibration'),
        ('normal', 'Without target refitting, quantitative supervision produces stronger rank agreement than expert supervision on Q-HERO and OOD-17, while raw R² remains negative. The highest OOD-17 mean rank agreement is ρ = 0.75 for the 9,338-record model; this estimate has n = 17. Expert scores still carry positive potency-related rank signal despite never observing concentrations.'),
        ('normal', 'Table S3. Direct-transfer rank agreement and AUC, means across three seeds (from finetune/runs_direct.jsonl).'),
        ('table', [
            ['Source', 'QAC-105 ρ / AUC', 'Q-HERO ρ / AUC', 'OOD-17 ρ / AUC', 'Interpretation'],
            ['Expert (740 labels)', '+0.221 / 0.644', '+0.397 / 0.688', '+0.295 / 0.597', 'rank signal only'],
            ['Quant. 1,153 molecules', '+0.210 / 0.652', '+0.547 / 0.780', '+0.619 / 0.852', 'stronger ranking'],
            ['Quant. 9,338 records', '+0.176 / 0.630', '+0.612 / 0.814', '+0.752 / 0.866', 'strongest; OOD n=17'],
        ]),
        ('figure', 'v8/figS8_zeroshot_v8', 'Figure S8. Direct zero-shot transfer. These predictions are best interpreted as rankings, not calibrated absolute MIC estimates.'),
        ('normal', 'Affine recalibration was fitted and evaluated on the same target predictions. It is included only as an exploratory diagnostic of scale mismatch; it does not demonstrate generalisable target calibration.'),
        ('normal', 'Table S4. Exploratory in-sample affine recalibration (from finetune/recalibration.csv).'),
        ('table', [
            ['Target', 'Raw R²', 'In-sample affine R²', 'Mean slope', 'Mean offset log₂'],
            ['QAC-105', '−0.83', '+0.03', '0.23', '+1.20'],
            ['Q-HERO', '−1.62', '+0.36', '0.47', '+2.11'],
            ['OOD-17', '−2.92', '+0.49', '0.98', '+3.01'],
        ]),
        ('figure', 'v8/figS9_calibration_v8', 'Figure S9. Exploratory in-sample affine recalibration. A held-out or nested target-calibration protocol is required before reporting calibrated generalisation.'),
        ('heading', 'S6. Reproducibility inventory and limitations'),
        ('normal', 'Primary artifacts: reproducibility/finetune/runs.jsonl (partial-fine-tuning matrix), runs_direct.jsonl (direct transfer), recalibration.csv (exploratory recalibration), qhero/qhero_metrics.csv and qhero_residuals.csv (Q-HERO), analysis/ablation_bootstrap.csv (matched OOD ablation), and FINDINGS.md (audit). CKA/probing and SHAP summary provenance is incomplete, so they are not used for causal or mechanistic claims in v8.'),
    ]
    fig_specs = []
    for kind, *vals in content:
        if kind == 'title': body.insert(len(body)-1, clone_text(title_t, vals[0]))
        elif kind == 'heading': body.insert(len(body)-1, clone_text(head_t, vals[0]))
        elif kind == 'normal': body.insert(len(body)-1, clone_text(normal_t, vals[0]))
        elif kind == 'figure': fig_specs.append(vals)
        elif kind == 'table': pass
    relroot = ET.fromstring(files['word/_rels/document.xml.rels'])
    image_type = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
    # Interleave figure drawings and captions at their marked positions after adding core text.
    # A second pass builds a new body in the intended sequence for figures.
    for child in list(body):
        if child is not sect:
            body.remove(child)
    relid = 100
    fig_no = 0
    for kind, *vals in content:
        if kind == 'title': body.insert(len(body)-1, clone_text(title_t, vals[0]))
        elif kind == 'heading': body.insert(len(body)-1, clone_text(head_t, vals[0]))
        elif kind == 'normal': body.insert(len(body)-1, clone_text(normal_t, vals[0]))
        elif kind == 'table':
            tbl = copy.deepcopy(table_t)
            set_table_rows(tbl, vals[0])
            body.insert(len(body)-1, tbl)
        elif kind == 'figure':
            name, cap = vals
            fig_no += 1
            rel = f'rId{relid}'; relid += 1
            src = os.path.join(R, 'figures', name + '.png')
            target = f'media/{name}.png'
            files['word/' + target] = open(src, 'rb').read()
            ET.SubElement(relroot, f'{{{PKGREL}}}Relationship', {'Id': rel, 'Type': image_type, 'Target': target})
            draw = copy.deepcopy(drawing_t)
            embed = draw.find('.//*[@r:embed]', NS)
            embed.set(f'{{{RNS}}}embed', rel)
            w_px, h_px = png_size(src)
            cx = 5660000
            cy = int(cx * h_px / w_px)
            for ex in draw.findall('.//wp:extent', NS): ex.set('cx', str(cx)); ex.set('cy', str(cy))
            for ex in draw.findall('.//a:ext', NS): ex.set('cx', str(cx)); ex.set('cy', str(cy))
            for dp in draw.findall('.//wp:docPr', NS): dp.set('id', str(100 + fig_no)); dp.set('name', f'Supplementary Figure S{fig_no}')
            body.insert(len(body)-1, draw)
            body.insert(len(body)-1, clone_text(caption_t, cap))
    files['word/document.xml'] = ET.tostring(doc, encoding='utf-8', xml_declaration=True)
    files['word/_rels/document.xml.rels'] = ET.tostring(relroot, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(SI_DOCX, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)


def main():
    applied = write_revised_manuscript()
    revise_html()
    build_si_docx()
    print(f'created {MANUSCRIPT}')
    print(f'created {SI_HTML}')
    print(f'created {SI_DOCX}')
    print(f'manuscript replacements: {len(applied)}')


if __name__ == '__main__':
    main()
