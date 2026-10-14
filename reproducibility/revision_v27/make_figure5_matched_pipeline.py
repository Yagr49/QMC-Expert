"""Figure 5 of manuscript v27: matched-supervision design drawn as a pipeline schematic
(Figure 1 layout language, Futura, v24 pastel palette) with the observed error
distributions embedded in place.

Replaces v26 Figures 5 (design) and 6 (violins). Data are unchanged from v26 Figure 6:
revision_v24/figure4_compact_error_values.csv, 420 compound-endpoint mean absolute
errors per arm and holdout scheme. No explanatory text is drawn beneath the figure;
it lives in the caption.
"""
from pathlib import Path
import os, hashlib, json
os.environ.setdefault('MPLCONFIGDIR', str(Path.home() / '.cache' / 'mpl_coma'))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
from matplotlib.lines import Line2D
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / 'revision_v24' / 'figure4_compact_error_values.csv'
OUT = ROOT / 'figures'
FONT_TTF = ROOT / 'FuturaMedium.ttf'

INK, MUTED, BAR = '#1B1C1F', '#6E6A73', '#64676D'
# arm colours match manuscript Figures 6 (Q-HERO) and 8 (OOD): human mint, quantitative
# lavender, shuffled human peach, raw MolFormer grey
MINT = dict(fill='#A3D6CA', edge='#7FC2B1', text='#2F7F6C', tint='#F1F9F6')
LAV = dict(fill='#C9BCDD', edge='#AF9DCF', text='#5E4D86', tint='#F6F3FA')
PEACH = dict(fill='#ECC6AA', edge='#DDAE8C')
GREY = dict(fill='#DCDCE1', edge='#BDBDC4')
NEUTRAL = dict(edge='#C9C7CF', text='#45424C')
ARMS = [('human', MINT, 'Human', 'Human'), ('mic_continuous', LAV, 'Quantitative', 'Quant.'),
        ('human_shuffled', PEACH, 'Shuffled human', 'Shuffled'), ('matched_raw', GREY, 'Raw MolFormer', 'Raw')]


def setup_font():
    font_manager.fontManager.addfont(str(FONT_TTF))
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=str(FONT_TTF)).get_name(),
                         'font.size': 8, 'text.color': INK, 'pdf.fonttype': 42, 'svg.fonttype': 'path',
                         'axes.edgecolor': '#B9B6BE', 'xtick.color': MUTED, 'ytick.color': MUTED})


def box(fig, x0, y0, x1, y1, text, tc, ec, fc='white', fs=8.4, sub=None, dashed=False):
    fig.patches.append(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, transform=fig.transFigure,
                                      boxstyle='round,pad=0,rounding_size=0.012', fc=fc, ec=ec, lw=1.4,
                                      ls=(0, (3, 2)) if dashed else '-', zorder=2))
    cy = (y0 + y1) / 2 + (0.013 if sub else 0)
    fig.text((x0 + x1) / 2, cy, text, ha='center', va='center', fontsize=fs, color=tc, linespacing=1.18, zorder=3)
    if sub:
        fig.text((x0 + x1) / 2, cy - 0.036, sub, ha='center', va='center', fontsize=6.7, color=MUTED, zorder=3)


def arrow(fig, a, b):
    fig.patches.append(FancyArrowPatch(a, b, transform=fig.transFigure, arrowstyle='-|>', mutation_scale=8,
                                       lw=1.0, color='#3A3B40', zorder=4, shrinkA=0, shrinkB=0))


def violin(ax, x, v, col, width=.78, bw=.35):
    grid = np.linspace(v.min(), v.max(), 220)
    dens = gaussian_kde(v, bw_method=bw)(grid); dens = dens / dens.max() * width / 2
    ax.fill(np.concatenate([x - dens, (x + dens)[::-1]]), np.concatenate([grid, grid[::-1]]),
            fc=col['fill'], ec=col['edge'], lw=.6, zorder=2)
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    ax.plot([x, x], [q1, q3], color=BAR, lw=1.6, solid_capstyle='round', zorder=4)
    ax.plot([x], [med], 'o', ms=3.8, mfc='white', mec=BAR, mew=.7, zorder=5)


