"""Section 2.2 pipeline schematic, redrawn in the visual language of Figure 1 with real
results in the three chart slots. Layout and topology follow the author's sketch.

Data: connector_pipeline_results.csv (compute_connector_pipeline.py).
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', str(Path.home() / '.cache' / 'mpl_coma'))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
FONT_TTF = ROOT / 'FuturaMedium.ttf'

INK, MUTED = '#141514', '#6E6A73'
BLUE_T, BLUE_E, BLUE_F, BLUE_TINT = '#145B96', '#8FB3DE', '#5B95D3', '#EEF4FB'      # Fig. 1 "Feature selection"
ORNG_T, ORNG_E, ORNG_F, ORNG_TINT = '#B8661A', '#F2C88E', '#F0A447', '#FDF3E6'      # Fig. 1 "Guided embeddings"
PURP_T, PURP_E = '#5B2879', '#B7B2DA'                                                # Fig. 1 "Property" boxes
BASE = '#9A96A0'

EP = ['S. aureus MIC', 'S. aureus MBC', 'E. coli MIC', 'E. coli MBC']
EP_LAB = ['Sa\nMIC', 'Sa\nMBC', 'Ec\nMIC', 'Ec\nMBC']


def setup_font():
    if not FONT_TTF.exists():
        from fontTools.ttLib import TTCollection
        TTCollection('/System/Library/Fonts/Supplemental/Futura.ttc').fonts[0].save(str(FONT_TTF))
    font_manager.fontManager.addfont(str(FONT_TTF))
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=str(FONT_TTF)).get_name(),
                         'font.size': 8, 'text.color': INK, 'pdf.fonttype': 42, 'svg.fonttype': 'path',
                         'axes.edgecolor': '#B9B6BE', 'xtick.color': MUTED, 'ytick.color': MUTED})


def box(fig, x0, y0, x1, y1, text, tc, ec, fc='white', fs=8.6, sub=None):
    fig.patches.append(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, transform=fig.transFigure,
                                      boxstyle='round,pad=0,rounding_size=0.012',
                                      fc=fc, ec=ec, lw=1.3, zorder=2))
    cy = (y0 + y1) / 2 + (0.012 if sub else 0)
    fig.text((x0 + x1) / 2, cy, text, ha='center', va='center', fontsize=fs, color=tc,
             linespacing=1.18, zorder=3)
    if sub:
        fig.text((x0 + x1) / 2, cy - 0.034, sub, ha='center', va='center', fontsize=6.6, color=MUTED, zorder=3)


def arrow(fig, a, b, lw=1.0):
    fig.patches.append(FancyArrowPatch(a, b, transform=fig.transFigure, arrowstyle='-|>',
                                       mutation_scale=8, lw=lw, color=INK, zorder=4,
                                       shrinkA=0, shrinkB=0))


def chart(fig, rect, df, panel, title, ylim, ylabel=False, yticks=True):
    ax = fig.add_axes(rect)
    d = df[df.panel == panel]
    w = .3
    for j, ep in enumerate(EP):
        for k, (arm, fcol, ecol) in enumerate([('intuition', BLUE_F, BLUE_T), ('data', ORNG_F, ORNG_T)]):
            v = d[(d.arm == arm) & (d.endpoint == ep)].rmse.values
            x = j + (k - .5) * (w + .04)
            ax.boxplot(v, positions=[x], widths=w, patch_artist=True, showfliers=False, whis=(5, 95),
                       boxprops=dict(fc=fcol, ec=ecol, lw=.7), medianprops=dict(color='white', lw=1.2),
                       whiskerprops=dict(color=ecol, lw=.7), capprops=dict(color=ecol, lw=.7))
        b = np.median(d[(d.arm == 'mean baseline') & (d.endpoint == ep)].rmse.values)
        ax.plot([j - .42, j + .42], [b, b], ls=(0, (2.2, 1.6)), lw=.9, color=BASE, zorder=1)
    ax.set_xlim(-.6, 3.6); ax.set_ylim(*ylim)
    ax.set_xticks(range(4)); ax.set_xticklabels(EP_LAB, fontsize=5.6, linespacing=1.0)
    ax.tick_params(axis='y', labelsize=6, length=2, pad=1.5); ax.tick_params(axis='x', length=0, pad=2)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_linewidth(.6); ax.spines['bottom'].set_linewidth(.6)
    ax.grid(axis='y', color='#ECEBEF', lw=.5); ax.set_axisbelow(True)
    if not yticks:
        ax.tick_params(axis='y', labelleft=False)
    if ylabel:
        ax.set_ylabel('RMSE, log$_2$ units', fontsize=6.4, color=MUTED, labelpad=2)
    fig.text(rect[0] + rect[2] / 2, rect[1] + rect[3] + .012, title, ha='center', va='bottom',
             fontsize=7.0, color=INK, linespacing=1.15)
    return ax


def main():
    OUT.mkdir(exist_ok=True)
    setup_font()
    df = pd.read_csv(ROOT / 'connector_pipeline_results.csv')
    lo = df.groupby(['panel', 'arm', 'endpoint']).rmse.quantile(.05).min()
    hi = df.groupby(['panel', 'arm', 'endpoint']).rmse.quantile(.95).max()
    ylim = (np.floor(lo * 2) / 2, np.ceil(hi * 2) / 2)

    fig = plt.figure(figsize=(180 / 25.4, 122 / 25.4), facecolor='white')

    TOP, BOT = (.765, .905), (.105, .245)
    # ---- top row: intuition arm
    box(fig, .0, TOP[0], .13, TOP[1], '1,103\nexpert Good/Bad\nlabels', PURP_T, PURP_E, fs=7.3)
    box(fig, .16, TOP[0], .285, TOP[1], 'Connector\npretrained for\nclassification', BLUE_T, BLUE_E)
    box(fig, .325, TOP[0], .60, TOP[1], 'Trained intuition-based model', BLUE_T, BLUE_E, BLUE_TINT, fs=9,
        sub='frozen connector + multitask CatBoost')
    box(fig, .645, TOP[0], .92, TOP[1], 'Post-trained intuition-based model', BLUE_T, BLUE_E, BLUE_TINT, fs=9,
        sub='refitted with 6 out-of-domain compounds')
    # ---- bottom row: data arm
    box(fig, .0, BOT[0], .13, BOT[1], '9,977\nmeasured activity\nrecords', PURP_T, PURP_E, fs=7.3)
    box(fig, .16, BOT[0], .285, BOT[1], 'Connector\npretrained for\nregression', ORNG_T, ORNG_E)
    box(fig, .325, BOT[0], .60, BOT[1], 'Trained data-based model', ORNG_T, ORNG_E, ORNG_TINT, fs=9,
        sub='frozen connector + multitask CatBoost')
    box(fig, .645, BOT[0], .92, BOT[1], 'Post-trained data-based model', ORNG_T, ORNG_E, ORNG_TINT, fs=9,
        sub='refitted with 6 out-of-domain compounds')
    # ---- middle: training subsets
    box(fig, .03, .44, .235, .56, '80 compounds training\nsubset from earlier-\nwork database', PURP_T, PURP_E, fs=8.2)
    box(fig, .635, .44, .80, .56, '6 compounds\ntraining subset of\nout-of-domain\nmolecules', PURP_T, PURP_E, fs=7.3)

    # ---- horizontal flow
    for y in ((TOP[0] + TOP[1]) / 2, (BOT[0] + BOT[1]) / 2):
        arrow(fig, (.133, y), (.157, y)); arrow(fig, (.29, y), (.32, y)); arrow(fig, (.605, y), (.64, y))
    # ---- training subsets feed the trained / post-trained models
    arrow(fig, (.19, .565), (.322, .76)); arrow(fig, (.19, .435), (.322, .25))
    arrow(fig, (.7175, .565), (.7175, .76)); arrow(fig, (.7175, .435), (.7175, .25))

    # ---- charts with real results
    c1 = [.355, .37, .118, .255]; c2 = [.49, .37, .118, .255]; c3 = [.85, .37, .135, .255]
    chart(fig, c1, df, 'in-domain test', 'In-domain test\n25–28 cpds', ylim, ylabel=True)
    chart(fig, c2, df, 'out-of-domain zero-shot', 'OOD, zero-shot\n17 cpds', ylim, yticks=False)
    chart(fig, c3, df, 'out-of-domain post-trained', 'OOD, post-trained\n11 held-back cpds', ylim)
    for c in (c1, c2):
        x = c[0] + c[2] / 2
        arrow(fig, (x, TOP[0] - .005), (x, .705)); arrow(fig, (x, BOT[1] + .005), (x, .305))
    x = c3[0] + c3[2] / 2
    arrow(fig, (x, TOP[0] - .005), (x, .705)); arrow(fig, (x, BOT[1] + .005), (x, .305))

    handles = [Patch(fc=BLUE_F, ec=BLUE_T, lw=.7, label='Intuition-based'),
               Patch(fc=ORNG_F, ec=ORNG_T, lw=.7, label='Data-based'),
               Line2D([], [], ls=(0, (2.2, 1.6)), lw=1, color=BASE, label='Predict-the-mean baseline')]
    fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(.005, .028), ncol=3, frameon=False,
               fontsize=7.4, handlelength=1.6, handletextpad=.5, columnspacing=1.8)
    fig.text(.007, .008, 'Sa = S. aureus ATCC 43300, Ec = E. coli ATCC 25922 · RMSE of log$_2$ MIC/MBC (mg/L), 20 random splits, whiskers 5–95%',
             ha='left', va='center', fontsize=6.4, color=MUTED)

    name = 'figure_connector_pipeline_fig1style'
    for ext, kw in [('pdf', {}), ('svg', {}), ('png', dict(dpi=600)), ('tiff', dict(dpi=600))]:
        fig.savefig(OUT / f'{name}.{ext}', facecolor='white', bbox_inches='tight', pad_inches=.05, **kw)
    plt.close(fig)
    print('saved', name, '| shared y-limits', ylim)


if __name__ == '__main__':
    main()
