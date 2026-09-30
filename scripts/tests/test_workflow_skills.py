"""Offline packaging checks, not behavioral proof or a general Markdown parser."""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = {
    'gptclaw-runtime-operation': {'references/operations.md', 'assets/operation-report.md'},
}


def validate(package, resources):
    """Validate our flat frontmatter and recursively discover local resources."""
    def read(path):
        if not path.resolve().is_relative_to(package.resolve()) or path.is_symlink():
            raise ValueError('resource escapes package or is a symlink')
        if not path.is_file():
            raise ValueError('missing resource')
        text = path.read_text(encoding='utf-8')
        if not text.strip():
            raise ValueError('empty resource')
        return text

    entry = read(package / 'SKILL.md')
    match = re.fullmatch(r'---\n(.*?)\n---\n(.+)', entry, re.S)
    if not match:
        raise ValueError('missing metadata or body')
    fields = {}
    for line in match[1].splitlines():
        key, sep, value = line.partition(': ')
        if not sep or key not in {'name', 'description'} or key in fields or not value.strip():
            raise ValueError('invalid metadata')
        fields[key] = value
    if set(fields) != {'name', 'description'} or fields['name'] != package.name:
        raise ValueError('missing or mismatched metadata')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name']) or len(fields['name']) > 64:
        raise ValueError('invalid name')
    if len(fields['description']) > 1024:
        raise ValueError('description too long')
    seen = set()
    pending = [package / 'SKILL.md']
    while pending:
        path = pending.pop()
        text = read(path)
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in link or link.startswith(('#', '/')):
                raise ValueError('expected package-relative file link')
            pending.append(path.parent / link)
    if not {(package / resource).resolve() for resource in resources} <= seen:
        raise ValueError('undiscoverable required resource')


class WorkflowSkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gptclaw-workflow-package-')
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / 'gptclaw-runtime-operation'
        shutil.copytree(ROOT / '.agents/skills' / self.package.name, self.package)
        self.resources = PACKAGES[self.package.name]

    def test_shipped_packages(self):
        for name, resources in PACKAGES.items():
            with self.subTest(name=name):
                validate(ROOT / '.agents/skills' / name, resources)

    def test_missing_resource(self):
        (self.package / 'assets/operation-report.md').unlink()
        with self.assertRaises(ValueError):
            validate(self.package, self.resources)

    def test_duplicate_metadata(self):
        p = self.package / 'SKILL.md'
        p.write_text(p.read_text().replace('---\nname:', '---\nname: duplicate\nname:', 1))
        with self.assertRaises(ValueError):
            validate(self.package, self.resources)

    def test_unlinked_resource(self):
        p = self.package / 'SKILL.md'
        p.write_text(p.read_text().replace('(assets/operation-report.md)', '(references/operations.md)'))
        with self.assertRaises(ValueError):
            validate(self.package, self.resources)

    def test_nested_relative_link(self):
        p = self.package / 'references/operations.md'
        p.write_text(p.read_text() + '\n[Report](../assets/operation-report.md)\n')
        validate(self.package, self.resources)

    def test_cyclic_resource_links_terminate(self):
        p = self.package / 'references/operations.md'
        p.write_text(p.read_text() + '\n[Entry](../SKILL.md)\n')
        validate(self.package, self.resources)

    def test_link_escape(self):
        p = self.package / 'references/operations.md'
        p.write_text(p.read_text() + '\n[Outside](../../outside.md)\n')
        with self.assertRaises(ValueError):
            validate(self.package, self.resources)

    def test_symlink_resource(self):
        p = self.package / 'assets/operation-report.md'
        p.unlink()
        p.symlink_to(self.package / 'SKILL.md')
        with self.assertRaises(ValueError):
            validate(self.package, self.resources)

    def test_document_commands_are_inert(self):
        sentinel = Path(self.temp.name) / 'must-not-exist'
        p = self.package / 'assets/operation-report.md'
        p.write_text(p.read_text() + f'\n```sh\ntouch {sentinel}\n```\n')
        validate(self.package, self.resources)
        self.assertFalse(sentinel.exists())


if __name__ == '__main__':
    unittest.main()
