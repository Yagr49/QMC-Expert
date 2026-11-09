"""Actual Kimi/Claude critique of the v5-anchored revision, executed on the Mac."""
from pathlib import Path
import argparse,json,subprocess,time,hashlib,datetime as dt
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews';REV.mkdir(exist_ok=True)
SYSTEM=('You are an independent scientific reviewer of an unpublished molecular ML manuscript. '
 'Its owner explicitly authorises review by Kimi and Claude. Review only supplied text; '
 'no tools, file edits, commands, delegation or invented results. Give at most 750 words. '
 'The author requires original v5 to remain the manuscript foundation, with new checks '
 'testing its hypotheses rather than silently replacing its method or metrics. '
 'Distinguish preserved original results, recovered notebook-output provenance, '
 'approximate reconstruction and newly completed controlled follow-ups.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('reviewer',choices=['kimi','claude']);a=ap.parse_args()
 prompt=SYSTEM+'\nFocus on '+('narrative continuity, adapter explanations and organising the hypothesis sequence.' if a.reviewer=='kimi' else 'numerical provenance, identifiability, validation and scientific claims.')+'\n'
 paths=[ROOT/'sources/v5_modelling_text.md',ROOT.parent/'notebook_recovery_20261012/README_RU.md',
        ROOT.parent/'v5_hypotheses_20261013/PROTOCOL.md']
 for p in paths:prompt+='\nSOURCE '+p.name+'\n'+p.read_text()+'\n'
 prompt+='\nNew checks are running, not completed. No future numbers may be invented. '
 prompt+='Original Tables 1–2 and chemistry will remain in the main paper. H1–H7/C1 '
 prompt+='are reserved for coauthors. Source-only heads and task text are not measured MIC. '
 prompt+='The full-corpus quantitative multitarget checkpoint has not been located; '
 prompt+='analysis/encoder_reg_only.pth is a distinct QAC-binned ablation. '
 prompt+='Recommend concrete corrections that retain the v5 narrative.\n'
 stem=a.reviewer+'_v5_revision_plan';(REV/(stem+'_prompt.txt')).write_text(prompt)
 if a.reviewer=='kimi':
  binary=Path.home()/'.kimi-code/bin/kimi';command=[str(binary),'-p',prompt,'--output-format','text']
 else:
  binary=Path.home()/'.local/bin/claude';command=[str(binary),'-p',prompt,'--model','sonnet','--tools','',
   '--permission-mode','dontAsk','--no-session-persistence','--disable-slash-commands','--no-chrome',
   '--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
   '--system-prompt',SYSTEM,'--output-format','json','--max-budget-usd','2']
 record=dict(reviewer=a.reviewer,execution='local Mac',authorised=True,completed=False,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
 meta=REV/(stem+'_process.json');meta.write_text(json.dumps(record,indent=2));start=time.time()
 try:
  with (REV/(stem+'_raw.txt')).open('w') as out,(REV/(stem+'_stderr.log')).open('w') as err:
   r=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=360)
  record['returncode']=r.returncode;output=(REV/(stem+'_raw.txt')).read_text()
  if a.reviewer=='claude':
   obj=json.loads(output);output=obj.get('result','');record['model_usage']=obj.get('modelUsage');record['cost_usd']=obj.get('total_cost_usd')
  if r.returncode==0 and output.strip():(REV/(stem+'_review.txt')).write_text(output);record['completed']=True
 except subprocess.TimeoutExpired:record['status']='Timed out'
 record['seconds']=time.time()-start;meta.write_text(json.dumps(record,indent=2));print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']}))
if __name__=='__main__':main()
