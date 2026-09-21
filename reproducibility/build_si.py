#!/usr/bin/env python
"""Assemble the Supplementary Information page, inlining the matplotlib SVGs."""
import re, os, pandas as pd

R = '/Users/egorilin/Desktop/COMA/reproducibility'
F = f'{R}/figures'
OUT = '/private/tmp/claude-501/-Users-egorilin-Desktop-COMA/990d2f42-4236-4501-b9e0-fecccb0c4e55/scratchpad/supplementary.html'


def svg(name):
    s = open(f'{F}/{name}.svg', encoding='utf-8').read()
    s = s[s.index('<svg'):]
    # strip the fixed pixel size so the figure scales to its container
    s = re.sub(r'<svg([^>]*?)\swidth="[^"]*"', r'<svg\1', s, count=1)
    s = re.sub(r'<svg([^>]*?)\sheight="[^"]*"', r'<svg\1', s, count=1)
    s = s.replace('<svg', '<svg preserveAspectRatio="xMidYMid meet"', 1)
    return s


def fig(num, name, caption):
    return f'''<figure class="fig">
  <div class="fig-plate">{svg(name)}</div>
  <figcaption><span class="fig-n">Figure S{num}.</span> {caption}</figcaption>
</figure>'''


# ---------------------------------------------------------------- tables
qh = pd.read_csv(f'{R}/qhero/qhero_metrics.csv')
REPS = ['expert (Good/Bad)', 'multi-regression', 'MolFormer (raw)']
import json as _json
FT = f'{R}/finetune'
ft1 = pd.DataFrame([_json.loads(l) for l in open(f'{FT}/runs.jsonl')])
ft2 = pd.DataFrame([_json.loads(l) for l in open(f'{FT}/runs_direct.jsonl')])
rcal = pd.read_csv(f'{FT}/recalibration.csv')
TG = ['QAC-105', 'Q-HERO', 'OOD-17']


def ft_table1():
    order = [('predict-the-mean', 'null baseline'), ('6 descriptors', 'null baseline'),
             ('MolFormer frozen', 'no fine-tuning'),
             ('FT expert-binary', 'fine-tuned \u00b7 740 binary labels'),
             ('FT quant-molecule', 'fine-tuned \u00b7 1153 MIC values'),
             ('FT quant-record', 'fine-tuned \u00b7 9338 MIC values')]
    best = {t: ft1[ft1.target == t].groupby('representation').R2.mean().max() for t in TG}
    rows = []
    for name, proto in order:
        cells = ''
        for t in TG:
            sub = ft1[(ft1.representation == name) & (ft1.target == t)]
            if not len(sub):
                cells += '<td class="num">\u00b7</td>'; continue
            m = sub.R2.mean(); sd = sub.R2.std() if len(sub) > 1 else float('nan')
            mk = ' class="best"' if abs(m - best[t]) < 1e-9 else ' class="num"'
            sdt = '' if pd.isna(sd) else f' <span class="sd">\u00b1 {sd:.2f}</span>'
            cells += f'<td class="num"{mk.replace(chr(34)+"num"+chr(34), chr(34)+"num best"+chr(34)) if "best" in mk else ""}>{m:+.3f}{sdt}</td>' if False else f'<td class="num{" best" if "best" in mk else ""}">{m:+.3f}{sdt}</td>'
        rows.append(f'<tr><td>{name}</td><td>{proto}</td>{cells}</tr>')
    return '\n'.join(rows)


def ft_table2(metric, d=3):
    lbl = {'FT expert-binary (direct)': ('740 binary expert labels', 0),
           'FT quant-molecule (direct)': ('1153 MIC values', 1),
           'FT quant-record (direct)': ('9338 MIC values', 2),
           'frozen MolFormer + CatBoost': ('not fine-tuned', 3),
           'predict source mean': ('null baseline', 4)}
    sub = ft2[ft2[metric].notna()]
    keys = sorted(sub.groupby(['representation', 'source']).groups.keys(),
                  key=lambda k: (lbl.get(k[0], ('', 9))[1], k[1]))
    best = {t: sub[sub.target == t].groupby(['representation', 'source'])[metric].mean().max() for t in TG}
    rows = []
    for rep, src in keys:
        cells = ''
        for t in TG:
            q = sub[(sub.representation == rep) & (sub.source == src) & (sub.target == t)]
            if not len(q):
                cells += '<td class="num">\u00b7</td>'; continue
            m = q[metric].mean(); sd = q[metric].std() if len(q) > 1 else float('nan')
            isb = abs(m - best[t]) < 1e-9
            sdt = '' if pd.isna(sd) else f' <span class="sd">\u00b1 {sd:.2f}</span>'
            cells += f'<td class="num{" best" if isb else ""}">{m:+.{d}f}{sdt}</td>'
        note = lbl.get(rep, ('', 9))[0]
        if rep in ('frozen MolFormer + CatBoost', 'predict source mean'):
            note = f'{note} \u00b7 {src}'
        rows.append(f'<tr><td>{rep.replace(" (direct)", "")}</td><td>{note}</td>{cells}</tr>')
    return '\n'.join(rows)


