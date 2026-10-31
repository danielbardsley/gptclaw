"""Fixed creation-time engineering/skill resources; no execution or synchronization."""
import hashlib
import json
import re

ENGINEERING = 'templates/projects/engineering/'
SKILL = '.agents/skills/gptclaw-specification/'
SKILL_FILES = {'SKILL.md', 'assets/spec.md', 'assets/technical-design.md',
               'assets/tasks.md', 'assets/acceptance.md'}
ENGINEERING_FILES = {'README.md', 'python-standards.md', 'mobile-standards.md', 'quality.md', 'android-emulator.md'}
RESOURCES = {**{ENGINEERING + name: 'docs/engineering/' + name for name in ENGINEERING_FILES},
             **{SKILL + name: SKILL + name for name in SKILL_FILES}}
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
Creation provenance records copied sources; it does not prove checks ran.
"""


def payload(read):
    """Read only the fixed reviewed resources through the caller's safe reader."""
    version = read(ENGINEERING + 'VERSION').decode().strip()
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('Invalid engineering bundle version')
    files = {target: read(source) for source, target in sorted(RESOURCES.items())}
    if any(not data.strip() for data in files.values()):
        raise ValueError('Empty project guidance resource')
    record = {'schema_version': 1, 'bundle': 'engineering', 'version': version,
              'source_repository': 'https://github.com/danielbardsley/gptclaw',
              'files': {target: {'source': source,
                        'sha256': hashlib.sha256(files[target]).hexdigest()}
                        for source, target in sorted(RESOURCES.items())}}
    return files, record


def validate_inventory(root):
    """Reject additions that have not been included in the reviewed copy contract."""
    expected = set(RESOURCES) | {ENGINEERING + 'VERSION'}
    actual = set()
    for prefix in (ENGINEERING, SKILL):
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


def install(stage, read, project_name="New project"):
    """Add guidance to a new private staging tree, refusing output collisions."""
    files, record = payload(read)
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
    record['generated_guidance_sha256'] = hashlib.sha256(root.read_bytes()).hexdigest()
    with (stage / 'docs/starter-guidance-provenance.json').open('x') as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write('\n')
