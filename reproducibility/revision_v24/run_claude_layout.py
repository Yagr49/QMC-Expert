"""Actual Claude layout proposal requested by the user, local Mac only."""
from pathlib import Path
import json,hashlib,datetime as dt,subprocess,time
ROOT=Path(__file__).resolve().parent;REV=ROOT/'reviews';REV.mkdir(exist_ok=True)
SYSTEM=('You are an independent scientific figure designer and auditor. The researcher '
 'explicitly requested Claude and authorised sharing unpublished research. Use only supplied '
 'text; no tools, commands, edits or delegation. Give at most600 words: an attractive layout '
 'proposal plus scientific guardrails. Preserve data and distinguish completed follow-ups '
 'from unresolved historical checkpoints.')

def main():
 prompt=SYSTEM+'''\nTASK: propose a coherent Figure4 explaining human vs quantitative guidance with actual scientific data, to accompany v5 Section2.2. User also wants both scientific violin figures vertical/classical, pastel/Aptos180mm, short upright labels, little text. Actual Kimi builds integratedFigure4; your concrete proposal will be forwarded to its agent. Root handles DOCX/SI; no edits byyou.

MAIN Figure3 separate adaptation comparison: two panels Cation/Scaffold, five routes onX and mean absolute error over3runs onY, medians/IQR. Routes frozenhead/LoRA/fullFT/humanpartialdirect/humanpartialfrozen→CB, all420endpoint summaries, targetseeds0–2. Humanpartialbackbone is NOTtheexternalv5compactMLP. OOD remains a separate standalone figure reserved for laterSection2.3.

FIGURE4 SPECIFICATION: top concise explanatory schematic: frozenMolFormer768D → two parallel externalcompactencoders768→512→384→256, trained with humanGood/Bad vscontinuous measuredMIC source signals → shared quantitative CatBoostdecoder/taskcode → SAME105QACtargets/fourMIC-MBCtasks. Bottom actual matched-source grouped error vertical violins: cation andscaffold only, noOOD. Human source andquant source usecommon681molecules, same377train/304validation, sameencoderwidths,5pairedseeds0–4, fixed80epochs480updates, noSMOTE. Encoder remains external; noMolFormerweightsupdated. Human usescontrastiveloss; quantitativecontinuous usesMSE, thus objective changes along with labels. Nativecategorical CB500/depth6/lr.05/seed42, exact420QACendpoints. Human cation/scaffoldRMSE1.872±.034/2.158±.050;quantcontinuous1.858±.031/2.168±.018. Shuffledhumancontrol1.833±.049/2.041±.085: nohumansemanticbenefitresolvedhere. Point values mayinform yourlayout but shouldnot crowdthegraphic. ProposedKimi stem figure4_human_quantitative_compact.

Crucialprovenance: this is availableNEWmatched681-source compact v5-architecturefollow-up (noSMOTE), NOTthe historical fullquantmultitargetmodel inoriginalTable2. That completecheckpoint isnotlocated; originalreported highR²metrics canremaininSIbut arenot the generatedviolin data. Originalv5compactreference wasSMOTEtrained ondifferent source; avoidclaimexactreplay. Nohumanannotationatpredictiontime; humanlabels guide source encoder, then decoder learns quantitative targetlabels. No'binaryhumanlabel equals aMICassay' claim. Sameencoderarchitecture/shareddecoder doesnotmeanalltrainingobjectivesidentical.

Suggest one clear180mm composite: top twoarm schematic and bottom two side-by-side classic vertical violin panels. Decide howbestto include human/shuffledcontrol honestly without overloadinggraphic; optionaltinygraycontrol marker/violin or explicitcaption/reference okay, butcannot hidethenullcontrol. Use lavender/human,mint/quantitative,gray/shuffled fromsoftexistingpalette. Include nolegend-heavyalphabet, nofloatingperformanceboxes; prefer labels/spatialgrouping. Densities usemean absolute error OVERfive source runs WITHINeachmolecule×endpoint, notfive independentRMSEdensities, noterrorofensembleprediction. Endpoints withinmolecules correlated; no significance fromviolinshape. Ifnoaccess topredict arraysyet,suggestonlylayout/guardrails; no inventedcurve.

Output: precisevisualarrangementandshortlabels, howsourceguidance endsbeforetargetdecoder, requiredcaptiondistinctions, smalldesignrisks. Do not claim actualnewfits or draw an invented figure.
'''
 (REV/'claude_layout_prompt.txt').write_text(prompt)
 command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet','--tools','',
  '--permission-mode','dontAsk','--no-session-persistence','--disable-slash-commands','--no-chrome',
  '--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
  '--system-prompt',SYSTEM,'--output-format','json','--max-budget-usd','2']
 rec=dict(actual_reviewer='Claude CLI',execution='local Mac',authorised=True,completed=False,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest());start=time.time()
 try:
  with (REV/'claude_layout_raw.json').open('w') as out,(REV/'claude_layout_stderr.log').open('w') as err:
   run=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=240)
  e=json.loads((REV/'claude_layout_raw.json').read_text());answer=e.get('result','')
  rec.update(returncode=run.returncode,model_usage=e.get('modelUsage'),cost_usd=e.get('total_cost_usd'))
  if run.returncode==0 and answer and not e.get('is_error'):
   (REV/'claude_layout_review.txt').write_text(answer);rec['completed']=True
 except subprocess.TimeoutExpired:rec['status']='timeout'
 rec['seconds']=time.time()-start
 (REV/'claude_layout_process.json').write_text(json.dumps(rec,indent=2));print(json.dumps({k:rec[k] for k in ['completed','seconds']}))

if __name__=='__main__':main()
