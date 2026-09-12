from tortoise import fields
from tortoise.models import Model


class User(Model):
    """Основная модель пользователя.

    Хранит учётные данные, контактную информацию и роль пользователя.
    Пароль сохраняется только в виде хеша (Argon2).
    """

    id = fields.IntField(primary_key=True)

    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255)
    other_name = fields.CharField(max_length=255, null=True)

    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=32, null=True)
    birthday = fields.DateField(null=True)

    city = fields.ForeignKeyField(
        "models.City", related_name="users", null=True, on_delete=fields.SET_NULL
    )
    additional_info = fields.TextField(null=True)

    is_admin = fields.BooleanField(default=False)

    password_hash = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
