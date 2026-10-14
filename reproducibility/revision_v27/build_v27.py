"""Manuscript v27 from v26.

Structure
  * 2.2 split into 2.2.1 (reference QAC cohort) and 2.2.2 (generalisation beyond it).
    2.2.2 gathers Q-HERO and the 17 new compounds, so the out-of-domain results sit next to
    the supervision comparison they test; 2.3.5 is dissolved into it.
  * 2.3 becomes the synthesis section for the 17 new compounds (2.3.1-2.3.4 unchanged).

Figures
  * v26 Figures 5 (design) and 6 (violins) -> one Figure 5: pipeline with embedded violins.
    Explanatory text lives in the caption, not under the figure.
  * Renumbered 7->6 (Q-HERO), 8->7 (compound classes), 9->8 (OOD errors) in captions and text.
  * The Figure 7 caption used a SEQ field while every other figure caption is literal text;
    a field refresh would have renumbered it to 1. It is made literal like the others.

Text
  * cross-references updated; Cyrillic homoglyphs and typos fixed; Scheme 4 says multi-QACs.
  * SI: six references to main-text figure/section numbers updated.
"""
from pathlib import Path
import copy, re, shutil, zipfile, sys
from lxml import etree

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parent.parent
SRC = COMA / '2026_10_14_Paper_2_edited-v26_OOD_and_interpretation.docx'
DST = COMA / '2026_10_14_Paper_2_edited-v27_section2_restructured.docx'
SI_SRC = ROOT.parent / 'revision_v26' / 'Supplementary_Information_v26.docx'
SI_DST = ROOT / 'Supplementary_Information_v27.docx'
FIG5 = ROOT / 'figures' / 'figure5_matched_supervision_pipeline.png'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
q = lambda ns, t: f'{{{ns}}}{t}'
LOG = []


def log(msg):
    LOG.append(msg); print(msg)


def ptext(el):
    return ''.join(t.text or '' for t in el.iter(q(W, 't')))


# ------------------------------------------------------------------ run-aware replace
def replace_in(el, old, new, required=True, label=''):
    """Replace `old` by `new` across the w:t nodes of one paragraph, keeping run formatting."""
    ts = list(el.iter(q(W, 't')))
    flat = ''.join(t.text or '' for t in ts)
    i = flat.find(old)
    if i < 0:
        if required:
            raise SystemExit(f'not found [{label}]: {old!r}')
        return False
    pos, spans = 0, []
    for t in ts:
        n = len(t.text or ''); spans.append((pos, pos + n)); pos += n
    j = i + len(old)
    first = True
    for t, (a, b) in zip(ts, spans):
        if b <= i or a >= j:
            continue
        s = t.text or ''
        pre, post = s[:max(0, i - a)], s[max(0, j - a):] if j < b else ''
        t.text = pre + (new if first else '') + post
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        first = False
    log(f'  edit [{label}] {old[:56]!r} -> {new[:56]!r}')
    return True


def set_text(p, text):
    """Replace a paragraph's text, keeping the formatting of its first text run."""
    runs = [r for r in p.iter(q(W, 'r')) if r.find(q(W, 't')) is not None]
    keep = runs[0]
    for r in runs[1:]:
        r.getparent().remove(r)
    t = keep.find(q(W, 't')); t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def strip_bookmarks(p):
    for tag in ('bookmarkStart', 'bookmarkEnd'):
        for b in list(p.iter(q(W, tag))):
            b.getparent().remove(b)


def strip_fields(p):
    """Turn a simple field into its displayed literal text."""
    for tag in ('fldChar', 'instrText', 'fldSimple'):
        for e in list(p.iter(q(W, tag))):
            r = e.getparent()
            if tag == 'fldSimple':
                idx = r.index(e)
                for k, ch in enumerate(list(e)):
                    r.insert(idx + k, ch)
                r.remove(e)
            else:
                r.remove(e)


def find(children, prefix, start=0, exact=False):
    for k in range(start, len(children)):
        t = ptext(children[k]).strip()
        if (t == prefix) if exact else t.startswith(prefix):
            return k
    raise SystemExit(f'anchor not found: {prefix!r}')


