from pathlib import Path
import importlib.util,json
import numpy as np,pandas as pd
from scipy.stats import gaussian_kde
from rdkit import Chem
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from analyse_extension import load,MODELS
R=Path(__file__).resolve().parent;O=R/'figures';O.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('prep',R.parent/'revision_v9/prepare_experiment.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
book=Path('/Users/egorilin/Desktop/Veresh_Dataset_Paper/QMR_dataset_JCIM_v8_publication_ready.xlsx')
raw=pd.read_excel(book,sheet_name='All')
raw=prep.standard(raw,'Canonical SMILES_v2','MIC_uM_unified');raw=raw[(raw.y>0)&(raw.MIC_qualifier=='none')].copy()
ban=set().union(*(set(pd.read_csv(R/'data'/f'target_{n}.csv').cation) for n in ['QAC-104','Q-HERO-405','OOD-17']))
raw=raw[~raw.cation.isin(ban)];raw['log2_mic']=np.log2(raw.y)
# A molecule appears once per organism class; reports/strains are summarised, not independent plot units.
dist=raw.groupby(['can','Organism_class']).agg(log2_mic=('log2_mic','median'),cationic_N=('n_cationic_N_v2','first'),records=('y','size'),strains=('Strain_normalized','nunique')).reset_index()
dist=dist[dist.cationic_N.isin([1,2])&dist.Organism_class.isin(['Gram+','Gram-','Fungal'])].copy()
dist.to_csv(R/'analysis/violin_source_MIC.csv',index=False)
q=pd.read_csv(R/'data/target_Q-HERO-405.csv');q['cationic_N']=q.can.map(lambda s:sum(a.GetAtomicNum()==7 and a.GetFormalCharge()>0 for a in Chem.MolFromSmiles(s).GetAtoms()))
q[['can','y','cationic_N','scaffold']].to_csv(R/'analysis/violin_QHERO_MIC.csv',index=False)
p,_=load();p=p[(p.panel=='matched-pooled')&(p.target=='Q-HERO-405')&(p.arm.isin(['expert','quant-continuous']))].copy();p['absolute_error']=abs(p.y-p.pred)
errors=p.groupby(['backbone','arm','can']).agg(absolute_error=('absolute_error','mean'),seeds=('seed','nunique')).reset_index()
assert len(errors)==4*2*405 and (errors.seeds==5).all();errors.to_csv(R/'analysis/violin_OOF_errors.csv',index=False)
paired=errors.pivot(index=['backbone','can'],columns='arm',values='absolute_error').reset_index();paired['expert_minus_MIC']=paired.expert-paired['quant-continuous'];paired.to_csv(R/'analysis/violin_paired_error.csv',index=False)
BLUE='#3b729d';ORANGE='#d39b56';PURPLE='#77598e';TEAL='#418b82'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.right':False,'axes.spines.top':False,'pdf.fonttype':42})
fig,axs=plt.subplots(2,2,figsize=(14,10.5),gridspec_kw={'hspace':.48,'wspace':.30})
summaries=[]
def violin(ax,data,x,color,side='both',width=.34,tag=''):
    data=np.asarray(data,float);data=data[np.isfinite(data)];assert len(data)>2
    # KDE is computed in the actual plotted coordinate (log2 MIC or log2 error), never linear MIC then warped.
    low,high=float(data.min()),float(data.max());grid=np.linspace(low,high,240)
    density=gaussian_kde(data,bw_method='scott')(grid) if np.std(data)>1e-8 else np.ones(len(grid));density=density/density.max()*width
    left=x-density if side!='right' else np.full_like(grid,x);right=x+density if side!='left' else np.full_like(grid,x)
    ax.fill_betweenx(grid,left,right,color=color,alpha=.42,lw=1.3,edgecolor=color)
    quant=np.quantile(data,[.25,.5,.75]);centre=x+(-.075 if side=='left' else .075 if side=='right' else 0)
    ax.plot([centre,centre],[quant[0],quant[2]],color=color,lw=2.5);ax.plot([centre-.07,centre+.07],[quant[1],quant[1]],color=color,lw=3)
    summaries.append({'panel':tag,'n':len(data),'q25':float(quant[0]),'median':float(quant[1]),'q75':float(quant[2]),'units':'plotted coordinates'})
    return len(data)
ax=axs[0,0];groups=['Gram+','Gram-','Fungal'];ticks=[]
for i,g in enumerate(groups):
    ns=[]
    for n,color,side in [(1,BLUE,'left'),(2,ORANGE,'right')]:
        vals=dist[(dist.Organism_class==g)&(dist.cationic_N==n)].log2_mic.values;ns.append(violin(ax,vals,i,color,side,tag='A '+g+f' N={n}'))
    ticks.append(g+f'\nmono n={ns[0]}\nbis n={ns[1]}')
ax.set_xticks(range(3));ax.set_xticklabels(ticks);ax.set_title('A   Source MIC by organism class',loc='left',fontweight='bold');ax.set_ylabel('MIC (µM; logarithmic spacing)')
ax.set_yticks([-2,0,2,4,6,8,10,12,14,16]);ax.set_yticklabels(['0.25','1','4','16','64','256','1024','4096','16384','65536']);ax.legend(handles=[Patch(facecolor=BLUE,alpha=.42,label='mono: one cationic N'),Patch(facecolor=ORANGE,alpha=.42,label='bis: two cationic N')],fontsize=9,loc='upper left')
ax=axs[0,1];labels=[]
for i,(n,color,label) in enumerate([(1,BLUE,'mono'),(2,ORANGE,'bis'),(3,PURPLE,'≥3 cationic N')]):
    sub=q[q.cationic_N>=3] if n==3 else q[q.cationic_N==n];num=violin(ax,sub.y.values,i,color,tag='B '+label);labels.append(label+f'\nn={num}')
ax.set_xticks(range(3));ax.set_xticklabels(labels);ax.set_title('B   External Q-HERO measured MIC',loc='left',fontweight='bold');ax.set_ylabel('MIC (µM; logarithmic spacing)');ax.set_yticks([-2,0,2,4,6,8]);ax.set_yticklabels(['0.25','1','4','16','64','256'])
names=['MolFormer-XL','c3-MoLFormer','ChemBERTa-100M','ChemFM-1B'];ax=axs[1,0]
for i,m in enumerate(MODELS):
    for arm,col,side in [('expert',PURPLE,'left'),('quant-continuous',TEAL,'right')]:violin(ax,errors[(errors.backbone==m)&(errors.arm==arm)].absolute_error,i,col,side,tag='C '+m+' '+arm)
ax.set_xticks(range(4));ax.set_xticklabels(names,rotation=12,ha='right');ax.set_title('C   Errors on the same held-out molecules',loc='left',fontweight='bold');ax.set_ylabel('Mean absolute log₂ MIC error per molecule');ax.legend(handles=[Patch(facecolor=PURPLE,alpha=.42,label='Human binary supervision'),Patch(facecolor=TEAL,alpha=.42,label='Continuous MIC supervision')],fontsize=9)
ax=axs[1,1]
for i,m in enumerate(MODELS):
    d=paired[paired.backbone==m].expert_minus_MIC.values;violin(ax,d,i,PURPLE,tag='D '+m)
    rng=np.random.default_rng(1729+i);ax.scatter(i+rng.uniform(-.19,.19,len(d)),d,s=5,alpha=.15,color=PURPLE,rasterized=True)
ax.axhline(0,color='.35',ls='--',lw=1);ax.set_xticks(range(4));ax.set_xticklabels(names,rotation=12,ha='right');ax.set_title('D   Paired error difference per molecule',loc='left',fontweight='bold');ax.set_ylabel('|error| human − |error| continuous MIC\n(log₂ µM; negative favours human)')
for ax in axs.flat:ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Chemical context and paired external prediction errors',fontsize=17,fontweight='bold',y=.99)
fig.text(.5,.015,'Bars: median and IQR. A: exact uncensored source MIC, aggregated once per molecule × organism class.\nB: external measured MIC; one compound with no cationic N omitted. C–D: fixed scaffold-held-out predictions; descriptive distributions, not independent tests.',ha='center',fontsize=9)
fig.subplots_adjust(top=.92,bottom=.14)
for ext in ['png','pdf','svg']:fig.savefig(O/('figure9_MIC_error_violins.'+ext),dpi=300,bbox_inches='tight')
(R/'analysis/violin_summary.json').write_text(json.dumps({'density':'Scott KDE in plotted log2 MIC/error coordinates, clipped to observed support','summaries':summaries,'source_rows':len(raw),'source_plot_molecule_class_pairs':len(dist),'note':'Molecules may appear in multiple organism classes; classes are not independent. No p-values or biological causal effect inferred.'},indent=2))
print(O)
