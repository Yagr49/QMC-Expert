"""Install pinned model packages in task-scoped virtual environments."""
from pathlib import Path
import json
import subprocess
import time
ROOT = Path(__file__).resolve().parent


def run(argv):
    print('RUN', argv, flush=True)
    subprocess.run(argv, check=True, cwd=ROOT)


def main():
    (ROOT / 'envs').mkdir(exist_ok=True)
    (ROOT / 'runtime').mkdir(exist_ok=True)
    (ROOT / 'status').mkdir(exist_ok=True)
    statuses = {}
    python = ROOT / 'envs/baselines/bin/python'
    run(['/home/yagr/anaconda3/envs/polysas/bin/python', '-m', 'venv',
         '--system-site-packages', str(python.parent.parent)])
    constraints = ROOT / 'envs/constraints.txt'
    constraints.write_text('torch==2.6.0\nnumpy==2.2.6\npandas==2.2.3\nscikit-learn==1.7.2\n')
    packages = [('core', ['numpy==2.2.6', 'pandas==2.2.3', 'scikit-learn==1.7.2',
                          'catboost==1.2.10', 'scipy']),
                ('chemprop', ['chemprop==2.3.1']),
                ('autogluon', ['autogluon.tabular[lightgbm,catboost]==1.6.3']),
                ('tabpfn', ['tabpfn==9.1.0'])]
    for name, specifications in packages:
        try:
            run([str(python), '-m', 'pip', 'install', '--no-cache-dir', '-c', str(constraints),
                 *specifications])
            statuses[name] = dict(installed=True)
        except Exception as exc:
            statuses[name] = dict(installed=False, error=repr(exc))
        (ROOT / 'status/baseline_setup.json').write_text(json.dumps(statuses, indent=2))
    # cuik_molmaker_pin links to hashed libraries supplied by the PyPI wheel.
    # The inherited Conda RDKit of the same version does not supply these files.
    run([str(python), '-m', 'pip', 'install', '--no-cache-dir', '--ignore-installed',
         '--no-deps', 'rdkit==2026.3.6'])
    try:
        jax_python = ROOT / 'envs/tabfm/bin/python'
        run(['/home/yagr/anaconda3/envs/tabfm/bin/python', '-m', 'venv',
             '--system-site-packages', str(jax_python.parent.parent)])
        repository = ROOT / 'runtime/tabfm'
        if not repository.exists():
            run(['git', 'clone', '--depth', '1', 'https://github.com/google-research/tabfm.git',
                 str(repository)])
        sha = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
        run([str(jax_python), '-m', 'pip', 'install', '--no-cache-dir', '--no-deps', '-e', str(repository)])
        run([str(jax_python), '-m', 'pip', 'install', '--no-cache-dir',
             'huggingface_hub', 'sentencepiece', 'rdkit==2026.3.6'])
        run([str(jax_python), '-s', '-c', 'from tabfm import TabFMRegressor; print("TabFM import OK")'])
        statuses['tabfm'] = dict(installed=True, git_sha=sha, backend='jax-cpu')
    except Exception as exc:
        statuses['tabfm'] = dict(installed=False, error=repr(exc))
    for name, py in [('baselines', python), ('tabfm', ROOT / 'envs/tabfm/bin/python')]:
        try:
            frozen = subprocess.check_output([str(py), '-m', 'pip', 'freeze'], text=True)
            (ROOT / 'envs' / (name + '_freeze.txt')).write_text(frozen)
        except Exception:
            pass
    statuses['finished_utc_epoch'] = time.time()
    (ROOT / 'status/baseline_setup.json').write_text(json.dumps(statuses, indent=2))
    (ROOT / 'status/baseline_setup.finished').write_text('installation attempts complete\n')
    print('SETUP RESULTS', json.dumps(statuses), flush=True)


if __name__ == '__main__':
    main()