def is_heading(el):
    ps = el.find(f'{q(W, "pPr")}/{q(W, "pStyle")}')
    return ps is not None and ps.get(q(W, 'val')) in ('1', '2', '3') and 'PAGEREF' not in etree.tostring(el, encoding=str)


# ------------------------------------------------------------------ main manuscript
work = ROOT / '_v27'
shutil.rmtree(work, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(work)
doc_path = work / 'word' / 'document.xml'
rels_path = work / 'word' / '_rels' / 'document.xml.rels'
tree = etree.parse(str(doc_path)); root = tree.getroot()
body = root.find(q(W, 'body'))
rels = etree.parse(str(rels_path)); rroot = rels.getroot()
ch = lambda: list(body)

log('== structure')
# heading template: an existing level-3 heading in Results
tmpl = ch()[find(ch(), '2.3.1 Kojic acid-based bis-QACs', exact=True)]


def new_heading(text):
    h = copy.deepcopy(tmpl); strip_bookmarks(h); set_text(h, text); return h


k = find(ch(), 'Having obtained the embeddings, we next evaluated them')
body.insert(k, new_heading('2.2.1 Prediction on the reference QAC cohort'))
log('  + 2.2.1 Prediction on the reference QAC cohort')
k = find(ch(), 'We additionally tested transfer of source-trained representations')
body.insert(k, new_heading('2.2.2 Generalisation beyond the reference cohort'))
log('  + 2.2.2 Generalisation beyond the reference cohort')

# block A: description of the 17 new compounds and Figure 8 (compound classes)
a0 = find(ch(), 'To evaluate prediction beyond the reference chemical families')
a1 = find(ch(), 'Figure 8. Molecular classes represented', a0)
blockA = ch()[a0:a1 + 1]
# block B: everything under 2.3.5 up to the 2.4 heading
h235 = find(ch(), '2.3.5 Out-of-domain performance verification', exact=True)
h24 = find(ch(), '2.4 Understanding the new embeddings', h235, exact=True)
blockB = ch()[h235 + 1:h24]
body.remove(ch()[h235]); log('  - heading 2.3.5 (content moved to 2.2.2)')
anchor = ch()[find(ch(), 'Figure 7. ROC curves for Q-HERO')]
for el in blockA + blockB:
    body.remove(el)
pos = list(body).index(anchor) + 1
for k, el in enumerate(blockA + blockB):
    body.insert(pos + k, el)
log(f'  moved {len(blockA)} + {len(blockB)} blocks into 2.2.2 after the Q-HERO figure')

h23 = ch()[find(ch(), '2.3 Out of domain inference', exact=True)]
set_text(h23, '2.3 Design and synthesis of the new QACs')
log('  2.3 renamed: Design and synthesis of the new QACs')

log('== figures')
# Figure 5: point its relationship at the new image and fix the aspect ratio
rel5 = next(r for r in rroot if r.get('Id') == 'rIdV25Design')
shutil.copy(FIG5, work / 'word' / 'media' / 'v27_figure5_matched_supervision_pipeline.png')
rel5.set('Target', 'media/v27_figure5_matched_supervision_pipeline.png')
from PIL import Image
w_px, h_px = Image.open(FIG5).size
img5 = next(el for el in ch() if 'rIdV25Design' in etree.tostring(el, encoding=str))
for ext in list(img5.iter(q(WP, 'extent'))) + list(img5.iter(q(A, 'ext'))):
    if ext.get('cx') is None:          # <a:ext uri=...> extension entries carry no size
        continue
    cx = int(ext.get('cx')); ext.set('cy', str(int(round(cx * h_px / w_px))))
log(f'  Figure 5 image replaced ({w_px}x{h_px})')

# remove v26 Figure 6 (image + caption) and its relationship
img6 = next(el for el in ch() if 'rIdV25Violins' in etree.tostring(el, encoding=str))
cap6 = ch()[find(ch(), 'Figure 6. Observed prediction-error distributions')]
body.remove(img6); body.remove(cap6)
rel6 = next(r for r in rroot if r.get('Id') == 'rIdV25Violins'); rroot.remove(rel6)
(work / 'word' / 'media' / 'v25_figure6_matched_supervision_violins.png').unlink()
log('  v26 Figure 6 removed (merged into Figure 5)')

CAP5 = ('Matched human and quantitative supervision of compact encoders, shown with the observed '
        'prediction errors. Both arms start from the same 681 source molecules (377 training, 304 '
        'validation; target cations excluded), five paired source seeds and frozen MolFormer features, '
        'and train the 768→512→384→256 encoder without SMOTE: expert Good/Bad labels with a contrastive '
        'objective (top row) or continuous MIC with a regression objective (bottom row). Encoder weights '
        'are frozen before separate CatBoost decoders with identical budgets and categorical task codes '
        'are fitted on target-training folds of the 105 reference QACs. Violins show, for cation (left) '
        'and scaffold (right) holdouts, the 420 compound–endpoint absolute errors per arm on the log₂(mg/L) '
        'scale for S. aureus and E. coli MIC and MBC, each averaged across the five source runs. '
        'Shuffled-human guidance is the label-permutation control and raw MolFormer a single fixed '
        'reference. White markers show medians and bars interquartile ranges; all tails are retained on '
        'shared linear axes. Values are means of absolute errors rather than errors of ensemble '
        'predictions, and correlated endpoints and runs preclude reading density differences as '
        'significance or causal effects. This is the matched follow-up design, rather than the historical '
        'full-corpus quantitative experiment.')
cap5 = ch()[find(ch(), 'Figure 5. Matched human and quantitative supervision')]
ts = list(cap5.iter(q(W, 't')))
flat = ''.join(t.text or '' for t in ts)
label_end = flat.index('Figure 5.') + len('Figure 5.')
# keep the bold label run(s), put the new body into the first run after the label
acc, body_run_set = 0, False
for t in ts:
    s = t.text or ''; a, b = acc, acc + len(s); acc = b
    if b <= label_end:
        continue
    if a < label_end:
        t.text = s[:label_end - a] + ' '
        if not body_run_set:           # label and body share this run
            t.text += CAP5; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); body_run_set = True
        continue
    if not body_run_set:
        t.text = CAP5; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); body_run_set = True
    else:
        t.text = ''
