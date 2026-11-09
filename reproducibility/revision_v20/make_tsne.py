"""Journal figure from exact archived PDF markers: soft Aptos, minimal text, vector output."""
from pathlib import Path
import os,importlib.util,json,hashlib
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v20_matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
s=importlib.util.spec_from_file_location('theme',ROOT.parent/'revision_v17/make_soft_figures.py');soft=importlib.util.module_from_spec(s);s.loader.exec_module(soft);soft.theme()
def main():
 data=pd.read_csv(ROOT/'tsne_pdf_marker_coordinates.csv');checks=[]
 for variant,bad,good in [('soft','#D8A377','#68B5A7'),('lavender','#A99ACF','#68B5A7')]:
  fig,axes=plt.subplots(1,2,figsize=(8.6,4.0))
  for i,(ax,panel,title) in enumerate(zip(axes,['before','after'],['Before contrastive learning','After contrastive learning'])):
   a=data[data.panel==panel]
   for label,color in [('Bad',bad),('Good',good)]:
    points=a[a.label==label];artist=ax.scatter(points.x_pdf,points.y_pdf,s=22,color=color,alpha=.86,edgecolors='white',linewidths=.45,zorder=3)
    assert np.array_equal(np.asarray(artist.get_offsets()),points[['x_pdf','y_pdf']].to_numpy())
   dx=a.x_pdf.max()-a.x_pdf.min();dy=a.y_pdf.max()-a.y_pdf.min()
   ax.set_xlim(a.x_pdf.min()-.075*dx,a.x_pdf.max()+.075*dx);ax.set_ylim(a.y_pdf.min()-.085*dy,a.y_pdf.max()+.085*dy)
   ax.set_aspect('equal',adjustable='box');ax.set_xticks([]);ax.set_yticks([]);ax.grid(False)
   ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
   for side in ['bottom','left']:ax.spines[side].set_color('#E1E4E9');ax.spines[side].set_linewidth(.65)
   ax.set_title(title,fontsize=11,pad=13);ax.text(-.025,1.06,'a' if i==0 else 'b',transform=ax.transAxes,fontsize=12,fontweight='bold')
   # One quiet line under the panel replaces the coloured score boxes.
   ax.set_xlabel('Silhouette 0.007' if panel=='before' else 'Silhouette 0.107',fontsize=9,color='#7C818B',labelpad=9)
   checks.append(dict(variant=variant,panel=panel,n=len(a),Bad=int((a.label=='Bad').sum()),Good=int((a.label=='Good').sum()),xlim=list(map(float,ax.get_xlim())),ylim=list(map(float,ax.get_ylim()))))
  legend=[Line2D([],[],marker='o',ls='',markersize=5.5,color=bad,label='Inactive (Bad)'),Line2D([],[],marker='o',ls='',markersize=5.5,color=good,label='Active (Good)')]
  fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.018),ncol=2,frameon=False,fontsize=10,handletextpad=.35,columnspacing=2.4)
  fig.subplots_adjust(left=.055,right=.985,top=.87,bottom=.22,wspace=.17)
  soft.finish(fig);name='figure2_contrastive_before_after_'+variant
  for ext in ['png','pdf','svg']:fig.savefig(OUT/(name+'.'+ext),dpi=400,bbox_inches='tight',facecolor='white')
  plt.close(fig)
 manifest=dict(font='Aptos',palettes={'soft':'muted peach / mint','lavender':'lavender / mint'},coordinate_input_sha256=hashlib.sha256((ROOT/'tsne_pdf_marker_coordinates.csv').read_bytes()).hexdigest(),checks=checks,
  preserved='All archived PDF marker centres and classes; no t-SNE rerun or alteration of scatter geometry',
  displayed_after_silhouette=.107,source_variants='Attached/v5 raster prints .108; archived PDF prints .107; discrepancy explicit',
  figure_scope='Original classification visualisation, not QAC105 regression CV, OOD performance or biological causality')
 (ROOT/'tsne_style_validation.json').write_text(json.dumps(manifest,indent=2));print('Soft and lavender before/after figures saved in PDF/SVG/PNG.')
if __name__=='__main__':main()
