from pydantic import BaseModel, Field


class ErrorResponseModel(BaseModel):
    code: int
    message: str


class CodelessErrorResponseModel(BaseModel):
    message: str


class ValidationError(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: list[ValidationError] = Field(default_factory=list)
