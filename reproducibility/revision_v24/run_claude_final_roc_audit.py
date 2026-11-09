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
 images=[ROOT/'figures/figure4_human_quantitative_compact.png',
         ROOT/'figures/figure5_qhero_real_roc.png']
 paths=images+[ROOT/'make_human_quantitative.py',ROOT/'make_qhero_roc.py',
  ROOT/'figure4_caption_EN.txt',ROOT/'figure5_caption_EN.txt',
  ROOT/'figure4_provenance.json',ROOT/'figure5_provenance.json',ROOT/'SECTION_2_2_EN.md']
 prompt=SYSTEM+'\nTASK: final visual and scientific check of final600dpi Figures4and5 and Section2.2 text. '
 prompt+='ActualClaude previously accepted verticalFTFigure3. Your earlierFigure4 findings werefixed: '
 prompt+='Ylabelnow Meanabsoluteerror, explicit sourceencoderfrozenbeforetargetdecodertraining,600dpiPNG. '
 prompt+='Please actually readbothPNG, bothcaptions andSection2.2EN, scripts/provenanceasneeded. '
 prompt+='Figure4 common681source/externalcompactMLP768→512→384→256,5pairedseeds,noSMOTE; '
 prompt+='actual420molecule×endpoint error means across5runsforhuman/quant/shuffle,Rawonefixedfit. '
 prompt+='IndependentCatBoostfits perrepresentation/seed/targetfold undercommonrecipe. '
 prompt+='HumancontrastivevscontinuousMIC/MSEobjectiveDIFFER,shuffledcontrolnull/unfavourable. '
 prompt+='ThisNEWmatchedfollow-upnotmissinghistoricalfullquantTable2checkpoint. '
 prompt+='Figure5 COMPLETEDQ-HEROclassification405cleanmolecules,360active45inactive,SaMIC≤8uM. '
 prompt+='Randomholdout324train/81test(72positive9negative),scaffoldpooledOOF405across5folds29scaffolds. '
 prompt+='Fivepairedsource/decoderseeds0–4 human/quant/shuffled PARTIALBACKBONE featureguidance, '
 prompt+='notFigure4externalcompactMLP. Sourcetraining681 excludesALLtargetsaltsandcations. '
 prompt+='NewCatBoostclassifier istrainedonQHEROtargettrainfolds,notzero-shotprediction. '
 prompt+='Actualempiricalper-seedROCaveragedpointwise;SDbands sampleddof1acrossseeds,NOTCI, '
 prompt+='NOTensembleprobabilities,andnoAUROC inferredfromaGaussian. RawanddashedRF35arefixedseed0. '
 prompt+='Faintchance diagonal shouldnot be confusedwithdashedblueRF35, legendidentifiesboth. '
 prompt+='Commoncleanedcohort referenceRF35usespublishedauthorarchitecture refittedsame405andfolds, '
 prompt+='NOTclaimofbeatingpublished421-roworiginalrandomtest. '
 prompt+='ScaffoldAUROCmean±sampleSD:Human.6755±.0332,Quant.7156±.0103,Shuffle.5674±.0703; '
 prompt+='Raw.5947,RF35.5651. Pairedconditionalbootstrap(source/decoderseedsand29scaffoldclusters, '
 prompt+='2000draws,noHPO/modelrefits) Human−shuffle+.1081CI[.0305,.2370], '
 prompt+='Human−quant−.0401CI[−.0876,.0269],Human−RF+.1104CI[.0262,.2012]. '
 prompt+='Noformalhumanquant_equivalence,uniqueindependenthumaninformationchannelorbiologicalcausality. '
 prompt+='RandomHuman−RFCIincludes0;scaffoldresultcannotgeneraliseallregimes. '
 prompt+='CurrentuserexplicitlyauthorisedQHEROmainexternalsubsection,revokingolderchat-onlyrestriction. '
 prompt+='Rootplacedthisasanadditionalbenchmark,last2paragraphs,not105QACcentralresults. '
 prompt+='Section2.2retainsoriginalv5highreportedR2(notCVmeans) andnewrowCVmeans±foldSDseparately. '
 prompt+='HistoricalTables1–2movedSI;fullquantcheckpointnotlocated. NoODS/OODresultsin2.1; '
 prompt+='original2.3retained. NoDOCXeditsbyyou. '
 prompt+='Outputatmost500words: finalPNGvisualreadverdict +mandatorymaterialfixesonly +textstatisticalscopes. '
 prompt+='Distinguishalreadyfixedissuesfromremainingones,donotrepeatstaledpi360finding.\nPERMITTED FILES\n'
 prompt+='\n'.join(map(str,paths))
 (REV/'claude_final_roc_prompt.txt').write_text(prompt)
 command=[str(Path.home()/'.local/bin/claude'),'-p',prompt,'--model','sonnet','--tools','Read',
  '--allowed-tools','Read','--permission-mode','dontAsk','--no-session-persistence',
  '--disable-slash-commands','--no-chrome','--setting-sources','','--strict-mcp-config',
  '--mcp-config','{"mcpServers":{}}','--system-prompt',SYSTEM,'--output-format','stream-json',
  '--verbose','--max-budget-usd','3']
 rec=dict(actual_reviewer='Claude CLI',execution='local Mac',authorised=True,completed=False,
  started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
  files_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths});start=time.time()
 try:
  with (REV/'claude_final_roc_raw.jsonl').open('w') as out,(REV/'claude_final_roc_stderr.log').open('w') as err:
   run=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=420)
  events=[]
  for line in (REV/'claude_final_roc_raw.jsonl').read_text().splitlines():
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
   (REV/'claude_final_roc_review.txt').write_text(answer);rec['completed']=True
 except subprocess.TimeoutExpired:rec['status']='timeout'
 rec['seconds']=time.time()-start
 (REV/'claude_final_roc_process.json').write_text(json.dumps(rec,indent=2));print(json.dumps({k:rec[k] for k in ['completed','seconds']}))

if __name__=='__main__':main()
