from tortoise import fields
from tortoise.models import Model


class Session(Model):
    """Отзываемая серверная сессия; исходный токен в БД не хранится."""

    id = fields.IntField(primary_key=True)
    token_hash = fields.CharField(max_length=64, unique=True, db_index=True)
    user = fields.ForeignKeyField("models.User", related_name="sessions", on_delete=fields.CASCADE)
    expires_at = fields.DatetimeField(db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "sessions"
