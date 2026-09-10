from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserNamesMixin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("first_name", "last_name", "other_name", check_fields=False)
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None and not value:
            raise ValueError("name must not be blank")
        return value


# ---- /users/current ----


class CurrentUserResponseModel(UserNamesMixin):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    other_name: str | None = None
    email: EmailStr
    phone: str | None = None
    birthday: date | None = None
    is_admin: bool


class UpdateUserModel(UserNamesMixin):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    other_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    birthday: date | None = None


class UpdateUserResponseModel(UserNamesMixin):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    other_name: str | None = None
    email: EmailStr
    phone: str | None = None
    birthday: date | None = None


# ---- /users (публичный список) ----


class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int


class UsersListElementModel(UserNamesMixin):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr


class UsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel


class UsersListResponseModel(BaseModel):
    data: list[UsersListElementModel]
    meta: UsersListMetaDataModel


# ---- /private/users (админский список) ----


class CitiesHintModel(BaseModel):
    id: int
    name: str


class PrivateUsersListHintMetaModel(BaseModel):
    city: list[CitiesHintModel] = Field(default_factory=list)


class PrivateUsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class PrivateUsersListResponseModel(BaseModel):
    data: list[UsersListElementModel]
    meta: PrivateUsersListMetaDataModel


# ---- /private/users создание/детали/изменение ----


class PrivateCreateUserModel(UserNamesMixin):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    other_name: str | None = None
    email: EmailStr
    phone: str | None = None
    birthday: date | None = None
    city: int | None = None
    additional_info: str | None = None
    is_admin: bool
    password: str = Field(min_length=8, max_length=128)


class PrivateDetailUserResponseModel(UserNamesMixin):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    other_name: str | None = None
    email: EmailStr
    phone: str | None = None
    birthday: date | None = None
    city: int | None = None
    additional_info: str | None = None
    is_admin: bool


class PrivateUpdateUserModel(UserNamesMixin):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    other_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    birthday: date | None = None
    city: int | None = None
    additional_info: str | None = None
    is_admin: bool | None = None
