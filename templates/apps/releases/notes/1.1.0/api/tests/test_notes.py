"""Test real CRUD, failures, synchronized capacity and data lifetime."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from fastapi_app.domain.notes import NoteInput
from fastapi_app.main import create_app
from fastapi_app.services.notes import FullStore, NotesService
from fastapi_app.settings import Settings

URL = "/projects/example-api/api/v1/notes"


def test_crud_and_lifetime() -> None:
    """Exercise the real HTTP contract and process-local data lifetime."""
    app = create_app(Settings(request_limit=1000))
    with TestClient(app) as client:
        assert client.get(URL).json()["total"] == 0
        made = client.post(
            URL, json={"title": "  synthetic  ", "body": "<script>"}
        )
        assert made.status_code == 201
        note = made.json()
        assert note["title"] == "synthetic"
        location = made.headers["location"]
        assert location == URL + "/" + note["id"]
        assert client.get(location).json() == note
        edited = client.put(location, json={"title": "edited", "body": "body"})
        assert edited.status_code == 200
        assert edited.json()["id"] == note["id"]
        assert client.get(URL + "?limit=1&offset=0").json()["items"] == [
            {"id": note["id"], "title": "edited", "preview": "body"}
        ]
        assert client.get(URL + "?offset=1").json()["items"] == []
        assert client.get(URL).json()["total"] == 1
        assert client.delete(location).status_code == 204
        assert client.get(location).status_code == 404
        assert (
            client.put(location, json={"title": "missing"}).status_code == 404
        )
        assert client.delete(location).status_code == 404
        client.post(URL, json={"title": "ephemeral"})
        assert client.get(URL).json()["total"] == 1
    with TestClient(create_app(Settings())) as fresh:
        assert fresh.get(URL).json()["total"] == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"title": " "},
        {"title": "x" * 121},
        {"title": 1},
        {"title": "ok", "body": "x" * 10001},
        {"title": "ok", "secret": "no"},
    ],
)
def test_invalid_input(payload: dict[str, object]) -> None:
    """Reject malformed input without reflecting it in errors."""
    with TestClient(create_app(Settings())) as client:
        assert client.post(URL, json=payload).status_code == 422
        assert client.get(URL + "?limit=101").status_code == 422
        assert client.get(URL + "?offset=-1").status_code == 422
        assert client.get(URL + "/bad-id").status_code == 422


def test_concurrent_capacity_and_copy_isolation() -> None:
    """Keep atomic capacity/order and copied responses under concurrent calls."""
    service = NotesService()

    def create(_index: int) -> bool:
        """Represent simultaneous mutations at the admission boundary."""
        try:
            service.create(NoteInput(title="synthetic"))
            return True
        except FullStore:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(create, range(120))) == 100
    page = service.list(100, 0)
    assert page.total == 100
    first = page.items[0]
    first.title = "changed copy"
    assert service.get(first.id).title == "synthetic"
    service.update(first.id, NoteInput(title="updated"))
    assert service.list(1, 0).items[0].id == first.id
    service.delete(first.id)
    assert service.list(100, 0).total == 99
    with TestClient(create_app(Settings(request_limit=1000))) as client:
        for _ in range(100):
            assert (
                client.post(URL, json={"title": "synthetic"}).status_code
                == 201
            )
        assert client.post(URL, json={"title": "overflow"}).status_code == 409
        assert client.get(URL + "/" + str(uuid4())).status_code == 404
