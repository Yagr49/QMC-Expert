"""Launch authorised standalone research jobs on the supplied servers."""
from pathlib import Path
import argparse,json,subprocess,tarfile
ROOT=Path(__file__).resolve().parent
SERVERS={'main':('yagr@100.76.26.71','/home/yagr/coma_models_check_20261012/envs/baselines/bin/python','all'),
         'independent':('yagr@100.118.123.26','/home/yagr/anaconda3/bin/python','original')}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['package','main','independent']);a=ap.parse_args()
 payload=ROOT/'payload.tar.gz'
 if a.action=='package':
  with tarfile.open(payload,'w:gz') as tar:
   for p in [ROOT/'run_checks.py',ROOT/'PROTOCOL.md']+sorted((ROOT/'data').glob('*')):
    assert p.is_file();tar.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
  print('Payload bytes',payload.stat().st_size);return
 host,python,stage=SERVERS[a.action];remote='/home/yagr/coma_v5_hypotheses_20261013'
 subprocess.run(['scp',str(payload),host+':/home/yagr/coma_v5_hypotheses_20261013.tar.gz'],check=True)
 code=f'''
from pathlib import Path
import tarfile,subprocess,json,signal,os
root=Path({remote!r})
root.mkdir(exist_ok=True)
assert not (root/'launch.json').exists(), 'Existing run is never overwritten'
with tarfile.open('/home/yagr/coma_v5_hypotheses_20261013.tar.gz','r:gz') as tar:
    for member in tar.getmembers():
        assert member.isfile() and root in (root/member.name).resolve().parents
        target=root/member.name
        target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as source,target.open('wb') as dest:dest.write(source.read())
log=root/'run.log'
if {a.action!r}=='main':
    cmd=['systemd-run','--user','--unit=coma-v5-hypotheses-20261013',
         '--property=WorkingDirectory='+str(root),
         '--property=StandardOutput=append:'+str(log),
         '--property=StandardError=append:'+str(log),
         {python!r},str(root/'run_checks.py'),{stage!r}]
    response=subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT)
    record=dict(host={host!r},python={python!r},stage={stage!r},service='coma-v5-hypotheses-20261013',response=response)
else:
    signal.signal(signal.SIGHUP,signal.SIG_IGN)
    with log.open('w') as out:
        process=subprocess.Popen([{python!r},str(root/'run_checks.py'),{stage!r}],cwd=root,
                stdin=subprocess.DEVNULL,stdout=out,stderr=out,start_new_session=True,
                env=dict(os.environ,PYTHONPATH='/home/yagr/coma_v5_cpu_deps_20261013'))
    record=dict(host={host!r},python={python!r},stage={stage!r},pid=process.pid,detached=True)
(root/'launch.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
'''
 result=subprocess.check_output(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',host,
                                 '/home/yagr/anaconda3/bin/python','-'],input=code,text=True)
 (ROOT/(a.action+'_launch.json')).write_text(result);print(result)

if __name__=='__main__':main()
