from app.core.settings import get_settings
from app.core.logging import configure_logging
from app.core.middleware import setup_middleware
from app.api.routes import api_router
from app.db.session import init_db

from fastapi import FastAPI


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(title=settings.app_name, version=settings.version)
    setup_middleware(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.on_event("startup")
    async def on_startup() -> None:  # pragma: no cover
        await init_db()
    return app


app = create_app()