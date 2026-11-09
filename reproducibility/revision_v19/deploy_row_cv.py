"""Use the authorised server; reuse immutable v5 inputs, no API calls."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parent;host='yagr@100.76.26.71';remote='/home/yagr/coma_v5_rowcv_20261013'
subprocess.run(['ssh','-o','BatchMode=yes',host,'mkdir','-p',remote],check=True)
subprocess.run(['scp',str(ROOT/'run_row_cv.py'),host+':'+remote+'/run_row_cv.py'],check=True)
code=r'''
from pathlib import Path
import subprocess,json
root=Path('/home/yagr/coma_v5_rowcv_20261013')
assert not (root/'launch.json').exists(),'Existing launch never overwritten'
command=['systemd-run','--user','--unit=coma-v5-rowcv-20261013',
 '--property=WorkingDirectory='+str(root),
 '--property=StandardOutput=append:'+str(root/'run.log'),
 '--property=StandardError=append:'+str(root/'run.log'),
 '/home/yagr/coma_models_check_20261012/envs/baselines/bin/python',str(root/'run_row_cv.py'),
 '--input-root','/home/yagr/coma_v5_hypotheses_20261013','--output-root',str(root/'results')]
response=subprocess.check_output(command,stderr=subprocess.STDOUT,text=True)
record=dict(service='coma-v5-rowcv-20261013',root=str(root),response=response)
(root/'launch.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
'''
result=subprocess.check_output(['ssh','-o','BatchMode=yes',host,'/home/yagr/anaconda3/bin/python','-'],input=code,text=True)
(ROOT/'rowcv_launch.json').write_text(result);print(result)
