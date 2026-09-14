from datetime import UTC, datetime

from fastapi import Request

from app.config import settings
from app.core.exceptions import ForbiddenError, NotAuthenticatedError
from app.core.security import hash_session_token
from app.models.session import Session
from app.models.user import User


async def get_current_user(request: Request) -> User:
    """Достаёт пользователя из cookie-сессии.

    Бросает NotAuthenticatedError (-> 401), если cookie отсутствует/невалидна
    или пользователь не найден в БД.
    """
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise NotAuthenticatedError()

    session = await Session.get_or_none(token_hash=hash_session_token(token)).prefetch_related(
        "user"
    )
    if session is None:
        raise NotAuthenticatedError()
    if session.expires_at <= datetime.now(UTC):
        await session.delete()
        raise NotAuthenticatedError()
    return session.user


async def require_admin(request: Request) -> User:
    """Как get_current_user, но дополнительно требует is_admin=True (-> 403)."""
    user = await get_current_user(request)
    if not user.is_admin:
        raise ForbiddenError("Admins only")
    return user
