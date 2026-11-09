"""Wait for another server lane, then launch a dependent job."""
import argparse
import json
from pathlib import Path
import subprocess
import time
ROOT = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--marker', required=True)
    ap.add_argument('--lane', required=True)
    ap.add_argument('command', nargs=argparse.REMAINDER)
    args = ap.parse_args()
    started = time.time()
    while not (ROOT / args.marker).exists():
        status = ROOT / 'status' / (args.lane + '.json')
        if status.exists():
            state = json.loads(status.read_text())
            if state['state'] == 'finished':
                raise RuntimeError('Dependency lane finished without the required marker')
        if time.time() - started > 172800:
            raise TimeoutError('Dependency did not complete in 48 hours')
        time.sleep(30)
    cmd = args.command[1:] if args.command[0] == '--' else args.command
    raise SystemExit(subprocess.call(cmd))


if __name__ == '__main__':
    main()
