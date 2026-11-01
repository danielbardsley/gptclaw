"""Fixed creation-time engineering/skill resources; no execution or synchronization."""
import hashlib
import json
import re

import project_skills as skills

ENGINEERING = 'templates/projects/engineering/'
SKILL = '.agents/skills/gptclaw-specification/'
SKILL_FILES = {'SKILL.md', 'assets/spec.md', 'assets/technical-design.md',
               'assets/tasks.md', 'assets/acceptance.md'}
ENGINEERING_FILES = {'README.md', 'python-standards.md', 'mobile-standards.md', 'quality.md', 'delivery.md'}
RESOURCES = {**{ENGINEERING + name: 'docs/engineering/' + name for name in ENGINEERING_FILES},
             **{name: name for name in skills.inventory()},
             'scripts/project_skills.py': skills.HELPER}
SOURCE_PREFIXES = [ENGINEERING, *('.agents/skills/' + name + '/' for name in skills.PACKAGES)]
SOURCE_FILES = ['scripts/project_skills.py']
# Explicit provider metadata, not project/release name matching.
PROVIDER_CAPABILITIES = {
    'nextjs-v1': ['runtime'], 'nextjs-static-v1': ['runtime'],
    'fastify-v1': ['runtime'], 'fastapi-v1': ['runtime'],
    'notes-v1': ['runtime'], 'notes-postgres-v1': ['runtime'],
    'fastapi-postgres-v1': ['runtime'],
    'expo-v1': ['runtime', 'android'], 'expo-notes-v1': ['runtime', 'android'],
    'expo-dev-v1': ['runtime', 'android', 'native-build'],
    'expo-dev-notes-v1': ['runtime', 'android', 'native-build'],
}
APP_TEMPLATES = {
    'templates/projects/planning/docs/README.md.template': 'docs/README.md',
    'templates/projects/planning/docs/platform/features.md.template': 'docs/platform/features.md',
}
ROOT_NOTICE = """

## Inherited engineering standards

Before material implementation, read [the required engineering standards](docs/engineering/README.md)
and every reference applicable to this component's stack. The technical design
and tasks must map them to actual local/CI gates and record justified adaptations
or inapplicable rules with owner and review status. Preserve standards while
removing demos. Use the [local specification skill](.agents/skills/gptclaw-specification/SKILL.md) for planning.
Start at the [documentation index](docs/README.md) for local plans.
Read [working journey priorities](docs/engineering/delivery.md) before planning
material implementation. Start with a bounded demonstration of the principal
journey; defer speculative hardening while retaining required gates.
The [skill selection guide](docs/engineering/skills.md) lists available workflows
and the local preview/apply command for later capability selection.
Creation provenance records copied sources; it does not prove checks ran.
"""


def payload(read, capabilities=()):
    """Read the full fixed bundle, activate only explicitly selected packages."""
    caps = skills.capabilities(capabilities)
    version = read(ENGINEERING + 'VERSION').decode().strip()
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('Invalid engineering bundle version')
    all_files = {target: read(source) for source, target in sorted(RESOURCES.items())}
    if any(not data.strip() or len(data) > 65536 for data in all_files.values()):
        raise ValueError('Empty or oversized project guidance resource')
    bundle = {'schema_version': 1, 'version': version,
              'files': {path: {'text': all_files[path].decode(),
                               'sha256': skills.digest(all_files[path])}
                        for path in sorted(skills.inventory())}}
    skills.validate_bundle(bundle)
    raw = skills.encode(bundle)
    files = {name: content for name, content in all_files.items()
             if not name.startswith('.agents/skills/')}
    files.update(skills.package_files(bundle, caps))
    files[skills.BUNDLE] = raw
    files[skills.SELECTION] = skills.encode(skills.record(raw, all_files[skills.HELPER], bundle, caps))
    files['docs/engineering/skills.md'] = selection_guide().encode()
    record = {'schema_version': 2, 'bundle': 'engineering', 'version': version,
              'source_repository': 'https://github.com/danielbardsley/gptclaw',
              'capabilities': caps, 'packages': skills.selected(caps),
              'source_files': {source: skills.digest(all_files[target])
                               for source, target in sorted(RESOURCES.items())},
              'files': {target: {'sha256': skills.digest(content)}
                        for target, content in sorted(files.items())}}
    return files, record


