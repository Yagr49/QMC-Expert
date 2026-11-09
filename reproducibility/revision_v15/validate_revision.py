"""Check document integrity, immutable inputs and correspondence to experiment outputs."""
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
spec = importlib.util.spec_from_file_location('builder', ROOT / 'build_revision.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
spec = importlib.util.spec_from_file_location('doc_inspection', ROOT.parent / 'revision_v12/validate_documents.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def author_fields(body):
    return [E.tostring(p) for p in body if b.h.text(p).startswith('[COAUTHORS')]


def rows(table):
    return [[b.h.text(c) for c in row.findall('w:tc', b.NS)]
            for row in table.findall('w:tr', b.NS)]


def main():
    for name, checksum in json.loads((ROOT / 'input_manifest.json').read_text()).items():
        assert b.sha(COMA / name) == checksum, ('input changed', name)
    oldfiles, oldtree, oldbody = b.v.read_doc(COMA / '2026_10_11_Paper_2_edited-v14_QAC105_OOD17.docx')
    files, tree, body = b.v.read_doc(b.MAIN)
    main_texts, figures = d.inspect(b.MAIN)
    si_texts, si_figures = d.inspect(b.SI)
    assert author_fields(body) == author_fields(oldbody)
    assert figures == 6 and si_figures == 21
    assert [int(re.match(r'^Figure (\d+)\.', t)[1]) for t in main_texts
            if re.match(r'^Figure (\d+)\.', t)] == list(range(1, 7))
    assert [int(re.match(r'^Table (\d+)\.', t)[1]) for t in main_texts
            if re.match(r'^Table (\d+)\.', t)] == list(range(1, 6))
    for number in range(1, 8):
        assert any(t.startswith('[COAUTHORS H' + str(number)) for t in main_texts)
    oldtables, tables = oldbody.findall('w:tbl', b.NS), body.findall('w:tbl', b.NS)
    assert len(oldtables) == 4 and len(tables) == 5
    assert [rows(t) for t in tables[:4]] == [rows(t) for t in oldtables]
    intro = main_texts.index('1. Introduction')
    assert main_texts[intro + 1].startswith('Fine-tuning a molecular foundation model')
    reference_index = main_texts.index('References')
    references = [t for t in main_texts[reference_index + 1:] if re.match(r'^\d+\. ', t)]
    assert len(references) == 12
    old_reference_index = [b.h.text(p) for p in oldbody].index('References')
    oldrefs = [E.tostring(p) for p in list(oldbody)[old_reference_index + 1:]
               if re.match(r'^\d+\. ', b.h.text(p))]
    newrefs = [E.tostring(p) for p in list(body)[list(body).index(b.find(body, 'References')) + 1:]
               if re.match(r'^\d+\. ', b.h.text(p))]
    assert oldrefs == newrefs[:8]
    # All original molecular depictions and article figures remain byte-identical.
    for name in oldfiles:
        if name.startswith('word/media/'):
            assert files[name] == oldfiles[name]
    pooled = pd.read_csv(b.ANALYSIS / 'comparison_pooled.csv')
    actual_rows = rows(tables[4])
    assert actual_rows == b.pooled_table(pooled)
    assert len(actual_rows) == 22
    # Independently reconstruct every pooled score from endpoint-level predictions.
    for model in b.MODELS:
        pred = pd.read_csv(b.RUN / ('results_20261012T152125Z/new_baselines/' + model + '/predictions.csv'))
        scored = pred[pred.qualifier == '=']
        values = {}
        for key, group in scored.groupby(['representation', 'schema', 'seed']):
            values[key] = float(np.sqrt(np.mean((group.y - group.prediction) ** 2)))
            assert group.compound_id.nunique() == (17 if key[1] == 'full-QAC105' else 105)
            assert len(group) == (67 if key[1] == 'full-QAC105' else 420)
        for row in pooled[pooled.model == model].itertuples():
            expected = np.mean([value for (rep, schema, seed), value in values.items()
                                if rep == row.representation and schema == row.schema])
            assert abs(expected - row.RMSE) < 1e-12
    # Verify the stated directions and retain quantitative wins in scaffold CV.
    for model in b.MODELS[:-1]:
        for schema in ['cation', 'scaffold', 'full-QAC105']:
            group = pooled[(pooled.model == model) & (pooled.schema == schema)].set_index('representation')
            comparisons = (['raw-molformer'] if schema == 'scaffold' else
                           ['raw-molformer', 'quant-continuous_seed0', 'quant-binary_seed0'])
            for rep in comparisons:
                assert group.loc['expert_seed0'].RMSE < group.loc[rep].RMSE
    for model, rep in [('catboost', 'quant-continuous_seed0'), ('autogluon', 'quant-binary_seed0')]:
        group = pooled[(pooled.model == model) & (pooled.schema == 'scaffold')].set_index('representation')
        assert group.loc[rep].RMSE < group.loc['expert_seed0'].RMSE
    bootstrap = pd.read_csv(b.ANALYSIS / 'paired_cluster_bootstrap.csv')
    for model in ['tabpfn', 'tabfm']:
        row = bootstrap[(bootstrap.model == model) & (bootstrap.schema == 'full-QAC105') &
                        (bootstrap.comparator == 'rdkit') & (bootstrap.grouping == 'cation')].iloc[0]
        assert row.low < 0 < row.high
        assert f'{row.low:+.3f}'.replace('-', '−') in '\n'.join(main_texts)
        assert f'{row.high:+.3f}' in '\n'.join(main_texts)
    old_si_files, _, old_si_body = b.v.read_doc(b.PREVIOUS / 'Supplementary_Information_v14.docx')
    si_files, _, si_body = b.v.read_doc(b.SI)
    assert author_fields(si_body) == author_fields(old_si_body)
    for name in old_si_files:
        if name.startswith('word/media/'):
            assert si_files[name] == old_si_files[name]
    assert all(f'Table S{number}.' in '\n'.join(si_texts) for number in range(23, 27))
    # Synthetic and microbiological records and all their reserved fields are preserved.
    before = [b.h.text(n) for n in old_si_body]
    after = [b.h.text(n) for n in si_body]
    start = next(i for i, t in enumerate(before) if t.startswith('S16.'))
    end = next(i for i, t in enumerate(before[start + 1:], start + 1) if t.startswith('S17.'))
    newstart = next(i for i, t in enumerate(after) if t.startswith('S16.'))
    newend = next(i for i, t in enumerate(after[newstart + 1:], newstart + 1) if t.startswith('S17.'))
    assert before[start:end] == after[newstart:newend]
    for filename, identifier in [('QAC105.csv', 'compound_id'), ('OOD17.csv', 'code')]:
        assert all(value in '\n'.join(si_texts) for value in pd.read_csv(b.PREVIOUS / 'data' / filename)[identifier])
    abstract = main_texts[main_texts.index('Abstract') + 1]
    assert len(abstract.split()) <= 200
    full = '\n'.join(main_texts + si_texts)
    assert 'sk-or-v1-' not in full and 'Authorization: Bearer' not in full
    assert 'general claim that fine-tuning is harmful would conflict' in full
    assert 'The earlier suggestion of an arithmetic correction to 2.27 is withdrawn.' in full
    assert 'its direct contribution to the v5 table has not been established' in full.replace('\n', ' ')
    report = dict(completed=True, main=str(b.MAIN), supporting_information=str(b.SI),
                  main_sha256=b.sha(b.MAIN), si_sha256=b.sha(b.SI),
                  input_hashes_unchanged=True, document_xml_relationships_styles_valid=True,
                  coauthor_fields_byte_preserved=True, chemistry_and_assay_records_preserved=True,
                  primary_tables_unchanged=True, existing_media_byte_preserved=True,
                  main_figures=figures, main_tables=len(tables), supplementary_figures=si_figures,
                  pooled_model_comparisons=len(pooled),
                  pooled_scores_recomputed_from_predictions=True,
                  full_QAC105_and_OOD17_preserved=True, abstract_words=len(abstract.split()))
    (ROOT / 'document_validation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
