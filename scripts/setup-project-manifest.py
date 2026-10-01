#!/usr/bin/env python3
"""Explicit network setup into a new, user-owned Python environment."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
import venv

PIP_URL = 'https://files.pythonhosted.org/packages/f3/6e/1736e5b4ae2b778ef2f81c47d797de9f891d4d8acb047a24ca37a60294dd/pip-26.2.1-py3-none-any.whl'
PIP_SHA256 = '71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e'
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv', required=True, type=Path)
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        parser.error('setup is supported on Python 3.12')
    # Never update/reuse or remove an uncertain environment on failure.
    destination = args.venv.absolute()
    if destination.exists() or destination.is_symlink():
        parser.error('choose a new environment directory')
    destination.mkdir(parents=False, exist_ok=False)
    try:
        venv.EnvBuilder(with_pip=False).create(destination)
        with tempfile.TemporaryDirectory(prefix='gptclaw-manifest-pip-') as tmp:
            wheel = Path(tmp) / 'pip.whl'
            with urllib.request.urlopen(PIP_URL, timeout=30) as response:
                data = response.read(5 * 1024 * 1024 + 1)
            if hashlib.sha256(data).hexdigest() != PIP_SHA256:
                raise RuntimeError('bootstrap digest mismatch')
            wheel.write_bytes(data)
            subprocess.run([
                str(destination / 'bin/python'), '-I', '-B', '-c',
                'import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); '
                'runpy.run_module("pip",run_name="__main__")', str(wheel),
                '--isolated', 'install', '--disable-pip-version-check', '--no-cache-dir',
                '--only-binary=:all:', '--require-hashes',
                '--index-url', 'https://pypi.org/simple',
                '-r', str(ROOT / 'requirements/project-manifest.txt'),
            ], check=True)
    except Exception:
        print('Setup failed; the new environment is retained for inspection. '
              'Use a new destination to retry.', file=sys.stderr)
        return 1
    print('Environment ready. Activate its bin/activate before validation and checks.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
