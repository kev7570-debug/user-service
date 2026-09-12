from fastapi import APIRouter, Depends, Query, status

from app.api.deps import require_admin
from app.api.responses import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_FOUND,
    UNAUTHORIZED,
    documented_errors,
)
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.city import City
from app.models.user import User
from app.schemas.user import (
    CitiesHintModel,
    PaginatedMetaDataModel,
    PrivateCreateUserModel,
    PrivateDetailUserResponseModel,
    PrivateUpdateUserModel,
    PrivateUsersListHintMetaModel,
    PrivateUsersListMetaDataModel,
    PrivateUsersListResponseModel,
    UsersListElementModel,
)

router = APIRouter(prefix="/private", tags=["admin"], dependencies=[Depends(require_admin)])


def detail_response(user: User) -> PrivateDetailUserResponseModel:
    return PrivateDetailUserResponseModel(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        other_name=user.other_name,
        email=user.email,
        phone=user.phone,
        birthday=user.birthday,
        city=user.city_id,
        additional_info=user.additional_info,
        is_admin=user.is_admin,
    )


async def validate_city(city_id: int | None) -> None:
    if city_id is not None and not await City.filter(id=city_id).exists():
        raise BadRequestError("City not found")


@router.get(
    "/users",
    response_model=PrivateUsersListResponseModel,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED, FORBIDDEN),
)
async def private_list_users(page: int = Query(..., ge=1), size: int = Query(..., ge=1, le=100)):
    """Постраничный список пользователей для администратора + подсказка по городам."""
    total = await User.all().count()
    users = await User.all().offset((page - 1) * size).limit(size).order_by("id")
    cities = await City.all()

    return PrivateUsersListResponseModel(
        data=[UsersListElementModel.model_validate(u) for u in users],
        meta=PrivateUsersListMetaDataModel(
            pagination=PaginatedMetaDataModel(total=total, page=page, size=size),
            hint=PrivateUsersListHintMetaModel(
                city=[CitiesHintModel(id=c.id, name=c.name) for c in cities]
            ),
        ),
    )


@router.post(
    "/users",
    response_model=PrivateDetailUserResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED, FORBIDDEN),
)
async def private_create_user(payload: PrivateCreateUserModel):
    """Создание пользователя администратором."""
    email = str(payload.email).lower()
    if await User.filter(email=email).exists():
        raise ConflictError("Email already exists")
    await validate_city(payload.city)
    data = payload.model_dump(exclude={"password", "city"})
    data["email"] = email
    user = await User.create(
        **data,
        city_id=payload.city,
        password_hash=hash_password(payload.password),
    )
    return detail_response(user)


@router.get(
    "/users/{pk}",
    response_model=PrivateDetailUserResponseModel,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED, FORBIDDEN, NOT_FOUND),
)
async def private_get_user(pk: int):
    user = await User.get_or_none(id=pk)
    if user is None:
        raise NotFoundError("User not found")
    return detail_response(user)


@router.delete(
    "/users/{pk}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=documented_errors(UNAUTHORIZED, FORBIDDEN),
)
async def private_delete_user(pk: int):
    deleted_count = await User.filter(id=pk).delete()
    if not deleted_count:
        raise NotFoundError("User not found")


@router.patch(
    "/users/{pk}",
    response_model=PrivateDetailUserResponseModel,
    responses=documented_errors(BAD_REQUEST, UNAUTHORIZED, FORBIDDEN, NOT_FOUND),
)
async def private_update_user(pk: int, payload: PrivateUpdateUserModel):
    user = await User.get_or_none(id=pk)
    if user is None:
        raise NotFoundError("User not found")

    if payload.id != pk:
        raise BadRequestError("Body id must match path pk")

    update_data = payload.model_dump(exclude={"id", "city"}, exclude_unset=True)
    if "email" in update_data:
        update_data["email"] = str(update_data["email"]).lower()
        duplicate = await User.filter(email=update_data["email"]).exclude(id=pk).exists()
        if duplicate:
            raise ConflictError("Email already exists")
    if "city" in payload.model_fields_set:
        await validate_city(payload.city)
        update_data["city_id"] = payload.city
    if update_data:
        await User.filter(id=pk).update(**update_data)
        await user.refresh_from_db()
    return detail_response(user)
