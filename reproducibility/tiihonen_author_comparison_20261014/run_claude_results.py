"""Actual Claude final check of completed experiment, local Mac only."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews'

def main():
 system=('You are Claude independently auditing completed molecular-ML results. The owner explicitly '
  'requested Claude and authorised sharing. Review only the supplied text, no tools or edits. '
  'At most450 words. Correct your earlier unsupported statements and give an accurate verdict; '
  'do not invent numerical confidence intervals, significance, provenance or experiments.')
 prompt=system+'\nEarlier your source-file audit had useful protocol comments but also errors. '
 prompt+='We completed fresh RF and frozen embedding comparisons; there is no victory claim. '
 for p in [ROOT/'comparison_test20.csv',ROOT/'validation.json',ROOT/'v5_comparison_manifest.json',
           REV/'REVIEW_RESPONSE.md']:
  text=p.read_text()
  if p.name=='v5_comparison_manifest.json':
   d=json.loads(text);d.pop('inputs',None);text=json.dumps(d,indent=2)
  prompt+='\nSOURCE '+p.name+'\n'+text
 prompt+='\nAssess: are native RF reproduction and matched78 comparison adequately supported? '
 prompt+='Can we say human-adapter improves raw point estimate but does not beat Tiihonen RF? '
 prompt+='What minimal caveats are needed? Explicitly separate human-source overlap from MolFormerpretraining, '
 prompt+='test20authorboundsubstitution from exactlabels, and newdata7 frompaper15. '
 prompt+='Do not repeat the earlier inventedCI or require formalattestation. Return concise final corrected assessment.'
 (REV/'claude_results_prompt.txt').write_text(prompt)
 command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet','--tools','',
  '--permission-mode','dontAsk','--no-session-persistence','--disable-slash-commands','--no-chrome',
  '--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
  '--system-prompt',system,'--output-format','json','--max-budget-usd','2']
 rec=dict(execution='local Mac',actual_reviewer='Claude CLI',authorised=True,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),completed=False,
  prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest());start=time.time()
 try:
  with (REV/'claude_results_raw.json').open('w') as out,(REV/'claude_results_stderr.log').open('w') as err:
   result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=240)
  e=json.loads((REV/'claude_results_raw.json').read_text());review=e.get('result','')
  rec.update(returncode=result.returncode,model_usage=e.get('modelUsage'),cost_usd=e.get('total_cost_usd'))
  if result.returncode==0 and review and not e.get('is_error'):
   (REV/'claude_results_review.txt').write_text(review);rec['completed']=True
 except subprocess.TimeoutExpired:rec['status']='timeout'
 rec['seconds']=time.time()-start
 (REV/'claude_results_process.json').write_text(json.dumps(rec,indent=2))
 print(json.dumps({k:rec[k] for k in ['completed','seconds']}))
if __name__=='__main__':main()
