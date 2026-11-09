"""Plot theme from Main_Article3_revised and native ACS 1996 structures.

RDKit's ACS preset generates the molecular geometry/style. Its SVG paths are
placed unchanged into Matplotlib so atlas PDFs retain vector bonds and glyphs.
Panel layout applies only a uniform scale and translation to each depiction.
"""
import re
import xml.etree.ElementTree as E
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex, to_rgba
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.transforms import Affine2D
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

PALETTE={'human':'#9c7abb','continuous':'#75aaa2','binary':'#d99b7e','raw':'#92999e',
         'human_null':'#c5b5d6','continuous_null':'#b4d1cb','binary_null':'#e8c7b6',
         'blue':'#a5c4de','orange':'#eabb98','purple':'#c8b8e2','teal':'#9acabd'}
RECOLOR={
    **dict.fromkeys(['#8064a2','#805c8e','#7651a8','#77598e'],PALETTE['human']),
    **dict.fromkeys(['#2c8c83','#328c82','#32836b','#418b82'],PALETTE['continuous']),
    **dict.fromkeys(['#357bad','#427aa6','#d69a36'],PALETTE['binary']),
    **dict.fromkeys(['#b6a6c9','#b8a4cc'],PALETTE['human_null']),
    '#9ec9c4':PALETTE['continuous_null'],'#a2bdd3':PALETTE['binary_null'],
    '#748493':PALETTE['raw'],'#3b729d':PALETTE['blue'],'#d39b56':PALETTE['orange'],
}


def theme():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'axes.labelsize':11,'axes.titlesize':12,'axes.titleweight':'normal',
                         'axes.edgecolor':'#a6aaae','axes.linewidth':.7,
                         'axes.spines.top':True,'axes.spines.right':True,
                         'xtick.labelsize':9,'ytick.labelsize':9,
                         'grid.color':'#e1e3e5','grid.linewidth':.6,
                         'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
                         'pdf.fonttype':42,'svg.fonttype':'none'})


def recolor(value):
    try:
        color=to_hex(value)
        if color in RECOLOR:
            rgba=to_rgba(value)
            return to_rgba(RECOLOR[color],rgba[3])
    except (ValueError,TypeError):pass
    return value


def finish(fig):
    """Use the reference's light frames, soft colours and regular panel labels."""
    for ax in fig.axes:
        if not ax.axison:continue
        for spine in ax.spines.values():
            spine.set_visible(True);spine.set_color('#afb3b7');spine.set_linewidth(.7)
        ax.set_axisbelow(True)
        for title in [ax.title,ax._left_title,ax._right_title]:
            title.set_fontweight('normal')
            title.set_text(re.sub(r'^([A-Da-d])\s{2,}',lambda m:m[1].lower()+') ',title.get_text()))
        for line in ax.lines:line.set_color(recolor(line.get_color()))
        for collection in ax.collections:
            for getter,setter in [(collection.get_facecolors,collection.set_facecolors),
                                  (collection.get_edgecolors,collection.set_edgecolors)]:
                values=getter()
                if len(values):setter([recolor(v) for v in values])
        for patch in ax.patches:
            patch.set_facecolor(recolor(patch.get_facecolor()))
            patch.set_edgecolor(recolor(patch.get_edgecolor()))
        legend=ax.get_legend()
        if legend:
            legend.get_frame().set_facecolor('white');legend.get_frame().set_edgecolor('#d0d3d6')
    fig.set_facecolor('white')


def acs_svg(smiles):
    mol=Chem.MolFromSmiles(smiles)
    assert mol is not None
    rdDepictor.Compute2DCoords(mol)
    drawer=rdMolDraw2D.MolDraw2DSVG(-1,-1)
    drawer.drawOptions().fontFile='/System/Library/Fonts/Supplemental/Arial.ttf'
    rdMolDraw2D.DrawMoleculeACS1996(drawer,mol)
    drawer.FinishDrawing()
    svg=drawer.GetDrawingText()
    tree=E.fromstring(svg)
    width=float(tree.get('width').removesuffix('px')) if hasattr(str,'removesuffix') else float(tree.get('width')[:-2])
    height=float(tree.get('height').removesuffix('px')) if hasattr(str,'removesuffix') else float(tree.get('height')[:-2])
    return svg,tree,width,height


def svg_path(data):
    tokens=re.findall(r'[MLQCZmlqcz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',data)
    vertices=[];codes=[];i=0;command=None
    while i<len(tokens):
        if tokens[i].isalpha():command=tokens[i];i+=1
        assert command in ['M','L','Q','C','Z'],command
        if command=='Z':
            vertices.append(vertices[0]);codes.append(MplPath.CLOSEPOLY);command=None;continue
        count={'M':2,'L':2,'Q':4,'C':6}[command]
        values=list(map(float,tokens[i:i+count]));assert len(values)==count;i+=count
        pairs=list(zip(values[::2],values[1::2]));vertices.extend(pairs)
        codes.extend([{'M':MplPath.MOVETO,'L':MplPath.LINETO,'Q':MplPath.CURVE3,'C':MplPath.CURVE4}[command]]*len(pairs))
        if command=='M':command='L'
    return MplPath(vertices,codes)


def draw_acs(ax,record,canvas_width,canvas_height):
    svg,tree,width,height=record
    dx=(canvas_width-width)/2;dy=(canvas_height-height)/2
    transform=Affine2D().translate(dx,dy)+ax.transData
    ax.set_xlim(0,canvas_width);ax.set_ylim(canvas_height,0);ax.set_aspect('equal');ax.axis('off')
    for element in tree:
        tag=element.tag.split('}')[-1]
        if tag=='rect':continue  # white background, already supplied by the page
        assert tag=='path',tag
        style=dict(s.split(':',1) for s in element.get('style','').split(';') if ':' in s)
        # FreeType atom glyph paths carry fill attributes; bond paths carry styles.
        fill=style.get('fill',element.get('fill','black'))
        stroke=style.get('stroke',element.get('stroke','none'))
        patch=PathPatch(svg_path(element.get('d')),
                        facecolor='none' if fill=='none' else fill,
                        edgecolor='none' if stroke=='none' else stroke,
                        linewidth=float(style.get('stroke-width','0').replace('px','')),
                        transform=transform)
        # Convert the SVG stroke from depiction coordinates to rendered points.
        ax.add_patch(patch)
    return dx,dy


def fix_acs_strokes(fig,axes,canvas_width):
    fig.canvas.draw()
    for ax in axes:
        scale=ax.get_window_extent().width / fig.dpi * 72 / canvas_width
        for patch in ax.patches:
            patch.set_linewidth(patch.get_linewidth()*scale)
            patch.set_joinstyle('round');patch.set_capstyle('round')
