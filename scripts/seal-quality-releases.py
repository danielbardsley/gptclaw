#!/usr/bin/env python3
"""Seal only unpublished quality releases; never edit a release in the merged base."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_templates as templates

EXCLUDE = {'.local', '.cache', '.expo', 'coverage', '.gptclaw-cache', 'node_modules', '.next', '.venv',
           '__pycache__', '.gptclaw-build', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'dist'}


def seal(root, version, baseline):
    subprocess.run(['git', 'rev-parse', '--verify', baseline+'^{commit}'], cwd=root, check=True, stdout=subprocess.DEVNULL)
    changed = []
    for path in sorted((root/'config/templates').glob('v*.json')):
        c = json.loads(path.read_text()); touched = False
        for release in c['releases']:
            if release['version'] != version:
                continue
            base = root/'templates/apps/releases'/release['id']/version
            rel = base.relative_to(root).as_posix()
            prior = subprocess.run(['git', 'cat-file', '-e', baseline+':'+rel], cwd=root, stderr=subprocess.DEVNULL)
            if prior.returncode == 0:
                raise ValueError('Refusing to reseal a published release: '+rel)
            # Sync the portable runner only into the explicitly selected unpublished release.
            (base/'checks/gptclaw_quality.py').write_bytes((root/'scripts/project_quality_core.py').read_bytes())
            if release['id'] in {'nextjs', 'fastapi', 'fastify'}:
                (base/'checks/browser.cjs').write_bytes((root/'templates/quality/v1/browser.cjs').read_bytes())
            outputs = {x['source']: x['output'] for x in release['files']}
            records = []
            for directory, names, entries in os.walk(base, followlinks=False):
                names[:] = sorted(x for x in names if x not in EXCLUDE)
                for name in sorted(entries):
                    file = Path(directory)/name
                    if file.suffix in {'.pyc', '.tsbuildinfo'} or file.name in {'.coverage', 'coverage.json'}:
                        continue
                    if file.is_symlink():
                        raise ValueError('Symlink in unpublished release')
                    source = file.relative_to(base).as_posix()
                    # Release-owned inert backend placeholders are starter source;
                    # generated project bindings never belong in this tree.
                    records.append({'source': source, 'output': outputs.get(source, source), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
            release['files'] = sorted(records, key=lambda x:x['source'])
            release['digest'] = templates.digest({k:v for k,v in release.items() if k != 'digest'})
            changed.append(release['id']+'@'+version); touched = True
        if touched:
            path.write_text(json.dumps(c, indent=2)+'\n')
    if not changed:
        raise ValueError('No matching unpublished releases')
    print(json.dumps({'sealed': changed, 'baseline': baseline}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    p.add_argument('--version', required=True);p.add_argument('--baseline', required=True)
    args = p.parse_args();seal(Path(__file__).resolve().parents[1], args.version, args.baseline)
