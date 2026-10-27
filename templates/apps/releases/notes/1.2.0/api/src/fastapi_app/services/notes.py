"""Synchronized ephemeral domain service; one store per API process."""

from threading import Lock
from uuid import UUID, uuid4

from fastapi_app.domain.notes import Note, NoteInput, NotesPage, NoteSummary


class MissingNote(Exception):
    """Signal a missing note without retaining request payloads."""


class FullStore(Exception):
    """Signal the finite memory-store capacity."""


class NotesService:
    """Own bounded notes with atomic mutations and stable creation order."""

    def __init__(self) -> None:
        """Initialize an empty process-local store and mutation lock."""
        self._notes: dict[UUID, Note] = {}
        self._lock = Lock()

    def list(self, limit: int, offset: int) -> NotesPage:
        """Copy a deterministic page under the store lock."""
        with self._lock:
            items = list(self._notes.values())[offset : offset + limit]
            return NotesPage(
                items=[
                    NoteSummary(id=n.id, title=n.title, preview=n.body[:90])
                    for n in items
                ],
                total=len(self._notes),
                limit=limit,
                offset=offset,
            )

    def get(self, note_id: UUID) -> Note:
        """Read one copied note or report a missing identity."""
        with self._lock:
            if note_id not in self._notes:
                raise MissingNote
            return self._notes[note_id].model_copy(deep=True)

    def create(self, body: NoteInput) -> Note:
        """Create at most 100 notes without overwriting another identity."""
        with self._lock:
            if len(self._notes) >= 100:
                raise FullStore
            note = Note(id=uuid4(), **body.model_dump())
            self._notes[note.id] = note
            return note.model_copy(deep=True)

    def update(self, note_id: UUID, body: NoteInput) -> Note:
        """Replace content while retaining identity and creation order."""
        with self._lock:
            if note_id not in self._notes:
                raise MissingNote
            note = Note(id=note_id, **body.model_dump())
            self._notes[note_id] = note
            return note.model_copy(deep=True)

    def delete(self, note_id: UUID) -> None:
        """Remove one note atomically or report a missing identity."""
        with self._lock:
            if note_id not in self._notes:
                raise MissingNote
            del self._notes[note_id]
