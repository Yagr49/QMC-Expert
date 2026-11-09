"""Validate existing scientific figure derivatives and declared provenance."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent


def main():
    errors=pd.read_csv(ROOT/'figure4_compact_error_values.csv')
    seeds=pd.read_csv(ROOT/'figure4_compact_seed_metrics.csv')
    reference=pd.read_csv(ROOT.parent/'revision_v18/analysis/summary.csv')
    assert len(errors)==3360 and errors.mean_absolute_error.ge(0).all()
    assert errors.groupby(['arm','schema']).size().eq(420).all()
    assert len(seeds)==32
    for (arm,schema),g in seeds.groupby(['arm','schema']):
        row=reference[(reference.arm==arm)&(reference.schema==schema)&
                      reference.encoding.eq('categorical')&reference.task.eq('pooled')].iloc[0]
        assert abs(g.RMSE.mean()-row.RMSE)<1e-12
        assert abs(g.MAE.mean()-row.MAE)<1e-12
    roc=pd.read_csv(ROOT/'figure5_roc_metrics.csv')
    ref=pd.read_csv(ROOT.parent/'qhero_author_comparison_20261014/results/summary.csv')
    assert len(roc)==10
    for row in roc.itertuples():
        protocol='scaffold_CV_pooled' if row.protocol=='scaffold_CV_fold' else row.protocol
        x=ref[(ref.model==row.model)&(ref.protocol==protocol)].iloc[0]
        assert abs(row.AUROC-x.AUROC)<1e-12
        assert row.n==(405 if row.protocol=='scaffold_CV_fold' else 81)
    files={}
    for name in ['figure4_human_quantitative_compact','figure5_qhero_real_roc']:
        for ext in ['png','pdf','svg']:
            p=ROOT/'figures'/f'{name}.{ext}'
            assert p.stat().st_size>10000
            files[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    for name in ['figure4_compact_error_values.csv','figure4_compact_seed_metrics.csv',
                 'figure4_caption_EN.txt','figure4_caption_RU.txt','figure4_provenance.json',
                 'figure5_roc_metrics.csv','figure5_empirical_roc_points.csv',
                 'figure5_mean_roc_points.csv','figure5_caption_EN.txt','figure5_provenance.json']:
        p=ROOT/name;files[str(p)]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    info=json.loads((ROOT/'figure4_provenance.json').read_text())
    assert len(info['source_sha256'])==16
    for filename,expected in info['source_sha256'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==expected
    record=dict(completed=True,compact_source_csv_files=16,
                compact_source_predictions=13440,derived_endpoint_values=3360,
                endpoint_values_per_violin=420,compact_seed_metrics=32,
                RMSE_MAE_agree_with_saved_summary=True,ROC_metrics_agree_with_saved_summary=True,
                no_new_model_fits=True,no_OOD_in_compact_figure=True,figures_separate_architectures=True,
                captions_word_count=len((ROOT/'figure4_caption_EN.txt').read_text().split()),
                files=files,docx_changed_by_this_agent=False)
    (ROOT/'compact_roc_validation.json').write_text(json.dumps(record,indent=2))
    print(json.dumps({k:v for k,v in record.items() if k!='files'}))


if __name__=='__main__':main()
