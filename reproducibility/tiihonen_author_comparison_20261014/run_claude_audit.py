"""Actual Claude read-only audit, using authorised local Mac CLI."""
from pathlib import Path
import datetime as dt, hashlib, json, subprocess, time

ROOT=Path(__file__).resolve().parent
REV=ROOT/'reviews'
SYSTEM=('You are an independent scientific reproducibility auditor. The researcher explicitly '
        'asked for Claude as a subagent and authorised sharing research materials. '
        'Read only the explicitly listed source files; never execute code, edit files, read '
        'credentials or delegate. Distinguish reported findings and verifiable code/data '
        'from hypotheses. Give a concrete concise comparison protocol and flag unsupported claims.')

def main():
    source=Path('/private/tmp/coma_tiihonen_20261014')
    paths=[source/'README.md',source/'Main_downselection.py',
           source/'Functions_downselection_training_RF.py',
           Path('/private/tmp/tiihonen2021_comparison.txt')]
    prompt=SYSTEM+'\nTASK: audit Tiihonen et al JACS 2021 (DOI10.1021/jacs.1c05055), COE/E.coli K12 MIC. '
    prompt+='We must test frozen raw MolFormer and an externally human-trained compact feature adapter '
    prompt+='(768→512→384→256, then fixed CatBoost500/depth6/lr.05/seed42) on their original held-out20, '
    prompt+='against a freshly fitted author RF21 (do NOT unpickle public artifacts). '
    prompt+='This is NOT Q-HERO, NOT S.aureus. Paper reports R².65; code footer reports .6491613775/RMSE1.0937822922. '
    prompt+='Observed local archive CSV: dataset_outliers_dropped114rows,5262data columns; '
    prompt+='Reference y_opt_train80/y_opt_test20/y_opt_newdata7; Fingerprints/y_smiles_train78. '
    prompt+='Source code explicit train80indices includes two invalid RDKit SMILES. '
    prompt+='Public and local sources being checked. Our encoder source corpus1103expert overlaps0/20test cations and2/78train cations preliminarily; quantitative source audit pending. '
    prompt+='Native target log2µg/mL equals log2mg/L numerically, unlike QHERO molar conversion. '
    prompt+='No test-set tuning allowed; source leakage must be disclosed. '
    prompt+='Please independently inspect listed files with Read, especially data curation, known changes to source XLSX, '
    prompt+='censor substitution, selected features/hyperparameters and what train78 versus80 allows us to claim. '
    prompt+='Give at most1000words: (1)dataset/protocol identity, (2)safe minimal replication, '
    prompt+='(3)pitfalls invalidating a claim of beating paper, (4)justified result wording.\nPERMITTED FILES:\n'
    prompt+='\n'.join(map(str,paths))
    (REV/'claude_prompt.txt').write_text(prompt)
    command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet',
             '--tools','Read','--allowed-tools','Read','--permission-mode','dontAsk',
             '--no-session-persistence','--disable-slash-commands','--no-chrome',
             '--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
             '--system-prompt',SYSTEM,'--output-format','stream-json','--verbose','--max-budget-usd','4']
    rec=dict(reviewer='actual Claude CLI',execution='local Mac',authorised=True,
             started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),completed=False,
             prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
             files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    start=time.time()
    try:
        with (REV/'claude_raw.jsonl').open('w') as out,(REV/'claude_stderr.log').open('w') as err:
            result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=480)
        events=[]
        for line in (REV/'claude_raw.jsonl').read_text().splitlines():
            try:events.append(json.loads(line))
            except json.JSONDecodeError:pass
        last={};calls=[]
        for e in events:
            if e.get('type')=='result':last=e
            for b in e.get('message',{}).get('content',[]):
                if isinstance(b,dict) and b.get('type')=='tool_use':
                    calls.append(dict(name=b.get('name'),input=b.get('input')))
        review=last.get('result','')
        rec.update(returncode=result.returncode,tool_calls=calls,
                   model_usage=last.get('modelUsage'),cost_usd=last.get('total_cost_usd'))
        if result.returncode==0 and review and not last.get('is_error'):
            (REV/'claude_review.txt').write_text(review);rec['completed']=True
    except subprocess.TimeoutExpired:rec['status']='timeout'
    rec['seconds']=time.time()-start
    (REV/'claude_process.json').write_text(json.dumps(rec,indent=2))
    print(json.dumps({k:rec[k] for k in ['reviewer','completed','seconds']}))

if __name__=='__main__':main()
