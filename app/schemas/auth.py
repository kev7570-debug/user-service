from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    login: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("login")
    @classmethod
    def normalize_login(cls, value: str) -> str:
        return value.lower()
