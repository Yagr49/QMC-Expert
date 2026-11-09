from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v14_matplotlib')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
import drawing_style as style
ROOT=Path(__file__).resolve().parent
ARMS=['expert','quant-continuous','quant-binary']
LABEL={'expert':'Human','quant-continuous':'Continuous MIC','quant-binary':'Binary MIC','raw-molformer':'Raw MolFormer','task-median':'Task median'}
COLOR={'expert':style.PALETTE['human'],'quant-continuous':style.PALETTE['continuous'],'quant-binary':style.PALETTE['binary'],'raw-molformer':style.PALETTE['raw']}
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
TLABEL={'Sa_MIC':'S. aureus · MIC','Sa_MBC':'S. aureus · MBC','Ec_MIC':'E. coli · MIC','Ec_MBC':'E. coli · MBC'}

def save(fig,name):
    style.finish(fig)
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/'figures'/(name+'.'+ext),dpi=230,bbox_inches='tight')
    plt.close(fig)

def box(ax,x,y,w,h,text,color):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.015',fc=color,ec='#93999f',lw=.7))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10,linespacing=1.45)

def arrow(ax,a,b):ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',lw=1,color='#51565c'))

def design():
    fig,ax=plt.subplots(figsize=(11,7));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    ax.text(.02,.96,'a) Learn molecular representations',fontsize=14)
    box(ax,.025,.72,.21,.16,'Same 681 source molecules\n377 train / 304 validation\nTarget cations excluded','#e9edf1')
    box(ax,.30,.73,.19,.14,'Pretrained MolFormer\n768 features','#d9e9f5');arrow(ax,(.24,.80),(.295,.80))
    for y,text,col in [(.82,'Human Good / Bad','#e5dbee'),(.65,'Continuous pooled MIC','#d5e7e2'),(.48,'Binary pooled MIC','#f3dfd3')]:
        box(ax,.57,y,.22,.12,text+'\n+ shuffled control',col);arrow(ax,(.495,.80),(.56,y+.06))
    box(ax,.84,.64,.13,.20,'Same training\nbudget and\n5 paired seeds','#f3efdf')
    for y in [.88,.71,.54]:arrow(ax,(.80,y),(.835,.74))
    ax.text(.02,.405,'b) Predict the original endpoints and test new scaffolds',fontsize=14)
    box(ax,.025,.17,.23,.17,'Original QAC-105\n103 cations · 420 endpoints\n5 cation-grouped folds','#e2edf5')
    box(ax,.325,.17,.28,.17,'Fixed CatBoost decoder\nTask: species + MIC / MBC\nOne-hot or fixed text vectors','#e6dfee');arrow(ax,(.265,.255),(.318,.255))
    box(ax,.68,.17,.29,.17,'Named OOD-17\n4 unseen scaffold families\n67 exact values + 1 >500','#f5e2d4');arrow(ax,(.61,.255),(.672,.255))
    ax.text(.025,.065,'All endpoints of a cation stay in one fold. OOD measurements are used only for scoring.',fontsize=10)
    ax.text(.025,.015,'Historical 256-d encoders and Q-HERO analyses are retained separately in Supporting Information.',fontsize=9,color='#626870')
    fig.tight_layout();save(fig,'figure1_supervision_and_transfer')

def parity(p,s,cohort,name):
    fig,axes=plt.subplots(4,3,figsize=(7.2,9.6),sharex=True,sharey=True)
    data=p[(p.cohort==cohort)&(p.encoding=='onehot')&(p.provenance=='matched-source-excluded')]
    for i,task in enumerate(TASKS):
        for j,arm in enumerate(ARMS):
            ax=axes[i,j];d=data[(data.task==task)&(data.arm==arm)]
            means=d.groupby(['can','qualifier'],as_index=False).agg(y=('y','first'),prediction=('prediction','mean'))
            exact=means.qualifier=='='
            ax.scatter(means.y[exact],means.prediction[exact],color=COLOR[arm],alpha=.65,s=25,edgecolors='white',linewidths=.3)
            if (~exact).any():
                ax.scatter(means.y[~exact],means.prediction[~exact],marker='>',s=65,color='#484d54',label='Right-censored')
            ax.plot([-4,10],[-4,10],ls='--',color='#72787e',lw=.9)
            stat=s[(s.cohort==cohort)&(s.encoding=='onehot')&(s.arm==arm)&(s.task==task)].iloc[0]
            ax.text(.06,.93,f'R² = {stat.R2:.2f}\nRMSE = {stat.RMSE:.2f}\nn = {int(stat.n)}',transform=ax.transAxes,va='top',fontsize=8,
                bbox=dict(boxstyle='square,pad=.35',fc='white',ec='#ced2d6',alpha=.94))
            ax.set_xlim(-3.5,10);ax.set_ylim(-3.5,10);ax.set_xticks([-2,2,6,10]);ax.set_yticks([-2,2,6,10]);ax.grid(alpha=.25)
            ax.set_title(f'{chr(97+i*3+j)}) '+(LABEL[arm] if i==0 else TLABEL[task]),loc='left',fontsize=8.5)
            if j==0:ax.set_ylabel(TLABEL[task]+'\nPredicted log₂(mg/L)',fontsize=9)
            if i==3:ax.set_xlabel('Measured log₂(mg/L)')
    fig.subplots_adjust(wspace=.12,hspace=.3,bottom=.08,top=.96,left=.11,right=.99)
    fig.text(.11,.025,'Points: seed-mean predictions. Statistics: mean seed-specific scores.',fontsize=8)
    save(fig,name)

