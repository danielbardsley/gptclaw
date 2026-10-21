"""Explicit container-only database migration and synthetic seed operations."""

import sys

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from fastapi_app.domain.notes import NoteInput
from fastapi_app.services.notes import NotesService


def main(action: str) -> None:
    """Run one explicitly selected operation; never execute it on app start."""
    if action == "migrate":
        config = Config("alembic.ini")
        script = ScriptDirectory.from_config(config)
        if len(script.get_heads()) != 1:
            raise ValueError("Exactly one migration head is required.")
        command.upgrade(config, "head")
    elif action == "seed":
        service = NotesService()
        if service.list(1, 0).total:
            raise ValueError("Synthetic seed requires an empty database.")
        service.create(
            NoteInput(
                title="Synthetic example", body="Development fixture only."
            )
        )
    else:
        raise ValueError("Unsupported database operation.")


if __name__ == "__main__":
    main(sys.argv[1])
