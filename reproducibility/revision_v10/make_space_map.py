from pathlib import Path
import json
import numpy as np,pandas as pd
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.model_selection import GroupShuffleSplit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'figures';O.mkdir(exist_ok=True)
source=pd.read_csv(R/'data/matched-pooled_expert.csv');tr,va=next(GroupShuffleSplit(n_splits=1,test_size=.15,random_state=1729).split(source,groups=source.scaffold))
source['role']='Source training';source.loc[va,'role']='Source validation'
frames=[source]
for n,label in [('Q-HERO-405','External Q-HERO'),('QAC-104','QAC target'),('OOD-17','New OOD compounds')]:
    d=pd.read_csv(R/'data'/f'target_{n}.csv');d['role']=label;frames.append(d)
d=pd.concat(frames,ignore_index=True);assert d.can.is_unique
smis=json.loads((R/'data/smiles.json').read_text());index={s:i for i,s in enumerate(smis)};x=np.load(R/'data/molformer.npy')[[index[s] for s in d.can]]
is_train=d.role.values=='Source training';z=normalize(x.astype('float64'),norm='l2');pca=PCA(n_components=50,random_state=1729,svd_solver='full').fit(z[is_train]);z=pca.transform(z)
assert np.isfinite(z).all() and z.std()>1e-8
embedding=TSNE(n_components=2,perplexity=35,learning_rate='auto',init='pca',random_state=1729,n_iter=1500).fit_transform(z)
assert np.isfinite(embedding).all() and embedding.std()>1e-3
d['tsne_1']=embedding[:,0];d['tsne_2']=embedding[:,1];d[['can','cation','scaffold','role','y','tsne_1','tsne_2']].to_csv(R/'analysis/chemical_space_coordinates.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.right':False,'axes.spines.top':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(10,7));colors={'Source training':'#6ab753','Source validation':'#de9c48','External Q-HERO':'#4b8db6','QAC target':'#8a70aa','New OOD compounds':'#c63f6b'}
for label in colors:
    p=d[d.role==label];large=label=='New OOD compounds';ax.scatter(p.tsne_1,p.tsne_2,s=48 if large else 13,alpha=.9 if large else .55,color=colors[label],label=f'{label} (n={len(p)})',edgecolors='white' if large else 'none',linewidths=.5,zorder=4 if large else 2)
ax.set_xlabel('t-SNE component 1');ax.set_ylabel('t-SNE component 2');ax.set_title('Chemical-space illustration from frozen MolFormer features',loc='left',fontweight='bold');ax.legend(loc='upper left',framealpha=.95,fontsize=10)
fig.text(.5,.015,'Shared unsupervised projection; per-molecule L2 normalisation, PCA fitted on source training only.\nThe joint t-SNE uses held-out structures for illustration, never for prediction. Distances do not prove transfer or causality.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.07,1,1])
for ext in ['png','pdf','svg']:fig.savefig(O/('figureS10_chemical_space.'+ext),dpi=300,bbox_inches='tight')
(R/'analysis/chemical_space_meta.json').write_text(json.dumps({'rows':len(d),'role_counts':d.role.value_counts().to_dict(),'representation':'frozen MolFormer full salts','normalisation':'per molecule L2; PCA fit on source training only','tsne':'joint illustrative embedding; perplexity35, seed1729,1500iterations','not_prediction':'Held-out structures used only for illustration. No ellipses or OOD distance threshold. No causal or transfer conclusion from proximity.'},indent=2))
print(O)
