"""Selected local credential-file access and bounded PostgreSQL pooling."""

import json
import os
from pathlib import Path

from sqlalchemy import URL, Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class Database:
    """Read one selected credential file only when a database operation needs it."""

    def __init__(self) -> None:
        """Keep construction and OpenAPI generation free of database side effects."""
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """Create a finite pool without embedding passwords in logs or arguments."""
        if self._engine is None:
            try:
                path = Path(
                    os.environ.get(
                        "GPTCLAW_DATABASE_FILE", "/run/secrets/database.json"
                    )
                )
                credentials = json.loads(path.read_text())
                url = URL.create(
                    "postgresql+psycopg",
                    username=credentials["username"],
                    password=credentials["password"],
                    host=os.environ.get("GPTCLAW_DATABASE_HOST", "db"),
                    database="app",
                )
                self._engine = create_engine(
                    url,
                    pool_size=5,
                    max_overflow=5,
                    pool_timeout=5,
                    hide_parameters=True,
                    connect_args={"connect_timeout": 5},
                )
            except (OSError, KeyError, ValueError):
                raise ValueError(
                    "Database configuration is unavailable."
                ) from None
        return self._engine

    def ready(self) -> bool:
        """Check authenticated connectivity and the declared source revision."""
        try:
            with self.engine.connect() as connection:
                revision = connection.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar_one()
                return bool(
                    revision == os.environ.get("GPTCLAW_DATABASE_HEAD", "0001")
                )
        except (SQLAlchemyError, ValueError):
            return False

    def close(self) -> None:
        """Release connections when the managed process shuts down."""
        if self._engine is not None:
            self._engine.dispose()
