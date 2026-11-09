"""Actual Claude final visual audit of vertical FT and compact-source figures."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews';REV.mkdir(exist_ok=True)
SYSTEM=('You are an independent scientific figure auditor. The owner explicitly requested '
 'Claude and authorised sharing unpublished materials. Use Read only on the listed files; '
 'no commands, edits, credentials, delegation or other access. Visually inspect both PNGs '
 'before answering. At most600 words; prioritise concrete material issues. Preserve all '
 'actual data and do not invent fits, evidence, numerical intervals or curves.')

def main():
 images=[ROOT/'figures/figure3_backbone_route_error_violins.png',
         ROOT/'figures/figure4_human_quantitative_compact.png']
 paths=images+[ROOT/'make_FT_violins.py',ROOT/'make_human_quantitative.py',
  ROOT/'figure3_caption_EN.txt',ROOT/'figure4_caption_EN.txt',
  ROOT/'figure3_FT_manifest.json',ROOT/'figure4_provenance.json']
 prompt=SYSTEM+'\nTASK: user requests classical VERTICAL violins, upright short labels, '
 prompt+='Aptos and pleasant pastel palette at180mm. ActualClaude already proposed Figure4 '
 prompt+='layout; your erroneous proposedYrange1.5–2.6 was rejected because it was based on '
 prompt+='RMSEmeans, not endpoint-error distributions. No tail clipping is allowed. '
 prompt+='Please actually inspect both final PNGs, then scripts/captions/manifests as needed. '
 prompt+='Figure3: two panels ONLY Cation/Scaffold, five routes onX, meanabsoluteerror OVER3 '
 prompt+='runs within EACHmolecule×endpoint onY,420values perroute/panel. Median/IQR. '
 prompt+='Frozenhead/LoRA/fullFT frompretrained; humanpartialdirect/frozenhumanpartial→CB '
 prompt+='share sourcecheckpointinitialisation,notfinalweights; THESEARENOTv5externalcompactMLP. '
 prompt+='PrimaryFigure3containsNOOOD; separateOODartifact preparedforfuture2.3 andnotinserted. '
 prompt+='Figure4: top sourceguidance schematic human vscontinuousMIC externalcompactencoders '
 prompt+='768→512→384→256 afterfrozenMolFormer; same681source/377train304val;5pairedsource '
 prompt+='seeds/noSMOTE. ContrastiveHuman andregression/MSEquantobjectives DIFFER. '
 prompt+='Common quantitativeCatBoostrecipe BUT independently trained decoder perrepresentation, '
 prompt+='source-seed/fold. Decoder learns105targetQAC trainfoldlabels,NOT681sourceMIC/zero-shot. '
 prompt+='Encoders trainedonsources applied to105targetstructures; samefourMIC/MBCtasks and '
 prompt+='cation/scaffoldgroupedfolds. Bottom actual420endpoint means over5source runs for '
 prompt+='human/quant/shuffledhuman; Rawonefixedrepresentation reference,not5source runs. '
 prompt+='Not ensembleerror,notKDEof5RMSE,not2100independentrepetitions. Alltails retained. '
 prompt+='This NEWmatched681compactv5architecturefollow-up differs from originalSMOTEv5reference '
 prompt+='and from the missing historicalfull-quantmultitargetcheckpoint ofTable2 movedtoSI. '
 prompt+='No claimhumansemanticsbeats shuffled: compactcontrolnull/unfavourable. Noformal '
 prompt+='equivalence/binarylabelreplacementrate/biologicalcausalclaim fromviolinshapes. '
 prompt+='NoOODinFigure4scientificpanels. MainDOCXandSIhandledbyroot;you cannotmodify. '
 prompt+='Requiredcaptionclarity: sourceguidance ends beforetargetdecodertraining, humanpartial '
 prompt+='backboneFig3 vs externalcompactFig4, rawfixedfit vs5source runs, samplecounts and '
 prompt+='historicalcheckpointdistinction. Suggestonlymaterial fixes, markacceptableifready.\nPERMITTED FILES\n'
 prompt+='\n'.join(map(str,paths))
 (REV/'claude_vertical_prompt.txt').write_text(prompt)
 command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet','--tools','Read',
  '--allowed-tools','Read','--permission-mode','dontAsk','--no-session-persistence',
  '--disable-slash-commands','--no-chrome','--setting-sources','','--strict-mcp-config',
  '--mcp-config','{"mcpServers":{}}','--system-prompt',SYSTEM,'--output-format','stream-json',
  '--verbose','--max-budget-usd','3']
 rec=dict(actual_reviewer='Claude CLI',execution='local Mac',authorised=True,completed=False,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
  files_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths});start=time.time()
 try:
  with (REV/'claude_vertical_raw.jsonl').open('w') as out,(REV/'claude_vertical_stderr.log').open('w') as err:
   run=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=420)
  events=[]
  for line in (REV/'claude_vertical_raw.jsonl').read_text().splitlines():
   try:events.append(json.loads(line))
   except json.JSONDecodeError:pass
  last={};calls=[]
  for e in events:
   if e.get('type')=='result':last=e
   for block in e.get('message',{}).get('content',[]):
    if isinstance(block,dict) and block.get('type')=='tool_use':calls.append(dict(name=block.get('name'),input=block.get('input')))
  read_paths={c['input'].get('file_path') for c in calls if c['name']=='Read'}
  rec.update(returncode=run.returncode,tool_calls=calls,model_usage=last.get('modelUsage'),
   cost_usd=last.get('total_cost_usd'),visually_read_both_final_figures=all(str(p) in read_paths for p in images))
  answer=last.get('result','')
  if run.returncode==0 and answer and not last.get('is_error'):
   (REV/'claude_vertical_review.txt').write_text(answer);rec['completed']=True
 except subprocess.TimeoutExpired:rec['status']='timeout'
 rec['seconds']=time.time()-start
 (REV/'claude_vertical_process.json').write_text(json.dumps(rec,indent=2));print(json.dumps({k:rec[k] for k in ['completed','seconds']}))

if __name__=='__main__':main()
