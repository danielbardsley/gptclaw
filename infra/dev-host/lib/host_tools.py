#!/usr/bin/env python3
"""Strict host profile validation and bootstrap-only adapters (stdlib only)."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

PROFILE = Path('/etc/gptclaw/host-tools-profile.json')
CONTEXT = Path('/etc/gptclaw/host-tools-context.json')
STATE = Path('/var/lib/gptclaw')
VERSION = re.compile(r'[A-Za-z0-9][A-Za-z0-9.+:~_-]{0,127}\Z')
PACKAGE = re.compile(r'[a-z0-9][a-z0-9+.-]{0,79}\Z')
SOURCES = {
    'apt': 'ubuntu:noble',
    'ssm': 'snap:amazon-ssm-agent/latest/stable',
    'aws-cli': 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip',
    'tailscale': 'https://tailscale.com/install.sh',
    'cloudwatch': 'https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb',
    'codex': 'https://chatgpt.com/codex/install.sh',
}
PHASES = ('base-packages', 'ssm-agent', 'aws-cli', 'tailscale', 'cloudwatch-agent', 'codex')
ADAPTER_PHASE = dict(zip(SOURCES, PHASES))


class ProfileError(ValueError):
    """Safe diagnostic; never includes command output or arbitrary profile values."""


def require(ok, message):
    if not ok:
        raise ProfileError(message)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected.split()), 'invalid fields')


def text(value):
    require(type(value) is str and 0 < len(value) <= 500 and
            value.strip() == value and all(ord(c) >= 32 and ord(c) != 127 for c in value),
            'invalid text')


def unique(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON key')
        result[k] = v
    return result


def load(path):
    try:
        return json.loads(Path(path).read_text(), object_pairs_hook=unique)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ProfileError('cannot read valid JSON') from None


def validate(profile, today=None):
    """Same validation in CI and bootstrap; no subprocesses or mutations."""
    today = today or dt.datetime.now(ZoneInfo('America/New_York')).date()
    keys(profile, 'schema_version target components')
    require(type(profile['schema_version']) is int and profile['schema_version'] == 1,
            'unsupported schema version')
    require(profile['target'] == {'os': 'ubuntu', 'release': '24.04', 'architecture': 'amd64'},
            'unsupported target')
    require(type(profile['components']) is list and 0 < len(profile['components']) <= 100,
            'invalid component list')
    ids, packages, adapters = set(), set(), set()
    for c in profile['components']:
        keys(c, 'id purpose owner adapter identity source package version verification')
        for field in ('id', 'purpose', 'owner', 'adapter', 'identity', 'source', 'verification'):
            text(c[field])
        require(re.fullmatch(r'[a-z][a-z0-9-]{0,63}', c['id']) is not None, 'invalid identifier')
        require(c['id'] not in ids, 'duplicate identifier')
        ids.add(c['id'])
        adapter = c['adapter']
        require(adapter in SOURCES, 'unsupported adapter')
        require(c['identity'] == ('forge' if adapter == 'codex' else 'root'), 'invalid identity')
        require(c['verification'] == adapter + '-version', 'unsupported verification')
        v = c['version']
        keys(v, 'policy value sha256 exception')
        require(v['policy'] in ('distribution', 'channel', 'exact'), 'unsupported version policy')
        if adapter == 'apt':
            require(type(c['package']) is str and PACKAGE.fullmatch(c['package']), 'invalid package')
            require(c['package'] not in packages, 'duplicate package ownership')
            packages.add(c['package'])
            require(v['policy'] in ('distribution', 'exact'), 'invalid apt policy')
            require(v['sha256'] is None and v['exception'] is None, 'invalid apt metadata')
        else:
            require(c['package'] is None and adapter not in adapters, 'duplicate adapter ownership')
            adapters.add(adapter)
            require(v['policy'] == 'channel' or
                    (v['policy'] == 'exact' and adapter == 'aws-cli'),
                    'unsupported adapter policy')
        if v['policy'] == 'channel':
            require(v['value'] is None and v['sha256'] is None, 'invalid channel metadata')
            e = v['exception']
            keys(e, 'owner scope reason approved_on expires_on removal')
            for val in e.values():
                text(val)
            require(e['owner'] == 'Daniel' and e['scope'] == c['id'], 'invalid exception ownership')
            try:
                approved, expires = (dt.date.fromisoformat(e[k]) for k in ('approved_on', 'expires_on'))
            except ValueError:
                raise ProfileError('invalid exception date') from None
            require(approved <= today <= expires and approved < expires, 'exception unapproved or expired')
        elif v['policy'] == 'exact':
            require(type(v['value']) is str and VERSION.fullmatch(v['value']), 'invalid exact version')
            require(v['exception'] is None, 'exact policy cannot have exception')
            if adapter != 'apt':
                require(type(v['sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', v['sha256']),
                        'missing artifact digest')
        else:
            require(v['value'] is None, 'invalid distribution version')
        expected = SOURCES[adapter]
        if v['policy'] == 'exact' and adapter == 'aws-cli':
            require(re.fullmatch(r'2\.[0-9]+\.[0-9]+', v['value']), 'invalid AWS version')
            expected = 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64-' + v['value'] + '.zip'
        require(c['source'] == expected, 'unapproved source')
    # These are consumers in bootstrap, not a second installation list. Retirement
    # requires changing the consuming phase and this contract in the same review.
    require(adapters == set(SOURCES) - {'apt'}, 'missing bootstrap component')
    require({'ca-certificates', 'curl', 'e2fsprogs', 'git', 'jq', 'nvme-cli',
             'openssh-server', 'python3', 'rsyslog', 'sudo', 'ufw', 'unzip'} <= packages,
            'missing bootstrap package capability')
    return profile


def digest(profile):
    return hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def run(args, *, optional=False, umask=-1):
    """Capture diagnostics rather than copying potentially sensitive installer output."""
    env = dict(os.environ, LC_ALL='C', DEBIAN_FRONTEND='noninteractive',
               PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
    try:
        with tempfile.TemporaryFile() as output:
            result = subprocess.run(args, stdout=output, stderr=subprocess.DEVNULL, env=env,
                                    timeout=900, check=False, umask=umask)
            if result.returncode:
                if optional:
                    return None
                raise ProfileError('component command failed')
            output.seek(0)
            data = output.read(65537)
            require(len(data) <= 65536, 'component output exceeds bound')
            return data.decode('utf-8', errors='strict').strip()
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        raise ProfileError('component command unavailable or timed out') from None


def atomic(path, value):
    path = Path(path)
    require(not path.is_symlink(), 'unsafe state path')
    fd, temp = tempfile.mkstemp(prefix='.host-tools-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def invalidate(state):
    for name in ('host-tools.json', 'bootstrap-complete.json'):
        (state / name).unlink(missing_ok=True)


def check_target(profile, runner=run):
    os_data = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)
    require(os_data.get('ID', '').strip('"') == profile['target']['os'] and
            os_data.get('VERSION_ID', '').strip('"') == profile['target']['release'] and
            runner(['dpkg', '--print-architecture']) == profile['target']['architecture'], 'host target mismatch')


def check_ubuntu_candidate(policy, selected=None):
    """Reject an unavailable version or a selected version supplied by other origins."""
    match = re.search(r'^  Candidate: (\S+)$', policy, re.M)
    require(match is not None and match[1] != '(none)', 'package version unavailable')
    selected = selected or match[1]
    active, found = False, False
    for line in policy.splitlines():
        version = re.fullmatch(r'\s+(?:\*\*\* )?(\S+) \d+', line)
        if version:
            active = version[1] == selected
            continue
        source = re.fullmatch(r'\s+\d+ (https?://\S+) (\S+) amd64 Packages', line)
        if active and source:
            host = urlsplit(source[1]).hostname or ''
            require(host in ('archive.ubuntu.com', 'security.ubuntu.com') or
                    re.fullmatch(r'[a-z0-9-]+\.ec2\.archive\.ubuntu\.com', host),
                    'selected package has unapproved origin')
            require(re.fullmatch(r'noble(?:-updates|-security|-backports)?/[a-z]+', source[2]),
                    'selected package has unapproved release')
            found = True
        elif active and ' Packages' in line:
            raise ProfileError('selected package has unapproved origin')
    require(found, 'selected Ubuntu version unavailable')


class Provisioner:
    def __init__(self, profile, runner=run):
        self.profile = validate(profile)
        self.run = runner

    def observe(self, c):
        a = c['adapter']
        if a in ('apt', 'cloudwatch'):
            package = c['package'] if a == 'apt' else 'amazon-cloudwatch-agent'
            value = self.run(['dpkg-query', '-W', '-f=${db:Status-Status} ${Version}', package], optional=True)
            if value is None:
                return None
            require(value.startswith('installed '), 'existing package is not fully installed')
            value = value.split(' ', 1)[1]
        elif a == 'ssm':
            # Check exact unit load state; list-unit-files can succeed on no matches.
            commands = []
            for unit, command in (
                ('amazon-ssm-agent.service', ['/usr/bin/amazon-ssm-agent', '-version']),
                ('snap.amazon-ssm-agent.amazon-ssm-agent.service', ['/snap/amazon-ssm-agent/current/amazon-ssm-agent', '-version']),
            ):
                state = self.run(['systemctl', 'show', '--property=LoadState', '--value', unit], optional=True)
                if state == 'loaded':
                    commands.append(command)
            require(len(commands) <= 1, 'conflicting SSM installations')
            if not commands:
                return None
            raw = self.run(commands[0])
            match = re.search(r'([0-9]+(?:\.[0-9]+){2,})', raw)
            require(match is not None, 'invalid SSM version')
            return match[1]

        else:
            commands = {
                'aws-cli': ['/usr/local/bin/aws', '--version'],
                'tailscale': ['/usr/bin/tailscale', 'version'],
                'codex': ['sudo', '-iu', 'forge', '/home/forge/.local/bin/codex', '--version'],
            }
            # Missing tool is allowed; an existing but failing binary is a conflict.
            binary = commands[a][-2] if a == 'codex' else commands[a][0]
            exists = self.run(['test', '-e', binary], optional=True)
            if exists is None:
                return None
            raw = self.run(commands[a])
            pattern = {'aws-cli': r'^aws-cli/(2\.[0-9]+\.[0-9]+)',
                       'tailscale': r'^([0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.+:~_-]*)',
                       'codex': r'^codex(?:-cli)?\s+([0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.+:~_-]*)'}[a]
            match = re.search(pattern, raw)
            require(match is not None, 'invalid tool version')
            value = match[1]
        require(VERSION.fullmatch(value), 'invalid observed version')
        return value

    def verify(self, c):
        value = self.observe(c)
        require(value is not None, 'required component absent')
        if c['version']['policy'] == 'exact':
            require(value == c['version']['value'], 'installed version conflicts with profile')
        return {'id': c['id'], 'identity': c['identity'], 'version': value,
                'policy': c['version']['policy'], 'verification': c['verification'], 'status': 'passed'}

    def install(self, c):
        value = self.observe(c)
        if value is not None:
            self.verify(c)
            return
        a, v = c['adapter'], c['version']
        if a == 'apt':
            # Repository selection remains Ubuntu's configured trusted distribution sources.
            policy = self.run(['apt-cache', 'policy', c['package']])
            selected = v['value'] if v['policy'] == 'exact' else None
            check_ubuntu_candidate(policy, selected)
            package = c['package'] + ('=' + v['value'] if v['policy'] == 'exact' else '')
            self.run(['apt-get', 'install', '-y', '--no-install-recommends', '--', package])
        elif a == 'ssm':
            self.run(['snap', 'install', 'amazon-ssm-agent', '--classic', '--channel=latest/stable'])
        else:
            with tempfile.TemporaryDirectory(prefix='gptclaw-tool-') as tmp:
                artifact = Path(tmp) / 'artifact'
                self.run(['curl', '--fail', '--silent', '--show-error', '--location',
                          '--proto', '=https', '--proto-redir', '=https', '--max-time', '300',
                          c['source'], '-o', str(artifact)])
                if v['policy'] == 'exact':
                    with artifact.open('rb') as stream:
                        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
                    require(actual == v['sha256'], 'artifact integrity mismatch')
                if a == 'aws-cli':
                    # Never overwrite an unrecognized existing installation tree.
                    require(self.run(['test', '-e', '/usr/local/aws-cli'], optional=True) is None,
                            'existing AWS installation conflicts')
                    self.run(['unzip', '-q', str(artifact), '-d', tmp], umask=0o022)
                    # Scope public tool permissions to this installer; retain bootstrap's 027.
                    self.run([str(Path(tmp) / 'aws/install')], umask=0o022)
                elif a == 'cloudwatch':
                    require(self.run(['test', '-e', '/opt/aws/amazon-cloudwatch-agent'], optional=True) is None,
                            'existing CloudWatch installation conflicts')
                    self.run(['dpkg', '-i', str(artifact)])
                elif a == 'tailscale':
                    self.run(['sh', str(artifact)])
                elif a == 'codex':
                    # Downloaded script runs only as forge; tmp is traversable, artifact read-only.
                    os.chmod(tmp, 0o755)
                    os.chmod(artifact, 0o644)
                    self.run(['sudo', '-u', 'forge', '-H', 'env', 'CODEX_NON_INTERACTIVE=1',
                              'CODEX_INSTALL_DIR=/home/forge/.local/bin', 'sh', str(artifact)])
        self.verify(c)

    def phase(self, phase):
        require(phase in PHASES, 'unknown phase')
        if phase == 'base-packages':
            self.run(['apt-get', 'update', '-y'])
        for c in self.profile['components']:
            if ADAPTER_PHASE[c['adapter']] == phase:
                self.install(c)

    def receipt(self, revision):
        require(re.fullmatch(r'[0-9a-f]{40}', revision), 'invalid deployment revision')
        # forge is created after the AWS installation phase. Check actual user
        # execution before publishing any successful provisioning receipt.
        aws = next(c for c in self.profile['components'] if c['adapter'] == 'aws-cli')
        expected = self.verify(aws)['version']
        observed = self.run(['sudo', '-u', 'forge', '-H', '/usr/local/bin/aws', '--version'])
        require(re.match(r'^aws-cli/' + re.escape(expected) + r'(?:\s|$)', observed),
                'AWS CLI unavailable or inconsistent for forge')
        return {'schema_version': 1, 'profile_digest': digest(self.profile),
                'deployment_revision': revision, 'target': self.profile['target'],
                'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'status': 'passed', 'components': [self.verify(c) for c in self.profile['components']]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('validate', 'begin', 'phase', 'finish'))
    parser.add_argument('argument', nargs='?')
    args = parser.parse_args()
    try:
        if args.action == 'validate':
            profile = validate(load(args.argument or PROFILE))
            print('Host profile valid; sha256=' + digest(profile))
            return 0
        require(os.geteuid() == 0 and Path(__file__).resolve() == Path('/usr/local/libexec/gptclaw-host-tools'),
                'provisioning is restricted to the installed bootstrap helper')
        # Invalidate before parsing, including malformed or expired profiles on retry.
        invalidate(STATE)
        profile = validate(load(PROFILE))
        context = load(CONTEXT)
        keys(context, 'deployment_revision')
        require(type(context['deployment_revision']) is str and
                re.fullmatch(r'[0-9a-f]{40}', context['deployment_revision']), 'invalid deployment revision')
        check_target(profile)
        engine = Provisioner(profile)
        if args.action == 'phase':
            engine.phase(args.argument)
        elif args.action == 'finish':
            atomic(STATE / 'host-tools.json', engine.receipt(context['deployment_revision']))
        print('host-tools action=' + args.action + ' status=succeeded')
        return 0
    except (ProfileError, OSError) as exc:
        print('host-tools status=failed reason=' + (str(exc) if isinstance(exc, ProfileError) else 'filesystem failure'))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