def ft_table3():
    g = rcal[rcal.source == 'quant-record'].groupby('target')[
        ['raw_R2', 'recal_R2', 'pearson', 'slope', 'pred_mean', 'true_mean']].mean().reindex(TG)
    rows = []
    for t in TG:
        r = g.loc[t]; off = r.pred_mean - r.true_mean
        rows.append(f'<tr><td>{t}</td><td class="num">{r.raw_R2:+.2f}</td>'
                    f'<td class="num best">{r.recal_R2:+.2f}</td><td class="num">{r.pearson:.2f}</td>'
                    f'<td class="num">{r.slope:.2f}</td><td class="num">{off:+.2f}</td>'
                    f'<td class="num">{2**off:.1f}\u00d7</td></tr>')
    return '\n'.join(rows)


def qhero_table():
    rows = []
    for subset in ['all Q-HERO', 'unseen by expert encoder']:
        for split in ['random 5-fold', 'scaffold 5-fold']:
            for rep in REPS:
                r = qh[(qh.subset == subset) & (qh.split == split) & (qh.representation == rep)].iloc[0]
                best = qh[(qh.subset == subset) & (qh.split == split)].R2_mean.max()
                mark = ' class="best"' if abs(r.R2_mean - best) < 1e-9 else ''
                rows.append(
                    f'<tr><td>{subset}</td><td>{split}</td><td>{rep}</td>'
                    f'<td class="num">{int(r.n)}</td>'
                    f'<td class="num"{mark}>{r.R2_mean:.3f} <span class="sd">± {r.R2_sd:.3f}</span></td>'
                    f'<td class="num">{r.RMSE_mean:.3f} <span class="sd">± {r.RMSE_sd:.3f}</span></td></tr>')
    return '\n'.join(rows)


t2p = f'{R}/table2/table2_rebuild.csv'
HAS_T2 = os.path.exists(t2p)
if HAS_T2:
    t2 = pd.read_csv(t2p)
    t2['representation'] = t2.representation.replace({'human (Good/Bad)': 'expert (Good/Bad)'})
    EPS = ['S. aureus MIC', 'S. aureus MBC', 'E. coli MIC', 'E. coli MBC']

    def t2_table():
        rows = []
        for sp, lab in [('pairs', 'random over (molecule, endpoint) pairs'),
                        ('mol', 'grouped by molecule')]:
            for rep in REPS:
                d = t2[(t2.split == sp) & (t2.representation == rep)].set_index('endpoint').reindex(EPS)
                cells = ''.join(
                    f'<td class="num">{v:.2f} <span class="sd">± {s:.2f}</span></td>'
                    for v, s in zip(d.R2_mean, d.R2_sd))
                rows.append(f'<tr><td>{lab}</td><td>{rep}</td>{cells}</tr>')
        return '\n'.join(rows)

FIG_T2 = fig(6, 'figS6_split_effect',
             'QAC-105 in-domain benchmark, CatBoost R² in the multitask setting, mean ± sd over 10 seeds. '
             '<strong>Left:</strong> the split used in the original notebook, drawn at random over '
             '(molecule, endpoint) pairs — each compound contributes up to four rows carrying an identical '
             'feature vector, so the same molecule appears in both training and test. '
             '<strong>Right:</strong> the same models under a grouped split in which a molecule falls '
             'entirely on one side. The three representations remain within one standard deviation of one '
             'another under both regimes; what changes the numbers is the split, not the supervision.'
             ) if HAS_T2 else ''

T2_TABLE = f'''
<div class="tbl-wrap">
<table>
  <caption><span class="fig-n">Table S3.</span> QAC-105 in-domain benchmark, R² (mean ± sd, 10 seeds), multitask CatBoost on 432 (molecule, endpoint) pairs from 108 compounds.</caption>
  <thead><tr><th>Split</th><th>Representation</th><th class="num">S. aureus MIC</th><th class="num">S. aureus MBC</th><th class="num">E. coli MIC</th><th class="num">E. coli MBC</th></tr></thead>
  <tbody>
{t2_table()}
  </tbody>
</table>
</div>''' if HAS_T2 else ''

