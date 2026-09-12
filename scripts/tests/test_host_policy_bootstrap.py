#!/usr/bin/env python3
"""Exercise the bootstrap helper offline against a temporary Git repository."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix='policy-bootstrap-source-')
        cls.repo = Path(cls.fixture.name)
        for name in ('config/codex/AGENTS.md', 'scripts/install-host-agents.sh', 'scripts/lib/host_policy.py'):
            p = cls.repo / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, p)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(cls.repo), '-c', 'core.hooksPath=/dev/null',
                '-c', 'commit.gpgsign=false', '-c', 'user.name=Fixture',
                '-c', 'user.email=fixture@example.invalid', *args], stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q')
        git('add', '.')
        git('commit', '-qm', 'Offline bootstrap fixture')
        cls.revision = git('rev-parse', 'HEAD')

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='policy-bootstrap-test-')
        self.base = Path(self.temp.name)
        self.home = self.base / 'profile'
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        # Simulate the forge account name on CI without creating a user or sudo.
        (self.bin / 'id').write_text('#!/bin/sh\nif [ "$1" = -un ]; then echo forge; else /usr/bin/id "$@"; fi\n')
        (self.bin / 'id').chmod(0o755)
        self.script = self.base / 'bootstrap.sh'
        template = (ROOT / 'infra/dev-host/templates/install-host-policy.sh.tftpl').read_text()
        template = template.replace('${jsonencode(host_policy_revision)}', json.dumps(self.revision))
        template = template.replace('https://github.com/danielbardsley/gptclaw.git', str(self.repo))
        template = template.replace('/home/forge/.codex', str(self.home))
        template = template.replace('/tmp/gptclaw-host-policy.XXXXXXXX', str(self.base / 'checkout.XXXXXXXX'))
        self.script.write_text(template)
        self.env = {**os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}

    def tearDown(self):
        self.assertFalse(list(self.base.glob('checkout.*')), 'temporary checkout must be cleaned')
        self.temp.cleanup()

    def run_bootstrap(self, success=True):
        result = subprocess.run(['bash', str(self.script)], env=self.env, capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_first_boot_and_repeat(self):
        self.run_bootstrap()
        self.assertEqual((self.home / 'AGENTS.md').read_bytes(), (self.repo / 'config/codex/AGENTS.md').read_bytes())
        self.assertEqual(self.home.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.home / 'AGENTS.md').stat().st_mode & 0o777, 0o600)
        original = (self.home / 'gptclaw-host-policy.meta').read_bytes()
        self.assertIn(self.revision.encode(), original)
        self.assertIn('no-op', self.run_bootstrap().stdout)
        self.assertEqual((self.home / 'gptclaw-host-policy.meta').read_bytes(), original)

    def test_existing_auth_and_drift_preserved(self):
        self.run_bootstrap()
        auth = self.home / 'auth.json'
        auth.write_text('synthetic sentinel')
        auth.chmod(0o600)
        self.run_bootstrap()
        p = self.home / 'AGENTS.md'
        p.write_bytes(p.read_bytes() + b'\nlocal edit\n')
        changed = p.read_bytes()
        self.run_bootstrap(False)
        self.assertEqual(p.read_bytes(), changed)
        self.assertEqual(auth.read_text(), 'synthetic sentinel')
        self.assertEqual(auth.stat().st_mode & 0o777, 0o600)

    def test_override_preserved(self):
        self.home.mkdir(mode=0o700)
        p = self.home / 'AGENTS.override.md'
        p.touch()
        self.run_bootstrap(False)
        self.assertTrue(p.exists())
        self.assertFalse((self.home / 'AGENTS.md').exists())

    def test_fetch_failure_leaves_home_absent(self):
        self.script.write_text(self.script.read_text().replace(self.revision, '0' * 40))
        self.run_bootstrap(False)
        self.assertFalse(self.home.exists())

    def test_wrong_fetched_commit_refused(self):
        wrapper = self.bin / 'git'
        wrapper.write_text('''#!/bin/sh
case "$*" in
  *"rev-parse --verify FETCH_HEAD"*) echo 0000000000000000000000000000000000000000; exit 0;;
esac
exec /usr/bin/git "$@"
''')
        wrapper.chmod(0o755)
        self.assertIn('does not match', self.run_bootstrap(False).stderr)
        self.assertFalse(self.home.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
