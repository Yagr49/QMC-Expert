"""Figures 1, 6 and 8 of manuscript v28, restyled in the Figure 5 visual language.

Only typography and colour change. Every value, curve and point comes from the same
archived result files the v25/v26 versions used:
  Figure 1  drawn programmatically, same label counts and R2 ranges as v25
  Figure 6  revision_v24/figure5_{mean,empirical}_roc_points.csv and figure5_roc_metrics.csv
  Figure 8  revision_v26/OOD_violin_values.csv

    python make_figures_futura.py [1] [6] [8]
"""
from pathlib import Path
import sys, json, importlib.util
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc, Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
REPRO = ROOT.parent
OUT = ROOT / 'figures'
sys.path.insert(0, str(ROOT))
import theme_v27 as T


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


# ----------------------------------------------------------------- Figure 1
def figure1():
    from rdkit import Chem
    from rdkit.Chem import rdDepictor
    from rdkit.Chem.Draw import rdMolDraw2D
    T.theme()
    acs = module('acs', REPRO / 'revision_v14/drawing_style.py')

    def box(ax, x, y, w, h, value, col, fs=8.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.006,rounding_size=.012',
                                    facecolor=col['tint'], edgecolor=col['edge'], lw=1.0))
        ax.text(x + w / 2, y + h / 2, value, ha='center', va='center', fontsize=fs,
                color=col['text'], linespacing=1.3)

    def arrow(ax, a, z, dashed=False):
        ax.annotate('', xy=z, xytext=a, arrowprops=dict(arrowstyle='-|>', color='#3A3B40', lw=.9,
                    mutation_scale=8, linestyle='--' if dashed else '-'))

    smiles = '[Br-].[Br-].*[n+]1ccc(Cc2ccc(Cc3cc[n+](*)cc3)cc2)cc1'
    mol = Chem.MolFromSmiles(smiles)
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 0:
            atom.SetProp('dummyLabel', 'R')
    rdDepictor.Compute2DCoords(mol)
    drawer = rdMolDraw2D.MolDraw2DSVG(-1, -1)
    drawer.drawOptions().fontFile = str(T.FONT_TTF)
    rdMolDraw2D.DrawMoleculeACS1996(drawer, mol); drawer.FinishDrawing()
    from xml.etree import ElementTree as E
    svg = drawer.GetDrawingText(); tree = E.fromstring(svg)
    record = (svg, tree, float(tree.get('width')[:-2]), float(tree.get('height')[:-2]))

    fig, ax = plt.subplots(figsize=(180 / 25.4, 125 / 25.4))
    fig.subplots_adjust(left=.03, right=.98, bottom=.02, top=.98)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_axis_off()
    dots = [T.MINT['fill'], T.LAV['fill'], T.PEACH['fill'], T.BLUE['fill'], '#E3C9D8']
    ax.text(.01, .98, 'The expert guidance pipeline', fontsize=11.5, va='top', color=T.INK)
    rng = np.random.RandomState(52)
    for i, (x, y) in enumerate(rng.uniform([.065, .76], [.17, .90], (23, 2))):
        ax.scatter(x, y, s=10, color=dots[i % 5], lw=0)
    ax.add_patch(Circle((.37, .856), .024, fc='none', ec='#8B6842', lw=1.1))
    ax.add_patch(Arc((.37, .78), .09, .10, theta1=0, theta2=180, color='#8B6842', lw=1.1))
    for row in range(5):
        ax.scatter(np.linspace(.58, .65, 5), np.repeat(.90 - row * .026, 5), s=10, color=dots[row], lw=0)
    ax.plot([.80, .94], [.765, .765], color='#D2D0D8', lw=.6)
    ax.plot([.80, .80], [.765, .90], color='#D2D0D8', lw=.6)
    ax.plot([.805, .84, .875, .91, .935], [.775, .795, .84, .868, .892], color=T.MINT['edge'], lw=1.6)
    ax.plot([.805, .84, .875, .91, .935], [.775, .783, .789, .799, .805], color=T.PEACH['edge'], lw=1.2, ls='--')
    ax.text(.87, .925, 'Schematic', fontsize=7, color=T.MUTED, ha='center')
    for x, label in [(.12, 'Raw information'), (.37, 'Expert guidance'),
                     (.615, 'Guided representation'), (.87, 'Prediction')]:
        ax.text(x, .72, label, ha='center', fontsize=8, color=T.INK)
    for a, z in [((.20, .832), (.31, .832)), ((.43, .832), (.545, .832)), ((.68, .832), (.765, .832))]:
        arrow(ax, a, z)
    ax.text(.01, .635, 'A) Earlier descriptor-based workflow', fontsize=10, color=T.INK)
    box(ax, .345, .455, .125, .13, 'Feature\nselection', T.BLUE)
    box(ax, .515, .455, .135, .13, 'Stacking\nmodels', T.MINT)
    box(ax, .70, .438, .285, .164, 'MIC / MBC · S. aureus / E. coli\nDescriptor MLP: R² 0.25–0.68\n'
        'Stacking: R² 0.30–0.43', T.LAV, 7.8)
    for a, z in [((.285, .52), (.334, .52)), ((.479, .52), (.505, .52)), ((.659, .52), (.69, .52))]:
        arrow(ax, a, z)
    ax.text(.01, .355, 'B) Our human-guided workflow', fontsize=10, color=T.INK)
    box(ax, .335, .135, .115, .125, 'Frozen\nMolFormer', T.GREY)
    box(ax, .485, .135, .155, .125, 'Compact\nencoder', T.MINT)
    box(ax, .675, .135, .11, .125, 'CatBoost', T.PEACH)
    box(ax, .825, .126, .16, .145, 'MIC / MBC\nHuman + text\nR² 0.59–0.77', T.LAV, 8)
    ax.text(.562, .305, '1,103 final expert labels', ha='center', fontsize=8.3, color=T.INK)
    arrow(ax, (.562, .291), (.562, .271), True)
    ax.text(.562, .092, f'768 {T.ARROW} 512 {T.ARROW} 384 {T.ARROW} 256', ha='center', fontsize=7.5, color=T.MUTED)
    ax.text(.73, .092, '+ task code', ha='center', fontsize=7.5, color=T.MUTED)
    for a, z in [((.285, .197), (.324, .197)), ((.459, .197), (.474, .197)),
                 ((.649, .197), (.664, .197)), ((.794, .197), (.814, .197))]:
        arrow(ax, a, z)
    molaxes = []
    for bottom in [.407, .099]:
        ma = fig.add_axes([.035, bottom, .263, .17]); molaxes.append(ma)
        acs.draw_acs(ma, record, record[2] + 8, record[3] + 8)
    acs.fix_acs_strokes(fig, molaxes, record[2] + 8)
    T.save(fig, OUT, 'figure1_pipeline_futura')


