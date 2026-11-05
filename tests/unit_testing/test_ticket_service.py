import pytest
from unittest.mock import AsyncMock

from app.models.user import user, UserRole, TicketPriority
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.models.error_ticket import ErrorTickets
from app.schemas.error_ticketSchema import TicketCreate, TicketStatus

from app.services.ticket_service import TicketService
from app.services.email_service import EmailService

from app.repositories.interfaces.ticket_interface import TicketInterface
from app.repositories.interfaces.category_interface import CategoryInterface
from app.repositories.interfaces.user_interface import UserInterface

from app.exceptions.custom_exceptions import (
    CategoryNotFoundError,
    PermissionDeniedError,
    TicketNotResolvedError,
)

# FIXTURES


@pytest.fixture
def ticket_repository():
    return AsyncMock(spec=TicketInterface)


@pytest.fixture
def category_repository():
    return AsyncMock(spec=CategoryInterface)


@pytest.fixture
def user_repository():
    return AsyncMock(spec=UserInterface)


@pytest.fixture
def email_service():
    return AsyncMock(spec=EmailService)


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def ticket_service(
    ticket_repository,
    category_repository,
    user_repository,
    email_service,
):
    return TicketService(
        ticket_repository,
        category_repository,
        user_repository,
        email_service,
    )


@pytest.fixture
def employee():
    return user(
        id=3,
        username="employee",
        role=UserRole.EMPLOYEE,
        manager_id=2,
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


@pytest.fixture
def category():
    return ErrorCategory(
        id=1,
        name="Hardware Issues",
        issue_type=IssueType.HARDWARE,
        default_sla_hours=24,
        requires_approval_default=False,
        is_active=True,
    )


# 1. CREATE TICKET SUCCESSFULLY


@pytest.mark.asyncio
async def test_create_ticket(
    ticket_service,
    ticket_repository,
    category_repository,
    email_service,
    db,
    employee,
    category,
):
    ticket_data = TicketCreate(
        title="Keyboard not working",
        description="Some keyboard keys are not responding",
        priority=TicketPriority.MEDIUM,
        issue_type=IssueType.HARDWARE,
    )

    category_repository.get_by_issue_type.return_value = category

    async def create_ticket(ticket):
        ticket.id = 10
        return ticket

    ticket_repository.create_ticket.side_effect = create_ticket

    result = await ticket_service.create_ticket(
        db,
        ticket_data,
        employee,
    )

    assert result.id == 10
    assert result.status == "open"
    assert result.requires_approval is False

    # Keyboard keyword gives 8-hour SLA
    assert result.due_at is not None

    ticket_repository.create_ticket.assert_awaited_once()
    ticket_repository.create_status_history.assert_awaited_once()
    ticket_repository.commit.assert_awaited_once()

    email_service.send_ticket_created.assert_awaited_once_with(result)


# 2. CREATE TICKET REQUIRING APPROVAL


@pytest.mark.asyncio
async def test_create_ticket_requires_approval(
    ticket_service,
    ticket_repository,
    category_repository,
    user_repository,
    email_service,
    db,
    category,
):
    employee = user(
        id=3,
        role=UserRole.EMPLOYEE,
        manager_id=2,
        is_active=True,
    )

    manager = user(
        id=2,
        role=UserRole.MANAGER,
        is_active=True,
    )

    ticket_data = TicketCreate(
        title="Hardware replacement required",
        description="Laptop motherboard replacement",
        priority=TicketPriority.HIGH,
        issue_type=IssueType.HARDWARE,
    )

    category_repository.get_by_issue_type.return_value = category
    user_repository.get_by_id.return_value = manager

    async def create_ticket(ticket):
        ticket.id = 11
        return ticket

    ticket_repository.create_ticket.side_effect = create_ticket

    result = await ticket_service.create_ticket(
        db,
        ticket_data,
        employee,
    )

    assert result.requires_approval is True
    assert result.status == "pending_approval"

    user_repository.get_by_id.assert_awaited_once_with(2)

    ticket_repository.create_approval.assert_awaited_once()
    ticket_repository.commit.assert_awaited_once()


# 3. REJECT TICKET WHEN CATEGORY IS INACTIVE


@pytest.mark.asyncio
async def test_create_ticket_rejects_inactive_category(
    ticket_service,
    category_repository,
    db,
    employee,
):
    ticket_data = TicketCreate(
        title="Keyboard not working",
        description="Some keyboard keys are not responding",
        priority=TicketPriority.MEDIUM,
        issue_type=IssueType.HARDWARE,
    )
    inactive_category = ErrorCategory(
        id=1,
        name="Hardware Issues",
        issue_type=IssueType.HARDWARE,
        is_active=False,
    )

    category_repository.get_by_issue_type.return_value = None
    category_repository.get_by_issue_type_any_status.return_value = inactive_category

    with pytest.raises(CategoryNotFoundError, match="category is inactive"):
        await ticket_service.create_ticket(db, ticket_data, employee)


# 4. GET MY TICKETS


@pytest.mark.asyncio
async def test_get_my_tickets(
    ticket_service,
    ticket_repository,
    employee,
):
    tickets = [
        ErrorTickets(id=1, user_id=3),
        ErrorTickets(id=2, user_id=3),
    ]

    ticket_repository.get_by_user_id.return_value = tickets

    result = await ticket_service.get_my_tickets(employee)

    assert len(result) == 2
    assert result[0].user_id == employee.id

    ticket_repository.get_by_user_id.assert_awaited_once_with(3)


# 4. EMPLOYEE CANNOT ACCESS ANOTHER EMPLOYEE'S TICKET


@pytest.mark.asyncio
async def test_employee_cannot_access_other_ticket(
    ticket_service,
    ticket_repository,
    employee,
):
    ticket = ErrorTickets(
        id=10,
        user_id=5,
    )

    ticket_repository.get_ticket_by_id.return_value = ticket

    with pytest.raises(PermissionDeniedError):
        await ticket_service.get_ticket_by_id(10, employee)

    ticket_repository.get_ticket_by_id.assert_awaited_once_with(10)


# 5. UPDATE TICKET STATUS


@pytest.mark.asyncio
async def test_update_ticket_status(
    ticket_service,
    ticket_repository,
    admin,
):
    ticket = ErrorTickets(
        id=10,
        user_id=3,
        status="open",
    )

    ticket_repository.get_ticket_by_id.return_value = ticket
    ticket_repository.save_status_update.return_value = ticket

    result = await ticket_service.update_ticket_status(
        ticket_id=10,
        new_status=TicketStatus.IN_PROGRESS,
        remarks="Work has started",
        current_user=admin,
    )

    assert result.status == "in_progress"

    ticket_repository.save_status_update.assert_awaited_once()

    # Verify history and remark were passed
    call_args = ticket_repository.save_status_update.await_args

    history = call_args.args[1]
    remark = call_args.args[2]

    assert history.old_status == "open"
    assert history.new_status == "in_progress"
    assert remark.remark == "Work has started"


# 6. CANNOT CLOSE UNRESOLVED TICKET


@pytest.mark.asyncio
async def test_close_unresolved_ticket(
    ticket_service,
    ticket_repository,
    admin,
):
    ticket = ErrorTickets(
        id=10,
        user_id=3,
        status="open",
    )

    ticket_repository.get_ticket_by_id.return_value = ticket

    with pytest.raises(TicketNotResolvedError):
        await ticket_service.close_ticket(10, admin)

    ticket_repository.save_status_update.assert_not_awaited()
    ticket_repository.commit.assert_not_awaited()
