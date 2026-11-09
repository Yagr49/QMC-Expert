from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'figures';O.mkdir(exist_ok=True)
P=pd.read_csv(R/'analysis/contrasts.csv');P=P[(P.target=='Q-HERO-405')&(P.unit=='seed+scaffold')]
models=['molformer','c3-molformer','chemberta100m','chemfm1b'];names=['MolFormer-XL','c3-MoLFormer','ChemBERTa-100M','ChemFM-1B']
plt.rcParams.update({'font.size':10,'axes.spines.right':False,'axes.spines.top':False,'font.family':'DejaVu Sans','pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1,1.3]})
for j,m in enumerate(models):
    p=P[(P.backbone==m)&(P.panel=='matched-pooled')&(P.comparison=='expert minus expert-shuffled')].iloc[0]
    axes[0].errorbar(p.delta_RMSE,j,xerr=[[p.delta_RMSE-p.ci_low],[p.ci_high-p.delta_RMSE]],fmt='o',color='#216a9c',capsize=4)
axes[0].set_yticks(range(4));axes[0].set_yticklabels(names);axes[0].invert_yaxis();axes[0].set_title('a  Human labels versus shuffled labels\n681 identical source molecules',loc='left',fontweight='bold')
comparisons=['quant-pooled minus quant-sa','quant-pooled minus quant-pooled-shuffled','expert minus quant-pooled','expert minus raw-molformer']
labels=['Pooled MIC − exact S. aureus MIC','Pooled MIC − shuffled pooled MIC','Human − pooled MIC','Human − raw MolFormer']
for j,c in enumerate(comparisons):
    p=P[(P.panel=='context')&(P.comparison==c)].iloc[0]
    axes[1].errorbar(p.delta_RMSE,j,xerr=[[p.delta_RMSE-p.ci_low],[p.ci_high-p.delta_RMSE]],fmt='o',color='#a05a2c',capsize=4)
axes[1].set_yticks(range(4));axes[1].set_yticklabels(labels);axes[1].invert_yaxis();axes[1].set_title('b  Context sensitivity\n529 identical source molecules',loc='left',fontweight='bold')
for ax in axes:
    ax.axvline(0,color='.45',ls='--',lw=1);ax.set_xlabel('ΔRMSE on Q-HERO-405 (log₂ µM)');ax.grid(axis='x',alpha=.18);ax.set_ylim(3.5,-.5)
fig.suptitle('Supervision effects depend on backbone and source context',fontsize=14,fontweight='bold')
fig.text(.5,.015,'Negative values favour the first arm. 95% paired seed/scaffold bootstrap; fixed target folds; exploratory, unadjusted.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.055,1,.94])
for ext in ['png','pdf','svg']:fig.savefig(O/('figure8_modern_context.'+ext),dpi=250,bbox_inches='tight')
print(O)
