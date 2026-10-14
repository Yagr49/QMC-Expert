"""Figure 2 redrawn in the visual language of Figure 1.

Scatter geometry is taken unchanged from the archived vector PDF
(revision_v20/tsne_pdf_marker_coordinates.csv, 221 points per panel); no t-SNE is
recomputed and no point is added, removed or moved. Metrics are the values stated
printed by that same archived run. The archived 'after' panel is a different t-SNE run
from the raster in manuscript v21 (it does not align under any rotation or reflection,
while the 'before' panels coincide), so the silhouette shown is 0.107, the value that run
reported, and the Davies-Bouldin / Calinski-Harabasz values are not drawn because their
run cannot be confirmed.

Style follows Figure 1: Futura Medium, its teal/salmon "with/without guidance"
pair, the copper expert motif, lavender rounded frames and thin black arrows.
"""
from pathlib import Path
import hashlib, json, os
os.environ.setdefault('MPLCONFIGDIR', str(Path.home() / '.cache' / 'mpl_coma'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Circle, Arc, FancyArrowPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / 'revision_v20' / 'tsne_pdf_marker_coordinates.csv'
OUT = ROOT / 'figures'
FONT_TTF = ROOT / 'FuturaMedium.ttf'

# ---- Figure 1 palette (sampled from the manuscript's Figure 1 raster) ----
INK = '#141514'
MUTED = '#6E6A73'
FRAME = '#C9C5E6'        # lavender box border, Fig. 1 "Property" boxes
COPPER = '#8B6842'       # expert motif
GOOD = '#289E78'         # Fig. 1 "With guidance"
GOOD_TINT = '#D6EFE5'
BAD = '#EFA28C'          # Fig. 1 "Without guidance" family
BAD_TINT = '#FBE4DC'

METRICS = {  # printed on the archived vector PDF that supplies the coordinates
    'before': dict(sil='0.007'),
    'after':  dict(sil='0.107'),
}


def futura():
    """Extract Futura Medium from the system collection so PDF/SVG embed it cleanly."""
    if not FONT_TTF.exists():
        from fontTools.ttLib import TTCollection
        TTCollection('/System/Library/Fonts/Supplemental/Futura.ttc').fonts[0].save(str(FONT_TTF))
    font_manager.fontManager.addfont(str(FONT_TTF))
    name = font_manager.FontProperties(fname=str(FONT_TTF)).get_name()
    plt.rcParams.update({'font.family': name, 'font.size': 9, 'text.color': INK,
                         'pdf.fonttype': 42, 'svg.fonttype': 'path'})
    return name


def expert_icon(fig, cx, cy, r):
    """Copper head-and-shoulders, as in Figure 1."""
    tr = fig.transFigure
    w, h = fig.get_size_inches()
    sx = r * h / w                          # keep the head circular in figure coords
    fig.patches.append(matplotlib.patches.Ellipse((cx, cy), 2 * sx, 2 * r, transform=tr,
                       fill=False, ec=COPPER, lw=1.5))
    for dx in (-0.42, 0.0):                 # two small brow arcs inside the head
        fig.patches.append(Arc((cx + dx * sx * 0.55 + 0.21 * sx, cy + 0.42 * r), 0.9 * sx, 0.55 * r,
                               theta1=25, theta2=155, transform=tr, ec=COPPER, lw=0.9))
    fig.patches.append(Arc((cx, cy - 2.75 * r), 4.0 * sx, 3.5 * r, theta1=0, theta2=180,
                           transform=tr, ec=COPPER, lw=1.5))
    for ox, oy, s in [(-1.55, 0.95, .07), (1.5, 0.75, .06), (-1.7, -0.35, .05), (1.62, -0.25, .045)]:
        fig.patches.append(matplotlib.patches.Ellipse((cx + ox * sx, cy + oy * r), 2 * s * sx, 2 * s * r,
                           transform=tr, fc='#D9BC93', ec='none'))


def panel(fig, rect, data, title, sub, key, tint):
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, transform=ax.transAxes,
                                boxstyle='round,pad=0,rounding_size=0.045',
                                fc='white', ec=FRAME, lw=1.1, clip_on=False, zorder=0))
    inner = fig.add_axes([rect[0] + .012, rect[1] + .02, rect[2] - .024, rect[3] - .04])
    inner.set_axis_off()
    for label, kw in [('Bad', dict(s=19, c=BAD, alpha=.92, linewidths=.45, zorder=3)),
                      ('Good', dict(s=23, c=GOOD, alpha=.95, linewidths=.55, zorder=4))]:
        pts = data[data.label == label]
        art = inner.scatter(pts.x_pdf, pts.y_pdf, edgecolors='white', **kw)
        assert np.array_equal(np.asarray(art.get_offsets()), pts[['x_pdf', 'y_pdf']].to_numpy())
    dx, dy = np.ptp(data.x_pdf), np.ptp(data.y_pdf)
    inner.set_xlim(data.x_pdf.min() - .05 * dx, data.x_pdf.max() + .05 * dx)
    inner.set_ylim(data.y_pdf.min() - .16 * dy, data.y_pdf.max() + .05 * dy)
    inner.set_aspect('equal', adjustable='datalim')

    x0, y1 = rect[0], rect[1] + rect[3]
    fig.text(x0 + .004, y1 + .072, title, fontsize=11.5, color=INK, va='bottom')
    fig.text(x0 + .004, y1 + .026, sub, fontsize=8.3, color=MUTED, va='bottom')

    m = METRICS[key]
    ax.text(.965, .055, f'Silhouette = {m["sil"]}', transform=ax.transAxes, ha='right', va='bottom',
            fontsize=9, color=INK, zorder=6,
            bbox=dict(boxstyle='round,pad=0.42,rounding_size=0.8', fc=tint, ec='none'))
    return ax


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fontname = futura()
    pts = pd.read_csv(SRC)
    assert len(pts) == 442 and (pts.groupby('panel').size() == 221).all()

    fig = plt.figure(figsize=(180 / 25.4, 86 / 25.4), facecolor='white')
    L = [.015, .16, .405, .62]
    R = [.58, .16, .405, .62]
    panel(fig, L, pts[pts.panel == 'before'], 'Before contrastive learning',
          'MolFormer embeddings (768-d)', 'before', BAD_TINT)
    panel(fig, R, pts[pts.panel == 'after'], 'After contrastive learning',
          'Guided embeddings (256-d)', 'after', GOOD_TINT)

    # connector: expert motif over a thin black arrow, as between stages in Figure 1
    cx = (L[0] + L[2] + R[0]) / 2
    expert_icon(fig, cx, .63, .044)
    fig.patches.append(FancyArrowPatch((L[0] + L[2] + .016, .462), (R[0] - .016, .462),
                                       transform=fig.transFigure, arrowstyle='-|>',
                                       mutation_scale=9, lw=1.05, color=INK))
    fig.text(cx, .415, 'Expert-guided\ncontrastive\nlearning', ha='center', va='top',
             fontsize=7.6, color=INK, linespacing=1.25)

    handles = [Line2D([], [], marker='o', ls='', ms=6.2, mfc=BAD, mec='white', mew=.5, label='Inactive (Bad)'),
               Line2D([], [], marker='o', ls='', ms=6.2, mfc=GOOD, mec='white', mew=.5, label='Active (Good)')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, -.005), ncol=2, frameon=False,
               fontsize=9, handletextpad=.3, columnspacing=2.2)
    fig.text(R[0] + R[2], .052, 't-SNE of the held-out fold, n = 221', ha='right', va='center',
             fontsize=7.6, color=MUTED)

    name = 'figure2_contrastive_fig1style'
    for ext, kw in [('pdf', {}), ('svg', {}), ('png', dict(dpi=600)), ('tiff', dict(dpi=600))]:
        fig.savefig(OUT / f'{name}.{ext}', facecolor='white', bbox_inches='tight', pad_inches=.06, **kw)
    plt.close(fig)

    (ROOT / 'figure2_manifest.json').write_text(json.dumps(dict(
        source=str(SRC.relative_to(ROOT.parent.parent)),
        source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
        points_per_panel=221, classes=dict(Bad=172, Good=49),
        geometry='archived PDF marker centres, unchanged; no t-SNE recomputation',
        metrics=METRICS, metrics_source='printed on the archived vector PDF',
        variant_check=dict(before='coincides with manuscript v21 raster (median NN 0.023, identity)',
                           after='different t-SNE run from manuscript v21 raster (no orientation aligns; best 0.049)'),
        note='manuscript v21 text and raster state 0.108 for a run with no surviving vector source',
        font=fontname, palette=dict(good=GOOD, bad=BAD, frame=FRAME, expert=COPPER, ink=INK),
    ), indent=2))
    print('saved', name, 'as pdf/svg/png/tiff in', OUT)


if __name__ == '__main__':
    main()
