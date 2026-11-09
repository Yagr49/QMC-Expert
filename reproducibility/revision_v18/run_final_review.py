"""Actual read-only Kimi and Claude review, on the authorised local computer."""
from pathlib import Path
import argparse,datetime as dt,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews';REV.mkdir(exist_ok=True)
SYSTEM=('You are a scientific manuscript and figure reviewer. The owner explicitly authorises Kimi and Claude to review this unpublished article. '
 'Use only image-reading tools on the listed paths; no commands, edits, delegation or other file access. '
 'Review provided text and visually inspect all listed figures. Report at most 1000 words: concrete scientific corrections and figure/style suggestions. '
 'The author requires v5 as the foundation. Preserve its original positive reported values while distinguishing reported values, recovered notebook outputs, '
 'approximate reconstruction and completed controlled follow-ups. Do not invent provenance or results.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('reviewer',choices=['kimi','claude']);a=ap.parse_args()
 text=(ROOT/'manuscript_v18_readable.md').read_text();text=text.split('4. Experimental protocol')[0]
 paths=[ROOT/'figures'/(n+'.png') for n in ['figure1_v5_guided_embedding_pipeline','figure6_v5_embedding_geometry','figure7_compact_real_shuffled_violins','figure8_v5_modern_decoders']]
 paths+=[ROOT.parent/'revision_v17/sources/image1.png']
 prompt=SYSTEM+'\nImportant limitations to respect: absent full-corpus quantitative checkpoint does NOT prove the original Table2 used a surrogate; '
 prompt+='April seed79 selection is NOT established as the origin of May Table1/2; CausalForest interval and endpoint ΔRMSE bootstrap are different analyses. '
 prompt+='New compact real-vs-shuffled and weight-reset contrasts are null or unfavourable; these are retained, not claimed as biological causality. '
 prompt+='Annotation methods H1–H7 and laboratory details are reserved for coauthors. Complete article package integrity is checked separately. '
 prompt+='Aim: soft Aptos, pastel lavender/mint, thin grids, minimal text inside scientific plots, ACS1996 exact molecules. '
 prompt+='PCA panels use independent axes and structural class colours, not activity labels. Violins are mean absolute error across seeds per compound/endpoint, no tail capping. '
 prompt+='264 modern-model fits are completed. Comment on claims, narrative continuity and legibility at journal width.\nARTICLE\n'+text
 prompt+='\nPERMITTED IMAGE PATHS (inspect all five):\n'+'\n'.join(map(str,paths))
 stem=a.reviewer+'_v18_final';(REV/(stem+'_prompt.txt')).write_text(prompt)
 if a.reviewer=='kimi':
  agent=REV/'v18_visual_reviewer.md';agent.write_text('---\nname: v18-reviewer\ndescription: Read-only scientific reviewer\ntools:\n  - ReadMediaFile\nsubagents: []\n---\n'+SYSTEM)
  executable=Path.home()/'.kimi-code/bin/kimi';command=[str(executable),'-p',prompt,'--agent-file',str(agent),'--output-format','stream-json']
 else:
  executable=Path.home()/'.local/bin/claude';command=[str(executable),'-p',prompt,'--model','sonnet','--tools','Read','--allowed-tools','Read',
   '--permission-mode','dontAsk','--no-session-persistence','--disable-slash-commands','--no-chrome','--setting-sources','',
   '--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--system-prompt',SYSTEM,'--output-format','stream-json','--verbose','--max-budget-usd','3']
 record=dict(reviewer=a.reviewer,execution='local Mac',authorised=True,completed=False,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
  images={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
 meta=REV/(stem+'_process.json');meta.write_text(json.dumps(record,indent=2));start=time.time()
 try:
  with (REV/(stem+'_raw.jsonl')).open('w') as out,(REV/(stem+'_stderr.log')).open('w') as err:
   result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=420)
  events=[]
  for line in (REV/(stem+'_raw.jsonl')).read_text().splitlines():
   try:events.append(json.loads(line))
   except json.JSONDecodeError:pass
  calls=[];texts=[];last={}
  for event in events:
   if event.get('type')=='result':last=event
   message=event.get('message',event)
   if message.get('role',event.get('type'))!='assistant':continue
   content=message.get('content',[])
   if isinstance(content,str):texts.append(content)
   else:
    for block in content:
     if block.get('type')=='text':texts.append(block.get('text',''))
     if block.get('type')=='tool_use':calls.append(dict(name=block.get('name'),arguments=block.get('input')))
   for call in message.get('tool_calls',[]):
    fn=call.get('function',{});calls.append(dict(name=fn.get('name'),arguments=fn.get('arguments')))
  review=last.get('result') or (texts[-1] if texts else '')
  record.update(returncode=result.returncode,tool_calls=calls,visually_read_images=len(calls),model_usage=last.get('modelUsage'),cost_usd=last.get('total_cost_usd'))
  if result.returncode==0 and review and calls and not last.get('is_error'):
   (REV/(stem+'_review.txt')).write_text(review);record['completed']=True
 except subprocess.TimeoutExpired:record['status']='Timed out; retained local evidence'
 record['seconds']=time.time()-start;meta.write_text(json.dumps(record,indent=2));print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']}))
if __name__=='__main__':main()
