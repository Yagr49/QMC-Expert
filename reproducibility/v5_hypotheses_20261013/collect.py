"""Read-only snapshots of the authorised remote experiments (no model bundles)."""
from pathlib import Path
import datetime,json,subprocess,tarfile
ROOT=Path(__file__).resolve().parent
stamp=datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
for name,host in [('main','yagr@100.76.26.71'),('independent','yagr@100.118.123.26')]:
    remote='/home/yagr/coma_v5_hypotheses_20261013'
    archive='/home/yagr/coma_v5_snapshot_'+name+'_'+stamp+'.tar.gz'
    code=r'''
from pathlib import Path
import tarfile,json
root=Path(REMOTE)
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if any(part in ('models','checkpoints','__pycache__') for part in rel.parts):continue
    if p.suffix not in ('.csv','.json','.log','.py','.md','.npy'):continue
    files.append(p)
with tarfile.open(ARCHIVE,'w:gz') as tar:
    for p in sorted(files):tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
for p in root.rglob('status.json'):
    print(str(p.relative_to(root)),p.read_text())
print('Snapshot files',len(files),'bytes',Path(ARCHIVE).stat().st_size)
'''.replace('REMOTE',repr(remote)).replace('ARCHIVE',repr(archive))
    response=subprocess.check_output(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',host,'/home/yagr/anaconda3/bin/python','-'],input=code,text=True)
    dest=ROOT/'snapshots'/name/stamp;dest.mkdir(parents=True,exist_ok=True)
    local=dest/'snapshot.tar.gz'
    subprocess.run(['scp',host+':'+archive,str(local)],check=True)
    with tarfile.open(local,'r:gz') as tar:
        for member in tar.getmembers():
            assert member.isfile() and dest in (dest/member.name).resolve().parents
            target=dest/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(member) as src,target.open('wb') as out:out.write(src.read())
    (dest/'snapshot_record.json').write_text(json.dumps(dict(host=host,utc=stamp,response=response),indent=2))
    (ROOT/(name+'_latest_snapshot.json')).write_text(json.dumps(dict(path=str(dest),utc=stamp),indent=2))
    print(name,response,flush=True)
