import pytest

from app.models.city import City


async def login_admin(client, admin_user) -> None:
    response = await client.post(
        "/login", json={"login": admin_user.email, "password": "adminpass"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_crud(client, admin_user):
    city = await City.create(name="Москва")
    await login_admin(client, admin_user)
    payload = {
        "first_name": "Анна",
        "last_name": "Петрова",
        "email": "ANNA@example.com",
        "city": city.id,
        "is_admin": False,
        "password": "strongpass",
    }
    created = await client.post("/private/users", json=payload)
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert created.json()["email"] == "anna@example.com"
    assert created.json()["city"] == city.id

    detail = await client.get(f"/private/users/{user_id}")
    assert detail.status_code == 200

    updated = await client.patch(
        f"/private/users/{user_id}", json={"id": user_id, "last_name": "Сидорова"}
    )
    assert updated.status_code == 200
    assert updated.json()["last_name"] == "Сидорова"

    deleted = await client.delete(f"/private/users/{user_id}")
    assert deleted.status_code == 204
    assert (await client.get(f"/private/users/{user_id}")).status_code == 404


@pytest.mark.asyncio
async def test_admin_list_contains_city_hints(client, admin_user):
    city = await City.create(name="Казань")
    await login_admin(client, admin_user)
    response = await client.get("/private/users", params={"page": 1, "size": 10})
    assert response.status_code == 200
    assert response.json()["meta"]["hint"]["city"] == [{"id": city.id, "name": "Казань"}]


@pytest.mark.asyncio
async def test_admin_update_requires_matching_id(client, admin_user, regular_user):
    await login_admin(client, admin_user)
    response = await client.patch(f"/private/users/{regular_user.id}", json={"id": admin_user.id})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_rejects_unknown_city(client, admin_user):
    await login_admin(client, admin_user)
    response = await client.post(
        "/private/users",
        json={
            "first_name": "Иван",
            "last_name": "Тестов",
            "email": "new@example.com",
            "city": 999,
            "is_admin": False,
            "password": "strongpass",
        },
    )
    assert response.status_code == 400
