#!/bin/bash
# Waits for the representation-quality run to finish, then runs direct inference.
cd "$(dirname "$0")"
while pgrep -f "run_matrix.py --seeds" > /dev/null; do sleep 30; done
echo "$(date '+%H:%M:%S')  run_matrix finished, starting direct_inference" >> chain.log
/opt/anaconda3/bin/python direct_inference.py --seeds 3 >> direct.log 2>&1
echo "$(date '+%H:%M:%S')  direct_inference exited $?" >> chain.log
