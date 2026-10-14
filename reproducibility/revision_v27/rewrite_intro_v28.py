"""v28: bring the Introduction's stated contributions in line with the completed results,
and make 1,103 the operative label count.

The v27 Introduction still claimed that the expert labels surpass a ten-fold larger
quantitative corpus, that text task descriptions outperform one-hot coding, and that
human guidance exposes biologically relevant components. Sections 2.2.2 and 2.4 now state
the opposite on each point: ordering depends on architecture, decoder and holdout;
shuffled labels remain competitive for the compact encoder; and no mechanism is
identified. The replacement paragraph states what the experiments support, with the
numbers they produced.
"""
from pathlib import Path
import shutil, zipfile
from lxml import etree

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parent.parent
SRC = COMA / '2026_10_14_Paper_2_edited-v27_section2_restructured.docx'
DST = COMA / '2026_10_14_Paper_2_edited-v28_intro_aligned.docx'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q = lambda t: f'{{{W}}}{t}'
LOG = []


def ptext(el):
    return ''.join(t.text or '' for t in el.iter(q('t')))


def replace_in(el, old, new, label=''):
    ts = list(el.iter(q('t')))
    flat = ''.join(t.text or '' for t in ts)
    i = flat.find(old)
    if i < 0:
        raise SystemExit(f'not found [{label}]: {old[:70]!r}')
    pos, spans = 0, []
    for t in ts:
        n = len(t.text or ''); spans.append((pos, pos + n)); pos += n
    j, first = i + len(old), True
    for t, (a, b) in zip(ts, spans):
        if b <= i or a >= j:
            continue
        s = t.text or ''
        t.text = s[:max(0, i - a)] + (new if first else '') + (s[max(0, j - a):] if j < b else '')
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        first = False
    LOG.append(f'  [{label}] {old[:60]!r} -> {new[:60]!r}')
    print(LOG[-1])


work = ROOT / '_v28'
shutil.rmtree(work, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(work)
path = work / 'word' / 'document.xml'
tree = etree.parse(str(path)); root = tree.getroot()
paras = list(root.iter(q('p')))
find = lambda frag: next(p for p in paras if frag in ptext(p))

OLD_CONTRIB = (
    'We make three contributions. First, we learn dedicated molecular embeddings by contrastive '
    'training on a compact set of expert “Good/Bad” activity classifications, and show that these '
    '1,500 binary human judgements rival an order-of-magnitude larger corpus of roughly 10,000 '
    'quantitative measurements covering the same compound families, even surpassing it on the most '
    'difficult Gram-negative endpoint. Second, we show that when the prediction task carries a '
    'textual description of its classes—the bacterial species and the activity type—encoding that '
    'description with large-language-model text embeddings outperforms one-hot encoding, '
    'particularly under scarce data. Third, through an interpretable analysis combining '
    'representational similarity, feature attribution, and a controlled ablation, we demonstrate '
    'that the foundation model already encodes a rich description of these molecules and that human '
    'guidance serves to direct and expose its biologically relevant components for downstream '
    'predictors. We assess generalization on a held-out set of 17 newly synthesized QACs belonging '
    'to a previously unexplored structural subtype.')

NEW_CONTRIB = (
    'We make three contributions. First, we learn dedicated molecular embeddings by contrastive '
    'training on a compact set of expert “Good/Bad” activity classifications — 1,103 final labels in '
    'the recovered archive — and compare them with quantitative supervision under a matched design in '
    'which both arms draw on the same 681 source molecules, the same partitions and five paired '
    'seeds, and feed decoders of identical budget that encode the bacterial species and the activity '
    'type. The two supervision sources give closely similar prediction errors whose ordering depends '
    'on the holdout scheme, so the comparison bounds how far a coarse categorical label can stand in '
    'for measurement rather than establishing an exchange rate between them. Second, we repeat the '
    'question across adaptation routes — a frozen head, LoRA, full fine-tuning and partial-backbone '
    'adaptation — and across cation, scaffold and out-of-domain holdouts, and find that the apparent '
    'ranking of routes and of supervision sources changes with the evaluation: full fine-tuning '
    'improves some grouped target scores while giving the highest error on the new compounds, where '
    'frozen human-guided features with a gradient-boosted decoder give the lowest point loss among '
    'the routes tested. Third, we use label-permutation and weight-restoration controls to locate '
    'where the meaning of a label contributes at all. Shuffled labels remain competitive for the '
    'compact encoder, whereas partial-backbone cation holdout and scaffold-held-out classification on '
    'the external Q-HERO collection resolve a difference in favour of meaningful assignment. A '
    'geometric analysis shows the learned features stay closely aligned with the pretrained '
    'representation (centred kernel alignment 0.93 in-domain and 0.95 on the new compounds), '
    'consistent with a compact task-oriented transformation of existing features rather than newly '
    'discovered chemistry. We assess generalization on a held-out set of 17 newly synthesized QACs '
    'spanning four previously unexplored scaffolds.')

print('== Introduction')
replace_in(find('binary human judgements rival'), OLD_CONTRIB, NEW_CONTRIB, label='contributions')

print('== Section 2.1 label count')
replace_in(find('This procedure yielded a curated collection of 1,500'),
           'This procedure yielded a curated collection of 1,500 labeled compounds encompassing '
           'diverse antibacterial activity data.',
           'This procedure yielded the curated expert collection used throughout this work.',
           label='2.1 count')
replace_in(find('The recovered computational archive contains 1,103'),
           'These final outcomes are distinguished from the earlier collection count reported above, '
           'which requires confirmation from the annotation records.',
           'All models reported here are trained on those 1,103 labels. A larger collection-stage '
           'count appears in the annotation records and requires coauthor confirmation.',
           label='2.1 provenance')

left = [ptext(p)[:80] for p in root.iter(q('p')) if '1,500' in ptext(p)]
print('\nremaining "1,500" mentions:', len(left))
for s in left:
    print('   ', s)

tree.write(str(path), xml_declaration=True, encoding='UTF-8', standalone=True)
if DST.exists():
    DST.unlink()
with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as z:
    ct = work / '[Content_Types].xml'
    z.write(ct, '[Content_Types].xml')
    for f in sorted(work.rglob('*')):
        if f.is_file() and f != ct:
            z.write(f, f.relative_to(work).as_posix())
shutil.rmtree(work)
(ROOT / 'rewrite_intro_v28.log').write_text('\n'.join(LOG))
print('\nwrote', DST.name)
