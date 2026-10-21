"""Validated explicit non-secret settings; no dotenv discovery."""

import os
from typing import Self

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Configure project identity and finite development request admission."""

    project_id: str = Field(
        default="example-api",
        pattern=r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$",
        max_length=48,
    )
    request_limit: int = Field(default=60, ge=1, le=1000)
    window_seconds: float = Field(default=60.0, ge=0.1, le=3600.0)

    @property
    def prefix(self) -> str:
        """Return the owned private ingress mount path."""
        return f"/projects/{self.project_id}"

    @classmethod
    def from_runtime(cls) -> Self:
        """Read only the documented, non-secret project identity variable."""
        return cls(
            project_id=os.environ.get("GPTCLAW_PROJECT_ID", "example-api")
        )
