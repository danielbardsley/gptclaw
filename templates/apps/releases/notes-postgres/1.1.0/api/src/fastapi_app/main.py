"""Construct the private mounted FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from fastapi_app.api.middleware import Admission, RequestMiddleware
from fastapi_app.api.notes import router as notes_router
from fastapi_app.api.routes import router
from fastapi_app.domain.models import DomainError
from fastapi_app.services.echo import EchoService
from fastapi_app.services.notes import NotesService
from fastapi_app.settings import Settings
from fastapi_app.utils.logging import configure_logging


def create_app(
    settings: Settings | None = None, echo_service: EchoService | None = None
) -> FastAPI:
    """Build one private API with explicit injected settings and service."""
    settings = settings or Settings.from_runtime()
    prefix = settings.prefix
    child = FastAPI(
        title="Persistent notes API",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        root_path_in_servers=False,
        servers=[{"url": prefix}],
        redirect_slashes=False,
    )
    child.state.echo_service = echo_service or EchoService()
    child.state.notes_service = NotesService()
    child.include_router(router)
    child.include_router(notes_router)

    @child.exception_handler(RequestValidationError)
    async def invalid_request(
        _request: Request, _error: RequestValidationError
    ) -> JSONResponse:
        """Avoid reflecting invalid input or validation internals into errors."""
        return JSONResponse({"detail": "Invalid request."}, status_code=422)

    @child.exception_handler(DomainError)
    async def domain_error(
        _request: Request, _error: DomainError
    ) -> JSONResponse:
        """Map domain failures to a stable response without exception details."""
        return JSONResponse(
            {"detail": "A nonblank message is required."}, status_code=422
        )

    @child.get("/", include_in_schema=False)
    def home() -> dict[str, str]:
        """Link the private API documentation."""
        return {"docs": prefix + "/api/docs", "api": prefix + "/api/v1/"}

    @child.get("/api/health", include_in_schema=False)
    def health() -> dict[str, str]:
        """Report liveness independently of API admission."""
        return {"status": "alive"}

    @child.get("/api/ready", include_in_schema=False)
    def ready() -> JSONResponse:
        """Report initialized application readiness."""
        initialized = (
            child.state.ready and child.state.notes_service.database.ready()
        )
        return JSONResponse(
            {"status": "ready" if initialized else "unready"},
            status_code=200 if initialized else 503,
        )

    child.mount(
        "/api/docs-assets",
        StaticFiles(directory=Path(__file__).parent / "static"),
        name="static",
    )

    @child.get("/api/docs", include_in_schema=False)
    def docs(request: Request) -> HTMLResponse:
        """Serve interactive docs using only bundled local assets."""
        page = get_swagger_ui_html(
            openapi_url=prefix + "/api/openapi.json",
            title="Private API docs",
            swagger_js_url=prefix + "/api/docs-assets/swagger-ui-bundle.js",
            swagger_css_url=prefix + "/api/docs-assets/swagger-ui.css",
            swagger_favicon_url=prefix + "/api/docs-assets/favicon.svg",
            swagger_ui_parameters={
                "validatorUrl": None,
                "persistAuthorization": False,
            },
        )
        return HTMLResponse(
            bytes(page.body)
            .decode()
            .replace("<script>", f'<script nonce="{request.state.nonce}">')
        )

    @child.get("/api/docs/", include_in_schema=False)
    def docs_slash(request: Request) -> RedirectResponse:
        """Keep slash redirects relative to the verified browser origin."""
        query = "?" + request.url.query if request.url.query else ""
        return RedirectResponse("../docs" + query, status_code=307)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        """Initialize and release the development application state."""
        child.state.ready = True
        try:
            yield
        finally:
            child.state.ready = False
            child.state.notes_service.database.close()

    child.state.ready = False
    parent = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        redirect_slashes=False,
        lifespan=lifespan,
    )
    parent.mount(prefix, child)
    parent.state.child = child
    parent.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
    )
    parent.add_middleware(
        RequestMiddleware,
        settings=settings,
        logger=configure_logging(),
        admission=Admission(settings),
    )
    return parent
