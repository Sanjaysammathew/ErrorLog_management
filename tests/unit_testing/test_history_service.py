import pytest
from unittest.mock import AsyncMock

from app.models.user import user, UserRole
from app.models.error_ticket import ErrorTickets
from app.models.ticket_status_history import TicketStatusHistory

from app.services.history_service import HistoryService
from app.repositories.interfaces.ticket_interface import TicketInterface

from app.exceptions.custom_exceptions import (
    PermissionDeniedError,
    TicketNotFoundError,
)

# Fixtures


@pytest.fixture
def ticket_repository():
    return AsyncMock(spec=TicketInterface)


@pytest.fixture
def history_service(ticket_repository):
    return HistoryService(ticket_repository)


@pytest.fixture
def employee():
    return user(
        id=3,
        username="employee",
        role=UserRole.EMPLOYEE,
        is_active=True,
    )


@pytest.fixture
def admin():
    return user(
        id=1,
        username="admin",
        role=UserRole.ADMIN,
        is_active=True,
    )


# 1. Admin gets ticket history successfully


@pytest.mark.asyncio
async def test_admin_get_history(
    history_service,
    ticket_repository,
    admin,
):
    ticket = ErrorTickets(id=10, user_id=3)

    history = [
        TicketStatusHistory(
            id=1,
            ticket_id=10,
            changed_by_id=1,
            old_status=None,
            new_status="open",
        ),
        TicketStatusHistory(
            id=2,
            ticket_id=10,
            changed_by_id=1,
            old_status="open",
            new_status="in_progress",
        ),
    ]

    ticket_repository.get_ticket_by_id.return_value = ticket
    ticket_repository.get_status_history.return_value = history

    result = await history_service.get_history(10, admin)

    assert len(result) == 2
    assert result[0].new_status == "open"
    assert result[1].new_status == "in_progress"

    ticket_repository.get_ticket_by_id.assert_awaited_once_with(10)
    ticket_repository.get_status_history.assert_awaited_once_with(10)


# 2. Employee gets own ticket history


@pytest.mark.asyncio
async def test_employee_get_own_history(
    history_service,
    ticket_repository,
    employee,
):
    ticket = ErrorTickets(id=10, user_id=employee.id)

    history = [
        TicketStatusHistory(
            id=1,
            ticket_id=10,
            changed_by_id=3,
            old_status=None,
            new_status="open",
        )
    ]

    ticket_repository.get_ticket_by_id.return_value = ticket
    ticket_repository.get_status_history.return_value = history

    result = await history_service.get_history(10, employee)

    assert len(result) == 1
    assert result[0].ticket_id == 10

    ticket_repository.get_ticket_by_id.assert_awaited_once_with(10)
    ticket_repository.get_status_history.assert_awaited_once_with(10)


# 3. Employee cannot access another employee's history


@pytest.mark.asyncio
async def test_employee_cannot_access_other_history(
    history_service,
    ticket_repository,
    employee,
):
    ticket = ErrorTickets(id=10, user_id=5)

    ticket_repository.get_ticket_by_id.return_value = ticket

    with pytest.raises(PermissionDeniedError):
        await history_service.get_history(10, employee)

    ticket_repository.get_ticket_by_id.assert_awaited_once_with(10)
    ticket_repository.get_status_history.assert_not_awaited()


# 4. Manager cannot access history


@pytest.mark.asyncio
async def test_manager_cannot_access_history(
    history_service,
    ticket_repository,
):
    manager = user(
        id=2,
        username="manager",
        role=UserRole.MANAGER,
        is_active=True,
    )

    ticket = ErrorTickets(id=10, user_id=3)

    ticket_repository.get_ticket_by_id.return_value = ticket

    with pytest.raises(PermissionDeniedError):
        await history_service.get_history(10, manager)

    ticket_repository.get_ticket_by_id.assert_awaited_once_with(10)
    ticket_repository.get_status_history.assert_not_awaited()


# 5. Ticket does not exist


@pytest.mark.asyncio
async def test_ticket_not_found(
    history_service,
    ticket_repository,
    admin,
):
    ticket_repository.get_ticket_by_id.return_value = None

    with pytest.raises(TicketNotFoundError):
        await history_service.get_history(999, admin)

    ticket_repository.get_ticket_by_id.assert_awaited_once_with(999)
    ticket_repository.get_status_history.assert_not_awaited()
