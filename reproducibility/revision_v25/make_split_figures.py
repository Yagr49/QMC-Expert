"""Separate the existing matched-design schematic from its unchanged error data."""
from pathlib import Path
import importlib.util, json, hashlib, os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v25_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'revision_v24';OUT=ROOT/'figures'
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('oldfigure',OLD/'make_human_quantitative.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def save(fig,name):
    for ext in ['png','pdf','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=600,facecolor='white')
    plt.close(fig)

def main():
    fig,ax=plt.subplots(figsize=(180/25.4,58/25.4))
    fig.subplots_adjust(left=.025,right=.985,bottom=.035,top=.92);ax.set_axis_off()
    box,arrow=old.box,old.arrow
    ax.text(.40,.985,'Supervision: 681 source molecules',ha='center',fontsize=8.4,transform=ax.transAxes)
    box(ax,.016,.55,.169,.23,'Frozen\nMolFormer','#EFF1F4')
    ax.text(.095,.90,'105 QAC inputs',ha='center',va='center',fontsize=8.5,transform=ax.transAxes)
    arrow(ax,(.095,.855),(.095,.795))
    box(ax,.285,.70,.225,.20,'Human Good / Bad\nCompact encoder',old.COLORS['human'],8.6)
    box(ax,.285,.35,.225,.20,'Measured MIC\nCompact encoder',old.COLORS['mic_continuous'],8.6)
    arrow(ax,(.191,.70),(.272,.80));arrow(ax,(.191,.62),(.272,.45))
    ax.text(.397,.225,'768 → 512 → 384 → 256',ha='center',fontsize=8.4,transform=ax.transAxes)
    box(ax,.605,.56,.18,.24,'Separate\nCatBoost fits','#F7E8DC',8.6)
    arrow(ax,(.518,.80),(.593,.73));arrow(ax,(.518,.45),(.593,.62))
    box(ax,.835,.56,.15,.24,'Held-out\nMIC / MBC','#EDF3F8',8.6)
    arrow(ax,(.794,.68),(.826,.68))
    ax.text(.91,.425,'Cation / scaffold\nholdout',ha='center',fontsize=8.2,transform=ax.transAxes)
    ax.text(.47,.07,'Source encoders frozen · Five paired runs',ha='center',fontsize=8.2,color='#767C86',transform=ax.transAxes)
    save(fig,'figure5_matched_supervision_design')
    data=pd.read_csv(OLD/'figure4_compact_error_values.csv');checks=[]
    fig,axes=plt.subplots(1,2,figsize=(180/25.4,96/25.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.085,right=.985,bottom=.19,top=.87,wspace=.20)
    maximum=data.mean_absolute_error.max()
    for index,(ax,schema,title) in enumerate(zip(axes,['cation','scaffold'],['Cation holdout','Scaffold holdout'])):
        ax.set_title(title,pad=12,fontsize=10)
        ax.text(-.12,1.075,'ab'[index],fontsize=11,transform=ax.transAxes)
        for position,arm in enumerate(old.ARMS):
            values=data[(data.arm==arm)&(data.schema==schema)].mean_absolute_error.to_numpy()
            assert len(values)==420
            artists=ax.violinplot([values],positions=[position],widths=.75,showextrema=False,bw_method=.28)
            for artist in artists['bodies']:
                artist.set_facecolor(old.COLORS[arm]);artist.set_edgecolor('#929AA4')
                artist.set_linewidth(.65);artist.set_alpha(.50 if arm=='matched_raw' else .85)
            low,median,high=np.percentile(values,[25,50,75])
            ax.vlines(position,low,high,color='#68717C',lw=1.15,zorder=4)
            ax.hlines(median,position-.10,position+.10,color='#56616D',lw=1.25,zorder=5)
            jitter=np.random.RandomState(112+position).uniform(-.18,.18,len(values))
            ax.scatter(position+jitter,values,s=1.3,color='#6A7380',alpha=.13,lw=0,zorder=3)
            checks.append(dict(arm=arm,schema=schema,n=len(values),median=float(median),maximum=float(values.max())))
        ax.set_xticks(range(4));ax.set_xticklabels(['Human','Quantitative','Shuffled\nhuman','Raw'],fontsize=8.5)
        ax.set_ylim(0,maximum*1.04);ax.set_xlim(-.6,3.6);ax.grid(axis='y',alpha=.6)
    axes[0].set_ylabel('Mean absolute error, log₂(mg/L)',fontsize=9)
    save(fig,'figure6_matched_supervision_violins')
    captions={
        'figure5':('Figure 5. Matched human and quantitative supervision of external compact encoders. '
            'Both arms use the same 681 source molecules (377 training, 304 validation), five paired '
            'source seeds, frozen MolFormer features and the 768→512→384→256 architecture, without '
            'SMOTE. Human Good/Bad labels train a contrastive encoder; continuous MIC trains a '
            'regression encoder. Source-encoder weights are frozen before separate CatBoost fits '
            'use target-training folds, identical budgets and categorical task codes. Both '
            'representations are evaluated on the same 105 QAC salts and four endpoints. '
            'This is the matched follow-up design, rather than the historical full-corpus '
            'quantitative experiment; its observed error distributions appear in Figure 6.'),
        'figure6':('Figure 6. Observed prediction-error distributions for matched compact supervision '
            'under (a) cation and (b) scaffold holdouts. Each vertical violin contains the same '
            '420 compound–endpoint absolute errors, averaged across five source runs for human, '
            'quantitative and shuffled-human guidance; raw MolFormer is one fixed reference. '
            'Crossbars show medians and vertical lines the interquartile range. All points and '
            'tails are retained on shared linear axes. These are means of absolute errors, '
            'rather than errors of ensemble predictions or densities over five RMSE values. '
            'The source and decoder design is shown separately in Figure 5. Correlated endpoints '
            'and runs preclude reading density differences as significance or causal effects.')}
    for name,value in captions.items():(ROOT/(name+'_caption_EN.txt')).write_text(value+'\n')
    (ROOT/'split_figure_validation.json').write_text(json.dumps(dict(completed=True,
        source=str(OLD/'figure4_compact_error_values.csv'),source_sha256=hashlib.sha256((OLD/'figure4_compact_error_values.csv').read_bytes()).hexdigest(),
        no_error_values_or_statistics_changed=True,checks=checks,font='Aptos',width_mm=180,png_dpi=600,
        figures=['figure5_matched_supervision_design','figure6_matched_supervision_violins']),indent=2))
    print('Figure4 split into separate design and real-error figures; all 3360 values preserved.')

if __name__=='__main__':main()
