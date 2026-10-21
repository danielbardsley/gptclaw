"""Operational API boundaries and deterministic native contract provenance."""

import json
import logging
from pathlib import Path
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from fastapi_app.api.middleware import Admission
from fastapi_app.domain.notes import Note, NoteInput
from fastapi_app.main import create_app
from fastapi_app.services.notes import NotesService
from fastapi_app.settings import Settings
from fastapi_app.utils.logging import JsonFormatter

PREFIX = "/projects/example-api"


def test_native_contract_matches_python_openapi() -> None:
    """Refuse checked-in client contract drift without opening a database socket."""
    schema = create_app(Settings()).state.child.openapi()
    schema.pop("servers", None)
    assert schema == json.loads(Path("contract/openapi.json").read_text())
    assert set(schema["paths"]) == {
        "/api/v1/notes",
        "/api/v1/notes/{note_id}",
    }


def test_health_docs_validation_and_missing_routes() -> None:
    """Retain operational support while removing unrelated starter endpoints."""
    with TestClient(create_app(Settings()), follow_redirects=False) as client:
        assert client.get(PREFIX + "/api/health").status_code == 200
        assert client.get(PREFIX + "/api/ready").status_code == 200
        docs = client.get(PREFIX + "/api/docs")
        assert docs.status_code == 200
        assert PREFIX + "/api/openapi.json" in docs.text
        assert client.get(PREFIX + "/api/docs/").status_code == 307
        assert client.get(PREFIX + "/api/openapi.json").status_code == 200
        assert client.get(PREFIX + "/api/v1/echo").status_code == 404
        assert client.get(PREFIX + "/api/v1/examples").status_code == 404
        invalid = client.post(PREFIX + "/api/v1/notes", json={"title": ""})
        assert invalid.status_code == 422
        assert invalid.json() == {"detail": "Invalid request."}
        assert (
            client.get(PREFIX + "/api/v1/notes?limit=101").status_code == 422
        )


@pytest.fixture
def app() -> FastAPI:
    """Construct operational test state with actual fixture database."""
    return create_app(Settings())


def test_health_and_readiness(app: FastAPI) -> None:
    """Distinguish initialization/shutdown readiness from liveness."""
    child = cast(FastAPI, app.state.child)
    with TestClient(app) as client:
        assert client.get(PREFIX + "/api/health").json() == {"status": "alive"}
        assert client.get(PREFIX + "/api/ready").status_code == 200
        child.state.ready = False
        assert client.get(PREFIX + "/api/ready").status_code == 503
    assert child.state.ready is False


def test_docs_contract_and_relative_redirects(app: FastAPI) -> None:
    """Keep docs, local assets and redirects under the private project prefix."""
    with TestClient(app, follow_redirects=False) as client:
        docs = client.get(PREFIX + "/api/docs")
        assert docs.status_code == 200
        assert "https://cdn" not in docs.text
        assert PREFIX + "/api/openapi.json" in docs.text
        assert 'nonce="' in docs.text
        for filename in (
            "swagger-ui.css",
            "swagger-ui-bundle.js",
            "favicon.svg",
        ):
            assert (
                client.get(PREFIX + "/api/docs-assets/" + filename).status_code
                == 200
            )
        redirect = client.get(
            PREFIX + "/api/docs/?q=synthetic",
            headers={"Host": "attacker.invalid", "X-Forwarded-Proto": "http"},
        )
        assert redirect.headers["location"] == "../docs?q=synthetic"
        schema = client.get(PREFIX + "/api/openapi.json").json()
        assert schema["servers"] == [{"url": PREFIX}]
        assert (
            schema["paths"]["/api/v1/notes"]["post"]["operationId"]
            == "create_note"
        )
        assert client.get(PREFIX + "/").json()["docs"] == PREFIX + "/api/docs"
        assert client.get(PREFIX + "/missing").status_code == 404
        assert client.get("/projects/unknown/ready").status_code == 404


def test_headers_cors_and_admission() -> None:
    """Deny cross-origin grants and excess calls while preserving readiness."""
    app = create_app(Settings(request_limit=1))
    with TestClient(app) as client:
        first = client.get(
            PREFIX + "/api/v1/notes",
            headers={"Origin": "https://unknown.invalid"},
        )
        assert "access-control-allow-origin" not in first.headers
        assert first.headers["x-content-type-options"] == "nosniff"
        assert first.headers["x-frame-options"] == "DENY"
        assert client.get(PREFIX + "/api/v1/notes").status_code == 429
        assert client.get(PREFIX + "/api/ready").status_code == 200
        assert (
            client.options(
                PREFIX + "/api/v1/notes",
                headers={
                    "Origin": "https://unknown.invalid",
                    "Access-Control-Request-Method": "POST",
                },
            ).status_code
            == 400
        )


def test_admission_constant_memory_and_recovery() -> None:
    """Recover after a finite window without retaining client identities."""
    clock = [0.0]
    admission = Admission(
        Settings(request_limit=1, window_seconds=1), lambda: clock[0]
    )
    assert admission.allow()
    for _ in range(1000):
        assert not admission.allow()
    assert admission.count == 1
    clock[0] = 2
    assert admission.allow()
    assert admission.count == 1


def test_safe_logs_and_failure(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Never record payload/query/headers/raw error or untrusted path details."""

    def failed(self: NotesService, body: NoteInput) -> Note:
        """Fail an injected real notes boundary without logging its input."""
        raise RuntimeError("synthetic-private-value")

    monkeypatch.setattr(NotesService, "create", failed)
    app = create_app(Settings())
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            PREFIX + "/api/v1/notes?token=synthetic-private-value",
            json={"title": "synthetic-private-value"},
            headers={"X-Request-ID": "synthetic-private-value"},
        )
        assert response.status_code == 500
        assert "synthetic-private-value" not in response.text
        assert response.headers["x-request-id"] != "synthetic-private-value"
        client.get(PREFIX + "/synthetic-private-value")
    formatter = JsonFormatter()
    logs = [
        formatter.format(record)
        for record in caplog.records
        if record.name == "fastapi_app.requests"
    ]
    assert logs and all("synthetic-private-value" not in line for line in logs)
    assert any(json.loads(line)["level"] == "ERROR" for line in logs)
    record = logging.LogRecord(
        "synthetic",
        logging.INFO,
        "private-path",
        1,
        "synthetic-private-value",
        (),
        None,
    )
    assert "synthetic-private-value" not in formatter.format(record)


def test_invalid_runtime_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject an unsafe identity and honor an explicit valid runtime project."""
    monkeypatch.setenv("GPTCLAW_PROJECT_ID", "another-api")
    assert Settings.from_runtime().prefix == "/projects/another-api"
    with pytest.raises(ValidationError):
        Settings(project_id="../invalid")
