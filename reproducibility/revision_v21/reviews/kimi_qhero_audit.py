"""Actual Kimi read-only audit on the Mac; authorised external review."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parents[2]
QH = COMA / 'reproducibility/qhero_author_comparison_20261014'

SYSTEM = ('You are Kimi, an independent scientific reviewer. The researcher explicitly '
          'authorised external review. Use only the supplied text; no tools, commands, '
          'edits or delegation. Do not invent results. Give a concise audit in Russian '
          'of at most 650 words, with concrete supported claims and unresolved limitations.')


def main():
    sources = [QH/'input_manifest.json', QH/'results/completion.json',
               QH/'results/summary.csv', QH/'run_comparison.py', QH/'summarize.py']
    prompt = SYSTEM + '''\nTASK: The researcher asks whether we beat Q-HERO and wishes to retain their v5 paper narrative.
Audit this completed comparison, identify what is genuinely still pending, and recommend honest claims.
All 18 configurations / 138 unique fits are completed. 6 independent duplicate configurations,
different threads on two servers, have zero prediction/metric difference. No models need rerunning
unless evidence shows a specific bug. Do not recommend an open-ended model search.
Published Q-HERO is a binary S. aureus MIC <=8 micromolar study; Tiihonen 2021 conjugated
oligoelectrolytes is a different dataset, not Q-HERO. Prior 411-molecule regression RMSE/R2
does not compare directly with this binary task. Current cohort is clean405, not public421 rows.
360/405 positives (AP no-skill baseline .8889); heldout81 has72 positives and9 negatives.
Source681 excludes all target full salts and cations; external partial-MolFormer fine-tuning
is separate from the original v5 compact adapter. Decoder CatBoost is trained on quantitative
Q-HERO train labels after source human/quantitative/shuffled training. Scaffold CV pooled scores
are over405 OOF; five seeds pair source training with decoder seed. Heldout20 split is fixed,
test not used for feature/model selection. Historical human+text v5 adapter is NOT rerun here.
Paired test bootstrap is conditional on fitted target models and fixed class counts, not full
training uncertainty. Main/SI must not receive new Q-HERO numbers yet, researcher wants chat only.
Human .832 heldout AUROC, shuffled .845: no human semantic advantage on random test.
Scaffold human .675 vs shuffled .567 suggests utility under that protocol, not biology causality.
No formal scaffold contrast CI has yet been calculated; SD is not a CI.
Please focus on whether claims are supported, protocol comparability, and what belongs in
v5 Introduction/2.1 versus discussion-only 2.2. Root handles DOCX edits preserving original text.
'''
    for p in sources:
        prompt += '\nSOURCE ' + p.name + '\n' + p.read_text() + '\n'
    (ROOT/'kimi_qhero_prompt.txt').write_text(prompt)
    agent = ROOT/'kimi_qhero_agent.md'
    agent.write_text('---\nname: qhero-auditor\ndescription: Read-only scientific audit\ntools: []\nsubagents: []\n---\n'+SYSTEM)
    record = dict(reviewer='actual Kimi CLI', execution='local Mac', authorised=True,
                  completed=False, started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                  files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    meta = ROOT/'kimi_qhero_process.json'
    meta.write_text(json.dumps(record,indent=2))
    started=time.time()
    try:
        with (ROOT/'kimi_qhero_raw.txt').open('w') as out, (ROOT/'kimi_qhero_stderr.log').open('w') as err:
            result = subprocess.run([str(Path.home()/'.kimi-code/bin/kimi'), '-p', prompt,
                                     '--agent-file', str(agent), '--output-format', 'text'],
                                    cwd=COMA,stdout=out,stderr=err,timeout=360)
        record['returncode']=result.returncode
        output=(ROOT/'kimi_qhero_raw.txt').read_text()
        if result.returncode==0 and output.strip():
            (ROOT/'kimi_qhero_review.txt').write_text(output)
            record['completed']=True
    except subprocess.TimeoutExpired:
        record['status']='Timed out; raw response preserved, no completed review claimed'
    record['seconds']=time.time()-started
    meta.write_text(json.dumps(record,indent=2))
    print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']}))


if __name__ == '__main__':
    main()
