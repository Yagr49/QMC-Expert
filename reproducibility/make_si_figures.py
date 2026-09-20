"""Supplementary figures. Emits SVG (for the SI document) and PNG/PDF (for submission)."""
import numpy as np, pandas as pd, matplotlib, os, warnings
matplotlib.use('Agg'); warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

R='reproducibility'; F=f'{R}/figures'; os.makedirs(F,exist_ok=True)
S1,S2,S3='#2a78d6','#eb6834','#1baf7a'          # validated categorical slots 1-3
INK,INK2,MUTED='#0b0b0b','#52514e','#8a8984'
SURF='#fcfcfb'
REPS=['expert (Good/Bad)','multi-regression','MolFormer (raw)']
COL=dict(zip(REPS,[S1,S2,S3]))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':MUTED,
    'axes.linewidth':.8,'xtick.color':INK2,'ytick.color':INK2,'text.color':INK,
    'axes.labelcolor':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF,
    'xtick.major.size':3,'ytick.major.size':3,'legend.frameon':False})
def save(fig,name):
    for ext in ('svg','png','pdf'):
        fig.savefig(f'{F}/{name}.{ext}',bbox_inches='tight',dpi=300 if ext=='png' else None,
                    facecolor=SURF)
    plt.close(fig); print('  ',name)
def despine(ax,keep=('left','bottom')):
    for s in ('top','right','left','bottom'):
        ax.spines[s].set_visible(s in keep)
    ax.grid(axis='y',color='#e6e5e0',lw=.7); ax.set_axisbelow(True)

# ---------- S1: expert annotation set ----------
e=pd.read_csv(f'{R}/expert_labels/expert_labels_1103.csv') if os.path.exists(f'{R}/expert_labels/expert_labels_1103.csv') else pd.read_csv('expert_labels/expert_labels_1103.csv')
fig,axes=plt.subplots(1,3,figsize=(9.2,2.9))
ax=axes[0]
ct=e.groupby(['batch','label']).size().unstack(fill_value=0)[['Bad','Good']]
b=np.arange(len(ct)); w=.55
ax.bar(b,ct.Bad,w,color=MUTED,label='Bad')
ax.bar(b,ct.Good,w,bottom=ct.Bad,color=S1,label='Good')
for i,(bd,gd) in enumerate(zip(ct.Bad,ct.Good)):
    ax.text(i,bd/2,str(bd),ha='center',va='center',color='white',fontsize=8.5)
    ax.text(i,bd+gd/2,str(gd),ha='center',va='center',color='white',fontsize=8.5)
    ax.text(i,bd+gd+18,f'{gd/(bd+gd)*100:.1f}% Good',ha='center',color=INK,fontsize=8.5)
ax.set_xticks(b); ax.set_xticklabels(['batch A\n2025-12-15','batch B\n2026-02-11'])
ax.set_ylabel('compounds'); ax.set_ylim(0,780); ax.set_title('Class balance by round',loc='left',fontsize=9.5)
ax.legend(loc='upper center',fontsize=8,ncol=2,bbox_to_anchor=(.5,1.02)); despine(ax)
ax=axes[1]
q=[int((e.parsed&~e.repair_applied).sum()),int(e.repair_applied.sum()),int((~e.parsed).sum())]
lab=['parse as\nsupplied','required\nrepair','unparseable']
bars=ax.bar(range(3),q,.55,color=[S3,S2,'#e34948'])
for i,v in enumerate(q): ax.text(i,v+18,str(v),ha='center',color=INK,fontsize=8.5)
ax.set_xticks(range(3)); ax.set_xticklabels(lab); ax.set_ylabel('SMILES')
ax.set_ylim(0,1150); ax.set_title('SMILES validity (RDKit)',loc='left',fontsize=9.5); despine(ax)
ax=axes[2]
sub=e[~e.parsed|e.repair_applied].groupby('batch').size().reindex(['A_2025-12-15','B_2026-02-11']).fillna(0)
ax.bar(range(2),sub.values,.55,color=S2)
for i,v in enumerate(sub.values): ax.text(i,v+2,str(int(v)),ha='center',color=INK,fontsize=8.5)
ax.set_xticks(range(2)); ax.set_xticklabels(['batch A','batch B']); ax.set_ylabel('malformed SMILES')
ax.set_ylim(0,120); ax.set_title('Defects concentrate in batch B',loc='left',fontsize=9.5); despine(ax)
fig.tight_layout(); save(fig,'figS1_expert_set')

# ---------- S2: dataset overlap ----------
names=['expert-1103','QMR-quant','QAC-105','Q-HERO','OOD-17']
M=np.array([[1066,1035,105,222,0],[1035,1515,99,255,0],[105,99,105,1,0],
            [222,255,1,411,0],[0,0,0,0,17]])
