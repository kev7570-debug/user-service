from tortoise.contrib.fastapi import register_tortoise

from app.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DB_DSN},
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.city",
                "app.models.session",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


def init_db(app, *, generate_schemas: bool = False):
    """Подключает Tortoise ORM к FastAPI-приложению.

    generate_schemas=False намеренно — схема управляется миграциями aerich,
    а не автогенерацией (иначе на проде можно случайно "потерять" данные).
    """
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=generate_schemas,
        add_exception_handlers=False,  # свои обработчики ошибок в app.core.exceptions
    )
