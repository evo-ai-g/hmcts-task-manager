import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import tasks


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Run once at startup: create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API for managing caseworker tasks (HMCTS technical test).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check for load balancers and container orchestrators."""
    return {"status": "ok"}


# --- Frontend -------------------------------------------------------------
# Serves the static HTML/JS/CSS in the sibling `frontend/` folder.
# In production, nginx would serve these files instead — the HTML wouldn't change.

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve the task manager UI."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
