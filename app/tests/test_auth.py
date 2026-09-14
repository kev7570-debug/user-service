import pytest


@pytest.mark.asyncio
async def test_login_success(client, regular_user):
    response = await client.post(
        "/login", json={"login": "ivan@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.cookies.get("session_id") is not None
    assert response.json()["email"] == "ivan@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client, regular_user):
    response = await client.post(
        "/login", json={"login": "ivan@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_current_user_requires_auth(client):
    response = await client.get("/users/current")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_session(client, regular_user):
    await client.post("/login", json={"login": regular_user.email, "password": "password123"})
    assert (await client.get("/users/current")).status_code == 200
    assert (await client.get("/logout")).status_code == 200
    assert (await client.get("/users/current")).status_code == 401
