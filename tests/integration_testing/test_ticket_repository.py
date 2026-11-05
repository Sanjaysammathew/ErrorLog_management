from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.exceptions.custom_exceptions import TicketCreationError
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.models.error_ticket import ErrorTickets
from app.models.ticket_remark import TicketRemark
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import UserRole, user
from app.repositories.implementations.ticket_repository import TicketRepository


async def make_category(db_session):
    category = ErrorCategory(
        name="Ticket Test Category",
        issue_type=IssueType.HARDWARE,
        description="Category for repository tests",
        default_sla_hours=24,
        is_active=True,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


async def make_ticket(db_session, *, title="Test ticket", **overrides):
    category = await make_category(db_session)
    employee = await db_session.scalar(
        select(user).where(user.email == "employee@example.com")
    )
    admin = await db_session.scalar(select(user).where(user.email == "admin@example.com"))
    ticket = ErrorTickets(
        ticket_number=overrides.get("ticket_number", f"T-{title[:8]}"),
        title=title,
        description=overrides.get("description", "Repository integration test"),
        status=overrides.get("status", "open"),
        priority=overrides.get("priority", "medium"),
        requires_approval=overrides.get("requires_approval", False),
        due_at=overrides.get("due_at"),
        category_id=category.id,
        user_id=employee.id,
        assigned_admin_id=admin.id,
    )
    return ticket, employee, admin


@pytest.mark.asyncio(loop_scope="session")
async def test_create_ticket_and_commit_persist_ticket(db_session):
    repository = TicketRepository(db_session)
    ticket, employee, _ = await make_ticket(db_session, title="Created Ticket")

    created = await repository.create_ticket(ticket)
    await repository.commit()
    persisted = await db_session.scalar(
        select(ErrorTickets).where(ErrorTickets.id == created.id)
    )

    assert created.id is not None
    assert persisted is not None
    assert persisted.title == "Created Ticket"
    assert persisted.user_id == employee.id


@pytest.mark.asyncio(loop_scope="session")
async def test_ticket_retrieval_filters_by_owner_and_identifier(db_session):
    repository = TicketRepository(db_session)
    owned, employee, _ = await make_ticket(db_session, title="Owned Ticket")
    other = user(
        username="other_employee",
        email="other_employee@example.com",
        hashed_password="hashed-password",
        role=UserRole.EMPLOYEE,
    )
    db_session.add(other)
    await db_session.flush()
    other_ticket = ErrorTickets(
        ticket_number="T-OTHER",
        title="Other Ticket",
        category_id=owned.category_id,
        user_id=other.id,
        assigned_admin_id=owned.assigned_admin_id,
    )
    db_session.add_all([owned, other_ticket])
    await db_session.commit()

    owned_tickets = await repository.get_by_user_id(employee.id)
    found = await repository.get_ticket_by_id(other_ticket.id)

    assert [item.id for item in owned_tickets] == [owned.id]
    assert found is not None and found.title == "Other Ticket"
    assert found.category.name == "Ticket Test Category"
    assert await repository.get_ticket_by_id(999999) is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_overdue_tickets_excludes_future_and_closed_tickets(db_session):
    repository = TicketRepository(db_session)
    past_open, _, _ = await make_ticket(
        db_session,
        title="Past Open",
        ticket_number="T-PAST-OPEN",
        due_at=datetime.utcnow() - timedelta(days=1),
    )
    future_open = ErrorTickets(
        ticket_number="T-FUTURE",
        title="Future Open",
        category_id=past_open.category_id,
        user_id=past_open.user_id,
        assigned_admin_id=past_open.assigned_admin_id,
        due_at=datetime.utcnow() + timedelta(days=1),
    )
    past_closed = ErrorTickets(
        ticket_number="T-PAST-CLOSED",
        title="Past Closed",
        status="closed",
        category_id=past_open.category_id,
        user_id=past_open.user_id,
        assigned_admin_id=past_open.assigned_admin_id,
        due_at=datetime.utcnow() - timedelta(days=2),
    )
    db_session.add_all([past_open, future_open, past_closed])
    await db_session.commit()

    overdue = await repository.get_overdue_tickets()

    assert [ticket.ticket_number for ticket in overdue] == ["T-PAST-OPEN"]


@pytest.mark.asyncio(loop_scope="session")
async def test_save_status_update_persists_ticket_history_and_remark(db_session):
    repository = TicketRepository(db_session)
    ticket, employee, _ = await make_ticket(db_session, title="Status Update")
    ticket.status = "resolved"
    history = TicketStatusHistory(
        ticket=ticket,
        changed_by_id=employee.id,
        old_status="open",
        new_status="resolved",
    )
    remark = TicketRemark(ticket=ticket, user_id=employee.id, remark="Issue fixed")

    updated = await repository.save_status_update(ticket, history, remark)
    persisted_ticket = await db_session.scalar(
        select(ErrorTickets).where(ErrorTickets.id == ticket.id)
    )
    persisted_history = await db_session.scalar(
        select(TicketStatusHistory).where(TicketStatusHistory.ticket_id == ticket.id)
    )
    persisted_remark = await db_session.scalar(
        select(TicketRemark).where(TicketRemark.ticket_id == ticket.id)
    )

    assert updated.status == "resolved"
    assert persisted_ticket is not None and persisted_ticket.status == "resolved"
    assert persisted_history is not None and persisted_history.new_status == "resolved"
    assert persisted_remark is not None and persisted_remark.remark == "Issue fixed"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_ticket_maps_integrity_failure_and_rolls_back(db_session):
    repository = TicketRepository(db_session)
    invalid_ticket = ErrorTickets(
        ticket_number="T-BAD-FK",
        title="Invalid foreign key",
        category_id=999999,
        user_id=999999,
        assigned_admin_id=999999,
    )

    with pytest.raises(TicketCreationError):
        await repository.create_ticket(invalid_ticket)

    assert await db_session.scalar(
        select(ErrorTickets).where(ErrorTickets.ticket_number == "T-BAD-FK")
    ) is None
