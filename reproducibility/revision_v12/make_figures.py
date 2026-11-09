"""Publication figures from the completed matched partial-FT experiment."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/coma_v12_matplotlib')
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,
                    'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
ARMS = ['expert','quant-continuous','quant-binary','expert-shuffled','quant-shuffled','quant-binary-shuffled']
LABELS = ['Human','Continuous MIC','Binary MIC','Human shuffled','Continuous shuffled','Binary shuffled']
COLORS = ['#8064a2','#2c8c83','#357bad','#b6a6c9','#9ec9c4','#a2bdd3']

def save(fig, name):
    for ext in ['png','pdf','svg']: fig.savefig(OUT / f'{name}.{ext}', dpi=300, bbox_inches='tight')
    plt.close(fig)

def box(ax, x, y, w, h, text, color):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.01,rounding_size=0.012',
                              facecolor=color,edgecolor='#67747e',lw=.8))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9,linespacing=1.5)

def design():
    fig, ax = plt.subplots(figsize=(14,6.6)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    titles=['A   Archived partial fine-tuning','B   Matched frozen-feature adaptation','C   Matched partial fine-tuning']
    texts=[['740 human / 1,153 MIC molecules\n9,338 repeated MIC records\nEvaluation full salts excluded',
            'MolFormer upper eight layers\n3 seeds; early stopping\nSource size and exposure differ',
            'Q-HERO-411\nTarget-refit scaffold CV\nDirect source-head ranking'],
           ['Same 681 pooled-source molecules\n529-molecule context sensitivity\nEvaluation cations excluded',
            'Frozen backbone + 256 → 128 MLP\n5 paired seeds; 80 fixed epochs\n4 pretrained backbones',
            'Q-HERO-405\nFixed target scaffold folds\nReal / shuffled / raw controls'],
           ['Same 681 pooled-source molecules\nSame 377 train / 304 validation\nEvaluation cations excluded',
            'MolFormer upper eight layers\n5 paired seeds; 30 fixed epochs\n6 real / shuffled supervision arms',
            'Q-HERO-405; same folds as B\nCommon target-refit CatBoost\nDirect ranking with shuffled controls']]
    for i in range(3):
        x=.015+i*.335; w=.30; mid=x+w/2
        ax.text(x,.98,titles[i],fontsize=11,weight='bold',va='top')
        for j,y in enumerate([.67,.40,.13]):box(ax,x,y,w,.19,texts[i][j],['#f4eee6','#e7f0f5','#eaf2e7'][i])
        for y in [.67,.40]:ax.add_patch(FancyArrowPatch((mid,y),(mid,y-.07),arrowstyle='-|>',mutation_scale=12,color='#52616c'))
    ax.text(.5,.02,'Separate outcomes: label-assignment signal • added value over raw features • numerical competition',ha='center',weight='bold')
    fig.tight_layout();save(fig,'figure1_study_design')

def matched():
    metrics=pd.read_csv(ROOT/'results/metrics.csv');metrics=metrics[metrics.target=='Q-HERO-405']
    direct=pd.read_csv(ROOT/'results/direct_metrics.csv');direct=direct[direct.target=='Q-HERO-405']
    contrast=pd.read_csv(ROOT/'analysis/contrasts.csv');contrast=contrast[(contrast.target=='Q-HERO-405')&(contrast.unit=='seed+scaffold')].set_index('comparison')
    rank=pd.read_csv(ROOT/'analysis/direct_contrasts.csv');rank=rank[rank.target=='Q-HERO-405'].set_index('comparison')
    fig,axs=plt.subplots(2,2,figsize=(13.5,9.2),gridspec_kw={'width_ratios':[1.2,1]})
    for i,(arm,color) in enumerate(zip(ARMS,COLORS)):
        for ax,df,field in [(axs[0,0],metrics,'RMSE'),(axs[1,0],direct,'rank_agreement')]:
            values=df[df.arm==arm].sort_values('seed')[field].values;assert len(values)==5
            ax.scatter(i+np.linspace(-.09,.09,5),values,s=24,color=color,zorder=3)
            ax.errorbar(i,values.mean(),yerr=values.std(ddof=1),fmt='_',markersize=20,color=color,capsize=3,lw=1.4)
    raw=metrics[metrics.arm=='raw-molformer'].RMSE.iloc[0]
    axs[0,0].axhline(raw,color='#68737c',ls='--',lw=1.3,label=f'Raw MolFormer: {raw:.3f}')
    axs[0,0].legend(frameon=False,fontsize=9);axs[0,0].set_ylabel('Target-refit RMSE (log2 µM)')
    axs[1,0].axhline(0,color='#68737c',lw=.8);axs[1,0].set_ylabel('Direct rank agreement')
    for ax in axs[:,0]:
        ax.set_xticks(range(6));ax.set_xticklabels(['Human','MIC\ncontinuous','MIC\nbinary','Human\nshuffled','Continuous\nshuffled','Binary\nshuffled'],fontsize=9)
        ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    def intervals(ax,frame,pairs,labels,field):
        for i,pair in enumerate(pairs):
            row=frame.loc[pair];ax.plot([row.ci_low,row.ci_high],[i,i],color='#42728f',lw=2)
            ax.scatter(row[field],i,color='#253f50',s=30,zorder=3)
        ax.axvline(0,color='#68737c',ls='--',lw=1);ax.set_yticks(range(len(pairs)));ax.set_yticklabels(labels,fontsize=10)
        ax.invert_yaxis();ax.grid(axis='x',alpha=.18)
    pairs=['expert minus expert-shuffled','expert minus raw-molformer','expert minus quant-continuous','expert minus quant-binary']
    intervals(axs[0,1],contrast,pairs,['Human − shuffled human','Human − raw','Human − continuous MIC','Human − binary MIC'],'delta_RMSE')
    axs[0,1].set_xlabel('Paired ΔRMSE; negative favours human')
    pairs=['expert minus expert-shuffled','expert minus quant-continuous','expert minus quant-binary','quant-continuous minus quant-shuffled']
    intervals(axs[1,1],rank,pairs,['Human − shuffled human','Human − continuous MIC','Human − binary MIC','Continuous MIC − shuffled'],'delta_rank')
    axs[1,1].set_xlabel('Paired Δrank; positive favours first arm')
    titles=['A   Target-refit prediction','B   Paired loss contrasts','C   Direct source-only transfer','D   Paired ranking contrasts']
    for ax,title in zip(axs.flat,titles):ax.set_title(title,loc='left',weight='bold',fontsize=12)
    fig.text(.5,.012,'Same source molecules, initialisations, batches and final-checkpoint budget. Points: 5 seeds; bars: seed SD.\nIntervals: 10,000 paired seed/scaffold bootstrap draws, fixed folds, exploratory and unadjusted.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,1]);save(fig,'figure5_matched_finetuning')

def violations():
    p=pd.read_csv(ROOT/'results/predictions.csv');p=p[(p.target=='Q-HERO-405')&p.arm.isin(['expert','quant-continuous'])].copy()
    p['ae']=np.abs(p.y-p.pred);d=p.groupby(['arm','can']).ae.mean().unstack('arm').sort_index()
    assert len(d)==405 and not d.isna().any().any()
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.7))
    # Split KDE is drawn on linear absolute-error coordinates and clipped to support.
    for j,arm in enumerate(['expert','quant-continuous']):
        values=d[arm].values;parts=axs[0].violinplot([values],positions=[0],widths=1.2,showextrema=False)
        body=parts['bodies'][0];verts=body.get_paths()[0].vertices
        verts[:,0]=np.minimum(verts[:,0],0) if j==0 else np.maximum(verts[:,0],0)
        body.set_facecolor(COLORS[j]);body.set_edgecolor(COLORS[j]);body.set_alpha(.65)
        x=-.12 if j==0 else .12;q=np.quantile(values,[.25,.5,.75])
        axs[0].plot([x,x],[q[0],q[2]],color=COLORS[j],lw=3);axs[0].plot([x-.05,x+.05],[q[1],q[1]],color=COLORS[j],lw=3)
    axs[0].set_xticks([0]);axs[0].set_xticklabels(['Same 405 Q-HERO structures']);axs[0].set_ylabel('Absolute MIC prediction error (log2 µM)')
    axs[0].legend(handles=[Patch(facecolor=COLORS[0],alpha=.65,label='Human'),Patch(facecolor=COLORS[1],alpha=.65,label='Continuous MIC')],frameon=False)
    delta=d.expert-d['quant-continuous'];axs[1].hist(delta,bins=27,color='#809aab',edgecolor='white')
    axs[1].axvline(0,color='#555',ls='--');axs[1].set_xlabel('Paired absolute-error difference\nHuman − continuous MIC (log2 µM)');axs[1].set_ylabel('Structures')
    axs[0].set_title('A   Matched partial-fine-tuning error',loc='left',weight='bold')
    axs[1].set_title('B   Within-structure error difference',loc='left',weight='bold')
    fig.text(.5,.01,'Absolute errors averaged across five source seeds for each structure; descriptive distributions, without independent-record tests.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.045,1,1]);save(fig,'figureS18_matched_finetuning_error_violins')
    d.to_csv(ROOT/'analysis/matched_error_violins_values.csv')

def learning():
    e=pd.read_csv(ROOT/'results/epochs.csv');fig,axs=plt.subplots(1,2,figsize=(11,4.3))
    for arm,color,label in zip(ARMS,COLORS,LABELS):
        task='binary' if arm.startswith('expert') or arm.startswith('quant-binary') else 'continuous'
        ax=axs[0] if task=='binary' else axs[1]
        for seed,sub in e[e.arm==arm].groupby('seed'):
            ax.plot(sub.epoch,sub.val_loss,color=color,alpha=.22,lw=.8)
        mean=e[e.arm==arm].groupby('epoch').val_loss.mean();ax.plot(mean.index,mean.values,color=color,label=label,lw=1.8)
    for ax,title,y in zip(axs,['A   Binary source objectives','B   Standardised continuous MIC'],['Validation BCE','Validation MSE']):
        ax.set_title(title,loc='left',weight='bold');ax.set_ylabel(y);ax.set_xlabel('Epoch');ax.legend(frameon=False,fontsize=8);ax.grid(alpha=.15)
    fig.text(.5,.01,'Source validation is diagnostic only. All arms use the final 30-epoch checkpoint; no checkpoint is selected by these curves.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.055,1,1]);save(fig,'figureS17_matched_finetuning_learning')

if __name__=='__main__':
    for name in ['figure2_partial_finetuning_and_direct','figure3_paired_context_contrasts','figure4_MIC_error_violins']:
        for ext in ['png','pdf','svg']:shutil.copy2(ROOT.parent/'revision_v11/figures'/f'{name}.{ext}',OUT/f'{name}.{ext}')
    design();matched();violations();learning();print(OUT)
