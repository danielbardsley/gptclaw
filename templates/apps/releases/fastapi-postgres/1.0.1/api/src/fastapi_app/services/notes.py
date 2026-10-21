"""Transactional persistent notes with a database-backed capacity lock."""

from uuid import UUID, uuid4

from sqlalchemy import text

from fastapi_app.domain.notes import Note, NoteInput, NotesPage, NoteSummary
from fastapi_app.services.database import Database


class MissingNote(Exception):
    """Signal a missing identity without retaining request payloads."""


class FullStore(Exception):
    """Signal the finite development dataset capacity."""


class NotesService:
    """Own durable CRUD transactions independently of HTTP adapters."""

    def __init__(self, database: Database | None = None) -> None:
        """Accept an injected connection boundary without opening a socket."""
        self.database = database or Database()

    def list(self, limit: int, offset: int) -> NotesPage:
        """Return a stable bounded page in one consistent transaction."""
        with self.database.engine.connect().execution_options(
            isolation_level="REPEATABLE READ"
        ) as connection:
            with connection.begin():
                total = int(
                    connection.execute(
                        text("SELECT count(*) FROM notes")
                    ).scalar_one()
                )
                rows = connection.execute(
                    text(
                        "SELECT id,title,left(body,90) AS preview FROM notes ORDER BY ordinal,id LIMIT :limit OFFSET :offset"
                    ),
                    {"limit": limit, "offset": offset},
                ).mappings()
                return NotesPage(
                    items=[
                        NoteSummary.model_validate(dict(row)) for row in rows
                    ],
                    total=total,
                    limit=limit,
                    offset=offset,
                )

    def get(self, note_id: UUID) -> Note:
        """Read one durable note or report a missing identity."""
        with self.database.engine.connect() as connection:
            row = (
                connection.execute(
                    text("SELECT id,title,body FROM notes WHERE id=:id"),
                    {"id": note_id},
                )
                .mappings()
                .first()
            )
            if row is None:
                raise MissingNote
            return Note.model_validate(dict(row))

    def create(self, body: NoteInput) -> Note:
        """Serialize capacity checks across API processes using a row lock."""
        note = Note(id=uuid4(), **body.model_dump())
        with self.database.engine.begin() as connection:
            connection.execute(
                text("SELECT id FROM capacity_guard WHERE id=1 FOR UPDATE")
            ).one()
            if (
                int(
                    connection.execute(
                        text("SELECT count(*) FROM notes")
                    ).scalar_one()
                )
                >= 100
            ):
                raise FullStore
            connection.execute(
                text(
                    "INSERT INTO notes(id,title,body) VALUES(:id,:title,:body)"
                ),
                {"id": note.id, "title": note.title, "body": note.body},
            )
        return note

    def update(self, note_id: UUID, body: NoteInput) -> Note:
        """Replace content atomically while preserving creation order."""
        with self.database.engine.begin() as connection:
            result = connection.execute(
                text("UPDATE notes SET title=:title,body=:body WHERE id=:id"),
                {"id": note_id, "title": body.title, "body": body.body},
            )
            if result.rowcount == 0:
                raise MissingNote
        return Note(id=note_id, **body.model_dump())

    def delete(self, note_id: UUID) -> None:
        """Remove one existing note inside a transaction."""
        with self.database.engine.begin() as connection:
            result = connection.execute(
                text("DELETE FROM notes WHERE id=:id"), {"id": note_id}
            )
            if result.rowcount == 0:
                raise MissingNote
