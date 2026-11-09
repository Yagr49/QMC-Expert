"""Integrated compact-encoder schematic and exact grouped-validation errors."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v24_compact_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(parents=True,exist_ok=True)
RUN=ROOT.parent/'v5_hypotheses_20261013'
SNAP=Path(json.loads((RUN/'main_latest_snapshot.json').read_text())['path'])
spec=importlib.util.spec_from_file_location('soft',ROOT.parent/'revision_v17/make_soft_figures.py')
soft=importlib.util.module_from_spec(spec);spec.loader.exec_module(soft);soft.theme()
COLORS={'human':'#AFD9CE','mic_continuous':'#C6BBE4','human_shuffled':'#EBC8B0','matched_raw':'#CDD2D9'}
LABELS={'human':'Human','mic_continuous':'Quantitative','human_shuffled':'Shuffled human','matched_raw':'Raw'}
ARMS=list(COLORS)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def source():
    frames=[];hashes={}
    for arm in ARMS:
        names=['matched_raw_categorical.csv'] if arm=='matched_raw' else [f'compact_{arm}_seed{s}_categorical.csv' for s in range(5)]
        for name in names:
            p=SNAP/'results/chunks'/name
            a=pd.read_csv(p);hashes[str(p)]=sha(p)
            a=a[(a.cohort=='QAC105')&(a.schema.isin(['cation','scaffold']))&(a.qualifier=='=')].copy()
            assert len(a)==840 and a.encoding.eq('categorical').all()
            assert a.arm.eq(arm).all()
            frames.append(a)
    p=pd.concat(frames,ignore_index=True)
    assert p.groupby(['arm','seed','schema','compound_id','task']).size().eq(1).all()
    assert p.groupby(['compound_id','task']).y.nunique().eq(1).all()
    assert p.compound_id.nunique()==105 and p.task.nunique()==4
    p['absolute_error']=abs(p.prediction-p.y)
    derived=p.groupby(['arm','schema','compound_id','task']).agg(mean_absolute_error=('absolute_error','mean'),
                n_source_seeds=('seed','nunique'),y=('y','first'),fold=('fold','first')).reset_index()
    assert derived.groupby(['arm','schema']).size().eq(420).all()
    assert derived[derived.arm!='matched_raw'].n_source_seeds.eq(5).all()
    assert derived[derived.arm=='matched_raw'].n_source_seeds.eq(1).all()
    derived.to_csv(ROOT/'figure4_compact_error_values.csv',index=False)
    return p,derived,hashes


def box(ax,x,y,w,h,text,color,fs=9):
    patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.018',
                         lw=.7,edgecolor='#B8BDC5',facecolor=color,transform=ax.transAxes)
    ax.add_patch(patch);ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,transform=ax.transAxes)


def arrow(ax,a,b,color='#9BA2AC',dashed=False):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,lw=.9,
                  color=color,linestyle='--' if dashed else '-',transform=ax.transAxes))


def draw(derived):
    fig=plt.figure(figsize=(180/25.4,136/25.4))
    grid=fig.add_gridspec(2,2,height_ratios=[.82,1.12],hspace=.28,wspace=.23,
                         left=.09,right=.985,bottom=.10,top=.95)
    ax=fig.add_subplot(grid[0,:]);ax.set_axis_off()
    ax.text(-.065,1.025,'a',fontsize=11,transform=ax.transAxes)
    ax.text(.40,.985,'Supervision: 681 source molecules',ha='center',fontsize=8.4,transform=ax.transAxes)
    box(ax,.016,.55,.169,.23,'Frozen\nMolFormer','#EFF1F4')
    ax.text(.095,.90,'105 QAC inputs',ha='center',va='center',fontsize=8.5,transform=ax.transAxes)
    arrow(ax,(.095,.855),(.095,.795))
    box(ax,.285,.70,.225,.20,'Human Good / Bad\nCompact encoder',COLORS['human'],8.6)
    box(ax,.285,.35,.225,.20,'Measured MIC\nCompact encoder',COLORS['mic_continuous'],8.6)
    arrow(ax,(.191,.70),(.272,.80));arrow(ax,(.191,.62),(.272,.45))
    ax.text(.397,.225,'768 → 512 → 384 → 256',ha='center',fontsize=8.4,transform=ax.transAxes)
    box(ax,.605,.56,.18,.24,'Separate\nCatBoost fits','#F7E8DC',8.6)
    arrow(ax,(.518,.80),(.593,.73));arrow(ax,(.518,.45),(.593,.62))
    box(ax,.835,.56,.15,.24,'Held-out\nMIC / MBC','#EDF3F8',8.6)
    arrow(ax,(.794,.68),(.826,.68))
    ax.text(.91,.425,'Cation / scaffold\nholdout',ha='center',fontsize=8.2,transform=ax.transAxes)
    ax.text(.47,.07,'Source encoders frozen · Five paired runs',ha='center',fontsize=8.2,color='#767C86',transform=ax.transAxes)
    maximum=derived.mean_absolute_error.max()
    plotstats=[]
    for index,(schema,title) in enumerate([('cation','Cation holdout'),('scaffold','Scaffold holdout')]):
        panel=fig.add_subplot(grid[1,index])
        panel.text(-.16,1.07,chr(ord('b')+index),fontsize=11,transform=panel.transAxes)
        panel.set_title(title,pad=10,fontsize=10)
        for position,arm in enumerate(ARMS):
            v=derived[(derived.arm==arm)&(derived.schema==schema)].mean_absolute_error.to_numpy()
            body=panel.violinplot([v],positions=[position],widths=.75,showextrema=False,bw_method=.28)
            for patch in body['bodies']:
                patch.set_facecolor(COLORS[arm]);patch.set_edgecolor('#929AA4');patch.set_linewidth(.65);patch.set_alpha(.50 if arm=='matched_raw' else .85)
            q1,median,q3=np.percentile(v,[25,50,75])
            panel.vlines(position,q1,q3,color='#68717C',lw=1.15,zorder=4)
            panel.hlines(median,position-.10,position+.10,color='#56616D',lw=1.25,zorder=5)
            # All 420 observed endpoint errors are shown with deterministic, decorative jitter.
            rng=np.random.RandomState(112+position)
            panel.scatter(position+rng.uniform(-.18,.18,len(v)),v,s=1.3,color='#6A7380',alpha=.13,lw=0,zorder=3)
            plotstats.append(dict(schema=schema,arm=arm,n=len(v),median=float(median),max=float(v.max())))
        panel.set_xticks(range(4));panel.set_xticklabels(['Human','Quantitative','Shuffled\nhuman','Raw'],fontsize=8.1)
        panel.set_ylim(0,maximum*1.04);panel.set_xlim(-.6,3.6);panel.grid(axis='y',alpha=.6)
        panel.set_ylabel('Mean absolute error, log₂(mg/L)' if index==0 else '',fontsize=9)
    for ext in ['png','pdf','svg']:
        fig.savefig(OUT/f'figure4_human_quantitative_compact.{ext}',dpi=600,facecolor='white')
    plt.close(fig)
    return plotstats


def main():
    p,d,hashes=source();stats=draw(d)
    rows=[]
    for (arm,schema,seed),group in p.groupby(['arm','schema','seed']):
        rows.append(dict(arm=arm,schema=schema,seed=int(seed),n=len(group),RMSE=float(np.sqrt(np.mean((group.prediction-group.y)**2))),MAE=float(group.absolute_error.mean())))
    pd.DataFrame(rows).to_csv(ROOT/'figure4_compact_seed_metrics.csv',index=False)
    manifest=json.loads((RUN/'data/manifest.json').read_text())
    info=dict(completed=True,source_molecules=681,source_train=377,source_validation=304,
              target_salts=105,endpoints=4,source_seeds=[0,1,2,3,4],SMOTE=False,
              architecture=[768,512,384,256],encoding='native categorical task_id',
              decoder=manifest['decoder'],decoder_fits_separate_for_each_arm_seed_fold=True,
              source_encoder_frozen_before_target_decoder_training=True,
              violin_unit='420 mean absolute errors per compound/endpoint across five source seeds; raw is one fixed reference',
              marker='Median horizontal bar, IQR vertical line; all420 errors have decorative jitter',
              historical_full_quantitative_Table2_model=False,OOD_included=False,
              source_sha256=hashes,plot_statistics=stats,
              caution='Human/quantitative training objectives differ; no semantic causal superiority established',
              docx_modified=False)
    (ROOT/'figure4_provenance.json').write_text(json.dumps(info,indent=2))
    caption=('Figure 4. Matched human and quantitative supervision of external compact encoders. '
       '(a) Frozen MolFormer embeddings are transformed by separate 768→512→384→256 encoders '
       'trained on the same 681 source molecules (377 training,304 validation) with five paired source seeds '
       'and no SMOTE. Human Good/Bad labels use the contrastive objective; continuous MIC uses regression. '
       'The learned source encoders are then applied to frozen embeddings of the105 target QAC salts. '
       'Each arm is evaluated through independently fitted CatBoost regressors under the same fixed '
       '500-iteration/depth6/learning-rate0.05/seed42 protocol and native categorical task codes. '
       'Target labels train only the relevant target-training fold. (b,c) Cation- and scaffold-held-out '
       'errors on the same105 QAC salts and four MIC/MBC endpoints. Each vertical violin contains420 '
       'compound–endpoint mean absolute errors across five source runs; the raw MolFormer reference '
       'uses one fixed representation. Horizontal bars show medians and vertical lines interquartile ranges; '
       'all420 values are shown with decorative jitter. No OOD data or historical full-corpus quantitative '
       'Table2 checkpoint is used. These are matched follow-ups to the v5 compact architecture, not '
       'a rerun of its missing quantitative checkpoint. Different objectives limit causal attribution.')
    (ROOT/'figure4_caption_detailed_EN.txt').write_text(caption+'\n')
    short=('Figure 4. Matched human and quantitative supervision. (a) Frozen MolFormer embeddings '
       'pass through external 768→512→384→256 encoders trained on the same 681 source molecules '
       '(377 training, 304 validation; five paired seeds; no SMOTE). Human Good/Bad labels use '
       'contrastive training; continuous MIC uses regression. The learned encoders transform '
       'the same 105 target QAC salts. CatBoost is fitted separately for each representation, '
       'seed and target-training fold, with identical budgets and categorical task codes. '
       'Source-encoder weights remain frozen while target-fold labels train CatBoost. '
       '(b,c) Cation- and scaffold-held-out errors across four MIC/MBC endpoints. Each violin '
       'contains 420 compound–endpoint absolute errors averaged across five source runs; raw '
       'MolFormer is one fixed reference. Bars show medians and interquartile ranges; all '
       'values and tails are retained. These matched follow-ups exclude OOD and the missing '
       'historical Table 2 quantitative checkpoint. Different training objectives limit causal attribution.')
    (ROOT/'figure4_caption_EN.txt').write_text(short+'\n')
    (ROOT/'figure4_caption_RU.txt').write_text('Рисунок 4. Человеческая и количественная разметка внешних компактных энкодеров. '
       'Общие 681 source-молекула (377 training, 304 validation), пять сопряжённых seeds, без SMOTE. '
       'Замороженный MolFormer и MLP 768→512→384→256; Human Good/Bad обучают contrastive-энкодер, '
       'непрерывный MIC — regression-энкодер. Энкодеры применяются к одним и тем же 105 target-солям. '
       'Веса source-энкодеров заморожены при обучении CatBoost на target-fold разметке. '
       'CatBoost обучается отдельно для каждой ветки, seed и target-training fold при одинаковом '
       'бюджете и categorical-кодах четырёх MIC/MBC задач. Вертикальные виолины содержат 420 '
       'средних абсолютных ошибок по молекуле×endpoint при cation/scaffold holdout, усреднённых '
       'по пяти source-runs; Raw — один фиксированный контроль. Черты показывают медиану и IQR. '
       'Все значения и хвосты сохранены. OOD и отсутствующий исторический checkpoint Table 2 '
       'не использованы; разные функции обучения ограничивают причинную интерпретацию.\n')
    print('Figure4 PNG/PDF/SVG + exact errors + seed metrics + source hashes/captions saved')


if __name__=='__main__':main()
