from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    PermissionDeniedError,
    TicketNotFoundError,
)
from app.models.user import UserRole, user
from app.repositories.interfaces.ticket_interface import TicketInterface
from app.schemas.ticket_remarkSchema import RemarkCreate
from app.services.remark_service import RemarkService


@pytest.fixture
def ticket_repository():
    return AsyncMock(spec=TicketInterface)


@pytest.fixture
def remark_service(ticket_repository):
    return RemarkService(ticket_repository)


# 1. Admin successfully adds a remark
@pytest.mark.asyncio
async def test_add_remark_success(remark_service, ticket_repository):
    admin = user(id=1, role=UserRole.ADMIN, is_active=True)
    data = RemarkCreate(remark="Issue is being investigated")

    ticket_repository.get_ticket_by_id.return_value = SimpleNamespace(id=10)
    ticket_repository.create_remark.side_effect = lambda remark: remark

    result = await remark_service.add_remark(10, data, admin)

    assert result.ticket_id == 10
    assert result.user_id == 1
    assert result.remark == "Issue is being investigated"
    ticket_repository.create_remark.assert_awaited_once()


# 2. Employee cannot add a remark
@pytest.mark.asyncio
async def test_add_remark_permission_denied(remark_service, ticket_repository):
    employee = user(id=3, role=UserRole.EMPLOYEE, is_active=True)
    data = RemarkCreate(remark="Please check this issue")

    with pytest.raises(PermissionDeniedError):
        await remark_service.add_remark(10, data, employee)

    ticket_repository.get_ticket_by_id.assert_not_awaited()


# 3. Adding a remark to a non-existing ticket
@pytest.mark.asyncio
async def test_add_remark_ticket_not_found(remark_service, ticket_repository):
    admin = user(id=1, role=UserRole.ADMIN, is_active=True)
    data = RemarkCreate(remark="Checking the issue")

    ticket_repository.get_ticket_by_id.return_value = None

    with pytest.raises(TicketNotFoundError):
        await remark_service.add_remark(10, data, admin)


# 4. Admin successfully gets remarks
@pytest.mark.asyncio
async def test_get_remarks_admin_success(remark_service, ticket_repository):
    admin = user(id=1, role=UserRole.ADMIN, is_active=True)
    remarks = [SimpleNamespace(remark="Issue checked")]

    ticket_repository.get_ticket_by_id.return_value = SimpleNamespace(user_id=3)
    ticket_repository.get_remarks.return_value = remarks

    result = await remark_service.get_remarks(10, admin)

    assert result == remarks
    ticket_repository.get_remarks.assert_awaited_once_with(10)


# 5. Employee successfully gets remarks for their own ticket
@pytest.mark.asyncio
async def test_get_remarks_employee_success(remark_service, ticket_repository):
    employee = user(id=3, role=UserRole.EMPLOYEE, is_active=True)
    remarks = [SimpleNamespace(remark="Working on it")]

    ticket_repository.get_ticket_by_id.return_value = SimpleNamespace(user_id=3)
    ticket_repository.get_remarks.return_value = remarks

    result = await remark_service.get_remarks(10, employee)

    assert result == remarks


# 6. Employee cannot access another employee's remarks
@pytest.mark.asyncio
async def test_get_remarks_permission_denied(remark_service, ticket_repository):
    employee = user(id=3, role=UserRole.EMPLOYEE, is_active=True)

    ticket_repository.get_ticket_by_id.return_value = SimpleNamespace(user_id=5)

    with pytest.raises(PermissionDeniedError):
        await remark_service.get_remarks(10, employee)

    ticket_repository.get_remarks.assert_not_awaited()
