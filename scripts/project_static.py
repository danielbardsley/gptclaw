"""Static web contract and stop/build/start recovery using existing owned jobs."""
import uuid
import private_apps as app


def contract(slug):
    return {
        'schema_version': 10,
        'project': {'id': slug, 'name': slug.replace('-', ' ').title(), 'kind': 'web'},
        'commands': {action: ['pnpm', action] for action in
                     ('build', 'start', 'test', 'format', 'lint', 'typecheck', 'security', 'verify')},
        'service': {'internal_port': 3000, 'health': {
            'path': '/projects/'+slug+'/_gptclaw/ready', 'timeout_seconds': 5}},
        'exposure': {'private': True, 'base_path': '/projects/'+slug+'/', 'funnel': False},
        'data': {'mode': 'ephemeral'},
    }


def rebuild(root, value, rows, stage, restart=False):
    """Called only inside the managed lifecycle project lock/guard."""
    active = rows['web']['active']
    stage('stop', 'web')
    app.stop(root, take_lock=False)
    s = app.reserve(root, value)
    s.update(operation='rebuild', operation_id=uuid.uuid4().hex,
             operation_result='running', phase='preparing', health_ready=False)
    app.save(app.STORE/(s['id']+'.json'), s)
    try:
        stage('build', 'web')
        if active or restart:
            stage('start', 'web')
            app.start(root, take_lock=False)
            return
        import project_toolchains as tools
        selected = tools.selection(root)
        s['image'] = app.toolchain(root, selected)
        s['toolchain_hash'] = selected['selection_hash']
        app.prepare(s, value, build=True)
        s.update(phase='stopped', operation_result='passed', health_ready=False)
        app.save(app.STORE/(s['id']+'.json'), s)
    except BaseException:
        s.update(phase='failed', operation_result='failed', health_ready=False, error='command')
        app.save(app.STORE/(s['id']+'.json'), s)
        raise
