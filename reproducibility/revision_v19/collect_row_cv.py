"""Collect a completed, immutable CV result snapshot from the authorised host."""
from pathlib import Path
import json,subprocess,tarfile
ROOT=Path(__file__).resolve().parent;HOST='yagr@100.76.26.71'
CODE=r'''
from pathlib import Path
import json,tarfile
root=Path('/home/yagr/coma_v5_rowcv_20261013');status=json.loads((root/'results/status.json').read_text())
if status['completed']:
 archive=root/'completed_results.tar.gz'
 if not archive.exists():
  with tarfile.open(archive,'w:gz') as tar:
   for p in sorted((root/'results').rglob('*')):
    if p.is_file():tar.add(p,arcname=str(p.relative_to(root/'results')),recursive=False)
 status['archive']=str(archive)
else:
 status['log_tail']=(root/'run.log').read_text()[-1200:]
print(json.dumps(status))
'''
response=subprocess.check_output(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',HOST,'/home/yagr/anaconda3/bin/python','-'],input=CODE,text=True)
status=json.loads(response);print(json.dumps(status,indent=2))
if status['completed']:
 dest=ROOT/'rowcv_results';dest.mkdir(exist_ok=True);archive=dest/'server_results.tar.gz'
 subprocess.run(['scp',HOST+':'+status['archive'],str(archive)],check=True)
 with tarfile.open(archive,'r:gz') as tar:
  for member in tar.getmembers():
   assert member.isfile() and dest in (dest/member.name).resolve().parents
   p=dest/member.name;p.parent.mkdir(parents=True,exist_ok=True)
   with tar.extractfile(member) as source,p.open('wb') as out:out.write(source.read())
