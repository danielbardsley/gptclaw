"""Isolate tests using the actual disposable PostgreSQL fixture."""

from collections.abc import Iterator

import pytest
from sqlalchemy import text

from fastapi_app.services.database import Database


@pytest.fixture(autouse=True)
def clean_database() -> Iterator[None]:
    """Delete only fixture rows between tests; preserve schema and lock row."""
    database = Database()
    with database.engine.begin() as connection:
        connection.execute(text("DELETE FROM notes"))
    try:
        yield
    finally:
        database.close()
