"""Editorial figures from existing results; no new model training."""
from pathlib import Path
import json, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'revision_v10'
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'pdf.fonttype': 42, 'svg.fonttype': 'none',
                     'axes.spines.right': False, 'axes.spines.top': False})


def save(fig, name):
    for ext in ['png', 'pdf', 'svg']:
        fig.savefig(OUT / (name + '.' + ext), dpi=300, bbox_inches='tight')
    plt.close(fig)


def box(ax, x, y, w, h, text, color):
    ax.add_patch(FancyBboxPatch((x,y), w,h, boxstyle='round,pad=0.01,rounding_size=0.015',
                 facecolor=color, edgecolor='#4a5563', linewidth=0.9))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=9.5, linespacing=1.4)


def arrow(ax, a, b):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,color='#52616c',lw=1.2))


def design():
    fig, ax = plt.subplots(figsize=(12,6.2))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    ax.text(.015,.98,'A   Partial backbone fine-tuning',va='top',weight='bold',fontsize=12)
    ax.text(.515,.98,'B   Matched-molecule frozen-feature interventions',va='top',weight='bold',fontsize=12)
    box(ax,.02,.68,.44,.20,'Eligible source collections\n740 expert molecules | 1,153 MIC molecules\n9,338 MIC records\nEvaluation full salts excluded', '#f4eee6')
    box(ax,.52,.68,.46,.20,'Identical source molecules within each panel\n681 pooled panel | 529 exact S. aureus panel\nExpert / continuous MIC / binary MIC\nShuffled controls | untrained encoder | raw features', '#e7f0f5')
    box(ax,.02,.42,.44,.15,'Train upper MolFormer layers\nEmbedding + lowest four layers frozen\n3 source-training seeds; sources differ in exposure', '#f4eee6')
    box(ax,.52,.42,.46,.15,'Frozen backbone + 256 → 128 encoder\nPaired weights, scaffold split and 80 epochs\n5 seeds; evaluation cations excluded', '#e7f0f5')
    arrow(ax,(.24,.68),(.24,.58)); arrow(ax,(.75,.68),(.75,.58))
    box(ax,.02,.15,.20,.16,'Target refitting\nQ-HERO-411\nScaffold-CV R²', '#f7f7f7')
    box(ax,.26,.15,.20,.16,'Direct transfer\nQ-HERO-411\nPotency ranking', '#f7f7f7')
    box(ax,.52,.15,.46,.16,'Target refitting on Q-HERO-405\nShared cation-scaffold folds; paired loss contrasts\n4 frozen backbones; same-chemistry context test', '#f7f7f7')
    arrow(ax,(.24,.42),(.12,.32)); arrow(ax,(.24,.42),(.36,.32))
    arrow(ax,(.75,.42),(.75,.32))
    ax.plot([.495,.495],[.14,.96],color='#ccd1d5',lw=1)
    ax.text(.5,.04,'Separate questions: label content • added value over raw features • practical competition',
            ha='center',fontsize=11,weight='bold')
    fig.tight_layout()
    save(fig,'figure1_study_design')


def competition():
    archive = ROOT.parent / 'finetune'
    p = pd.DataFrame([json.loads(x) for x in (archive/'runs.jsonl').read_text().splitlines()])
    d = pd.DataFrame([json.loads(x) for x in (archive/'runs_direct.jsonl').read_text().splitlines()])
    names=['expert-binary','quant-molecule','quant-record']
    labels=['Human binary\n740 molecules','Molecule MIC\n1,153 molecules','Record MIC\n9,338 records']
    colors=['#805c8e','#328c82','#427aa6']
    fig, axes=plt.subplots(1,2,figsize=(11.7,5))
    raw=p[(p.target=='Q-HERO')&(p.representation=='MolFormer frozen')].R2.values
    assert len(raw)==3
    axes[0].axhline(raw.mean(),color='#646d75',lw=1.2,ls='--',label='Raw MolFormer mean')
    exported=[]
    for i,(name,col) in enumerate(zip(names,colors)):
        a=p[(p.target=='Q-HERO')&(p.representation=='FT '+name)].R2.values
        b=d[(d.target=='Q-HERO')&(d.representation=='FT '+name+' (direct)')].rank_agreement.values
        assert len(a)==len(b)==3
        for j,y in enumerate([a,b]):
            axes[j].scatter(i+np.linspace(-.08,.08,3),y,color=col,s=38,zorder=3)
            axes[j].errorbar(i,y.mean(),yerr=y.std(ddof=1),fmt='_',color=col,markersize=22,capsize=4,lw=1.4)
        exported.append({'source':name,'downstream_R2':float(a.mean()),'downstream_seed_sd':float(a.std(ddof=1)),
                         'direct_rank':float(b.mean()),'direct_seed_sd':float(b.std(ddof=1))})
    axes[0].set_title('A   Downstream refitting on Q-HERO-411',loc='left',weight='bold')
    axes[1].set_title('B   Direct transfer on Q-HERO-411',loc='left',weight='bold')
    axes[0].set_ylabel('Scaffold-CV R²'); axes[0].set_ylim(0,.43)
    axes[1].set_ylabel('Direct rank agreement with measured MIC'); axes[1].set_ylim(0,.8)
    axes[0].legend(frameon=False,loc='upper left',fontsize=9)
    for ax in axes:
        ax.set_xticks(range(3)); ax.set_xticklabels(labels);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.text(.5,.012,'Three source-training seeds; mean ± seed SD. Sources differ in size and exposure; panels use different evaluation regimes.',
             ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,1])
    save(fig,'figure2_partial_finetuning_and_direct')
    (ROOT/'figure2_values.json').write_text(json.dumps({'raw_R2':float(raw.mean()),'sources':exported},indent=2))


if __name__=='__main__':
    design(); competition()
    for old,new in [('figure8_modern_context','figure3_paired_context_contrasts'),
                    ('figure9_MIC_error_violins','figure4_MIC_error_violins')]:
        for ext in ['png','pdf','svg']:
            shutil.copyfile(OLD/'figures'/(old+'.'+ext),OUT/(new+'.'+ext))
    print(OUT)
