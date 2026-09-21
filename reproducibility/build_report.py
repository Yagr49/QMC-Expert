#!/usr/bin/env python
"""Assemble the fine-tuning results report, inlining the matplotlib SVGs."""
import re, os, json
import numpy as np, pandas as pd

C = '/Users/egorilin/Desktop/COMA'
FT = f'{C}/reproducibility/finetune'
F = f'{C}/reproducibility/figures'
OUT = '/private/tmp/claude-501/-Users-egorilin-Desktop-COMA/990d2f42-4236-4501-b9e0-fecccb0c4e55/scratchpad/ft_report.html'
T = ['QAC-105', 'Q-HERO', 'OOD-17']


def svg(name):
    s = open(f'{F}/{name}.svg', encoding='utf-8').read()
    s = s[s.index('<svg'):]
    s = re.sub(r'<svg([^>]*?)\swidth="[^"]*"', r'\g<0>', s, count=0)
    s = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1', s, count=1)
    s = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1', s, count=1)
    return s.replace('<svg', '<svg preserveAspectRatio="xMidYMid meet"', 1)


def fig(n, name, cap):
    return (f'<figure class="fig"><div class="plate">{svg(name)}</div>'
            f'<figcaption><span class="fn">Figure {n}.</span> {cap}</figcaption></figure>')


r1 = pd.DataFrame([json.loads(l) for l in open(f'{FT}/runs.jsonl')])
r2 = pd.DataFrame([json.loads(l) for l in open(f'{FT}/runs_direct.jsonl')])
rc = pd.read_csv(f'{FT}/recalibration.csv')


