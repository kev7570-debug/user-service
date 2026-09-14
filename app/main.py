from fastapi import FastAPI

from app.api import auth, private_users, users
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.database import init_db


def create_app(*, init_database: bool = True) -> FastAPI:
    application = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
    register_exception_handlers(application)
    if init_database:
        init_db(application)
    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(private_users.router)

    @application.get("/health", tags=["service"], include_in_schema=False)
    async def health():
        return {"status": "ok"}

    return application


app = create_app()
