"""Prove quality thresholds and vulnerability-service failure propagation."""

import subprocess
from pathlib import Path

import pytest
import quality


def test_missing_and_low_critical_coverage() -> None:
    """Reject missing modules, empty branches and low critical coverage."""
    with pytest.raises(ValueError):
        quality.check_coverage({"files": {}})
    files = {
        str(path): {
            "summary": {
                "num_statements": 10,
                "covered_lines": 9,
                "num_branches": 10,
                "covered_branches": 9,
            }
        }
        for path in Path("src/fastapi_app").rglob("*.py")
        if path.name != "__init__.py"
    }
    quality.check_coverage({"files": files})
    for info in files.values():
        info["summary"]["covered_branches"] = 7
    with pytest.raises(ValueError):
        quality.check_coverage({"files": files})


@pytest.mark.parametrize("returncode", [1, 2])
def test_audit_findings_or_unavailable_data_fail(
    monkeypatch: pytest.MonkeyPatch, returncode: int
) -> None:
    """Treat findings and failed advisory access as failed security checks."""

    def scan(module: str, *args: str, timeout: int = 120) -> None:
        """Simulate exact scanner findings/failure without contacting a service."""
        if module == "pip_audit":
            assert "--disable-pip" in args and "--require-hashes" in args
            assert "--fix" not in args
            raise subprocess.CalledProcessError(returncode, [module])

    def export(
        *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        """Simulate the bounded already-locked graph export."""
        return subprocess.CompletedProcess([], 0, "", "")

    monkeypatch.setattr(quality, "run", scan)
    monkeypatch.setattr(subprocess, "run", export)
    with pytest.raises(subprocess.CalledProcessError):
        quality.security()


def test_verify_propagates_each_failed_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Never turn an earlier check failure into successful verify."""

    def failed(*args: str, timeout: int = 120) -> None:
        """Represent a failed installed lint tool."""
        raise subprocess.CalledProcessError(1, list(args))

    monkeypatch.setattr(quality, "run", failed)
    with pytest.raises(subprocess.CalledProcessError):
        quality.main("verify")
    with pytest.raises(ValueError):
        quality.main("unknown")
