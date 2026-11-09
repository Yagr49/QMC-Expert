"""Author-authorised image review by actual Kimi/Claude CLIs on the local Mac."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import time

ROOT=Path(__file__).resolve().parent
REVIEWS=ROOT/'reviews'
SYSTEM=('You are a scientific figure and typography reviewer. Review the supplied '
 'images visually using ONLY image-reading tools; do not execute commands, edit files, '
 'delegate or read any other files. The owner explicitly authorised transmission of '
 'these unpublished figures to Kimi and Claude. Do not infer that counts, medians '
 'or confidence intervals mean biological causality. Give at most 800 words. '
 'Provide a self-contained final review, a font preference between Aptos and Segoe UI, '
 'concrete corrections and filenames. If you cannot view an image, say so explicitly.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('reviewer',choices=['kimi','claude']);args=ap.parse_args()
 REVIEWS.mkdir(exist_ok=True)
 images=[ROOT/'sources/image1.png',ROOT/'sources/image4.png',
  ROOT/'font_previews/Aptos/figureS26_prediction_route_violins.png',
  ROOT/'font_previews/Segoe_UI/figureS26_prediction_route_violins.png']
 images += [ROOT/'figures'/(n+'.png') for n in ['figure1_supervision_and_transfer',
  'figure2_QAC105_parity','figure3_OOD_families_ACS1996','figure4_paired_error_violins',
  'figure5_weight_rewind','figureS28_decoder_error_violins','figureS29_direct_adaptation']]
 assert all(p.exists() for p in images)
 prompt=SYSTEM+'\n\nRead and visually inspect every listed PNG. Start by comparing the '
 prompt+='two reference images from the author’s original SI with the two font previews. '
 prompt+='Aim: soft, calm scientific graphics, readable ordinary fonts, pastel lavender '
 prompt+='and mint, thin light grids, short labels. Statistical explanations belong in '
 prompt+='captions, not as blocks inside the image. Check scientific glyphs, text collision, '
 prompt+='colour/marker consistency, contrast at journal size, density tails, molecule '
 prompt+='legibility, and whether reducing text loses essential identification.\n'
 prompt+='Both font previews use identical data: mean absolute errors over three paired '
 prompt+='seeds, then distributions over 420 exact endpoint pairs for each CV regime '
 prompt+='and 67 exact OOD pairs. OOD has four families and one >500 mg/L observation '
 prompt+='excluded from exact-value violins and separately retained in the caption/tables. '
 prompt+='The main parity plot shows seed-mean predictions; endpoint statistics are in '
 prompt+='Table 2. The error distributions compare human left/continuous MIC right; '
 prompt+='the two-route plot uses direct FT left/encoder+decoder right. Component-weight '
 prompt+='error bars are unadjusted 95% paired seed/scaffold intervals. Molecules use '
 prompt+='native RDKit ACS 1996 geometry and include counterions. Historical reference '
 prompt+='images are preserved, not claimed as new matched regression results.\n\n'
 prompt+='Permitted image paths:\n'+'\n'.join(str(p) for p in images)
 stem=args.reviewer+'_v17_visual'
 (REVIEWS/(stem+'_prompt.txt')).write_text(prompt)
 if args.reviewer=='kimi':
  agent=REVIEWS/'visual_reviewer.md'
  agent.write_text('---\nname: visual-reviewer\ndescription: Read-only scientific figure reviewer\n'
   'tools:\n  - ReadMediaFile\nsubagents: []\n---\n'+SYSTEM+'\n')
  executable=Path.home()/'.kimi-code/bin/kimi'
  command=[str(executable),'-p',prompt,'--agent-file',str(agent),'--output-format','stream-json']
 else:
  executable=Path.home()/'.local/bin/claude'
  command=[str(executable),'-p',prompt,'--model','sonnet','--tools','Read',
   '--allowed-tools','Read','--permission-mode','dontAsk','--no-session-persistence',
   '--disable-slash-commands','--no-chrome','--setting-sources','',
   '--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
   '--system-prompt',SYSTEM,'--output-format','stream-json','--verbose','--max-budget-usd','3']
 record=dict(reviewer=args.reviewer,execution='local Mac',authorised=True,
  cli_version=subprocess.check_output([str(executable),'--version'],text=True).strip(),
  prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
  image_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in images},
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),completed=False)
 metadata=REVIEWS/(stem+'_process.json');metadata.write_text(json.dumps(record,indent=2))
 start=time.time();raw=REVIEWS/(stem+'_raw.jsonl')
 try:
  with raw.open('w') as out,(REVIEWS/(stem+'_stderr.log')).open('w') as err:
   result=subprocess.run(command,cwd=str(ROOT),stdout=out,stderr=err,timeout=420,check=False)
  record['returncode']=result.returncode
  events=[]
  for line in raw.read_text().splitlines():
   try:events.append(json.loads(line))
   except json.JSONDecodeError:pass
  # Only text and tool request metadata are extracted; never print image payloads.
  calls=[];texts=[];result_event={}
  for event in events:
   if event.get('type')=='result':result_event=event
   message=event.get('message',event)
   role=message.get('role',event.get('type'))
   if role!='assistant':continue
   content=message.get('content',[])
   if isinstance(content,str) and content.strip():texts.append(content)
   elif isinstance(content,list):
    for block in content:
     if block.get('type')=='text':texts.append(block.get('text',''))
     if block.get('type')=='tool_use':calls.append(dict(name=block.get('name'),arguments=block.get('input')))
   for call in message.get('tool_calls',[]):
    fn=call.get('function',{});calls.append(dict(name=fn.get('name'),arguments=fn.get('arguments')))
  review=result_event.get('result') or (texts[-1] if texts else '')
  record.update(tool_calls=calls,visually_read_images=len(calls),
                model_usage=result_event.get('modelUsage'),cost_usd=result_event.get('total_cost_usd'))
  if result.returncode==0 and review and not result_event.get('is_error'):
   (REVIEWS/(stem+'_review.txt')).write_text(review);record['completed']=bool(calls)
   if not calls:record['status']='Text returned, but image-tool evidence is missing'
  else:record['status']='Review did not complete; local raw output retained'
 except subprocess.TimeoutExpired:record['status']='Timed out; local tool/image evidence retained'
 record['seconds']=time.time()-start;metadata.write_text(json.dumps(record,indent=2))
 print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']},indent=2))

if __name__=='__main__':main()
