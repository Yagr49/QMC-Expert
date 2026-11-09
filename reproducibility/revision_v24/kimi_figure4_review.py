"""Actual Kimi visual/method audit of the proposed integrated Figure4 on Mac."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import time

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'reviews';OUT.mkdir(exist_ok=True)
IMAGE=ROOT/'figures/figure4_human_quantitative_compact.png'
SYSTEM=('You are an independent molecular machine-learning figure reviewer. The researcher '
        'explicitly authorised Kimi review of the unpublished study. Use only ReadMediaFile '
        'on the single listed image; no commands, writes, other reads or delegation. '
        'Inspect the image and give at most400 Russian words of concrete visual and '
        'scientific feedback. Do not invent results or claim causality.')


def main():
    prompt=SYSTEM+'\nTASK: propose refinements to the integrated human vs quantitative schematic '
    prompt+='with classic vertical error violins. Preserve the soft Figure1 style, Aptos,180mm width, '
    prompt+='minimal text inside figures. Assess source-vs-target flow: MolFormer frozen, external MLP '
    prompt+='trained on681 source (377train/304val), applied to105 target QAC embeddings; CatBoost '
    prompt+='is independently fitted for each arm/source seed/target fold under the SAME fixed protocol, '
    prompt+='not one shared fitted model. Five paired source seeds; noSMOTE. Human contrastive vs '
    prompt+='continuous MIC MSE objectives differ. All four endpoints pooled; categorical taskcode '
    prompt+='used in every branch, because shuffled-human text-code predictions do not exist. '
    prompt+='420 true endpoint-wise mean absolute errors per arm/panel across five seeds (raw1fixed); '
    prompt+='never five-RMSE KDE, never ensemble error. Both cation/scaffold holdout, noOOD. '
    prompt+='All points/tails retained; median horizontal/IQRvertical. These new matched compact controls '
    prompt+='do not establish semantic causal superiority; shuffled actually has lower scaffold RMSE. '
    prompt+='Historical Table2 quantitative checkpoint remains missing, so this must never be called its '
    prompt+='reproduction. Original1500/10000source narrative belongs to historical v5, not matched681. '
    prompt+='Suggest only changes materially improving honesty/legibility; avoid adding more text.\n'
    for path in [ROOT/'figure4_caption_EN.txt',ROOT/'figure4_provenance.json',ROOT/'figure4_compact_seed_metrics.csv']:
        prompt+='\nSUPPLIED '+path.name+'\n'+path.read_text()
    prompt+='\nPERMITTED IMAGE (visually inspect):\n'+str(IMAGE)
    (OUT/'kimi_figure4_prompt.txt').write_text(prompt)
    agent=OUT/'kimi_figure4_agent.md'
    agent.write_text('---\nname: compact-figure-reviewer\ndescription: Read-only figure reviewer\ntools:\n  - ReadMediaFile\nsubagents: []\n---\n'+SYSTEM)
    record=dict(reviewer='actual Kimi CLI',execution='local Mac',authorised=True,completed=False,
                started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                figure_sha256=hashlib.sha256(IMAGE.read_bytes()).hexdigest())
    meta=OUT/'kimi_figure4_process.json';meta.write_text(json.dumps(record,indent=2))
    start=time.time()
    try:
        with (OUT/'kimi_figure4_raw.jsonl').open('w') as out,(OUT/'kimi_figure4_stderr.log').open('w') as err:
            result=subprocess.run([str(Path.home()/'.kimi-code/bin/kimi'),'-p',prompt,
                    '--agent-file',str(agent),'--output-format','stream-json'],cwd=ROOT,
                    stdout=out,stderr=err,timeout=360)
        events=[]
        for line in (OUT/'kimi_figure4_raw.jsonl').read_text().splitlines():
            try:events.append(json.loads(line))
            except json.JSONDecodeError:pass
        texts=[];calls=[]
        for event in events:
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
        record.update(returncode=result.returncode,tool_calls=calls)
        if result.returncode==0 and texts and calls:
            (OUT/'kimi_figure4_review.txt').write_text(texts[-1])
            record['completed']=True
    except subprocess.TimeoutExpired:record['status']='Timed out, no completed review claimed'
    record['seconds']=time.time()-start;meta.write_text(json.dumps(record,indent=2))
    print(json.dumps({k:record[k] for k in ['reviewer','completed','seconds']}))


if __name__=='__main__':main()
