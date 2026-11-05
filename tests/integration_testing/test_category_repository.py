import pytest
from sqlalchemy import select

from app.exceptions.custom_exceptions import CategoryAlreadyExistsError
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.repositories.implementations.category_repository import CategoryRepository


def make_category(name: str, issue_type: IssueType = IssueType.HARDWARE, **kwargs):
    return ErrorCategory(
        name=name,
        issue_type=issue_type,
        description=kwargs.get("description", f"{name} support category"),
        default_sla_hours=kwargs.get("default_sla_hours", 12),
        requires_approval_default=kwargs.get("requires_approval_default", False),
        is_active=kwargs.get("is_active", True),
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_create_category_persists_all_fields(db_session):
    repository = CategoryRepository(db_session)
    created = await repository.create(
        make_category(
            "Laptop Repair",
            description="Hardware repair requests",
            default_sla_hours=8,
            requires_approval_default=True,
        )
    )
    persisted = await db_session.scalar(
        select(ErrorCategory).where(ErrorCategory.id == created.id)
    )

    assert created.id is not None
    assert persisted is not None
    assert persisted.name == "Laptop Repair"
    assert persisted.default_sla_hours == 8
    assert persisted.requires_approval_default is True


@pytest.mark.asyncio(loop_scope="session")
async def test_category_lookup_by_name_id_and_active_issue_type(db_session):
    repository = CategoryRepository(db_session)
    hardware = await repository.create(make_category("Hardware Help"))
    inactive_network = await repository.create(
        make_category("Old Network Help", IssueType.NETWORK, is_active=False)
    )
    active_network = await repository.create(
        make_category("Network Help", IssueType.NETWORK)
    )

    assert (await repository.get_by_name("Hardware Help")).id == hardware.id
    assert (await repository.get_by_id(inactive_network.id)).name == "Old Network Help"
    network_category = await repository.get_by_issue_type(IssueType.NETWORK)
    assert network_category is not None
    assert network_category.id == active_network.id
    assert await repository.get_by_id(999999) is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_returns_persisted_categories(db_session):
    repository = CategoryRepository(db_session)
    await repository.create(make_category("Software Help", IssueType.SOFTWARE))
    await repository.create(make_category("Network Help", IssueType.NETWORK))

    categories = await repository.get_all()
    persisted_names = set(
        (await db_session.scalars(select(ErrorCategory.name))).all()
    )

    assert {category.name for category in categories} == {
        "Software Help",
        "Network Help",
    }
    assert persisted_names == {"Software Help", "Network Help"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_category_persists_changed_values(db_session):
    repository = CategoryRepository(db_session)
    category = await repository.create(make_category("Initial Name"))
    category.name = "Updated Name"
    category.description = "Updated category description"
    category.is_active = False

    updated = await repository.update(category)
    persisted = await db_session.scalar(
        select(ErrorCategory).where(ErrorCategory.id == category.id)
    )

    assert updated.name == "Updated Name"
    assert persisted is not None
    assert persisted.description == "Updated category description"
    assert persisted.is_active is False


@pytest.mark.asyncio(loop_scope="session")
async def test_duplicate_category_name_raises_and_preserves_existing_row(db_session):
    repository = CategoryRepository(db_session)
    original = await repository.create(make_category("Unique Category"))
    original_id = original.id

    with pytest.raises(CategoryAlreadyExistsError):
        await repository.create(make_category("Unique Category", IssueType.SOFTWARE))

    persisted = await db_session.scalar(
        select(ErrorCategory).where(ErrorCategory.id == original_id)
    )
    assert persisted is not None
    assert persisted.issue_type == IssueType.HARDWARE
    assert await db_session.scalar(
        select(ErrorCategory).where(ErrorCategory.issue_type == IssueType.SOFTWARE)
    ) is None
