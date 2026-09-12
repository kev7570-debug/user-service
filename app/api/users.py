from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.api.responses import BAD_REQUEST, NOT_FOUND, UNAUTHORIZED, documented_errors
from app.core.exceptions import ConflictError
from app.models.user import User
from app.schemas.user import (
    CurrentUserResponseModel,
    PaginatedMetaDataModel,
    UpdateUserModel,
    UpdateUserResponseModel,
    UsersListElementModel,
    UsersListMetaDataModel,
    UsersListResponseModel,
)

router = APIRouter(tags=["user"])


@router.get(
    "/users/current",
    response_model=CurrentUserResponseModel,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED),
)
async def current_user(user: User = Depends(get_current_user)):
    """Данные о текущем аутентифицированном пользователе."""
    return CurrentUserResponseModel.model_validate(user)


@router.patch(
    "/users/current",
    response_model=UpdateUserResponseModel,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED, NOT_FOUND),
)
async def edit_current_user(
    payload: UpdateUserModel,
    user: User = Depends(get_current_user),
):
    """Пользователь редактирует часть своих данных.

    Путь /users/current соответствует спецификации из приложения к ТЗ.
    Пользователь может менять только те поля, которые ему разрешены
    (без is_admin и city); email проверяется на уникальность.
    """
    update_data = payload.model_dump(exclude_unset=True)
    if "email" in update_data:
        update_data["email"] = str(update_data["email"]).lower()
        duplicate = await User.filter(email=update_data["email"]).exclude(id=user.id).exists()
        if duplicate:
            raise ConflictError("Email already exists")
    if update_data:
        await User.filter(id=user.id).update(**update_data)
        await user.refresh_from_db()
    return UpdateUserResponseModel.model_validate(user)


@router.get(
    "/users",
    response_model=UsersListResponseModel,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED),
)
async def list_users(
    page: int = Query(..., ge=1),
    size: int = Query(..., ge=1, le=100),
    _: User = Depends(get_current_user),
):
    """Постраничный список кратких данных обо всех пользователях (для обычных юзеров)."""
    total = await User.all().count()
    users = await User.all().offset((page - 1) * size).limit(size).order_by("id")
    return UsersListResponseModel(
        data=[UsersListElementModel.model_validate(u) for u in users],
        meta=UsersListMetaDataModel(
            pagination=PaginatedMetaDataModel(total=total, page=page, size=size)
        ),
    )
