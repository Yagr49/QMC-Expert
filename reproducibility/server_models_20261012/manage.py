"""Inspect server queues or download a result snapshot, without API calls."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
HOST = 'yagr@100.76.26.71'
REMOTE = '/home/yagr/coma_models_check_20261012'
STATUS_CODE = '''
from pathlib import Path
import json, subprocess
root = Path('/home/yagr/coma_models_check_20261012')
result = {}
for lane in ['gpu','core_cpu','tabular_cpu']:
    path = root / 'status' / (lane + '.json')
    if path.exists(): result[lane] = json.loads(path.read_text())
result['units'] = subprocess.check_output(['systemctl','--user','show',
    'coma-models-20261012-gpu','coma-models-20261012-cpu','coma-models-20261012-tabular',
    '-p','Id','-p','ActiveState','-p','MainPID'], text=True)
result['linger'] = subprocess.check_output(['loginctl','show-user','yagr','-p','Linger'], text=True).strip()
print(json.dumps(result, indent=2))
'''
COLLECT_CODE = '''
from pathlib import Path
import datetime as dt, json, tarfile
root = Path('/home/yagr/coma_models_check_20261012')
stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
output = root / ('results_' + stamp + '.tar.gz')
directories = ['status','logs','core_frozen','core_ft','core_v14','retrained_v14','new_baselines']
files = []
for directory in directories:
    for p in (root / directory).rglob('*'):
        if p.is_file() and not p.is_symlink() and p.suffix in ['.csv','.json','.log','.md','.py']:
            files.append(p)
for p in root.glob('*'):
    if p.is_file() and p.suffix in ['.py','.md','.json']: files.append(p)
for p in (root / 'envs').glob('*_freeze.txt'): files.append(p)
with tarfile.open(output, 'w:gz') as tar:
    for p in files: tar.add(p, arcname=str(p.relative_to(root)), recursive=False)
print(json.dumps(dict(archive=str(output), files=len(files), bytes=output.stat().st_size)))
'''


def ssh(code):
    return subprocess.check_output(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                    HOST, '/home/yagr/anaconda3/bin/python', '-'], input=code, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['status', 'collect'])
    args = ap.parse_args()
    if args.action == 'status':
        status = json.loads(ssh(STATUS_CODE))
        (ROOT / 'LATEST_STATUS.json').write_text(json.dumps(status, indent=2))
        print(json.dumps(status, indent=2))
        return
    record = json.loads(ssh(COLLECT_CODE))
    if not re.fullmatch(re.escape(REMOTE) + r'/results_\d{8}T\d{6}Z\.tar\.gz', record['archive']):
        raise ValueError('Unexpected snapshot path')
    archive = ROOT / Path(record['archive']).name
    subprocess.run(['scp', HOST + ':' + record['archive'], str(archive)], check=True)
    dest = ROOT / archive.name[:-7]
    dest.mkdir(exist_ok=False)
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar.getmembers():
            resolved = (dest / member.name).resolve()
            if not member.isfile() or dest.resolve() not in resolved.parents:
                raise ValueError('Unexpected archive member')
        for member in tar.getmembers():
            target = dest / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, open(target, 'wb') as output:
                shutil.copyfileobj(source, output)
    print('Downloaded snapshot:', dest)
    print('Check status/*.json: an active queue means the snapshot contains partial results.')


if __name__ == '__main__':
    main()
