#!/usr/bin/env python3
"""Offline archive safety and retained-fixture tests for the Android appliance."""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import textwrap
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("android_runner", ROOT / "infra/dev-host/lib/android_runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def archive(entries):
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w") as zipped:
        for name, content in entries:
            zipped.writestr(name, content)
    return result.getvalue()


class AndroidRunnerTests(unittest.TestCase):
    def test_reject_traversal_absolute_and_other_package_before_writing(self):
        for name in ["fixture/../escape", "/fixture/absolute", "other/file", "fixture\\escape"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                destination = Path(temp) / "out"
                destination.mkdir()
                payload = archive([("fixture/valid", "ok"), (name, "bad")])
                with self.assertRaises(ValueError):
                    runner.unpack(io.BytesIO(payload), destination, "fixture")
                self.assertEqual(list(destination.iterdir()), [])

    def test_reject_symlinks(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as zipped:
            entry = zipfile.ZipInfo("fixture/link")
            entry.external_attr = 0o120777 << 16
            zipped.writestr(entry, "../../outside")
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(ValueError):
            runner.unpack(io.BytesIO(payload.getvalue()), Path(temp), "fixture")

    def test_checksum_failure_never_installs_package(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            item = {"url": "https://example.invalid/fixture.zip", "sha256": "0" * 64,
                    "bytes": 3, "prefix": "fixture", "destination": "sdk/fixture"}
            with patch.object(runner.urllib.request, "urlopen", return_value=io.BytesIO(b"bad")):
                with self.assertRaises(ValueError):
                    runner.install(base, item)
            self.assertFalse((base / "sdk/fixture").exists())
            self.assertEqual(list((base / "downloads").glob("*.partial")), [])

    def test_idempotent_install_preserves_runtime_files_and_unknown_destination(self):
        content = archive([("fixture/bin/tool", "fixture")])
        item = {"url": "https://example.invalid/fixture.zip",
                "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content),
                "prefix": "fixture", "destination": "sdk/fixture"}
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            with patch.object(runner.urllib.request, "urlopen", return_value=io.BytesIO(content)):
                runner.install(base, item)
            retained = base / "sdk/fixture/retained-test-data"
            retained.write_text("keep")
            with patch.object(runner.urllib.request, "urlopen", side_effect=AssertionError("network rerun")):
                runner.install(base, item)
            self.assertEqual(retained.read_text(), "keep")
            (base / "sdk/fixture/.gptclaw-sha256").unlink()
            with self.assertRaises(ValueError):
                runner.install(base, item)
            self.assertEqual(retained.read_text(), "keep")

    def test_ssh_validation_handles_missing_runtime_directory(self):
        template = (ROOT / "infra/dev-host/templates/android-runner.yaml.tftpl").read_text()
        bootstrap = template.split("      ufw --force enable\n", 1)[1].split(
            "      systemctl reload-or-restart ssh.service", 1)[0]
        # Model socket activation: sshd -t fails until its runtime directory exists.
        # Stub privileged commands; never create /run/sshd on the test host.
        harness = r'''set -e
install() {
  test "$*" = "-d -o root -g root -m 0755 /run/sshd"
  mkdir -p -m 0755 "$FIXTURE/sshd"
}
sshd() { test "$1" = "-t" && test -d "$FIXTURE/sshd"; }
'''
        with tempfile.TemporaryDirectory() as temp:
            env = dict(os.environ, FIXTURE=temp)
            missing = subprocess.run(["bash", "-c", harness + "sshd -t"], env=env,
                                     capture_output=True, text=True)
            self.assertNotEqual(missing.returncode, 0)
            for _ in range(2):
                result = subprocess.run(["bash", "-c", harness + textwrap.dedent(bootstrap)],
                                        env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((Path(temp) / "sshd").stat().st_mode & 0o777, 0o755)

    def test_live_bootstrap_is_scoped_and_uses_verified_pins(self):
        pins = json.loads((ROOT / "infra/dev-host/android-runner-artifacts.json").read_text())
        self.assertEqual(set(pins), {"platform-tools", "emulator", "android-36-google-apis-x86_64"})
        for item in pins.values():
            self.assertTrue(item["url"].startswith("https://dl.google.com/android/repository/"))
            self.assertRegex(item["sha256"], r"^[a-f0-9]{64}$")
            self.assertNotIn("..", Path(item["destination"]).parts)
        bootstrap = (ROOT / "infra/dev-host/templates/android-runner.yaml.tftpl").read_text()
        self.assertIn("OnBootSec=4h", bootstrap)
        self.assertIn("User=forge", bootstrap)
        self.assertIn("-accel on", bootstrap)
        self.assertNotIn("/srv/forge", bootstrap)
        self.assertNotIn("NOPASSWD", bootstrap)


if __name__ == "__main__":
    unittest.main()
