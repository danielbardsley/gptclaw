"""Development-client runtime admission. No inherited Go advisory exceptions."""
import hashlib
import time
from pathlib import Path

import native_contract as contract
import private_apps as app
import project_dependencies as deps


def policy(root):
    root, _, config = contract.inspect(root)
    return {'schema_version': 2, 'scope': 'android-development-client', 'owner': 'project owner',
            'expires_at': config['expires_at'], 'max_session_seconds': 28800,
            'lock_sha256': hashlib.sha256(deps.read_bytes(root / 'pnpm-lock.yaml')).hexdigest(),
            'approval_id': config['approval_id'], 'exceptions': []}


def evaluate(report, value, lock_bytes, now=None):
    """Require complete counts and zero high/critical findings, including transitive tools."""
    import metro_security as security
    now = time.time() if now is None else now
    app.need(value['scope'] == 'android-development-client' and value['exceptions'] == []
             and security.timestamp(value['expires_at']) > now
             and hashlib.sha256(lock_bytes).hexdigest() == value['lock_sha256'], 'native-policy')
    app.need(isinstance(report, dict) and isinstance(report.get('advisories'), dict), 'native-policy')
    counts = {k: 0 for k in security.LEVELS}
    app.need(len(report['advisories']) <= 4096, 'native-policy')
    for finding in report['advisories'].values():
        app.need(isinstance(finding, dict) and finding.get('severity') in counts, 'native-policy')
        counts[finding['severity']] += 1
    app.need(report.get('metadata', {}).get('vulnerabilities') == counts
             and counts['high'] == 0 and counts['critical'] == 0, 'native-policy')
    return {'scope': value['scope'], 'vulnerabilities': counts, 'temporary_exceptions': [],
            'expires_at': value['expires_at'], 'lock_sha256': value['lock_sha256']}
