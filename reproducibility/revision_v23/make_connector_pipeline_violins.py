"""Section 2.2 pipeline schematic in the Figure 1 layout and font, pastel palette of v24,
with real results drawn as violins in the three chart slots.

Unit of each violin: one (compound, endpoint) pair, its absolute error in log2 units
averaged over the seeds in which that compound was evaluated
(connector_pipeline_residuals.csv, from compute_connector_pipeline.py).

    python make_connector_pipeline_violins.py [split] [paired] [pooled]
"""
from pathlib import Path
import os, sys
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
OUT = ROOT / 'figures'
FONT_TTF = ROOT / 'FuturaMedium.ttf'

# pastel palette sampled from v24 Figure 3; text tones deepened for legibility
INK, MUTED, BAR = '#1B1C1F', '#6E6A73', '#64676D'
BLUE = dict(fill='#ABC8DF', edge='#8FB2D1', text='#3D6B92', tint='#F2F7FB')
PEACH = dict(fill='#ECC6AA', edge='#DDAE8C', text='#A8683A', tint='#FCF4EE')
LAV = dict(edge='#C9BCDD', text='#5E4D86')
GREY = dict(fill='#DCDCE1', edge='#BDBDC4')
EP = ['S. aureus MIC', 'S. aureus MBC', 'E. coli MIC', 'E. coli MBC']
EP_LAB = ['Sa\nMIC', 'Sa\nMBC', 'Ec\nMIC', 'Ec\nMBC']
YLIM = None   # set from the data in main()


def setup_font():
    font_manager.fontManager.addfont(str(FONT_TTF))
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=str(FONT_TTF)).get_name(),
                         'font.size': 8, 'text.color': INK, 'pdf.fonttype': 42, 'svg.fonttype': 'path',
                         'axes.edgecolor': '#B9B6BE', 'xtick.color': MUTED, 'ytick.color': MUTED})


def box(fig, x0, y0, x1, y1, text, tc, ec, fc='white', fs=8.6, sub=None):
    fig.patches.append(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, transform=fig.transFigure,
                                      boxstyle='round,pad=0,rounding_size=0.012', fc=fc, ec=ec, lw=1.4, zorder=2))
    cy = (y0 + y1) / 2 + (0.012 if sub else 0)
    fig.text((x0 + x1) / 2, cy, text, ha='center', va='center', fontsize=fs, color=tc, linespacing=1.18, zorder=3)
    if sub:
        fig.text((x0 + x1) / 2, cy - 0.034, sub, ha='center', va='center', fontsize=6.6, color=MUTED, zorder=3)


def arrow(fig, a, b):
    fig.patches.append(FancyArrowPatch(a, b, transform=fig.transFigure, arrowstyle='-|>', mutation_scale=8,
                                       lw=1.0, color='#3A3B40', zorder=4, shrinkA=0, shrinkB=0))


def violin(ax, x, v, width, side, col, bw=.35):
    """side: -1 left half, +1 right half, 0 full. Clipped to the observed range."""
    v = np.asarray(v); grid = np.linspace(v.min(), v.max(), 200)
    dens = gaussian_kde(v, bw_method=bw)(grid); dens = dens / dens.max() * width / 2
    if side == 0:
        xs = np.concatenate([x - dens, (x + dens)[::-1]])
    else:
        xs = np.concatenate([np.full_like(grid, x), (x + side * dens)[::-1]])
    ax.fill(xs, np.concatenate([grid, grid[::-1]]), fc=col['fill'], ec=col['edge'], lw=.6, zorder=2)


def summary(ax, x, v, lw=1.6, ms=3.6):
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    ax.plot([x, x], [q1, q3], color=BAR, lw=lw, solid_capstyle='round', zorder=4)
    ax.plot([x], [med], 'o', ms=ms, mfc='white', mec=BAR, mew=.7, zorder=5)


