"""Publication violin distributions from actual paired endpoint predictions.

No new fits, no pseudo-replication of seed predictions, no endpoint tail clipping.
Human routes here are partial-backbone follow-ups, not the compact v5 MLP.
"""
from pathlib import Path
import os,hashlib,json
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v23_ft_matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parent;REPRO=ROOT.parent
ANALYSIS=ROOT/'analysis';OUT=ROOT/'figures'
for p in [ANALYSIS,OUT]:p.mkdir(parents=True,exist_ok=True)
SOURCE=REPRO/'server_finetune_causal_20261012/analysis'
SEEDS=[0,1,2];SCHEMES=['cation','scaffold','full-QAC105']
ROUTES=[
 dict(id='frozen_head',label='Frozen head',branch='direct',arm='raw-molformer',mode='linear',color='#91B7D6'),
 dict(id='lora',label='LoRA',branch='direct',arm='raw-molformer',mode='lora',color='#B8A7D3'),
 dict(id='full_FT',label='Full FT',branch='direct',arm='raw-molformer',mode='full',color='#E6B490'),
 dict(id='human_direct',label='Human direct',branch='direct',arm='expert',mode='partial',color='#D7A9BD'),
 dict(id='human_CatBoost',label='Human → CB',branch='ablation',arm='expert',variant='intact',color='#87CABA')]
KEYS=['schema','cohort','compound_id','task']
STEM='figure3_backbone_route_error_violins'
FONT=Path('/Applications/Microsoft Word.app/Contents/Resources/DFonts/Aptos.ttf')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def data():
 frames={b:pd.read_csv(SOURCE/(b+'_predictions.csv')) for b in ['direct','ablation']}
 long=[];seed_metrics=[];checks=[]
 for route in ROUTES:
  d=frames[route['branch']]
  select=(d.arm==route['arm'])&d.seed.isin(SEEDS)
  select &= d['mode'].eq(route['mode']) if route['branch']=='direct' else d.variant.eq(route['variant'])
  g=d[select].copy();g['route']=route['id']
  bounds=g[g.qualifier!='=']
  assert len(bounds)==3
  assert bounds.compound_id.eq('IT505').all() and bounds.task.eq('Ec_MBC').all()
  g=g[g.qualifier=='='].copy();g['absolute_error']=np.abs(g.y-g.prediction)
  assert not g.duplicated(KEYS+['seed']).any()
  assert g.groupby(KEYS).seed.nunique().eq(3).all()
  assert g.groupby(KEYS).y.nunique().eq(1).all()
  for schema,sub in g.groupby('schema'):
   expected=67 if schema=='full-QAC105' else 420
   assert len(sub)==expected*3 and sub.compound_id.nunique()==(17 if expected==67 else 105)
   for seed,rows in sub.groupby('seed'):
    seed_metrics.append(dict(route=route['id'],schema=schema,seed=int(seed),n=len(rows),
      RMSE=float(np.sqrt(np.mean((rows.y-rows.prediction)**2))),MAE=float(rows.absolute_error.mean())))
   checks.append(dict(route=route['id'],schema=schema,n_endpoint_summaries=expected,
    seeds=SEEDS,n_seed_predictions=len(sub),all_three_seeds_present=True,exact_only=True))
  long.append(g[['route']+KEYS+['seed','y','prediction','absolute_error','cation','scaffold']])
 long=pd.concat(long,ignore_index=True)
 summaries=long.groupby(['route']+KEYS,as_index=False).agg(mean_absolute_error=('absolute_error','mean'),
  n_seeds=('seed','nunique'),y=('y','first'),cation=('cation','first'),scaffold=('scaffold','first'))
 long.to_csv(ANALYSIS/'FT_route_seed_predictions.csv',index=False)
 summaries.to_csv(ANALYSIS/'FT_route_endpoint_mean_absolute_errors.csv',index=False)
 sm=pd.DataFrame(seed_metrics);sm.to_csv(ANALYSIS/'FT_route_seed_metrics.csv',index=False)
 stats=sm.groupby(['route','schema'],as_index=False).agg(RMSE=('RMSE','mean'),RMSE_SD=('RMSE','std'),
  MAE=('MAE','mean'),MAE_SD=('MAE','std'),n_seeds=('seed','nunique'),n_exact=('n','first'))
 # Validate the direct means/SD against completed v16 tables independently.
 prior=pd.read_csv(REPRO/'revision_v16/analysis/direct_summary.csv')
 for route in ROUTES[:4]:
  for schema in SCHEMES:
   old=prior[(prior.arm==route['arm'])&(prior['mode']==route['mode'])&(prior.schema==schema)&(prior.task=='pooled')].iloc[0]
   new=stats[(stats.route==route['id'])&(stats.schema==schema)].iloc[0]
   assert abs(old.RMSE-new.RMSE)<1e-12 and abs(old.RMSE_SD-new.RMSE_SD)<1e-12
 stats.to_csv(ANALYSIS/'FT_route_RMSE_mean_sample_SD.csv',index=False)
 return summaries,stats,checks