# ----------------------------------------------------------------- Figure 6
ROC_LABEL = [('CB_human', 'Human'), ('CB_quantitative', 'Quantitative'),
             ('CB_shuffled_human', 'Shuffled human'), ('CB_raw_MolFormer', 'Raw MolFormer'),
             ('RF_35_descriptors', 'RF, 35 descriptors')]


def figure6():
    T.theme()
    mean = pd.read_csv(REPRO / 'revision_v24/figure5_mean_roc_points.csv')
    emp = pd.read_csv(REPRO / 'revision_v24/figure5_empirical_roc_points.csv')
    met = pd.read_csv(REPRO / 'revision_v24/figure5_roc_metrics.csv')
    fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 92 / 25.4), sharex=True, sharey=True)
    panels = [('random_heldout20', 'Random holdout', 'a'), ('scaffold_CV_fold', 'Scaffold holdout', 'b')]
    for ax, (proto, title, letter) in zip(axes, panels):
        ax.plot([0, 1], [0, 1], ls=(0, (3, 3)), lw=.8, color='#C6C4CC', zorder=1)
        for model, label in ROC_LABEL:
            col = T.ARM[model]
            m = mean[(mean.model == model) & (mean.protocol == proto)].sort_values('FPR')
            if not len(m):
                e = emp[(emp.model == model) & (emp.protocol == proto)].sort_values('FPR')
                ax.step(e.FPR, e.TPR, where='post', lw=1.5, color=col['edge'],
                        ls=(0, (4, 2)), zorder=3, label=label)
                continue
            if m.seed_SD.notna().any():
                ax.fill_between(m.FPR, (m.mean_TPR - m.seed_SD).clip(0, 1),
                                (m.mean_TPR + m.seed_SD).clip(0, 1),
                                color=col['fill'], alpha=.45, lw=0, zorder=2)
            dash = (0, (4, 2)) if model == 'RF_35_descriptors' else '-'
            ax.plot(m.FPR, m.mean_TPR, lw=1.8, color=col['edge'], ls=dash, zorder=3, label=label)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
        ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1])
        ax.set_xlabel('False positive rate', fontsize=8.4)
        ax.set_title(title, fontsize=9.6, pad=8, color=T.INK)
        T.panel_letter(ax, letter, x=-.1, y=1.02)
        T.despine(ax, grid='both')
        rows = []
        for model, label in ROC_LABEL:
            r = met[(met.model == model) & (met.protocol == proto)]
            if len(r):
                sd = r.AUROC_SD.iloc[0]
                rows.append(f'{label}  {r.AUROC.iloc[0]:.3f}' + ('' if pd.isna(sd) else f' ± {sd:.3f}'))
        ax.text(.98, .035, 'AUROC\n' + '\n'.join(rows), transform=ax.transAxes, ha='right', va='bottom',
                fontsize=6.4, color=T.INK, linespacing=1.45,
                bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=T.RULE, lw=.5, alpha=.9))
    axes[0].set_ylabel('True positive rate', fontsize=8.4)
    handles = [Line2D([], [], lw=1.8, color=T.ARM[m]['edge'],
                      ls=(0, (4, 2)) if m == 'RF_35_descriptors' else '-', label=l)
               for m, l in ROC_LABEL]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, -.02), ncol=5,
               frameon=False, fontsize=7.6, handlelength=1.8, columnspacing=1.6)
    T.save(fig, OUT, 'figure6_qhero_roc_futura')


