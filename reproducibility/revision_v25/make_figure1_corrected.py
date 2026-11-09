"""Native publication diagram with checked label counts and archived point-score ranges."""
from pathlib import Path
import importlib.util, json, os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v25_fig1')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
soft=module('soft',ROOT.parent/'revision_v17/make_soft_figures.py');soft.theme()
acs=module('acs',ROOT.parent/'revision_v14/drawing_style.py')

def box(ax,x,y,w,h,value,color,fs=8.5):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.006,rounding_size=.012',
        facecolor=color,edgecolor='#B9BEC6',lw=.7))
    ax.text(x+w/2,y+h/2,value,ha='center',va='center',fontsize=fs,linespacing=1.3)
def arrow(ax,a,z,dashed=False):
    ax.annotate('',xy=z,xytext=a,arrowprops=dict(arrowstyle='-|>',color='#929AA4',lw=.9,
        mutation_scale=8,linestyle='--' if dashed else '-'))
def molecule():
    smiles='[Br-].[Br-].*[n+]1ccc(Cc2ccc(Cc3cc[n+](*)cc3)cc2)cc1'
    mol=Chem.MolFromSmiles(smiles);assert mol is not None
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum()==0:atom.SetProp('dummyLabel','R')
    rdDepictor.Compute2DCoords(mol)
    drawer=rdMolDraw2D.MolDraw2DSVG(-1,-1)
    drawer.drawOptions().fontFile='/System/Library/Fonts/Supplemental/Arial.ttf'
    rdMolDraw2D.DrawMoleculeACS1996(drawer,mol);drawer.FinishDrawing()
    from xml.etree import ElementTree as E
    svg=drawer.GetDrawingText();tree=E.fromstring(svg)
    return smiles,(svg,tree,float(tree.get('width')[:-2]),float(tree.get('height')[:-2]))

