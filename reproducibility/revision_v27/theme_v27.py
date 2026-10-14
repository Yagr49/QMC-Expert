"""Shared look for the v27 figures: Futura Medium and the pastel palette of Figure 5.

Arm colours are fixed here so that one supervision source keeps one colour across every
figure in the manuscript: human mint, quantitative lavender, shuffled human peach,
raw MolFormer grey, and the descriptor reference a muted blue.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', str(Path.home() / '.cache' / 'mpl_coma'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent
FONT_TTF = ROOT / 'FuturaMedium.ttf'
FONT_TTC = '/System/Library/Fonts/Supplemental/Futura.ttc'

INK, MUTED, BAR, RULE = '#1B1C1F', '#6E6A73', '#64676D', '#B9B6BE'
MINT = dict(fill='#A3D6CA', edge='#7FC2B1', text='#2F7F6C', tint='#F1F9F6')
LAV = dict(fill='#C9BCDD', edge='#AF9DCF', text='#5E4D86', tint='#F6F3FA')
PEACH = dict(fill='#ECC6AA', edge='#DDAE8C', text='#A8683A', tint='#FCF4EE')
GREY = dict(fill='#DCDCE1', edge='#BDBDC4', text='#5B5B63', tint='#F6F6F8')
BLUE = dict(fill='#ABC8DF', edge='#8FB2D1', text='#3D6B92', tint='#F2F7FB')
NEUTRAL = dict(edge='#C9C7CF', text='#45424C')

ARM = {'human': MINT, 'CB_human': MINT,
       'quantitative': LAV, 'CB_quantitative': LAV, 'mic_continuous': LAV,
       'shuffled': PEACH, 'CB_shuffled_human': PEACH, 'human_shuffled': PEACH,
       'raw': GREY, 'CB_raw_MolFormer': GREY, 'matched_raw': GREY,
       'descriptors': BLUE, 'RF_35_descriptors': BLUE}


def theme(base=8.0):
    if not FONT_TTF.exists():
        from fontTools.ttLib import TTCollection
        TTCollection(FONT_TTC).fonts[0].save(str(FONT_TTF))
    font_manager.fontManager.addfont(str(FONT_TTF))
    name = font_manager.FontProperties(fname=str(FONT_TTF)).get_name()
    plt.rcParams.update({
        'font.family': name, 'font.size': base, 'text.color': INK,
        'axes.edgecolor': RULE, 'axes.linewidth': .6, 'axes.labelcolor': MUTED,
        'xtick.color': MUTED, 'ytick.color': MUTED,
        'xtick.labelsize': base - 1.6, 'ytick.labelsize': base - 1.6,
        'xtick.major.size': 2.2, 'ytick.major.size': 2.2, 'xtick.major.width': .6,
        'ytick.major.width': .6, 'legend.frameon': False, 'figure.facecolor': 'white',
        'axes.facecolor': 'white', 'grid.color': '#EEEDF1', 'grid.linewidth': .5,
        'pdf.fonttype': 42, 'svg.fonttype': 'path',
        # Futura has no U+2082; render subscripts as scaled Futura digits via mathtext
        'mathtext.fontset': 'custom', 'mathtext.rm': name, 'mathtext.it': name,
        'mathtext.bf': name, 'mathtext.default': 'regular'})
    return name


ARROW = '\u203a'   # Futura has no U+2192; U+203A is its narrow right-pointing form


def despine(ax, grid='y'):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    if grid:
        ax.grid(axis=grid, color='#EEEDF1', lw=.5)
    ax.set_axisbelow(True)


def panel_letter(ax, letter, x=-.14, y=1.06):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=10.5, color=INK, va='bottom')


def violin(ax, x, v, col, width=.78, bw=.35, summary=True):
    """Full violin clipped to the observed range, with median and IQR."""
    from scipy.stats import gaussian_kde
    v = np.asarray(v)
    grid = np.linspace(v.min(), v.max(), 220)
    dens = gaussian_kde(v, bw_method=bw)(grid)
    dens = dens / dens.max() * width / 2
    ax.fill(np.concatenate([x - dens, (x + dens)[::-1]]),
            np.concatenate([grid, grid[::-1]]),
            fc=col['fill'], ec=col['edge'], lw=.6, zorder=2)
    if summary:
        q1, med, q3 = np.percentile(v, [25, 50, 75])
        ax.plot([x, x], [q1, q3], color=BAR, lw=1.6, solid_capstyle='round', zorder=4)
        ax.plot([x], [med], 'o', ms=3.8, mfc='white', mec=BAR, mew=.7, zorder=5)


def save(fig, out_dir, stem, pad=.05):
    out_dir.mkdir(exist_ok=True)
    for ext, kw in [('pdf', {}), ('svg', {}), ('png', dict(dpi=600))]:
        fig.savefig(out_dir / f'{stem}.{ext}', facecolor='white',
                    bbox_inches='tight', pad_inches=pad, **kw)
    plt.close(fig)
    print('saved', stem)
