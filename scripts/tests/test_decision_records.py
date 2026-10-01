"""Narrow ADR metadata, index and graph checks; never execute document content.

Only decision Markdown is read. Other local link targets are checked for existence,
not opened. This does not validate approval truth, prose semantics or Git history.
"""
import copy
import datetime
import json
import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SECTIONS = ('Scope', 'Context', 'Alternatives', 'Decision', 'Consequences',
            'Revisit', 'Evidence and follow-up')
STATES = {'Proposed', 'Accepted', 'Rejected', 'Superseded', 'Deprecated'}
ACCEPTED_HISTORY = {'Accepted', 'Superseded', 'Deprecated'}
FIELDS = {'id', 'title', 'status', 'owner', 'recorded_date', 'decision_date',
          'approval_reference', 'supersedes', 'superseded_by', 'replacement_scope',
          'retirement'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def line(value):
    return isinstance(value, str) and bool(value.strip()) and not any(
        ord(c) < 32 or c == '|' for c in value)


def date(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), 'invalid date')
    datetime.date.fromisoformat(value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON field')
        result[key] = value
    return result


def scope_text(record):
    values = []
    for target, scope in sorted(record['replacement_scope'].items()):
        text = f"{target} ({scope['kind']}: {scope['replaced']}"
        if scope['kind'] == 'partial':
            text += f"; remains: {scope['remaining']}"
        values.append(text + ')')
    return ' / '.join(values) or '—'


def index_row(record, filename):
    return (f"| [{record['id']}]({filename}) | {record['title']} | {record['status']} | "
            f"{', '.join(record['supersedes']) or '—'} | "
            f"{', '.join(record['superseded_by']) or '—'} | {scope_text(record)} |")


def validate(directory, repo_root):
    require(not directory.is_symlink() and directory.is_dir(), 'invalid decision directory')
    records, filenames, texts = {}, {}, {}
    paths = sorted(directory.glob('*.md'))
    require(directory / 'README.md' in paths, 'missing decision index')
    for path in paths:
        require(not path.is_symlink() and path.is_file(), 'invalid decision file')
        source = path.read_text(encoding='utf-8')
        texts[path] = source
        if path.name == 'README.md':
            continue
        name = re.fullmatch(r'([0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md', path.name)
        require(name is not None and name[1] != '0000', 'invalid filename')
        blocks = re.findall(r'^```adr-metadata\n(.*?)\n```\s*$', source, re.M | re.S)
        require(len(blocks) == 1, 'expected one metadata block')
        record = json.loads(blocks[0], object_pairs_hook=unique_object)
        require(isinstance(record, dict) and set(record) == FIELDS, 'invalid metadata fields')
        identity = record['id']
        require(identity == name[1] and identity not in records, 'duplicate/mismatched ID')
        require(line(record['title']) and line(record['owner']), 'missing title/owner')
        require(record['status'] in STATES, 'invalid status')
        date(record['recorded_date'])
        if record['status'] == 'Proposed':
            require(record['decision_date'] is None and record['approval_reference'] is None,
                    'proposed record claims disposition')
        else:
            date(record['decision_date'])
            require(line(record['approval_reference']), 'missing approval evidence')
        if record['status'] in {'Superseded', 'Deprecated'}:
            retired = record['retirement']
            require(isinstance(retired, dict) and set(retired) == {'date', 'approval_reference', 'reason'},
                    'missing retirement evidence')
            date(retired['date'])
            require(line(retired['approval_reference']) and line(retired['reason']), 'invalid retirement')
        else:
            require(record['retirement'] is None, 'unexpected retirement')
        for field in ['supersedes', 'superseded_by']:
            values = record[field]
            require(isinstance(values, list) and all(isinstance(v, str) and re.fullmatch(r'[0-9]{4}', v) for v in values), 'invalid relationship IDs')
            require(len(values) == len(set(values)) and identity not in values, 'duplicate/self relationship')
        related = set(record['supersedes'] + record['superseded_by'])
        require(isinstance(record['replacement_scope'], dict) and set(record['replacement_scope']) == related,
                'replacement scope must cover exactly the relationships')
        for scope in record['replacement_scope'].values():
            require(isinstance(scope, dict) and set(scope) == {'kind', 'replaced', 'remaining'}, 'invalid replacement scope')
            require(scope['kind'] in {'full', 'partial'} and line(scope['replaced']), 'missing replacement scope')
            require(line(scope['remaining']) if scope['kind'] == 'partial' else scope['remaining'] is None,
                    'invalid remaining scope')
        if record['status'] not in ACCEPTED_HISTORY:
            require(not related, 'unaccepted relationship')
        require(bool(record['superseded_by']) == (record['status'] == 'Superseded'), 'status/successor mismatch')
        for section in SECTIONS:
            match = re.search(r'^## ' + re.escape(section) + r'\n(.*?)(?=^## |\Z)', source, re.M | re.S)
            require(match is not None and bool(match[1].strip()), f'missing section: {section}')
        records[identity], filenames[identity] = record, path.name
    for identity, record in records.items():
        for direction, opposite in [('supersedes', 'superseded_by'), ('superseded_by', 'supersedes')]:
            for other_id in record[direction]:
                other = records.get(other_id)
                require(other is not None and other['status'] in ACCEPTED_HISTORY, 'missing/unaccepted related record')
                require(identity in other[opposite], 'nonreciprocal relationship')
                require(record['replacement_scope'][other_id] == other['replacement_scope'][identity], 'scope mismatch')
    visiting, visited = set(), set()

    def visit(identity):
        require(identity not in visiting, 'supersession cycle')
        if identity in visited:
            return
        visiting.add(identity)
        for successor in records[identity]['superseded_by']:
            visit(successor)
        visiting.remove(identity)
        visited.add(identity)

    for identity in records:
        visit(identity)
    rows = [text.strip() for text in texts[directory / 'README.md'].splitlines() if text.startswith('| [')]
    expected = {index_row(record, filenames[identity]) for identity, record in records.items()}
    require(len(rows) == len(expected) and set(rows) == expected, 'index mismatch or duplicate')
    for path, source in texts.items():
        for link in re.findall(r'\]\(([^)]+)\)', source):
            parts = urlsplit(link)
            if parts.scheme in {'https', 'http'}:
                continue
            require(not parts.scheme and not parts.netloc and not parts.query, 'unsupported link')
            if not parts.path:
                continue  # Heading anchors are outside this narrow check.
            target = path.parent / unquote(parts.path)
            require(not Path(parts.path).is_absolute() and target.resolve().is_relative_to(repo_root.resolve()), 'link outside repository')
            require(target.is_file(), 'broken local link')
    return records


class DecisionRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gptclaw-adr-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / 'docs/decisions'
        self.directory.mkdir(parents=True)
        self.records = []

    def record(self, identity='0001', status='Accepted'):
        result = dict(id=identity, title='Fixture decision', status=status, owner='Fixture Owner',
                      recorded_date='2026-09-30', decision_date=None if status == 'Proposed' else '2026-09-29',
                      approval_reference=None if status == 'Proposed' else 'Owner fixture approval',
                      supersedes=[], superseded_by=[], replacement_scope={}, retirement=None)
        if status in {'Superseded', 'Deprecated'}:
            result['retirement'] = dict(date='2026-09-30', approval_reference='Owner retirement approval', reason='Changed constraints')
        self.records.append(result)
        return result

    def replace(self, old, new, partial=False):
        old['status'] = 'Superseded'
        old['retirement'] = dict(date='2026-09-30', approval_reference='Owner retirement approval', reason='Successor accepted')
        old['superseded_by'].append(new['id'])
        new['supersedes'].append(old['id'])
        scope = dict(kind='partial' if partial else 'full', replaced='Placement', remaining='Retention' if partial else None)
        old['replacement_scope'][new['id']] = copy.deepcopy(scope)
        new['replacement_scope'][old['id']] = copy.deepcopy(scope)

    def write(self):
        rows = []
        for record in self.records:
            name = record['id'] + '-fixture.md'
            text = '# Fixture\n\n```adr-metadata\n' + json.dumps(record) + '\n```\n'
            text += ''.join(f'\n## {section}\n\nFixture evidence.\n' for section in SECTIONS)
            (self.directory / name).write_text(text)
            rows.append(index_row(record, name))
        (self.directory / 'README.md').write_text('# Decisions\n\n' + '\n'.join(rows) + '\n')

    def check(self):
        return validate(self.directory, self.root)

    def test_shipped_records(self):
        validate(ROOT / 'docs/decisions', ROOT)

    def test_proposed_accepted_rejected_deprecated(self):
        for index, status in enumerate(['Proposed', 'Accepted', 'Rejected', 'Deprecated'], 1):
            self.record(f'{index:04}', status)
        self.write(); self.check()

    def test_multihop_and_partial_supersession(self):
        a, b, c = [self.record(f'{i:04}') for i in range(1, 4)]
        self.replace(a, b, partial=True); self.replace(b, c)
        self.write(); self.check()

    def test_successor_can_later_be_deprecated(self):
        a, b = self.record(), self.record('0002')
        self.replace(a, b)
        b['status'] = 'Deprecated'
        b['retirement'] = dict(date='2026-09-30', approval_reference='Owner deprecation', reason='No longer applicable')
        self.write(); self.check()

    def test_editorial_correction_preserves_identity_and_evidence(self):
        self.record(); self.write()
        before = self.check()
        p = self.directory / '0001-fixture.md'
        p.write_text(p.read_text().replace('Fixture evidence.', 'Clearer fixture evidence.', 1))
        self.assertEqual(before, self.check())

    def test_missing_approval_and_invalid_date(self):
        r = self.record()
        for field, value in [('approval_reference', None), ('decision_date', '2026-02-30')]:
            original = r[field]; r[field] = value; self.write()
            with self.assertRaises(ValueError): self.check()
            r[field] = original

    def test_missing_retirement_evidence(self):
        r = self.record(status='Deprecated'); r['retirement'] = None; self.write()
        with self.assertRaises(ValueError): self.check()

    def test_duplicate_id(self):
        self.record(); self.write()
        p = self.directory / '0001-fixture.md'
        (self.directory / '0001-duplicate.md').write_text(p.read_text())
        with self.assertRaises(ValueError): self.check()

    def test_duplicate_json_key(self):
        self.record(); self.write(); p = self.directory / '0001-fixture.md'
        p.write_text(p.read_text().replace('"id": "0001"', '"id": "0001", "id": "0001"'))
        with self.assertRaises(ValueError): self.check()

    def test_missing_successor(self):
        a, b = self.record(), self.record('0002'); self.replace(a, b); self.records.pop(); self.write()
        with self.assertRaises(ValueError): self.check()

    def test_unaccepted_successor(self):
        a, b = self.record(), self.record('0002', 'Proposed'); self.replace(a, b); self.write()
        with self.assertRaises(ValueError): self.check()

    def test_nonreciprocal_relationship(self):
        a, b = self.record(), self.record('0002'); self.replace(a, b)
        b['supersedes'] = []; b['replacement_scope'] = {}; self.write()
        with self.assertRaises(ValueError): self.check()

    def test_self_and_cycle(self):
        a = self.record(); self.replace(a, a); self.write()
        with self.assertRaises(ValueError): self.check()
        self.records = []
        a, b = self.record(), self.record('0002'); self.replace(a, b); self.replace(b, a); self.write()
        with self.assertRaises(ValueError): self.check()

    def test_partial_scope_required_and_reciprocal(self):
        a, b = self.record(), self.record('0002'); self.replace(a, b, partial=True)
        b['replacement_scope']['0001']['remaining'] = None; self.write()
        with self.assertRaises(ValueError): self.check()
        b['replacement_scope']['0001']['remaining'] = 'Different scope'; self.write()
        with self.assertRaises(ValueError): self.check()

    def test_stale_index_status_and_missing_row(self):
        self.record(); self.write(); p = self.directory / 'README.md'
        p.write_text(p.read_text().replace('Accepted', 'Proposed'))
        with self.assertRaises(ValueError): self.check()
        p.write_text('# Empty index\n')
        with self.assertRaises(ValueError): self.check()

    def test_broken_and_escaping_links(self):
        self.record(); self.write(); p = self.directory / '0001-fixture.md'; original = p.read_text()
        for target in ['missing.md', '../../../outside.md']:
            p.write_text(original + f'\n[Source]({target})\n')
            with self.assertRaises(ValueError): self.check()

    def test_missing_section(self):
        self.record(); self.write(); p = self.directory / '0001-fixture.md'
        p.write_text(p.read_text().replace('## Alternatives', '## Removed'))
        with self.assertRaises(ValueError): self.check()

    def test_symlink_record(self):
        self.record(); self.write(); p = self.directory / '0001-fixture.md'
        outside = self.root / 'outside.md'; p.rename(outside); p.symlink_to(outside)
        with self.assertRaises(ValueError): self.check()

    def test_commands_remain_inert(self):
        self.record(); self.write(); p = self.directory / '0001-fixture.md'; sentinel = self.root / 'should-not-exist'
        p.write_text(p.read_text() + f'\n```sh\ntouch {sentinel}\n```\n')
        self.check(); self.assertFalse(sentinel.exists())


if __name__ == '__main__':
    unittest.main()
