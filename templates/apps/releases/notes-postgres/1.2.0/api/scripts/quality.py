"""Run the pinned checks inside the already prepared project container."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI

from fastapi_app.main import create_app


def run(module: str, *args: str, timeout: int = 120) -> None:
    """Execute one installed tool with no shell or implicit dependency sync."""
    subprocess.run(
        [sys.executable, "-m", module, *args], check=True, timeout=timeout
    )


def check_coverage(data: dict[str, Any]) -> None:
    """Require meaningful statement and branch coverage of every source module."""
    expected = {
        str(p)
        for p in Path("src/fastapi_app").rglob("*.py")
        if p.name != "__init__.py"
    }
    if not expected or not expected <= set(data["files"]):
        raise ValueError("Critical coverage modules are missing.")
    summaries = [data["files"][name]["summary"] for name in expected]
    for covered, total in [
        ("covered_lines", "num_statements"),
        ("covered_branches", "num_branches"),
    ]:
        denominator = sum(s[total] for s in summaries)
        numerator = sum(s[covered] for s in summaries)
        if not denominator or numerator / denominator < 0.8:
            raise ValueError(f"Critical {covered} coverage is below 80%.")


def build() -> None:
    """Construct the app and validate its OpenAPI without opening a socket."""
    app = create_app()
    child = cast(FastAPI, app.state.child)
    schema = child.openapi()
    paths = schema["paths"]
    if not {"/api/v1/notes", "/api/v1/notes/{note_id}"} <= set(paths):
        raise ValueError("Required API routes are missing.")
    output = Path(".gptclaw-cache")
    output.mkdir(exist_ok=True)
    (output / "openapi.json").write_text(json.dumps(schema, indent=2) + "\n")


def security() -> None:
    """Check source and the exact lock graph without install, resolution or fixes."""
    run("bandit", "-r", "src", "-q")
    output = Path(".gptclaw-cache")
    output.mkdir(exist_ok=True)
    lock_export = output / "audit-requirements.txt"
    subprocess.run(
        [
            "uv",
            "export",
            "--locked",
            "--offline",
            "--no-config",
            "--no-python-downloads",
            "--cache-dir=.gptclaw-cache/uv",
            "--all-groups",
            "--no-emit-project",
            "--no-header",
            "--no-annotate",
            "--output-file",
            str(lock_export),
        ],
        check=True,
        timeout=30,
        stdout=subprocess.DEVNULL,
    )
    run(
        "pip_audit",
        "--vulnerability-service=pypi",
        "--require-hashes",
        "--no-deps",
        "--disable-pip",
        "--timeout",
        "15",
        "--cache-dir",
        str(output / "advisories"),
        "-r",
        str(lock_export),
        timeout=120,
    )


def main(action: str) -> None:
    """Run one action and propagate all quality failures."""
    if action == "format":
        run("isort", "src", "scripts", "tests")
        run("black", "src", "scripts", "tests")
    elif action == "lint":
        run("isort", "--check-only", "src", "scripts", "tests")
        run("black", "--check", "src", "scripts", "tests")
        run("ruff", "check", "src", "scripts", "tests")
    elif action == "typecheck":
        run("mypy")
    elif action == "test":
        Path(".gptclaw-cache").mkdir(exist_ok=True)
        run("coverage", "run", "-m", "pytest")
        run("coverage", "json")
        data = json.loads(Path(".gptclaw-cache/coverage.json").read_text())
        check_coverage(data)
        print("Critical statement and branch coverage each passed 80%.")
    elif action == "security":
        security()
    elif action == "build":
        build()
    elif action == "verify":
        for gate in ("lint", "typecheck", "test", "security", "build"):
            main(gate)
    else:
        raise ValueError("Unknown quality action.")


if __name__ == "__main__":
    main(sys.argv[1])
