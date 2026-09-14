import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app.core.security import hash_password
from app.main import create_app
from app.models.user import User

TEST_DB_MODULES = ["app.models.user", "app.models.city", "app.models.session"]
app = create_app(init_database=False)


@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    """Свежая in-memory SQLite БД на каждый тест."""
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": TEST_DB_MODULES})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def regular_user():
    return await User.create(
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password_hash=hash_password("password123"),
        is_admin=False,
    )


@pytest_asyncio.fixture
async def admin_user():
    return await User.create(
        first_name="Admin",
        last_name="Adminov",
        email="admin@example.com",
        password_hash=hash_password("adminpass"),
        is_admin=True,
    )
