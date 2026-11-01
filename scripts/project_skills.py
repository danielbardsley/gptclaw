#!/usr/bin/env python3
"""Preview or materialize project-owned skills from the recorded local bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys

PACKAGES = {
    'gptclaw-specification': ('SKILL.md', 'assets/spec.md', 'assets/technical-design.md', 'assets/tasks.md', 'assets/acceptance.md'),
    'gptclaw-session-handover': ('SKILL.md', 'assets/handover.md'),
    'gptclaw-journey-verification': ('SKILL.md', 'assets/journey.md'),
    'gptclaw-runtime-operation': ('SKILL.md', 'references/operations.md', 'assets/operation-report.md'),
    'gptclaw-android-operation': ('SKILL.md', 'references/device.md', 'assets/observation.md'),
    'gptclaw-native-preview': ('SKILL.md', 'references/preview.md', 'assets/preview.md'),
}
COMMON = {'gptclaw-specification', 'gptclaw-session-handover', 'gptclaw-journey-verification'}
CAPABILITIES = {'runtime': {'gptclaw-runtime-operation'},
                'android': {'gptclaw-android-operation'},
                'native-build': {'gptclaw-native-preview'}}
BUNDLE = 'docs/engineering/skills-bundle.json'
SELECTION = '.agents/skills-selection.json'
HELPER = '.agents/materialize-skills.py'
MARKER = '.agents/skills-materialization-in-progress'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    # Match the reviewed templates' default Prettier JSON layout for short arrays.
    text = json.dumps(value, indent=2, sort_keys=True) + '\n'
    pattern = r'(?m)^([ ]*)("[^"\n]+": )\[\n((?:[ ]+"(?:[^"\\]|\\.)*",?\n)+)[ ]*\](,?)$'
    def compact(match):
        items = json.loads('[' + match[3] + ']')
        line = match[1] + match[2] + json.dumps(items) + match[4]
        return line if len(line) <= 80 else match[0]
    return re.sub(pattern, compact, text).encode()


def capabilities(values):
    if not isinstance(values, (list, tuple)) or any(not isinstance(x, str) or x not in CAPABILITIES for x in values):
        raise ValueError('Unknown skill capability')
    result = sorted(set(values))
    if 'native-build' in result and 'android' not in result:
        raise ValueError('native-build requires an explicit android capability')
    return result


def selected(values):
    return sorted(COMMON | set().union(*(CAPABILITIES[c] for c in capabilities(values))))


def inventory():
    return {'.agents/skills/' + name + '/' + rel for name, resources in PACKAGES.items() for rel in resources}


def package_files(bundle, values):
    names = selected(values)
    return {path: item['text'].encode() for path, item in bundle['files'].items()
            if PurePosixPath(path).parts[2] in names}


def validate_bundle(bundle):
    if (not isinstance(bundle, dict) or set(bundle) != {'schema_version', 'version', 'files'}
            or type(bundle['schema_version']) is not int or bundle['schema_version'] != 1
            or not isinstance(bundle['version'], str) or not re.fullmatch(r'\d+\.\d+\.\d+', bundle['version'])
            or set(bundle['files']) != inventory()):
        raise ValueError('Invalid local skill bundle inventory/version')
    for path, item in bundle['files'].items():
        if set(item) != {'text', 'sha256'} or not isinstance(item['text'], str):
            raise ValueError('Invalid skill resource')
        data = item['text'].encode()
        if not data.strip() or len(data) > 65536 or digest(data) != item['sha256']:
            raise ValueError('Skill resource hash/size mismatch: ' + path)
    files = {p: i['text'].encode() for p, i in bundle['files'].items()}
    for name in PACKAGES:
        text = files['.agents/skills/' + name + '/SKILL.md'].decode()
        if not text.startswith('---\nname: ' + name + '\n') or '\ndescription: ' not in text:
            raise ValueError('Invalid skill entry: ' + name)
    validate_links(files)


def validate_links(files):
    """Only package-contained relative links; a package must be independently usable."""
    for name, data in files.items():
        if not name.endswith('.md'):
            continue
        boundary = '/'.join(PurePosixPath(name).parts[:3])
        for target in re.findall(r'\]\(([^)]+)\)', data.decode()):
            if target.startswith('#') or '://' in target:
                continue
            if target.startswith('/'):
                raise ValueError('Absolute skill link')
            resolved = os.path.normpath(str(PurePosixPath(name).parent / target.split('#')[0]))
            if not resolved.startswith(boundary + '/') or resolved not in files:
                raise ValueError('Missing or escaping skill link: ' + name)


def record(bundle_bytes, helper, bundle, values):
    caps = capabilities(values)
    return {'schema_version': 1, 'version': bundle['version'], 'capabilities': caps,
            'packages': selected(caps), 'bundle_sha256': digest(bundle_bytes),
            'helper_sha256': digest(helper),
            'files': {p: digest(b) for p, b in sorted(package_files(bundle, caps).items())}}


def checked_root(value):
    root = Path(os.path.abspath(value))
    for path in [*reversed(root.parents), root]:
        if path.is_symlink():
            raise ValueError('Symlink project ancestor')
    if not root.is_dir():
        raise ValueError('Missing project root')
    return root


def safe_path(root, relative):
    path = root
    for part in PurePosixPath(relative).parts:
        if part in {'..', '/', ''}:
            raise ValueError('Unsafe resource path')
        path = path / part
        if path.is_symlink():
            raise ValueError('Symlink resource: ' + relative)
    return path


def read(root, relative, limit=1048576):
    path = safe_path(root, relative)
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError('Missing or oversized resource: ' + relative)
    return path.read_bytes()


def publish(root, relative, data):
    """Exclusive writes anchored through no-follow directory descriptors."""
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = PurePosixPath(relative).parts
        for part in parts[:-1]:
            try:
                os.mkdir(part, mode=0o755, dir_fd=fd)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        out = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=fd)
        with os.fdopen(out, 'wb') as stream:
            stream.write(data)
    finally:
        os.close(fd)


def materialize(root, values, apply=False):
    root = checked_root(root)
    if safe_path(root, MARKER).exists():
        raise ValueError('Incomplete materialization; preserve files and inspect marker')
    raw = read(root, BUNDLE)
    bundle = json.loads(raw)
    validate_bundle(bundle)
    helper = read(root, HELPER)
    old_raw = read(root, SELECTION)
    old = json.loads(old_raw)
    # Validate the complete active inventory, including adaptations and missing files.
    expected_old = record(raw, helper, bundle, old.get('capabilities'))
    if old != expected_old:
        raise ValueError('Selection provenance or bundle/helper identity mismatch')
    for path, hash_value in old['files'].items():
        if digest(read(root, path, 65536)) != hash_value:
            raise ValueError('Adapted active skill; prepare a reviewed diff: ' + path)
    if not isinstance(values, (list, tuple)):
        raise ValueError('Invalid requested capabilities')
    caps = capabilities([*old['capabilities'], *values])
    new = record(raw, helper, bundle, caps)
    wanted = package_files(bundle, caps)
    additions = {p: data for p, data in wanted.items() if p not in old['files']}
    for name in set(new['packages']) - set(old['packages']):
        package = safe_path(root, '.agents/skills/' + name)
        if package.exists():
            raise ValueError('Skill collision; preserve and prepare a reviewed diff: ' + name)
    for path in additions:
        p = safe_path(root, path)
        if p.exists():
            raise ValueError('Skill collision; preserve and prepare a reviewed diff: ' + path)
    report = {'operation': 'apply' if apply else 'check', 'capabilities': caps,
              'packages': new['packages'], 'add': sorted(additions),
              'status': 'ready' if new != old else 'unchanged'}
    if not apply or new == old:
        return report
    # A retained marker prevents blind retry after any partial publication.
    publish(root, MARKER, encode({'before_sha256': digest(old_raw), 'after': new}))
    for path, data in sorted(additions.items()):
        publish(root, path, data)
    # Recheck selection before atomic replacement; concurrent applies see the marker.
    if read(root, SELECTION) != old_raw:
        raise ValueError('Selection changed during publication; inspect marker')
    temporary = '.agents/skills-selection.next.json'
    publish(root, temporary, encode(new))
    agents_fd = os.open(root / '.agents', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.replace('skills-selection.next.json', 'skills-selection.json', src_dir_fd=agents_fd, dst_dir_fd=agents_fd)
        os.unlink('skills-materialization-in-progress', dir_fd=agents_fd)
    finally:
        os.close(agents_fd)
    report['status'] = 'materialized'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument('--capability', action='append', choices=sorted(CAPABILITIES), default=[])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(materialize(args.project_root, args.capability, args.apply), sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print('Skill materialization stopped: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
