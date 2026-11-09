"""Restyle archived results, with Aptos/Segoe UI previews and no model refitting."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import re
import sys
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v17_matplotlib')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text
from matplotlib.colors import to_hex, to_rgba
from matplotlib.patches import Patch, FancyBboxPatch

ROOT=Path(__file__).resolve().parent
REPRO=ROOT.parent
OUT=ROOT/'figures'
PREVIEW=ROOT/'font_previews'
FONT_PATHS={'Aptos':Path('/Applications/Microsoft Word.app/Contents/Resources/DFonts/Aptos.ttf'),
            'Segoe UI':Path('/private/tmp/coma_v17_SegoeUI.ttf')}
FONT='Aptos'
PALETTE={'human':'#8B7BC7','continuous':'#52AB98','binary':'#D8A377','raw':'#98A2AD',
         'human_null':'#C6BBE4','continuous_null':'#AFD9CE','binary_null':'#EBD1BB',
         'blue':'#94B6D5','orange':'#D8A377','purple':'#C6BBE4','teal':'#AFD9CE'}
MAP={
 '#9c7abb':'human','#8064a2':'human','#805c8e':'human','#7651a8':'human','#77598e':'human',
 '#329465':'human','#2a78d6':'human',
 '#75aaa2':'continuous','#2c8c83':'continuous','#328c82':'continuous','#32836b':'continuous',
 '#418b82':'continuous','#c38239':'continuous','#eb6834':'continuous',
 '#d99b7e':'binary','#357bad':'binary','#427aa6':'binary','#d69a36':'binary',
 '#a46da0':'binary','#1baf7a':'binary',
 '#92999e':'raw','#748493':'raw','#858585':'raw',
 '#b6a6c9':'human_null','#b8a4cc':'human_null','#c5b5d6':'human_null',
 '#9ec9c4':'continuous_null','#b4d1cb':'continuous_null',
 '#a2bdd3':'binary_null','#e8c7b6':'binary_null',
 '#4b79a3':'blue','#3b729d':'blue','#a5c4de':'blue','#eabb98':'orange','#d39b56':'orange'}
INPUTS={}
FIGURES=[]
AUDIT=[]

def read_csv(path):
 path=Path(path);INPUTS[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
 return pd.read_csv(path)

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def theme(font=None):
 font=font or FONT
 if font=='Segoe UI' and not FONT_PATHS[font].exists():
  from fontTools.ttLib import TTFont
  office=Path('/Applications/Microsoft Word.app/Contents/Resources')
  webfont=next(office.glob('sdx/FA000000002/OfflineFiles/segoeui-regular*.woff'))
  face=TTFont(str(webfont));face.flavor=None;face.save(str(FONT_PATHS[font]))
 font_manager.fontManager.addfont(str(FONT_PATHS[font]))
 plt.rcParams.update({'font.family':font,'font.size':10,'axes.labelsize':10,
  'axes.titlesize':11,'axes.titleweight':'normal','axes.edgecolor':'#C9CCD1',
  'axes.labelcolor':'#4E5158','axes.linewidth':.6,'axes.spines.top':False,
  'axes.spines.right':False,'xtick.color':'#737780','ytick.color':'#737780',
  'xtick.labelsize':9,'ytick.labelsize':9,'xtick.major.size':0,'ytick.major.size':0,
  'text.color':'#3E4148','grid.color':'#E7E8EB','grid.linewidth':.6,
  'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
  'legend.frameon':False,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
  'mathtext.fontset':'dejavusans'})

def recolor(value):
 try:
  rgba=to_rgba(value);key=to_hex(rgba)
  if key in MAP:return to_rgba(PALETTE[MAP[key]],rgba[3])
 except (ValueError,TypeError):pass
 return value

def finish(fig,font=None):
 font=font or FONT
 for text in fig.findobj(Text):
  text.set_fontfamily([font,'Arial']);text.set_fontweight('normal')
  if font=='Segoe UI':text.set_text(text.get_text().replace('₂',r'$_2$'))
  if to_hex(text.get_color()) in ['#000000','#ffffff','#0b0b0b']:text.set_color('#3E4148')
 for ax in fig.axes:
  if not ax.axison:continue
  ax.set_axisbelow(True)
  for side,spine in ax.spines.items():
   spine.set_visible(side in ['bottom','left']);spine.set_color('#D6D8DC');spine.set_linewidth(.55)
  ax.tick_params(colors='#737780',length=0,pad=5)
  for line in ax.lines:line.set_color(recolor(line.get_color()))
  for collection in ax.collections:
   for getter,setter in [(collection.get_facecolors,collection.set_facecolors),
                         (collection.get_edgecolors,collection.set_edgecolors)]:
    values=getter()
    if len(values):setter([recolor(v) for v in values])
  for patch in ax.patches:
   # ACS atom and bond paths retain native monochrome geometry and stroke widths.
   patch.set_facecolor(recolor(patch.get_facecolor()));patch.set_edgecolor(recolor(patch.get_edgecolor()))
  for title in [ax.title,ax._left_title,ax._right_title]:
   title.set_text(re.sub(r'^([A-Da-d])\s{2,}',lambda m:m[1].lower()+') ',title.get_text()))
  for gridline in ax.get_xgridlines()+ax.get_ygridlines():
   gridline.set_color('#E7E8EB');gridline.set_alpha(1);gridline.set_linewidth(.55)
  ax.set_facecolor('white')
 fig.set_facecolor('white')

def save(fig,name,font=None,directory=None):
 finish(fig,font)
 directory=directory or OUT;directory.mkdir(exist_ok=True)
 for ext in ['png','pdf','svg']:
  fig.savefig(directory/(name+'.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
 if directory==OUT:FIGURES.append(name)
 plt.close(fig)

def clean_source_save(fig,name):
 # Explanations and statistical conventions stay in the existing full captions.
 for text in list(fig.texts):text.remove()
 if name=='figure3_task_encoding':name='figureS27_task_encoding'
 if name=='figure4_OOD_families_ACS1996':
  name='figure3_OOD_families_ACS1996'
  for ax in fig.axes:ax.set_title(ax._left_title.get_text().split('\n')[0],loc='left')
 if name=='figure5_paired_error_violins':
  name='figure4_paired_error_violins'
  from matplotlib.collections import PathCollection
  for ax in fig.axes:
   ax.set_title(ax._left_title.get_text().replace('QAC105','QAC-105').replace('OOD17','OOD-17'),loc='left')
   for line in ax.lines:line.set_zorder(4)
   for collection in ax.collections:
    if isinstance(collection,PathCollection):collection.set_alpha(.35)
  fig.legend(handles=[Patch(facecolor=PALETTE['human'],alpha=.45,label='Human'),
                     Patch(facecolor=PALETTE['continuous'],alpha=.45,label='Continuous MIC')],
             loc='lower center',bbox_to_anchor=(.5,.005),ncol=2,frameon=False)
 if name=='figureS21_scaffold_transfer':
  name='figureS25_scaffold_transfer'
  fig.legend(handles=[plt.Line2D([],[],marker='o',color='#7B8189',ls='',label='Cation holdout'),
                     plt.Line2D([],[],marker='s',mfc='white',color='#7B8189',ls='',label='Scaffold holdout')],
             loc='lower center',ncol=2,frameon=False)
 if name=='figureS19_OOD17_parity':name='figureS23_OOD17_parity'
 if name=='figureS20_OOD17_individual_endpoints':name='figureS24_OOD17_individual_endpoints'
 if name=='figureS27_task_encoding':
  fig.legend(handles=[plt.Line2D([],[],marker='o',color='#7B8189',ls='',label='One-hot'),
                     plt.Line2D([],[],marker='s',mfc='white',color='#7B8189',ls='',label='Text embedding')],
             loc='lower center',ncol=2,frameon=False)
 save(fig,name)

def design():
 fig,ax=plt.subplots(figsize=(9,4.7));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
 def box(x,y,w,h,text,color):
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.01,rounding_size=.02',
                            fc=color,ec='#D7D9DE',lw=.65))
  ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=11,linespacing=1.5)
 def arrow(a,z):ax.annotate('',xy=z,xytext=a,arrowprops={'arrowstyle':'->','color':'#8B9098','lw':.9})
 ax.text(.02,.96,'a) Source guidance',fontsize=13)
 box(.025,.61,.19,.24,'681 molecules\nMolFormer', '#F1F3F7')
 for y,label,color in [(.79,'Human Good / Bad','#EBE5F6'),(.60,'Continuous MIC','#E0F0EB'),(.41,'Binary MIC','#F7EBDD')]:
  box(.32,y,.25,.14,label,color);arrow((.22,.73),(.31,y+.07))
 box(.69,.61,.26,.24,'Guided encoders\n5 paired seeds','#F1F3F7')
 for y in [.86,.67,.48]:arrow((.585,y),(.68,.73))
 ax.text(.02,.31,'b) Target prediction',fontsize=13)
 box(.025,.05,.25,.18,'Frozen features\n+ task code','#EBE5F6')
 box(.365,.05,.20,.18,'CatBoost','#E0F0EB');arrow((.29,.14),(.35,.14))
 box(.665,.05,.29,.18,'QAC-105 · CV\nOOD-17 · 4 families','#F7EBDD');arrow((.58,.14),(.65,.14))
 fig.tight_layout(pad=.8);save(fig,'figure1_supervision_and_transfer')

def parity(p,cohort,name):
 arms=['expert','quant-continuous','quant-binary'];tasks=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
 labels=['S. aureus · MIC','S. aureus · MBC','E. coli · MIC','E. coli · MBC']
 data=p[(p.cohort==cohort)&(p.encoding=='onehot')&(p.provenance=='matched-source-excluded')]
 lower=min(-3.5,float(data.y.min())-.4,float(data.prediction.min())-.4)
 upper=max(10.,float(data.y.max())+.4,float(data.prediction.max())+.4)
 fig,axes=plt.subplots(4,3,figsize=(7.2,8.3),sharex=True,sharey=True)
 for i,task in enumerate(tasks):
  for j,(arm,key,marker) in enumerate(zip(arms,['human','continuous','binary'],['o','s','^'])):
   ax=axes[i,j];d=data[(data.task==task)&(data.arm==arm)]
   means=d.groupby(['can','qualifier'],as_index=False).agg(y=('y','first'),prediction=('prediction','mean'))
   exact=means.qualifier=='='
   ax.scatter(means.y[exact],means.prediction[exact],s=26 if marker=='^' else 23,
              color=PALETTE[key],marker=marker,alpha=.7,edgecolors=PALETTE[key],linewidths=.3)
   if (~exact).any():
    ax.scatter(means.y[~exact],means.prediction[~exact],s=65,color='#4E5158',marker='>',zorder=5)
   ax.plot([lower,upper],[lower,upper],color='#B5B8BE',lw=.75,ls='--')
   ax.set_xlim(lower,upper);ax.set_ylim(lower,upper);ax.set_aspect('equal',adjustable='box')
   ax.set_xticks([-2,2,6,10]);ax.set_yticks([-2,2,6,10]);ax.grid(axis='y')
   if i==0:ax.set_title(['Human','Continuous MIC','Binary MIC'][j],fontsize=11,pad=9)
   ax.text(.05,.95,chr(97+3*i+j),transform=ax.transAxes,va='top',fontsize=10)
   if j==0:ax.set_ylabel(labels[i],fontsize=10)
 fig.text(.025,.51,'Predicted log₂(mg/L)',rotation=90,va='center',fontsize=10)
 fig.text(.55,.012,'Measured log₂(mg/L)',ha='center',fontsize=10)
 fig.subplots_adjust(left=.14,right=.99,top=.96,bottom=.065,hspace=.14,wspace=.12)
 AUDIT.append({'figure':name,'cohort':cohort,'prediction_rows':len(data),'limits':[lower,upper],
               'all_predictions_within_axes':True,'statistics_in_caption_and_tables':True})
 save(fig,name)

def half_violin(ax,values,x,color,left):
 violin=ax.violinplot(values,positions=[x],widths=.82,showextrema=False)
 body=violin['bodies'][0];verts=body.get_paths()[0].vertices
 verts[:,0]=np.minimum(verts[:,0],x) if left else np.maximum(verts[:,0],x)
 body.set_facecolor(color);body.set_edgecolor(color);body.set_alpha(.45);body.set_linewidth(.7)
 lo,med,hi=np.quantile(values,[.25,.5,.75]);centre=x+(-.11 if left else .11)
 ax.vlines(centre,lo,hi,color=color,lw=1.8);ax.plot([centre-.06,centre+.06],[med,med],color=color,lw=2.2)

def routes(direct,ablation,font=None,directory=None):
 fig,axes=plt.subplots(1,3,figsize=(8.1,3.05),sharey=True)
 maximum=0.;records=[]
 for ax,schema,title in zip(axes,['cation','scaffold','full-QAC105'],['Cation holdout','Scaffold holdout','OOD-17']):
  for j,arm in enumerate(['expert','quant-continuous','quant-binary']):
   for left,data,color in [(True,direct,PALETTE['human']),(False,ablation,PALETTE['continuous'])]:
    g=data[(data.arm==arm)&(data.schema==schema)&(data.qualifier=='=')&data.seed.isin([0,1,2])].copy()
    if not left:g=g[g.variant=='intact']
    g['ae']=np.abs(g.y-g.prediction)
    values=g.groupby(['compound_id','task']).ae.mean().to_numpy()
    assert len(values)==(67 if schema=='full-QAC105' else 420)
    maximum=max(maximum,float(values.max()));half_violin(ax,values,j,color,left)
    records.append(dict(schema=schema,arm=arm,route='direct' if left else 'decoder',
                        n=len(values),max=float(values.max()),median=float(np.median(values))))
  ax.set_title(title,pad=10);ax.set_xticks(range(3));ax.set_xticklabels(['Human','Continuous\nMIC','Binary\nMIC'])
  ax.grid(axis='y')
 for ax in axes:ax.set_ylim(0,np.ceil(maximum+.2))
 axes[0].set_ylabel('Absolute error, log₂(mg/L)')
 fig.legend(handles=[Patch(facecolor=PALETTE['human'],alpha=.45,label='Direct target FT'),
                     Patch(facecolor=PALETTE['continuous'],alpha=.45,label='Frozen encoder + decoder')],
            loc='lower center',ncol=2,frameon=False,fontsize=10,bbox_to_anchor=(.5,-.02))
 finish(fig,font)
 fig.tight_layout(rect=(0,.12,1,1),pad=.9,w_pad=1.8)
 if directory is None:AUDIT.append(dict(figure='figureS26_prediction_route_violins',distributions=records,full_tail_max=maximum))
 save(fig,'figureS26_prediction_route_violins',font,directory)

def direct_capacity(metrics):
 pooled=metrics[(metrics.task=='pooled')&(metrics.arm=='raw-molformer')]
 fig,axes=plt.subplots(1,3,figsize=(8.1,3.1),sharey=True)
 modes=['linear','compact','lora','partial','full'];colors=['#8FA8BD']*5
 for ax,schema,title in zip(axes,['cation','scaffold','full-QAC105'],['Cation holdout','Scaffold holdout','OOD-17']):
  for j,(mode,color) in enumerate(zip(modes,colors)):
   g=pooled[(pooled['mode']==mode)&(pooled.schema==schema)];assert len(g)==3
   ax.scatter(j+np.linspace(-.12,.12,3),g.RMSE,c=color,s=25,alpha=.75)
   ax.plot([j-.19,j+.19],[g.RMSE.mean()]*2,color=color,lw=2)
  ax.set_xticks(range(5));ax.set_xticklabels(['Linear','MLP','LoRA','Partial','Full'],rotation=35,ha='right')
  ax.set_title(title);ax.grid(axis='y')
 axes[0].set_ylabel('Pooled RMSE, log₂(mg/L)');fig.tight_layout(pad=1,w_pad=1.8)
 save(fig,'figureS29_direct_adaptation')

def weights(ci):
 fig,axes=plt.subplots(1,3,figsize=(8.1,3.25),sharey=True)
 bounds=[]
 for ax,schema,title in zip(axes,['cation','scaffold','full-QAC105'],['Cation holdout','Scaffold holdout','OOD-17']):
  for j,variant in enumerate(['rewind_outer_norm','rewind_blocks','rewind_all']):
   for k,(arm,key,marker) in enumerate(zip(['expert','quant-continuous','quant-binary'],['human','continuous','binary'],['o','s','^'])):
    g=ci[(ci.branch=='ablation')&(ci.contrast=='weight_rewind_minus_intact')&(ci.a==arm+'/'+variant)&
         (ci.schema==schema)&(ci.grouping=='scaffold')]
    assert len(g)==1,(variant,ci.a.unique())
    r=g.iloc[0];delta=r.delta_RMSE_a_minus_b
    bounds.append((float(r.low),float(r.high)))
    ax.errorbar(j+(k-1)*.22,delta,yerr=[[delta-r.low],[r.high-delta]],fmt=marker,
                ms=4.5,capsize=2,color=PALETTE[key],lw=1.1)
  ax.axhline(0,color='#A0A5AD',ls='--',lw=.7);ax.grid(axis='y');ax.set_title(title,pad=10)
  ax.set_xticks(range(3));ax.set_xticklabels(['Outer norm','Eight blocks','All weights'],rotation=30,ha='right')
 axes[0].set_ylabel('Rewind − intact ΔRMSE')
 axes[0].set_ylim(min(x[0] for x in bounds)-.06,max(x[1] for x in bounds)+.08)
 fig.legend(handles=[plt.Line2D([],[],marker=marker,ls='',color=PALETTE[key],label=label)
                     for marker,key,label in zip(['o','s','^'],['human','continuous','binary'],['Human','Continuous MIC','Binary MIC'])],
            loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,-.01))
 fig.tight_layout(rect=(0,.13,1,1),pad=.9,w_pad=1.8);save(fig,'figure5_weight_rewind')

def decoder_violins():
 base=REPRO/'server_models_20261012';snapshot=json.loads((base/'analysis/verification.json').read_text())['snapshot']
 tables={m:read_csv(Path(snapshot)/'new_baselines'/m/'predictions.csv') for m in ['tabpfn','tabfm']}
 fig,axes=plt.subplots(2,3,figsize=(8.1,5.65),sharey=True)
 colors=[PALETTE[k] for k in ['raw','blue','human','continuous','binary']]
 reps=['rdkit','raw-molformer','expert_seed0','quant-continuous_seed0','quant-binary_seed0']
 maximum=0.;records=[]
 for row,model in enumerate(['tabpfn','tabfm']):
  for col,(schema,title) in enumerate(zip(['cation','scaffold','full-QAC105'],['Cation holdout','Scaffold holdout','OOD-17'])):
   ax=axes[row,col];d=tables[model]
   distributions=[]
   for rep in reps:
    sub=d[(d.representation==rep)&(d.schema==schema)&(d.qualifier=='=')]
    values=np.abs(sub.y.to_numpy()-sub.prediction.to_numpy());distributions.append(values)
    maximum=max(maximum,float(values.max()));records.append(dict(model=model,representation=rep,schema=schema,n=len(values),max=float(values.max())))
   violins=ax.violinplot(distributions,positions=range(5),widths=.74,showextrema=False)
   for j,(body,color,values) in enumerate(zip(violins['bodies'],colors,distributions)):
    body.set_facecolor(color);body.set_edgecolor(color);body.set_alpha(.45);body.set_linewidth(.7)
    lo,med,hi=np.quantile(values,[.25,.5,.75]);ax.vlines(j,lo,hi,color=color,lw=1.8)
    ax.plot([j-.11,j+.11],[med,med],color=color,lw=2.2)
   ax.set_xticks(range(5));ax.set_xticklabels(['RDKit','Raw','Human','Continuous','Binary'],rotation=40,ha='right')
   ax.set_title(title if row==0 else '',pad=10);ax.grid(axis='y')
   if col==0:ax.set_ylabel(('TabPFN-V2' if row==0 else 'TabFM')+'\nAbsolute error, log₂(mg/L)')
 for ax in axes.flat:ax.set_ylim(0,np.ceil(maximum+.25))
 fig.tight_layout(pad=.9,w_pad=1.8,h_pad=1.4)
 AUDIT.append(dict(figure='figureS28_decoder_error_violins',distributions=records,full_tail_max=maximum))
 save(fig,'figureS28_decoder_error_violins')

def historical():
 # Re-evaluate only plotting/data aggregation from the archived scripts. Save is replaced
 # before execution, so previous figures are never overwritten. No training is invoked.
 mapping={'figS1_expert_set':'figureS5_expert_set','figS2_overlap':'figureS6_overlap',
 'figS3_qhero_violins':'figureS7_qhero_violins','figS4_qhero_r2':'figureS8_qhero_r2',
 'figS5_equivalence':'figureS9_equivalence','figS6_split_effect':'figureS10_split_effect',
 'figS7_representation_quality_v8':'figureS11_representation_quality',
 'figS8_zeroshot_v8':'figureS12_zeroshot','figS9_calibration_v8':'figureS13_calibration'}
 def hist_save(fig,name):
  for text in list(fig.texts):text.remove()
  save(fig,mapping[name])
 for source in [REPRO/'make_si_figures.py',REPRO/'make_ft_figures_v8.py']:
  tree=ast.parse(source.read_text())
  tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='save']
  env={'__name__':'v17_historical_style','__file__':str(source),'save':hist_save}
  exec(compile(tree,str(source),'exec'),env)

def main():
 OUT.mkdir(exist_ok=True);PREVIEW.mkdir(exist_ok=True);theme()
 sys.path.insert(0,str(REPRO/'revision_v14'))
 old=module('v14_soft',REPRO/'revision_v14/make_figures.py')
 old.style.PALETTE.update(PALETTE);old.COLOR={arm:PALETTE[key] for arm,key in zip(
  ['expert','quant-continuous','quant-binary','raw-molformer'],['human','continuous','binary','raw'])}
 old.save=clean_source_save
 p=read_csv(REPRO/'revision_v14/results/predictions.csv');s=read_csv(REPRO/'revision_v14/analysis/summary.csv')
 o=read_csv(REPRO/'revision_v14/data/OOD17.csv')
 design();parity(p,'QAC105','figure2_QAC105_parity');parity(p,'OOD17','figureS23_OOD17_parity')
 old.encodings(s);old.ood_families(o);old.violations(p);old.ood_individual(p,o)
 sc=read_csv(REPRO/'revision_v14/analysis/scaffold_summary.csv')
 fig,axes=plt.subplots(2,2,figsize=(8.1,5.8),sharey=True)
 for i,(task,ax) in enumerate(zip(old.TASKS,axes.flat)):
  for j,arm in enumerate(old.ARMS+['raw-molformer']):
   a=s[(s.arm==arm)&(s.task==task)&(s.cohort=='QAC105')&(s.encoding=='onehot')].iloc[0]
   b=sc[(sc.arm==arm)&(sc.task==task)&(sc.cohort=='QAC105')].iloc[0]
   color=old.COLOR[arm];ax.plot([j-.12,j+.12],[a.R2,b.R2],c=color,lw=.85)
   ax.errorbar(j-.12,a.R2,yerr=a.R2_sd,fmt='o',color=color,ms=5,capsize=2)
   ax.errorbar(j+.12,b.R2,yerr=b.R2_sd,fmt='s',mfc='white',mec=color,ecolor=color,ms=5,capsize=2)
  ax.axhline(0,c='#A0A5AD',ls='--',lw=.65);ax.grid(axis='y')
  ax.set_title(old.TLABEL[task],loc='left');ax.set_xticks(range(4));ax.set_xticklabels(['Human','Continuous\nMIC','Binary\nMIC','Raw'])
  if i%2==0:ax.set_ylabel('Endpoint-specific R²')
 fig.tight_layout(rect=(0,.065,1,1));clean_source_save(fig,'figureS21_scaffold_transfer')
 analysis=REPRO/'server_finetune_causal_20261012/analysis'
 direct=read_csv(analysis/'direct_predictions.csv');ablation=read_csv(analysis/'ablation_predictions.csv')
 for font in FONT_PATHS:
  theme(font);routes(direct,ablation,font,PREVIEW/font.replace(' ','_'))
 theme();routes(direct,ablation);direct_capacity(read_csv(analysis/'direct_metrics.csv'))
 weights(read_csv(analysis/'paired_bootstrap.csv'));decoder_violins();historical()
 theme()
 learning=module('v12_soft_learning',REPRO/'revision_v12/make_figures.py')
 learning.save=lambda fig,name:clean_source_save(fig,name.replace('figureS17','figureS21'))
 learning.learning()
 matched=module('v13_soft_matched',REPRO/'revision_v13/render_figures.py')
 matched.save=lambda fig,name:clean_source_save(fig,name.replace('figureS18','figureS22'))
 matched.matched_violins()
 for relative in ['qhero/qhero_residuals.csv','qhero/qhero_metrics.csv',
  'causal/ood_paired_residuals.csv','table2/table2_rebuild.csv',
  'finetune/runs.jsonl','finetune/runs_direct.jsonl','finetune/predictions_seed0.csv',
  'finetune/recalibration.csv','revision_v12/results/epochs.csv',
  'revision_v12/results/predictions.csv']:
  path=REPRO/relative;INPUTS[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
 expert=REPRO/'expert_labels/expert_labels_1103.csv'
 if not expert.exists():expert=REPRO.parent/'expert_labels/expert_labels_1103.csv'
 INPUTS[str(expert)]=hashlib.sha256(expert.read_bytes()).hexdigest()
 report=dict(font=FONT,font_files={k:str(v) for k,v in FONT_PATHS.items()},
  font_comparison='Same data and layout in Aptos and Segoe UI; fonts not redistributed.',
  font_embedding='Print/preview embedding permitted by installed font flags (fsType=8).',
  palette=PALETTE,figures=FIGURES,inputs_sha256=INPUTS,plot_checks=AUDIT,
  model_training_performed=False,raw_predictions_changed=False,
  original_author_SI_images='Retained unchanged as S1–S4',
  historical_raster_and_chemical_diagrams='Retained unchanged when editable/source data were unavailable',
  captions='Methods, uncertainty, counts and censoring remain in document captions and tables')
 (ROOT/'style_manifest.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(dict(font=FONT,redrawn_figures=len(FIGURES),font_previews=list(FONT_PATHS)),indent=2))

if __name__=='__main__':main()
