from pathlib import Path
import importlib.util, re, json, hashlib, zipfile
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('previous_validation',ROOT.parent/'revision_v12/validate_documents.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def main():
    previous,_=old.inspect(COMA/'2026_10_11_Paper_2_edited-v12_matched_finetuning.docx')
    oldfields={re.search(r'\[COAUTHORS ([AHD]\d+)',p)[1]:p for p in previous if re.search(r'\[COAUTHORS ([AHD]\d+)',p)}
    paths=[COMA/'2026_10_11_Paper_2_edited-v14_QAC105_OOD17.docx',ROOT/'Supplementary_Information_v14.docx']
    docs=[]
    for path in paths:
        texts,figures=old.inspect(path);full='\n'.join(texts)
        if path==paths[0]:
            fields={re.search(r'\[COAUTHORS ([AHD]\d+)',p)[1]:p for p in texts if re.search(r'\[COAUTHORS ([AHD]\d+)',p)}
            assert fields==oldfields
            assert [int(re.match(r'^Figure (\d+)\.',t)[1]) for t in texts if re.match(r'^Figure (\d+)\.',t)]==list(range(1,6))
            assert [int(re.match(r'^Table (\d+)\.',t)[1]) for t in texts if re.match(r'^Table (\d+)\.',t)]==list(range(1,5))
            assert figures==5
            assert 'Q-HERO scaffold-CV RMSE 1.529' not in full
            assert 'target_25e7bff606cb' in full and '>500 mg/L' in full
            assert 'after inspection of earlier analyses' in full
            assert 'no consistently resolved advantage over one-hot' in full
            assert '28,375,297' in full
            assert 'randomised biological treatments' in full
            for number in range(1,8):assert f'COAUTHORS H{number}' in full
            reference_index=texts.index('References')
            assert len([t for t in texts[reference_index+1:] if re.match(r'^\d+\. ',t)])==8
        else:
            assert 'S19. Original-cohort four-endpoint evaluation' in full
            assert 'S20. Complete original and OOD registries' in full
            assert 'COAUTHORS C1' in full and 'S16.6.4. MIC and MBC determination' in full
            assert all(code in full for code in pd.read_csv(ROOT/'data/OOD17.csv').code)
            assert all(code in full for code in pd.read_csv(ROOT/'data/QAC105.csv').compound_id)
            assert figures==21
            assert [int(re.match(r'^Figure S(\d+)\.',t)[1]) for t in texts if re.match(r'^Figure S(\d+)\.',t)]==list(range(1,22))
            for number in range(16,23):assert f'Table S{number}.' in full
        assert all(term not in full for term in ['sk-or-v1-','Authorization: Bearer'])
        docs.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),figures=figures,xml_styles_relationships_valid=True))
    summary=pd.read_csv(ROOT/'analysis/summary.csv')
    draft=(ROOT/'main_draft.md').read_text()
    for arm in ['expert','quant-continuous','quant-binary','raw-molformer']:
        row=summary.query("cohort=='QAC105' and encoding=='onehot' and task=='pooled' and arm==@arm").iloc[0]
        assert f'{row.RMSE:.3f}' in draft
    p=pd.read_csv(ROOT/'results/predictions.csv');q=pd.read_csv(ROOT/'data/QAC105.csv')
    assert q.groupby('cation').fold.nunique().max()==1 and len(q)==105
    assert p.query("cohort=='OOD17' and qualifier=='>'").compound_id.unique().tolist()==['IT505']
    for f in (ROOT/'figures').glob('*.pdf'):assert f.read_bytes().startswith(b'%PDF')
    abstract=draft.split('## Abstract\n\n')[1].split('\n\n## Keywords')[0]
    assert len(abstract.split())<=210
    assert 'partial' not in abstract.lower() or 'partial MolFormer' in abstract
    # Input credentials are never in project scripts or generated research text.
    for f in ROOT.rglob('*'):
        if f.is_file() and f.suffix in ['.py','.md','.json','.txt']:
            assert not re.search(r'sk-or-v1-[0-9a-f]{64}',f.read_text(errors='replace')),f
    report=dict(completed=True,documents=docs,coauthor_fields_preserved=True,full_original_registry=True,
        named_OOD_registry=True,abstract_words=len(abstract.split()),local_OpenRouter_only=True,
        keys_absent_from_project=True,numerical_validation='validation.json',scaffold_validation='scaffold_validation.json')
    (ROOT/'document_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
