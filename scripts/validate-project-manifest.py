#!/usr/bin/env python3
"""Validate one project manifest without executing project code."""
import argparse
import json
import sys

# Avoid creating cache files beside the entrypoint or imported project tooling.
sys.dont_write_bytecode = True


def failed(code, message):
    return {'valid': False, 'schema_version': None, 'project_id': None,
            'errors': [{'code': code, 'path': '', 'message': message}], 'truncated': False}


class UsageError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    json_mode = '--json' in argv
    parser = Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--json', action='store_true')
    try:
        args = parser.parse_args(argv)
    except UsageError:
        result, code = failed('usage', 'Supply --project-root DIRECTORY and optionally --json.'), 2
    else:
        try:
            from project_manifest import validate_project
        except Exception:
            result, code = failed('setup', 'Validator dependencies or the bundled schema are unavailable or invalid.'), 2
        else:
            result, _, code = validate_project(args.project_root)
    if json_mode:
        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    elif result['valid']:
        print(f"Valid manifest: {result['project_id']} (schema {result['schema_version']}).")
    else:
        for error in result['errors']:
            print(f"{error['code']} {error['path'] or '/'}: {error['message']}", file=sys.stderr)
        if result['truncated']:
            print('Further errors omitted.', file=sys.stderr)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
