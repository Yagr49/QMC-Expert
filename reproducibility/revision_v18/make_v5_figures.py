"""Native vector v5 pipeline and actual archived feature-space illustration."""
from pathlib import Path
import os,importlib.util,json,hashlib,sys
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v18_matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from rdkit import Chem
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
REPRO=ROOT.parent
spec=importlib.util.spec_from_file_location('soft',REPRO/'revision_v17/make_soft_figures.py')
soft=importlib.util.module_from_spec(spec);spec.loader.exec_module(soft)
sys.path.insert(0,str(REPRO/'revision_v14'))
import drawing_style as acs
soft.theme()

def save(fig,name):
 soft.finish(fig)
 for ext in ['pdf','png','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=300,bbox_inches='tight',facecolor='white')
 plt.close(fig)
def box(ax,x,y,w,h,text,color='#F1F3F7',size=10):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.007,rounding_size=.018',fc=color,ec='#D4D7DD',lw=.65))
 ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,linespacing=1.5)
def arrow(ax,a,b,dashed=False):
 ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',lw=.9,color='#8C939D',linestyle='--' if dashed else '-'))
def vector(ax,x,y,w,h,values,color):
 values=np.asarray(values);v=(values-values.mean())/max(values.std(),1e-8)
 for i,value in enumerate(v):
  ax.add_patch(Rectangle((x+i*w/len(v),y),w/len(v)*.82,h,fc=color,ec='none',alpha=.2+.65*np.clip((value+2)/4,0,1)))

def pipeline(q,raw,human):
 example=next(i for i,s in enumerate(q.can) if sum(a.GetAtomicNum()==7 and a.GetFormalCharge()>0 for a in Chem.MolFromSmiles(s).GetAtoms())==1)
 fig,ax=plt.subplots(figsize=(9.3,4.85));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
 ax.text(.015,.96,'a) Learn the molecular representation',fontsize=12)
 chem=fig.add_axes([.045,.49,.135,.245]);record=acs.acs_svg(q.can.iloc[example]);acs.draw_acs(chem,record,record[2]+8,record[3]+8)
 ax.text(.08,.47,'QAC structure',ha='center',fontsize=10)
 box(ax,.22,.49,.18,.19,'Frozen\nMolFormer','#E3ECF5',11)
 ax.text(.31,.43,'SMILES → features',ha='center',fontsize=9,color='#737780')
 vector(ax,.465,.56,.10,.065,raw[example,:24],'#94B6D5');ax.text(.515,.47,'768-D',ha='center',fontsize=10)
 box(ax,.635,.49,.22,.19,'Trainable encoder\n768 → 512 → 384 → 256','#EBE5F6',10)
 vector(ax,.91,.56,.068,.065,human[example,:24],'#8B7BC7');ax.text(.943,.47,'256-D',ha='center',fontsize=10)
 for a,b in [((.155,.585),(.21,.585)),((.41,.585),(.455,.585)),((.575,.585),(.625,.585)),((.868,.585),(.90,.585))]:arrow(ax,a,b)
 box(ax,.42,.79,.21,.085,'Human Good / Bad','#EBE5F6',10)
 box(ax,.70,.79,.27,.085,'Quantitative supervision','#E0F0EB',10)
 arrow(ax,(.525,.785),(.72,.69),True);arrow(ax,(.835,.785),(.79,.69),True)
 ax.text(.745,.73,'training objective',ha='center',fontsize=9,color='#737780')
 ax.text(.015,.345,'b) Use the learned representation',fontsize=12)
 vector(ax,.065,.16,.13,.065,human[example,:24],'#8B7BC7');ax.text(.13,.11,'Guided vector',ha='center',fontsize=10)
 ax.text(.24,.195,'+',ha='center',va='center',fontsize=21,color='#8C939D')
 box(ax,.295,.105,.20,.17,'Task code\nspecies + MIC / MBC','#E0F0EB',10)
 box(ax,.61,.105,.145,.17,'CatBoost','#F7EBDD',11)
 box(ax,.855,.095,.12,.19,'MIC / MBC\nlog₂(mg/L)','#F1F3F7',10)
 arrow(ax,(.505,.19),(.60,.19));arrow(ax,(.765,.19),(.845,.19))
 fig.canvas.draw();acs.fix_acs_strokes(fig,[chem],record[2]+8)
 save(fig,'figure1_v5_guided_embedding_pipeline')
 return example

