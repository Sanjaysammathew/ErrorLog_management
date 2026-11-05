from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.error_ticket import ErrorTickets
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import ApprovalStatus, UserRole, user
from app.repositories.implementations.approval_repository import ApprovalRepository


async def create_approval_fixture(db_session, *, status=ApprovalStatus.PENDING):
    category = ErrorCategory(
        name="Approval Test Category",
        issue_type=IssueType.SOFTWARE,
        default_sla_hours=12,
    )
    db_session.add(category)
    await db_session.flush()
    employee = await db_session.scalar(
        select(user).where(user.email == "employee@example.com")
    )
    manager = await db_session.scalar(
        select(user).where(user.email == "manager@example.com")
    )
    ticket = ErrorTickets(
        ticket_number=f"A-{datetime.utcnow().timestamp()}",
        title="Requires approval",
        status="pending_approval",
        requires_approval=True,
        category_id=category.id,
        user_id=employee.id,
        assigned_admin_id=1,
    )
    db_session.add(ticket)
    await db_session.flush()
    approval = TicketApproval(
        ticket=ticket,
        manager_id=manager.id,
        status=status,
    )
    db_session.add(approval)
    await db_session.commit()
    await db_session.refresh(approval)
    return ticket, manager, approval


@pytest.mark.asyncio(loop_scope="session")
async def test_pending_approvals_returns_manager_requests_from_database(db_session):
    repository = ApprovalRepository(db_session)
    ticket, manager, approval = await create_approval_fixture(db_session)

    pending = await repository.get_pending_approvals(manager.id)

    assert len(pending) == 1
    assert pending[0].id == approval.id
    assert pending[0].ticket.id == ticket.id
    persisted = await db_session.scalar(
        select(TicketApproval).where(TicketApproval.id == approval.id)
    )
    assert persisted is not None and persisted.status == ApprovalStatus.PENDING


@pytest.mark.asyncio(loop_scope="session")
async def test_pending_approvals_excludes_decided_and_other_manager_requests(
    db_session,
):
    repository = ApprovalRepository(db_session)
    _, manager, pending_approval = await create_approval_fixture(db_session)
    decided_ticket, _, _ = await create_approval_fixture_for_other_ticket(
        db_session, manager, ApprovalStatus.APPROVED
    )
    other_manager = user(
        username="second_manager",
        email="second_manager@example.com",
        hashed_password="hashed-password",
        role=UserRole.MANAGER,
    )
    db_session.add(other_manager)
    await db_session.flush()
    other_ticket, _, _ = await create_approval_fixture_for_other_ticket(
        db_session, other_manager, ApprovalStatus.PENDING
    )
    await db_session.commit()

    results = await repository.get_pending_approvals(manager.id)

    assert [item.id for item in results] == [pending_approval.id]
    assert all(
        item.ticket_id not in {decided_ticket.id, other_ticket.id}
        for item in results
    )


async def create_approval_fixture_for_other_ticket(db_session, manager, status):
    category = await db_session.scalar(
        select(ErrorCategory).where(ErrorCategory.name == "Approval Test Category")
    )
    employee = await db_session.scalar(
        select(user).where(user.email == "employee@example.com")
    )
    ticket = ErrorTickets(
        ticket_number=f"A-{status.value}-{datetime.utcnow().microsecond}",
        title="Second approval ticket",
        status="pending_approval",
        requires_approval=True,
        category_id=category.id,
        user_id=employee.id,
        assigned_admin_id=1,
    )
    db_session.add(ticket)
    await db_session.flush()
    approval = TicketApproval(
        ticket_id=ticket.id,
        manager_id=manager.id,
        status=status,
        approved_at=datetime.utcnow() if status != ApprovalStatus.PENDING else None,
    )
    db_session.add(approval)
    await db_session.flush()
    return ticket, manager, approval


@pytest.mark.asyncio(loop_scope="session")
async def test_get_approval_by_id_loads_related_ticket_and_missing_returns_none(
    db_session,
):
    repository = ApprovalRepository(db_session)
    ticket, _, approval = await create_approval_fixture(db_session)

    found = await repository.get_approval_by_id(approval.id)

    assert found is not None
    assert found.ticket_id == ticket.id
    assert found.ticket.title == "Requires approval"
    assert found.ticket.category.name == "Approval Test Category"
    assert await repository.get_approval_by_id(999999) is None


@pytest.mark.asyncio(loop_scope="session")
async def test_save_decision_persists_approval_ticket_and_history(db_session):
    repository = ApprovalRepository(db_session)
    ticket, manager, approval = await create_approval_fixture(db_session)
    approval.status = ApprovalStatus.APPROVED
    approval.decision_reason = "Approved for replacement"
    approval.approved_at = datetime.utcnow()
    ticket.status = "open"
    history = TicketStatusHistory(
        ticket_id=ticket.id,
        changed_by_id=manager.id,
        old_status="pending_approval",
        new_status="open",
    )

    saved = await repository.save_decision(approval, history)
    persisted_approval = await db_session.scalar(
        select(TicketApproval).where(TicketApproval.id == approval.id)
    )
    persisted_ticket = await db_session.scalar(
        select(ErrorTickets).where(ErrorTickets.id == ticket.id)
    )
    persisted_history = await db_session.scalar(
        select(TicketStatusHistory).where(TicketStatusHistory.ticket_id == ticket.id)
    )

    assert saved.status == ApprovalStatus.APPROVED
    assert persisted_approval is not None
    assert persisted_approval.decision_reason == "Approved for replacement"
    assert persisted_ticket is not None and persisted_ticket.status == "open"
    assert persisted_history is not None and persisted_history.new_status == "open"


@pytest.mark.asyncio(loop_scope="session")
async def test_save_duplicate_ticket_manager_decision_fails_database_constraint(
    db_session,
):
    repository = ApprovalRepository(db_session)
    ticket, manager, _ = await create_approval_fixture(db_session)
    ticket_id = ticket.id
    duplicate = TicketApproval(
        ticket=ticket,
        manager_id=manager.id,
        status=ApprovalStatus.PENDING,
    )
    history = TicketStatusHistory(
        ticket_id=ticket.id,
        changed_by_id=manager.id,
        old_status="pending_approval",
        new_status="open",
    )

    with pytest.raises(IntegrityError):
        await repository.save_decision(duplicate, history)
    await db_session.rollback()

    approvals = (
        await db_session.scalars(
            select(TicketApproval).where(TicketApproval.ticket_id == ticket_id)
        )
    ).all()
    assert len(approvals) == 1
