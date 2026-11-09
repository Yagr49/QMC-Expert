"""Re-typeset the archived correlation grid using theme_v27, retaining raster plot content.

Native axes/text surround each untouched raster plot interior. Historical point
coordinates, regression lines and printed metrics are preserved, not reconstructed
from approximate marker extraction or substituted from a different experiment.
"""
from pathlib import Path
import hashlib, json, os, sys
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v27_correlation_font')
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0,str(Path(__file__).resolve().parent))
import theme_v27 as T

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'scatter_grid_desc_vs_emb_modified.png'
OUT=ROOT/'figures'
XCOL=[(201,1771),(1986,3556),(3771,5341)]
YROW=[(30,1615),(1807,3392)]
STATS=[[(.476,1.58,1.18),(.559,1.55,1.14),(.616,1.45,1.06)],
       [(.384,1.48,1.09),(.719,1.06,.84),(.767,.97,.73)]]

def grid_centres(counts):
    ids=np.flatnonzero(counts>1100)
    groups=np.split(ids,np.flatnonzero(np.diff(ids)>1)+1)
    return np.array([group.mean() for group in groups])

def affine(pixels,values):
    return np.linalg.lstsq(np.column_stack([pixels,np.ones(len(pixels))]),values,rcond=None)[0]

def main():
    family=T.theme(base=8)
    source=np.asarray(Image.open(SOURCE).convert('RGB'))
    assert source.shape==(3570,5370,3)
    fig,axes=plt.subplots(2,3,figsize=(180/25.4,136/25.4))
    fig.subplots_adjust(left=.104,right=.985,bottom=.09,top=.86,wspace=.26,hspace=.25)
    checks=[]
    for r,(y0,y1) in enumerate(YROW):
        for c,(x0,x1) in enumerate(XCOL):
            ax=axes[r,c]
            interior=source[y0+3:y1-2,x0+3:x1-2].copy()
            rgb=interior.astype(int)
            grid=(rgb.min(2)>=226)&(rgb.max(2)<=244)&((rgb.max(2)-rgb.min(2))<=2)
            xp=grid_centres(grid.sum(0));yp=grid_centres(grid.sum(1))
            xvalues=np.array([-2,0,2,4,6,8] if (r,c)==(1,0) else
                             [-2,0,2,4,6] if r==1 else [0,2,4,6,8])
            yvalues=np.array([8,6,4,2,0,-2] if (r,c)==(1,0) else
                             [6,4,2,0,-2] if r==1 else [8,6,4,2,0])
            assert len(xp)==len(xvalues) and len(yp)==len(yvalues)
            mx,cx=affine(xp,xvalues);my,cy=affine(yp,yvalues)
            height,width=interior.shape[:2]
            extent=[cx,mx*width+cx,my*height+cy,cy]
            image=ax.imshow(interior,extent=extent,origin='upper',interpolation='none',aspect='auto',zorder=1)
            assert np.array_equal(np.asarray(image.get_array()),interior)
            # The old metric text is the only raster area covered with native text.
            # Confirm this rectangle contains no blue data markers before covering it.
            top_left=rgb[:270,:430]
            blue=np.abs(top_left-np.array([0x62,0x9f,0xca])).sum(2)<90
            assert not blue.any(),(r,c,'metric region contains data markers')
            ax.add_patch(Rectangle((cx,cy+my*270),mx*430,-my*270,
                facecolor='white',edgecolor='none',zorder=2))
            score,rmse,mae=STATS[r][c]
            ax.text(.035,.967,'R² = %.3f\nRMSE = %.2f\nMAE = %.2f'%(score,rmse,mae),
                transform=ax.transAxes,ha='left',va='top',fontsize=6.4,color=T.INK,
                bbox=dict(boxstyle='round,pad=.25',facecolor='white',edgecolor=T.RULE,lw=.55),zorder=3)
            ax.set_xticks(xvalues);ax.set_yticks(yvalues[::-1]);ax.grid(False)
            ax.set_xlim(extent[0],extent[1]);ax.set_ylim(extent[2],extent[3])
            ax.set_xlabel('Experimental log$_2$(MIC/MBC)',fontsize=6.7,labelpad=3)
            ax.set_ylabel('Predicted log$_2$(MIC/MBC)',fontsize=6.7,labelpad=2)
            ax.tick_params(labelsize=5.9,pad=2)
            for spine in ax.spines.values():spine.set_visible(True);spine.set_linewidth(.55);spine.set_color(T.RULE)
            if r==0:
                ax.set_title(['No labels','One-hot encoded\nlabels','OpenAI embeddings\nlabels'][c],
                    fontsize=10,pad=14,color=T.INK)
            checks.append(dict(row=r,column=c,raster_region=[x0+3,y0+3,x1-2,y1-2],
                raster_region_sha256=hashlib.sha256(interior.tobytes()).hexdigest(),
                all_plot_pixels_preserved=True,metric_overlay_has_zero_data_markers=True,
                R2=score,RMSE=rmse,MAE=mae))
    fig.text(.017,.688,'Descriptors',rotation=90,ha='center',va='center',fontsize=10.4,color=T.INK)
    fig.text(.017,.29,'Embeddings',rotation=90,ha='center',va='center',fontsize=10.4,color=T.INK)
    T.save(fig,OUT,'figure4_correlations_futura')
    record=dict(completed=True,font=family,font_source='theme_v27.py',source=str(SOURCE),
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),panels=checks,
        method='Native Futura axes/text around unchanged archived raster plot interiors',
        no_marker_digitisation=True,no_predictions_recomputed=True,
        historical_metrics_preserved=True,formats=['PNG600dpi','PDF','SVG'])
    (ROOT/'figure4_font_sync_manifest.json').write_text(json.dumps(record,indent=2))
    print('Correlation grid: Futura from theme_v27; all six archived plot interiors preserved.')

if __name__=='__main__':main()
