from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import gaussian_kde
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
R=Path(__file__).resolve().parent;O=R/'figures'
old=pd.read_csv(R.parent/'finetune/predictions_seed0.csv');q=pd.read_csv(R/'data/target_Q-HERO-405.csv')
d=old[(old.source=='expert-binary')&(old.target=='Q-HERO')].merge(q[['can']],on='can',validate='one_to_one');assert len(d)==405
d['predicted_class']=np.where(d.pred>=0,'Predicted Good','Predicted Bad')
d.to_csv(R/'analysis/direct_expert_violin_seed0.csv',index=False)
records=pd.DataFrame([json.loads(t) for t in (R.parent/'finetune/runs_direct.jsonl').read_text().splitlines()])
records=records[(records.target=='Q-HERO')&records.representation.str.startswith('FT')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.right':False,'axes.spines.top':False,'pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(11,5))
ax=axes[0];colors=['#9b758d','#418b82'];counts=[]
for i,name in enumerate(['Predicted Bad','Predicted Good']):
    y=d[d.predicted_class==name].y.values;counts.append(len(y));grid=np.linspace(y.min(),y.max(),240);v=gaussian_kde(y)(grid);v=v/v.max()*.3;ax.fill_betweenx(grid,i-v,i+v,color=colors[i],alpha=.4,edgecolor=colors[i],lw=1.3);q25,med,q75=np.quantile(y,[.25,.5,.75]);ax.plot([i,i],[q25,q75],color=colors[i],lw=3);ax.plot([i-.11,i+.11],[med,med],color=colors[i],lw=3)
ax.set_xticks([0,1]);ax.set_xticklabels([f'Predicted Bad\nn={counts[0]}',f'Predicted Good\nn={counts[1]}']);ax.set_ylabel('Measured MIC (µM; logarithmic spacing)');ax.set_yticks([-2,0,2,4,6,8]);ax.set_yticklabels(['0.25','1','4','16','64','256']);ax.set_title('A   Direct expert-score transfer\nNo concentration targets or target refitting',loc='left',fontweight='bold')
ax=axes[1];names=['expert-binary','quant-molecule','quant-record'];labels=['Human binary','Molecule MIC','Record MIC']
for i,name in enumerate(names):
    y=records[records.source==name].rank_agreement.values;assert len(y)==3
    ax.scatter(i+np.linspace(-.08,.08,3),y,color=['#77598e','#418b82','#3b729d'][i],s=40);ax.errorbar(i,y.mean(),yerr=y.std(ddof=1),color='.25',fmt='_',markersize=18,capsize=4)
ax.axhline(0,color='.5',ls='--',lw=1);ax.set_xticks(range(3));ax.set_xticklabels(labels);ax.set_ylabel('Direct rank agreement with measured MIC');ax.set_title('B   Archived Q-HERO-411 direct ranking\nThree checkpoints; mean ± seed SD',loc='left',fontweight='bold');ax.set_ylim(0,.85)
for ax in axes:ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.text(.5,.012,'A: one archived expert checkpoint (seed 0), fixed class threshold logit=0; Q-HERO-405 subset.\nB: original 411-molecule cohort. Panels are descriptive, use different cohorts, and do not establish quantitative calibration or causality.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.1,1,1])
for ext in ['png','pdf','svg']:fig.savefig(O/('figureS11_direct_expert_violin.'+ext),dpi=300,bbox_inches='tight')
print(counts)
