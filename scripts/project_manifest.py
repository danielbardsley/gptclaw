"""Offline project contract validation. No project commands or code are loaded."""
import errno
import json
import math
import os
from pathlib import Path
import re
import stat

import yaml
from jsonschema import Draft202012Validator, validators
from referencing import Registry

MAX_BYTES = 64 * 1024
MAX_DEPTH = 16
MAX_ERRORS = 50
SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'schemas/project/v1.schema.json'
MESSAGES = {
    'input_missing': 'The project manifest or a parent directory is missing.',
    'input_unreadable': 'The project manifest cannot be read.',
    'input_path': 'Use a non-symlink directory path without parent traversal.',
    'input_kind': 'The manifest must be a regular file.',
    'input_size': 'The manifest exceeds the 64 KiB input limit.',
    'input_depth': 'The manifest exceeds the 16-level nesting limit.',
    'parse': 'The manifest must be valid UTF-8 YAML.',
    'yaml_feature': 'Aliases, anchors, explicit tags and merge keys are unsupported.',
    'document': 'Provide exactly one mapping document.',
    'mapping_key': 'Mapping keys must be unique strings.',
    'version': 'Use the supported integer schema_version: 1.',
    'field_required': 'A required field is missing.',
    'field_unknown': 'This object contains unsupported fields.',
    'field_type': 'The field has the wrong type.',
    'field_value': 'The field violates its documented constraint.',
    'usage': 'Supply --project-root DIRECTORY and optionally --json.',
    'setup': 'Validator dependencies or the bundled schema are unavailable or invalid.',
    'internal': 'Validation failed internally; no contract was returned.',
}


def diagnostic(code, path=''):
    return {'code': code, 'path': path, 'message': MESSAGES[code]}


class ManifestError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def failure(code, exit_code=1):
    return ({'valid': False, 'schema_version': None, 'project_id': None,
             'errors': [diagnostic(code)], 'truncated': False}, None, exit_code)


