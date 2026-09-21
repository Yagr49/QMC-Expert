"""Insert a new section 2.1 reporting the fine-tuning experiments, renumber what
follows, and renumber Tables 1-2 to 2-3."""
import re, os, shutil, zipfile, sys

SRC = '/Users/egorilin/Desktop/COMA/2026_07_09_Paper_2_edited-v6_corrected.docx'
DST = '/Users/egorilin/Desktop/COMA/2026_07_09_Paper_2_edited-v7_finetuning.docx'
WORK = '/private/tmp/claude-501/-Users-egorilin-Desktop-COMA/990d2f42-4236-4501-b9e0-fecccb0c4e55/scratchpad/v6/_w'

shutil.rmtree(WORK, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)
XML = f'{WORK}/word/document.xml'
d = open(XML, encoding='utf-8').read()

E = '<w:lang w:val="en-US"/>'


def body(text, first_indent=True):
    """A normal body paragraph matching the document's running style."""
    ind = '<w:ind w:firstLine="709"/>' if first_indent else ''
    runs = ''
    for chunk, bold, ital in text:
        rpr = '<w:rPr>' + ('<w:b/>' if bold else '') + ('<w:i/>' if ital else '') + E + '</w:rPr>'
        c = (chunk.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        runs += f'<w:r>{rpr}<w:t xml:space="preserve">{c}</w:t></w:r>'
    return (f'<w:p><w:pPr><w:spacing w:line="276" w:lineRule="auto"/>'
            f'<w:jc w:val="both"/>{ind}<w:rPr>{E}</w:rPr></w:pPr>{runs}</w:p>')


def p(text):
    return body([(text, False, False)])


def heading(text):
    return ('<w:p><w:pPr><w:pStyle w:val="2"/><w:ind w:firstLine="284"/>'
            '<w:rPr><w:i/><w:color w:val="auto"/><w:sz w:val="28"/><w:szCs w:val="28"/>'
            f'{E}</w:rPr></w:pPr><w:r><w:rPr><w:i/><w:color w:val="auto"/>'
            f'<w:sz w:val="28"/><w:szCs w:val="28"/>{E}</w:rPr>'
            f'<w:t>{text}</w:t></w:r></w:p>')


def caption(rest):
    """Table caption using the same SEQ field as the existing captions, so Word
    renumbers every table in document order when fields are updated."""
    RP = f'<w:rPr><w:b/><w:bCs/><w:sz w:val="20"/><w:szCs w:val="20"/>{E}</w:rPr>'
    RPn = f'<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/>{E}</w:rPr>'
    seq = (f'<w:r>{RP}<w:t xml:space="preserve">Table </w:t></w:r>'
           f'<w:r>{RP}<w:fldChar w:fldCharType="begin"/></w:r>'
           f'<w:r>{RP}<w:instrText xml:space="preserve"> SEQ Table \\* ARABIC </w:instrText></w:r>'
           f'<w:r>{RP}<w:fldChar w:fldCharType="separate"/></w:r>'
           f'<w:r>{RP}<w:t>1</w:t></w:r>'
           f'<w:r>{RP}<w:fldChar w:fldCharType="end"/></w:r>'
           f'<w:r>{RP}<w:t xml:space="preserve">. </w:t></w:r>')
    r = f'<w:r>{RPn}<w:t xml:space="preserve">{rest}</w:t></w:r>'
    return ('<w:p><w:pPr><w:spacing w:line="276" w:lineRule="auto"/><w:jc w:val="center"/>'
            f'<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:pPr>{seq}{r}</w:p>')


# ---------------------------------------------------------------- table
def cell(text, w, bold=False, span=None, align='center'):
    gs = f'<w:gridSpan w:val="{span}"/>' if span else ''
    rpr = '<w:rPr>' + ('<w:b/><w:bCs/>' if bold else '') + '<w:sz w:val="18"/><w:szCs w:val="18"/>' + E + '</w:rPr>'
    t = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{gs}<w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:line="276" w:lineRule="auto"/><w:jc w:val="{align}"/>'
            f'<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:pPr>'
            f'<w:r>{rpr}<w:t xml:space="preserve">{t}</w:t></w:r></w:p></w:tc>')


W = [3000, 1573, 1573, 1573, 1574]
ROWS = [
    (['Representation', 'Supervision', 'QAC-105', 'Q-HERO', 'OOD-17'], True),
    (['predict-the-mean', 'none', '0.000', '0.000', '-0.058'], False),
    (['descriptors', 'none', '-0.310', '+0.057', '-0.486'], False),
    (['MolFormer, frozen', 'none', '-0.105', '+0.134', '-0.289'], False),
    (['MolFormer, fine-tuned', '740 expert binary', '+0.053', '+0.269', '-0.174'], False),
    (['MolFormer, fine-tuned', '1153 MIC values', '-0.004', '+0.312', '-0.191'], False),
    (['MolFormer, fine-tuned', '9338 MIC values', '+0.048', '+0.308', '-0.027'], False),
]
rows = ''
for vals, bold in ROWS:
    tcs = ''.join(cell(v, w, bold, align='left' if i < 2 else 'center')
                  for i, (v, w) in enumerate(zip(vals, W)))
    rows += f'<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>{tcs}</w:tr>'
grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in W)
TABLE = ('<w:tbl><w:tblPr><w:tblStyle w:val="ad"/><w:tblW w:w="9293" w:type="dxa"/>'
         '<w:jc w:val="center"/><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0"'
         ' w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
         f'<w:tblGrid>{grid}</w:tblGrid>{rows}</w:tbl>')

# ---------------------------------------------------------------- prose
SEC = heading('2.1 Frozen versus fine-tuned representations')

SEC += p(
    'The encoder described below adapts a frozen foundation model: MolFormer weights are held '
    'fixed and only a small contrastive head is trained on top. That design keeps the experiment '
    'cheap, but it also caps what any supervision signal can express, because the head can only '
    'recombine features the frozen backbone already computes. Before comparing supervision '
    'sources through such a bottleneck, we therefore asked whether the bottleneck itself is '
    'what limits them, and repeated the comparison with the backbone free to move.')

SEC += p(
    'MolFormer-XL was fine-tuned end-to-end on each supervision source in turn: the expert '
    '"Good/Bad" annotations, the quantitative MIC values aggregated to one value per molecule, '
    'and the full set of quantitative records. The embeddings and the lowest four encoder layers '
    'were kept frozen (16.0 of 44.4 M parameters), training used a one-cycle schedule at a peak '
    'learning rate of 3e-5, and early stopping was on a validation split disjoint by Bemis-Murcko '
    'scaffold. Critically, every molecule belonging to any evaluation set - the in-domain QAC '
    'benchmark, the external Q-HERO collection and the 17 newly synthesised compounds, 532 '
    'structures in total - was removed from all three training sources, so that no representation '
    'had seen a test compound under any form of supervision. This leaves 740 expert-annotated '
    'molecules against 9338 quantitative measurements, a 12.6-fold difference. Results are '
    'averaged over three seeds and reported against two null baselines: predicting the training '
    'mean, and a six-descriptor model.')

SEC += p(
    'Fine-tuning changes the picture on every target (Table 1). On the external Q-HERO benchmark '
    'the variance explained rises from 0.134 for the frozen encoder to 0.27-0.31 once the '
    'backbone is trained, roughly a two-fold gain; on the in-domain benchmark it moves from '
    '-0.105 to approximately +0.05, and on the out-of-domain compounds from -0.289 to -0.027. '
    'Both null baselines sit at or below zero throughout. The frozen configuration was therefore '
    'suppressing what the supervision contributed, and comparisons made through it understate '
    'every source equally.')

SEC += p(
    'Under this fairer setup the central comparison of this work survives. Embeddings learned '
    'from 740 binary expert judgements match those learned from 9338 quantitative measurements: '
    'the expert arm leads on the in-domain benchmark (0.053 against 0.048), the quantitative arms '
    'lead on Q-HERO (0.312 against 0.269) and on the out-of-domain set (-0.027 against -0.174), '
    'and no difference exceeds roughly one standard deviation across seeds. A coarse human call '
    'is worth about as much as an order of magnitude more measured activity, now with every test '
    'compound held out and with null baselines stated.')

SEC += p(
    'A second experiment asked what these models do when nothing at all is fitted on the target: '
    'the fine-tuned head predicts the evaluation sets directly. Because the quantitative sources '
    'and all three targets are expressed as log2 MIC in micromolar units, this transfer is well '
    'defined; the expert head emits a "Good/Bad" score instead, so both arms are compared on rank '
    'agreement with the measured MIC and on the area under the ROC curve against MIC split at each '
    'target\'s median. The outcome separates two things that the coefficient of determination '
    'conflates. Rank agreement is strong and grows with the amount of supervision, reaching a '
    'Spearman coefficient of 0.75 and an AUC of 0.87 on the out-of-domain compounds for the model '
    'trained on all 9338 values. The coefficient of determination of those same predictions is '
    '-2.9.')

SEC += p(
    'Refitting a single intercept and slope on each target resolves the contradiction. Two '
    'parameters cannot create rank information, so whatever is recovered was already present in '
    'the ordering. On the out-of-domain compounds the fitted slope is 0.98 - the scale is already '
    'correct - and the whole error is an offset of +2.8 log2 units, a seven-fold systematic '
    'overestimate of MIC; recalibration lifts the coefficient of determination from -2.92 to '
    '+0.49. On Q-HERO the slope is 0.47, so the model additionally compresses the range, and '
    'recalibration gives +0.36 in place of -1.62. A model trained on literature MIC values pooled '
    'across hundreds of strains and dozens of protocols thus learns the correct ordering of '
    'compounds together with the wrong absolute scale for any single new assay. This is the '
    'predicted consequence of protocol heterogeneity stated in the Introduction, observed here as '
    'a measurement rather than assumed as a motivation.')

