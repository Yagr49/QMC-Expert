"""Expose the original QAC cohort and the fixed, named OOD molecules.

No training or target selection is performed. All predictions are immutable v12
outputs; original compound codes are joined by canonical full-salt identity.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/coma_v13_matplotlib')
import hashlib, json, warnings, copy
import xml.etree.ElementTree as E
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, Descriptors, Draw
from scipy.stats import spearmanr
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import drawing_style as style
RDLogger.DisableLog('rdApp.*')
warnings.filterwarnings('ignore', message='Data Validation extension')

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'revision_v12'
COMA = ROOT.parents[1]
DESKTOP = COMA.parent
ARMS = ['expert', 'quant-continuous', 'quant-binary', 'expert-shuffled', 'raw-molformer']
LABELS = {'expert': 'Human', 'quant-continuous': 'Continuous MIC',
          'quant-binary': 'Binary MIC', 'expert-shuffled': 'Shuffled human', 'raw-molformer': 'Raw'}
COLORS = {'expert': '#7651a8', 'quant-continuous': '#32836b', 'quant-binary': '#d69a36',
          'expert-shuffled': '#b8a4cc', 'raw-molformer': '#748493'}


def canonical(s):
    return Chem.MolToSmiles(Chem.MolFromSmiles(str(s)))


def fingerprints(smiles):
    return [AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(s), 2, nBits=2048)
            for s in smiles]


def save(fig, name):
    style.finish(fig)
    for ext in ['pdf', 'png', 'svg']:
        fig.savefig(ROOT / 'figures' / (name + '.' + ext), dpi=220, bbox_inches='tight')
    plt.close(fig)


def atlas(df, name, legends, per_page=6):
    """ACS 1996 glyphs and bonds are vector paths in SVG and print PDF."""
    records = [style.acs_svg(s) for s in df.can]
    individual = ROOT/'figures/molecules_ACS1996';individual.mkdir(exist_ok=True)
    ids=df.code if 'code' in df else df.compound_id
    for identity,record in zip(ids,records):
        (individual/(str(identity)+'.svg')).write_text(record[0])
    columns=2 if name.startswith('figureS20') else 3
    canvas_width=max(r[2] for r in records)+20
    canvas_height=max(r[3] for r in records)+20
    # Atlas SVG preserves the same native ACS bond/font scale for every molecule.
    svg_ns='http://www.w3.org/2000/svg'
    rows=(len(records)+columns-1)//columns
    cell_height=canvas_height+50
    svgroot=E.Element('{'+svg_ns+'}svg',width=str(canvas_width*columns),height=str(cell_height*rows),
                      viewBox=f'0 0 {canvas_width*columns} {cell_height*rows}')
    for j,(record,legend) in enumerate(zip(records,legends)):
        _,tree,width,height=record
        x=(j%columns)*canvas_width;y=(j//columns)*cell_height
        group=E.SubElement(svgroot,'{'+svg_ns+'}g',transform=f'translate({x+(canvas_width-width)/2},{y+40+(canvas_height-height)/2})')
        for child in tree:group.append(copy.deepcopy(child))
        for line,text in enumerate(legend.split('\n')):
            element=E.SubElement(svgroot,'{'+svg_ns+'}text',x=str(x+canvas_width/2),y=str(y+13+line*14),
                                 attrib={'text-anchor':'middle','font-family':'Arial, sans-serif','font-size':'11','fill':'black'})
            element.text=text
    (ROOT / 'figures' / (name + '.svg')).write_text(E.tostring(svgroot,encoding='unicode'))
    pngs = []
    with PdfPages(ROOT / 'figures' / (name + '.pdf')) as pdf:
        for start in range(0, len(df), per_page):
            nrows = (per_page + columns-1) // columns
            fig, axes = plt.subplots(nrows, columns, figsize=(11.7, nrows * 3.8), squeeze=False)
            for j, ax in enumerate(axes.ravel()):
                ax.axis('off')
                if start+j < len(df):
                    style.draw_acs(ax,records[start+j],canvas_width,canvas_height)
                    ax.set_title(legends[start+j], fontsize=9, pad=8)
            fig.suptitle(('Fixed OOD-17 compounds' if name.startswith('figureS20') else
                          'Original QAC-105 structure registry') +
                         ' · page ' + str(start // per_page + 1), fontsize=14)
            fig.tight_layout(rect=(0, 0, 1, .95))
            style.fix_acs_strokes(fig,axes.ravel(),canvas_width)
            pdf.savefig(fig)
            if name.startswith('figureS20'):
                path = ROOT / 'figures' / (name + '_page' + str(start // per_page + 1) + '.png')
                fig.savefig(path, dpi=220, bbox_inches='tight')
                pngs.append(path.name)
            plt.close(fig)
    return pngs


def main():
    for folder in ['data', 'analysis', 'figures']:
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    inputs = {
        'original_prepared': DESKTOP/'Veresh_paper_Mendeley/outputs/prepared_qac_target.csv',
        'original_raw': DESKTOP/'Veresh_paper_Mendeley/Data_biocides.xlsx',
        'ood_codes': DESKTOP/'Veresh_paper/QACs_SMILES_MIC_MBC.xlsx',
        'archived_QAC105': ROOT.parent/'finetune/data/eval_QAC-105.csv',
        'strict_QAC104': OLD/'data/target_QAC-104.csv',
        'strict_OOD17': OLD/'data/target_OOD-17.csv',
        'source_expert': OLD/'data/matched-pooled_expert.csv',
        'source_quant': OLD/'data/matched-pooled_quant.csv',
        'source_split': OLD/'results/source_split.csv',
        'folds': OLD/'data/target_folds.csv',
        'predictions': OLD/'results/predictions.csv',
        'direct_predictions': OLD/'results/direct_predictions.csv',
        'summary': OLD/'analysis/summary.csv',
        'direct_summary': OLD/'analysis/direct_summary.csv',
    }
    qac = pd.read_csv(inputs['strict_QAC104'])
    ood = pd.read_csv(inputs['strict_OOD17'])
    expert = pd.read_csv(inputs['source_expert'])
    quant = pd.read_csv(inputs['source_quant'])
    for col in ['can', 'cation', 'scaffold']:
        assert expert[col].tolist() == quant[col].tolist()
    split = pd.read_csv(inputs['source_split'])
    folds = pd.read_csv(inputs['folds'])
    pred = pd.read_csv(inputs['predictions'])
    direct = pd.read_csv(inputs['direct_predictions'])
    summary = pd.read_csv(inputs['summary'])
    dsummary = pd.read_csv(inputs['direct_summary'])

    original = pd.read_csv(inputs['original_prepared'])
    original['can'] = original.canonical_full_smiles.map(canonical)
    archived = pd.read_csv(inputs['archived_QAC105'])
    assert len(original) == 105 and set(original.can) == set(archived.can)
    assert np.allclose(original.set_index('can').loc[archived.can, 'log2_sa_mic_um'], archived.y)
    raw = pd.read_excel(inputs['original_raw'])
    raw['_can'] = raw.iloc[:, 1].map(canonical)
    rowids = raw.groupby('_can')[raw.columns[0]].apply(lambda v: ';'.join(str(int(x)) for x in v))
    original['original_row_ids'] = original.can.map(rowids)
    original['included_in_matched_QAC104'] = original.can.isin(qac.can)
    original['status'] = np.where(original.included_in_matched_QAC104, 'retained',
                                  'excluded: conflicting duplicate endpoints')
    original['target_fold'] = original.can.map(folds[folds.target=='QAC-104'].set_index('can').fold)
    excluded = original[~original.included_in_matched_QAC104]
    assert len(excluded) == 1 and excluded.label_conflict.astype(bool).all()
    assert set(qac.can) == set(original.loc[~original.label_conflict.astype(bool), 'can'])
    original.to_csv(ROOT/'data/original_QAC105_registry.csv', index=False)
    raw.loc[raw._can.isin(excluded.can)].to_csv(ROOT/'data/QAC_excluded_duplicate_records.csv', index=False)

    codes = pd.read_excel(inputs['ood_codes'], sheet_name='Лист1')
    codes['can'] = codes.SMILES.map(canonical)
    assert len(codes) == 17 and codes.can.is_unique and set(codes.can)==set(ood.can)
    names = codes.set_index('can').Code.astype(str)
    ood['code'] = ood.can.map(names)
    ood['measured_MIC_mg_L'] = ood.can.map(codes.set_index('can')['MIC Sa']).astype(float)
    ood['RDKit_salt_MW'] = ood.can.map(lambda s: Descriptors.MolWt(Chem.MolFromSmiles(s)))
    ood['measured_MIC_uM'] = 1000*ood.measured_MIC_mg_L/ood.RDKit_salt_MW
    assert np.allclose(np.log2(ood.measured_MIC_uM), ood.y, rtol=0, atol=1e-12)
    groups = {s: 'G'+str(i+1) for i, s in enumerate(ood.scaffold.drop_duplicates())}
    ood['scaffold_group'] = ood.scaffold.map(groups)
    ood['cation_charge'] = ood.cation.map(lambda s: Chem.GetFormalCharge(Chem.MolFromSmiles(s)))
    ood['source_cation_overlap'] = ood.cation.isin(expert.cation)
    ood['QAC_cation_overlap'] = ood.cation.isin(qac.cation)
    ood['source_scaffold_overlap'] = ood.scaffold.isin(expert.scaffold)
    ood['QAC_scaffold_overlap'] = ood.scaffold.isin(qac.scaffold)
    overlap_cols = [c for c in ood if c.endswith('_overlap')]
    assert not ood[overlap_cols].any().any()
    assert not set(qac.cation) & set(expert.cation)
    assert not set(qac.cation) & set(quant.cation)
    assert not set(ood.cation) & set(quant.cation)
    assert not set(qac.scaffold) & set(ood.scaffold)
    # Chemical similarity is descriptive and does not redefine the fixed OOD set.
    query = fingerprints(ood.cation)
    references = [('QAC104', qac), ('source_train', expert[expert.can.isin(split[split.partition=='train'].can)]),
                  ('source_all681', expert)]
    for prefix, frame in references:
        fps = fingerprints(frame.cation)
        sims = np.array([DataStructs.BulkTanimotoSimilarity(fp, fps) for fp in query])
        nearest = sims.argmax(axis=1)
        ood[prefix+'_nearest_cation_SMILES'] = frame.iloc[nearest].cation.values
        ood[prefix+'_max_Morgan2_2048_Tanimoto'] = sims.max(axis=1)
        if prefix=='QAC104': ood['nearest_QAC_compound_id'] = frame.iloc[nearest].compound_id.values
    ood.to_csv(ROOT/'data/OOD17_named_registry.csv', index=False)

    audits = []
    for target, expected in [('QAC-104', qac), ('OOD-17', ood)]:
        for frame, score, summary_frame in [(pred, 'pred', summary), (direct, 'rank_score', dsummary)]:
            t = frame[frame.target==target]
            for (arm, seed), group in t.groupby(['arm', 'seed']):
                assert group.can.is_unique and set(group.can)==set(expected.can)
                assert np.allclose(group.y, expected.set_index('can').loc[group.can, 'y'])
            for arm, group in t.groupby('arm'):
                seeds = sorted(group.seed.unique().tolist())
                assert seeds==([0] if arm=='raw-molformer' else list(range(5)))
                values = []
                for seed, g in group.groupby('seed'):
                    if score=='pred': values.append((r2_score(g.y,g.pred), mean_squared_error(g.y,g.pred)**.5))
                    else: values.append((spearmanr(g.y,g.rank_score).statistic,))
                reference = summary_frame[(summary_frame.target==target)&(summary_frame.arm==arm)].iloc[0]
                actual = np.mean(values,axis=0)
                expected_metrics = [reference.R2,reference.RMSE] if score=='pred' else [reference.rank_agreement]
                error = float(np.max(np.abs(actual-expected_metrics)))
                assert error < 1e-12
                audits.append(dict(target=target,arm=arm,type=score,n=len(expected),seeds=seeds,max_metric_error=error))

    p = pred[pred.target=='OOD-17'].copy()
    p['code'] = p.can.map(names)
    p.to_csv(ROOT/'analysis/OOD17_predictions_all_seeds.csv', index=False)
    q = pred[pred.target=='QAC-104'].merge(original[['can','compound_id','original_row_ids','target_fold']],on='can',validate='many_to_one')
    q.to_csv(ROOT/'analysis/QAC104_predictions_all_seeds.csv', index=False)
    dp = direct[direct.target=='OOD-17'].copy();dp['code']=dp.can.map(names)
    dp['score_unit'] = np.where(dp.arm.str.contains('continuous')|dp.arm.eq('quant-shuffled'),
                               'direct predicted log2 MIC (uM)', 'binary source-head logit; not MIC')
    dp.to_csv(ROOT/'analysis/OOD17_direct_scores_all_seeds.csv',index=False)
    wide = ood[['code','scaffold_group','measured_MIC_mg_L','measured_MIC_uM','y','can']].copy()
    for arm, g in p.groupby('arm'):
        agg=g.groupby('can').pred.agg(['mean','std','count'])
        wide[arm+'_predicted_log2_uM_mean']=wide.can.map(agg['mean'])
        wide[arm+'_predicted_log2_uM_seed_SD']=wide.can.map(agg['std'])
        wide[arm+'_prediction_seeds']=wide.can.map(agg['count'])
        wide[arm+'_geometric_predicted_MIC_uM']=2**wide[arm+'_predicted_log2_uM_mean']
        wide[arm+'_mean_absolute_error_log2_uM']=wide.can.map(g.assign(ae=(g.pred-g.y).abs()).groupby('can').ae.mean())
    for arm,g in dp.groupby('arm'):
        agg=g.groupby('can').score.agg(['mean','std'])
        wide[arm+'_direct_score_mean']=wide.can.map(agg['mean'])
        wide[arm+'_direct_score_seed_SD']=wide.can.map(agg['std'])
    wide.to_csv(ROOT/'analysis/OOD17_per_molecule.csv',index=False)
    pd.concat([summary[summary.target.isin(['QAC-104','OOD-17'])].assign(outcome='target_regression'),
               dsummary[dsummary.target.isin(['QAC-104','OOD-17'])].assign(outcome='direct_source_head')]).to_csv(
                   ROOT/'analysis/cohort_summary.csv',index=False)

    style.theme()
    fig, axes=plt.subplots(2,2,figsize=(12,8.1),constrained_layout=True)
    for col,target in enumerate(['QAC-104','OOD-17']):
        for row in [0,1]:
            ax=axes[row,col];sf=summary if row==0 else dsummary
            arms=ARMS if row==0 else ARMS[:-1]
            for i,arm in enumerate(arms):
                s=sf[(sf.target==target)&(sf.arm==arm)].iloc[0]
                metric='RMSE' if row==0 else 'rank_agreement'
                sd='RMSE_sd' if row==0 else 'rank_sd'
                g=(pred if row==0 else direct).query('target==@target and arm==@arm')
                vv=[mean_squared_error(z.y,z.pred)**.5 if row==0 else spearmanr(z.y,z.rank_score).statistic
                    for _,z in g.groupby('seed')]
                ax.scatter(i+np.linspace(-.10,.10,len(vv)),vv,s=24,color=COLORS[arm],alpha=.6,zorder=3)
                ax.errorbar(i,s[metric],yerr=s[sd] if np.isfinite(s[sd]) else None,
                            fmt='D',color=COLORS[arm],capsize=4,markersize=6,zorder=4)
            ax.set_xticks(range(len(arms)));ax.set_xticklabels([LABELS[a] for a in arms],rotation=22,ha='right')
            ax.set_ylabel('RMSE (log2 µM)' if row==0 else 'Direct Spearman rank agreement')
            ax.set_title(('QAC-104 · original cohort'+(', scaffold CV' if row==0 else '') if col==0 else
                          'OOD-17 · fixed named compounds')+('\nQAC-trained MIC decoder' if row==0 and col==1 else
                                                                   '\nSource head; no target fitting' if row==1 else ''))
            ax.text(-.13,1.06,['a','b','c','d'][row*2+col],transform=ax.transAxes,fontweight='bold',fontsize=16)
            ax.grid(axis='y',alpha=.17)
            if row==0:ax.set_ylim(1.45,2.25)
            else:ax.set_ylim(-.43,.93);ax.axhline(0,color='#666666',lw=.8)
    save(fig,'figure6_original_QAC_and_OOD')

    fig,axes=plt.subplots(2,1,figsize=(12,9.2),constrained_layout=True)
    ax=axes[0];xx=np.arange(17)
    ax.scatter(xx,wide.y,color='#20252a',marker='x',s=55,label='Measured',zorder=4)
    for offset,arm in [(-.18,'expert'),(0,'quant-continuous'),(.18,'raw-molformer')]:
        ax.errorbar(xx+offset,wide[arm+'_predicted_log2_uM_mean'],
                    yerr=None if arm=='raw-molformer' else wide[arm+'_predicted_log2_uM_seed_SD'],
                    fmt='o',ms=4,capsize=2,color=COLORS[arm],label=LABELS[arm])
    ax.set_xticks(xx);ax.set_xticklabels(wide.code,rotation=40,ha='right');ax.set_ylabel('log2 MIC (µM)')
    ax.set_title('a  Per-compound MIC predictions · decoder fitted on QAC-104 only',loc='left',fontweight='bold')
    ax.legend(ncol=4,frameon=False);ax.grid(axis='y',alpha=.15)
    ax=axes[1]
    palette=['#4477aa','#228833','#cc6677','#aa3377']
    for group,g in wide.groupby('scaffold_group',sort=False):
        ax.errorbar(g.expert_direct_score_mean,g.y,xerr=g.expert_direct_score_seed_SD,
                    fmt='o',color=palette[int(group[1:])-1],capsize=2,label=group)
        offsets={'IT499':(-14,24), 'SEV-035':(-20,-17), 'SEV-0338':(18,12)}
        for _,r in g.iterrows():ax.annotate(r.code,(r.expert_direct_score_mean,r.y),
                                          xytext=offsets.get(r.code,(4,4)),
                                          textcoords='offset points',fontsize=8)
    ax.set_xlabel('Direct human source-head logit (larger = Good; no MIC calibration)')
    ax.set_ylabel('Measured log2 MIC (µM)')
    ax.set_title('b  Human source-only ranking · mean seed-specific ρ = 0.667 ± 0.120',loc='left',fontweight='bold')
    ax.legend(title='Cation-scaffold group',frameon=False);ax.grid(alpha=.15)
    save(fig,'figureS19_OOD17_per_molecule')
    atlas_pages=atlas(ood,'figureS20_OOD17_structures',
                      [f'{r.code} · {r.scaffold_group} · charge +{r.cation_charge}\nMIC {r.measured_MIC_mg_L:g} mg/L = {r.measured_MIC_uM:.3g} µM'
                       for r in ood.itertuples()])
    atlas(original,'original_QAC105_structures',
          [f'Rows {r.original_row_ids} · {r.compound_id}\nMIC {r.sa_mic_um:.3g} µM · '+
           ('retained' if r.included_in_matched_QAC104 else 'EXCLUDED: conflicting duplicates')
           for r in original.itertuples()],per_page=12)
    report = dict(original_raw_records=len(raw),original_unique_structures=len(original),
                  retained_QAC104=len(qac),excluded=[dict(compound_id=r.compound_id, original_row_ids=r.original_row_ids,
                                                        conflict_columns=r.conflict_columns) for r in excluded.itertuples()],
                  QAC_cations=int(qac.cation.nunique()),QAC_scaffolds=int(qac.scaffold.nunique()),
                  OOD_codes=ood.code.tolist(),OOD_cations=int(ood.cation.nunique()),OOD_scaffolds=int(ood.scaffold.nunique()),
                  OOD_overlap_counts={c:int(ood[c].sum()) for c in overlap_cols},
                  score_audits=audits,OOD_atlas_pngs=atlas_pages,
                  inputs={k:dict(path=str(v),sha256=hashlib.sha256(v.read_bytes()).hexdigest()) for k,v in inputs.items()},
                  source_predictions_unchanged=True,training_performed=False,
                  molecular_drawing='RDKit MolToACS1996SVG; vector bonds and atom glyphs in SVG/PDF; uniform panel layout scale.',
                  style_reference='/Users/egorilin/Downloads/Telegram Desktop/Main_Article3_revised.docx',
                  uncertainty='Source-seed SD only; not assay uncertainty or per-molecule prediction intervals.')
    (ROOT/'cohort_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['inputs','score_audits']},indent=2))


if __name__=='__main__':main()
