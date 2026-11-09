"""Authorised read-only reviewers; OpenRouter requests run on this computer."""
from pathlib import Path
import argparse, getpass, json, shutil, subprocess
import requests
ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('reviewer',choices=['kimi','claude']);ap.add_argument('--stage',default='protocol',choices=['protocol','manuscript']);args=ap.parse_args()
    out=ROOT/'reviews';out.mkdir(exist_ok=True)
    prompt='''You are an independent read-only reviewer of a QAC molecular ML manuscript. All material below is explicitly authorised for this external review. Do not use tools, execute commands, inspect additional files or invent measurements/annotation methods. Give a concise scientific critique (under 800 words), prioritising concrete defects and fixes. The authors are moving Q-HERO out of the main narrative AFTER inspecting earlier results and centring the original 105 molecules and their named 17-compound structural OOD. This selection must be disclosed. Human annotation methods H1-H7 are reserved for coauthors. Text-embedding-3-small embeds four strain/endpoint descriptions, not molecular activities. No equivalence or biological causal claim should be inferred. Historical encoders saw original-cohort structures; new matched-source encoders excluded all target cations. Evaluate validity of molecule grouping, censored endpoints, task encoding, controls, and bounded conclusions.\n\n'''
    if args.stage=='protocol':
        for name in ['PROTOCOL.md','data/cohort_audit.json','run_comparisons.py']:
            prompt+=name+'\n'+(ROOT/name).read_text()+'\n\n'
    else:
        for name in ['manuscript_v14_readable.md','analysis/summary.csv','analysis/contrasts.csv']:
            prompt+=name+'\n'+(ROOT/name).read_text()+'\n\n'
    stem=f'{args.reviewer}_v14_{args.stage}';(out/(stem+'_prompt.txt')).write_text(prompt)
    if args.reviewer=='kimi':
        command=[str(Path.home()/'.kimi-code/bin/kimi'),'-p',prompt,'--output-format','text']
        with (out/(stem+'_review.txt')).open('w') as f,(out/(stem+'_stderr.log')).open('w') as err:
            p=subprocess.run(command,cwd=str(ROOT),stdout=f,stderr=err)
        metadata=dict(returncode=p.returncode,reviewer='Kimi Code CLI',execution='local computer')
    else:
        key=getpass.getpass('OpenRouter key (hidden): ')
        headers={'Authorization':'Bearer '+key.strip()}
        catalog=requests.get('https://openrouter.ai/api/v1/models',timeout=30).json()['data']
        available={m['id'] for m in catalog}
        model=next((m for m in ['anthropic/claude-sonnet-4.6','anthropic/claude-sonnet-4.5','anthropic/claude-sonnet-4'] if m in available),None)
        assert model is not None,'No requested Claude model in current catalog'
        response=requests.post('https://openrouter.ai/api/v1/chat/completions',headers=headers,
            json={'model':model,'messages':[{'role':'user','content':prompt}],'max_tokens':2000,'temperature':0},timeout=180)
        print('Claude request HTTP status:',response.status_code,flush=True)
        if response.status_code!=200:
            print('Response body omitted; no review recorded.');return
        body=response.json();content=body['choices'][0]['message']['content'];assert content
        (out/(stem+'_review.txt')).write_text(content)
        metadata=dict(reviewer=model,returned_model=body.get('model'),usage=body.get('usage'),execution='local computer',completed=True)
        headers.clear();key=None
    (out/(stem+'_process.json')).write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata))

if __name__=='__main__':main()
