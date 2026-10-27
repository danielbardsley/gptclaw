"""Thin versioned notes REST adapters with injected service state."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from fastapi_app.domain.notes import Note, NoteInput, NotesPage
from fastapi_app.services.notes import FullStore, MissingNote, NotesService

router = APIRouter(prefix="/api/v1/notes")


def service(request: Request) -> NotesService:
    """Resolve the initialized process-local service."""
    instance: NotesService = request.app.state.notes_service
    return instance


@router.get("", response_model=NotesPage, operation_id="list_notes")
def list_notes(
    notes: Annotated[NotesService, Depends(service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> NotesPage:
    """Return one bounded page from the shared ephemeral store."""
    return notes.list(limit, offset)


@router.post(
    "", response_model=Note, status_code=201, operation_id="create_note"
)
def create_note(
    body: NoteInput,
    request: Request,
    response: Response,
    notes: Annotated[NotesService, Depends(service)],
) -> Note:
    """Create without implicit retries; reject the finite capacity explicitly."""
    try:
        note = notes.create(body)
    except FullStore:
        raise HTTPException(409, "Note capacity reached.") from None
    response.headers["Location"] = (
        str(request.scope.get("root_path", "")) + f"/api/v1/notes/{note.id}"
    )
    return note


@router.get("/{note_id}", response_model=Note, operation_id="get_note")
def get_note(
    note_id: UUID, notes: Annotated[NotesService, Depends(service)]
) -> Note:
    """Return content without exposing missing identity internals."""
    try:
        return notes.get(note_id)
    except MissingNote:
        raise HTTPException(404, "Note not found.") from None


@router.put("/{note_id}", response_model=Note, operation_id="update_note")
def update_note(
    note_id: UUID,
    body: NoteInput,
    notes: Annotated[NotesService, Depends(service)],
) -> Note:
    """Replace a complete note with validated plain text."""
    try:
        return notes.update(note_id, body)
    except MissingNote:
        raise HTTPException(404, "Note not found.") from None


@router.delete("/{note_id}", status_code=204, operation_id="delete_note")
def delete_note(
    note_id: UUID, notes: Annotated[NotesService, Depends(service)]
) -> Response:
    """Delete one known note and return an empty response."""
    try:
        notes.delete(note_id)
    except MissingNote:
        raise HTTPException(404, "Note not found.") from None
    return Response(status_code=204)
