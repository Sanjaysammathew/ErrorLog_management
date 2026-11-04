import pytest
from unittest.mock import AsyncMock

from app.models.user import user, UserRole
from app.schemas.userSchema import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.repositories.interfaces.user_interface import UserInterface
from app.services.email_service import EmailService
from app.exceptions.custom_exceptions import (
    UserAlreadyExistsError,
    ManagerNotFoundError,
)


# Fixtures
@pytest.fixture
def user_repository():
    return AsyncMock(spec=UserInterface)


@pytest.fixture
def email_service():
    return AsyncMock(spec=EmailService)


@pytest.fixture
def user_service(user_repository, email_service):
    return UserService(user_repository, email_service)


# 1. Register user successfully
@pytest.mark.asyncio
async def test_register_user(
    user_service,
    user_repository,
    email_service,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.user_service.hash_password",
        lambda password: "hashed_password",
    )

    manager = user(id=2, role=UserRole.MANAGER)

    user_repository.get_by_username_or_email.return_value = None
    user_repository.get_by_role.return_value = manager

    async def create_user(new_user):
        new_user.id = 3
        return new_user

    user_repository.create.side_effect = create_user

    data = UserCreate(
        username="john",
        email="john@example.com",
        password="password123",
        role=UserRole.EMPLOYEE,
        department="IT",
    )

    result = await user_service.register_user(data)

    assert result.id == 3
    assert result.username == "john"
    assert result.hashed_password == "hashed_password"
    assert result.manager_id == 2

    user_repository.create.assert_awaited_once()
    email_service.send_account_created.assert_awaited_once()


# 2. Duplicate user registration
@pytest.mark.asyncio
async def test_duplicate_user(
    user_service,
    user_repository,
):
    user_repository.get_by_username_or_email.return_value = user(
        id=1,
        username="john",
        email="john@example.com",
    )

    data = UserCreate(
        username="john",
        email="john@example.com",
        password="password123",
    )

    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(data)

    user_repository.create.assert_not_awaited()


# 3. Manager not found
@pytest.mark.asyncio
async def test_manager_not_found(
    user_service,
    user_repository,
):
    user_repository.get_by_username_or_email.return_value = None
    user_repository.get_by_role.return_value = None

    data = UserCreate(
        username="john",
        email="john@example.com",
        password="password123",
        role=UserRole.EMPLOYEE,
    )

    with pytest.raises(ManagerNotFoundError):
        await user_service.register_user(data)

    user_repository.create.assert_not_awaited()


# 4. List users
@pytest.mark.asyncio
async def test_list_users(
    user_service,
    user_repository,
):
    user_repository.get_all.return_value = [
        user(id=1, username="john"),
        user(id=2, username="smith"),
    ]

    user_repository.count_all.return_value = 20

    result = await user_service.list_users(2, 10)

    assert len(result["items"]) == 2
    assert result["total"] == 20
    assert result["page"] == 2
    assert result["page_size"] == 10

    user_repository.get_all.assert_awaited_once_with(10, 10)


# 5. Update user password
@pytest.mark.asyncio
async def test_update_user_password(
    user_service,
    user_repository,
    monkeypatch,
):
    existing_user = user(
        id=1,
        username="john",
        role=UserRole.EMPLOYEE,
        manager_id=2,
    )

    user_repository.get_by_id.return_value = existing_user
    user_repository.update.return_value = existing_user

    monkeypatch.setattr(
        "app.services.user_service.hash_password",
        lambda password: "new_hashed_password",
    )

    data = UserUpdate(password="newpassword123")

    result = await user_service.update_user(1, data)

    assert result.id == 1

    user_repository.update.assert_awaited_once_with(
        1,
        {"hashed_password": "new_hashed_password"},
    )
