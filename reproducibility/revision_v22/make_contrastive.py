"""Publication redraw of archived marker coordinates; no generated scientific data."""
from pathlib import Path
import hashlib, json, os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/coma_v22_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'revision_v20/tsne_pdf_marker_coordinates.csv'
OUT = ROOT/'figures'

def main():
    OUT.mkdir(exist_ok=True)
    font_manager.fontManager.addfont('/Applications/Microsoft Word.app/Contents/Resources/DFonts/Aptos.ttf')
    plt.rcParams.update({'font.family': 'Aptos', 'font.size': 9,
        'text.color': '#42434B', 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    points = pd.read_csv(SOURCE)
    colors = {'Bad': '#E6B490', 'Good': '#87CABA'}
    edges = {'Bad': '#BF8C68', 'Good': '#589D8D'}
    fig, axes = plt.subplots(1, 2, figsize=(180/25.4, 87/25.4))
    checks = []
    for i, (ax, panel, title, score) in enumerate(zip(axes, ['before', 'after'],
            ['Before contrastive learning', 'After contrastive learning'], ['0.007', '0.107'])):
        data = points[points.panel == panel]
        ax.set_axis_off()
        frame = FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0.012,rounding_size=0.025',
            transform=ax.transAxes, fc='#FEFEFE', ec='#DADDE1', lw=.65,
            clip_on=False, zorder=0)
        ax.add_patch(frame)
        for label in ['Bad', 'Good']:
            subset = data[data.label == label]
            artist = ax.scatter(subset.x_pdf, subset.y_pdf, s=17.5, c=colors[label],
                edgecolors=edges[label], linewidths=.25, alpha=.95, zorder=3)
            assert np.array_equal(np.asarray(artist.get_offsets()), subset[['x_pdf', 'y_pdf']].to_numpy())
        dx = data.x_pdf.max()-data.x_pdf.min()
        dy = data.y_pdf.max()-data.y_pdf.min()
        ax.set_xlim(data.x_pdf.min()-.09*dx, data.x_pdf.max()+.09*dx)
        ax.set_ylim(data.y_pdf.min()-.09*dy, data.y_pdf.max()+.09*dy)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(title, fontsize=10, pad=11)
        ax.text(-.01, 1.065, 'ab'[i], transform=ax.transAxes, fontsize=11, fontweight='bold')
        ax.text(.5, -.075, 'Silhouette '+score, ha='center', va='center',
            fontsize=8, color='#727781', transform=ax.transAxes)
        checks.append({'panel': panel, 'points': len(data),
            'Bad': int((data.label=='Bad').sum()), 'Good': int((data.label=='Good').sum()),
            'all_scatter_offsets_exactly_preserved': True})
    handles = [Line2D([], [], marker='o', ls='', markersize=4.8,
        markerfacecolor=colors[l], markeredgecolor=edges[l], markeredgewidth=.3,
        label='Expert label: '+l) for l in ['Bad', 'Good']]
    legend=fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5,.045),
        ncol=2, frameon=False, fontsize=8.5, handletextpad=.35, columnspacing=2.2)
    fig.subplots_adjust(left=.03, right=.98, bottom=.20, top=.88, wspace=.14)
    fig.canvas.draw()
    legend_margin_mm=legend.get_window_extent(fig.canvas.get_renderer()).y0/fig.dpi*25.4
    assert legend_margin_mm >= 4
    for ext in ['png', 'pdf', 'svg']:
        fig.savefig(OUT/('figure2_contrastive_enhanced.'+ext), dpi=600, facecolor='white')
    plt.close(fig)
    manifest = {'font':'Aptos', 'width_mm':180, 'png_dpi':600, 'palette':colors,
        'source':str(SOURCE), 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'checks':checks, 'source_reported_after_silhouette':.107,
        'original_v5_raster_reported_after_silhouette':.108,
        'no_tsne_rerun':True, 'no_point_selection_or_geometry_changes':True,
        'class_labels_are_expert_calls_not_new_assay_measurements':True,
        'legend_bottom_margin_mm':legend_margin_mm,
        'panel_axes_independently_scaled_not_aligned':True}
    (ROOT/'contrastive_validation.json').write_text(json.dumps(manifest,indent=2))
    print('Figure2 enhanced: all 442 archived marker coordinates preserved.')

if __name__ == '__main__':
    main()
