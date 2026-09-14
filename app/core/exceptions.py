import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app")


class AppError(Exception):
    """Базовый класс для всех предсказуемых ошибок приложения.

    Наследники должны задавать status_code и message.
    Общий handler превращает их в единый JSON-формат ответа.
    """

    status_code: int = 400
    message: str = "Bad request"
    code: int | None = None

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class NotAuthenticatedError(AppError):
    status_code = 401
    message = "Not authenticated"


class ForbiddenError(AppError):
    status_code = 403
    message = "Forbidden"


class NotFoundError(AppError):
    status_code = 404
    message = "Not found"


class BadRequestError(AppError):
    status_code = 400
    message = "Bad request"
    code = 400


class ConflictError(AppError):
    status_code = 400
    message = "Resource already exists"
    code = 400


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует обработчики ошибок согласно ТЗ:

    - AppError и наследники -> предсказуемый JSON с описанием ошибки.
    - RequestValidationError -> 422 в формате HTTPValidationError (стандарт FastAPI).
    - Любое другое необработанное исключение -> 500 с generic-сообщением,
      детали логируются, но не отдаются клиенту.
    """

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        body = {"message": exc.message}
        if exc.code is not None:
            body["code"] = exc.code
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"message": "что-то пошло не так, мы уже исправляем эту ошибку"},
        )
