#!/usr/bin/env python3
"""Bootstrap-only Tailscale enrollment using the EC2 workload identity."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

CONFIG = Path('/etc/gptclaw/tailscale-federation.json')

class EnrollmentError(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise EnrollmentError(reason)

def validate(config):
    require(set(config) == {'client_id', 'audience', 'tag', 'hostname', 'region'}, 'invalid configuration fields')
    for key in config:
        require(isinstance(config[key], str), 'invalid configuration type')
    require(re.fullmatch(r'[A-Za-z0-9_-]{10,128}', config['client_id']), 'invalid client ID')
    require(config['audience'] == 'api.tailscale.com/' + config['client_id'], 'audience must match generated client audience')
    require(config['tag'] == 'tag:gptclaw-dev', 'unexpected enrollment tag')
    require(re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9-]{0,62}', config['hostname']), 'invalid hostname')
    require(config['region'] == 'us-east-1', 'unexpected AWS region')

def command(args, region):
    # Use the instance role, never inherited static credentials or credential files.
    env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
           'HOME': '/nonexistent', 'LC_ALL': 'C', 'AWS_REGION': region,
           'AWS_DEFAULT_REGION': region, 'AWS_STS_REGIONAL_ENDPOINTS': 'regional',
           'AWS_SHARED_CREDENTIALS_FILE': '/dev/null', 'AWS_CONFIG_FILE': '/dev/null'}
    try:
        result = subprocess.run(args, capture_output=True, text=True, env=env, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise EnrollmentError('Tailscale command unavailable or timed out') from None
    require(result.returncode == 0, 'Tailscale command failed; check issuer/trust, audience and host IAM')
    require(len(result.stdout) <= 131072, 'Tailscale response exceeds bound')
    return result.stdout

def check_status(status, config):
    require(status.get('BackendState') == 'Running', 'Tailscale is not running')
    own = status.get('Self', {})
    require(own.get('Online') is True and own.get('TailscaleIPs'), 'Tailscale node is not online')
    require(own.get('Tags') == [config['tag']], 'Tailscale node tag differs')

def enroll(config, runner=command):
    validate(config)
    version = runner(['tailscale', 'version'], config['region']).splitlines()[0].strip()
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:-[A-Za-z0-9.+_-]+)?', version)
    require(match and tuple(map(int, match.groups())) >= (1, 94, 0), 'Tailscale >= 1.94.0 required')
    status = json.loads(runner(['tailscale', 'status', '--json'], config['region']))
    if status.get('BackendState') != 'Running':
        runner(['tailscale', 'up', '--client-id=' + config['client_id'] + '?ephemeral=false&preauthorized=true',
                '--audience=' + config['audience'], '--advertise-tags=' + config['tag'],
                '--hostname=' + config['hostname'], '--ssh=false', '--timeout=120s'], config['region'])
        status = json.loads(runner(['tailscale', 'status', '--json'], config['region']))
    check_status(status, config)
    return {'status': 'passed', 'method': 'aws-workload-identity', 'version': version, 'tag': config['tag']}

def main():
    try:
        require(os.geteuid() == 0 and Path(__file__).resolve() == Path('/usr/local/libexec/gptclaw-tailscale-federation'),
                'enrollment restricted to installed bootstrap helper')
        result = enroll(json.loads(CONFIG.read_text()))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (EnrollmentError, OSError, ValueError, KeyError, IndexError, TypeError):
        # Never expose CLI output, identity tokens, or unexpected exception text.
        print('tailscale-federation status=failed; inspect client version, AWS issuer/IAM and Tailscale trust configuration')
        return 1

if __name__ == '__main__':
    sys.exit(main())
