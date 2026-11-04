import pytest
import pytest_asyncio
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

from sqlalchemy import URL, make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient

from app.core import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.connection import get_db
from app.api.dependency.dependencies import get_email_service
from app import models  # noqa: F401
from app.main import app
from app.models.user import UserRole, user
from app.services.email_service import EmailService

# 1. Create test database URL
TEST_DATABASE_URL = URL.create(
    drivername=settings.TEST_DATABASE_DRIVER,
    username=settings.TEST_DATABASE_USER,
    password=settings.TEST_DATABASE_PASSWORD.get_secret_value(),
    host=settings.TEST_DATABASE_HOST,
    port=settings.TEST_DATABASE_PORT,
    database=settings.TEST_DATABASE_NAME,
)

# 2. Prevent using the production database
app_url = make_url(settings.database_url)

if (
    TEST_DATABASE_URL.host,
    TEST_DATABASE_URL.port,
    TEST_DATABASE_URL.database,
) == (app_url.host, app_url.port, app_url.database):
    raise RuntimeError("Cannot use production database for testing")


# 3. Create test engine and session
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 4. Create tables before tests and drop them after
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


# 5. Clear data before every test
@pytest_asyncio.fixture(autouse=True)
async def clean_database(setup_database):
    async with test_engine.begin() as connection:
        table_names = ", ".join(
            f'"{table.name}"' for table in Base.metadata.sorted_tables
        )
        await connection.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )

    async with TestSessionLocal() as session:
        session.add(
            user(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
            )
        )
        manager = user(
            username="manager",
            email="manager@example.com",
            hashed_password=hash_password("manager123"),
            role=UserRole.MANAGER,
        )
        session.add(manager)
        await session.flush()
        session.add(
            user(
                username="employee",
                email="employee@example.com",
                hashed_password=hash_password("employee123"),
                role=UserRole.EMPLOYEE,
                manager_id=manager.id,
            )
        )
        await session.commit()


# 6. Override database dependency
@pytest.fixture
def client():
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with TestSessionLocal() as session:
            yield session

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    # Do not enter TestClient's context manager: it runs the app lifespan,
    # whose seed functions use the non-test application engine.
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture(autouse=True)
def mock_email_service():
    email_service = AsyncMock(spec=EmailService)
    app.dependency_overrides[get_email_service] = lambda: email_service
    yield email_service
    app.dependency_overrides.pop(get_email_service, None)


@pytest.fixture
def admin_headers(client):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def manager_headers(client):
    response = client.post(
        "/auth/login",
        data={"username": "manager", "password": "manager123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def employee_headers(client):
    response = client.post(
        "/auth/login",
        data={"username": "employee", "password": "employee123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