fig,ax=plt.subplots(figsize=(4.6,3.9))
norm=M/np.maximum(np.diag(M)[None,:],1)
im=ax.imshow(np.where(np.eye(5,dtype=bool),np.nan,norm),cmap='Blues',vmin=0,vmax=1)
for i in range(5):
    for j in range(5):
        v=M[i,j]; on_diag=i==j
        frac=v/M[j,j] if M[j,j] else 0
        ax.text(j,i,f'{v}',ha='center',va='center',fontsize=9,
                color=(MUTED if on_diag else ('white' if frac>.55 else INK)),
                fontweight='normal' if on_diag else ('bold' if frac>.9 and not on_diag else 'normal'))
ax.set_xticks(range(5)); ax.set_xticklabels(names,rotation=35,ha='right',fontsize=8.5)
ax.set_yticks(range(5)); ax.set_yticklabels(names,fontsize=8.5)
ax.set_title('Shared molecules between datasets',loc='left',fontsize=9.5,pad=9)
ax.text(0,-.95,'diagonal = set size; cell = |row ∩ column|',fontsize=8,color=MUTED)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks(np.arange(-.5,5),minor=True); ax.set_yticks(np.arange(-.5,5),minor=True)
ax.grid(which='minor',color=SURF,lw=2.5); ax.tick_params(which='minor',length=0)
fig.tight_layout(); save(fig,'figS2_overlap')
print('done part 1')

# ---------- S3: Q-HERO residual violins ----------
rs=pd.read_csv(f'{R}/qhero/qhero_residuals.csv')
fig,axes=plt.subplots(1,2,figsize=(8.4,3.4),sharey=True)
for ax,subset in zip(axes,['all Q-HERO','unseen by expert encoder']):
    d=rs[rs.subset==subset]
    data=[d[d.representation==r].abs_residual.values for r in REPS]
    vp=ax.violinplot(data,positions=range(3),widths=.72,showextrema=False,showmedians=False)
    for body,r,dd in zip(vp['bodies'],REPS,data):
        body.set_facecolor(COL[r]); body.set_alpha(.30); body.set_edgecolor(COL[r]); body.set_linewidth(1.6)
        # clip the KDE tails to the observed range
        v=body.get_paths()[0].vertices
        v[:,1]=np.clip(v[:,1],dd.min(),dd.max())
    bp=ax.boxplot(data,positions=range(3),widths=.13,patch_artist=True,showfliers=False,
                  medianprops=dict(color='white',lw=1.6),whiskerprops=dict(color=INK2,lw=1),
                  capprops=dict(lw=0),boxprops=dict(lw=0))
    for patch,r in zip(bp['boxes'],REPS): patch.set_facecolor(COL[r])
    for i,r in enumerate(REPS):
        med=np.median(data[i])
        ax.text(i+.13,med,f'  {med:.2f}',ha='left',va='center',color=INK,fontsize=8.5)
    ax.set_xticks(range(3)); ax.set_xticklabels(['expert\n(Good/Bad)','multi-\nregression','MolFormer\n(raw)'],fontsize=8.5)
    ax.set_title(f'{subset}  (n = {d.groupby("representation").size().iloc[0]})',loc='left',fontsize=9.5)
    despine(ax); ax.set_ylim(-.15,6.1)
axes[0].set_ylabel('|residual|, log₂ units')
axes[0].text(-.45,5.75,'labels = median |residual|',fontsize=8,color=MUTED,ha='left')
fig.suptitle('Q-HERO external benchmark — scaffold-split cross-validated residuals (S. aureus MIC)',
             x=.005,ha='left',fontsize=10.5,y=1.04)
fig.tight_layout(); save(fig,'figS3_qhero_violins')

# ---------- S4: Q-HERO R2 ----------
m=pd.read_csv(f'{R}/qhero/qhero_metrics.csv')
fig,axes=plt.subplots(1,2,figsize=(8.4,3.2),sharey=True)
for ax,split in zip(axes,['random 5-fold','scaffold 5-fold']):
    d=m[m.split==split]; x=np.arange(2); w=.26
    for k,r in enumerate(REPS):
        sub=d[d.representation==r].set_index('subset').reindex(['all Q-HERO','unseen by expert encoder'])
        ax.bar(x+(k-1)*w,sub.R2_mean,w*.9,color=COL[r],label=r,
               yerr=sub.R2_sd,error_kw=dict(ecolor=INK2,lw=.9,capsize=2.5))
        for xi,v,sd in zip(x+(k-1)*w,sub.R2_mean,sub.R2_sd):
            ax.text(xi,v+(sd+.018 if v>=0 else -sd-.045),f'{v:.2f}',ha='center',fontsize=7.6,color=INK)
    ax.axhline(0,color=INK2,lw=.9)
    ax.set_xticks(x); ax.set_xticklabels(['all\nQ-HERO','unseen by\nexpert encoder'],fontsize=8.5)
    ax.set_title(split,loc='left',fontsize=9.5); despine(ax); ax.set_ylim(-.16,.57)
axes[0].set_ylabel('R²  (mean ± sd, 5 seeds)')
axes[1].legend(fontsize=8,loc='upper right')
fig.suptitle('Q-HERO: no representation beats raw MolFormer',x=.005,ha='left',fontsize=10.5,y=1.03)
fig.tight_layout(); save(fig,'figS4_qhero_r2')
print('done part 2')