def selection_guide():
    return """# Project-local skills

Common: specification, session handover/acceptance reconciliation, and journey
verification. Capability `runtime` adds private development runtime operation;
`android` adds existing Android emulator/device operation; `native-build` adds
private Android preview delivery and requires `android`. Capabilities select
instructions, not installed tools or authority to mutate services or upload code.
Catalogue providers select their reviewed capabilities: web/API/static/group
providers use runtime; Expo Go providers add Android operation; development-build
providers also add native preview. A custom mixed stack selects the union explicitly.

When a planning project selects its stack, preview then apply from its root:

```sh
python3 .agents/materialize-skills.py --capability runtime --capability android --capability native-build --check
python3 .agents/materialize-skills.py --capability runtime --capability android --capability native-build --apply
```

Choose only applicable flags. Selection adds packages and never removes them.
The local versioned bundle and helper need no original checkout or network.
Selection provenance records current capabilities and active file hashes in
`.agents/skills-selection.json`; creation provenance remains the original snapshot.
An unchanged retry writes nothing. Adapted active files, unknown collisions or an
in-progress marker stop the operation: preserve files and prepare a reviewed diff;
there is no overwrite, update, reset or repair mode. New unrelated skill packages
remain untouched. Updates to the bundle/helper require a reviewed project change.
Use this helper only in projects created with this bundle; adopting existing
projects is separately scoped. Verify skill discovery/use in a fresh supported
client; files and hashes alone do not prove loading or runtime acceptance.
"""


def validate_inventory(root):
    """Reject additions that have not been included in the reviewed copy contract."""
    expected = set(RESOURCES) | {ENGINEERING + 'VERSION'}
    actual = {name for name in SOURCE_FILES if (root / name).is_file() and not (root / name).is_symlink()}
    for prefix in SOURCE_PREFIXES:
        base = root / prefix
        if not base.is_dir() or base.is_symlink():
            raise ValueError('Missing or unsafe guidance directory: ' + prefix)
        for path in base.rglob('*'):
            if path.is_symlink():
                raise ValueError('Symlink guidance resource')
            if path.is_file():
                actual.add(path.relative_to(root).as_posix())
    if actual != expected:
        raise ValueError('Guidance inventory differs from reviewed allowlist')


def install(stage, read, project_name="New project", capabilities=()):
    """Add guidance to a new private staging tree, refusing output collisions."""
    files, record = payload(read, capabilities)
    # Validate every collision and local skill reference before any publication.
    for name in files:
        path = skills.safe_path(stage, name)
        if path.exists():
            raise FileExistsError('Guidance collision: ' + name)
    for name, content in files.items():
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(content)
    values = {'PROJECT_NAME': project_name, 'PROJECT_OWNER': 'project owner'}
    for source, target in sorted(APP_TEMPLATES.items()):
        template = read(source)
        def replace(match):
            if match[1] not in values:
                raise ValueError('Unknown planning placeholder')
            return re.sub(r'([\\`*_{}\[\]()<>#!|])', r'\\\1', values[match[1]])
        rendered = re.sub(r'\{\{([^{}]+)\}\}', replace, template.decode())
        if '{{' in rendered or '}}' in rendered:
            raise ValueError('Unresolved planning placeholder')
        path = stage / target
        path.parent.mkdir(parents=True, exist_ok=True)
        if target == 'docs/README.md' and path.exists():
            # Keep the release's application documentation and extend its index.
            rendered = path.read_text() + '\n## Product planning\n\n' + rendered.split('\n', 1)[1].lstrip()
            path.write_text(rendered)
        else:
            with path.open('x') as stream:
                stream.write(rendered)
        record['files'][target] = {'source': source,
                                  'source_sha256': hashlib.sha256(template).hexdigest(),
                                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    root = stage / 'AGENTS.md'
    text = root.read_text().rstrip() + '\n\n' + ROOT_NOTICE.lstrip()
    if len(text.encode()) > 8192:
        raise ValueError('Generated guidance exceeds 8 KiB')
    root.write_text(text)
    validate_generated_links(stage, [*files, 'AGENTS.md', 'docs/README.md', 'docs/platform/features.md'])
    record['generated_guidance_sha256'] = hashlib.sha256(root.read_bytes()).hexdigest()
    with (stage / 'docs/starter-guidance-provenance.json').open('xb') as stream:
        stream.write(skills.encode(record))


def validate_generated_links(root, names):
    """Fail creation on missing or escaping local links before publishing its stage."""
    from pathlib import PurePosixPath
    import os
    for name in names:
        if not name.endswith('.md'):
            continue
        for link in re.findall(r'(?<!\\)\]\(([^)]+)\)', (root / name).read_text()):
            if '://' in link or link.startswith('#'):
                continue
            target = os.path.normpath(str(PurePosixPath(name).parent / link.split('#')[0]))
            if target.startswith(('/', '../')) or not skills.safe_path(root, target).is_file():
                raise ValueError('Broken generated guidance link: ' + name + ': ' + link)
