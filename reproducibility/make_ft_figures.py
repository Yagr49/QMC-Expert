"""Figures for the fine-tuning report."""
import numpy as np, pandas as pd, matplotlib, os, json, warnings
matplotlib.use('Agg'); warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
FT='reproducibility/finetune'; F='reproducibility/figures'; os.makedirs(F,exist_ok=True)
S1,S2,S3='#2a78d6','#eb6834','#1baf7a'
INK,INK2,MUTED,SURF='#0b0b0b','#52514e','#8a8984','#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':MUTED,
 'axes.linewidth':.8,'xtick.color':INK2,'ytick.color':INK2,'text.color':INK,
 'axes.labelcolor':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF,'legend.frameon':False})
def save(fig,n):
    for e in ('svg','png','pdf'): fig.savefig(f'{F}/{n}.{e}',bbox_inches='tight',dpi=300 if e=='png' else None,facecolor=SURF)
    plt.close(fig); print('  ',n)
def despine(ax,ax_grid='y'):
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.grid(axis=ax_grid,color='#e6e5e0',lw=.7); ax.set_axisbelow(True)
T=['QAC-105','Q-HERO','OOD-17']

# ---- F7: representation quality ----
d=pd.DataFrame([json.loads(l) for l in open(f'{FT}/runs.jsonl')])
order=['6 descriptors','MolFormer frozen','FT expert-binary','FT quant-molecule','FT quant-record']
lab=['6 descriptors\n(null)','MolFormer\nfrozen','fine-tuned\n740 binary','fine-tuned\n1153 values','fine-tuned\n9338 values']
col=[MUTED,'#9aa3ae',S1,S2,S3]
fig,ax=plt.subplots(figsize=(8.6,3.5))
x=np.arange(3); w=.16
for k,(r,c) in enumerate(zip(order,col)):
    m=[d[(d.representation==r)&(d.target==t)].R2.mean() for t in T]
    s=[d[(d.representation==r)&(d.target==t)].R2.std() for t in T]
    s=[0 if np.isnan(v) else v for v in s]
    ax.bar(x+(k-2)*w,m,w*.88,color=c,label=lab[k],yerr=s,error_kw=dict(ecolor=INK2,lw=.9,capsize=2))
    for xi,v,sd in zip(x+(k-2)*w,m,s):
        ax.text(xi,v+(sd+.012 if v>=0 else -sd-.04),f'{v:+.2f}',ha='center',fontsize=7,color=INK)
ax.axhline(0,color=INK2,lw=1)
ax.text(2.46,.012,'predict-the-mean',fontsize=7.5,color=MUTED,ha='right')
ax.set_xticks(x); ax.set_xticklabels(T,fontsize=10)
ax.set_ylabel('R²  (mean ± sd, 3 seeds)'); ax.set_ylim(-.55,.42)
ax.legend(fontsize=8,ncol=5,loc='upper center',bbox_to_anchor=(.5,1.16))
ax.set_title('Fine-tuning lifts every target above the frozen baseline',loc='left',fontsize=10.5,pad=26)
despine(fig.axes[0]); fig.tight_layout(); save(fig,'figS7_representation_quality')

# ---- F8: zero-shot rank vs R2 ----
dd=pd.DataFrame([json.loads(l) for l in open(f'{FT}/runs_direct.jsonl')])
dd=dd[dd.representation.str.startswith('FT')]
dd['src']=dd.source
fig,axes=plt.subplots(1,2,figsize=(9.2,3.4))
srcs=['expert-binary','quant-molecule','quant-record']
slab=['740 binary\nexpert labels','1153\nMIC values','9338\nMIC values']
for ax,metric,ylab,lo,hi in [(axes[0],'rank_agreement','Spearman ρ with true log₂ MIC',-.05,1.0),
                             (axes[1],'R2','R²  (raw predictions)',-5.0,.6)]:
    for k,(s,c) in enumerate(zip(srcs,[S1,S2,S3])):
        m=[dd[(dd.src==s)&(dd.target==t)][metric].mean() for t in T]
        e=[dd[(dd.src==s)&(dd.target==t)][metric].std() for t in T]
        if all(np.isnan(v) for v in m): continue
        e=[0 if np.isnan(v) else v for v in e]
        ax.bar(x+(k-1)*.24,m,.22,color=c,label=slab[k],yerr=e,error_kw=dict(ecolor=INK2,lw=.9,capsize=2))
    ax.axhline(0,color=INK2,lw=1)
    ax.set_xticks(x); ax.set_xticklabels(T,fontsize=9.5); ax.set_ylabel(ylab); ax.set_ylim(lo,hi)
    despine(ax)
