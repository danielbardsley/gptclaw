"""Offline checks for this package's deliberately small frontmatter format.

Not a YAML parser, Markdown validator, or test of agent behavior. Links supported
here are ordinary relative inline file links; only package-owned files are read.
"""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2] / '.agents/skills/gptclaw-specification'
ASSETS = {'spec.md', 'technical-design.md', 'tasks.md', 'acceptance.md'}


def validate(package):
    root = package.resolve()

    def read(relative):
        path = package / relative
        if not path.resolve().is_relative_to(root):
            raise ValueError('resource escapes package')
        if not path.is_file():
            raise ValueError('missing resource')
        text = path.read_text(encoding='utf-8')
        if not text.strip():
            raise ValueError('empty resource')
        return text

    source = read('SKILL.md')
    match = re.match(r'\A---\n(.*?)\n---\n(.+)\Z', source, re.S)
    if not match:
        raise ValueError('missing frontmatter or body')
    fields = {}
    for line in match[1].splitlines():
        key, separator, value = line.partition(': ')
        if not separator or key not in {'name', 'description'} or key in fields:
            raise ValueError('invalid package frontmatter')
        fields[key] = value.strip()
    if set(fields) != {'name', 'description'} or not all(fields.values()):
        raise ValueError('missing metadata')
    name = fields['name']
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64 or name != package.name:
        raise ValueError('invalid name')
    if len(fields['description']) > 1024:
        raise ValueError('description too long')
    resources = {f'assets/{name}' for name in ASSETS}
    texts = [source] + [read(path) for path in sorted(resources)]
    links = set()
    for text in texts:
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                raise ValueError('only package-relative file links supported')
            read(target)
            links.add(target)
    if not resources <= links:
        raise ValueError('undiscoverable outline')


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gptclaw-skill-test-')
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / PACKAGE.name
        shutil.copytree(PACKAGE, self.package)

    def edit(self, old, new):
        path = self.package / 'SKILL.md'
        path.write_text(path.read_text().replace(old, new))

    def test_shipped_package(self):
        validate(PACKAGE)

    def test_required_metadata(self):
        self.edit('name: gptclaw-specification\n', '')
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_duplicate_metadata(self):
        self.edit('name: gptclaw-specification', 'name: gptclaw-specification\nname: duplicate')
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_invalid_name(self):
        self.edit('name: gptclaw-specification', 'name: Bad Name')
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_missing_outline(self):
        (self.package / 'assets/spec.md').unlink()
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_empty_outline(self):
        (self.package / 'assets/tasks.md').write_text('  \n')
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_broken_reference(self):
        self.edit('(assets/spec.md)', '(assets/missing.md)')
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_unlinked_outline(self):
        self.edit('[Specification](assets/spec.md)', 'Specification')
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_symlink_escape(self):
        outside = Path(self.temp.name) / 'outside.md'
        outside.write_text('outside fixture')
        target = self.package / 'assets/spec.md'
        target.unlink()
        target.symlink_to(outside)
        with self.assertRaises(ValueError):
            validate(self.package)

    def test_commands_are_not_executed(self):
        sentinel = Path(self.temp.name) / 'must-not-exist'
        with (self.package / 'assets/spec.md').open('a') as output:
            output.write(f'\n```sh\ntouch {sentinel}\n```\n')
        validate(self.package)
        self.assertFalse(sentinel.exists())


if __name__ == '__main__':
    unittest.main()
