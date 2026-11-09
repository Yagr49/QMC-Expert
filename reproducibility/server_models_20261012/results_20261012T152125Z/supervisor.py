"""Server-owned sequential job lanes. No external inference API calls."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False))
    tmp.replace(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lane')
    ap.add_argument('--retry-failed', action='store_true')
    args = ap.parse_args()
    (ROOT / 'status').mkdir(exist_ok=True)
    (ROOT / 'logs').mkdir(exist_ok=True)
    lock = open(ROOT / 'status' / (args.lane + '.lock'), 'w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    plan = json.loads((ROOT / 'jobs.json').read_text())[args.lane]
    status_path = ROOT / 'status' / (args.lane + '.json')
    state = json.loads(status_path.read_text()) if status_path.exists() else {'jobs': {}}
    state.update(lane=args.lane, pid=os.getpid(), started=now(), state='running')
    atomic_json(status_path, state)
    for job in plan:
        name = job['name']
        previous = state['jobs'].get(name, {})
        if previous.get('state') == 'complete' or (previous.get('state') == 'failed' and not args.retry_failed):
            continue
        record = dict(state='running', started=now(), command=job['argv'])
        if previous:
            record['previous_attempts'] = previous.get('previous_attempts', []) + [
                {k: v for k, v in previous.items() if k != 'previous_attempts'}]
        state['jobs'][name] = record
        state['current_job'] = name
        atomic_json(status_path, state)
        env = os.environ.copy()
        env.update(job.get('env', {}))
        # Credentials must never propagate into experiment children.
        for key in ('OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY'):
            env.pop(key, None)
        print(now(), 'START', name, flush=True)
        try:
            with open(ROOT / 'logs' / (name + '.log'), 'a') as log:
                process = subprocess.Popen(job['argv'], cwd=ROOT, env=env,
                                           stdout=log, stderr=subprocess.STDOUT)
                record['pid'] = process.pid
                atomic_json(status_path, state)
                code = process.wait()
            record.update(state='complete' if code == 0 else 'failed', exit_code=code)
        except Exception as exc:
            record.update(state='failed', error=repr(exc))
        record['finished'] = now()
        atomic_json(status_path, state)
        print(now(), record['state'].upper(), name, flush=True)
    state.update(state='finished', finished=now(), current_job=None,
                 failures=sum(j['state'] == 'failed' for j in state['jobs'].values()))
    atomic_json(status_path, state)


if __name__ == '__main__':
    main()
