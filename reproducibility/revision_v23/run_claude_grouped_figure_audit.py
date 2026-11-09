"""Actual Claude visual/scientific audit on the authorised local Mac."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews';REV.mkdir(exist_ok=True)
SYSTEM=('You are Claude, an independent scientific figure reviewer. The owner explicitly '
 'requested Claude and authorised reviewing unpublished materials. Use only Read on '
 'the listed paths: no commands, edits, credentials, other file access, delegation or '
 'browser. Visually inspect all three listed PNG figures. Audit the script/data-statistic description '
 'and return at most700 words of actionable conclusions, preserving actual data and '
 'avoiding cosmetic changes that exaggerate effects. Do not invent model fits or metrics.')

def main():
 images=[ROOT.parent/'revision_v22/figures/figure3_backbone_route_error_violins.png',
         ROOT/'figures/figure3_backbone_route_error_violins.png',
         ROOT/'figures/figure_OOD_routes_for_section2_3.png']
 paths=images+[ROOT/'make_FT_violins.py',ROOT/'figure3_FT_manifest.json',
              ROOT/'figure3_caption_EN.txt',ROOT/'figure_OOD_caption_EN.txt']
 prompt=SYSTEM+'\nTASK: user explicitly requests removing OOD from Section2.1 and its figure, '
 prompt+='then discussing it separately in Section2.3 later. SourcePNG=v22threepanels. '
 prompt+='NewFigure3=v23two grouped-validation panels (Cation andScaffold),180×88mm. '
 prompt+='NewOODsinglepanel=v23separate105×88mm artifact prepared onlyforfutureSection2.3, NOT inserted intoDOCX. '
 prompt+='Please actually inspect allthreePNGfiles (source,newmain,separateOOD) then script/captions as needed. '
 prompt+='Judge thetwo-panelredesign: softpastelblue/lavender/peach/rose/mint, Aptos, minimalisttext, '
 prompt+='correctly preserved420per-molecule×endpoint summaries per route/panel across SAME3runs0–2. '
 prompt+='Eachendpointstatistic=mean(abs(y−prediction_seed)),not ensembleerror,notKDEover3RMSE, '
 prompt+='not1260independentresiduals. No newfits orchangedlabels. Median/IQR, commontwo-panel0–8.05axes, '
 prompt+='allactualtailsretained. PrimaryFigure3caption must contain NO OOD,67,bounds or OODdot description. '
 prompt+='SeparateOODartifact has67exact summariesandall67faintpoints,IT505EcMBC>500boundretained elsewhere. '
 prompt+='Routesfrozenhead,LoRA,fullFT frompretrained;humandirect vsfrozenhuman→CB sharepartialbackbone '
 prompt+='sourcecheckpoints,not samefinalmodel. TheseareNOTv5externalcompactMLP. Cannot claimparameterisolated '
 prompt+='causalbenefitofhumanknowledgeoruniversalfine-tuningbad. Three-runwhole-RMSEmean±sampleSD '
 prompt+='retainedinseparateanalysisCSV,notdensityuncertaintybars. Root preservesalloriginalv5prose '
 prompt+='andmovesonlynewOODdiscussion tofuture2.3; you cannoteditDOCX. '
 prompt+='Outputatmost500words: actualvisualinspection verdict;onlymaterialstatistic/caption/spacingfixes; '
 prompt+='confirmOODabsentnewmainandkeptstandalone; do not requireaddingOODbackto2.1.\nPERMITTED FILES\n'
 prompt+='\n'.join(map(str,paths))
 (REV/'claude_grouped_prompt.txt').write_text(prompt)
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
  with (REV/'claude_grouped_raw.jsonl').open('w') as out,(REV/'claude_grouped_stderr.log').open('w') as err:
   result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=420)
  events=[]
  for line in (REV/'claude_grouped_raw.jsonl').read_text().splitlines():
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
   cost_usd=last.get('total_cost_usd'),visually_read_all_three_figures=all(str(p) in read_paths for p in images))
  if result.returncode==0 and review and not last.get('is_error'):
   (REV/'claude_grouped_review.txt').write_text(review);rec['completed']=True
 except subprocess.TimeoutExpired:rec['status']='timeout'
 rec['seconds']=time.time()-start
 (REV/'claude_grouped_process.json').write_text(json.dumps(rec,indent=2))
 print(json.dumps({k:rec[k] for k in ['completed','seconds']}))
if __name__=='__main__':main()
