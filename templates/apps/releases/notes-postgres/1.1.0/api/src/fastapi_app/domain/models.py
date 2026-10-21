"""Typed synthetic API contracts and domain errors."""

from pydantic import BaseModel, Field


class DomainError(Exception):
    """Represent an expected safe business validation failure."""


class EchoInput(BaseModel):
    """Describe a bounded synthetic message."""

    message: str = Field(min_length=1, max_length=200)


class EchoOutput(BaseModel):
    """Describe the normalized synthetic result."""

    message: str


class Example(BaseModel):
    """Represent one stateless example record."""

    id: int
    name: str


class Page(BaseModel):
    """Describe explicit pagination metadata and records."""

    items: list[Example]
    total: int
    limit: int
    offset: int