# ----------------------------------------------------------------- Figure 8
OOD_PANELS = [('compact', 'Compact feature encoders',
               [('matched_raw', 'Raw'), ('human', 'Human'),
                ('mic_continuous', 'Quantitative'), ('human_shuffled', 'Shuffled\nhuman')]),
              ('backbone', 'Backbone adaptation routes',
               [('frozen_head', 'Frozen\nhead'), ('lora', 'LoRA'), ('full_FT', 'Full FT'),
                ('human_direct', 'Human\ndirect'), ('human_CatBoost', 'Human\n' + '\u203a CB')])]
ROUTE_COL = {'matched_raw': 'raw', 'human': 'human', 'mic_continuous': 'quantitative',
             'human_shuffled': 'shuffled', 'frozen_head': 'raw', 'lora': 'descriptors',
             'full_FT': 'quantitative', 'human_direct': 'human', 'human_CatBoost': 'human'}


def figure8():
    T.theme()
    d = pd.read_csv(REPRO / 'revision_v26/OOD_violin_values.csv')
    top = float(np.ceil(d.mean_absolute_error.max() + .3))
    fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 95 / 25.4), sharey=True,
                             gridspec_kw={'width_ratios': [4, 5]})
    rng = np.random.RandomState(0)
    for ax, (exp, title, arms) in zip(axes, OOD_PANELS):
        for k, (route, label) in enumerate(arms):
            v = d[(d.experiment == exp) & (d.route == route)].mean_absolute_error.to_numpy()
            col = T.ARM[ROUTE_COL[route]]
            T.violin(ax, k, v, col, width=.8)
            ax.scatter(k + rng.uniform(-.12, .12, len(v)), v, s=2.6, color=T.BAR,
                       alpha=.33, lw=0, zorder=3)
        ax.set_xlim(-.6, len(arms) - .4); ax.set_ylim(0, top)
        ax.set_xticks(range(len(arms)))
        ax.set_xticklabels([a[1] for a in arms], fontsize=7.2, linespacing=1.05)
        ax.tick_params(axis='x', length=0, pad=3)
        ax.set_title(title, fontsize=9.6, pad=8, color=T.INK)
        T.panel_letter(ax, 'ab'[OOD_PANELS.index((exp, title, arms))], x=-.09, y=1.02)
        T.despine(ax)
    axes[0].set_ylabel('Mean absolute error, log$_2$(mg/L)', fontsize=8.4)
    handles = [Patch(fc=T.ARM[k]['fill'], ec=T.ARM[k]['edge'], lw=.7, label=l)
               for k, l in [('human', 'Human guidance'), ('quantitative', 'Quantitative / full FT'),
                            ('shuffled', 'Shuffled human'), ('raw', 'Raw / frozen'),
                            ('descriptors', 'LoRA')]]
    handles.append(Line2D([], [], marker='o', ls='-', lw=1.5, color=T.BAR, mfc='white',
                          mec=T.BAR, ms=4, label='median and interquartile range'))
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, -.03), ncol=6,
               frameon=False, fontsize=7.2, handlelength=1.5, columnspacing=1.2)
    fig.text(.01, -.055, '67 exact compound–endpoint errors per violin, averaged within runs; '
             'dots are the individual summaries. The IT505 E. coli MBC >500 mg/L bound is excluded.',
             fontsize=6.4, color=T.MUTED, ha='left')
    T.save(fig, OUT, 'figure8_ood_errors_futura')


if __name__ == '__main__':
    want = sys.argv[1:] or ['1', '6', '8']
    if '1' in want:
        figure1()
    if '6' in want:
        figure6()
    if '8' in want:
        figure8()
