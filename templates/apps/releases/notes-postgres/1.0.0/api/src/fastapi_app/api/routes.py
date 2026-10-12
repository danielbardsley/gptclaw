"""Versioned REST adapters with injected application services."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from fastapi_app.domain.models import EchoInput, EchoOutput, Page
from fastapi_app.services.echo import EchoService

router = APIRouter(prefix="/api/v1")


def service(request: Request) -> EchoService:
    """Resolve the injected application service from initialized state."""
    instance: EchoService = request.app.state.echo_service
    return instance


@router.post("/echo", response_model=EchoOutput, operation_id="echo_message")
def echo_message(
    body: EchoInput, echo: Annotated[EchoService, Depends(service)]
) -> EchoOutput:
    """Normalize a bounded message without retaining application data."""
    return echo.echo(body.message)


@router.get("/examples", response_model=Page, operation_id="list_examples")
def list_examples(
    echo: Annotated[EchoService, Depends(service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
) -> Page:
    """Return a bounded page from the stateless synthetic collection."""
    return echo.examples(limit, offset)