log('  Figure 5 caption rewritten')

log('== renumbering and cross-references')
P = lambda prefix: ch()[find(ch(), prefix)]
replace_in(P('The vertical violins in Figure 6 show'),
           'The vertical violins in Figure 6 show the observed endpoint-error distributions on the same 105 salts.',
           'The violins in Figure 5 show the observed endpoint-error distributions on the same 105 salts. '
           'Median absolute errors are 1.18, 1.08, 1.14 and 1.18 log₂ units for human, quantitative, '
           'shuffled-human and raw MolFormer features under cation holdout, and 1.42, 1.36, 1.30 and 1.38 '
           'under scaffold holdout.', label='Fig6->5 text')
p = P('We additionally tested transfer of source-trained representations')
replace_in(p, '(Figure 7)', '(Figure 6)', label='QHERO ref')
replace_in(p, 'compact encoders in Figures 5–6', 'compact encoders in Figure 5', label='QHERO ref')
p = P('Figure 7. ROC curves for Q-HERO')
replace_in(p, 'Figure 7.', 'Figure 6.', label='QHERO caption')
replace_in(p, 'differs from Figures 5–6', 'differs from Figure 5', label='QHERO caption')
p = P('To evaluate prediction beyond the reference chemical families')
replace_in(p, '(Figure 8)', '(Figure 7)', label='classes ref')
replace_in(p, 'Their independent MIC/MBC measurements form the structural OOD case study described below; '
              'the new computational evaluation keeps these measurements outside target model training and '
              'assesses quantitative predictions in Section 2.3.5.',
           'Their independent MIC/MBC measurements form the structural OOD case study evaluated below; these '
           'measurements are kept outside target model training, and the synthesis of the compounds is '
           'described in Section 2.3.', label='OOD intro')
