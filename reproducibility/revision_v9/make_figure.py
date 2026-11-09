import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(ROOT/'runtime/matplotlib')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=ROOT/'figures';out.mkdir(exist_ok=True)
summary=pd.read_csv(ROOT/'analysis/summary.csv')
paired=pd.read_csv(ROOT/'analysis/paired_bootstrap.csv')
assert __import__('json').loads((ROOT/'analysis/analysis_meta.json').read_text())['complete']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axs=plt.subplots(2,2,figsize=(11,8.3),layout='constrained')
colors=['#718096','#146c94','#bd6d28','#96549a']
old=pd.read_json(ROOT.parent/'finetune/runs.jsonl',lines=True)
tags=['MolFormer frozen','FT expert-binary','FT quant-molecule','FT quant-record']
vv=old[old.target=='Q-HERO'].groupby('representation').R2.agg(['mean','std']).loc[tags]
ax=axs[0,0];ax.bar(range(4),vv['mean'],yerr=vv['std'],capsize=4,color=colors,width=.6)
ax.set_xticks(range(4),['Frozen','740 human\nlabels','1,153 MIC\nmolecules','9,338 MIC\nrecords'])
ax.set_ylabel('Q-HERO R² (mean ± seed SD)');ax.set_title('A  Partial fine-tuning: comparable representation quality',loc='left',fontsize=10)
ax.set_ylim(0,.45)
for i,v in enumerate(vv['mean']):ax.text(i,v+.035,f'{v:.3f}',ha='center',fontsize=9)
comparators=['quant-continuous','quant-binary','expert-shuffled','untrained','raw-molformer']
names=['Continuous MIC','Binary MIC','Shuffled human labels','Untrained encoder','Raw MolFormer']
for ax,panel,title in [(axs[0,1],'matched-pooled','B  Same 681 molecules: human labels vs pooled MIC'),(axs[1,0],'matched-sa','C  Same 529 molecules: human labels vs S. aureus MIC')]:
 d=paired[(paired.panel==panel)&(paired['head']=='catboost')&(paired.target=='Q-HERO-405')&(paired.unit=='scaffold')].set_index('comparison')
 for i,(c,n) in enumerate(zip(comparators,names)):
  r=d.loc[f'expert minus {c}'];ax.errorbar(r.delta_RMSE,i,xerr=[[r.delta_RMSE-r.ci_low],[r.ci_high-r.delta_RMSE]],fmt='o',capsize=3,color=colors[1] if c!='quant-continuous' else colors[2])
 ax.axvline(0,color='#88929e',linestyle='--',lw=1);ax.set_yticks(range(len(names)),names);ax.invert_yaxis();ax.set_xlabel('ΔRMSE = human − comparator (log₂ µM)\n95% paired scaffold-bootstrap CI');ax.set_title(title,loc='left',fontsize=10);ax.grid(axis='x',alpha=.15)
ax=axs[1,1]
arms=['expert-full','quant-pooled-full','quant-sa-full','quant-iltox-full']
d=summary[(summary.panel=='full')&(summary['head']=='catboost')&(summary.target=='Q-HERO-405')].set_index('arm').loc[arms]
ax.bar(range(4),d.R2,yerr=d.R2_sd,capsize=4,color=[colors[1],colors[2],'#448773',colors[3]],width=.6)
ax.set_xticks(range(4),['Human\nn = 712','Pooled MIC\nn = 1,120','S. aureus MIC\nn = 888','Cytotoxicity\nn = 273'])
ax.set_ylabel('Q-HERO-405 R² (mean ± seed SD)');ax.set_ylim(0,.36);ax.set_title('D  Practical source comparison: unequal source sizes',loc='left',fontsize=10)
fig.suptitle('Useful human supervision has protocol-dependent limits',fontsize=14,fontweight='bold')
for suffix in ['png','pdf','svg']:fig.savefig(out/f'figure7_supervision_controls.{suffix}',dpi=300)
plt.close(fig)
print('Figure saved')
