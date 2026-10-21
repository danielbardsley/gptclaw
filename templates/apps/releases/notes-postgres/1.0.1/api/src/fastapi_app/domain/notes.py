"""Typed plain-text notes and bounded mutation inputs."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NoteInput(BaseModel):
    """Validate and normalize one complete note mutation."""

    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="", max_length=10_000)

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value: object) -> object:
        """Trim before validating title bounds without coercing other types."""
        return value.strip() if isinstance(value, str) else value


class Note(NoteInput):
    """Return an immutable server identity with plain-text content."""

    id: UUID


class NoteSummary(BaseModel):
    """Bound list responses independently of full note-body size."""

    id: UUID
    title: str
    preview: str


class NotesPage(BaseModel):
    """Report a bounded page and total store size."""

    items: list[NoteSummary]
    total: int
    limit: int
    offset: int
