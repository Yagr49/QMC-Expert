"""Explicitly authorised read-only model critique, invoked only on the local Mac."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REVIEWS = ROOT/'reviews'
SYSTEM = ('You are an independent scientific reviewer. Review only the supplied manuscript '
          'and numerical summaries. Do not call tools, read extra files, execute commands, '
          'edit files or invent experiments, annotation procedures or facts. This unpublished '
          'material is explicitly authorised by its owner for review by Kimi and Claude. '
          'Give at most 600 words. Separate concrete errors affecting current claims from '
          'optional new experiments outside their scope. Check internal numerical consistency '
          'and causal interpretation; finding a model critique is not human peer review.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('reviewer',choices=['kimi','claude']);args=ap.parse_args()
    REVIEWS.mkdir(exist_ok=True)
    prompt=SYSTEM+'\n\nFocus on the v16 additions: direct MIC/MBC prediction versus '
    prompt+='frozen guided encoder plus decoder; actual LoRA versus partial/full fine-tuning; '
    prompt+='weight rewinds that preserve source checkpoint buffers and refit the decoder. '
    prompt+='The design is exploratory, with fixed budgets and conditional unadjusted '
    prompt+='seed/group intervals. Primary frozen-decoder results have five source seeds; '
    prompt+='direct fits pair three source/target seeds one-to-one, and route contrasts '
    prompt+='use only those same first three source checkpoints. No universal adapter '
    prompt+='superiority, equivalence to measurements, independent human-information '
    prompt+='channel or biological causality is established. H1-H7 remain blank by '
    prompt+='author instruction. QAC105 has 420 exact endpoints; OOD17 has 67 exact '
    prompt+='and one right-censored endpoint, four scaffold families. Return concrete '
    prompt+='corrections if these limitations are nevertheless violated.\n\n'
    paths=[ROOT/'manuscript_v16_readable.md',ROOT/'analysis/parameters_and_budgets.csv',
           ROOT/'analysis/published_metrics.csv']
    for path in paths:
        prompt+=path.name+'\n'+path.read_text()+'\n\n'
    stem=args.reviewer+'_v16_manuscript'
    (REVIEWS/(stem+'_prompt.txt')).write_text(prompt)
    version_command=([str(Path.home()/'.kimi-code/bin/kimi'),'--version'] if args.reviewer=='kimi'
                     else [str(Path.home()/'.local/bin/claude'),'--version'])
    version=subprocess.check_output(version_command,text=True).strip()
    if args.reviewer=='kimi':
        command=[str(Path.home()/'.kimi-code/bin/kimi'),'-p',prompt,'--output-format','text']
    else:
        command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet',
                 '--tools','','--permission-mode','dontAsk','--no-session-persistence',
                 '--disable-slash-commands','--no-chrome','--setting-sources','',
                 '--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
                 '--system-prompt',SYSTEM,'--output-format','json','--max-budget-usd','2']
    start=time.time()
    record=dict(reviewer=args.reviewer,cli_version=version,execution='local Mac',
                authorised_external_review=True,read_only_requested=True,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                main_sha256=hashlib.sha256((ROOT/'manuscript_v16_readable.md').read_bytes()).hexdigest(),
                started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),completed=False)
    metadata=REVIEWS/(stem+'_process.json')
    metadata.write_text(json.dumps(record,indent=2))
    raw=REVIEWS/(stem+'_raw.txt')
    try:
        with raw.open('w') as stdout,(REVIEWS/(stem+'_stderr.log')).open('w') as stderr:
            result=subprocess.run(command,cwd=str(ROOT),stdout=stdout,stderr=stderr,
                                  timeout=240,check=False)
        record['returncode']=result.returncode
        output=raw.read_text()
        if args.reviewer=='claude' and result.returncode==0:
            body=json.loads(output)
            if not body.get('is_error') and body.get('result'):
                (REVIEWS/(stem+'_review.txt')).write_text(body['result'])
                record.update(completed=True,model_usage=body.get('modelUsage'),
                              total_cost_usd=body.get('total_cost_usd'),usage=body.get('usage'))
            else:
                record['status']='CLI returned no completed scientific review'
        elif args.reviewer=='kimi' and result.returncode==0 and output.strip():
            (REVIEWS/(stem+'_review.txt')).write_text(output)
            record['completed']=True
        else:
            record['status']='CLI did not complete; raw error retained locally'
    except subprocess.TimeoutExpired:
        record['status']='Timed out without a completed review'
    record['seconds']=time.time()-start
    metadata.write_text(json.dumps(record,indent=2))
    print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']},indent=2))


if __name__=='__main__':main()
