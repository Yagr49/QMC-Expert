"""Actual Claude visual/scientific audit on the authorised local Mac."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews';REV.mkdir(exist_ok=True)
SYSTEM=('You are Claude, an independent scientific figure reviewer. The owner explicitly '
 'requested Claude and authorised reviewing unpublished materials. Use only Read on '
 'the listed paths: no commands, edits, credentials, other file access, delegation or '
 'browser. Visually inspect both PNG figures. Audit the script/data-statistic description '
 'and return at most700 words of actionable conclusions, preserving actual data and '
 'avoiding cosmetic changes that exaggerate effects. Do not invent model fits or metrics.')

def main():
 images=[ROOT/'figures/figure2_contrastive_enhanced.png',
         ROOT/'figures/figure3_backbone_route_error_violins.png']
 paths=images+[ROOT/'make_contrastive.py',ROOT/'make_FT_violins.py',
              ROOT/'figure3_FT_manifest.json',ROOT/'figure3_caption_EN.txt']
 prompt=SYSTEM+'\nTASK: user requests soft pastel figures matching oldFigure1 style, Aptos, '
 prompt+='minimal text and publication readability at180mm. MainDOCXediting belongs to root; '
 prompt+='you cannot modify it. First inspect both PNGs then read scripts as needed. '
 prompt+='Figure2 is a vector-source restyle of221markers/panel (172Bad,49Good), not rerunembeddings. '
 prompt+='SourcePDF prints .007→.107, while authorv5raster prints .007→.108; root maintains the discrepancy openly. '
 prompt+='Do not imply alignedtsneaxes, newheldoutmolecules or causalproof of a classsplit. '
 prompt+='Figure3 uses real per-molecule×endpoint absolute prediction errors across SAMEthree runs0–2, '
 prompt+='averaged within endpoint BEFOREviolin:420values(cation/scaffold),67OODexact. NoKDEover3RMSE, '
 prompt+='not error of ensembleprediction, not1260independentseedresiduals. OODboundIT505EcMBC>500 retained '
 prompt+='elsewhere, notplottedasexact. Commonlinear0–8.05 axes, all actualtails max7.34 retained. '
 prompt+='Whitepoints median,graybarIQR; OODjitterpoints individual67endpoint summaries. '
 prompt+='Routes frozenhead, LoRA, fullFT from pretrained; humanpartialdirect targetfinetuning vs '
 prompt+='sourcehumanpartialfrozen→CatBoost use same3sourcecheckpoints, not samefinalmodel. '
 prompt+='Thesehumanmodels are NOTv5externalcompactMLP. Comparison is practicalpipeline, capacity/objective '
 prompt+='differ; cannot claim universalFTbad,smalladapterbetter or humansemanticcausality. '
 prompt+='Whole-runRMSE±sampleSD3run recomputed separatelyfrompredictions, noSDbars/CIshowninviolins. '
 prompt+='Please judge hierarchy, visualsoftness, typographyat180mm, labelspacing, clearmeaningandcaption. '
 prompt+='Recommend only material fixes; ifalreadyacceptable sayso. Explain any source/statistic ambiguity.\nPERMITTED FILES\n'
 prompt+='\n'.join(map(str,paths))
 (REV/'claude_figures_prompt.txt').write_text(prompt)
 command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet','--tools','Read',
  '--allowed-tools','Read','--permission-mode','dontAsk','--no-session-persistence',
  '--disable-slash-commands','--no-chrome','--setting-sources','','--strict-mcp-config',
  '--mcp-config','{"mcpServers":{}}','--system-prompt',SYSTEM,'--output-format','stream-json',
  '--verbose','--max-budget-usd','3']
 rec=dict(actual_reviewer='Claude CLI',execution='local Mac',authorised=True,completed=False,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
  files_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
 start=time.time()
 try:
  with (REV/'claude_figures_raw.jsonl').open('w') as out,(REV/'claude_figures_stderr.log').open('w') as err:
   result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=420)
  events=[]
  for line in (REV/'claude_figures_raw.jsonl').read_text().splitlines():
   try:events.append(json.loads(line))
   except json.JSONDecodeError:pass
  last={};calls=[]
  for event in events:
   if event.get('type')=='result':last=event
   for block in event.get('message',{}).get('content',[]):
    if isinstance(block,dict) and block.get('type')=='tool_use':
     calls.append(dict(name=block.get('name'),input=block.get('input')))
  review=last.get('result','')
  read_paths={c['input'].get('file_path') for c in calls if c['name']=='Read'}
  rec.update(returncode=result.returncode,tool_calls=calls,model_usage=last.get('modelUsage'),
   cost_usd=last.get('total_cost_usd'),visually_read_both_figures=all(str(p) in read_paths for p in images))
  if result.returncode==0 and review and not last.get('is_error'):
   (REV/'claude_figures_review.txt').write_text(review);rec['completed']=True
 except subprocess.TimeoutExpired:rec['status']='timeout'
 rec['seconds']=time.time()-start
 (REV/'claude_figures_process.json').write_text(json.dumps(rec,indent=2))
 print(json.dumps({k:rec[k] for k in ['completed','seconds']}))
if __name__=='__main__':main()
