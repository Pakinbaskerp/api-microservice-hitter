from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from .core.logging import configure_logging
from .core.http_client import build_client
from .routers import proxy as proxy_router
from .routers import docs as docs_router
from .routers import misc as misc_router

log = configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # shared httpx client
    app.state.http_client = build_client()

    # UI state
    app.state.api_gw_base = None  # user-set base for swagger "try it out"
    app.state.auth_scheme = "Bearer"
    app.state.auth_token = None

    # templates folder (prefer app/templates; fallback to repo-root/templates)
    templates_dir = Path(__file__).resolve().parent / "templates"
    if not templates_dir.exists():
        alt = Path(__file__).resolve().parents[1] / "templates"
        templates_dir = alt if alt.exists() else templates_dir
    app.state.templates = templates_dir

    log.info("API Gateway started. Services loaded.")
    try:
        yield
    finally:
        await app.state.http_client.aclose()
        log.info("API Gateway stopped.")

def create_app() -> FastAPI:
    app = FastAPI(title="Python API Gateway", version="1.0", lifespan=lifespan)

    # CORS (same as your single file)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(proxy_router.router)
    app.include_router(docs_router.router)
    app.include_router(misc_router.router)
    return app

app = create_app()
