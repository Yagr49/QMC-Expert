"""An explicitly authorised read-only Kimi critique; no autonomous file tools."""
from pathlib import Path
import subprocess, shutil, json, argparse
ROOT=Path(__file__).resolve().parent
REVIEWS=ROOT/'reviews'; REVIEWS.mkdir(exist_ok=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['protocol','manuscript'],default='manuscript');a=ap.parse_args()
    prefix='''Provide a read-only scientific critique. Do not execute commands, access additional files, edit anything or send messages. All evidence is included below. The authors authorised this external internal review. Do not invent annotation votes, methods, agreement, numerical outcomes, equivalence, preregistration or chemical mechanisms. Give at most 700 words: concrete errors with quoted wording and a correction, then material limitations. Distinguish a factual error from an optional follow-up experiment.\n\n'''
    if a.stage=='protocol':
        prompt=prefix+'''Audit source-target leakage, matching of initial weights/batches/updates/stochastic schedules, training-only label transformation and permutation, direct versus target-refit evaluation, and checkpoint reproducibility. Evaluate without inspecting results. A documented clarification preserves native MolFormer stochastic training and recovers final feature-map buffers; assess this separately from changes to training or outcomes.\n\n'''
        for name in ['PROTOCOL.md','PROTOCOL_IMPLEMENTATION_NOTE.md','run_matched_finetuning.py','reconstruct_checkpoints.py']:
            prompt+=name+'\n'+(ROOT/name).read_text()+'\n\n'
    else:
        prompt=manuscript_prompt(prefix)
    name='kimi_v12_'+a.stage
    (REVIEWS/(name+'_prompt.txt')).write_text(prompt)
    command=[shutil.which('kimi'),'-p',prompt,'--output-format','text']
    with (REVIEWS/(name+'_review.txt')).open('w') as out,(REVIEWS/(name+'_stderr.log')).open('w') as err:
        process=subprocess.run(command,cwd=str(ROOT),stdout=out,stderr=err)
    (REVIEWS/(name+'_process.json')).write_text(json.dumps({'returncode':process.returncode},indent=2))
    print(json.dumps({'stage':a.stage,'kimi_returncode':process.returncode}))

def manuscript_prompt(prefix):
    prompt=prefix+'''Review this author draft for JCIM. Human-annotation methods H1–H7 and archive/chemistry fields are intentionally reserved for coauthors. Matched partial fine-tuning is newly executed; older unmatched partial fine-tuning and matched frozen-feature MLP experiments remain separate. Test whether the claims correctly distinguish algorithmic causal interventions, actual human-label benefit over raw features, real-vs-shuffled signal, competition against numerical MIC and direct source-only ranking. The MLP is not an internal LoRA adapter; no general claim that fine-tuning is bad is justified. Intervals are exploratory and unadjusted.\n\n'''+(ROOT/'manuscript_v12_readable.md').read_text()+'\n\nPAIRED QHERO CONTRASTS:\n'
    import pandas as pd
    for name in ['contrasts.csv','direct_contrasts.csv','adaptation_contrasts.csv']:
        d=pd.read_csv(ROOT/'analysis'/name);d=d[d.target=='Q-HERO-405']
        if 'unit' in d:d=d[d.unit=='seed+scaffold']
        prompt+=name+'\n'+d.to_csv(index=False)+'\n'
    return prompt

if __name__=='__main__':main()
