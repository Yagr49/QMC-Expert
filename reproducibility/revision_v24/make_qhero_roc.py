"""Real Q-HERO ROC curves, separate partial-backbone experiment, no new fits."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v24_qhero_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve,roc_auc_score

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
SOURCE=ROOT.parent/'qhero_author_comparison_20261014'
spec=importlib.util.spec_from_file_location('soft',ROOT.parent/'revision_v17/make_soft_figures.py')
soft=importlib.util.module_from_spec(spec);spec.loader.exec_module(soft);soft.theme()
ARMS=[('CB_human','Human','#72AE9C'),('CB_quantitative','Quantitative','#A293C9'),
      ('CB_shuffled_human','Shuffled human','#D4A782'),('CB_raw_MolFormer','Raw','#9098A4'),
      ('RF_35_descriptors','RF35','#7694AC')]


def main():
    p=pd.read_csv(SOURCE/'results/predictions.csv')
    target=pd.read_csv(SOURCE/'data/target.csv')
    summary=pd.read_csv(SOURCE/'results/summary.csv')
    fig,axes=plt.subplots(1,2,figsize=(180/25.4,96/25.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.09,right=.985,top=.86,bottom=.24,wspace=.24)
    common=np.linspace(0,1,1001);points=[];interpolated=[];metricrows=[]
    for panel,(protocol,title) in enumerate([('random_heldout20','Random holdout'),('scaffold_CV_fold','Scaffold holdout')]):
        ax=axes[panel]
        ax.plot([0,1],[0,1],color='#CFD3D9',lw=.75,ls='--',zorder=0)
        for name,label,color in ARMS:
            a=p[(p.model==name)&(p.protocol==protocol)]
            curves=[];aucs=[]
            for seed,g in a.groupby('seed'):
                g=g.sort_values('row_index');assert g.row_index.is_unique
                assert len(g)==(81 if panel==0 else 405)
                assert np.array_equal(g.label.values,target.sa_mic_um.le(8).astype(int).iloc[g.row_index].values)
                fpr,tpr,threshold=roc_curve(g.label,g.probability,drop_intermediate=False)
                auc=roc_auc_score(g.label,g.probability);aucs.append(auc)
                for x,y,cutoff in zip(fpr,tpr,threshold):
                    points.append(dict(model=name,protocol=protocol,seed=int(seed),FPR=float(x),TPR=float(y),threshold=float(cutoff)))
                curves.append(np.interp(common,fpr,tpr))
            values=np.array(curves);mean=values.mean(0)
            # These are means of individual empirical ROC curves, not ensemble probabilities.
            ax.plot(np.r_[0,common],np.r_[0,mean],color=color,lw=1.5,label=label,zorder=3,
                    linestyle='--' if name=='RF_35_descriptors' else '-')
            if len(values)>1:
                sd=values.std(0,ddof=1)
                ax.fill_between(common,np.clip(mean-sd,0,1),np.clip(mean+sd,0,1),color=color,alpha=.10,lw=0,zorder=1)
            else:sd=np.zeros_like(mean)
            for x,y,s in zip(common,mean,sd):
                interpolated.append(dict(model=name,protocol=protocol,FPR=float(x),mean_TPR=float(y),seed_SD=float(s)))
            metricrows.append(dict(model=name,protocol=protocol,n=len(a)//len(values),seeds=len(values),AUROC=float(np.mean(aucs)),AUROC_SD=float(np.std(aucs,ddof=1)) if len(aucs)>1 else None))
            refprotocol='scaffold_CV_pooled' if panel else protocol
            expected=summary[(summary.model==name)&(summary.protocol==refprotocol)].AUROC.item()
            assert abs(np.mean(aucs)-expected)<1e-12
        ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_aspect('equal',adjustable='box')
        ax.set_xticks([0,.5,1]);ax.set_yticks([0,.5,1]);ax.set_xlabel('False positive rate',fontsize=9)
        ax.set_title(title,fontsize=10,pad=10);ax.grid(alpha=.55)
        ax.text(-.15,1.07,chr(ord('a')+panel),fontsize=11,transform=ax.transAxes)
    axes[0].set_ylabel('True positive rate',fontsize=9)
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,.025),ncol=3,fontsize=8.5,columnspacing=1.6,handlelength=2)
    for ext in ['png','pdf','svg']:fig.savefig(OUT/f'figure5_qhero_real_roc.{ext}',dpi=600,facecolor='white')
    plt.close(fig)
    pd.DataFrame(points).to_csv(ROOT/'figure5_empirical_roc_points.csv',index=False)
    pd.DataFrame(interpolated).to_csv(ROOT/'figure5_mean_roc_points.csv',index=False)
    pd.DataFrame(metricrows).to_csv(ROOT/'figure5_roc_metrics.csv',index=False)
    record=dict(completed=True,target=405,endpoint='S. aureus MIC<=8 micromolar',
       source='v12 matched partial-MolFormer adaptation, not v5 external compact encoder',
       source_molecules=681,target_source_cation_overlap=0,source_decoder_seeds='Paired0..4',
       test_random=81,test_positive=72,test_negative=9,scaffold_OOF=405,scaffolds=29,
       curves='Mean of each seed ROC, common FPR grid1001; no ensemble probability',
       shade='Pointwise sampleSD across5 source/decoder runs, not confidence interval; single-fit raw/RF have no shade',
       no_new_fits=True,published421_not_same_cohort=True,
       source_sha256={str(SOURCE/'results/predictions.csv'):hashlib.sha256((SOURCE/'results/predictions.csv').read_bytes()).hexdigest(),
                      str(SOURCE/'data/target.csv'):hashlib.sha256((SOURCE/'data/target.csv').read_bytes()).hexdigest()},
       manuscript_modified=False)
    (ROOT/'figure5_provenance.json').write_text(json.dumps(record,indent=2))
    caption=('Figure5. ROC curves for the binary Q-HERO S.aureus endpoint(MIC≤8µM) on a common '
       'deduplicated405-molecule cohort. (a) Fixed stratified80/20 heldout(324training/81test;72active/9inactive '
       'in test). (b) Pooled out-of-fold predictions from five scaffold-heldout folds(29scaffolds). '
       'Human, quantitative and shuffled-human representations are independently pretrained through '
       'matched partial-MolFormer adaptation on681 source molecules excluding target full salts and '
       'cations; CatBoost classifiers are then independently trained on target-training folds using the '
       'same800iteration/depth6/learning-rate0.05 budget. These are separate from Figure4 compact encoders. '
       'Curves average individual ROC curves across five paired source/decoder seeds on a common FPR '
       'grid; shade is pointwise sampleSD, not a confidence interval. Raw MolFormer and RF35 are fixed '
       'seed0 references without estimated run variation. No ensemble probabilities or test-driven '
       'model selection is used. This is a paired comparison with RF retrained on the same405 molecules, '
       'not a direct numerical comparison with published421-row Q-HERO metrics.')
    (ROOT/'figure5_caption_detailed_EN.txt').write_text(caption+'\n')
    short=('Figure 5. ROC curves for Q-HERO S. aureus activity (MIC ≤ 8 µM) on 405 deduplicated '
       'molecules. (a) Fixed stratified random holdout: 324 training and 81 test molecules, including '
       '72 active and 9 inactive test compounds. (b) Pooled predictions from five scaffold-held-out '
       'folds across 29 scaffolds. Human, quantitative and shuffled-human representations use '
       'matched partial-MolFormer adaptation on 681 source molecules excluding target salts and '
       'cations; this architecture differs from Figure 4. CatBoost classifiers are fitted independently '
       'on target-training folds under the same protocol. Curves average individual ROC curves across '
       'five paired source/decoder seeds; shading is pointwise sample SD, not a confidence interval. '
       'Raw MolFormer and dashed RF35 are fixed seed 0 references. No ensemble probabilities or '
       'test-based model selection is used. Published 421-row metrics refer to a different cohort.')
    (ROOT/'figure5_caption_EN.txt').write_text(short+'\n')
    print(pd.DataFrame(metricrows).to_string(index=False))


if __name__=='__main__':main()
