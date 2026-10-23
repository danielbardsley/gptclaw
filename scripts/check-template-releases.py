#!/usr/bin/env python3
"""Validate bundled releases and refuse changes to an existing baseline release."""
import argparse
import hashlib
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
    indexed = subprocess.run(['git','ls-files','--stage','-z'],cwd=repo,capture_output=True,check=True).stdout
    tracked = {}
    for record in indexed.split(b'\0'):
        if not record: continue
        metadata, name = record.split(b'\t',1)
        mode, blob, stage = metadata.split()
        if stage == b'0': tracked[name.decode()] = blob.decode()
    algorithm = subprocess.run(['git','rev-parse','--show-object-format'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip()
    templates.check(algorithm in {'sha1','sha256'})
    for (name, version), (release, contents) in releases.items():
        for item in release['files']:
            rel = (Path('templates/apps/releases')/name/version/item['source']).as_posix()
            content = contents[item['output']]
            blob = hashlib.new(algorithm,b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
            # A clean local tree must prove that CI will receive these exact bytes.
            templates.check(tracked.get(rel) == blob)
    if exists.returncode: return
    old = {'releases': []}
    for version in (1, 2, 3, 4, 5, 6, 7, 8, 9):
        rel = 'config/templates/v'+str(version)+'.json'
        entry = subprocess.run(['git','show',commit+':'+rel], cwd=repo, capture_output=True)
        if entry.returncode == 0: old['releases'].extend(json.loads(entry.stdout)['releases'])
    if any(release.get('provider')=='expo-v1' for release in old['releases']):
        original=subprocess.run(['git','show',commit+':config/mobile/v1.json'],cwd=repo,capture_output=True,check=True).stdout
        templates.check(original==(repo/'config/mobile/v1.json').read_bytes())
    if any(release.get('provider') in {'expo-dev-v1','expo-dev-notes-v1'} for release in old['releases']):
        original=subprocess.run(['git','show',commit+':config/mobile/v2.json'],cwd=repo,capture_output=True,check=True).stdout
        templates.check(original==(repo/'config/mobile/v2.json').read_bytes())
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
