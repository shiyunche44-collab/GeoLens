from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from geolens.app.bootstrap import load_all
from geolens.core.logging_setup import configure_logging
from geolens.modules.audit.api import router as audit_router
from geolens.modules.collection.api import router as collection_router
from geolens.modules.identity import public as identity
from geolens.modules.metrics.api import router as metrics_router
from geolens.modules.projects.api import router as projects_router

load_all()

ROUTERS = [projects_router, collection_router, metrics_router, audit_router]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="GeoLens API", version="0.1.0", lifespan=lifespan)

    @app.get("/healthz", tags=["ops"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    for router in ROUTERS:
        app.include_router(router, dependencies=[Depends(identity.workspace_scope)])
    return app


app = create_app()