cap7 = P('Figure 8. Molecular classes represented')
strip_fields(cap7)
replace_in(cap7, 'Figure 8.', 'Figure 7.', label='classes caption')
p = P('The source-matched compact encoders from Section 2.2')
replace_in(p, 'from Section 2.2 provide', 'from Section 2.2.1 provide', label='OOD xref')
replace_in(P('Figure 9 shows the observed OOD error'), 'Figure 9 shows', 'Figure 8 shows', label='OOD text')
replace_in(P('Figure 9. OOD prediction errors'), 'Figure 9.', 'Figure 8.', label='OOD caption')
p = P('The stronger test of supervisory content')
replace_in(p, '(Figures 6 and 9)', '(Figures 5 and 8)', label='2.4 refs')
replace_in(p, 'guidance (Section 2.2).', 'guidance (Section 2.2.2).', label='2.4 refs')
replace_in(P('Figure 4. Original v5 experimental-versus-predicted'), 'Section2.2', 'Section 2.2.1', label='Fig4 caption')

log('== typography')
for prefix, old, new in [
        ('Kojic acid (KA) is a multifunctional', 'bis-QAСs', 'bis-QACs'),
        ('Tetrahydropyridine (THP) scaffold', 'MСR is a convenient', 'MCR is a convenient'),
        ('Finally, a series of glycoluril-based', 'is problemating', 'is problematic'),
        ('Scheme 3. Synthesis of dihydropyrans', 'dihydropyrans -based', 'dihydropyran-based'),
        ('Scheme 4. Synthesis of GU-based', 'GU-based mono-QACs', 'GU-based multi-QACs')]:
    replace_in(P(prefix), old, new, label='typo')
left = [m for m in ('QAСs', 'MСR', 'problemating') if m in ''.join(ptext(e) for e in ch())]
assert not left, left

log('== table of contents')
# the TOC sits inside a content control (w:sdt); its entries are paragraphs within it
for el in list(root.iter(q(W, 'p'))):
    s_ = etree.tostring(el, encoding=str)
    if 'PAGEREF' not in s_:
        continue
    t = ptext(el)
    if t.startswith('2.3.5 Out-of-domain performance verification'):
        el.getparent().remove(el); log('  TOC: 2.3.5 entry removed (its heading no longer exists)')
    elif t.startswith('2.3 Out of domain inference'):
        replace_in(el, '2.3 Out of domain inference', '2.3 Design and synthesis of the new QACs', label='TOC')

tree.write(str(doc_path), xml_declaration=True, encoding='UTF-8', standalone=True)
rels.write(str(rels_path), xml_declaration=True, encoding='UTF-8', standalone=True)


def pack(folder, dst):
    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        ct = folder / '[Content_Types].xml'
        z.write(ct, '[Content_Types].xml')
        for f in sorted(folder.rglob('*')):
            if f.is_file() and f != ct:
                z.write(f, f.relative_to(folder).as_posix())


pack(work, DST); shutil.rmtree(work)
log(f'wrote {DST.name}')

# ------------------------------------------------------------------ SI
log('== SI cross-references')
work = ROOT / '_si27'
shutil.rmtree(work, ignore_errors=True)
with zipfile.ZipFile(SI_SRC) as z:
    z.extractall(work)
sp = work / 'word' / 'document.xml'
st = etree.parse(str(sp)); sroot = st.getroot()
SI_EDITS = [('main Figures 5–6 uses categorical codes', 'main Figure 5 uses categorical codes'),
            ('grouped validation in main Figure 6.', 'grouped validation in main Figure 5.'),
            ('For main Figures 3 and 6,', 'For main Figures 3 and 5,'),
            ('The current main Section 2.3.5', 'The current main Section 2.2.2'),
            ('frozen OOD evaluation in main Figure 9.', 'frozen OOD evaluation in main Figure 8.')]
paras = list(sroot.iter(q(W, 'p')))
for old, new in SI_EDITS:
    hit = [p for p in paras if old in ptext(p)]
    assert len(hit) == 1, (old, len(hit))
    replace_in(hit[0], old, new, label='SI')
for p in paras:
    while 'main Section2.4' in ptext(p):
        replace_in(p, 'main Section2.4', 'main Section 2.4', label='SI')
st.write(str(sp), xml_declaration=True, encoding='UTF-8', standalone=True)
pack(work, SI_DST); shutil.rmtree(work)
log(f'wrote {SI_DST.name}')
(ROOT / 'build_v27.log').write_text('\n'.join(LOG))
