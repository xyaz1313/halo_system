"""FastAPI application entry point with global exception handlers."""

import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.core.exceptions import (
    AccessDeniedError,
    AlreadyExistsError,
    NotFoundError,
    ValidationError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup / shutdown hooks."""
    from backend.logging.config import setup_logging

    setup_logging()
    yield


app = FastAPI(
    title="Halo System",
    description="Backend API for the Halo caretaker-assistance system",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Global exception handlers — services raise, these map to HTTP responses
# ---------------------------------------------------------------------------


@app.exception_handler(NotFoundError)
async def _not_found_handler(request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(AlreadyExistsError)
async def _already_exists_handler(request, exc: AlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(ValidationError)
async def _validation_error_handler(request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.detail})


@app.exception_handler(AccessDeniedError)
async def _access_denied_handler(request, exc: AccessDeniedError):
    return JSONResponse(status_code=403, content={"detail": exc.detail})


# ---------------------------------------------------------------------------
# Router includes (populated by later tasks)
# ---------------------------------------------------------------------------

from backend.api.accounts import router as accounts_router
from backend.api.calendars import router as calendars_router
from backend.api.devices import anchors_router, tags_router
from backend.api.notifications import router as notifications_router

app.include_router(accounts_router, prefix="/api/v1")
app.include_router(anchors_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(calendars_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")

from backend.api.admin import router as admin_router

app.include_router(admin_router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Root redirect and static file serving
# ---------------------------------------------------------------------------

_FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend" / "static"


@app.get("/")
async def _root_redirect():
    return RedirectResponse(url="/static/index.html")


app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR)), name="static")