def encodings(s):
    fig,axes=plt.subplots(2,2,figsize=(10,7.5),sharey=True)
    for i,(task,ax) in enumerate(zip(TASKS,axes.ravel())):
        for j,arm in enumerate(ARMS+['raw-molformer']):
            rows=s[(s.cohort=='QAC105')&(s.task==task)&(s.arm==arm)&s.encoding.isin(['onehot','text'])]
            one=rows[rows.encoding=='onehot'].iloc[0];text=rows[rows.encoding=='text'].iloc[0]
            ax.plot([j-.12,j+.12],[one.R2,text.R2],color=COLOR[arm],lw=1.1)
            ax.errorbar(j-.12,one.R2,yerr=one.R2_sd,fmt='o',ms=7,color=COLOR[arm],capsize=3)
            ax.errorbar(j+.12,text.R2,yerr=text.R2_sd,fmt='s',ms=7,mfc='white',mec=COLOR[arm],ecolor=COLOR[arm],capsize=3)
        ax.axhline(0,color='#969da4',lw=.7,ls='--');ax.set_xticks(range(4));ax.set_xticklabels(['Human','Continuous\nMIC','Binary\nMIC','Raw'],fontsize=9)
        ax.set_title(f'{chr(97+i)}) '+TLABEL[task],loc='left');ax.grid(axis='y',alpha=.3)
        if i%2==0:ax.set_ylabel('Cation-held-out R²')
    fig.text(.14,.025,'● One-hot     □ Text embedding     Error bars: source-seed SD; raw has one fixed run.',fontsize=10)
    fig.tight_layout(rect=(0,.05,1,1));save(fig,'figure3_task_encoding')

def ood_families(o):
    records=[];titles=[]
    names={'G1':'CF₃-dihydropyran · mono-QAC','G2':'Kojic acid · bis-QAC','G3':'Tetrahydropyridine · bis-QAC','G4':'Glycoluril · tetra-QAC'}
    for g,d in o.groupby('scaffold_group',sort=True):
        row=d.iloc[0];records.append(style.acs_svg(row.can));titles.append(g+' · '+names[g]+f'\n{len(d)} compounds · representative {row.code}')
    cw=max(r[2] for r in records)+15;ch=max(r[3] for r in records)+10
    fig,axes=plt.subplots(2,2,figsize=(11.7,8.5))
    for i,(ax,record,title) in enumerate(zip(axes.ravel(),records,titles)):
        style.draw_acs(ax,record,cw,ch);ax.set_title(f'{chr(97+i)}) '+title,fontsize=11,pad=10,loc='left')
    fig.tight_layout(rect=(0,.045,1,1));style.fix_acs_strokes(fig,axes.ravel(),cw)
    fig.text(.07,.012,'ACS 1996 depictions. All four cation-scaffold families are absent from source and QAC-105.',fontsize=10)
    save(fig,'figure4_OOD_families_ACS1996')

def violations(p):
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),sharey=True)
    for ax,cohort,panel in zip(axes,['QAC105','OOD17'],['a','b']):
        d=p[(p.cohort==cohort)&(p.encoding=='onehot')&p.arm.isin(['expert','quant-continuous'])&(p.qualifier=='=')].copy()
        d['absolute_error']=np.abs(d.y-d.prediction)
        molecule=d.groupby(['arm','task','can'],as_index=False).absolute_error.mean()
        for i,task in enumerate(TASKS):
            for arm,side in [('expert',-1),('quant-continuous',1)]:
                values=molecule[(molecule.task==task)&(molecule.arm==arm)].absolute_error.values
                violin=ax.violinplot(values,positions=[i],widths=.78,showextrema=False)
                body=violin['bodies'][0];verts=body.get_paths()[0].vertices
                verts[:,0]=np.minimum(verts[:,0],i) if side==-1 else np.maximum(verts[:,0],i)
                body.set_facecolor(COLOR[arm]);body.set_edgecolor(COLOR[arm]);body.set_alpha(.45)
                x=i+side*.08;lo,med,hi=np.quantile(values,[.25,.5,.75]);ax.plot([x,x],[lo,hi],color=COLOR[arm],lw=2)
                ax.plot([x-.05,x+.05],[med,med],color=COLOR[arm],lw=2)
                if cohort=='OOD17':
                    jitter=np.linspace(.11,.33,len(values));ax.scatter(i+side*jitter,values,s=12,c=COLOR[arm],alpha=.65)
        ax.set_xticks(range(4));ax.set_xticklabels(['Sa MIC','Sa MBC','Ec MIC','Ec MBC'],fontsize=9);ax.set_title(f'{panel}) '+cohort,loc='left')
        ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.25)
    axes[0].set_ylabel('Absolute error in log₂(mg/L)')
    fig.text(.15,.025,'Left halves: human supervision. Right halves: continuous MIC. Median and IQR; exact endpoints only.',fontsize=10)
    fig.tight_layout(rect=(0,.05,1,1));save(fig,'figure5_paired_error_violins')

