"""Submission-safe v8 variants of fine-tuning figures.

Original figure assets are intentionally untouched.  These variants fix terminology
and scope while reproducing values directly from the archived result files.
"""
import json, os, warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
FT = 'reproducibility/finetune'
OUT = 'reproducibility/figures/v8'
os.makedirs(OUT, exist_ok=True)
S1, S2, S3 = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, MUTED, SURF = '#0b0b0b', '#52514e', '#8a8984', '#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':MUTED,
 'axes.linewidth':.8,'xtick.color':INK2,'ytick.color':INK2,'text.color':INK,
 'axes.labelcolor':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF,'legend.frameon':False})
T = ['QAC-105', 'Q-HERO', 'OOD-17']

def save(fig, name):
    for ext in ('svg', 'png', 'pdf'):
        fig.savefig(f'{OUT}/{name}.{ext}', bbox_inches='tight', dpi=300 if ext == 'png' else None, facecolor=SURF)
    plt.close(fig)

def despine(ax, grid='y'):
    for side in ('top','right'): ax.spines[side].set_visible(False)
    ax.grid(axis=grid, color='#e6e5e0', lw=.7); ax.set_axisbelow(True)

# S7: representation quality
d = pd.DataFrame([json.loads(line) for line in open(f'{FT}/runs.jsonl')])
order = ['6 descriptors','MolFormer frozen','FT expert-binary','FT quant-molecule','FT quant-record']
labels = ['6 descriptors\n(null)', 'MolFormer\nfrozen', 'partial FT\n740 expert labels',
          'partial FT\n1153 molecules', 'partial FT\n9338 records']
colors = [MUTED, '#9aa3ae', S1, S2, S3]
fig, ax = plt.subplots(figsize=(9.1,3.6)); x = np.arange(3); w = .16
for k, (rep, label, color) in enumerate(zip(order, labels, colors)):
    mean = [d[(d.representation==rep)&(d.target==t)].R2.mean() for t in T]
    sd = [d[(d.representation==rep)&(d.target==t)].R2.std() for t in T]
    sd = [0 if np.isnan(v) else v for v in sd]
    ax.bar(x+(k-2)*w, mean, w*.88, color=color, label=label, yerr=sd,
           error_kw=dict(ecolor=INK2,lw=.9,capsize=2))
    for xi, val, err in zip(x+(k-2)*w,mean,sd):
        ax.text(xi, val+(err+.012 if val>=0 else -err-.04), f'{val:+.2f}', ha='center', fontsize=7)
ax.axhline(0,color=INK2,lw=1); ax.set_xticks(x); ax.set_xticklabels(T,fontsize=10)
ax.set_ylabel('R² (mean ± SD, 3 seeds)'); ax.set_ylim(-.55,.42)
ax.legend(fontsize=7.5,ncol=5,loc='upper center',bbox_to_anchor=(.5,1.17))
ax.set_title('Partial fine-tuning improves mean representation quality; absolute R² remains modest',loc='left',fontsize=10,pad=27)
ax.text(.99,.02,'OOD-17: n = 17',transform=ax.transAxes,ha='right',va='bottom',fontsize=7.5,color=MUTED)
despine(ax); fig.tight_layout(); save(fig,'figS7_representation_quality_v8')

# S8: direct transfer
dd = pd.DataFrame([json.loads(line) for line in open(f'{FT}/runs_direct.jsonl')])
dd = dd[dd.representation.str.startswith('FT')]; dd['src'] = dd.source
fig, axes = plt.subplots(1,2,figsize=(9.5,3.5)); srcs=['expert-binary','quant-molecule','quant-record']
labels=['740 final\nexpert labels','1153 unique\nmolecules','9338 MIC records\n(1153 molecules)']
for ax, metric, ylabel, lo, hi in [(axes[0],'rank_agreement','Spearman ρ with measured log₂ MIC',-.05,1.0),
                                    (axes[1],'R2','R² (raw direct predictions)',-5.0,.6)]:
    for k,(src,color) in enumerate(zip(srcs,[S1,S2,S3])):
        mean=[dd[(dd.src==src)&(dd.target==t)][metric].mean() for t in T]
        sd=[dd[(dd.src==src)&(dd.target==t)][metric].std() for t in T]
        sd=[0 if np.isnan(v) else v for v in sd]
        ax.bar(x+(k-1)*.24,mean,.22,color=color,label=labels[k],yerr=sd,error_kw=dict(ecolor=INK2,lw=.9,capsize=2))
    ax.axhline(0,color=INK2,lw=1); ax.set_xticks(x); ax.set_xticklabels(T,fontsize=9.5)
    ax.set_ylabel(ylabel); ax.set_ylim(lo,hi); despine(ax)
axes[0].legend(fontsize=7.6,loc='upper left'); axes[0].set_title('Ranking transfers; quantitative is stronger',loc='left',fontsize=9.5)
axes[1].set_title('Absolute values are not calibrated',loc='left',fontsize=9.5)
fig.suptitle('Direct zero-shot transfer (no target refitting; OOD-17 n = 17)',x=.005,ha='left',fontsize=10.5,y=1.04)
fig.tight_layout(); save(fig,'figS8_zeroshot_v8')

# S9: in-sample calibration diagnostic
p = pd.read_csv(f'{FT}/predictions_seed0.csv'); p = p[p.source=='quant-record']
rc = pd.read_csv(f'{FT}/recalibration.csv'); rc = rc[rc.source=='quant-record']
fig,axes=plt.subplots(1,3,figsize=(10.2,3.35))
for ax,target in zip(axes[:2],['Q-HERO','OOD-17']):
    sub=p[p.target==target]; lim=[min(sub.y.min(),sub.pred.min())-.4,max(sub.y.max(),sub.pred.max())+.4]
    ax.plot(lim,lim,color=MUTED,lw=1,ls='--'); ax.scatter(sub.y,sub.pred,s=26,color=S3,alpha=.55,edgecolor='white',linewidth=.5)
    slope,intercept=np.polyfit(sub.y,sub.pred,1); xs=np.array(lim); ax.plot(xs,intercept+slope*xs,color=S2,lw=2)
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect('equal'); ax.set_xlabel('measured log₂ MIC (µM)')
    ax.set_title(f'{target} (n = {len(sub)})',loc='left',fontsize=9.5); despine(ax,'both')
axes[0].set_ylabel('direct prediction, log₂ MIC (µM)')
ax=axes[2]; g=rc.groupby('target')[['raw_R2','recal_R2']].mean().reindex(T); xx=np.arange(3)
ax.bar(xx-.17,g.raw_R2,.32,color=MUTED,label='raw direct')
ax.bar(xx+.17,g.recal_R2,.32,color=S1,label='in-sample affine fit')
for xi,v in zip(xx-.17,g.raw_R2): ax.text(xi,v-.22,f'{v:.2f}',ha='center',fontsize=7.5)
for xi,v in zip(xx+.17,g.recal_R2): ax.text(xi,v+.08,f'{v:+.2f}',ha='center',fontsize=7.5)
ax.axhline(0,color=INK2,lw=1); ax.set_xticks(xx); ax.set_xticklabels(T,fontsize=9); ax.set_ylabel('R²'); ax.set_ylim(-3.6,.95)
ax.legend(fontsize=7.6,loc='lower left'); ax.set_title('Diagnostic only: same-target fit',loc='left',fontsize=9.5); despine(ax)
fig.suptitle('Exploratory in-sample recalibration of direct predictions (9,338 MIC records; 1,153 molecules)',x=.005,ha='left',fontsize=10.2,y=1.04)
fig.tight_layout(); save(fig,'figS9_calibration_v8')
