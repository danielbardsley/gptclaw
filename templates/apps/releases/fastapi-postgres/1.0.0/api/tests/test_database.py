"""Exercise real database readiness and explicit operation error boundaries."""

from pathlib import Path
from unittest.mock import patch

import pytest

from fastapi_app.db_cli import main
from fastapi_app.services.database import Database


def test_readiness_revision_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject a different migration head while retaining actual connectivity."""
    database = Database()
    assert database.ready()
    monkeypatch.setenv("GPTCLAW_DATABASE_HEAD", "unknown")
    assert not database.ready()
    database.close()


def test_missing_config_is_safe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Map missing configuration to a fixed error without echoing its path."""
    monkeypatch.setenv("GPTCLAW_DATABASE_FILE", str(tmp_path / "missing"))
    database = Database()
    database.close()
    assert not database.ready()
    with pytest.raises(
        ValueError, match="Database configuration is unavailable"
    ):
        _ = database.engine


def test_explicit_seed_and_repeat_refusal() -> None:
    """Seed only an empty fixture and refuse to silently replace its records."""
    main("seed")
    with pytest.raises(ValueError, match="empty database"):
        main("seed")
    with pytest.raises(ValueError, match="Unsupported"):
        main("other")


def test_current_migration_and_divergent_head_refusal() -> None:
    """Check the real already-current schema and refuse a divergent source graph."""
    main("migrate")
    with patch("fastapi_app.db_cli.ScriptDirectory.from_config") as script:
        script.return_value.get_heads.return_value = ["one", "two"]
        with pytest.raises(ValueError, match="one migration head"):
            main("migrate")
