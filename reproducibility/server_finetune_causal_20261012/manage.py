"""Read status or collect research outputs; never transmit API credentials."""
from pathlib import Path
import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
REMOTE = '/home/yagr/coma_finetune_causal_20261012'
HOST = 'yagr@100.76.26.71'
STATUS = '''
from pathlib import Path
import json,subprocess
r=Path('/home/yagr/coma_finetune_causal_20261012')
status={}
for name in ['direct','ablation']:
 status[name]={'chunks':len(list((r/name/'chunks').glob('*.csv')))}
 status[name]['workers']=[json.loads(p.read_text()) for p in (r/name/'status').glob('*.json')]
p=r/'ablation/vector_status.json'
if p.exists():status['vectors']=json.loads(p.read_text())
p=r/'checkpoint_replay.json'
if p.exists():status['checkpoint_replay']=json.loads(p.read_text())
status['units']=subprocess.check_output(['systemctl','--user','show']+['coma-ftcausal-20261012-'+n for n in ['direct0','direct1','vectors','decode0','decode1','decode2','decode3','verify']]+['-p','Id','-p','ActiveState','-p','SubState','-p','ExecMainStatus'],text=True)
status['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],text=True).strip()
status['log_tail']={p.name:p.read_text(errors='replace').splitlines()[-4:] for p in (r/'logs').glob('*.log')}
print(json.dumps(status,indent=2))
'''
COLLECT = '''
from pathlib import Path
import datetime as dt,json,tarfile
r=Path('/home/yagr/coma_finetune_causal_20261012')
name='snapshot_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
paths=[p for p in r.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix in ['.csv','.json','.log','.md','.py','.npy'] and 'smoke_' not in str(p.relative_to(r)) and 'snapshot_' not in str(p.relative_to(r))]
out=r/(name+'.tar.gz')
with tarfile.open(out,'w:gz') as t:
 for p in paths:t.add(p,arcname=str(p.relative_to(r)),recursive=False)
print(json.dumps({'archive':str(out),'files':len(paths),'bytes':out.stat().st_size}))
'''


def ssh(code):
    return subprocess.check_output(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST,
               '/home/yagr/anaconda3/bin/python', '-'], input=code, text=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['status', 'collect'])
    args = p.parse_args()
    if args.action == 'status':
        value = json.loads(ssh(STATUS))
        (ROOT / 'LATEST_STATUS.json').write_text(json.dumps(value, indent=2))
        print(json.dumps(value, indent=2))
        return
    record = json.loads(ssh(COLLECT))
    assert re.fullmatch(re.escape(REMOTE) + r'/snapshot_\d{8}T\d{6}Z\.tar\.gz', record['archive'])
    path = ROOT / Path(record['archive']).name
    subprocess.run(['scp', HOST + ':' + record['archive'], str(path)], check=True)
    dest = ROOT / path.name[:-7]
    dest.mkdir(exist_ok=False)
    with tarfile.open(path) as t:
        for member in t.getmembers():
            assert member.isfile() and dest.resolve() in (dest / member.name).resolve().parents
        for member in t.getmembers():
            target = dest / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with t.extractfile(member) as source, open(target, 'wb') as output:
                shutil.copyfileobj(source, output)
    print(dest)


if __name__ == '__main__':
    main()
