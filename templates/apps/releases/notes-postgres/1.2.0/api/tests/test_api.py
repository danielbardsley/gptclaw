"""Exercise typed API boundaries, lifecycle, safe logs and static docs."""

import json
import logging
from typing import cast

import factory
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from fastapi_app.api.middleware import Admission
from fastapi_app.domain.models import DomainError, EchoInput, EchoOutput
from fastapi_app.main import create_app
from fastapi_app.services.echo import EchoService
from fastapi_app.settings import Settings
from fastapi_app.utils.logging import JsonFormatter

PREFIX = "/projects/example-api"


class EchoFactory(factory.Factory):  # type: ignore[name-defined,misc]
    """Create typed synthetic input; factory-boy has dynamic unstubbed exports."""

    class Meta:
        """Select the input model constructed by this factory."""

        model: type[EchoInput] = EchoInput

    message: str = "synthetic example"


@pytest.fixture
def app() -> FastAPI:
    """Construct a fresh application for every test."""
    return create_app(Settings())


@pytest.mark.parametrize("message", ["hello", "  synthetic   example  "])
def test_echo(message: str, app: FastAPI) -> None:
    """Normalize valid messages through the real request/response boundary."""
    with TestClient(app) as client:
        response = client.post(
            PREFIX + "/api/v1/echo", json={"message": message}
        )
        assert response.status_code == 200
        assert response.json() == {"message": " ".join(message.split())}


@pytest.mark.parametrize("message", ["", " ", "x" * 201])
def test_invalid_message(message: str, app: FastAPI) -> None:
    """Reject empty, blank and oversized input with validation statuses."""
    with TestClient(app) as client:
        assert (
            client.post(
                PREFIX + "/api/v1/echo", json={"message": message}
            ).status_code
            == 422
        )


@pytest.mark.parametrize(
    "query,status,ids",
    [
        ("limit=2&offset=1", 200, [2, 3]),
        ("offset=20", 200, []),
        ("limit=0", 422, []),
        ("offset=-1", 422, []),
    ],
)
def test_pagination(
    query: str, status: int, ids: list[int], app: FastAPI
) -> None:
    """Bound pagination parameters and report deterministic synthetic records."""
    with TestClient(app) as client:
        result = client.get(PREFIX + "/api/v1/examples?" + query)
        assert result.status_code == status
        if status == 200:
            assert [item["id"] for item in result.json()["items"]] == ids
            assert result.json()["total"] == 3


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
            schema["paths"]["/api/v1/echo"]["post"]["operationId"]
            == "echo_message"
        )
        assert client.get(PREFIX + "/").json()["docs"] == PREFIX + "/api/docs"
        assert client.get(PREFIX + "/missing").status_code == 404
        assert client.get("/projects/unknown/ready").status_code == 404


def test_headers_cors_and_admission() -> None:
    """Deny cross-origin grants and excess calls while preserving readiness."""
    app = create_app(Settings(request_limit=1))
    with TestClient(app) as client:
        first = client.get(
            PREFIX + "/api/v1/examples",
            headers={"Origin": "https://unknown.invalid"},
        )
        assert "access-control-allow-origin" not in first.headers
        assert first.headers["x-content-type-options"] == "nosniff"
        assert first.headers["x-frame-options"] == "DENY"
        assert client.get(PREFIX + "/api/v1/examples").status_code == 429
        assert client.get(PREFIX + "/api/ready").status_code == 200
        assert (
            client.options(
                PREFIX + "/api/v1/examples",
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


def test_settings_and_injected_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validate non-secret runtime identity and injected domain behavior."""
    monkeypatch.setenv("GPTCLAW_PROJECT_ID", "other-api")
    assert Settings.from_runtime().prefix == "/projects/other-api"
    with pytest.raises(ValidationError):
        Settings(project_id="../invalid")
    sample = cast(EchoInput, EchoFactory())
    assert EchoService().echo(sample.message).message == "synthetic example"
    with pytest.raises(DomainError):
        EchoService().echo(" ")
    injected = EchoService()
    app = create_app(echo_service=injected)
    assert app.state.child.state.echo_service is injected


class FailedService(EchoService):
    """Simulate an unexpected failure containing sensitive-looking context."""

    def echo(self, message: str) -> EchoOutput:
        """Fail at the application boundary for safe response/log verification."""
        raise RuntimeError("synthetic-private-value")


def test_safe_logs_and_failure(caplog: pytest.LogCaptureFixture) -> None:
    """Never record payload/query/headers/raw error or untrusted path details."""
    app = create_app(Settings(), cast(EchoService, FailedService()))
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            PREFIX + "/api/v1/echo?token=synthetic-private-value",
            json={"message": "synthetic-private-value"},
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
