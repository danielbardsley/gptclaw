#!/usr/bin/env python3
"""SYS-001 tests use synthetic identities/files and mock all provisioning commands."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import pwd
import grp
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result
r=module('rootless',ROOT/'infra/dev-host/lib/rootless.py')
f=module('fixture',ROOT/'scripts/rootless-fixture.py')

def user(name='forge',uid=1002,gid=1002):
    return pwd.struct_passwd((name,'x',uid,gid,'', '/home/'+name,'/bin/bash'))
def group(name='forge',gid=1002,members=()):
    return grp.struct_group((name,'x',gid,list(members)))
def info():
    return {'host':{'security':{'rootless':True},'cgroupVersion':'v2','cgroupManager':'systemd',
                    'networkBackend':'netavark','slirp4netns':{'executable':'/usr/bin/slirp4netns'},'ociRuntime':{'name':'crun'}},
            'store':{'graphDriverName':'overlay','graphRoot':str(r.GRAPH),'runRoot':str(r.RUNROOT)},
            'version':{'Version':'4.9.3'}}

class RootlessTests(unittest.TestCase):
    def test_mapping_add_and_repeat(self):
        old='ubuntu:100000:65536\nssm-user:165536:65536\n'
        new=r.mappings(old,[0,1000,1001,1002])
        self.assertEqual(new,old+'forge:231072:65536\n')
        self.assertEqual(r.mappings(new,[1002]),new)

    def test_mapping_conflicts_and_real_identity(self):
        cases=[('forge:100000:65536\n',[]),('other:230000:65536\n',[]),
               ('other:296607:1\n',[]),('forge:231072:65536\nforge:231072:65536\n',[]),
               ('bad data',[]),('',[231072]),('1002:231072:65536\n',[])]
        for content,accounts in cases:
            with self.subTest(content=content):
                with self.assertRaises(r.RootlessError): r.mappings(content,accounts)

    def test_identity_conflicts_precede_all_writes(self):
        for users,groups,subgid in [([user(uid=1003)],[group()],''),
                                   ([user('other')],[group()],''),
                                   ([user()],[group('other')],''),
                                   ([user()],[group(),group('docker',999,['forge'])],''),
                                   ([user()],[group()],'other:231072:65536\n')]:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); (root/'etc').mkdir()
                (root/'etc/subuid').write_text('ubuntu:100000:65536\n')
                (root/'etc/subgid').write_text(subgid)
                calls=[]
                with self.assertRaises(r.RootlessError):
                    r.identity(root,lambda args:calls.append(args),users,groups)
                self.assertEqual(calls,[])
                self.assertEqual((root/'etc/subuid').read_text(),'ubuntu:100000:65536\n')
                self.assertEqual((root/'etc/subgid').read_text(),subgid)

    def test_new_identity_has_explicit_ids_and_no_automatic_subids(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'etc').mkdir(); calls=[]
            r.identity(root,lambda args:calls.append(args),[],[])
            self.assertEqual(calls[0],['groupadd','--gid','1002','forge'])
            self.assertIn('SUB_UID_COUNT=0',calls[1])
            self.assertIn('SUB_GID_COUNT=0',calls[1])
            self.assertEqual((root/'etc/subuid').read_text(),'forge:231072:65536\n')
            calls.clear()
            r.identity(root,lambda args:calls.append(args),[user()],[group()])
            self.assertEqual(calls,[])

    def test_existing_home_without_account_refused_before_group_creation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'etc').mkdir(); (root/'home/forge').mkdir(parents=True)
            calls=[]
            with self.assertRaises(r.RootlessError): r.identity(root,lambda args:calls.append(args),[],[])
            self.assertEqual(calls,[])

    def setup_home(self,root):
        home=root/'home'; home.mkdir(); state=root/'state'; state.mkdir()
        return home,state

    def test_configuration_conflicts_preserve_content(self):
        for name in ('storage.conf','containers.conf'):
            with tempfile.TemporaryDirectory() as d,patch.object(r,'UID',os.getuid()),patch.object(r,'GID',os.getgid()):
                home,state=self.setup_home(Path(d)); config=home/'.config/containers'; config.mkdir(parents=True)
                p=config/name; p.write_text('unrelated configuration')
                with self.assertRaises(r.RootlessError): r.preflight(home,state)
                self.assertEqual(p.read_text(),'unrelated configuration')

    def test_storage_adoption_requires_matching_marker(self):
        with tempfile.TemporaryDirectory() as d,patch.object(r,'UID',os.getuid()),patch.object(r,'GID',os.getgid()):
            home,state=self.setup_home(Path(d)); graph=home/'.local/share/containers'; graph.mkdir(parents=True)
            (graph/'sentinel').write_text('unrelated storage')
            with self.assertRaises(r.RootlessError): r.preflight(home,state)
            (state/'rootless-policy.json').write_text(json.dumps(r.POLICY))
            r.preflight(home,state)
            self.assertEqual((graph/'sentinel').read_text(),'unrelated storage')

    def test_symlink_and_override_refused(self):
        with tempfile.TemporaryDirectory() as d,patch.object(r,'UID',os.getuid()),patch.object(r,'GID',os.getgid()):
            home,state=self.setup_home(Path(d)); (home/'.config').symlink_to(state,target_is_directory=True)
            with self.assertRaises(r.RootlessError): r.preflight(home,state)
            (home/'.config').unlink(); override=home/'.config/containers/containers.conf.d'; override.mkdir(parents=True)
            (override/'custom.conf').write_text('custom')
            with self.assertRaises(r.RootlessError): r.preflight(home,state)

    def test_info_checks_observed_capabilities(self):
        self.assertEqual(r.check_info(info())['podman'],'4.9.3')
        changes=[('host','cgroupVersion','v1'),('host','cgroupManager','cgroupfs'),
                 ('host','networkBackend','cni'),('store','graphDriverName','vfs'),
                 ('store','graphRoot','/srv/forge/containers'),('store','runRoot','/tmp/root'),
                 ('version','Version','5.0.0')]
        for section,key,value in changes:
            bad=info(); bad[section][key]=value
            with self.assertRaises(r.RootlessError): r.check_info(bad)
        bad=info(); bad['host']['security']['rootless']=False
        with self.assertRaises(r.RootlessError): r.check_info(bad)

    def test_missing_capability_never_publishes_receipt(self):
        with tempfile.TemporaryDirectory() as d,patch.object(r,'STATE',Path(d)):
            def runner(args,**kw):
                if args[:2]==['podman','info']: return json.dumps(info())
                return '0 0 1\n'
            with self.assertRaises(r.RootlessError): r.verify(runner)
            self.assertFalse((Path(d)/'rootless-toolchain.json').exists())

    def test_probes_always_run_as_forge_and_receipt_is_sanitized(self):
        with tempfile.TemporaryDirectory() as d,patch.object(r,'STATE',Path(d)):
            calls=[]
            def runner(args,**kw):
                calls.append((args,kw))
                if args[:2]==['podman','info']: return json.dumps(info())
                if args[:2]==['podman','unshare']: return '0 1002 1\n1 231072 65536\n'
                return 'gptclaw-generator-probe.service\nExecStart=/usr/bin/podman run'
            result=r.verify(runner)
            self.assertTrue(all(kw['user'] for _,kw in calls))
            self.assertEqual(result['status'],'passed')
            self.assertNotIn('auth',json.dumps(result))
            self.assertTrue((Path(d)/'rootless-toolchain.json').exists())

    def test_system_masks_precede_package_install_and_are_repeatable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'etc/systemd/system').mkdir(parents=True); (root/'var/lib/gptclaw').mkdir(parents=True)
            calls=[]
            r.prepare(root,lambda args:calls.append(args))
            for unit in r.SYSTEM_UNITS:
                self.assertEqual(os.readlink(root/'etc/systemd/system'/unit),'/dev/null')
            r.prepare(root,lambda args:calls.append(args))
            self.assertEqual(calls,[['systemctl','daemon-reload']]*2)
        script=(ROOT/'infra/dev-host/templates/bootstrap-forge.sh.tftpl').read_text()
        self.assertLess(script.index('rootless prepare'),script.index('host-tools phase base-packages'))

    def test_unknown_system_unit_or_engine_blocks_masks_without_changes(self):
        for conflict in ('unit','engine','storage'):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); units=root/'etc/systemd/system'; units.mkdir(parents=True)
                (root/'var/lib/gptclaw').mkdir(parents=True)
                if conflict=='unit': (units/'podman.socket').write_text('existing unit')
                elif conflict=='engine':
                    (root/'usr/bin').mkdir(parents=True); (root/'usr/bin/podman').touch()
                else:
                    (root/'var/lib/containers').mkdir(); (root/'var/lib/containers/sentinel').touch()
                calls=[]
                with self.assertRaises(r.RootlessError): r.prepare(root,lambda args:calls.append(args))
                self.assertFalse((units/'podman.service').exists())
                self.assertFalse((units/'podman.service').is_symlink())
                self.assertEqual(calls,[])

    def test_unmasked_or_active_system_unit_blocks_configuration(self):
        for status in ('active','enabled','loaded'):
            with self.assertRaises(r.RootlessError): r.check_system_units(lambda args:status)
        def runner(args): return 'masked' if 'LoadState' in args else 'inactive'
        r.check_system_units(runner)

    def test_probe_environment_drops_root_and_inherited_variables(self):
        with patch.object(r.subprocess,'run') as call:
            call.return_value.returncode=0; call.return_value.stdout='ok'
            r.command(['podman','info'],user=True)
            args=call.call_args.args[0]
            self.assertEqual(args[:7],['sudo','-u','forge','-H','env','-i','HOME=/home/forge'])
            self.assertIn('XDG_RUNTIME_DIR=/run/user/1002',args)
            self.assertEqual(args[-2:],['podman','info'])

    def test_engine_error_is_not_mistaken_for_absent_fixture(self):
        with patch.object(f.subprocess,'run') as call:
            call.return_value.returncode=125; call.return_value.stdout=''
            with self.assertRaises(f.FixtureError): f.owned_object('container','fixture','token')
            call.return_value.returncode=1
            self.assertFalse(f.owned_object('container','fixture','token'))

    def test_checkout_cannot_provision(self):
        result=subprocess.run(['python3',str(ROOT/'infra/dev-host/lib/rootless.py'),'identity'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0); self.assertIn('restricted',result.stdout)

    def test_fixture_template_has_bounds_and_loopback(self):
        state={'token':'0123456789ab','name':'gptclaw-sys001-0123456789ab','port':18081,'image':'sha256:'+'1'*64}
        unit=f.unit_text(state)
        for required in ('127.0.0.1:18081:8080','UserNS=keep-id','Pull=never','Restart=on-failure',
                         'StartLimitBurst=3','WantedBy=default.target','--memory=128m',
                         'timeout 120','mountpoint -q /srv/forge'):
            self.assertIn(required,unit)
        self.assertNotIn('Privileged=true',unit)
        self.assertRegex((ROOT/'examples/rootless-toolchain/Containerfile').read_text(),r'FROM docker.io/library/alpine@sha256:[0-9a-f]{64}')

    def test_cleanup_rejects_changed_unit_before_commands(self):
        with tempfile.TemporaryDirectory() as d,patch.object(f,'UNITS',Path(d)):
            state={'name':'gptclaw-sys001-0123456789ab','token':'0123456789ab','unit_sha256':'0'*64}
            unit=Path(d)/(state['name']+'.container'); unit.write_text('unrelated')
            with patch.object(f,'run') as runner:
                with self.assertRaises(f.FixtureError): f.cleanup(Path(d),state)
                runner.assert_not_called()
            self.assertEqual(unit.read_text(),'unrelated')

    def test_unrelated_container_cannot_be_removed(self):
        with patch.object(f,'run',return_value=json.dumps([{'Config':{'Labels':{'other':'value'}}}])):
            with self.assertRaises(f.FixtureError): f.owned_object('container','fixture','0123456789ab')

    def test_bad_fixture_path_rejected(self):
        for path in ('/srv/forge/projects/real-project','/tmp/gptclaw-sys001-0123456789ab','/srv/forge/projects/gptclaw-sys001-nothex'):
            with self.assertRaises(f.FixtureError): f.load(path)

    def test_profile_declares_rootless_dependencies(self):
        profile=json.loads((ROOT/'infra/dev-host/host-tools.json').read_text())
        names={c['package'] for c in profile['components'] if c['owner']=='SYS-001'}
        self.assertEqual(names,{'podman','uidmap','slirp4netns','fuse-overlayfs','netavark','aardvark-dns','dbus-user-session','crun','libpam-systemd'})
        script=(ROOT/'infra/dev-host/templates/bootstrap-forge.sh.tftpl').read_text()
        self.assertLess(script.index('rootless identity'),script.index('current_phase="project-volume"'))
        self.assertLess(script.index('mountpoint -q /srv/forge\nlog'),script.index('rootless configure'))
        self.assertLess(script.index('rootless verify'),script.index('host-tools finish'))

if __name__=='__main__': unittest.main(verbosity=2)