def plot(summaries,schemes,titles,stem,width_mm=180):
 assert FONT.exists();font_manager.fontManager.addfont(str(FONT))
 plt.rcParams.update({'font.family':'Aptos','font.size':8.5,'axes.titlesize':9,
  'axes.labelsize':8.5,'xtick.labelsize':7.5,'ytick.labelsize':8.5,
  'text.color':'#42464B','axes.labelcolor':'#42464B','axes.edgecolor':'#666A70',
  'xtick.color':'#666A70','ytick.color':'#42464B','pdf.fonttype':42,
  'ps.fonttype':42,'svg.fonttype':'none','axes.linewidth':.65})
 # Exact canvas width180mm, no tight-bbox crop that changes publication width.
 fig,axes=plt.subplots(1,len(schemes),figsize=(width_mm/25.4,88/25.4),sharex=True,sharey=True)
 axes=np.atleast_1d(axes)
 fig.subplots_adjust(left=(.159 if len(schemes)==2 else .276),right=.982,bottom=.19,top=.872,wspace=.092)
 plotted=[]
 for index,(ax,schema,title) in enumerate(zip(axes,schemes,titles)):
  ax.set_axisbelow(True);ax.grid(axis='x',color='#EBE9EE',linewidth=.5)
  for position,route in enumerate(ROUTES):
   values=summaries[(summaries.route==route['id'])&(summaries.schema==schema)].mean_absolute_error.to_numpy()
   assert len(values)==(67 if schema=='full-QAC105' else 420)
   violin=ax.violinplot(values,positions=[position],widths=.69,vert=False,
     showmeans=False,showmedians=False,showextrema=False,points=220,bw_method='scott')
   for body in violin['bodies']:
    body.set_facecolor(route['color']);body.set_edgecolor(route['color']);body.set_alpha(.76);body.set_linewidth(.65)
   lo,med,hi=np.quantile(values,[.25,.5,.75])
   ax.plot([lo,hi],[position,position],color='#64676D',lw=1.6,solid_capstyle='round',zorder=4)
   ax.scatter([med],[position],s=12,color='white',edgecolor='#64676D',linewidth=.55,zorder=5)
   # Make the small OOD sample visible without treating seed predictions as replicates.
   if schema=='full-QAC105':
    jitter=np.random.RandomState(1700+position).uniform(-.085,.085,len(values))
    ax.scatter(values,position+jitter,s=3.5,color='#51565D',alpha=.28,linewidths=0,zorder=3)
   plotted.append(dict(route=route['id'],schema=schema,n=len(values),minimum=float(values.min()),
    maximum=float(values.max()),median=float(med),q25=float(lo),q75=float(hi)))
  ax.set_xlim(0,8.05);ax.set_xticks([0,2,4,6,8]);ax.set_ylim(4.62,-.62)
  ax.set_title(title,pad=11,fontweight='normal')
  if len(schemes)>1:
   ax.text(-.008,1.055,'ab'[index],transform=ax.transAxes,fontsize=9.3,fontweight='bold',ha='left',va='center')
  for spine in ['left','top','right']:ax.spines[spine].set_visible(False)
  ax.tick_params(axis='y',length=0,pad=7)
  ax.tick_params(axis='x',length=2.5,width=.65,pad=4)
  ax.set_yticks(range(len(ROUTES)))
  if index==0:ax.set_yticklabels([r['label'] for r in ROUTES])
  else:ax.tick_params(labelleft=False)
 fig.text((.567 if len(schemes)==2 else .625),.071,'Mean absolute error over three runs, log₂(mg/L)',ha='center',va='center',fontsize=8.4)
 for ext in ['pdf','svg','png']:
  fig.savefig(OUT/(stem+'.'+ext),dpi=600,facecolor='white')
 plt.close(fig)
 return plotted

