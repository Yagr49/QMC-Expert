"""Observed OOD errors and conditional intervention estimates; no model refits."""
from pathlib import Path
import importlib.util, hashlib, json, os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v26_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent;REPRO=ROOT.parent;OUT=ROOT/'figures';OUT.mkdir(parents=True,exist_ok=True)
s=importlib.util.spec_from_file_location('soft',REPRO/'revision_v17/make_soft_figures.py')
soft=importlib.util.module_from_spec(s);s.loader.exec_module(soft);soft.theme()

def save(fig,stem):
    for ext in ['png','pdf','svg']:fig.savefig(OUT/(stem+'.'+ext),dpi=600,facecolor='white')
    plt.close(fig)

def main():
    cp=REPRO/'revision_v18/analysis/predictions.csv'
    p=pd.read_csv(cp);p=p[p.cohort.eq('OOD17')&p.schema.eq('full-QAC105')&p.encoding.eq('categorical')&p.qualifier.eq('=')]
    spec=[('matched_raw','Raw','#CDD2D9',1),('human','Human','#AFD9CE',5),
        ('mic_continuous','Quantitative','#C6BBE4',5),('human_shuffled','Shuffled\nhuman','#EBC8B0',5)]
    frames=[]
    for arm,label,color,seeds in spec:
        g=p[p.arm.eq(arm)].copy();g['absolute_error']=abs(g.prediction-g.y)
        assert len(g)==67*seeds and not g.duplicated(['seed','compound_id','task']).any()
        a=g.groupby(['compound_id','task'],as_index=False).agg(mean_absolute_error=('absolute_error','mean'),
            n_seeds=('seed','nunique'),y=('y','first'))
        assert len(a)==67 and a.n_seeds.eq(seeds).all()
        a['route']=arm;a['experiment']='compact';frames.append(a)
    bp=REPRO/'revision_v24/analysis/FT_route_endpoint_mean_absolute_errors.csv'
    q=pd.read_csv(bp);q=q[q.schema.eq('full-QAC105')].copy();q['experiment']='backbone'
    specs=[('frozen_head','Frozen\nhead','#91B7D6',3),('lora','LoRA','#B8A7D3',3),
        ('full_FT','Full FT','#E6B490',3),('human_direct','Human\ndirect','#D7A9BD',3),
        ('human_CatBoost','Human\n→ CB','#87CABA',3)]
    joined=pd.concat(frames+[q[['compound_id','task','mean_absolute_error','n_seeds','y','route','experiment']]],ignore_index=True)
    assert joined.groupby(['compound_id','task']).y.nunique().eq(1).all()
    assert len(joined)==67*9 and joined.compound_id.nunique()==17
    joined.to_csv(ROOT/'OOD_violin_values.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(180/25.4,100/25.4),sharey=True)
    fig.subplots_adjust(left=.08,right=.985,bottom=.19,top=.85,wspace=.17)
    for i,(ax,experiment,arms,title) in enumerate(zip(axes,['compact','backbone'],[spec,specs],
            ['Compact feature encoders','Backbone adaptation routes'])):
        ax.set_title(title,fontsize=9.5,pad=13);ax.text(-.12,1.07,'ab'[i],transform=ax.transAxes,fontsize=11)
        for x,(arm,label,color,seeds) in enumerate(arms):
            values=joined[(joined.experiment==experiment)&joined.route.eq(arm)].mean_absolute_error.to_numpy()
            assert len(values)==67
            parts=ax.violinplot(values,positions=[x],widths=.72,showextrema=False,bw_method='scott',points=200)
            for body in parts['bodies']:body.set_facecolor(color);body.set_edgecolor(color);body.set_alpha(.8);body.set_linewidth(.7)
            low,median,high=np.quantile(values,[.25,.5,.75])
            ax.vlines(x,low,high,color='#626A73',lw=1.6,zorder=4)
            ax.scatter([x],[median],s=13,color='white',edgecolor='#626A73',lw=.55,zorder=5)
            jitter=np.random.RandomState(2600+i*10+x).uniform(-.14,.14,len(values))
            ax.scatter(x+jitter,values,s=3.5,alpha=.27,color='#65717A',linewidths=0,zorder=3)
        ax.set_xticks(range(len(arms)));ax.set_xticklabels([a[1] for a in arms],fontsize=8)
        ax.set_xlim(-.6,len(arms)-.4);ax.set_ylim(0,8.05);ax.set_yticks([0,2,4,6,8]);ax.grid(axis='y',alpha=.6)
    axes[0].set_ylabel('Mean absolute error, log₂(mg/L)',fontsize=9)
    save(fig,'figure9_OOD17_prediction_errors')
    caption=('Figure 9. OOD prediction errors on 17 compounds from four chemical families. '
        '(a) Source-matched external compact encoders with categorical task codes: five '
        'source runs per guided arm and one raw reference. (b) Five backbone-adaptation '
        'routes, each evaluated in three runs. These are separate experiments with different '
        'decoding procedures. Each violin contains 67 exact molecule–endpoint absolute errors '
        'averaged within runs; points show individual summaries, white markers medians and '
        'bars interquartile ranges. All tails are retained. The IT505 E. coli MBC >500 mg/L '
        'bound is excluded from exact-error densities and retained separately. Human direct '
        'and Human → CB share partial-backbone source checkpoints, then use target adaptation '
        'or frozen source features with CatBoost. Neither panel uses OOD labels to train '
        'its target predictor. Correlated endpoints and four families limit inference.')
    (ROOT/'figure9_caption_EN.txt').write_text(caption+'\n')
    # Two separate inference panels retain each experiment's own conditional bootstrap.
    compact=pd.read_csv(REPRO/'revision_v18/analysis/contrasts.csv')
    partial=pd.read_csv(REPRO/'revision_v16/analysis/paired_bootstrap.csv')
    rows=[]
    for scheme in ['cation','scaffold','full-QAC105']:
        for contrast,label in [('human minus human_shuffled','Human − shuffled'),('human_weight_only minus human','Reset weights − intact')]:
            a=compact[(compact.comparison==contrast)&(compact.schema==scheme)&(compact.unit=='scaffold')].iloc[0]
            rows.append(dict(experiment='compact',scheme=scheme,contrast=label,delta=a.delta_RMSE,
                low=a.ci_low,high=a.ci_high,seeds=int(a.n_seeds),groups=int(a.n_clusters),draws=int(a.bootstrap_draws)))
        for contrast,a_name,b_name,label in [('real_vs_shuffled','expert/intact','expert-shuffled/intact','Human − shuffled'),
            ('weight_rewind_minus_intact','expert/rewind_all','expert/intact','Reset weights − intact')]:
            a=partial[(partial.contrast==contrast)&partial.a.eq(a_name)&partial.b.eq(b_name)&partial.schema.eq(scheme)&partial.grouping.eq('scaffold')].iloc[0]
            rows.append(dict(experiment='partial',scheme=scheme,contrast=label,delta=a.delta_RMSE_a_minus_b,
                low=a.low,high=a.high,seeds=int(a.seeds),groups=int(a.groups),draws=int(a.draws)))
    derived=pd.DataFrame(rows);derived.to_csv(ROOT/'interpretation_contrasts.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(180/25.4,98/25.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.25,right=.985,bottom=.17,top=.85,wspace=.19)
    regimes={'cation':'Cation','scaffold':'Scaffold','full-QAC105':'OOD-17'}
    for i,(ax,experiment,title) in enumerate(zip(axes,['compact','partial'],['Compact encoders','Partial backbone'])):
        data=derived[derived.experiment==experiment]
        ax.axvline(0,color='#C0C5CC',lw=.8,ls='--');ax.set_title(title,fontsize=9.5,pad=12)
        ax.text(-.025,1.075,'ab'[i],transform=ax.transAxes,fontsize=11)
        for j,a in enumerate(data.itertuples()):
            color='#78AF9D' if a.contrast.startswith('Human') else '#A393C7'
            ax.plot([a.low,a.high],[j,j],color=color,lw=1.5)
            ax.scatter([a.delta],[j],color=color,s=17,zorder=3)
        ax.set_yticks(range(len(data)));ax.set_yticklabels([regimes[a.scheme]+' · '+a.contrast for a in data.itertuples()],fontsize=8)
        ax.set_ylim(5.6,-.6);ax.set_xlim(-.68,.68);ax.set_xticks([-.6,-.3,0,.3,.6]);ax.grid(axis='x',alpha=.5)
        ax.set_xlabel('ΔRMSE, log₂(mg/L)',fontsize=9)
    save(fig,'figureS35_interpretation_controls')
    (ROOT/'figureS35_caption_EN.txt').write_text('Figure S35. Conditional prediction-loss contrasts for '
        'source-matched compact encoders and separate human-guided partial-backbone experiments. '
        'Human − shuffled compares label assignment; reset weights − intact restores source '
        'weights while retaining the experiment-specific feature-map state. Dots are ΔRMSE and '
        'lines conditional 95% paired seed/scaffold bootstrap intervals. Both panels use five '
        'source runs; compact intervals use 10,000 resamples and partial-backbone intervals '
        '5,000. Cation/scaffold tests contain 29 scaffold clusters; OOD contains four families. '
        'Prediction models are fixed during resampling; intervals are exploratory and unadjusted. '
        'Compact resets retain BatchNorm state and are not equivalent to an untrained model. '
        'The experiments have different architectures and decoders, so contrasts are interpreted '
        'within each panel. These are computational interventions on prediction procedures, '
        'rather than causal effects on antibacterial biology.\n')
    manifest=dict(completed=True,OOD_compounds=17,OOD_exact_endpoints=67,OOD_bound='IT505 Ec_MBC >500 mg/L',
        violin_values=603,no_ensemble_error=True,no_tail_clipping=True,no_model_refits=True,
        source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in [cp,bp,
            REPRO/'revision_v18/analysis/contrasts.csv',REPRO/'revision_v16/analysis/paired_bootstrap.csv']})
    (ROOT/'figure_validation.json').write_text(json.dumps(manifest,indent=2))
    print('OOD17 figure and SI intervention figure saved from completed predictions/contrasts.')

if __name__=='__main__':main()
