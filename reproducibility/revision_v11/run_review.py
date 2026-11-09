"""Run an already-authorised, read-only Kimi editorial review."""
from pathlib import Path
import subprocess, json, shutil

ROOT=Path(__file__).resolve().parent
REVIEWS=ROOT/'reviews'
REVIEWS.mkdir(exist_ok=True)
prompt='''You are reviewing a scientific author draft intended for JCIM. Give a read-only editorial and scientific critique. Do not execute commands, access any additional files, edit files, or submit anything. All evidence to review is provided below. The authors explicitly reserved annotation-method fields for coauthors. Treat those fields as intentional and do not invent their contents.

Focus on: unsupported scientific claims; distinctions between direct source-only ranking and target-refitted scaffold CV; unmatched partial fine-tuning versus matched frozen-feature interventions; the human-versus-shuffled control versus incremental value over raw features; the definition of causal intervention; and coherence of the manuscript. Identify only concrete issues with quoted draft wording and a suggested correction. No new numerical results or claims of preregistration, equivalence, universally superior quantitative supervision, human denoising, or independent architecture replication may be inferred. Recommendations for future work must be distinguished from errors in the existing evidence.

The numerical summaries were recomputed from archived results. No new experiments were run during this editorial revision. Annotation and public-archive fields await coauthors. The chemistry appendix preserves available protocols; original spectra are missing from this computational folder and are separately reserved for coauthor completion.

Return a concise review (maximum 800 words), using (1) concrete corrections, (2) remaining limits, (3) positioning for JCIM. Draft follows:

'''+(ROOT/'manuscript_v11_readable.md').read_text()
(REVIEWS/'kimi_v11_prompt.txt').write_text(prompt)
command=[shutil.which('kimi'),'-p',prompt,'--output-format','text']
with (REVIEWS/'kimi_v11_review.txt').open('w') as out,(REVIEWS/'kimi_v11_stderr.log').open('w') as err:
    process=subprocess.run(command,cwd=str(ROOT),stdout=out,stderr=err)
(REVIEWS/'kimi_process.json').write_text(json.dumps({'returncode':process.returncode},indent=2))
print(json.dumps({'kimi_returncode':process.returncode}))