def chart(fig, rect, d, title, ylim, ylabel):
    ax = fig.add_axes(rect)
    for k, (arm, col, _, _) in enumerate(ARMS):
        violin(ax, k, d[d.arm == arm].mean_absolute_error.to_numpy(), col)
    ax.set_xlim(-.6, len(ARMS) - .4); ax.set_ylim(*ylim)
    ax.set_xticks(range(len(ARMS))); ax.set_xticklabels([a[3] for a in ARMS], fontsize=6.6)
    ax.tick_params(axis='y', labelsize=6.2, length=2, pad=1.5); ax.tick_params(axis='x', length=0, pad=2.5)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_linewidth(.6); ax.spines['bottom'].set_linewidth(.6)
    ax.grid(axis='y', color='#EEEDF1', lw=.5); ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel('|error|, log$_2$(mg/L)', fontsize=6.6, color=MUTED, labelpad=2)
    n = int((d.arm == 'human').sum())
    fig.text(rect[0] + rect[2] / 2, rect[1] + rect[3] + .014, f'{title}\nn = {n}',
             ha='center', va='bottom', fontsize=7.2, color=INK, linespacing=1.2)


def main():
    OUT.mkdir(exist_ok=True); setup_font()
    data = pd.read_csv(SRC)
    assert set(data.arm) == {a[0] for a in ARMS}
    assert (data.groupby(['schema', 'arm']).size() == 420).all()
    top = float(np.ceil(data.mean_absolute_error.max() + .2))

    fig = plt.figure(figsize=(180 / 25.4, 112 / 25.4), facecolor='white')
    TOP, BOT = (.79, .935), (.075, .22)
    box(fig, .0, TOP[0], .14, TOP[1], '681 source\nmolecules\nGood/Bad labels', NEUTRAL['text'], NEUTRAL['edge'], fs=7.4)
    box(fig, .175, TOP[0], .31, TOP[1], 'Compact encoder\ncontrastive,\nGood/Bad', MINT['text'], MINT['edge'], fs=7.8)
    box(fig, .35, TOP[0], .985, TOP[1], 'Human-guided model', MINT['text'], MINT['edge'], MINT['tint'], fs=9.2,
        sub='frozen encoder features + CatBoost with categorical task codes')
    box(fig, .0, BOT[0], .14, BOT[1], '681 source\nmolecules\nmeasured MIC', NEUTRAL['text'], NEUTRAL['edge'], fs=7.4)
    box(fig, .175, BOT[0], .31, BOT[1], 'Compact encoder\nregression,\ncontinuous MIC', LAV['text'], LAV['edge'], fs=7.8)
    box(fig, .35, BOT[0], .985, BOT[1], 'Quantitative-guided model', LAV['text'], LAV['edge'], LAV['tint'], fs=9.2,
        sub='frozen encoder features + CatBoost with categorical task codes')
    box(fig, .02, .425, .255, .585, '105 reference QACs\nS. aureus, E. coli\nMIC and MBC', NEUTRAL['text'], NEUTRAL['edge'], fs=8.0)

    for y in ((TOP[0] + TOP[1]) / 2, (BOT[0] + BOT[1]) / 2):
        arrow(fig, (.143, y), (.172, y)); arrow(fig, (.313, y), (.347, y))
    arrow(fig, (.2, .59), (.347, .785)); arrow(fig, (.2, .42), (.347, .225))

    c1 = [.43, .335, .235, .3]; c2 = [.735, .335, .235, .3]
    for c, schema, title, yl in [(c1, 'cation', 'Cation holdout', True), (c2, 'scaffold', 'Scaffold holdout', False)]:
        chart(fig, c, data[data.schema == schema], title, (0, top), yl)
        x = c[0] + c[2] / 2
        arrow(fig, (x, TOP[0] - .006), (x, .728)); arrow(fig, (x, BOT[1] + .006), (x, .262))

    handles = [Patch(fc=c['fill'], ec=c['edge'], lw=.7, label=l) for _, c, l, _ in ARMS]
    handles.append(Line2D([], [], marker='o', ls='-', lw=1.5, color=BAR, mfc='white', mec=BAR, ms=4,
                          label='median and interquartile range'))
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, -.005), ncol=5, frameon=False,
               fontsize=7.2, handlelength=1.5, handletextpad=.45, columnspacing=1.3)

    name = 'figure5_matched_supervision_pipeline'
    for ext, kw in [('pdf', {}), ('svg', {}), ('png', dict(dpi=600))]:
        fig.savefig(OUT / f'{name}.{ext}', facecolor='white', bbox_inches='tight', pad_inches=.05, **kw)
    plt.close(fig)
    summ = data.groupby(['schema', 'arm']).mean_absolute_error.agg(['median', 'mean']).round(3)
    (ROOT / 'figure5_manifest.json').write_text(json.dumps(dict(
        source=str(SRC.relative_to(ROOT.parent.parent)), source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
        n_per_arm_and_scheme=420, medians={f'{s}/{a}': float(v) for (s, a), v in summ['median'].items()},
        replaces='v26 Figures 5 and 6'), indent=2))
    print('saved', name)


if __name__ == '__main__':
    main()
