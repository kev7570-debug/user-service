from app.schemas.errors import CodelessErrorResponseModel, ErrorResponseModel

BAD_REQUEST = {400: {"model": ErrorResponseModel, "description": "Bad Request"}}
UNAUTHORIZED = {401: {"model": CodelessErrorResponseModel, "description": "Unauthorized"}}
FORBIDDEN = {403: {"model": CodelessErrorResponseModel, "description": "Forbidden"}}
NOT_FOUND = {404: {"model": CodelessErrorResponseModel, "description": "Not Found"}}


def documented_errors(*groups: dict) -> dict:
    result: dict = {}
    for group in groups:
        result.update(group)
    return result
