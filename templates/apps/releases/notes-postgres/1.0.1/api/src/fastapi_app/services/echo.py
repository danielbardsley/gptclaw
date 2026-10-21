"""Application services independent of HTTP and persistence."""

from fastapi_app.domain.models import DomainError, EchoOutput, Example, Page


class EchoService:
    """Normalize messages and serve a small synthetic collection."""

    def echo(self, message: str) -> EchoOutput:
        """Normalize a message or reject whitespace-only input."""
        normalized = " ".join(message.split())
        if not normalized:
            raise DomainError("A nonblank message is required.")
        return EchoOutput(message=normalized)

    def examples(self, limit: int, offset: int) -> Page:
        """Return a bounded slice of three immutable synthetic examples."""
        records = [Example(id=i, name=f"Example {i}") for i in range(1, 4)]
        return Page(
            items=records[offset : offset + limit],
            total=len(records),
            limit=limit,
            offset=offset,
        )