PAGE = f'''<title>Expert Supervision Supplement</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
  :root {{
    --paper:      #fbfaf7;
    --plate:      #ffffff;
    --ink:        #15171b;
    --ink-2:      #474d57;
    --muted:      #878d97;
    --rule:       #e2e2dc;
    --rule-soft:  #eeeeE8;
    --accent:     #2a78d6;
    --accent-dim: #d9e6f7;
    --flag:       #a8410f;
    --flag-bg:    #fbf0e8;

    --serif: "Source Serif 4", "Iowan Old Style", Georgia, serif;
    --mono:  "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;

    --measure: 40rem;
    --wide:    62rem;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --paper:      #14151a;
      --plate:      #ffffff;
      --ink:        #eceef2;
      --ink-2:      #a9b0bb;
      --muted:      #79808b;
      --rule:       #2b2e36;
      --rule-soft:  #21242b;
      --accent:     #6aa6ef;
      --accent-dim: #1e2c3f;
      --flag:       #e09268;
      --flag-bg:    #2a1d15;
    }}
  }}
  :root[data-theme="dark"] {{
    --paper:      #14151a;
    --plate:      #ffffff;
    --ink:        #eceef2;
    --ink-2:      #a9b0bb;
    --muted:      #79808b;
    --rule:       #2b2e36;
    --rule-soft:  #21242b;
    --accent:     #6aa6ef;
    --accent-dim: #1e2c3f;
    --flag:       #e09268;
    --flag-bg:    #2a1d15;
  }}

  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: var(--serif);
    font-size: 17px;
    line-height: 1.62;
    -webkit-font-smoothing: antialiased;
  }}
  .sheet {{
    max-width: var(--wide);
    margin: 0 auto;
    padding-inline: 20px;
    padding-block: 3.5rem 5rem;
    display: flex;
    flex-direction: column;
    gap: 3.25rem;
  }}
  .measure {{ max-width: var(--measure); }}

  /* ---------- masthead ---------- */
  .mast {{ display: flex; flex-direction: column; gap: .9rem; }}
  .eyebrow {{
    font-family: var(--mono); font-size: .7rem; font-weight: 500;
    letter-spacing: .14em; text-transform: uppercase; color: var(--accent);
  }}
  .mast h1 {{
    font-size: clamp(1.9rem, 1.35rem + 2.1vw, 2.8rem);
    line-height: 1.12; font-weight: 700; margin: 0; text-wrap: balance;
    letter-spacing: -.012em;
  }}
  .mast .paper-ref {{
    font-size: 1.02rem; color: var(--ink-2); font-style: italic;
    max-width: var(--measure); margin: 0;
  }}
  .mast-meta {{
    display: flex; flex-wrap: wrap; gap: .4rem 1.6rem;
    font-family: var(--mono); font-size: .74rem; color: var(--muted);
    border-top: 1px solid var(--rule); padding-top: .9rem; margin-top: .4rem;
  }}
  .mast-meta b {{ color: var(--ink-2); font-weight: 500; }}

  /* ---------- sections ---------- */
  section {{ display: flex; flex-direction: column; gap: 1.15rem; scroll-margin-top: 1rem; }}
  h2 {{
    font-size: 1.32rem; font-weight: 600; margin: 0; letter-spacing: -.005em;
    display: flex; gap: .7rem; align-items: baseline; text-wrap: balance;
  }}
  h2 .sn {{
    font-family: var(--mono); font-size: .78rem; font-weight: 600;
    color: var(--accent); letter-spacing: .04em; flex: none;
    padding-top: .12rem;
  }}
  h3 {{
    font-family: var(--mono); font-size: .76rem; font-weight: 600;
    letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2);
    margin: .6rem 0 0;
  }}
  p {{ margin: 0; max-width: var(--measure); }}
  section > p + p {{ margin-top: -.15rem; }}
  strong {{ font-weight: 600; }}
  code, .mono {{ font-family: var(--mono); font-size: .86em; }}
  a {{ color: var(--accent); text-underline-offset: .18em; }}

  ul {{ margin: 0; padding-left: 1.15rem; max-width: var(--measure);
        display: flex; flex-direction: column; gap: .45rem; }}
  li::marker {{ color: var(--muted); }}

  /* ---------- figures ---------- */
  .fig {{ margin: .6rem 0 0; display: flex; flex-direction: column; gap: .85rem; }}
  .fig-plate {{
    background: var(--plate);
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 14px 10px;
    overflow-x: auto;
  }}
  .fig-plate svg {{ display: block; width: 100%; height: auto; min-width: 520px; }}
  figcaption {{
    font-size: .875rem; line-height: 1.58; color: var(--ink-2);
    max-width: var(--wide);
  }}
  .fig-n {{ font-family: var(--mono); font-size: .78rem; font-weight: 600; color: var(--ink); letter-spacing: .02em; }}

  /* ---------- tables ---------- */
  .tbl-wrap {{ overflow-x: auto; margin-top: .4rem; }}
  table {{
    border-collapse: collapse; width: 100%; min-width: 560px;
    font-size: .845rem; font-variant-numeric: tabular-nums;
  }}
  caption {{
    caption-side: top; text-align: left; font-size: .875rem; color: var(--ink-2);
    padding-bottom: .7rem; line-height: 1.55;
  }}
  th, td {{ padding: .45rem .7rem; text-align: left; border-bottom: 1px solid var(--rule-soft); }}
  thead th {{
    font-family: var(--mono); font-size: .7rem; font-weight: 600; letter-spacing: .05em;
    text-transform: uppercase; color: var(--muted);
    border-bottom: 1px solid var(--rule); white-space: nowrap;
  }}
  tbody tr:last-child td {{ border-bottom: 1px solid var(--rule); }}
  td.num, th.num {{ text-align: right; font-family: var(--mono); font-size: .8rem; white-space: nowrap; }}
  .sd {{ color: var(--muted); font-size: .92em; }}
  td.best {{ color: var(--accent); font-weight: 600; }}

  /* ---------- callout ---------- */
  .flag {{
    background: var(--flag-bg);
    border-left: 2px solid var(--flag);
    padding: .85rem 1.05rem;
    max-width: var(--measure);
    font-size: .92rem; line-height: 1.55;
  }}
  .flag .flag-h {{
    font-family: var(--mono); font-size: .68rem; font-weight: 600;
    letter-spacing: .11em; text-transform: uppercase; color: var(--flag);
    display: block; margin-bottom: .3rem;
  }}

  .keyfacts {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
  }}
  .keyfacts div {{ padding: .85rem 1rem .85rem 0; }}
  .keyfacts .k {{
    font-family: var(--mono); font-size: .68rem; letter-spacing: .09em;
    text-transform: uppercase; color: var(--muted); display: block; margin-bottom: .2rem;
  }}
  .keyfacts .v {{ font-size: 1.45rem; font-weight: 600; letter-spacing: -.015em; font-variant-numeric: tabular-nums; }}
  .keyfacts .v small {{ font-size: .8rem; font-weight: 400; color: var(--ink-2); letter-spacing: 0; }}

  footer {{
    border-top: 1px solid var(--rule); padding-top: 1.3rem;
    font-family: var(--mono); font-size: .74rem; color: var(--muted);
    line-height: 1.7; max-width: var(--wide);
  }}
  footer a {{ color: var(--accent); }}

  @media (max-width: 560px) {{
    body {{ font-size: 16px; }}
    h2 {{ flex-direction: column; gap: .2rem; }}
    .sheet {{ gap: 2.6rem; padding-block: 2.5rem 3.5rem; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
</style>

<div class="sheet">

  <header class="mast">
    <span class="eyebrow">Supplementary Information</span>
    <h1>Expert annotation, dataset overlap and external validation</h1>
    <p class="paper-ref">Supporting <em>Expert Judgement as Supervision: Binary Human Labels Match Quantitative
      Measurements for Representation Learning for Rational Design of Highly Efficient Biocides</em>.</p>
    <div class="mast-meta">
      <span><b>Expert set</b> 1103 compounds</span>
      <span><b>Quantitative corpus</b> 13 404 records</span>
      <span><b>External benchmark</b> Q-HERO, 411 structures</span>
      <span><b>Out-of-domain</b> 17 compounds</span>\n      <span><b>Fine-tuning</b> 3 seeds \u00d7 3 sources</span>
    </div>
  </header>

  <section id="s1">
    <h2><span class="sn">S1</span> The expert annotation set</h2>
    <p>Two annotation rounds were delivered as spreadsheets: batch A (<code>2025-12-15_QACs SMILES_Final.xls</code>,
      ids 1–518) and batch B (<code>2026-02-11_QACs SMILES_NF_MS_519-1103.xls</code>, ids 519–1103). Concatenated they
      give <strong>1103 rows with no duplicate identifiers</strong>, labelled 859 <em>Bad</em> and 244 <em>Good</em>.
      This is the set that supervised the contrastive encoder, and it matches the shape logged during the
      interpretability run (<code>MoLFormer X: (1103, 768) | Good/Bad: {{0: 859, 1: 244}}</code>).</p>

    <div class="keyfacts">
      <div><span class="k">Labelled compounds</span><span class="v">1103</span></div>
      <div><span class="k">Positive rate</span><span class="v">22.1<small>&thinsp;% Good</small></span></div>
      <div><span class="k">Majority baseline</span><span class="v">0.779<small> accuracy</small></span></div>
      <div><span class="k">SMILES needing repair</span><span class="v">9.6<small>&thinsp;%</small></span></div>
    </div>

    <p>Two properties of this set bear on how its results should be read. First, the class balance is strongly
      skewed, so the accuracy of 0.856 reported for the MolFormer classifier sits only 0.077 above a
      majority-class baseline; the F1 of 0.655 is the informative figure. Second, the two rounds do not share a
      positive rate: batch A is 29.5&thinsp;% <em>Good</em> and batch B 15.6&thinsp;%, a near two-fold shift
      between December and February.</p>

    {fig(1, 'figS1_expert_set',
         'Composition and quality of the expert annotation set. '
         '<strong>Left:</strong> class balance in each annotation round; the positive rate falls from 29.5&thinsp;% '
         'to 15.6&thinsp;% between rounds. '
         '<strong>Centre:</strong> RDKit parse status of the 1103 supplied SMILES. '
         '<strong>Right:</strong> malformed strings by round — 104 of the 106 defects fall in batch B.')}

    <div class="flag">
      <span class="flag-h">Structure parsing</span>
      106 of the 1103 supplied SMILES (9.6&thinsp;%) do not parse in RDKit. The dominant failure is a
      data-entry pattern in which counterions are written <code>.[Br]-.[Br]-</code> rather than
      <code>.[Br-].[Br-]</code>; 91 of them are recovered by that substitution alone and 15 remain
      unparseable because the string was truncated on entry. MolFormer tokenises SMILES without validating
      them, so these strings produced embeddings regardless. The repaired and canonicalised set is released as
      <code>expert_labels_1103.csv</code>.
    </div>

    <p>After canonicalisation the 1088 parseable rows collapse to 1066 unique structures. Twenty-two structures
      appear twice; one pair (ids 235 and 337) carries <em>opposite</em> expert labels for the same molecule.
      The delivered files contain only the adjudicated <code>Annotation_Final</code> column — no per-annotator
      votes — so the majority rule described in the main text cannot be re-derived and no inter-rater agreement
      statistic can be computed from the released data.</p>
  </section>

  <section id="s2">
    <h2><span class="sn">S2</span> Dataset composition and overlap</h2>
    <p>Five compound collections enter the study. Because several were assembled from overlapping literature
      sources, their intersections determine which comparisons are informative and which are confounded.
      All sets were canonicalised with RDKit before intersection.</p>

    {fig(2, 'figS2_overlap',
         'Shared molecules between the five collections. The diagonal gives each set’s size after '
         'canonicalisation and de-duplication; off-diagonal cells count structures common to the row and '
         'column sets. QAC-105 is fully contained in the expert-labelled set and almost fully contained in '
         'the quantitative corpus; the 17-compound out-of-domain set is disjoint from everything.')}

    <div class="flag">
      <span class="flag-h">Containment of the in-domain benchmark</span>
      All 105 molecules of QAC-105 — the benchmark behind Tables 1 and 2 of the main text — are members of the
      1103-compound expert set, and 99 of them are in the quantitative corpus. Both encoders therefore saw every
      QAC-105 test molecule during representation learning. The contamination is symmetric across the two arms,
      so the <em>comparison</em> between them survives, but the absolute R² values on that benchmark are not
      estimates of generalisation. The 17-compound out-of-domain set has zero overlap with any training
      collection and carries the generalisation claims.
    </div>

    <p>A related point concerns the framing of the two supervision sources. 1035 of the 1066 expert-labelled
      structures (97&thinsp;%) also appear in the quantitative corpus. The comparison is therefore not between
      two independently assembled collections but between coarse and fine labels on substantially the same
      molecules — a more tightly controlled contrast than a comparison of separate corpora would be.</p>
  </section>

  <section id="s3">
    <h2><span class="sn">S3</span> Q-HERO: an external benchmark</h2>
    <p>Q-HERO supplies 411 canonicalised QAC structures with a matched <em>S. aureus</em> MIC endpoint. It shares
      exactly one molecule with QAC-105, which makes it the only available substitute for the contaminated
      in-domain evaluation. It does share 222 molecules with the expert-labelled set, so results are reported
      both on the full collection and on the 189 structures the expert encoder never saw.</p>

    {fig(3, 'figS3_qhero_violins',
         'Distribution of absolute residuals on Q-HERO under scaffold-grouped five-fold cross-validation '
         '(CatBoost, log₂ MIC in µM). Violins show the full residual density, clipped to the observed range; '
         'the inner box gives the interquartile range with a white median rule, labelled at right. '
         'The three representations produce near-identical distributions on both the full collection and the '
         'subset unseen by the expert encoder.')}

    <p>Under a random fold assignment all three representations reach R² ≈ 0.31–0.46, but the same models drop
      to R² ≈ 0 once folds are grouped by Bemis–Murcko scaffold. The gap indicates that the apparent skill under
      random splitting is scaffold recognition rather than transferable structure–activity signal — the same
      mechanism documented for the in-domain benchmark in §S5.</p>

    {fig(4, 'figS4_qhero_r2',
         'Variance explained on Q-HERO, mean ± sd over five seeds. Under random folds (left) the three '
         'representations are separated by less than 0.06 R²; under scaffold-grouped folds (right) all three '
         'fall to approximately zero. Raw MolFormer is the highest-scoring representation in three of the four '
         'panels and is never beaten by either contrastive encoder outside its own seed spread.')}

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S1.</span> Q-HERO cross-validated performance, mean ± sd over five seeds.
        Best R² within each subset × split block is marked.</caption>
      <thead><tr><th>Subset</th><th>Split</th><th>Representation</th><th class="num">n</th><th class="num">R²</th><th class="num">RMSE</th></tr></thead>
      <tbody>
{qhero_table()}
      </tbody>
    </table>
    </div>

    <div class="flag">
      <span class="flag-h">Negative result</span>
      On this external benchmark neither contrastive encoder outperforms the raw MolFormer features. On the
      189 structures the expert encoder never saw, scaffold-split R² is 0.023 for raw MolFormer, −0.019 for the
      expert encoder and −0.045 for the regression encoder. The equivalence between the two supervision sources
      therefore holds here as well, but it holds at a level indistinguishable from applying no contrastive
      training at all. Evidence that the expert labels add a task-relevant component beyond the foundation model
      rests on the 17-compound out-of-domain set alone (§S4), where the effect is not statistically separable
      from zero either.
    </div>
  </section>

  <section id="s4">
    <h2><span class="sn">S4</span> Out-of-domain equivalence of the two supervision sources</h2>
    <p>Both encoders were trained on the 108 in-domain biocides and applied to the 17 newly synthesised
      compounds, giving 68 paired (compound, endpoint) residuals. One <em>E. coli</em> MBC value is
      right-censored (<code>&gt;500</code>) and is treated at its censoring bound. Predictions are averaged over
      five CatBoost seeds before residuals are formed.</p>

    <h3>Why a paired test rather than a causal forest</h3>
    <p>The design is fully crossed and deterministic: every compound–endpoint unit receives both
      representations, so both potential outcomes are observed and the average effect is the mean of the
      observed paired differences. No identification assumption is required, and the propensity score is 0.5
      by construction. Double machine learning exists to remove confounding through residualisation; with
      nothing to confound, its cross-fitting adds variance without removing bias. Fitting
      <code>CausalForestDML</code> to these data returns an ATE of −0.177 with a 95&thinsp;% interval of
      [−0.994, +0.640] — an interval four times wider than the cluster bootstrap on the same residuals
      (−0.160, [−0.406, +0.088]) and, at 17 clusters, well below the number at which cluster-robust asymptotics
      are dependable. The paired analysis below is reported in its place.</p>

    {fig(5, 'figS5_equivalence',
         '<strong>Left:</strong> per-compound mean difference in absolute residual between the expert-supervised '
         'and regression-supervised encoders, averaged over the four endpoints; negative values favour expert '
         'supervision, which leads on 11 of 17 compounds. '
         '<strong>Right:</strong> two one-sided tests against three equivalence margins. The grey band is the '
         'margin, the bar the 90&thinsp;% confidence interval on the molecule-level mean, and the point the '
         'estimate. Equivalence is established at ±0.5 log₂ units and fails at ±0.25.')}

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S2.</span> Paired comparison of the two supervision sources on the
        out-of-domain set: 68 (compound, endpoint) pairs clustered within 17 compounds.</caption>
      <thead><tr><th>Statistic</th><th class="num">Value</th><th>Interpretation</th></tr></thead>
      <tbody>
        <tr><td>Out-of-domain RMSE, expert encoder</td><td class="num">2.109</td><td>lowest of the three</td></tr>
        <tr><td>Out-of-domain RMSE, raw MolFormer</td><td class="num">2.291</td><td>—</td></tr>
        <tr><td>Out-of-domain RMSE, regression encoder</td><td class="num">2.396</td><td>highest of the three</td></tr>
        <tr><td>Mean paired Δ (expert − regression)</td><td class="num">−0.158</td><td>favours expert supervision</td></tr>
        <tr><td>Pairs favouring expert supervision</td><td class="num">38 / 68</td><td>56&thinsp;%</td></tr>
        <tr><td>Sign test</td><td class="num">p = 0.396</td><td>not significant</td></tr>
        <tr><td>Wilcoxon signed-rank</td><td class="num">p = 0.103</td><td>not significant</td></tr>
        <tr><td>Cluster bootstrap ATE, 95&thinsp;% CI</td><td class="num">−0.160 [−0.406, +0.088]</td><td>includes zero</td></tr>
        <tr><td>TOST at ±1.0 log₂</td><td class="num">p &lt; 0.001</td><td>equivalent</td></tr>
        <tr><td>TOST at ±0.5 log₂</td><td class="num">p = 0.010</td><td>equivalent</td></tr>
        <tr><td>TOST at ±0.25 log₂</td><td class="num">p = 0.248</td><td>not established</td></tr>
      </tbody>
    </table>
    </div>

    <p>The equivalence conclusion of the main text is supported, and at a tighter margin than the one quoted
      there. A margin of ±1.0 log₂ — one two-fold dilution — is roughly 45&thinsp;% of the out-of-domain RMSE
      and six times the observed effect, so a test against it has little power to discriminate; equivalence at
      ±0.5 log₂ is the stronger and better-supported statement. At ±0.25 log₂ the data are not sufficient to
      establish equivalence, which bounds how fine a claim this design can carry.</p>

    <p>Two descriptive statistics in the main text do not reproduce from these residuals. The fraction of pairs
      favouring the expert encoder is 56&thinsp;% here rather than 66&thinsp;%, and neither figure is
      significantly different from chance. The absolute out-of-domain RMSE values also differ from those in the
      main text; the ordering of the expert encoder against raw MolFormer is preserved, but the regression
      encoder ranks below raw MolFormer in this re-derivation.</p>
  </section>

  <section id="s5">
    <h2><span class="sn">S5</span> The in-domain split and what it contributes</h2>
    <p>The in-domain evaluation is built from 432 (molecule, endpoint) pairs over 108 compounds. In the original
      notebook the train/test division is drawn at random over those pairs. Because a compound contributes up to
      four rows whose molecular feature vector is identical, a random pair split places the same molecule on both
      sides of the division, and a gradient-boosted model can carry an activity value learned from one of its rows
      to another.</p>

    {FIG_T2}
    {T2_TABLE}

    <p>A further consequence is visible in Tables 1 and 2 of the main text. For a fixed test set
      R² = 1 − RMSE²/Var, so RMSE²/(1 − R²) must be constant down a column. It is not: for <em>S. aureus</em>
      MIC the classified-embedding rows move from RMSE 0.91 at R² 0.71 to RMSE 0.92 at R² 0.75 — a higher error
      and a higher R² on the same endpoint, which cannot occur on a common test set. The plain and multitask rows
      of those tables come from separate pipelines with separate splits and are not directly comparable.</p>
  </section>

  <section id="s6">
    <h2><span class="sn">S6</span> Encoder provenance</h2>
    <p>Three encoder checkpoints share the 768 → 512 → 384 → 256 trunk described in the main text but differ in
      projection head, which identifies them as separate training runs.</p>

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S4.</span> Encoder checkpoints and the analyses they support.</caption>
      <thead><tr><th>Checkpoint</th><th>Trunk</th><th>Projection head</th><th>Used by</th></tr></thead>
      <tbody>
        <tr><td><code>encoder_borderline_smote.pth</code></td><td class="mono">768→512→384→256</td><td class="mono">128 / 128</td><td>expert arm, Tables 1–2, out-of-domain</td></tr>
        <tr><td><code>encoder_reg_only.pth</code></td><td class="mono">768→512→384→256</td><td class="mono">128 / 128</td><td>regression arm, ablation</td></tr>
        <tr><td><code>encoder_256_final.pth</code></td><td class="mono">768→512→384→256</td><td class="mono">256 / 256</td><td>interpretability run log</td></tr>
      </tbody>
    </table>
    </div>

    <p>The ablation pair is correctly matched, so the statement in the main text that the two encoders differ in
      exactly one respect holds for it. The interpretability run recorded in
      <code>interpretability_results/embedding_analysis_full/run.log</code> loaded the third checkpoint, whose
      projection head differs; the script that produced <code>analysis/cka_probing.csv</code> is not in the
      repository, so it cannot be confirmed which encoder generated the published CKA and SHAP values. The
      released probing file gives linear-probe R² of 0.891 for MolFormer → embedding and 0.844 in the reverse
      direction, and <code>decomposition/shap_by_type.csv</code> gives a summed attribution of 2.656 for the
      256-dimensional embedding block.</p>
  </section>


  <section id="s7">
    <h2><span class="sn">S7</span> Frozen versus fine-tuned representations</h2>
    <p>The encoder used in the main text adapts a frozen backbone: MolFormer weights are held
      fixed and only a contrastive head is trained. That caps what any supervision signal can
      express, because the head can only recombine features the frozen model already computes.
      To separate the effect of the bottleneck from the effect of the supervision, MolFormer-XL
      was fine-tuned end-to-end on each source in turn.</p>

    <h3>Protocol</h3>
    <ul>
      <li><strong>Held out.</strong> Every molecule belonging to any evaluation set — QAC-105,
        Q-HERO and the 17 newly synthesised compounds, 532 structures in total — was removed
        from all three training sources. No representation has seen a test compound under any
        form of supervision.</li>
      <li><strong>Sources after hold-out.</strong> 740 expert-annotated molecules;
        1153 molecule-level MIC values; 9338 MIC records over the same 1153 molecules — a
        12.6-fold difference between the binary and the quantitative arms.</li>
      <li><strong>Training.</strong> Embeddings and the lowest four encoder layers frozen
        (16.0 of 44.4 M parameters), one-cycle schedule at peak learning rate 3&#215;10<sup>-5</sup>,
        weight decay 0.01, gradient clipping at 1.0, early stopping with patience 6 on a
        validation split disjoint by Bemis–Murcko scaffold. Three seeds.</li>
      <li><strong>Evaluation.</strong> Gradient-boosted regressors on the resulting embeddings,
        under scaffold-grouped five-fold cross-validation for QAC-105 and Q-HERO; the
        out-of-domain compounds are predicted from a model trained on QAC-105.</li>
    </ul>

    {fig(7, 'figS7_representation_quality',
         'Variance explained by each representation, mean \u00b1 sd over three seeds. Every '
         'fine-tuned model beats the frozen encoder on every target, and both null baselines sit '
         'at or below zero. Absolute values remain low: Q-HERO is the only target on which any '
         'representation clears R\u00b2 = 0.1.')}

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S5.</span> Representation quality, R\u00b2 (mean \u00b1 sd,
        3 seeds). Best per target marked.</caption>
      <thead><tr><th>Representation</th><th>Supervision</th>
        <th class="num">QAC-105</th><th class="num">Q-HERO</th><th class="num">OOD-17</th></tr></thead>
      <tbody>
{ft_table1()}
      </tbody>
    </table>
    </div>

    <div class="flag">
      <span class="flag-h">Correction to the frozen-encoder comparison</span>
      Section S3 reports that on Q-HERO neither contrastive encoder outperforms raw MolFormer.
      That holds for the frozen configuration and does not generalise: once the backbone is free
      to move, Q-HERO rises from R\u00b2 = 0.134 to 0.27–0.31, QAC-105 from \u22120.105 to
      approximately +0.05, and OOD-17 from \u22120.289 to \u22120.027. The frozen setup was
      suppressing what every supervision source contributed, and comparisons made through it
      understate all of them equally.
    </div>

    <p>Under this setup the central comparison of the manuscript survives, and on data from which
      every test compound has been removed. Embeddings learned from 740 binary expert judgements
      match those learned from 9338 quantitative measurements: the expert arm leads on QAC-105
      (0.053 against 0.048), the quantitative arms lead on Q-HERO (0.312 against 0.269) and on the
      out-of-domain set (\u22120.027 against \u22120.174), and no difference exceeds roughly one
      standard deviation across seeds.</p>
  </section>

  <section id="s8">
    <h2><span class="sn">S8</span> Zero-shot inference and calibration</h2>
    <p>Section S7 fits a fresh downstream model on target-domain data, so it measures the quality
      of the representation rather than the ability to predict. Here the fine-tuned head predicts
      the evaluation sets itself, with nothing fitted on the target. The quantitative sources and
      all three targets are log\u2082 MIC in µM, so regression transfers directly; the expert head
      emits a Good/Bad logit instead, so both arms are scored on rank agreement with the measured
      MIC (Spearman, signed so that positive is correct for either) and on ROC-AUC against MIC
      split at each target&#8217;s median.</p>

    {fig(8, 'figS8_zeroshot',
         'Zero-shot transfer. <strong>Left:</strong> rank agreement with the measured MIC is '
         'strong and grows with the amount of supervision, reaching \u03c1 = 0.75 on the '
         'out-of-domain compounds for the model trained on 9338 values. <strong>Right:</strong> '
         'the coefficient of determination of those same predictions is negative on every target.')}

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S6.</span> Rank agreement with measured log\u2082 MIC
        (Spearman \u03c1, signed so positive is correct for both arms).</caption>
      <thead><tr><th>Model</th><th>Supervision</th>
        <th class="num">QAC-105</th><th class="num">Q-HERO</th><th class="num">OOD-17</th></tr></thead>
      <tbody>
{ft_table2('rank_agreement')}
      </tbody>
    </table>
    </div>

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S7.</span> ROC-AUC against MIC binarised at each
        target&#8217;s median. Chance is 0.500.</caption>
      <thead><tr><th>Model</th><th>Supervision</th>
        <th class="num">QAC-105</th><th class="num">Q-HERO</th><th class="num">OOD-17</th></tr></thead>
      <tbody>
{ft_table2('AUC')}
      </tbody>
    </table>
    </div>

    <div class="flag">
      <span class="flag-h">A model that never saw a concentration</span>
      The expert arm was fine-tuned only on Good/Bad judgements and has no notion of a
      concentration. It nonetheless ranks unseen compounds by their measured MIC at
      \u03c1 = 0.22 / 0.40 / 0.30 and separates above- from below-median actives at
      AUC 0.64 / 0.69 / 0.60 against a chance value of 0.50. This is direct evidence that a
      coarse human call carries quantitatively relevant information, which is the claim
      §2.5 of the main text argues for on interpretability grounds alone.
    </div>

    <h3>Where the error lives</h3>
    <p>A model can rank well and still score R\u00b2 = \u22122.9. Refitting a single affine map,
      <em>a</em> + <em>b</em>&#183;prediction, on each target separates the two failures: two
      parameters cannot create rank information, so whatever is recovered was already present in
      the ordering and was lost to scale and offset alone.</p>

    {fig(9, 'figS9_calibration',
         'The model fine-tuned on 9338 literature MIC values, applied to two independently '
         'measured collections. <strong>Left and centre:</strong> predicted against measured '
         'log\u2082 MIC, identity dashed and the fitted line solid; almost every compound sits '
         'above identity. <strong>Right:</strong> R\u00b2 as predicted, and after refitting an '
         'intercept and a slope.')}

    <div class="tbl-wrap">
    <table>
      <caption><span class="fig-n">Table S8.</span> Calibration of the model fine-tuned on 9338
        MIC values, averaged over three seeds.</caption>
      <thead><tr><th>Target</th><th class="num">R\u00b2 raw</th><th class="num">R\u00b2 recalibrated</th>
        <th class="num">Pearson r</th><th class="num">Slope</th>
        <th class="num">Offset, log\u2082</th><th class="num">Fold error</th></tr></thead>
      <tbody>
{ft_table3()}
      </tbody>
    </table>
    </div>

    <p>On the out-of-domain compounds the fitted slope is 0.98 — the scale is already correct —
      and the whole error is an offset of +2.8 log\u2082 units, a seven-fold systematic
      overestimate of MIC; recalibration lifts R\u00b2 from \u22122.92 to +0.49. On Q-HERO the
      slope is 0.47, so the model additionally compresses the range, and recalibration gives
      +0.36 in place of \u22121.62. A model trained on literature MIC pooled across hundreds of
      strains and dozens of protocols learns the correct ordering of compounds and the wrong
      absolute scale for any single new assay. QAC-105 is the exception: rank agreement there is
      weak (\u03c1 \u2248 0.18) and recalibration recovers almost nothing, consistent with it
      being the narrowest and most structurally homogeneous of the three sets.</p>
  </section>

  <section id="s9">
    <h2><span class="sn">S9</span> Data and code</h2>
    <p>The quantitative corpus is deposited as <strong>QAC-AMR</strong> at Zenodo,
      <a href="https://doi.org/10.5281/zenodo.22286669">10.5281/zenodo.22286669</a> (CC BY 4.0): 13 404 activity
      records over 1515 canonical structures and 371 normalised strains, compiled from 103 publications spanning
      2003–2026.</p>
    <p>The expert annotation set, the trained encoders, the analysis scripts that generate every figure and
      table above, and the audit they belong to are available at
      <a href="https://github.com/Yagr49/QMC-Expert">github.com/Yagr49/QMC-Expert</a>.</p>

    <h3>Scripts behind each item</h3>
    <ul>
      <li><code>expert_labels/expert_labels_1103.csv</code> — the canonicalised annotation set (§S1, Figure S1).</li>
      <li><code>reproducibility/leakage_check.py</code> — set intersections (§S2, Figure S2).</li>
      <li><code>reproducibility/qhero_benchmark.py</code> — external benchmark (§S3, Figures S3–S4, Table S1).</li>
      <li><code>reproducibility/causal_check.py</code> — out-of-domain residuals and equivalence tests (§S4, Figure S5, Table S2).</li>
      <li><code>reproducibility/rebuild_table2_multiseed.py</code> — in-domain split comparison (§S5).</li>
      <li><code>reproducibility/finetune/data_prep.py</code> — builds the fine-tuning sources with every evaluation molecule held out (§S7).</li>
      <li><code>reproducibility/finetune/run_matrix.py</code> — representation quality (§S7, Figure S7, Table S5).</li>
      <li><code>reproducibility/finetune/direct_inference.py</code> — zero-shot inference (§S8, Figure S8, Tables S6–S7).</li>
      <li><code>reproducibility/finetune/recalibrate.py</code> — calibration analysis (§S8, Figure S9, Table S8).</li>
      <li><code>reproducibility/make_si_figures.py</code>, <code>make_ft_figures.py</code> — all figures in this document.</li>
    </ul>
  </section>

  <footer>
    Figures rendered from the released result files; every value in this document is reproducible from the
    scripts listed in §S9. Vector versions of all figures are in <code>reproducibility/figures/</code> as SVG
    and PDF.
  </footer>

</div>
'''

open(OUT, 'w', encoding='utf-8').write(PAGE)
print('wrote', OUT, os.path.getsize(OUT), 'bytes | table2 included:', HAS_T2)
