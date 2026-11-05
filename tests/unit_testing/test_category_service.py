from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import UserNotFoundError
from app.repositories.interfaces.category_interface import CategoryInterface
from app.schemas.error_categorySchema import CategoryUpdate
from app.services.category_service import CategoryService


@pytest.fixture
def category_repository():
    return AsyncMock(spec=CategoryInterface)


@pytest.fixture
def category_service(category_repository):
    return CategoryService(category_repository)


# 1. Get category by ID successfully
@pytest.mark.asyncio
async def test_get_category_by_id(category_service, category_repository):
    category = SimpleNamespace(id=1, name="Hardware Issue")
    category_repository.get_by_id.return_value = category

    result = await category_service.get_category_by_id(1)

    assert result == category
    category_repository.get_by_id.assert_awaited_once_with(1)


# 2. Update category successfully
@pytest.mark.asyncio
async def test_update_category_success(category_service, category_repository):
    category = SimpleNamespace(
        id=1,
        name="Hardware Issue",
        description="Old description",
    )

    data = CategoryUpdate(description="Updated description")

    category_repository.get_by_id.return_value = category
    category_repository.update.side_effect = lambda category: category

    result = await category_service.update_category(1, data)

    assert result.description == "Updated description"
    category_repository.update.assert_awaited_once()


# 3. Update category that does not exist
@pytest.mark.asyncio
async def test_update_category_not_found(category_service, category_repository):
    category_repository.get_by_id.return_value = None

    data = CategoryUpdate(description="Updated description")

    with pytest.raises(UserNotFoundError):
        await category_service.update_category(1, data)

    category_repository.update.assert_not_awaited()


# 4. Deactivate category successfully
@pytest.mark.asyncio
async def test_deactivate_category_success(category_service, category_repository):
    category = SimpleNamespace(id=1, is_active=True)

    category_repository.get_by_id.return_value = category
    category_repository.update.side_effect = lambda category: category

    result = await category_service.deactivate_category(1)

    assert result.is_active is False
    category_repository.update.assert_awaited_once()


# 5. Activate category successfully
@pytest.mark.asyncio
async def test_activate_category_success(category_service, category_repository):
    category = SimpleNamespace(id=1, is_active=False)

    category_repository.get_by_id.return_value = category
    category_repository.update.side_effect = lambda category: category

    result = await category_service.activate_category(1)

    assert result.is_active is True
    category_repository.update.assert_awaited_once()
