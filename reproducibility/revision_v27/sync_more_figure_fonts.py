"""Use theme_v27's font on the original grouped-violin and before/after layouts."""
from pathlib import Path
import hashlib, importlib.util, json, os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/coma_v27_more_fonts')
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib import font_manager
import theme_v27 as T

ROOT=Path(__file__).resolve().parent;REPRO=ROOT.parent;OUT=ROOT/'figures'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    family=T.theme()
    original_save=Figure.savefig
    outputs=[]
    def save_using_theme(self,fname,*args,**kwargs):
        # Apply the exact theme font while leaving existing colour, sizing and artists intact.
        T.theme()
        for ax in self.axes:
            labels=[label.get_text() for label in ax.get_xticklabels()]
            if any('→' in label for label in labels):
                ax.set_xticklabels([label.replace('→',T.ARROW) for label in labels])
            for axis in [ax.xaxis,ax.yaxis]:
                formatter=axis.get_major_formatter()
                if hasattr(formatter,'seq'):
                    formatter.seq=[str(label).replace('→',T.ARROW) for label in formatter.seq]
        for text in self.findobj(Text):
            size=text.get_fontsize()
            text.set_fontproperties(font_manager.FontProperties(fname=str(T.FONT_TTF),size=size))
            text.set_text(text.get_text().replace('log₂','log$_2$').replace('→',T.ARROW))
        path=Path(fname)
        if path.stem=='figure2_contrastive_enhanced':
            path=path.with_name('figure2_contrastive_futura'+path.suffix)
        self.canvas.draw()
        outputs.append(str(path))
        return original_save(self,path,*args,**kwargs)
    Figure.savefig=save_using_theme
    try:
        violin=module('grouped_violin',REPRO/'revision_v24/make_FT_violins.py')
        violin.OUT=OUT
        data_path=REPRO/'revision_v24/analysis/FT_route_endpoint_mean_absolute_errors.csv'
        data=pd.read_csv(data_path)
        checks=violin.plot(data,['cation','scaffold'],['Cation holdout','Scaffold holdout'],
            'figure3_backbone_route_error_violins_futura',width_mm=180)
        assert len(checks)==10 and all(c['n']==420 for c in checks)
        contrastive=module('contrastive_redraw',REPRO/'revision_v22/make_contrastive.py')
        contrastive.ROOT=ROOT;contrastive.OUT=OUT
        contrastive.main()
    finally:
        Figure.savefig=original_save
    record=json.loads((ROOT/'contrastive_validation.json').read_text())
    record['font']=family
    record['font_file']=str(T.FONT_TTF)
    record['font_source']='theme_v27.py'
    record['output_stem']='figure2_contrastive_futura'
    (ROOT/'contrastive_validation.json').write_text(json.dumps(record,indent=2))
    manifest=dict(completed=True,font=family,font_file=str(T.FONT_TTF),
        font_sha256=hashlib.sha256(T.FONT_TTF.read_bytes()).hexdigest(),
        shared_font_source='theme_v27.py',colours_and_layout_from_attached_reference_figures_preserved=True,
        grouped_violin_source=str(data_path),grouped_violin_sha256=hashlib.sha256(data_path.read_bytes()).hexdigest(),
        grouped_violin_summary=checks,tsne_points_per_panel=221,no_models_refitted=True,
        no_tsne_rerun=True,formats=['PDF','SVG','PNG600dpi'],
        output_sha256={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in outputs})
    (ROOT/'additional_font_sync_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Both attached figure layouts now use '+family+' from theme_v27.py.')

if __name__=='__main__':main()
