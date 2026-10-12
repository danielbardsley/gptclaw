#!/usr/bin/env python3
"""Offline database ownership, plan, redaction and compatibility failure tests."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from jsonschema import Draft202012Validator
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as a
import project_database as db
import project_groups as g
import project_templates as templates


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='run011-offline-');self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.projects=self.base/'projects';self.projects.mkdir();self.units=self.base/'units';self.units.mkdir()
        for target,key,value in [(a,'PROJECTS',self.projects),(a,'STORE',self.base/'runtime'),(a,'UNITS',self.units),(db,'BASE',self.base/'data'),(db,'mount',lambda:None)]:
            mocked=patch.object(target,key,value);mocked.start();self.addCleanup(mocked.stop)
        self.root=Path(a.create('db-fixture',template='notes-postgres',template_version='1.0.0')['root'])
        self.contract=a.target(self.root)[1]
        self.s=db.create(self.root,self.contract)

    def test_owned_runtime_store_can_allocate_without_volume_root_writes(self):
        base=a.STORE/'data/projects'
        with patch.object(db,'BASE',base):
            selected=db.create(self.projects/'owned-store',self.contract | {'project':self.contract['project'] | {'id':'owned-store'}})
            for directory in [a.STORE,base.parent,base,base/'owned-store']:
                self.assertEqual(directory.stat().st_uid,os.getuid())
                self.assertEqual(directory.stat().st_mode&0o777,0o700)
            self.assertEqual(db.state('owned-store')['active'],selected['active'])
    def test_legacy_store_refusal_precedes_allocation_and_execution(self):
        legacy=self.base/'legacy';legacy.mkdir();(legacy/'retained').write_text('untouched synthetic marker')
        base=a.STORE/'data/projects'
        # Exercise the production mount function rather than this suite's fixture bypass.
        import importlib.util
        spec=importlib.util.spec_from_file_location('storage_probe',Path(db.__file__))
        probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
        with patch.object(probe,'BASE',base),patch.object(probe,'LEGACY_BASE',legacy),patch.object(a,'command') as command:
            with self.assertRaises(a.AppError) as error:probe.create(self.projects/'legacy-target',self.contract)
            self.assertEqual(error.exception.code,'database-storage');command.assert_not_called()
        self.assertFalse(base.exists());self.assertEqual((legacy/'retained').read_text(),'untouched synthetic marker')
    def test_storage_selector_required_before_database_state_or_secret_access(self):
        legacy=copy.deepcopy(self.contract);legacy['database'].pop('storage');a.save(self.root/'.gptclaw/project.yaml',legacy)
        with patch.object(db,'state') as state,patch.object(db,'acquire') as acquire:
            observed=db.dispatch(self.root,'status');self.assertEqual(observed['state'],'storage-upgrade-required')
            with self.assertRaises(a.AppError) as error:db.dispatch(self.root,'init')
            self.assertEqual(error.exception.code,'database-storage');state.assert_not_called();acquire.assert_not_called()
    def test_old_strict_schema_refuses_new_storage_selector(self):
        schema=json.loads((a.REPO/'schemas/project/v4.schema.json').read_text())
        old=copy.deepcopy(schema);old['properties']['database']['properties'].pop('storage')
        self.assertTrue(Draft202012Validator(schema).is_valid(self.contract))
        self.assertFalse(Draft202012Validator(old).is_valid(self.contract))
        legacy=copy.deepcopy(self.contract);legacy['database'].pop('storage')
        self.assertTrue(Draft202012Validator(old).is_valid(legacy))
    def test_generation_validation_never_reads_credentials_or_executes(self):
        with patch.object(a,'command') as command,patch.object(db,'credential') as credential:
            self.assertEqual(a.validate_project(self.root)[2],0)
            templates.validate_provenance(self.root)
            command.assert_not_called();credential.assert_not_called()
        for edit in [lambda c:c['components']['db'].update(image='untrusted'),lambda c:c['components']['api'].update(depends_on=[]),lambda c:c['data'].update(mode='ephemeral'),lambda c:c['database'].update(migrate=['sh','-c','unsafe']),lambda c:c['database'].update(storage='/unapproved/path'),lambda c:c['components'].update(worker={})]:
            value=copy.deepcopy(self.contract);edit(value);a.save(self.root/'.gptclaw/project.yaml',value)
            self.assertNotEqual(a.validate_project(self.root)[2],0)

    def test_private_roles_unique_and_values_absent_from_metadata(self):
        values=[db.credential(self.s,role)['password'] for role in db.ROLES]
        self.assertEqual(len(set(values)),3)
        text=db.unit_text(self.s)+json.dumps(db.state('db-fixture',self.root))
        for value in values:self.assertNotIn(value,text)
        self.assertNotIn('PublishPort',db.unit_text(self.s))
        self.assertIn('POSTGRES_PASSWORD_FILE=',db.unit_text(self.s))

    def test_existing_root_never_overwritten(self):
        marker=(db.home('db-fixture')/'owner.json').read_bytes()
        with self.assertRaises(a.AppError):db.create(self.root,self.contract)
        self.assertEqual(marker,(db.home('db-fixture')/'owner.json').read_bytes())

    def test_grants_transfer_only_retained_migration_ownership(self):
        next_epoch='f'*32;db.credentials(db.home('db-fixture'),next_epoch)
        old=db.credential(self.s,'migration')['username']
        selected=db.credential(self.s,'migration',next_epoch)['username']
        with patch.object(db,'sql') as sql:
            db.grants(self.s,epoch=next_epoch)
        statement=sql.call_args.args[1]
        self.assertIn(f'REASSIGN OWNED BY {old} TO {selected}',statement)
        self.assertNotIn('REASSIGN OWNED BY admin_',statement)
        self.assertNotIn('REASSIGN OWNED BY runtime_',statement)
        self.assertNotIn(f'REASSIGN OWNED BY {selected}',statement)
        self.assertLess(statement.index('REASSIGN OWNED'),statement.index('ALTER SCHEMA public OWNER'))

    def test_interrupted_rotation_blocks_readiness_until_recovered(self):
        self.s.update(revision='0001',blocked=False)
        self.s['operation']={'id':'f'*32,'action':'rotate','stage':'planned'}
        with patch.object(db,'active',return_value=True),patch.object(db,'revision',return_value='0001'):
            self.assertTrue(db.ready(self.s,self.contract))
            for stage in ('running','failed','unknown'):
                self.s['operation']['stage']=stage
                self.assertFalse(db.ready(self.s,self.contract))
            self.s['operation']['stage']='complete'
            self.assertTrue(db.ready(self.s,self.contract))

    def test_missing_data_never_reinitialized(self):
        (db.home('db-fixture')/'postgres'/self.s['active']).rmdir()
        with self.assertRaises(a.AppError):db.state('db-fixture',self.root)
        self.assertFalse((db.home('db-fixture')/'postgres'/self.s['active']).exists())

    def test_foreign_major_root_and_symlink_refused(self):
        for field,value in [('major',17),('root',str(self.projects/'other')),('image','foreign')]:
            selected=copy.deepcopy(self.s);selected[field]=value;db.save(selected)
            with self.assertRaises(a.AppError):db.state('db-fixture',self.root)
        db.save(self.s)
        path=db.home('db-fixture')/'credentials'/self.s['epoch']/'runtime.json'
        saved=path.read_bytes();path.unlink();path.symlink_to('/dev/null')
        with self.assertRaises(a.AppError):db.credential(self.s,'runtime')
        path.unlink();path.write_bytes(saved);path.chmod(0o644)
        with self.assertRaises(a.AppError):db.credential(self.s,'runtime')

    def test_plan_bound_to_target_source_epoch_and_confirmation(self):
        with patch.object(db,'stopped'):
            plan=db.plan(self.root,self.contract,self.s,'reset')
            with self.assertRaises(a.AppError) as failure:db.apply(self.root,self.contract,self.s,plan['operation_id'],'other')
            self.assertEqual(failure.exception.code,'database-confirmation')
            path=self.root/'api/src/fastapi_app/db_cli.py';path.write_text(path.read_text()+'\n# edit after preview\n')
            with patch.object(db,'start') as start:
                with self.assertRaises(a.AppError) as failure:db.apply(self.root,self.contract,self.s,plan['operation_id'],'db-fixture')
                self.assertEqual(failure.exception.code,'database-plan');start.assert_not_called()

    def test_mount_failure_precedes_any_creation(self):
        with patch.object(db,'mount',side_effect=a.AppError('database-storage')):
            with self.assertRaises(a.AppError):db.create(self.projects/'other',self.contract)
        self.assertFalse((db.BASE/'other').exists())

    def test_major_mismatch_precedes_container_mount(self):
        self.s['revision']='0001';db.save(self.s)
        pg=db.home('db-fixture')/'postgres'/self.s['active']/'PG_VERSION';pg.write_text('17\n')
        with patch.object(a,'command') as command:
            with self.assertRaises(a.AppError):db.start(self.s)
            command.assert_not_called()

    def test_unknown_backup_and_only_verified_pruning_refused(self):
        with patch.object(db,'stopped'):
            with self.assertRaises(a.AppError):db.plan(self.root,self.contract,self.s,'restore','0'*32)
            with self.assertRaises(a.AppError):db.plan(self.root,self.contract,self.s,'prune','0'*32)

    def test_owned_quadlet_activation_refuses_overrides_and_uses_private_unit(self):
        def command(args,**kwargs):
            return SimpleNamespace(returncode=0,stdout='SourcePath='+str(db.unit(self.s))+'\nDropInPaths=\n')
        with patch.object(db,'active',return_value=False),patch.object(db,'network'),patch.object(db,'sql',return_value='1'),patch.object(a,'command',side_effect=command):
            db.start(self.s)
        self.assertEqual(db.unit(self.s).stat().st_mode&0o777,0o600)
        with patch.object(a,'command',return_value=SimpleNamespace(stdout='SourcePath='+str(db.unit(self.s))+'\nDropInPaths=/unknown\n')):
            with self.assertRaises(a.AppError):db.verify_unit(self.s)

    def test_unit_bootstrap_is_immutable_and_known_path_reconciliation_is_exact(self):
        relative=Path('templates/apps/start-development-postgres.sh')
        trusted=a.provider_bundle()/relative
        self.assertIn(str(trusted),db.unit_text(self.s))
        source=a.PROJECTS/'gptclaw'/relative;source.parent.mkdir(parents=True)
        source.write_bytes(trusted.read_bytes())
        expected=db.unit_text(self.s);legacy=expected.replace(str(trusted),str(source))
        db.unit(self.s).write_text(legacy);db.unit(self.s).chmod(0o600)
        observed=SimpleNamespace(stdout='SourcePath='+str(db.unit(self.s))+'\nDropInPaths=\n')
        with patch.object(a,'command',return_value=observed):db.verify_unit(self.s)
        with patch.object(a,'command') as command:
            for invalid in [legacy.replace('PidsLimit=128','PidsLimit=129'),legacy.replace(str(source),str(self.base/'unknown.sh'))]:
                db.unit(self.s).write_text(invalid)
                with self.assertRaises(a.AppError):db.verify_unit(self.s)
            db.unit(self.s).write_text(legacy);source.write_bytes(b'unknown changed bootstrap')
            with self.assertRaises(a.AppError):db.verify_unit(self.s)
            command.assert_not_called()

    def test_old_manifests_and_snapshot_are_preserved(self):
        for slug,template,version in [('web-old','nextjs','1.0.0'),('api-old','fastapi','1.0.0'),('group-old','notes','1.0.0')]:
            root=Path(a.create(slug,template=template,template_version=version)['root'])
            self.assertIn(a.target(root)[1]['schema_version'],[1,2,3])
        paths=templates.bundle_paths()
        self.assertIn(Path('config/templates/v4.json'),paths)
        self.assertIn(Path('schemas/templates/v4.schema.json'),paths)


if __name__=='__main__':unittest.main(verbosity=2)