def main():
    fig,ax=plt.subplots(figsize=(180/25.4,125/25.4))
    fig.subplots_adjust(left=.03,right=.98,bottom=.02,top=.98)
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_axis_off()
    colors=['#A8C5DF','#9ED2C1','#E6B79F','#C8BCE5','#DDB7CC']
    ax.text(.01,.98,'The expert guidance pipeline',fontsize=11,va='top')
    rng=np.random.RandomState(52)
    for i,(x,y) in enumerate(rng.uniform([.065,.76],[.17,.90],(23,2))):
        ax.scatter(x,y,s=9,color=colors[i%5],lw=0)
    ax.add_patch(Circle((.37,.856),.024,fc='none',ec='#BA986D',lw=.9))
    ax.add_patch(Arc((.37,.78),.09,.10,theta1=0,theta2=180,color='#BA986D',lw=.9))
    for row in range(5):
        ax.scatter(np.linspace(.58,.65,5),np.repeat(.90-row*.026,5),s=9,color=colors[row],lw=0)
    # The unnumbered curve is explicitly conceptual, not measured model performance.
    ax.plot([.80,.94],[.765,.765],color='#CBD0D7',lw=.6)
    ax.plot([.80,.80],[.765,.90],color='#CBD0D7',lw=.6)
    ax.plot([.805,.84,.875,.91,.935],[.775,.795,.84,.868,.892],color='#8CBCAA',lw=1.2)
    ax.plot([.805,.84,.875,.91,.935],[.775,.783,.789,.799,.805],color='#DDB7CC',lw=.9,ls='--')
    ax.text(.87,.925,'Schematic',fontsize=7,color='#7C838D',ha='center')
    for x,label in [(.12,'Raw information'),(.37,'Expert guidance'),(.615,'Guided representation'),(.87,'Prediction')]:
        ax.text(x,.72,label,ha='center',fontsize=8)
    for a,z in [((.20,.832),(.31,.832)),((.43,.832),(.545,.832)),((.68,.832),(.765,.832))]:arrow(ax,a,z)
    ax.text(.01,.635,'A) Earlier descriptor-based workflow',fontsize=10)
    box(ax,.345,.455,.125,.13,'Feature\nselection','#ECF2F8')
    box(ax,.515,.455,.135,.13,'Stacking\nmodels','#E8F3ED')
    box(ax,.70,.438,.285,.164,'MIC / MBC · S. aureus / E. coli\nDescriptor MLP: R² 0.25–0.68\nStacking: R² 0.30–0.43','#F1EDF8',7.8)
    for a,z in [((.285,.52),(.334,.52)),((.479,.52),(.505,.52)),((.659,.52),(.69,.52))]:arrow(ax,a,z)
    ax.text(.01,.355,'B) Our human-guided workflow',fontsize=10)
    box(ax,.335,.135,.115,.125,'Frozen\nMolFormer','#ECF2F8')
    box(ax,.485,.135,.155,.125,'Compact\nencoder','#E8F3ED')
    box(ax,.675,.135,.11,.125,'CatBoost','#F7E8DC')
    box(ax,.825,.126,.16,.145,'MIC / MBC\nHuman + text\nR² 0.59–0.77','#F1EDF8',8)
    ax.text(.562,.305,'1,103 final expert labels',ha='center',fontsize=8.3)
    arrow(ax,(.562,.291),(.562,.271),True)
    ax.text(.562,.092,'768 → 512 → 384 → 256',ha='center',fontsize=7.5,color='#737B85')
    ax.text(.73,.092,'+ task code',ha='center',fontsize=7.5,color='#737B85')
    for a,z in [((.285,.197),(.324,.197)),((.459,.197),(.474,.197)),((.649,.197),(.664,.197)),((.794,.197),(.814,.197))]:arrow(ax,a,z)
    smiles,record=molecule();molaxes=[]
    for bottom in [.407,.099]:
        ma=fig.add_axes([.035,bottom,.263,.17]);molaxes.append(ma)
        acs.draw_acs(ma,record,record[2]+8,record[3]+8)
    acs.fix_acs_strokes(fig,molaxes,record[2]+8)
    for ext in ['png','pdf','svg']:fig.savefig(OUT/('figure1_verified_workflow.'+ext),dpi=600,facecolor='white')
    plt.close(fig)
    caption=('Figure 1. Conceptual expert-guidance pipeline and reference prediction workflows. '
        'The archive contains 1,103 final Good/Bad labels; the earlier collection-stage '
        'count of 1,500 remains subject to coauthor confirmation. Panel A distinguishes '
        'the descriptor-MLP reference range (R² 0.25–0.68, four endpoints) from stacking '
        '(R² 0.30–0.43, the three reported endpoints). Panel B uses recovered human/text '
        'holdout scores across four endpoints (R² 0.5918–0.7708, shown as 0.59–0.77). '
        'These are historical point-score ranges from Table S45, not CV uncertainty or '
        'a paired estimate from the new matched experiments. The upper curves are schematic. '
        'Representative bis-QAC scaffolds are drawn using ACS1996 styling; R denotes an '
        'unspecified substituent.')
    (ROOT/'figure1_caption_EN.txt').write_text(caption+'\n')
    (ROOT/'figure1_numeric_provenance.json').write_text(json.dumps(dict(
        expert_final_labels=1103,collection_stage_reported_1500_not_used_as_final_count=True,
        descriptor_MLP_R2=[.68,.25,.32,.40],stacking_R2=[.30,.43,.41],
        human_text_recovered_R2=[.7494,.6752,.5918,.7708],
        displayed_human_range=[.59,.77],unknown_original_range_053_086_removed=True,
        scores_historical_holdout_not_CV=True,upper_curves_schematic=True,
        molecule_generic_not_dataset_specific=smiles,molecule_style='RDKit ACS1996',font='Aptos'),indent=2))
    print('Figure1: verified 1103 labels and source-specific R2 ranges; ACS1996 vector structures.')

if __name__=='__main__':main()
