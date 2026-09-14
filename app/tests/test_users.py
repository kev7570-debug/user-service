import pytest


async def login(client, email: str, password: str) -> None:
    response = await client.post("/login", json={"login": email, "password": password})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_can_read_and_edit_self(client, regular_user):
    await login(client, regular_user.email, "password123")
    response = await client.patch("/users/current", json={"first_name": "Пётр"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Пётр"


@pytest.mark.asyncio
async def test_user_list_is_paginated(client, regular_user, admin_user):
    await login(client, regular_user.email, "password123")
    response = await client.get("/users", params={"page": 1, "size": 1})
    assert response.status_code == 200
    assert response.json()["meta"]["pagination"] == {"total": 2, "page": 1, "size": 1}
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_user_cannot_use_admin_api(client, regular_user):
    await login(client, regular_user.email, "password123")
    response = await client.get("/private/users", params={"page": 1, "size": 10})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_duplicate_email_is_rejected(client, regular_user, admin_user):
    await login(client, regular_user.email, "password123")
    response = await client.patch("/users/current", json={"email": admin_user.email})
    assert response.status_code == 400
    assert response.json()["code"] == 400
