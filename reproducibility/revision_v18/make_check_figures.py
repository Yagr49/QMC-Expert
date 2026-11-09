"""Soft vector plots of completed checks, with all recorded exact endpoints."""
from pathlib import Path
import os,importlib.util,json
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v18_matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'figures'
spec=importlib.util.spec_from_file_location('theme',ROOT.parent/'revision_v17/make_soft_figures.py');soft=importlib.util.module_from_spec(spec);spec.loader.exec_module(soft);soft.theme()
SCHEMAS=['cation','scaffold','full-QAC105'];TITLES=['Cation holdout','Scaffold holdout','OOD-17']
def save(fig,name):
 soft.finish(fig)
 for ext in ['png','pdf','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
 plt.close(fig)
def main():
 p=pd.read_csv(ROOT/'analysis/predictions.csv');p=p[(p.qualifier=='=')&(p.encoding=='categorical')&(p.provenance=='v5_architecture_matched_source')].copy()
 p['ae']=abs(p.prediction-p.y);records=[]
 fig,axes=plt.subplots(1,3,figsize=(9.4,3.75),sharey=True)
 for ax,schema,title in zip(axes,SCHEMAS,TITLES):
  for i,(real,shuffled) in enumerate([('human','human_shuffled'),('mic_binary','binary_shuffled'),('mic_continuous','continuous_shuffled')]):
   for shift,arm,color in [(-.16,real,'#A99ACF'),(.16,shuffled,'#97C8BC')]:
    a=p[(p.schema==schema)&(p.arm==arm)];v=a.groupby(['compound_id','task']).ae.mean().to_numpy()
    assert len(v)==(67 if schema=='full-QAC105' else 420)
    violin=ax.violinplot([v],positions=[i+shift],widths=.30,showextrema=False)
    for patch in violin['bodies']:patch.set_facecolor(color);patch.set_edgecolor(color);patch.set_alpha(.65)
    ax.scatter([i+shift],[np.median(v)],s=12,c=color,edgecolors='#62636C',linewidths=.4,zorder=3)
    records.append(dict(schema=schema,arm=arm,n=len(v),median=float(np.median(v)),max=float(v.max())))
  ax.set_title(title);ax.set_xticks(range(3));ax.set_xticklabels(['Human','Binary MIC','Continuous\nMIC'],fontsize=9);ax.grid(axis='y',alpha=.4);ax.set_ylim(bottom=0)
 axes[0].set_ylabel('Absolute error, log₂(mg/L)')
 from matplotlib.patches import Patch
 fig.legend(handles=[Patch(fc='#A99ACF',alpha=.65,label='Real labels'),Patch(fc='#97C8BC',alpha=.65,label='Shuffled labels')],loc='upper center',bbox_to_anchor=(.5,1.035),ncol=2,frameon=False)
 fig.subplots_adjust(top=.82,bottom=.18,wspace=.14);save(fig,'figure7_compact_real_shuffled_violins')
 m=pd.read_csv(ROOT/'analysis/modern_metrics.csv');s=pd.read_csv(ROOT/'analysis/summary.csv')
 fig,axes=plt.subplots(1,3,figsize=(9.4,3.4),sharey=True)
 names=['CatBoost','TabPFN v2','TabFM','AutoGluon']
 for ax,schema,title in zip(axes,SCHEMAS,TITLES):
  for rep,color,shift in [('v5_raw','#94B6D5',-.10),('v5_human','#A99ACF',.10)]:
   cb=s[(s.arm==rep)&(s.encoding=='separate')&(s.schema==schema)&(s.task=='pooled')].RMSE.item()
   values=[cb]+[m[(m.model==model)&(m.representation==rep)&(m.schema==schema)&(m.task=='pooled')].RMSE.item() for model in ['tabpfn','tabfm','autogluon']]
   ax.plot(values,np.arange(4)+shift,'o',ms=5,color=color,label='Raw' if rep=='v5_raw' else 'Human-guided')
  ax.set_title(title);ax.set_xlabel('RMSE, log₂(mg/L)');ax.set_yticks(range(4));ax.set_yticklabels(names);ax.invert_yaxis();ax.grid(axis='x',alpha=.4)
  ax.set_xlim(1.8,2.25)
 fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,1.04),ncol=2,frameon=False)
 fig.subplots_adjust(top=.80,bottom=.18,left=.13,wspace=.2);save(fig,'figure8_v5_modern_decoders')
 c=pd.read_csv(ROOT/'analysis/contrasts.csv')
 fig,axes=plt.subplots(1,3,figsize=(9.4,3.3),sharey=True)
 comparisons=['human minus human_shuffled','human minus mic_continuous','human minus mic_binary','human_weight_only minus human','initial minus human']
 labels=['Human − shuffled','Human − continuous','Human − binary','Weights reset − human','Initial − human']
 for ax,schema,title in zip(axes,SCHEMAS,TITLES):
  for i,comparison in enumerate(comparisons):
   row=c[(c.comparison==comparison)&(c.schema==schema)&(c.unit=='scaffold')].iloc[0]
   ax.errorbar(row.delta_RMSE,i,xerr=[[row.delta_RMSE-row.ci_low],[row.ci_high-row.delta_RMSE]],fmt='o',color='#A99ACF',ms=4,lw=1,capsize=2)
  ax.axvline(0,color='#ABB0B8',lw=.7,ls='--');ax.set_yticks(range(5));ax.set_yticklabels(labels,fontsize=9);ax.invert_yaxis();ax.set_title(title);ax.set_xlabel('ΔRMSE, log₂(mg/L)');ax.grid(axis='x',alpha=.4)
 fig.subplots_adjust(left=.23,bottom=.2,wspace=.17);save(fig,'figureS30_compact_paired_contrasts')
 (ROOT/'check_figure_provenance.json').write_text(json.dumps(dict(font='Aptos',qualifier='Exact endpoints only; IT505 E. coli MBC remains a bound',
  violin=records,violin_unit='Per compound/endpoint mean absolute error across five source seeds; not ensemble error',
  CIs='Pointwise 95% paired source-seed and scaffold bootstrap, including four OOD scaffolds',
  modern='One saved v5 checkpoint; separate four endpoint models for every decoder; PCA32 only for modern models'),indent=2))
 print('Three completed-check figures saved in PNG/PDF/SVG')
if __name__=='__main__':main()