def main():
 summaries,stats,checks=data()
 main_schemes=['cation','scaffold']
 plotted=plot(summaries,main_schemes,['Cation holdout','Scaffold holdout'],STEM)
 ood_stem='figure_OOD_routes_for_section2_3'
 ood_plotted=plot(summaries,['full-QAC105'],['OOD-17'],ood_stem,width_mm=105)
 grouped_stats=stats[stats.schema.isin(main_schemes)].copy()
 grouped_stats.to_csv(ANALYSIS/'FT_route_grouped_RMSE_mean_sample_SD.csv',index=False)
 caption_en=('Figure 3. Absolute prediction-error distributions for (a) cation holdout '
  'and (b) scaffold holdout. Each violin uses the mean absolute error across three runs '
  '(seeds 0–2) for each molecule–endpoint pair, giving 420 exact endpoint summaries '
  'per route and panel. Correlated endpoints and runs preclude interpreting density '
  'differences as statistical significance or causal human-label effects. These are '
  'not errors of ensemble predictions. White markers '
  'show medians and bars show interquartile ranges; shared linear axes retain all tails. '
  'Frozen head, LoRA and full FT start from pretrained MolFormer. Human direct and '
  'Human → CB share human-guided partial-backbone source checkpoints; the former '
  'further fine-tunes on targets, whereas the latter freezes source features and fits '
  'CatBoost. These human models are separate follow-ups, not the external v5 compact '
  'encoder.')
 caption_ru=('Рисунок 3. Распределения абсолютных ошибок для (a) cation holdout и '
  '(b) scaffold holdout. Для каждой пары молекула×endpoint усреднены абсолютные ошибки '
  'трёх запусков 0–2: по 420 точных endpoint summaries на каждый route и панель. Это '
  'не ошибки усреднённого предсказания. Белый маркер — медиана, полоска — IQR; '
  'линейные оси общие, хвосты сохранены. Human direct и Human → CB исходят из одних '
  'human-guided partial-backbone checkpoints: первый путь дополнительно адаптирует '
  'backbone под target, второй замораживает source features и обучает CatBoost. '
  'Это отдельные follow-up модели, не внешний компактный v5 MLP. Зависимые endpoint '
  'и запуски не позволяют судить по плотностям о значимости или причинной роли '
  'человеческих меток.')
 ood_caption_en=('Prepared for Section 2.3. Absolute prediction-error distributions on '
  'OOD-17. Each violin contains 67 exact molecule–endpoint summaries, obtained by '
  'averaging absolute errors across runs 0–2. White markers show medians, bars show '
  'interquartile ranges, and faint points show individual endpoint summaries. This '
  'is not the error of an ensemble prediction. The IT505 E. coli MBC >500 mg/L '
  'bound is retained separately. Human direct and Human → CB use matched human-guided '
  'partial-backbone source checkpoints, with further target fine-tuning or frozen '
  'source features plus CatBoost, respectively. These models are distinct from the '
  'external v5 compact encoder. Endpoints and runs are dependent; density shapes '
  'do not establish significance or causality. This standalone figure is prepared '
  'for later discussion and is not inserted into Section 2.1.')
 for name,caption in [('figure3_caption_EN.txt',caption_en),('figure3_caption_RU.txt',caption_ru),
                      ('figure_OOD_caption_EN.txt',ood_caption_en)]:
  (ROOT/name).write_text(caption+'\n')
 assert all(token.lower() not in caption_en.lower() for token in ['OOD','67','bound'])
 manifest=dict(figure=STEM,font='Aptos',width_mm=180,height_mm=88,dpi_png=600,
  panels=main_schemes,
  primary_statistic='Mean of absolute errors within each molecule×endpoint over the same three runs',
  seeds=SEEDS,violin_KDE='Scott bandwidth on observed endpoint summaries, support within actual min/max',
  medians_IQR=True,no_tail_clipping=True,no_ensemble_predictions=True,no_KDE_over_RMSE=True,
  routes=ROUTES,checks=[c for c in checks if c['schema'] in main_schemes],plotted_summary=plotted,
  source_checkpoint_vs_compact_v5_distinct=True,
  whole_run_RMSE_mean_sample_SD_table=str(ANALYSIS/'FT_route_grouped_RMSE_mean_sample_SD.csv'),
  input_sha256={str(SOURCE/(b+'_predictions.csv')):sha(SOURCE/(b+'_predictions.csv')) for b in ['direct','ablation']},
  forked_v22_script_sha256=sha(REPRO/'revision_v22/make_FT_violins.py'),
  outputs_sha256={ext:sha(OUT/(STEM+'.'+ext)) for ext in ['pdf','svg','png']})
 (ROOT/'figure3_FT_manifest.json').write_text(json.dumps(manifest,indent=2))
 ood_manifest=dict(figure=ood_stem,font='Aptos',width_mm=105,height_mm=88,dpi_png=600,
  inserted_into_DOCX=False,purpose='Prepared separately for future Section2.3 discussion',
  primary_statistic=manifest['primary_statistic'],seeds=SEEDS,plotted_summary=ood_plotted,
  checks=[c for c in checks if c['schema']=='full-QAC105'],source_checkpoint_vs_compact_v5_distinct=True,
  all_tails_preserved=True,bound_retained_separately='IT505/Ec_MBC>500mg/L',
  input_sha256=manifest['input_sha256'],
  outputs_sha256={ext:sha(OUT/(ood_stem+'.'+ext)) for ext in ['pdf','svg','png']})
 (ROOT/'figure_OOD_manifest.json').write_text(json.dumps(ood_manifest,indent=2))
 print(grouped_stats.to_string(index=False))
 print('Grouped Figure3 saved:2panels,180mm; separateOOD prepared105mm; noDOCX edits')

if __name__=='__main__':main()