axes[0].legend(fontsize=8,loc='upper left')
axes[0].set_title('Ranking transfers',loc='left',fontsize=10)
axes[1].set_title('Absolute values do not',loc='left',fontsize=10)
fig.suptitle('Zero-shot inference: the fine-tuned head predicts the target directly',
             x=.005,ha='left',fontsize=10.5,y=1.04)
fig.tight_layout(); save(fig,'figS8_zeroshot')

# ---- F9: calibration ----
p=pd.read_csv(f'{FT}/predictions_seed0.csv'); p=p[p.source=='quant-record']
rc=pd.read_csv(f'{FT}/recalibration.csv'); rc=rc[rc.source=='quant-record']
fig,axes=plt.subplots(1,3,figsize=(10.2,3.3))
for ax,t in zip(axes[:2],['Q-HERO','OOD-17']):
    s=p[p.target==t]
    lim=[min(s.y.min(),s.pred.min())-.4,max(s.y.max(),s.pred.max())+.4]
    ax.plot(lim,lim,color=MUTED,lw=1,ls='--',zorder=1)
    ax.scatter(s.y,s.pred,s=26,color=S3,alpha=.55,edgecolor='white',linewidth=.5,zorder=3)
    b,a=np.polyfit(s.y,s.pred,1)
    xs=np.array(lim); ax.plot(xs,a+b*xs,color=S2,lw=2,zorder=4)
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect('equal')
    ax.set_xlabel('true log₂ MIC (µM)'); ax.set_title(f'{t}  (n = {len(s)})',loc='left',fontsize=9.5)
    off=s.pred.mean()-s.y.mean()
    ax.text(.04,.95,f'offset {off:+.2f} log₂\n({2**off:.1f}× MIC)',transform=ax.transAxes,
            va='top',fontsize=8.5,color=INK)
    despine(ax,'both')
axes[0].set_ylabel('predicted log₂ MIC (µM)')
ax=axes[2]
g=rc.groupby('target')[['raw_R2','recal_R2']].mean().reindex(T)
xx=np.arange(3)
ax.bar(xx-.17,g.raw_R2,.32,color=MUTED,label='as predicted')
ax.bar(xx+.17,g.recal_R2,.32,color=S1,label='after affine\nrecalibration')
for xi,v in zip(xx-.17,g.raw_R2): ax.text(xi,v-.22,f'{v:.2f}',ha='center',fontsize=7.5,color=INK)
for xi,v in zip(xx+.17,g.recal_R2): ax.text(xi,v+.08,f'{v:+.2f}',ha='center',fontsize=7.5,color=INK)
ax.axhline(0,color=INK2,lw=1)
ax.set_xticks(xx); ax.set_xticklabels(T,fontsize=9); ax.set_ylabel('R²'); ax.set_ylim(-3.6,.95)
ax.legend(fontsize=8,loc='lower left'); ax.set_title('Two parameters recover it',loc='left',fontsize=9.5)
despine(ax)
fig.suptitle('The failure is calibration, not signal  —  model fine-tuned on 9338 literature MIC values',
             x=.005,ha='left',fontsize=10.5,y=1.04)
fig.tight_layout(); save(fig,'figS9_calibration')
print('done')
