#!/usr/bin/env python3
"""Offline filesystem and CLI tests; never touch the real Codex home."""
import argparse
import fcntl
import importlib.util
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('host_policy', ROOT / 'scripts/lib/host_policy.py')
hp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hp)


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_tmp = tempfile.TemporaryDirectory(prefix='host-policy-source-')
        cls.repo = Path(cls.repo_tmp.name)
        for name in ('config/codex/AGENTS.md', 'scripts/install-host-agents.sh', 'scripts/lib/host_policy.py'):
            target = cls.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        cls.git('init', '-q')
        cls.git('config', 'user.name', 'Policy fixture')
        cls.git('config', 'user.email', 'fixture@example.invalid')
        cls.old = (cls.repo / hp.SOURCE).read_bytes()
        cls.rev1 = cls.commit(cls.old)
        cls.new = cls.old.replace(b'Policy-Version: 1.0.0', b'Policy-Version: 1.0.1')
        cls.rev2 = cls.commit(cls.new)
        # Dirty working tree must never influence a requested commit.
        (cls.repo / hp.SOURCE).write_text('unreviewed working-tree text')
        hp.REPO = cls.repo

    @classmethod
    def tearDownClass(cls):
        cls.repo_tmp.cleanup()

    @classmethod
    def git(cls, *args):
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false', '-C', str(cls.repo), *args], stderr=subprocess.DEVNULL).decode().strip()

    @classmethod
    def commit(cls, data):
        (cls.repo / hp.SOURCE).write_bytes(data)
        cls.git('add', hp.SOURCE)
        cls.git('commit', '-qm', 'Synthetic policy')
        return cls.git('rev-parse', 'HEAD')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='host-policy-test-')
        self.base = Path(self.temp.name)
        self.home = self.base / 'profile'
        self.home.mkdir(mode=0o700)
        for name in ('auth.json', 'config.toml'):
            p = self.home / name
            p.write_text('synthetic sentinel only\n')
            p.chmod(0o600)
        self.sentinels = self.snapshot_sentinels()

    def tearDown(self):
        self.assertEqual(self.sentinels, self.snapshot_sentinels())
        self.temp.cleanup()

    def snapshot_sentinels(self):
        return {n: ((self.home / n).read_bytes(), (self.home / n).stat().st_mode)
                for n in ('auth.json', 'config.toml')}

    def run_cli(self, command='install', revision=None, expected=None, home=None, code=0):
        args = ['bash', str(self.repo / 'scripts/install-host-agents.sh'), command,
                '--codex-home', str(home or self.home)]
        if command != 'rollback':
            args += ['--revision', revision or self.rev1]
        if expected:
            args += ['--expected-current-sha256', expected]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def install(self):
        self.run_cli()

    def update(self):
        self.run_cli(revision=self.rev2, expected=hp.digest(self.old))

    def test_first_install_noop_and_committed_source(self):
        self.install()
        self.assertEqual((self.home / hp.POLICY).read_bytes(), self.old)
        before = (self.home / hp.META).read_bytes()
        timestamp = (self.home / hp.POLICY).stat().st_mtime_ns
        self.assertIn('no-op', self.run_cli())
        self.assertEqual((self.home / hp.META).read_bytes(), before)
        self.assertEqual((self.home / hp.POLICY).stat().st_mtime_ns, timestamp)
        self.run_cli('verify')
        self.assertFalse((self.home / hp.PREVIOUS).exists())

    def test_new_home_and_readonly_missing(self):
        other = self.base / 'new-profile'
        self.assertIn('missing:', self.run_cli('verify', home=other, code=1))
        self.assertFalse(other.exists())
        self.run_cli(home=other)
        self.assertEqual(stat.S_IMODE(other.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((other / hp.POLICY).stat().st_mode), 0o600)

    def test_update_and_two_way_rollback(self):
        self.install()
        self.update()
        self.assertEqual(hp.pair(self.home / hp.PREVIOUS)[0], self.old)
        self.run_cli('rollback', expected=hp.digest(self.new))
        self.run_cli('verify')
        self.assertEqual(hp.pair(self.home / hp.PREVIOUS)[0], self.new)
        self.run_cli('rollback', expected=hp.digest(self.old))
        self.run_cli('verify', revision=self.rev2)

    def test_conflicts_and_no_previous(self):
        self.install()
        self.run_cli(revision=self.rev2, code=1)
        self.run_cli(revision=self.rev2, expected='0' * 64, code=1)
        self.assertIn('no previous', self.run_cli('rollback', expected=hp.digest(self.old), code=1))
        self.assertEqual(hp.pair(self.home)[0], self.old)

    def test_unmanaged_policy_preserved(self):
        p = self.home / hp.POLICY
        p.write_text('operator content')
        p.chmod(0o600)
        self.run_cli(expected=hp.digest(p.read_bytes()), code=1)
        self.assertEqual(p.read_text(), 'operator content')
        self.assertFalse((self.home / hp.LOCK).exists())

    def test_drift_and_readonly_verify(self):
        self.install()
        p = self.home / hp.POLICY
        p.write_bytes(self.new)
        before = {x.name: (x.read_bytes(), x.stat().st_mtime_ns) for x in self.home.iterdir()}
        self.run_cli('verify', code=1)
        after = {x.name: (x.read_bytes(), x.stat().st_mtime_ns) for x in self.home.iterdir()}
        self.assertEqual(before, after)
        self.run_cli(expected=hp.digest(self.new), code=1)
        self.assertEqual(p.read_bytes(), self.new)

    def test_metadata_validation(self):
        self.install()
        p = self.home / hp.META
        original = p.read_bytes()
        variants = [original + b'format=1\n', original.replace(b'format=1', b'format=2'),
                    original.replace(b'source=', b'unknown='), b'not metadata',
                    original.replace(self.rev1.encode(), b'bad'),
                    original.replace(b'installed_utc=', b'installed_utc=invalid')]
        for data in variants:
            p.write_bytes(data)
            self.assertIn('incomplete:', self.run_cli('verify', code=1))
        p.write_bytes(original)
        self.run_cli('verify')

    def test_symlinks_and_hardlinks(self):
        target = self.base / 'unrelated'
        target.write_text('leave unchanged')
        target.chmod(0o600)
        for name in (hp.POLICY, hp.META, hp.LOCK, hp.PREVIOUS):
            p = self.home / name
            p.symlink_to(target)
            self.assertIn('unsafe-path:', self.run_cli(code=1))
            p.unlink()
        linked_home = self.base / 'linked'
        linked_home.symlink_to(self.home)
        self.run_cli(home=linked_home, code=1)
        os.link(target, self.home / hp.POLICY)
        self.run_cli(code=1)
        self.assertEqual(target.read_text(), 'leave unchanged')

    def test_previous_child_symlink_and_unknown_entry(self):
        self.install()
        self.update()
        p = self.home / hp.PREVIOUS / hp.POLICY
        p.unlink()
        p.symlink_to(self.home / hp.POLICY)
        self.run_cli('verify', revision=self.rev2, code=1)
        p.unlink()
        hp.write_new(p, self.old)
        (p.parent / 'unmanaged').write_text('keep')
        self.run_cli('rollback', expected=hp.digest(self.new), code=1)
        self.assertEqual((p.parent / 'unmanaged').read_text(), 'keep')

    def test_modes_and_owner(self):
        self.home.chmod(0o755)
        self.assertIn('unsafe-mode:', self.run_cli(code=1))
        self.assertEqual(stat.S_IMODE(self.home.stat().st_mode), 0o755)
        self.home.chmod(0o700)
        self.install()
        (self.home / hp.META).chmod(0o644)
        self.run_cli('verify', code=1)
        with patch.object(hp.os, 'getuid', return_value=os.getuid() + 1):
            with self.assertRaisesRegex(hp.Failure, 'unsafe-owner'):
                hp.inspect(self.home, directory=True)

    def test_override_including_empty(self):
        p = self.home / 'AGENTS.override.md'
        p.touch()
        self.assertIn('shadowed:', self.run_cli(code=1))
        self.assertTrue(p.exists())
        self.assertFalse((self.home / hp.POLICY).exists())

    def test_source_validation_and_bad_arguments(self):
        for data in (b'', b'\xff', self.old + b'x' * 8192,
                     self.old.replace(b'## Secrets and data', b'## Missing'),
                     self.old + b'\x00', self.old + b'Policy-Version: 2.0.0\n'):
            with self.assertRaises(hp.Failure):
                hp.validate_policy(data)
        self.run_cli(revision='main', code=2)
        self.run_cli(revision='0' * 40, code=2)
        self.run_cli(expected='wrong', code=2)
        self.run_cli(home=Path('relative'), code=2)
        self.run_cli('verify', expected='0' * 64, code=2)
        self.run_cli('rollback', code=2)
        with patch.object(hp.os, 'getuid', return_value=0):
            with self.assertRaisesRegex(hp.Failure, 'not root'):
                hp.execute(argparse.Namespace(command='install'))
        with patch.object(hp, 'git', side_effect=[b'commit', b'120000 blob abc\tconfig/codex/AGENTS.md']):
            with self.assertRaisesRegex(hp.Failure, 'regular'):
                hp.source(self.rev1)

    def test_lock_contention_and_concurrent_install(self):
        self.install()
        with (self.home / hp.LOCK).open('rb') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            self.assertIn('busy:', self.run_cli(revision=self.rev2, expected=hp.digest(self.old), code=1))
        cmd = ['bash', str(self.repo / 'scripts/install-host-agents.sh'), 'install',
               '--codex-home', str(self.home), '--revision', self.rev2,
               '--expected-current-sha256', hp.digest(self.old)]
        procs = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        results = [(p.communicate(), p.returncode) for p in procs]
        self.assertEqual(sorted(r[1] for r in results), [0, 1])
        self.run_cli('verify', revision=self.rev2)

    def test_real_invalid_git_sources(self):
        for data in (b'bad header', b'\xff', self.old + b'x' * 8192):
            revision = self.commit(data)
            self.run_cli(revision=revision, code=2)
            self.assertFalse((self.home / hp.POLICY).exists())
        path = self.repo / hp.SOURCE
        path.unlink()
        path.symlink_to('missing-target')
        self.git('add', hp.SOURCE)
        self.git('commit', '-qm', 'Synthetic symlink source')
        revision = self.git('rev-parse', 'HEAD')
        self.run_cli(revision=revision, code=2)
        path.unlink()
        path.write_bytes(self.new)

    def test_missing_current_and_metadata(self):
        self.install()
        self.update()
        (self.home / hp.POLICY).unlink()
        self.run_cli('verify', revision=self.rev2, code=1)
        (self.home / hp.META).unlink()
        self.assertIn('previous policy exists', self.run_cli(code=1))
        self.assertFalse((self.home / hp.POLICY).exists())

    def test_restrictive_umask(self):
        other = self.base / 'restrictive-profile'
        cmd = ['bash', str(self.repo / 'scripts/install-host-agents.sh'), 'install',
               '--codex-home', str(other), '--revision', self.rev1]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                preexec_fn=lambda: os.umask(0o777))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.run_cli('verify', home=other)

    def test_publication_failures_detected(self):
        self.install()
        original_replace = hp.os.replace
        for failing_name in (hp.POLICY, hp.META):
            def fail(src, dst):
                if Path(dst) == self.home / failing_name:
                    raise OSError('injected rename failure')
                return original_replace(src, dst)
            current = hp.pair(self.home)
            desired = hp.source(self.rev2)
            with patch.object(hp.os, 'replace', side_effect=fail):
                with self.assertRaises(OSError):
                    hp.publish(self.home, *desired, current)
            self.assertIn((self.home / hp.POLICY).read_bytes(), (self.old, self.new))
            self.assertIn('incomplete:', self.run_cli('verify', code=1))
            # Explicit fixture-only reconciliation from the intact previous pair.
            previous = hp.pair(self.home / hp.PREVIOUS)
            (self.home / hp.POLICY).write_bytes(previous[0])
            (self.home / hp.META).write_bytes(previous[1])
            for p in self.home.iterdir():
                if p.name.startswith(hp.STAGING):
                    shutil.rmtree(p)
            self.run_cli('verify')


if __name__ == '__main__':
    unittest.main(verbosity=2)