def read_manifest(project_root):
    """Walk with pinned directory descriptors; never follow a symlink or block on FIFO."""
    raw = os.fspath(project_root)
    if not raw or '\x00' in raw or '..' in Path(raw).parts:
        raise ManifestError('input_path')
    parts = Path(os.path.abspath(raw)).parts[1:]
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open('/', directory_flags)
    try:
        for part in (*parts, '.gptclaw'):
            child = os.open(part, directory_flags, dir_fd=parent)
            os.close(parent)
            parent = child
        # Check type before open, then check again on the opened descriptor.
        before = os.stat('project.yaml', dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode):
            raise ManifestError('input_path')
        if not stat.S_ISREG(before.st_mode):
            raise ManifestError('input_kind')
        fd = os.open('project.yaml', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK |
                     os.O_CLOEXEC, dir_fd=parent)
        with os.fdopen(fd, 'rb') as source:
            opened = os.fstat(source.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise ManifestError('input_kind')
            if opened.st_size > MAX_BYTES:
                raise ManifestError('input_size')
            data = source.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ManifestError('input_size')
        return data.decode('utf-8')
    finally:
        os.close(parent)


class JsonLoader(yaml.SafeLoader):
    """YAML syntax with JSON scalar resolution, not YAML 1.1 coercions."""
    yaml_implicit_resolvers = {}


for tag, pattern, first in [
    ('null', r'^(?:null)$', ['n']),
    ('bool', r'^(?:true|false)$', ['t', 'f']),
    ('int', r'^-?(?:0|[1-9][0-9]*)$', list('-0123456789')),
    ('float', r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+(?:[eE][+-]?[0-9]+)?|[eE][+-]?[0-9]+)$', list('-0123456789')),
]:
    JsonLoader.add_implicit_resolver('tag:yaml.org,2002:' + tag, re.compile(pattern), first)


def parse_manifest(text):
    # Event iteration bounds nesting before PyYAML's recursive node composition.
    depth = documents = 0
    for event in yaml.parse(text, Loader=JsonLoader):
        if isinstance(event, yaml.events.AliasEvent) or getattr(event, 'anchor', None) is not None:
            raise ManifestError('yaml_feature')
        if getattr(event, 'tag', None) is not None:
            raise ManifestError('yaml_feature')
        if isinstance(event, yaml.events.DocumentStartEvent):
            documents += 1
            if documents > 1:
                raise ManifestError('document')
        if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
            depth += 1
            if depth > MAX_DEPTH:
                raise ManifestError('input_depth')
        elif isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
            depth -= 1
    if documents != 1:
        raise ManifestError('document')
    loader = JsonLoader(text)
    try:
        node = loader.get_single_node()

        def construct(node):
            if isinstance(node, yaml.nodes.MappingNode):
                result = {}
                for key_node, value_node in node.value:
                    if not isinstance(key_node, yaml.nodes.ScalarNode) or key_node.tag != 'tag:yaml.org,2002:str':
                        raise ManifestError('mapping_key')
                    key = key_node.value
                    if key == '<<':
                        raise ManifestError('yaml_feature')
                    if key in result:
                        raise ManifestError('mapping_key')
                    result[key] = construct(value_node)
                return result
            if isinstance(node, yaml.nodes.SequenceNode):
                return [construct(item) for item in node.value]
            value = loader.construct_object(node)
            if isinstance(value, float) and not math.isfinite(value):
                raise ManifestError('parse')
            return value

        if not isinstance(node, yaml.nodes.MappingNode):
            raise ManifestError('document')
        return construct(node)
    finally:
        loader.dispose()


# JSON Schema permits 1.0 as an integer; this contract deliberately does not.
StrictValidator = validators.extend(Draft202012Validator, type_checker=
    Draft202012Validator.TYPE_CHECKER.redefine('integer', lambda checker, value: type(value) is int))


def load_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    if schema.get('$id') != 'urn:gptclaw:project:v1' or schema.get('type') != 'object':
        raise ValueError('unexpected bundled schema')
    # No network retrieval, even if a future schema mistakenly adds an external ref.
    def check_refs(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ('$ref', '$dynamicRef') and (not isinstance(item, str) or not item.startswith('#')):
                    raise ValueError('nonlocal reference')
                check_refs(item)
        elif isinstance(value, list):
            for item in value:
                check_refs(item)
    check_refs(schema)
    StrictValidator.check_schema(schema)
    return schema, StrictValidator(schema, registry=Registry())


def safe_pointer(parts, schema):
    """Only schema-owned property names and numeric indices enter diagnostics."""
    safe = []
    for part in parts:
        if isinstance(part, str) and part in schema.get('properties', {}):
            safe.append(part)
            schema = schema['properties'][part]
        elif isinstance(part, int) and schema.get('type') == 'array':
            safe.append(str(part))
            prefix = schema.get('prefixItems', [])
            schema = prefix[part] if part < len(prefix) else schema.get('items', {})
        else:
            break
    return ''.join('/' + part.replace('~', '~0').replace('/', '~1') for part in safe)


def validate_project(project_root):
    """Return (public summary, validated mapping or None, exit status).

    Callers must separately establish authorization and a reviewed runtime.
    """
    try:
        try:
            schema, validator = load_schema()
        except Exception:
            return failure('setup', 2)
        document = parse_manifest(read_manifest(project_root))
        version = document.get('schema_version')
        if type(version) is not int or version != 1:
            result, contract, code = failure('version')
            result['errors'][0]['path'] = '/schema_version'
            return result, contract, code
        errors = []
        for error in validator.iter_errors(document):
            code = {'type': 'field_type', 'required': 'field_required',
                    'additionalProperties': 'field_unknown'}.get(error.validator, 'field_value')
            parts = list(error.absolute_path)
            if error.validator == 'required':
                # Names come from the schema, never from a formatted library message.
                for missing in error.validator_value:
                    if missing not in error.instance:
                        errors.append(diagnostic(code, safe_pointer(parts + [missing], schema)))
            else:
                errors.append(diagnostic(code, safe_pointer(parts, schema)))
        # Cross-field checks run only on a structurally valid contract.
        if not errors:
            if document['exposure']['base_path'] != '/projects/' + document['project']['id'] + '/':
                errors.append(diagnostic('field_value', '/exposure/base_path'))
            health = document['service']['health']['path']
            if any(segment in ('.', '..') for segment in health.split('/')):
                errors.append(diagnostic('field_value', '/service/health/path'))
        if errors:
            unique = {(e['path'], e['code']): e for e in errors}
            ordered = [unique[key] for key in sorted(unique)]
            return ({'valid': False, 'schema_version': None, 'project_id': None,
                     'errors': ordered[:MAX_ERRORS], 'truncated': len(ordered) > MAX_ERRORS}, None, 1)
        return ({'valid': True, 'schema_version': 1, 'project_id': document['project']['id'],
                 'errors': [], 'truncated': False}, document, 0)
    except ManifestError as error:
        return failure(error.code)
    except FileNotFoundError:
        return failure('input_missing')
    except (UnicodeError, yaml.YAMLError, ValueError):
        return failure('parse')
    except OSError as error:
        code = 'input_path' if error.errno in (errno.ELOOP, errno.ENOTDIR) else 'input_unreadable'
        return failure(code)
    except Exception:
        return failure('internal', 2)
