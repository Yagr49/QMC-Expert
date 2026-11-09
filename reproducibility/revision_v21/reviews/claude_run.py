"""User-requested actual Claude audit; local Mac, read-only, no credential output."""
from pathlib import Path
import hashlib,json,subprocess,time,datetime as dt
ROOT=Path(__file__).resolve().parent

def main():
 prompt=(ROOT/'claude_prompt.txt').read_text()
 system=('You are an independent scientific reviewer. The owner explicitly requested Claude '
  'and authorised sharing the research. Work only on supplied text with no tools, commands '
  'or edits. Do not claim experiments are completed unless supported by saved results. '
  'Preserve the original v5 prose: suggest additions only to Introduction and2.1;2.2 remains '
  'for later discussion. Be concise and distinguish external compact adaptation, partial '
  'backbone adaptation, LoRA and full fine-tuning. No universal anti-fine-tuning claims.')
 command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet','--tools','',
  '--permission-mode','dontAsk','--no-session-persistence','--disable-slash-commands','--no-chrome',
  '--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
  '--system-prompt',system,'--output-format','json','--max-budget-usd','2']
 record=dict(reviewer='actual Claude CLI',execution='local Mac',authorised=True,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),completed=False,
  prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest());start=time.time()
 try:
  with (ROOT/'claude_raw.json').open('w') as out,(ROOT/'claude_stderr.log').open('w') as err:
   run=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=240)
  obj=json.loads((ROOT/'claude_raw.json').read_text());review=obj.get('result','')
  record.update(returncode=run.returncode,model_usage=obj.get('modelUsage'),cost_usd=obj.get('total_cost_usd'))
  if run.returncode==0 and review and not obj.get('is_error'):
   (ROOT/'claude_review.txt').write_text(review);record['completed']=True
 except subprocess.TimeoutExpired:record['status']='timeout'
 except (json.JSONDecodeError,OSError) as exc:record['status']=str(exc)
 record['seconds']=time.time()-start
 (ROOT/'claude_process.json').write_text(json.dumps(record,indent=2))
 print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']}))

if __name__=='__main__':main()
