#!/usr/bin/env python3
"""Validate bundled releases and refuse changes to an existing baseline release."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_templates as templates


def verify_baseline(baseline):
    repo = templates.app().REPO
    commit = subprocess.run(['git','rev-parse','--verify',baseline+'^{commit}'], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    exists = subprocess.run(['git','cat-file','-e',commit+':config/templates/v1.json'], cwd=repo, capture_output=True)
    current, releases = templates.catalogue()
    if exists.returncode: return
    old = json.loads(subprocess.run(['git','show',commit+':config/templates/v1.json'], cwd=repo, capture_output=True, check=True).stdout)
    for release in old['releases']:
        key = (release['id'],release['version'])
        templates.check(key in releases and releases[key][0] == release)
        base = Path('templates/apps/releases')/key[0]/key[1]
        for item in release['files']:
            rel = base/item['source']
            original = subprocess.run(['git','show',commit+':'+rel.as_posix()], cwd=repo, capture_output=True, check=True).stdout
            templates.check(original == (repo/rel).read_bytes())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--baseline', default='HEAD')
    args = parser.parse_args()
    try:
        verify_baseline(args.baseline)
        print('Template catalogue integrity and baseline release immutability passed.')
    except (templates.app().AppError, subprocess.CalledProcessError, ValueError, OSError):
        print('Template catalogue or baseline release check failed.', file=sys.stderr)
        raise SystemExit(1)