def ood_individual(p,o):
    fig,axes=plt.subplots(4,1,figsize=(11.5,11),sharex=True)
    ordered=o.sort_values(['scaffold_group','code']);codes=ordered.code.tolist()
    for i,(ax,task) in enumerate(zip(axes,TASKS)):
        data=p[(p.cohort=='OOD17')&(p.task==task)&(p.encoding=='onehot')]
        truth=data.drop_duplicates('compound_id').set_index('compound_id').loc[codes]
        exact=truth.qualifier=='=';xx=np.arange(17)
        ax.scatter(xx[exact],truth.y.values[exact],c='#333940',marker='D',s=26,label='Measured')
        if (~exact).any():ax.scatter(xx[~exact],truth.y.values[~exact],c='#333940',marker='^',s=65,label='Reported lower bound')
        for arm,shift in [('expert',-.17),('quant-continuous',0),('quant-binary',.17)]:
            d=data[data.arm==arm].groupby('compound_id').prediction.agg(['mean','std']).loc[codes]
            ax.errorbar(xx+shift,d['mean'],yerr=d['std'],fmt='o',ms=4,color=COLOR[arm],capsize=2,label=LABEL[arm])
        counts=ordered.groupby('scaffold_group',sort=True).size().values
        for limit in np.cumsum(counts)[:-1]-.5:ax.axvline(limit,color='#ced3d8',ls=':',lw=1)
        ax.set_title(f'{chr(97+i)}) '+TLABEL[task],loc='left');ax.set_ylabel('log₂(mg/L)');ax.grid(axis='y',alpha=.25)
        if i==0:ax.legend(ncol=4,fontsize=8,loc='lower left')
    axes[-1].set_xticks(range(17));axes[-1].set_xticklabels(codes,rotation=50,ha='right',fontsize=9)
    fig.tight_layout();save(fig,'figureS20_OOD17_individual_endpoints')

def main():
    (ROOT/'figures').mkdir(exist_ok=True);style.theme()
    p=pd.read_csv(ROOT/'results/predictions.csv');s=pd.read_csv(ROOT/'analysis/summary.csv');o=pd.read_csv(ROOT/'data/OOD17.csv')
    design();parity(p,s,'QAC105','figure2_QAC105_parity');encodings(s);ood_families(o);violations(p)
    parity(p,s,'OOD17','figureS19_OOD17_parity');ood_individual(p,o)
    scaffold=pd.read_csv(ROOT/'analysis/scaffold_summary.csv')
    fig,axes=plt.subplots(2,2,figsize=(9,6.5),sharey=True)
    for i,(task,ax) in enumerate(zip(TASKS,axes.ravel())):
        for j,arm in enumerate(ARMS+['raw-molformer']):
            a=s[(s.arm==arm)&(s.task==task)&(s.cohort=='QAC105')&(s.encoding=='onehot')].iloc[0]
            b=scaffold[(scaffold.arm==arm)&(scaffold.task==task)&(scaffold.cohort=='QAC105')].iloc[0]
            ax.plot([j-.12,j+.12],[a.R2,b.R2],c=COLOR[arm],lw=.9)
            ax.errorbar(j-.12,a.R2,yerr=a.R2_sd,fmt='o',color=COLOR[arm],ms=5,capsize=2)
            ax.errorbar(j+.12,b.R2,yerr=b.R2_sd,fmt='s',mfc='white',mec=COLOR[arm],ecolor=COLOR[arm],ms=5,capsize=2)
        ax.axhline(0,c='#858c93',ls='--',lw=.7);ax.grid(axis='y',alpha=.25)
        ax.set_title(f'{chr(97+i)}) '+TLABEL[task],loc='left');ax.set_xticks(range(4));ax.set_xticklabels(['Human','Continuous\nMIC','Binary\nMIC','Raw'],fontsize=9)
        if i%2==0:ax.set_ylabel('Endpoint-specific R²')
    fig.text(.13,.02,'● Cation holdout     □ Scaffold holdout     Bars: source-seed SD.',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,1));save(fig,'figureS21_scaffold_transfer')
    # Reuse the audited complete 105 / 17 structure atlases; no compound is hidden.
    import shutil
    old=ROOT.parent/'revision_v13/figures'
    for name in ['original_QAC105_structures.pdf','original_QAC105_structures.svg','figureS20_OOD17_structures.pdf','figureS20_OOD17_structures.svg']:
        destination=name.replace('figureS20_OOD17_structures','OOD17_structures')
        shutil.copy2(old/name,ROOT/'figures'/destination)
    print('Saved eight figures in PNG, PDF and SVG, plus complete structure atlases.')

if __name__=='__main__':main()