SEC += p(
    'One result deserves separate emphasis. The model fine-tuned only on "Good/Bad" annotations '
    'has never been shown a concentration, yet it ranks unseen compounds by their measured MIC '
    'with Spearman coefficients of 0.22, 0.40 and 0.30 on the three evaluation sets, at AUC 0.64, '
    '0.69 and 0.60 against a chance value of 0.50. Binary expert judgement carries information '
    'about quantitative potency that survives transfer to independently measured compounds.')

SEC += p(
    'Two consequences follow for the sections that follow. First, the frozen-encoder results '
    'reported there are a lower bound on what each supervision source can deliver, and the '
    'comparison between sources is the informative part rather than the absolute values. Second, '
    'on independently measured data these models are best read as rankers rather than as '
    'predictors of absolute MIC, and are reported accordingly. Full tables, per-seed values and '
    'the calibration analysis are given in the Supporting Information (Figures S7-S9, Tables '
    'S1-S4).')

SEC += caption('Variance explained on three evaluation sets by representations differing in whether '
               'the MolFormer backbone was fine-tuned and in the supervision used, mean over three '
               'seeds. All 532 evaluation molecules were held out of every training source. '
               'Downstream models are gradient-boosted regressors under scaffold-grouped '
               'cross-validation for QAC-105 and Q-HERO; the out-of-domain compounds are predicted '
               'from a model trained on QAC-105.')
SEC += TABLE
SEC += '<w:p><w:pPr><w:spacing w:line="276" w:lineRule="auto"/></w:pPr></w:p>'

# ---------------------------------------------------------------- splice in
paras = [(m.start(), m.end()) for m in re.finditer(r'<w:p[ >].*?</w:p>', d, re.S)]
target = None
for a, b in paras:
    seg = d[a:b]
    t = re.sub(r'<[^>]+>', '', ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', seg, re.S)))
    if t.strip() == '2.1 Training guidance NN models' and 'PAGEREF' not in seg:
        target = a; break
assert target, 'anchor paragraph not found'
d = d[:target] + SEC + d[target:]
print('inserted new section 2.1')

# ---------------------------------------------------------------- renumber


def swap(old, new, expect=1, label=''):
    global d
    n = d.count(old)
    if n != expect:
        print(f'  !! {label}: found {n}, expected {expect}: {old!r}')
    d = d.replace(old, new)
    print(f'  ok {label}: {old!r} -> {new!r} x{n}')


# headings, deepest first so prefixes do not collide
for a, b in [('2.4 Understanding the new embeddings', '2.5 Understanding the new embeddings'),
             ('2.3.5 Out-of-domain performance verification', '2.4.5 Out-of-domain performance verification'),
             ('2.3.4 Glycoluril-based multi-QACs', '2.4.4 Glycoluril-based multi-QACs'),
             ('2.3.3 Dihydropyran-based mono-QACs', '2.4.3 Dihydropyran-based mono-QACs'),
             ('2.3.2 Tetrahydropyridine-based bis-QACs', '2.4.2 Tetrahydropyridine-based bis-QACs'),
             ('2.3.1 Kojic acid-based bis-QACs', '2.4.1 Kojic acid-based bis-QACs'),
             ('2.3 Out of domain inference', '2.4 Out of domain inference'),
             ('2.2 Training on QACs', '2.3 Training on QACs'),
             ('2.1 Training guidance NN models', '2.2 Training guidance NN models')]:
    swap(a, b, expect=d.count(a), label='heading')

# in-text references in the pre-existing sections shift by one.
# Do Table 2 -> 3 first so the Table 1 -> 2 pass cannot cascade into it.
print('\nin-text table references:')
swap('behind them (Table 2)', 'behind them (Table 3)', 1, 'ref 2->3')
swap('As summarized in Table 1', 'As summarized in Table 2', 1, 'ref 1->2')
swap('As shown in Table 1 (Multitask Catboost)', 'As shown in Table 2 (Multitask Catboost)', 1, 'ref 1->2')
swap('As Table 1 shows (Multitask MLP)', 'As Table 2 shows (Multitask MLP)', 1, 'ref 1->2')

open(XML, 'w', encoding='utf-8').write(d)

# ---------------------------------------------------------------- repackage
if os.path.exists(DST):
    os.remove(DST)
zf = zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED)
for root, _, files in os.walk(WORK):
    for f in files:
        fp = os.path.join(root, f)
        zf.write(fp, os.path.relpath(fp, WORK))
zf.close()
print('\nwrote', DST, os.path.getsize(DST), 'bytes')
