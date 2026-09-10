from tortoise import fields
from tortoise.models import Model


class City(Model):
    """Справочник городов (используется в PrivateUsersListHintMetaModel / CitiesHintModel)."""

    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "cities"

    def __str__(self) -> str:
        return self.name
