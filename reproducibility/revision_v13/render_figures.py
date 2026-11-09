"""Render main figures in the user's Main_Article3_revised visual style.

Use archived numerical files unchanged. Colours, frames and panel typography
change; every prediction, KDE coordinate and uncertainty definition is retained.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v13_matplotlib')
import importlib.util,json
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import drawing_style as style

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'revision_v12'
V10=ROOT.parent/'revision_v10'
OUT=ROOT/'figures'


def save(fig,name):
    style.finish(fig)
    for ext in ['png','pdf','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
    plt.close(fig)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def main():
    m12=module('v12_plots',OLD/'make_figures.py')
    m11=module('v11_plots',ROOT.parent/'revision_v11/make_figures.py')
    # Redirect outputs only. All archived inputs and analyses remain intact.
    m12.save=save
    m11.ROOT=ROOT;m11.OUT=OUT;m11.save=save
    style.theme()
    m12.design();m11.competition();m12.matched();m12.learning()
    context();violins();matched_violins();parity()
    reference=Path('/Users/egorilin/Downloads/Telegram Desktop/Main_Article3_revised.docx')
    import hashlib
    report=dict(reference=str(reference),reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                main_figures=list(range(1,7)),new_SI_figures=[17,18,19,20,21],
                appearance='White background; muted consistent colours; light boxed axes; fine grid; regular panel labels; parity matrix.',
                molecular_preset='RDKit MolToACS1996SVG (monochrome, native bond width 0.6, native fixed font size 10).',
                numerical_predictions_changed=False,
                archived_SI='Historical supplementary images retained; newly rendered cohort structures use ACS 1996.')
    (ROOT/'style_validation.json').write_text(json.dumps(report,indent=2))
    print(OUT)


def context():
    contrasts=pd.read_csv(V10/'analysis/contrasts.csv')
    contrasts=contrasts[(contrasts.target=='Q-HERO-405')&(contrasts.unit=='seed+scaffold')]
    fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1,1.3]})
    models=['molformer','c3-molformer','chemberta100m','chemfm1b']
    labels=['MolFormer-XL','c3-MoLFormer','ChemBERTa-100M','ChemFM-1B']
    for i,backbone in enumerate(models):
        row=contrasts[(contrasts.backbone==backbone)&(contrasts.panel=='matched-pooled')&
                      (contrasts.comparison=='expert minus expert-shuffled')].iloc[0]
        axes[0].errorbar(row.delta_RMSE,i,xerr=[[row.delta_RMSE-row.ci_low],[row.ci_high-row.delta_RMSE]],
                         fmt='o',color=style.PALETTE['human'],capsize=4,lw=1.4)
    axes[0].set_yticks(range(4));axes[0].set_yticklabels(labels)
    axes[0].set_title('a) Human versus shuffled labels\n681 identical source molecules',loc='left')
    pairs=['quant-pooled minus quant-sa','quant-pooled minus quant-pooled-shuffled','expert minus quant-pooled','expert minus raw-molformer']
    labels=['Pooled MIC − exact S. aureus MIC','Pooled MIC − shuffled pooled MIC','Human − pooled MIC','Human − raw MolFormer']
    for i,pair in enumerate(pairs):
        row=contrasts[(contrasts.panel=='context')&(contrasts.comparison==pair)].iloc[0]
        axes[1].errorbar(row.delta_RMSE,i,xerr=[[row.delta_RMSE-row.ci_low],[row.ci_high-row.delta_RMSE]],
                         fmt='o',color=style.PALETTE['continuous'],capsize=4,lw=1.4)
    axes[1].set_yticks(range(4));axes[1].set_yticklabels(labels)
    axes[1].set_title('b) Context sensitivity\n529 identical source molecules',loc='left')
    for ax in axes:
        ax.axvline(0,color='#8b9196',ls='--',lw=.9);ax.grid(axis='x',alpha=.6)
        ax.set_ylim(3.5,-.5);ax.set_xlabel('ΔRMSE on Q-HERO-405 (log2 µM)')
    fig.text(.5,.012,'95% paired seed/scaffold bootstrap intervals; fixed folds; exploratory, unadjusted.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,1]);save(fig,'figure3_paired_context_contrasts')


def violin(ax,values,x,color,side='both',width=.34):
    values=np.asarray(values,float);values=values[np.isfinite(values)]
    grid=np.linspace(values.min(),values.max(),240)
    density=gaussian_kde(values,bw_method='scott')(grid) if values.std()>1e-8 else np.ones(len(grid))
    density=density/density.max()*width
    left=x-density if side!='right' else np.full_like(grid,x)
    right=x+density if side!='left' else np.full_like(grid,x)
    ax.fill_betweenx(grid,left,right,color=color,alpha=.48,lw=1,edgecolor=color)
    q=np.quantile(values,[.25,.5,.75]);centre=x+(-.075 if side=='left' else .075 if side=='right' else 0)
    ax.plot([centre,centre],[q[0],q[2]],color=color,lw=2)
    ax.plot([centre-.06,centre+.06],[q[1],q[1]],color=color,lw=2.5)
    return len(values)


def violins():
    # Same molecule-level aggregation and KDE coordinates as v10; no new assay sampling.
    source=pd.read_csv(V10/'analysis/violin_source_MIC.csv')
    target=pd.read_csv(V10/'analysis/violin_QHERO_MIC.csv')
    errors=pd.read_csv(V10/'analysis/violin_OOF_errors.csv')
    paired=pd.read_csv(V10/'analysis/violin_paired_error.csv')
    fig,axes=plt.subplots(2,2,figsize=(14,10.5),gridspec_kw={'hspace':.48,'wspace':.30})
    ax=axes[0,0];ticks=[]
    for i,group in enumerate(['Gram+','Gram-','Fungal']):
        counts=[]
        for n,color,side in [(1,style.PALETTE['blue'],'left'),(2,style.PALETTE['orange'],'right')]:
            values=source[(source.Organism_class==group)&(source.cationic_N==n)].log2_mic.values
            counts.append(violin(ax,values,i,color,side))
        ticks.append(group+f'\nmono n={counts[0]}\nbis n={counts[1]}')
    ax.set_xticks(range(3));ax.set_xticklabels(ticks);ax.set_ylabel('MIC (µM; logarithmic spacing)')
    ax.set_title('a) Source MIC by organism class',loc='left')
    ax.set_yticks([-2,0,2,4,6,8,10,12,14,16]);ax.set_yticklabels(['0.25','1','4','16','64','256','1024','4096','16384','65536'])
    ax.legend(handles=[Patch(facecolor=style.PALETTE['blue'],alpha=.48,label='mono: one cationic N'),
                       Patch(facecolor=style.PALETTE['orange'],alpha=.48,label='bis: two cationic N')],fontsize=9)
    ax=axes[0,1];ticks=[]
    for i,(n,color,label) in enumerate([(1,style.PALETTE['blue'],'mono'),(2,style.PALETTE['orange'],'bis'),(3,style.PALETTE['purple'],'≥3 cationic N')]):
        sub=target[target.cationic_N>=3] if n==3 else target[target.cationic_N==n]
        count=violin(ax,sub.y.values,i,color);ticks.append(label+f'\nn={count}')
    ax.set_xticks(range(3));ax.set_xticklabels(ticks);ax.set_title('b) External Q-HERO measured MIC',loc='left')
    ax.set_ylabel('MIC (µM; logarithmic spacing)');ax.set_yticks([-2,0,2,4,6,8]);ax.set_yticklabels(['0.25','1','4','16','64','256'])
    models=['molformer','c3-molformer','chemberta100m','chemfm1b']
    names=['MolFormer-XL','c3-MoLFormer','ChemBERTa-100M','ChemFM-1B']
    ax=axes[1,0]
    for i,backbone in enumerate(models):
        for arm,color,side in [('expert',style.PALETTE['human'],'left'),('quant-continuous',style.PALETTE['continuous'],'right')]:
            violin(ax,errors[(errors.backbone==backbone)&(errors.arm==arm)].absolute_error,i,color,side)
    ax.set_xticks(range(4));ax.set_xticklabels(names,rotation=12,ha='right')
    ax.set_title('c) Errors on the same held-out molecules',loc='left');ax.set_ylabel('Mean absolute log2 MIC error per molecule')
    ax.legend(handles=[Patch(facecolor=style.PALETTE['human'],alpha=.48,label='Human binary supervision'),
                       Patch(facecolor=style.PALETTE['continuous'],alpha=.48,label='Continuous MIC supervision')],fontsize=9)
    ax=axes[1,1]
    for i,backbone in enumerate(models):
        values=paired[paired.backbone==backbone].expert_minus_MIC.values
        violin(ax,values,i,style.PALETTE['human'])
        rng=np.random.default_rng(1729+i);ax.scatter(i+rng.uniform(-.19,.19,len(values)),values,s=5,
                                                     alpha=.15,color=style.PALETTE['human'],rasterized=True)
    ax.axhline(0,color='#8b9196',ls='--',lw=.9);ax.set_xticks(range(4));ax.set_xticklabels(names,rotation=12,ha='right')
    ax.set_title('d) Paired error difference per molecule',loc='left')
    ax.set_ylabel('|error| human − |error| continuous MIC\n(log2 µM; negative favours human)')
    for ax in axes.flat:ax.grid(axis='y',alpha=.6)
    fig.text(.5,.015,'Bars: median and IQR. MIC KDEs use log2 coordinates. Error distributions use identical held-out molecules.\nDescriptive distributions; no independent-record tests or biological causal interpretation.',ha='center',fontsize=9)
    fig.subplots_adjust(top=.94,bottom=.14);save(fig,'figure4_MIC_error_violins')


def matched_violins():
    p=pd.read_csv(OLD/'results/predictions.csv')
    p=p[(p.target=='Q-HERO-405')&p.arm.isin(['expert','quant-continuous'])].copy();p['ae']=abs(p.y-p.pred)
    values=p.groupby(['arm','can']).ae.mean().unstack('arm').sort_index()
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.7))
    for arm,color,side in [('expert',style.PALETTE['human'],'left'),('quant-continuous',style.PALETTE['continuous'],'right')]:
        violin(axes[0],values[arm],0,color,side,width=.6)
    axes[0].set_xticks([0]);axes[0].set_xticklabels(['Same 405 Q-HERO structures'])
    axes[0].set_ylabel('Absolute MIC prediction error (log2 µM)')
    axes[0].set_title('a) Matched partial-fine-tuning error',loc='left')
    axes[0].legend(handles=[Patch(facecolor=style.PALETTE['human'],alpha=.48,label='Human'),
                           Patch(facecolor=style.PALETTE['continuous'],alpha=.48,label='Continuous MIC')],frameon=False)
    delta=values.expert-values['quant-continuous']
    axes[1].hist(delta,bins=27,color=style.PALETTE['blue'],edgecolor='white')
    axes[1].axvline(0,color='#8b9196',ls='--');axes[1].set_xlabel('Human − continuous MIC absolute error (log2 µM)')
    axes[1].set_ylabel('Structures');axes[1].set_title('b) Within-structure error difference',loc='left')
    fig.text(.5,.01,'Absolute errors averaged across five source seeds per structure; descriptive distributions.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.045,1,1]);save(fig,'figureS18_matched_finetuning_error_violins')


def parity():
    pred=pd.read_csv(OLD/'results/predictions.csv')
    summary=pd.read_csv(OLD/'analysis/summary.csv')
    targets=['QAC-104','Q-HERO-405','OOD-17']
    arms=['expert','quant-continuous','quant-binary']
    labels=['Human supervision','Continuous MIC supervision','Binary MIC supervision']
    colors=[style.PALETTE[k] for k in ['human','continuous','binary']]
    fig,axes=plt.subplots(3,3,figsize=(11.6,10.8),constrained_layout=True)
    rows=[]
    for i,target in enumerate(targets):
        sub=pred[(pred.target==target)&pred.arm.isin(arms)]
        bounds=[min(sub.y.min(),sub.pred.min())-.35,max(sub.y.max(),sub.pred.max())+.35]
        for j,(arm,label,color) in enumerate(zip(arms,labels,colors)):
            ax=axes[i,j];g=sub[sub.arm==arm].groupby('can').agg(y=('y','first'),pred=('pred','mean'),seeds=('seed','nunique')).reset_index()
            assert (g.seeds==5).all()
            s=summary[(summary.target==target)&(summary.arm==arm)].iloc[0]
            ax.scatter(g.y,g.pred,s=18 if len(g)>100 else 32,color=color,alpha=.65,edgecolors='white',linewidths=.35)
            ax.plot(bounds,bounds,color='#b9bec3',ls='--',lw=.8)
            ax.set_xlim(bounds);ax.set_ylim(bounds);ax.set_aspect('equal');ax.grid(alpha=.6)
            ax.text(.035,.97,f'Mean seed R² = {s.R2:.3f}\nMean seed RMSE = {s.RMSE:.3f}',
                    transform=ax.transAxes,va='top',fontsize=9,
                    bbox=dict(boxstyle='round,pad=.25',fc='white',ec='#d2d5d8',lw=.6))
            if i==0:ax.set_title(label)
            if j==0:ax.set_ylabel(target+'\nPredicted log2 MIC (µM)')
            if i==2:ax.set_xlabel('Measured log2 MIC (µM)')
            rows.append(g.assign(target=target,arm=arm))
    save(fig,'figureS21_MIC_parity_cohorts')
    pd.concat(rows,ignore_index=True).to_csv(ROOT/'analysis/parity_display_values.csv',index=False)


if __name__=='__main__':main()
