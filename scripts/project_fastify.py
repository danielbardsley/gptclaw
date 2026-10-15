"""Explicit single-service TypeScript API contract; no project code is executed."""


def contract(slug):
    return {
        'schema_version': 7,
        'project': {'id': slug, 'name': slug.replace('-', ' ').title(), 'kind': 'api'},
        'commands': {
            **{action: ['pnpm', action] for action in
               ('build', 'test', 'format', 'lint', 'typecheck', 'security', 'verify')},
            'start': ['pnpm', 'dev'],
        },
        'service': {'internal_port': 8000, 'health': {
            'path': '/projects/'+slug+'/ready', 'timeout_seconds': 5}},
        'exposure': {'private': True, 'base_path': '/projects/'+slug+'/', 'funnel': False},
        'data': {'mode': 'ephemeral'},
    }
