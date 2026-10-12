#!/usr/bin/env python3
"""Prevent starter overlays from hiding evolved application verification failures."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('database_check',Path(__file__).with_name('check_database_template.py'))
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)


class SourceTests(unittest.TestCase):
    def test_removed_migrations_tests_and_browser_checks_match_source(self):
        with tempfile.TemporaryDirectory(prefix='db-source-test-') as directory:
            base=Path(directory);root=base/'fixture';source=base/'application'
            for component in ['api','web','checks']:
                (root/component/'.gptclaw').mkdir(parents=True)
                (root/component/'.gptclaw/provenance.json').write_text('retained')
                (root/component/'old_starter.py').write_text('obsolete')
                (source/component).mkdir(parents=True)
                (source/component/'application.py').write_text('current '+component)
            for part in ['api/migrations/versions','api/tests']:
                (root/part).mkdir(parents=True);(root/part/'notes.py').write_text('removed')
                (source/part).mkdir(parents=True);(source/part/'library.py').write_text('selected')
            (source/'api/.venv').mkdir();(source/'api/.venv/ignored').write_text('cache')
            (source/'checks/browser.cjs').write_text('selected browser')
            contract={'components':{'api':{'root':'api'},'web':{'root':'web'}}}
            check.replace_fixture_source(root,source,contract)
            for component in ['api','web','checks']:
                self.assertEqual((root/component/'.gptclaw/provenance.json').read_text(),'retained')
                self.assertEqual((root/component/'application.py').read_text(),'current '+component)
                self.assertFalse((root/component/'old_starter.py').exists())
            for part in ['api/migrations/versions','api/tests']:
                self.assertFalse((root/part/'notes.py').exists())
                self.assertEqual((root/part/'library.py').read_text(),'selected')
            self.assertFalse((root/'api/.venv').exists())
            self.assertEqual((root/'checks/browser.cjs').read_text(),'selected browser')
            self.assertEqual((source/'checks/browser.cjs').read_text(),'selected browser')


if __name__=='__main__':unittest.main(verbosity=2)
