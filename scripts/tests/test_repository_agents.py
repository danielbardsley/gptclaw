#!/usr/bin/env python3
"""Narrow, offline checks for the shipped repository-guidance contract.

This is not a general Markdown parser or policy execution engine. See
../../templates/agents/README.md for the supported authoring/link syntax.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates/agents/AGENTS.md.template"
FIXTURE = ROOT / "scripts/tests/fixtures/repository-agents"
MAX_BYTES = 8192
SECTIONS = (
    "Project and ownership",
    "Stack and layout",
    "Commands and quality gates",
    "Planning and delivery",
    "Data and product constraints",
    "Guidance maintenance",
)
PLACEHOLDERS = {
    "PROJECT_NAME",
    "PROJECT_PURPOSE_AND_OWNER",
    "STACK_VERSION_SOURCES_AND_LAYOUT",
    "COMMAND_TABLE",
    "PLANNING_AND_REVIEW_REFERENCES",
    "DATA_RULES_AND_PRODUCT_BOUNDARIES",
    "GUIDANCE_OWNER_AND_PROCEDURE",
}
LINK = re.compile(r"\[[^\]\n]+\]\(([^\n)]*)\)")


def validate_policy(path, root, *, template=False, max_bytes=MAX_BYTES,
                    sections=SECTIONS, placeholder_names=PLACEHOLDERS):
    """Read only the supplied policy; stat local targets without reading them.

    All links must use simple inline Markdown, no titles/spaces/parentheses.
    External HTTPS/HTTP links and fragments are not fetched or anchor-checked.
    Local targets must exist and resolve within the explicit repository root.
    """
    root = root.resolve()
    if not path.resolve().is_relative_to(root):
        raise ValueError("policy is outside repository")
    with path.open("rb") as source:
        raw = source.read(max_bytes + 1)
    if not raw or len(raw) > max_bytes:
        raise ValueError(f"policy must be nonempty and at most {max_bytes} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("policy must be UTF-8") from error
    if "\x00" in text or text.startswith("\ufeff"):
        raise ValueError("policy must be plain UTF-8 without NUL or BOM")
    # Ignore fenced examples so fake headings inside them cannot satisfy checks.
    prose = re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$", "", text)
    headings = list(re.finditer(r"(?m)^## (.+)$", prose))
    for section in sections:
        matches = [i for i, heading in enumerate(headings) if heading[1] == section]
        if len(matches) != 1:
            raise ValueError(f"expected one section: {section}")
        index = matches[0]
        end = headings[index + 1].start() if index + 1 < len(headings) else len(prose)
        if not prose[headings[index].end():end].strip():
            raise ValueError(f"empty section: {section}")
    key = "Template-Version" if template else "Source-Template-Version"
    if not re.search(rf"(?m)^{key}: [0-9]+\.[0-9]+\.[0-9]+$", text):
        raise ValueError(f"missing or invalid {key}")
    if not re.search(r"(?m)^Template-Source: \S[^\n]+$", text):
        raise ValueError("missing template source")
    placeholders = set(re.findall(r"\{\{([A-Z][A-Z0-9_]*)\}\}", text))
    if template:
        if placeholders != placeholder_names:
            raise ValueError("template placeholder contract changed")
        remaining = re.sub(r"\{\{[A-Z][A-Z0-9_]*\}\}", "", text)
    else:
        remaining = text
    if "{{" in remaining or "}}" in remaining:
        raise ValueError("unresolved or malformed authoring placeholder")
    # Reject unsupported reference links rather than silently ignoring them.
    if re.search(r"(?m)^\s*\[[^\]]+\]:|\[[^\]\n]+\]\[[^\]\n]*\]", prose):
        raise ValueError("use inline Markdown links")
    if prose.count("](") != len(LINK.findall(prose)):
        raise ValueError("malformed inline link")
    for target in LINK.findall(prose):
        if not target or re.search(r"[\s()<>]", target):
            raise ValueError("unsupported link syntax")
        parts = urlsplit(target)
        if parts.scheme in {"http", "https"} and parts.netloc:
            continue
        if parts.scheme or parts.netloc or parts.query:
            raise ValueError("unsupported link scheme or query")
        if not parts.path:  # Fragment only: anchor validation is out of scope.
            continue
        local = Path(unquote(parts.path))
        if local.is_absolute():
            raise ValueError("local links must be repository-relative")
        resolved = (path.parent / local).resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("local link escapes repository")
        if not resolved.exists():
            raise ValueError("broken local link")
    return len(raw)


def materialize_fixture(destination):
    """Copy only the three known synthetic files into a caller-owned directory."""
    for name in ("README.md", "verify.py"):
        shutil.copyfile(FIXTURE / name, destination / name)
    shutil.copyfile(FIXTURE / "AGENTS.md.fixture", destination / "AGENTS.md")


class RepositoryAgentsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="gptclaw-agt002-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        materialize_fixture(self.root)
        self.policy = self.root / "AGENTS.md"
        self.original = self.policy.read_text()

    def check_invalid(self, text, message):
        self.policy.write_text(text)
        with self.assertRaisesRegex(ValueError, message):
            validate_policy(self.policy, self.root)

    def test_shipped_contracts(self):
        validate_policy(TEMPLATE, ROOT, template=True)
        validate_policy(ROOT / "AGENTS.md", ROOT)
        validate_policy(self.policy, self.root)

    def test_template_can_be_fully_adapted(self):
        values = {"PROJECT_NAME": "Pebble Counter"}
        headings = list(re.finditer(r"(?m)^## (.+)$", self.original))
        for heading, placeholder in zip(headings, (
            "PROJECT_PURPOSE_AND_OWNER", "STACK_VERSION_SOURCES_AND_LAYOUT",
            "COMMAND_TABLE", "PLANNING_AND_REVIEW_REFERENCES",
            "DATA_RULES_AND_PRODUCT_BOUNDARIES", "GUIDANCE_OWNER_AND_PROCEDURE",
        )):
            index = headings.index(heading)
            end = headings[index + 1].start() if index + 1 < len(headings) else len(self.original)
            values[placeholder] = self.original[heading.end():end].strip()
        adapted = TEMPLATE.read_text().replace("\nTemplate-Version:", "\nSource-Template-Version:")
        for key, value in values.items():
            adapted = adapted.replace("{{" + key + "}}", value)
        self.policy.write_text(adapted)
        validate_policy(self.policy, self.root)

    def test_missing_duplicate_and_empty_sections(self):
        for section in SECTIONS:
            with self.subTest(section=section):
                self.check_invalid(self.original.replace("## " + section, "### " + section), "section")
                self.check_invalid(self.original + "\n## " + section + "\nDuplicate\n", "section")
        self.check_invalid(re.sub(
            r"(?s)(## Project and ownership).*?(## Stack and layout)",
            r"\1\n\n\2", self.original), "empty section")

    def test_placeholders_and_metadata(self):
        for token in ("{{UNFILLED}}", "{{bad token}}", "{{UNCLOSED", "STRAY}}"):
            with self.subTest(token=token):
                self.check_invalid(self.original + token, "placeholder")
        self.check_invalid(self.original.replace("Source-Template-Version: 1.0.0", ""), "Version")
        self.check_invalid(self.original.replace("1.0.0", "latest"), "Version")
        self.check_invalid(self.original.replace("Template-Source:", "Source:"), "template source")

    def test_size_and_encoding(self):
        base = self.original.encode()
        self.policy.write_bytes(base + b" " * (MAX_BYTES - len(base)))
        self.assertEqual(validate_policy(self.policy, self.root), MAX_BYTES)
        for raw in (b"", base + b" " * (MAX_BYTES + 1 - len(base)),
                    base + b"\xff", base + b"\x00", b"\xef\xbb\xbf" + base,
                    base + "\u00e9".encode() * MAX_BYTES):
            with self.subTest(length=len(raw)):
                self.policy.write_bytes(raw)
                with self.assertRaises(ValueError):
                    validate_policy(self.policy, self.root)

    def test_missing_escaping_and_unsupported_links(self):
        for target, error in (("missing.md", "broken"), ("../outside.md", "escapes"),
                              ("%2e%2e/outside.md", "escapes"), ("/etc/passwd", "relative"),
                              ("file:///etc/passwd", "scheme"), ("//example.test/a", "scheme"),
                              ('README.md "title"', "syntax"), ("README.md?x=1", "query")):
            with self.subTest(target=target):
                self.check_invalid(self.original + f"\n[bad]({target})", error)
        self.check_invalid(self.original + "\n[ref][x]\n[x]: README.md", "inline")

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory(prefix="gptclaw-agt002-outside-") as other:
            outside = Path(other) / "sentinel"
            outside.write_text("synthetic content must not be read")
            (self.root / "escape").symlink_to(outside)
            self.check_invalid(self.original + "\n[bad](escape)", "escapes")

    def test_validation_never_executes_or_fetches_or_changes_files(self):
        sentinel = self.root / "executed"
        self.policy.write_text(self.original +
            "\nCommand example: `touch executed`\n[external](https://example.invalid/policy)\n")
        before = {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.root.iterdir()}
        with mock.patch("subprocess.run", side_effect=AssertionError("execution")), \
                mock.patch("os.system", side_effect=AssertionError("execution")), \
                mock.patch("socket.socket", side_effect=AssertionError("network")):
            validate_policy(self.policy, self.root)
        self.assertFalse(sentinel.exists())
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.root.iterdir()})

    def test_synthetic_command(self):
        # Explicit test of known fixture code, not a command extracted from policy.
        result = subprocess.run(["python3", str(self.root / "verify.py")],
                                cwd=self.root, check=True, capture_output=True, text=True)
        self.assertIn("total is 10", result.stdout)

    def test_targeted_git_rollback_preserves_later_work(self):
        # Use only task-owned Git config; never inherit host credentials or hooks.
        env = {"PATH": os.defpath, "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
        def git(*args):
            return subprocess.run(
                ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                 "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                cwd=self.root, env=env, check=True, capture_output=True, text=True).stdout.strip()
        git("init", "--quiet")
        git("add", "README.md", "verify.py")
        git("commit", "-qm", "Synthetic baseline")
        git("add", "AGENTS.md")
        git("commit", "-qm", "Adopt guidance")
        adoption = git("rev-parse", "HEAD")
        self.policy.write_text(self.original.replace("# Pebble Counter repository guidance",
                                                       "# Pebble Counter updated guidance"))
        git("add", "AGENTS.md")
        git("commit", "-qm", "Update guidance")
        update = git("rev-parse", "HEAD")
        readme = self.root / "README.md"
        readme.write_text(readme.read_text() + "\nUnrelated later documentation.\n")
        git("add", "README.md")
        git("commit", "-qm", "Unrelated documentation")
        (self.root / "user-note.txt").write_text("Uncommitted user note\n")
        git("revert", "--no-edit", update)
        self.assertEqual(self.policy.read_text(), self.original)
        validate_policy(self.policy, self.root)
        git("revert", "--no-edit", adoption)
        self.assertFalse(self.policy.exists())
        self.assertIn("Unrelated later documentation", readme.read_text())
        self.assertEqual((self.root / "user-note.txt").read_text(), "Uncommitted user note\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
