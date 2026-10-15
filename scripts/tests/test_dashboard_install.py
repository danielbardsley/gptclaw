"""Owned release/lifecycle fixtures; no host services, routes or project data change."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manage_dashboard as manager
import private_apps as app
import dashboard_collector as collector


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dashboard-install-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base/'source'
        self.frontend = self.source/'platform/dashboard/.next/standalone'
        self.frontend.mkdir(parents=True)
        (self.frontend/'server.js').write_text('/* synthetic release */')
        (self.frontend/'.next').mkdir()
        static = self.source/'platform/dashboard/.next/static'; static.mkdir()
        (static/'app.js').write_text('/* synthetic static asset */')
        for name, value in [(manager, ('PLATFORM', self.base/'platform')), (manager, ('USER_UNITS', self.base/'units')),
                            (manager, ('QUADLETS', self.base/'quadlets')), (app, ('REPO', self.source)), (app, ('STORE', self.base/'provider-store'))]:
            mock = patch.object(name, *value); mock.start(); self.addCleanup(mock.stop)
        manager.USER_UNITS.mkdir(); manager.QUADLETS.mkdir()
        self.calls = []
        def command(args, **kwargs):
            self.calls.append(args)
            if args[:3] == ['podman','image','inspect']: output='sha256:'+'1'*64
            elif 'DropInPaths' in args: output='DropInPaths='
            else: output='active'
            return subprocess.CompletedProcess(args, 1 if args[:3] == ['podman','container','exists'] else 0, output, '')
        for target, name, value in [(app,'command',command),(app,'provider_bundle',lambda:app.STORE/'providers'/('1'*64)),
                                    (app,'node_identity',lambda:'forge-dev.example.ts.net'),(app,'available',lambda _:True)]:
            mock=patch.object(target,name,value);mock.start();self.addCleanup(mock.stop)

    def test_prepare_activate_reprepare_stop_and_previous_release(self):
        first=manager.prepare()
        self.assertEqual(manager.prepare(),first)
        result=manager.activate(first)
        self.assertEqual(result['state'],'started')
        self.assertEqual(manager.status()['services'][manager.FRONTEND_UNIT],'active')
        (self.frontend/'server.js').write_text('/* second synthetic release */')
        second=manager.prepare();self.assertNotEqual(first,second)
        manager.activate(second)
        self.assertEqual(manager.owner()['previous'],first)
        self.assertEqual(manager.stop()['state'],'stopped')
        self.assertTrue((manager.PLATFORM/'releases'/first/'web/server.js').is_file())
        self.assertFalse(any('tailscale' in args or 'sudo' in args for args in self.calls))
        frontend=(manager.QUADLETS/'gptclaw-dashboard.container').read_text()
        self.assertIn('PublishPort=127.0.0.1:18200:3000',frontend)
        self.assertIn(':/run/gptclaw:ro',frontend)
        self.assertNotIn(':/srv/forge/projects',frontend)
        self.assertNotIn('podman.sock',frontend)

    def test_podman_unprefixed_image_id_is_frozen_as_sha256(self):
        command=app.command
        def unprefixed(args, **kwargs):
            result=command(args, **kwargs)
            if args[:3] == ['podman','image','inspect']:
                result.stdout='1'*64
            return result
        with patch.object(app,'command',side_effect=unprefixed):
            release=manager.prepare()
        descriptor=manager.read_owned(manager.PLATFORM/'releases'/release/'release.json')
        self.assertEqual(descriptor['image'],'sha256:'+'1'*64)

    def test_compiled_checksum_metadata_has_its_own_finite_bound(self):
        file=self.base/'compiled-record.json'
        value={f'asset-{index}':'a'*64 for index in range(1500)}
        file.write_text(json.dumps(value));file.chmod(0o600)
        self.assertGreater(file.stat().st_size,65536)
        self.assertEqual(manager.read_owned(file),value)
        file.write_text('x'*1048577)
        with self.assertRaises(app.AppError):manager.read_owned(file)
        file.write_text('{"duplicate":1,"duplicate":2}')
        with self.assertRaises(app.AppError):manager.read_owned(file)

    def test_unknown_units_and_modified_release_are_preserved(self):
        release=manager.prepare()
        unit=manager.USER_UNITS/manager.COLLECTOR_UNIT
        unit.write_text('unknown unit')
        with self.assertRaises(app.AppError):manager.activate(release)
        self.assertEqual(unit.read_text(),'unknown unit')
        unit.unlink()
        file=manager.PLATFORM/'releases'/release/'web/server.js'
        file.write_text('unreviewed modification')
        with self.assertRaises(app.AppError):manager.activate(release)
        self.assertEqual(file.read_text(),'unreviewed modification')

    def test_drifted_owned_unit_and_foreign_receipt_refuse_stop(self):
        release=manager.prepare();manager.activate(release)
        unit=manager.QUADLETS/'gptclaw-dashboard.container'
        unit.write_text('unknown later change')
        self.calls.clear()
        with self.assertRaises(app.AppError):manager.stop()
        self.assertFalse(any('stop' in args for args in self.calls))
        self.assertEqual(unit.read_text(),'unknown later change')

    def test_symlink_escape_in_build_assets_refused(self):
        (self.frontend/'escape').symlink_to(self.base/'outside')
        with self.assertRaises(app.AppError):manager.prepare()
        self.assertFalse(manager.PLATFORM.exists())


class SocketRecoveryTests(unittest.TestCase):
    def test_unknown_socket_preserved_owned_stale_recovered_and_clean_exit(self):
        import socket
        with tempfile.TemporaryDirectory(prefix='dashboard-socket-lease-') as base:
            path=Path(base)/'collector.sock'
            unknown=socket.socket(socket.AF_UNIX);unknown.bind(str(path));os.chmod(path,0o600);unknown.close()
            with self.assertRaises(Exception):
                with collector.SocketLease(path):pass
            self.assertTrue(path.exists())
            path.unlink()
            with collector.SocketLease(path) as lease:
                sock=socket.socket(socket.AF_UNIX);sock.bind(str(path));os.chmod(path,0o600);sock.close()
                lease.record()
                # Simulate process death: leave exact owned inode/receipt behind.
                lease.recorded=None
            with collector.SocketLease(path) as lease:
                self.assertFalse(path.exists())
                with collector.Server(str(path),collector.Collector({})):
                    lease.record()
            self.assertFalse(path.exists())
            self.assertFalse(path.with_suffix('.owner.json').exists())

    def test_live_socket_and_concurrent_owner_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory(prefix='dashboard-socket-lease-') as base:
            path=Path(base)/'collector.sock'
            with collector.SocketLease(path) as lease:
                with collector.Server(str(path),collector.Collector({})):
                    lease.record()
                    with self.assertRaises(Exception):
                        with collector.SocketLease(path):pass
                    self.assertTrue(path.exists())


if __name__ == '__main__':unittest.main()