def cell(v, s=None, d=3, sign=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '<td class="n dim">·</td>'
    txt = f'{v:+.{d}f}' if sign else f'{v:.{d}f}'
    sd = '' if (s is None or np.isnan(s)) else f' <span class="sd">± {s:.2f}</span>'
    return f'<td class="n">{txt}{sd}</td>'


def table1():
    order = [('predict-the-mean', 'null baseline'), ('6 descriptors', 'null baseline'),
             ('MolFormer frozen', 'no fine-tuning'),
             ('FT expert-binary', 'fine-tuned · 740 binary labels'),
             ('FT quant-molecule', 'fine-tuned · 1153 MIC values'),
             ('FT quant-record', 'fine-tuned · 9338 MIC values')]
    rows = []
    best = {t: r1[r1.target == t].groupby('representation').R2.mean().max() for t in T}
    for name, proto in order:
        cells = ''
        for t in T:
            sub = r1[(r1.representation == name) & (r1.target == t)]
            if not len(sub):
                cells += '<td class="n dim">·</td>'; continue
            m, s = sub.R2.mean(), (sub.R2.std() if len(sub) > 1 else np.nan)
            mark = ' best' if abs(m - best[t]) < 1e-9 else ''
            sd = '' if np.isnan(s) else f' <span class="sd">± {s:.2f}</span>'
            cells += f'<td class="n{mark}">{m:+.3f}{sd}</td>'
        rows.append(f'<tr><td>{name}</td><td class="dim">{proto}</td>{cells}</tr>')
    return '\n'.join(rows)


def table2(metric, d=3):
    lbl = {'FT expert-binary (direct)': ('740 binary expert labels', 0),
           'FT quant-molecule (direct)': ('1153 MIC values', 1),
           'FT quant-record (direct)': ('9338 MIC values', 2),
           'frozen MolFormer + CatBoost': ('not fine-tuned', 3),
           'predict source mean': ('null baseline', 4)}
    sub = r2[r2[metric].notna()]
    keys = sorted(sub.groupby(['representation', 'source']).groups.keys(),
                  key=lambda k: (lbl.get(k[0], ('', 9))[1], k[1]))
    best = {t: sub[sub.target == t].groupby(['representation', 'source'])[metric].mean().max() for t in T}
    rows = []
    for rep, src in keys:
        cells = ''
        for t in T:
            s = sub[(sub.representation == rep) & (sub.source == src) & (sub.target == t)]
            if not len(s):
                cells += '<td class="n dim">·</td>'; continue
            m, sd_ = s[metric].mean(), (s[metric].std() if len(s) > 1 else np.nan)
            mark = ' best' if abs(m - best[t]) < 1e-9 else ''
            sdt = '' if np.isnan(sd_) else f' <span class="sd">± {sd_:.2f}</span>'
            cells += f'<td class="n{mark}">{m:+.{d}f}{sdt}</td>'
        nm = rep.replace(' (direct)', '')
        note = lbl.get(rep, ('', 9))[0]
        if rep in ('frozen MolFormer + CatBoost', 'predict source mean'):
            note = f'{note} · {src}'
        rows.append(f'<tr><td>{nm}</td><td class="dim">{note}</td>{cells}</tr>')
    return '\n'.join(rows)


def table3():
    g = rc[rc.source == 'quant-record'].groupby('target')[
        ['raw_R2', 'recal_R2', 'pearson', 'slope', 'pred_mean', 'true_mean']].mean().reindex(T)
    rows = []
    for t in T:
        r = g.loc[t]
        off = r.pred_mean - r.true_mean
        rows.append(
            f'<tr><td>{t}</td>'
            f'<td class="n">{r.raw_R2:+.2f}</td><td class="n best">{r.recal_R2:+.2f}</td>'
            f'<td class="n">{r.pearson:.2f}</td><td class="n">{r.slope:.2f}</td>'
            f'<td class="n">{off:+.2f}</td><td class="n">{2**off:.1f}×</td></tr>')
    return '\n'.join(rows)


PAGE = f'''<title>Fine-Tuning Verdict</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
  :root {{
    --paper:#fbfaf7; --plate:#ffffff; --ink:#15171b; --ink2:#474d57; --muted:#878d97;
    --rule:#e2e2dc; --rule-soft:#eeeee8; --accent:#2a78d6;
    --good:#0f7a52; --good-bg:#e9f5ef; --flag:#a8410f; --flag-bg:#fbf0e8;
    --serif:"Source Serif 4","Iowan Old Style",Georgia,serif;
    --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    --measure:40rem; --wide:62rem;
  }}
  @media (prefers-color-scheme:dark) {{ :root:not([data-theme="light"]) {{
    --paper:#14151a; --plate:#ffffff; --ink:#eceef2; --ink2:#a9b0bb; --muted:#79808b;
    --rule:#2b2e36; --rule-soft:#21242b; --accent:#6aa6ef;
    --good:#4ecb9a; --good-bg:#12291f; --flag:#e09268; --flag-bg:#2a1d15;
  }}}}
  :root[data-theme="dark"] {{
    --paper:#14151a; --plate:#ffffff; --ink:#eceef2; --ink2:#a9b0bb; --muted:#79808b;
    --rule:#2b2e36; --rule-soft:#21242b; --accent:#6aa6ef;
    --good:#4ecb9a; --good-bg:#12291f; --flag:#e09268; --flag-bg:#2a1d15;
  }}
  body {{ background:var(--paper); color:var(--ink); font-family:var(--serif);
         font-size:17px; line-height:1.62; -webkit-font-smoothing:antialiased; }}
  .sheet {{ max-width:var(--wide); margin:0 auto; padding-inline:20px;
            padding-block:3.5rem 5rem; display:flex; flex-direction:column; gap:3rem; }}
  .mast {{ display:flex; flex-direction:column; gap:.85rem; }}
  .eyebrow {{ font-family:var(--mono); font-size:.7rem; font-weight:500; letter-spacing:.14em;
              text-transform:uppercase; color:var(--accent); }}
  h1 {{ font-size:clamp(1.9rem,1.35rem + 2.1vw,2.7rem); line-height:1.12; font-weight:700;
        margin:0; text-wrap:balance; letter-spacing:-.012em; }}
  .lede {{ font-size:1.06rem; color:var(--ink2); max-width:var(--measure); margin:0; }}
  .meta {{ display:flex; flex-wrap:wrap; gap:.4rem 1.6rem; font-family:var(--mono);
           font-size:.73rem; color:var(--muted); border-top:1px solid var(--rule);
           padding-top:.9rem; margin-top:.3rem; }}
  .meta b {{ color:var(--ink2); font-weight:500; }}
  section {{ display:flex; flex-direction:column; gap:1.1rem; }}
  h2 {{ font-size:1.3rem; font-weight:600; margin:0; letter-spacing:-.005em;
        display:flex; gap:.7rem; align-items:baseline; text-wrap:balance; }}
  h2 .sn {{ font-family:var(--mono); font-size:.76rem; font-weight:600; color:var(--accent);
            flex:none; padding-top:.12rem; }}
  h3 {{ font-family:var(--mono); font-size:.75rem; font-weight:600; letter-spacing:.1em;
        text-transform:uppercase; color:var(--ink2); margin:.5rem 0 0; }}
  p {{ margin:0; max-width:var(--measure); }}
  strong {{ font-weight:600; }}
  code {{ font-family:var(--mono); font-size:.86em; }}
  a {{ color:var(--accent); text-underline-offset:.18em; }}
  ul {{ margin:0; padding-left:1.15rem; max-width:var(--measure);
        display:flex; flex-direction:column; gap:.4rem; }}
  li::marker {{ color:var(--muted); }}
  .fig {{ margin:.5rem 0 0; display:flex; flex-direction:column; gap:.8rem; }}
  .plate {{ background:var(--plate); border:1px solid var(--rule); border-radius:3px;
            padding:14px 10px; overflow-x:auto; }}
  .plate svg {{ display:block; width:100%; height:auto; min-width:540px; }}
  figcaption {{ font-size:.87rem; line-height:1.58; color:var(--ink2); max-width:var(--wide); }}
  .fn {{ font-family:var(--mono); font-size:.77rem; font-weight:600; color:var(--ink); }}
  .tw {{ overflow-x:auto; margin-top:.3rem; }}
  table {{ border-collapse:collapse; width:100%; min-width:560px; font-size:.845rem;
           font-variant-numeric:tabular-nums; }}
  caption {{ caption-side:top; text-align:left; font-size:.87rem; color:var(--ink2);
             padding-bottom:.7rem; line-height:1.55; }}
  th,td {{ padding:.45rem .7rem; text-align:left; border-bottom:1px solid var(--rule-soft); }}
  thead th {{ font-family:var(--mono); font-size:.69rem; font-weight:600; letter-spacing:.05em;
              text-transform:uppercase; color:var(--muted); border-bottom:1px solid var(--rule);
              white-space:nowrap; }}
  tbody tr:last-child td {{ border-bottom:1px solid var(--rule); }}
  td.n, th.n {{ text-align:right; font-family:var(--mono); font-size:.8rem; white-space:nowrap; }}
  .sd {{ color:var(--muted); font-size:.92em; }}
  td.best {{ color:var(--accent); font-weight:600; }}
  td.dim, .dim {{ color:var(--muted); }}
  .box {{ padding:.9rem 1.1rem; max-width:var(--measure); font-size:.93rem; line-height:1.56;
          border-left:2px solid var(--accent); background:color-mix(in srgb,var(--accent) 7%,transparent); }}
  .box.good {{ border-left-color:var(--good); background:var(--good-bg); }}
  .box.flag {{ border-left-color:var(--flag); background:var(--flag-bg); }}
  .box .h {{ font-family:var(--mono); font-size:.67rem; font-weight:600; letter-spacing:.11em;
             text-transform:uppercase; display:block; margin-bottom:.3rem; color:var(--accent); }}
  .box.good .h {{ color:var(--good); }} .box.flag .h {{ color:var(--flag); }}
  .keys {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:0;
           border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); }}
  .keys div {{ padding:.85rem 1rem .85rem 0; }}
  .keys .k {{ font-family:var(--mono); font-size:.67rem; letter-spacing:.09em;
              text-transform:uppercase; color:var(--muted); display:block; margin-bottom:.2rem; }}
  .keys .v {{ font-size:1.4rem; font-weight:600; letter-spacing:-.015em;
              font-variant-numeric:tabular-nums; }}
  .keys .v small {{ font-size:.78rem; font-weight:400; color:var(--ink2); letter-spacing:0; }}
  footer {{ border-top:1px solid var(--rule); padding-top:1.2rem; font-family:var(--mono);
            font-size:.73rem; color:var(--muted); line-height:1.7; max-width:var(--wide); }}
  @media (max-width:560px) {{ body {{ font-size:16px; }} h2 {{ flex-direction:column; gap:.2rem; }}
    .sheet {{ gap:2.4rem; padding-block:2.5rem 3.5rem; }} }}
  @media (prefers-reduced-motion:reduce) {{ * {{ animation:none!important; transition:none!important; }} }}
</style>

<div class="sheet">

<header class="mast">
  <span class="eyebrow">QMC-Expert · fine-tuning results</span>
  <h1>Ranking transfers, absolute MIC does not</h1>
  <p class="lede">Two experiments on MolFormer for quaternary ammonium biocides: whether
    end-to-end fine-tuning beats the frozen encoder, and whether 740 binary expert
    judgements match 9338 quantitative measurements. Every evaluation molecule is held out
    of every training source.</p>
  <div class="meta">
    <span><b>Backbone</b> MolFormer-XL, 44.4 M params</span>
    <span><b>Seeds</b> 3</span>
    <span><b>Held out</b> 532 molecules</span>
    <span><b>Compute</b> 137 min + 92 min, Apple M4 Pro</span>
  </div>
</header>

<section>
  <h2><span class="sn">1</span> What changed</h2>
  <p>An earlier analysis of the frozen-encoder setup found that the contrastive encoders were
    indistinguishable from raw MolFormer, and concluded that expert supervision added nothing.
    That conclusion was an artefact of the frozen design. When the backbone is allowed to move,
    the picture changes on all three targets.</p>

  <div class="keys">
    <div><span class="k">Q-HERO, frozen</span><span class="v">+0.13</span></div>
    <div><span class="k">Q-HERO, fine-tuned</span><span class="v" style="color:var(--accent)">+0.31</span></div>
    <div><span class="k">Expert labels</span><span class="v">740</span></div>
    <div><span class="k">Quantitative values</span><span class="v">9338<small> &nbsp;12.6×</small></span></div>
  </div>

  <div class="box good">
    <span class="h">Headline</span>
    Fine-tuning roughly doubles variance explained on the external benchmark and lifts every
    target above its frozen baseline. Under that fairer setup, <strong>740 binary expert
    judgements match a 12.6× larger corpus of quantitative measurements</strong> — the
    manuscript's central claim, now measured without contamination and against explicit null
    baselines.
  </div>
</section>

<section>
  <h2><span class="sn">2</span> Does fine-tuning help?</h2>
  <p>Each representation feeds a CatBoost regressor fitted on target-domain data — QAC-105 and
    Q-HERO under scaffold-grouped five-fold CV, OOD-17 predicted from a model trained on
    QAC-105. This measures the quality of the representation, not inference.</p>

  {fig(1, 'figS7_representation_quality',
       'Variance explained by each representation, mean ± sd over three seeds. Every '
       'fine-tuned model beats the frozen encoder on every target, and both null baselines '
       'sit at or below zero. Absolute values stay low: Q-HERO is the only target where any '
       'representation clears R² = 0.1.')}

  <div class="tw"><table>
    <caption><span class="fn">Table 1.</span> Representation quality, R² (mean ± sd, 3 seeds).
      Best per target marked.</caption>
    <thead><tr><th>Representation</th><th>Supervision</th>
      <th class="n">QAC-105</th><th class="n">Q-HERO</th><th class="n">OOD-17</th></tr></thead>
    <tbody>
{table1()}
    </tbody>
  </table></div>

  <p>Two readings follow. Fine-tuning is worth doing — the frozen bottleneck was suppressing
    whatever the supervision contributed, which is why the earlier comparison came out flat.
    And the supervision sources are close: the expert arm leads on QAC-105, the quantitative
    arms lead on Q-HERO and OOD-17, and no gap exceeds roughly one standard deviation across
    seeds.</p>
</section>

<section>
  <h2><span class="sn">3</span> Zero-shot inference</h2>
  <p>Here the fine-tuned head predicts the targets itself, with nothing fitted on the target
    domain. The quantitative sources and all three targets are log₂ MIC in µM, so regression
    transfers directly. The expert head emits a Good/Bad logit instead, so both arms are scored
    on rank agreement with the true MIC (Spearman, signed so positive is correct for either)
    and on ROC-AUC against MIC split at the target's median.</p>

  {fig(2, 'figS8_zeroshot',
       'Zero-shot transfer. <strong>Left:</strong> rank agreement with the true MIC is strong '
       'and grows with the amount of supervision — on OOD-17 the model trained on 9338 values '
       'reaches ρ = 0.75. <strong>Right:</strong> the R² of those same predictions is deeply '
       'negative on every target. The ordering is right; the numbers are not.')}

  <div class="tw"><table>
    <caption><span class="fn">Table 2.</span> Rank agreement with true log₂ MIC (Spearman ρ,
      signed so that positive is correct for both arms).</caption>
    <thead><tr><th>Model</th><th>Supervision</th>
      <th class="n">QAC-105</th><th class="n">Q-HERO</th><th class="n">OOD-17</th></tr></thead>
    <tbody>
{table2('rank_agreement')}
    </tbody>
  </table></div>

  <div class="tw"><table>
    <caption><span class="fn">Table 3.</span> ROC-AUC against MIC binarised at each target's
      median. Chance is 0.500.</caption>
    <thead><tr><th>Model</th><th>Supervision</th>
      <th class="n">QAC-105</th><th class="n">Q-HERO</th><th class="n">OOD-17</th></tr></thead>
    <tbody>
{table2('AUC')}
    </tbody>
  </table></div>

  <div class="box">
    <span class="h">A model that never saw a MIC value</span>
    The expert arm was fine-tuned only on Good/Bad judgements and has no notion of a
    concentration. It nonetheless ranks unseen compounds by MIC at ρ = 0.22 / 0.40 / 0.30 and
    separates above- from below-median actives at AUC 0.64 / 0.69 / 0.60. That is direct
    evidence that a coarse human call carries quantitatively relevant information — the claim
    the manuscript makes but does not currently demonstrate.
  </div>
</section>

<section>
  <h2><span class="sn">4</span> Why the numbers are wrong</h2>
  <p>A model can rank well and still score R² = −2.9. Refitting a single affine map,
    <code>a + b·prediction</code>, on each target separates the two failures. Two parameters
    cannot invent rank information, so whatever R² returns was already in the ordering and was
    lost to scale and offset alone.</p>

  {fig(3, 'figS9_calibration',
       'The model fine-tuned on 9338 literature MIC values, applied to two independently '
       'measured collections. <strong>Left and centre:</strong> predicted against true log₂ MIC, '
       'with the identity line dashed and the fitted line solid. Almost every compound sits '
       'above identity — the model overestimates MIC systematically. <strong>Right:</strong> R² '
       'as predicted, and after refitting an intercept and a slope.')}

  <div class="tw"><table>
    <caption><span class="fn">Table 4.</span> Calibration of the model fine-tuned on 9338 MIC
      values, averaged over three seeds.</caption>
    <thead><tr><th>Target</th><th class="n">R² raw</th><th class="n">R² recalibrated</th>
      <th class="n">Pearson r</th><th class="n">Slope</th>
      <th class="n">Offset, log₂</th><th class="n">Fold error</th></tr></thead>
    <tbody>
{table3()}
    </tbody>
  </table></div>

  <div class="box flag">
    <span class="h">The mechanism</span>
    On OOD-17 the fitted slope is 0.98 — the scale is already correct — and the entire error is
    an offset of +2.8 log₂ units, a <strong>7-fold systematic overestimate of MIC</strong>.
    Recalibrating recovers R² = +0.49 from −2.92. On Q-HERO the slope is 0.47, so the model also
    compresses the range, and recalibration recovers +0.36 from −1.62. A model trained on
    literature MIC pooled across hundreds of strains and dozens of protocols learns the right
    ordering of compounds and the wrong absolute scale for any single new assay.
  </div>

  <p>QAC-105 is the exception: rank agreement is weak there (ρ ≈ 0.18) and recalibration
    recovers almost nothing, which is consistent with it being the narrowest and most
    structurally homogeneous of the three sets.</p>
</section>

<section>
  <h2><span class="sn">5</span> What this means for the manuscript</h2>

  <h3>Claims that now hold</h3>
  <ul>
    <li><strong>Binary expert labels rival quantitative measurement.</strong> 740 human calls
      match 9338 measured values on representation quality, with eval molecules held out and
      null baselines in the table.</li>
    <li><strong>Human judgement carries quantitative signal.</strong> A head trained only on
      Good/Bad ranks unseen compounds by MIC well above chance without ever seeing a
      concentration.</li>
    <li><strong>Protocol heterogeneity is the binding constraint.</strong> Stated as motivation
      in the introduction, it is now a measured result: rank transfers across collections,
      absolute MIC does not.</li>
  </ul>

  <h3>Claims that need rewriting</h3>
  <ul>
    <li>Anything resting on the frozen contrastive encoder's advantage over raw MolFormer.
      The advantage appears only under fine-tuning, and the manuscript does not fine-tune.</li>
    <li>Absolute R² on QAC-105 from the original tables. Those came from a split drawn over
      (molecule, endpoint) pairs on a benchmark fully contained in the training set.</li>
    <li>The framing of the model as a predictor of MIC. On independent data it is a
      <em>ranker</em>. Reported as such — with AUC and Spearman rather than R² — the result is
      both defensible and useful for screening.</li>
  </ul>

  <div class="box good">
    <span class="h">Suggested framing</span>
    A molecular foundation model fine-tuned on heterogeneous literature bioactivity data
    transfers its <em>ordering</em> of compounds to independently measured sets (ρ up to 0.75,
    AUC up to 0.87) while its absolute predictions carry a systematic multi-fold offset that two
    calibration points remove. Within that ceiling, 740 binary expert judgements are worth as
    much as 9338 quantitative measurements.
  </div>
</section>

<footer>
  Produced by <code>reproducibility/finetune/run_matrix.py</code>,
  <code>direct_inference.py</code> and <code>recalibrate.py</code>; figures by
  <code>reproducibility/make_ft_figures.py</code>. Protocol: bottom four encoder layers and
  embeddings frozen (16.0 M of 44.4 M parameters), OneCycle at 3e-5, early stopping on a
  scaffold-disjoint 15 % split. Quantitative corpus: QAC-AMR, Zenodo 10.5281/zenodo.22286669.
  Code at github.com/Yagr49/QMC-Expert.
</footer>

</div>
'''

open(OUT, 'w', encoding='utf-8').write(PAGE)
print('wrote', OUT, os.path.getsize(OUT), 'bytes')