def style_axes(ax, labels, positions, ylabel, yticks, fs=5.8):
    ax.set_ylim(*YLIM)
    ax.set_xticks(positions); ax.set_xticklabels(labels, fontsize=fs, linespacing=1.0)
    ax.tick_params(axis='y', labelsize=6, length=2, pad=1.5); ax.tick_params(axis='x', length=0, pad=2)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_linewidth(.6); ax.spines['bottom'].set_linewidth(.6)
    ax.grid(axis='y', color='#EEEDF1', lw=.5); ax.set_axisbelow(True)
    if not yticks:
        ax.tick_params(axis='y', labelleft=False)
    if ylabel:
        ax.set_ylabel('|error|, log$_2$ units', fontsize=6.4, color=MUTED, labelpad=2)


def chart(fig, rect, res, panel, title, variant, ylabel=False, yticks=True):
    ax = fig.add_axes(rect)
    d = res[res.panel == panel].groupby(['arm', 'compound', 'endpoint']).abs_err.mean().reset_index()
    get = lambda arm, ep=None: d[(d.arm == arm) & ((d.endpoint == ep) if ep else True)].abs_err.values
    base_tick = lambda j, ep, hw: ax.plot([j - hw, j + hw], [np.median(get('mean baseline', ep))] * 2,
                                          ls=(0, (2, 1.6)), lw=.8, color='#A3A0A8', zorder=3)
    if variant == 'split':
        for j, ep in enumerate(EP):
            a, b = get('intuition', ep), get('data', ep)
            violin(ax, j, a, .88, -1, BLUE); violin(ax, j, b, .88, +1, PEACH)
            summary(ax, j - .1, a, lw=1.3, ms=3.0); summary(ax, j + .1, b, lw=1.3, ms=3.0)
            base_tick(j, ep, .42)
        ax.set_xlim(-.6, 3.6); style_axes(ax, EP_LAB, range(4), ylabel, yticks)
    elif variant == 'paired':
        for j, ep in enumerate(EP):
            for k, (arm, col) in enumerate([('intuition', BLUE), ('data', PEACH)]):
                x = j + (k - .5) * .42; v = get(arm, ep)
                violin(ax, x, v, .38, 0, col); summary(ax, x, v, lw=1.1, ms=2.6)
            base_tick(j, ep, .45)
        ax.set_xlim(-.6, 3.6); style_axes(ax, EP_LAB, range(4), ylabel, yticks)
    else:
        for k, (arm, col) in enumerate([('intuition', BLUE), ('data', PEACH), ('mean baseline', GREY)]):
            v = get(arm); violin(ax, k, v, .8, 0, col); summary(ax, k, v)
        ax.set_xlim(-.6, 2.6)
        style_axes(ax, ['Intuition', 'Data', 'Mean\nbaseline'], range(3), ylabel, yticks, fs=6.0)
    n = len(get('intuition'))
    fig.text(rect[0] + rect[2] / 2, rect[1] + rect[3] + .012, f'{title}\nn = {n}',
             ha='center', va='bottom', fontsize=6.8, color=INK, linespacing=1.2)


