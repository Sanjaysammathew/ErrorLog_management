import pytest
from sqlalchemy import select

from app.exceptions.custom_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.models.user import UserRole, user
from app.repositories.implementations.user_repository import UserRepository


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_persists_account(db_session):
    repository = UserRepository(db_session)
    new_user = user(
        username="repo_created",
        email="repo_created@example.com",
        hashed_password="hashed-password",
        role=UserRole.EMPLOYEE,
        department="Support",
    )

    created = await repository.create(new_user)
    persisted = await db_session.scalar(select(user).where(user.id == created.id))

    assert created.id is not None
    assert persisted is not None
    assert persisted.email == "repo_created@example.com"
    assert persisted.department == "Support"


@pytest.mark.asyncio(loop_scope="session")
async def test_user_lookups_find_email_username_and_role(db_session):
    repository = UserRepository(db_session)
    employee = await repository.get_by_email("employee@example.com")
    duplicate_match = await repository.get_by_username_or_email(
        "employee", "not-the-email@example.com"
    )
    manager = await repository.get_by_role(UserRole.MANAGER)

    assert employee is not None and employee.username == "employee"
    assert duplicate_match is not None and duplicate_match.id == employee.id
    assert manager is not None and manager.email == "manager@example.com"
    assert await repository.get_by_email("missing@example.com") is None


@pytest.mark.asyncio(loop_scope="session")
async def test_user_pagination_and_count_reflect_persisted_accounts(db_session):
    repository = UserRepository(db_session)
    for number in range(3):
        await repository.create(
            user(
                username=f"page_user_{number}",
                email=f"page_user_{number}@example.com",
                hashed_password="hashed-password",
                role=UserRole.EMPLOYEE,
            )
        )

    first_page = await repository.get_all(offset=0, limit=2)
    second_page = await repository.get_all(offset=2, limit=2)
    total = await repository.count_all()
    persisted_emails = set(
        (
            await db_session.scalars(
                select(user.email).where(user.username.like("page_user_%"))
            )
        ).all()
    )

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert {item.id for item in first_page}.isdisjoint(
        {item.id for item in second_page}
    )
    assert total == 6  # Three fixture accounts plus three created above.
    assert persisted_emails == {
        "page_user_0@example.com",
        "page_user_1@example.com",
        "page_user_2@example.com",
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_persists_changed_fields(db_session):
    repository = UserRepository(db_session)
    employee = await repository.get_by_email("employee@example.com")
    assert employee is not None

    updated = await repository.update(
        employee.id,
        {"department": "Infrastructure", "is_active": False},
    )
    persisted = await db_session.scalar(select(user).where(user.id == employee.id))

    assert updated.department == "Infrastructure"
    assert updated.is_active is False
    assert persisted is not None
    assert persisted.department == "Infrastructure"
    assert persisted.is_active is False


@pytest.mark.asyncio(loop_scope="session")
async def test_create_duplicate_account_raises_and_rolls_back(db_session):
    repository = UserRepository(db_session)
    duplicate = user(
        username="employee",
        email="different@example.com",
        hashed_password="hashed-password",
        role=UserRole.EMPLOYEE,
    )

    with pytest.raises(UserAlreadyExistsError):
        await repository.create(duplicate)

    assert await repository.get_by_email("different@example.com") is None
    with pytest.raises(UserNotFoundError):
        await repository.update(999999, {"department": "Nowhere"})