def feature_space(q,raw,human):
 count=np.array([sum(a.GetAtomicNum()==7 and a.GetFormalCharge()>0 for a in Chem.MolFromSmiles(s).GetAtoms()) for s in q.can])
 groups=np.minimum(count,3)
 fig=plt.figure(figsize=(8.1,5.8));top=fig.add_axes([.035,.74,.94,.23]);top.axis('off');top.set_xlim(0,1);top.set_ylim(0,1)
 box(top,.015,.25,.23,.49,'MolFormer features\n768-D','#E3ECF5',11)
 box(top,.395,.25,.23,.49,'Learned projection','#EBE5F6',11)
 box(top,.775,.25,.21,.49,'Human embedding\n256-D','#EBE5F6',11)
 arrow(top,(.258,.495),(.38,.495));arrow(top,(.64,.495),(.762,.495))
 projections=[];coords=[]
 axes=[fig.add_axes([.09,.16,.37,.50]),fig.add_axes([.57,.16,.37,.50])]
 for ax,matrix,title,which in zip(axes,[raw,human],['Pretrained features','Guided features'],['raw','human']):
  z=normalize(matrix.astype(np.float64));model=PCA(n_components=2,svd_solver='full');xy=model.fit_transform(z)
  for number,color,marker,label in [(1,'#94B6D5','o','Mono-QAC'),(2,'#52AB98','s','Bis-QAC'),(3,'#D8A377','^','Multi-QAC')]:
   select=groups==number;ax.scatter(xy[select,0],xy[select,1],s=25,color=color,marker=marker,alpha=.75,linewidths=.3,edgecolors='white',label=label+' (n = '+str(int(select.sum()))+')')
  ax.set_title(title,pad=10);ax.set_xlabel(f'PC1 ({model.explained_variance_ratio_[0]*100:.1f}%)');ax.set_ylabel(f'PC2 ({model.explained_variance_ratio_[1]*100:.1f}%)');ax.grid(axis='y',alpha=.5)
  projections.append(dict(representation=which,shape=list(matrix.shape),explained_variance_ratio=model.explained_variance_ratio_.tolist(),projection='Independent PCA after per-row L2 normalisation'))
  frame=q[['compound_id','can']].copy();frame['representation']=which;frame['cationic_N']=count;frame['pc1']=xy[:,0];frame['pc2']=xy[:,1];coords.append(frame)
 handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.02),fontsize=10)
 save(fig,'figure6_v5_embedding_geometry')
 pd.concat(coords,ignore_index=True).to_csv(ROOT/'feature_space_coordinates.csv',index=False)
 return projections

def main():
 q=pd.read_csv(REPRO/'revision_v14/data/QAC105.csv')
 paths=[REPRO/'revision_v14/representations/legacy-raw_QAC105.npy',REPRO/'revision_v14/representations/legacy-human_QAC105.npy']
 raw,human=[np.load(p) for p in paths];assert raw.shape==(105,768) and human.shape==(105,256)
 example=pipeline(q,raw,human);projections=feature_space(q,raw,human)
 (ROOT/'figure_provenance.json').write_text(json.dumps(dict(base='v5 Figures 1 and 6; explanatory redraw',
  exact_example_compound=q.compound_id.iloc[example],ACS1996=True,font='Aptos',
  input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
  projections=projections,n_molecules=105,source_provenance='Archived v5 human encoder; source corpus overlaps QAC105',
  visualisation_only=True,activities_used_for_projection=False,independent_axes=True,
  no_structural_biological_variance_partition=True),indent=2))
 print('v5 pipeline and actual 105-molecule feature-space illustrations saved')

if __name__=='__main__':main()