def main(variant):
    global YLIM
    OUT.mkdir(exist_ok=True); setup_font()
    res = pd.read_csv(ROOT / 'connector_pipeline_residuals.csv')
    top = res.groupby(['panel', 'arm', 'compound', 'endpoint']).abs_err.mean().max()
    YLIM = (0, float(np.ceil(top + .2)))
    fig = plt.figure(figsize=(180 / 25.4, 122 / 25.4), facecolor='white')
    TOP, BOT = (.765, .905), (.105, .245)
    box(fig, .0, TOP[0], .13, TOP[1], '1,103\nexpert Good/Bad\nlabels', LAV['text'], LAV['edge'], fs=7.3)
    box(fig, .16, TOP[0], .285, TOP[1], 'Connector\npretrained for\nclassification', BLUE['text'], BLUE['edge'])
    box(fig, .325, TOP[0], .60, TOP[1], 'Trained intuition-based model', BLUE['text'], BLUE['edge'], BLUE['tint'],
        fs=9, sub='frozen connector + multitask CatBoost')
    box(fig, .645, TOP[0], .92, TOP[1], 'Post-trained intuition-based model', BLUE['text'], BLUE['edge'], BLUE['tint'],
        fs=9, sub='refitted with 6 out-of-domain compounds')
    box(fig, .0, BOT[0], .13, BOT[1], '9,977\nmeasured activity\nrecords', LAV['text'], LAV['edge'], fs=7.3)
    box(fig, .16, BOT[0], .285, BOT[1], 'Connector\npretrained for\nregression', PEACH['text'], PEACH['edge'])
    box(fig, .325, BOT[0], .60, BOT[1], 'Trained data-based model', PEACH['text'], PEACH['edge'], PEACH['tint'],
        fs=9, sub='frozen connector + multitask CatBoost')
    box(fig, .645, BOT[0], .92, BOT[1], 'Post-trained data-based model', PEACH['text'], PEACH['edge'], PEACH['tint'],
        fs=9, sub='refitted with 6 out-of-domain compounds')
    box(fig, .03, .44, .235, .56, '80 compounds training\nsubset from earlier-\nwork database', LAV['text'], LAV['edge'], fs=8.2)
    box(fig, .635, .44, .80, .56, '6 compounds\ntraining subset of\nout-of-domain\nmolecules', LAV['text'], LAV['edge'], fs=7.3)
    for y in ((TOP[0] + TOP[1]) / 2, (BOT[0] + BOT[1]) / 2):
        arrow(fig, (.133, y), (.157, y)); arrow(fig, (.29, y), (.32, y)); arrow(fig, (.605, y), (.64, y))
    arrow(fig, (.19, .565), (.322, .76)); arrow(fig, (.19, .435), (.322, .25))
    arrow(fig, (.7175, .565), (.7175, .76)); arrow(fig, (.7175, .435), (.7175, .25))
    c1 = [.355, .37, .118, .255]; c2 = [.49, .37, .118, .255]; c3 = [.85, .37, .135, .255]
    chart(fig, c1, res, 'in-domain test', 'In-domain test', variant, ylabel=True)
    chart(fig, c2, res, 'out-of-domain zero-shot', 'OOD, zero-shot', variant, yticks=False)
    chart(fig, c3, res, 'out-of-domain post-trained', 'OOD, post-trained', variant)
    for c in (c1, c2, c3):
        x = c[0] + c[2] / 2
        arrow(fig, (x, TOP[0] - .005), (x, .712)); arrow(fig, (x, BOT[1] + .005), (x, .305))
    handles = [Patch(fc=BLUE['fill'], ec=BLUE['edge'], lw=.7, label='Intuition-based'),
               Patch(fc=PEACH['fill'], ec=PEACH['edge'], lw=.7, label='Data-based')]
    handles.append(Patch(fc=GREY['fill'], ec=GREY['edge'], lw=.7, label='Predict-the-mean') if variant == 'pooled'
                   else Line2D([], [], ls=(0, (2, 1.6)), lw=1, color='#A3A0A8', label='Predict-the-mean (median)'))
    handles.append(Line2D([], [], marker='o', ls='-', lw=1.4, color=BAR, mfc='white', mec=BAR, ms=4,
                          label='median, interquartile range'))
    fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(.005, .028), ncol=4, frameon=False,
               fontsize=7.2, handlelength=1.6, handletextpad=.5, columnspacing=1.5)
    lead = ('four endpoints pooled' if variant == 'pooled'
            else 'Sa = S. aureus ATCC 43300, Ec = E. coli ATCC 25922')
    fig.text(.007, .008, lead + ' · absolute error of log$_2$ MIC/MBC (mg/L) per compound and endpoint '
             '(n = compound × endpoint pairs), averaged over 20 random splits',
             ha='left', va='center', fontsize=6.4, color=MUTED)
    name = f'figure_connector_pipeline_violin_{variant}'
    for ext, kw in [('pdf', {}), ('svg', {}), ('png', dict(dpi=600))]:
        fig.savefig(OUT / f'{name}.{ext}', facecolor='white', bbox_inches='tight', pad_inches=.05, **kw)
    plt.close(fig); print('saved', name)


if __name__ == '__main__':
    for v in (sys.argv[1:] or ['split', 'paired', 'pooled']):
        main(v)
