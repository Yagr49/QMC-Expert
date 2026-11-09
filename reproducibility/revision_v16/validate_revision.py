"""Validate document preservation and correspondence to held-out predictions."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import xml.etree.ElementTree as E
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parents[1]
spec = importlib.util.spec_from_file_location('v16_builder', ROOT/'build_revision.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
spec = importlib.util.spec_from_file_location('doc_inspector', ROOT.parent/'revision_v12/validate_documents.py')
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)


def rows(table):
    return [[b.h.text(c) for c in row.findall('w:tc',b.NS)] for row in table.findall('w:tr',b.NS)]


def fields(body):
    return [E.tostring(p) for p in body if b.h.text(p).startswith('[COAUTHORS')]


def check_prediction_metrics(branch):
    predictions = pd.read_csv(b.ANALYSIS/(branch+'_predictions.csv'))
    metrics = pd.read_csv(b.ANALYSIS/(branch+'_metrics.csv'))
    category = 'mode' if branch == 'direct' else 'variant'
    configuration_keys = ['arm',category,'seed','schema']
    metric_count = 0
    for key, g in predictions.groupby(configuration_keys):
        assert len(g) == (68 if key[-1] == 'full-QAC105' else 420)
        assert g.compound_id.nunique() == (17 if key[-1] == 'full-QAC105' else 105)
        assert (g.qualifier == '=').sum() == (67 if key[-1] == 'full-QAC105' else 420)
        assert not g.duplicated(['compound_id','task']).any()
        mask = np.ones(len(metrics),dtype=bool)
        for name, value in zip(configuration_keys,key):
            mask &= metrics[name].to_numpy() == value
        scores = metrics[mask].set_index('task')
        assert set(scores.index) == {'pooled','Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC'}
        for task, score in scores.iterrows():
            subset = g[g.qualifier == '=']
            if task != 'pooled':
                subset = subset[subset.task == task]
            residual = subset.prediction.to_numpy() - subset.y.to_numpy()
            assert score.n == len(residual)
            assert abs(score.RMSE - np.sqrt(np.dot(residual,residual)/len(residual))) < 1e-12
            assert abs(score.MAE - np.abs(residual).sum()/len(residual)) < 1e-12
            if task == 'pooled':
                assert pd.isna(score.R2)
            else:
                y = subset.y.to_numpy()
                assert abs(score.R2 - (1-np.dot(residual,residual)/np.sum((y-y.mean())**2))) < 1e-12
            metric_count += 1
    return dict(predictions=len(predictions), metric_rows=metric_count)


def main():
    for path, checksum in json.loads((ROOT/'input_manifest.json').read_text()).items():
        assert b.sha(COMA/path) == checksum, ('input changed',path)
    old_files,_,old_body = b.v.read_doc(b.b.MAIN)
    files,_,body = b.v.read_doc(b.MAIN)
    old_si_files,_,old_si_body = b.v.read_doc(b.b.SI)
    si_files,_,si_body = b.v.read_doc(b.SI)
    texts,main_figures = d.inspect(b.MAIN)
    si_texts,si_figures = d.inspect(b.SI)
    assert fields(body) == fields(old_body)
    assert fields(si_body) == fields(old_si_body)
    for number in range(1,8):
        assert any(t.startswith('[COAUTHORS H'+str(number)) for t in texts)
    for old, new in [(old_files,files),(old_si_files,si_files)]:
        for name in old:
            if name.startswith('word/media/'):
                assert old[name] == new[name],name
    main_tables = body.findall('w:tbl',b.NS)
    original_tables = old_body.findall('w:tbl',b.NS)
    assert len(main_tables) == 7
    assert [rows(t) for t in main_tables[:5]] == [rows(t) for t in original_tables]
    assert main_figures == 8 and si_figures == 22
    assert [int(re.match(r'^Figure (\d+)\.', t)[1]) for t in texts if re.match(r'^Figure (\d+)\.', t)] == list(range(1,9))
    assert [int(re.match(r'^Table (\d+)\.', t)[1]) for t in texts if re.match(r'^Table (\d+)\.', t)] == list(range(1,8))
    refs = texts[texts.index('References')+1:]
    assert len([t for t in refs if re.match(r'^\d+\. ',t)]) == 13
    assert any(t.startswith('6. Cai, F.; Zacour, K.;') for t in refs)
    assert 'layers 4–11, the pooler' not in '\n'.join(texts)
    assert 'outer encoder LayerNorm' in '\n'.join(texts)
    for number in range(27,34):
        assert any(t.startswith('Table S'+str(number)+'.') for t in si_texts)
    before = [b.h.text(p) for p in old_si_body]
    after = [b.h.text(p) for p in si_body]
    def section(text):
        start = next(i for i,t in enumerate(text) if t.startswith('S16.'))
        end = next(i for i,t in enumerate(text[start+1:],start+1) if t.startswith('S17.'))
        return text[start:end]
    assert section(before) == section(after)
    summary = pd.read_csv(b.ANALYSIS/'direct_summary.csv')
    parameters = pd.read_csv(b.ANALYSIS/'parameters_and_budgets.csv')
    ci = pd.read_csv(b.ANALYSIS/'paired_bootstrap.csv')
    assert rows(main_tables[5]) == b.direct_table(summary,parameters)
    assert rows(main_tables[6]) == b.weight_table(ci)
    derivation = pd.read_csv(ROOT/'analysis/human_censor_derivation.csv')
    assert set(derivation.seed) == set(range(5))
    assert round(derivation.pooled_RMSE_lower_bound.mean(),3) == 2.101
    assert round(derivation.Ec_MBC_RMSE_lower_bound.mean(),3) == 2.356
    assert rows(si_body.findall('w:tbl',b.NS)[-1]) == b.censor_table(derivation)
    primary = pd.read_csv(b.PRIMARY_CONTRASTS)
    for arm,shuffled in [('expert','expert-shuffled'),('quant-continuous','quant-shuffled'),
                         ('quant-binary','quant-binary-shuffled')]:
        old = primary[(primary.cohort=='QAC105') & (primary.task=='pooled') &
                      (primary.comparison==arm+' minus '+shuffled)].iloc[0]
        bound = f'{old.ci_low:+.3f}'.replace('-','−')
        assert bound in '\n'.join(texts)
    assert len(summary) == 165
    assert len(pd.read_csv(b.ANALYSIS/'ablation_summary.csv')) == 375
    check = json.loads((b.ANALYSIS/'verification.json').read_text())
    assert check['completed'] and check['direct_fits'] == 363 and check['ablation_fits'] == 1331
    assert check['saved_final_models_replay']['completed']
    assert check['saved_final_models_replay']['final_models'] == 33
    assert len(check['original_prediction_replays']) == 93
    assert all(r['max_prediction_difference'] < 1e-12 for r in check['original_prediction_replays'])
    assert len(check['rewind_all_predictions_equal']) == 15
    assert all(r['arms'] == 6 and r['predictions_identical'] for r in check['rewind_all_predictions_equal'])
    recomputation = {branch:check_prediction_metrics(branch) for branch in ['direct','ablation']}
    assert recomputation['direct']['metric_rows'] == 495
    assert recomputation['ablation']['metric_rows'] == 1815
    full = '\n'.join(texts+si_texts)
    for filename,column in [('QAC105.csv','compound_id'),('OOD17.csv','code')]:
        assert all(str(value) in full for value in pd.read_csv(b.RUN/'data'/filename)[column])
    assert 'sk-or-v1-' not in full and 'Authorization: Bearer' not in full
    abstract = texts[texts.index('Abstract')+1]
    assert len(abstract.split()) <= 200
    report = dict(completed=True, main=str(b.MAIN), supporting_information=str(b.SI),
        main_sha256=b.sha(b.MAIN), si_sha256=b.sha(b.SI),
        input_hashes_unchanged=True, original_five_tables_preserved=True,
        original_media_preserved=True, coauthor_fields_byte_preserved=True,
        chemistry_and_assay_section_preserved=True, main_figures=main_figures,
        main_tables=len(main_tables), supplementary_figures=si_figures,
        published_metric_rows=8, new_direct_fits=363, new_decoder_fits=1331,
        original_prediction_sets_reproduced=93, metric_recomputation=recomputation,
        saved_final_OOD_models_reloaded=33,
        human_censor_sensitivity_derived_per_seed=True,
        primary_repeated_contrasts_keep_10000draw_intervals=True,
        abstract_words=len(abstract.split()), full_cohorts_preserved=True)
    (ROOT/'document_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
