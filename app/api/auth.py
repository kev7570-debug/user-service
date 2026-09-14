from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Request, Response

from app.api.responses import BAD_REQUEST
from app.config import settings
from app.core.exceptions import BadRequestError
from app.core.security import create_session_token, hash_session_token, verify_password
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import LoginModel
from app.schemas.user import CurrentUserResponseModel

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=CurrentUserResponseModel, responses=BAD_REQUEST)
async def login(payload: LoginModel, response: Response):
    """Вход в систему. При успехе устанавливает cookie с подписанной сессией."""
    user = await User.get_or_none(email=payload.login.lower())
    if user is None or not verify_password(payload.password, user.password_hash):
        raise BadRequestError("Invalid login or password")

    token = create_session_token()
    await Session.create(
        user=user,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.SESSION_TTL_SECONDS),
    )
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.SESSION_TTL_SECONDS,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        path="/",
    )
    return CurrentUserResponseModel.model_validate(user)


@router.get("/logout")
async def logout(request: Request, response: Response):
    """Выход из системы. Удаляет cookie."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if token:
        await Session.filter(token_hash=hash_session_token(token)).delete()
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    return {"message": "ok"}