# ---------- S5: OOD equivalence ----------
from scipy import stats
pr=pd.read_csv(f'{R}/causal/ood_paired_residuals.csv')
per=pr.groupby('mol').delta_expert_minus_reg.mean()
n=len(per); mn=per.mean(); se=per.std(ddof=1)/np.sqrt(n)
fig,axes=plt.subplots(1,2,figsize=(10.2,3.6),gridspec_kw={'width_ratios':[1.15,1]})
ax=axes[0]
o=per.sort_values()
ax.barh(range(n),o.values,.62,color=[S1 if v<0 else S2 for v in o.values])
ax.axvline(0,color=INK2,lw=.9)
ax.set_yticks(range(n)); ax.set_yticklabels([f'#{i+1}' for i in o.index],fontsize=7)
ax.set_xlabel('Δ|residual| = expert − regression  (log₂ units)')
ax.set_title('Per-compound paired difference (17 OOD compounds)',loc='left',fontsize=9.5,pad=17)
ax.text(.02,1.005,'← expert better',transform=ax.transAxes,color=S1,fontsize=8.5)
ax.text(.98,1.005,'regression better →',transform=ax.transAxes,color=S2,fontsize=8.5,ha='right')
despine(ax,keep=('bottom',)); ax.grid(axis='x',color='#e6e5e0',lw=.7); ax.grid(axis='y',lw=0)
ax=axes[1]
margins=[1.0,0.5,0.25]; ci90=stats.t.interval(0.90,n-1,loc=mn,scale=se)
for i,mg in enumerate(margins):
    t_lo=(mn+mg)/se; t_hi=(mn-mg)/se
    p=max(stats.t.sf(t_lo,n-1),stats.t.cdf(t_hi,n-1))
    ok=p<0.05
    ax.plot([-mg,mg],[i,i],lw=9,solid_capstyle='butt',color='#eceae4')
    ax.plot(ci90,[i,i],lw=3,color=S1 if ok else '#e34948',solid_capstyle='round')
    ax.plot([mn],[i],'o',ms=7,color=S1 if ok else '#e34948',mec='white',mew=1.4)
    ax.text(1.14,i,f'±{mg}    p = {p:.3f}    {"equivalent" if ok else "not shown"}',
            va='center',fontsize=8.5,color=INK if ok else '#e34948')
ax.axvline(0,color=INK2,lw=.9,zorder=0)
ax.set_yticks([]); ax.set_ylim(-.6,2.9); ax.set_xlim(-1.18,2.85)
ax.set_xticks([-1,-.5,0,.5,1])
ax.set_xlabel('Δ|residual|  (log₂ units)')
ax.set_title('TOST equivalence, 90% CI',loc='left',fontsize=9.5,pad=17)
ax.text(-1.18,2.62,f'mean Δ = {mn:+.3f}    90% CI [{ci90[0]:+.2f}, {ci90[1]:+.2f}]',
        ha='left',fontsize=8.5,color=MUTED)
ax.text(2.82,-.55,'grey band = equivalence margin',ha='right',fontsize=7.8,color=MUTED)
despine(ax,keep=('bottom',)); ax.grid(axis='x',color='#e6e5e0',lw=.7); ax.grid(axis='y',lw=0)
fig.tight_layout(); save(fig,'figS5_equivalence')

# ---------- S6: in-domain split effect ----------
t2=pd.read_csv(f'{R}/table2/table2_rebuild.csv')
t2['representation']=t2.representation.replace({'human (Good/Bad)':'expert (Good/Bad)'})
assert set(REPS)<=set(t2.representation), sorted(t2.representation.unique())
EPS=['S. aureus MIC','S. aureus MBC','E. coli MIC','E. coli MBC']
fig,axes=plt.subplots(1,2,figsize=(8.6,3.2),sharey=True)
for ax,(sp,lab) in zip(axes,[('pairs','random split over (molecule, endpoint) pairs'),
                             ('mol','grouped split by molecule')]):
    d=t2[t2.split==sp]; x=np.arange(4); w=.26
    for k,r in enumerate(REPS):
        sub=d[d.representation==r].set_index('endpoint').reindex(EPS)
        ax.bar(x+(k-1)*w,sub.R2_mean,w*.9,color=COL[r],label=r,
               yerr=sub.R2_sd,error_kw=dict(ecolor=INK2,lw=.9,capsize=2))
    ax.axhline(0,color=INK2,lw=.9)
    ax.set_xticks(x); ax.set_xticklabels(['S.a.\nMIC','S.a.\nMBC','E.c.\nMIC','E.c.\nMBC'],fontsize=8.5)
    ax.set_title(lab,loc='left',fontsize=9.5); despine(ax); ax.set_ylim(-.22,.95)
axes[0].set_ylabel('R²  (mean ± sd, 10 seeds)'); axes[0].legend(fontsize=8,loc='upper left')
fig.suptitle('QAC-105 in-domain: the split, not the representation, drives the numbers',
             x=.005,ha='left',fontsize=10.5,y=1.03)
fig.tight_layout(); save(fig,'figS6_split_effect')
print('done part 3')
