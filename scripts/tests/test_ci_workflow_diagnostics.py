#!/usr/bin/env python3
"""CI diagnostics retain useful bounded failure output without leaking secrets."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('mobile_check', ROOT/'scripts/tests/check_mobile_template.py')
mobile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mobile)


class DiagnosticsTests(unittest.TestCase):
    def test_generated_workflow_selects_runner_before_artifact_upload(self):
        import yaml
        workflow = yaml.safe_load((ROOT/'templates/apps/releases/expo-react-native/1.2.0/.github/workflows/quality.yml').read_text())
        self.assertEqual(mobile.generated_script(workflow), 'python3 checks/gptclaw_quality.py verify --engine docker')

    def test_failure_excerpt_is_bounded_and_redacts_secret(self):
        token = 'gh'+'p_'+'a'*30
        text = mobile.failure_excerpt(b'x'*10000 + ('\nAudit failed '+token).encode())
        self.assertIn('Audit failed', text)
        self.assertNotIn(token, text)
        self.assertLessEqual(len(text), 8192)


if __name__ == '__main__':
    unittest.main()
