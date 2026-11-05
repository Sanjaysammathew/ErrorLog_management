from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    ApprovalAlreadyDecidedError,
    PermissionDeniedError,
)
from app.models.user import ApprovalStatus, UserRole
from app.repositories.interfaces.approval_interface import ApprovalInterface
from app.services.approval_service import ApprovalService
from app.services.email_service import EmailService

# Fixtures


@pytest.fixture
def approval_repository():
    return AsyncMock(spec=ApprovalInterface)


@pytest.fixture
def email_service():
    return AsyncMock(spec=EmailService)


@pytest.fixture
def approval_service(approval_repository, email_service):
    return ApprovalService(approval_repository, email_service)


@pytest.fixture
def manager():
    return SimpleNamespace(
        id=2,
        role=UserRole.MANAGER,
        is_active=True,
    )


@pytest.fixture
def sample_approval(manager):
    ticket = SimpleNamespace(
        id=10,
        status="pending_approval",
    )

    return SimpleNamespace(
        id=1,
        ticket_id=10,
        manager_id=manager.id,
        status=ApprovalStatus.PENDING,
        decision_reason=None,
        approved_at=None,
        ticket=ticket,
    )


# 1. Get pending approvals


@pytest.mark.asyncio
async def test_get_pending_approvals(
    approval_service,
    approval_repository,
    manager,
    sample_approval,
):
    approval_repository.get_pending_approvals.return_value = [sample_approval]

    result = await approval_service.get_pending_approvals(manager)

    assert len(result) == 1
    assert result[0].status == ApprovalStatus.PENDING

    approval_repository.get_pending_approvals.assert_awaited_once_with(2)


# 2. Employee cannot access pending approvals


@pytest.mark.asyncio
async def test_employee_cannot_get_pending_approvals(
    approval_service,
    approval_repository,
):
    employee = SimpleNamespace(
        id=3,
        role=UserRole.EMPLOYEE,
        is_active=True,
    )

    with pytest.raises(PermissionDeniedError):
        await approval_service.get_pending_approvals(employee)

    approval_repository.get_pending_approvals.assert_not_awaited()


# 3. Get approval by ID


@pytest.mark.asyncio
async def test_get_approval_by_id(
    approval_service,
    approval_repository,
    manager,
    sample_approval,
):
    approval_repository.get_approval_by_id.return_value = sample_approval

    result = await approval_service.get_approval_by_id(1, manager)

    assert result.id == 1
    assert result.manager_id == manager.id

    approval_repository.get_approval_by_id.assert_awaited_once_with(1)


# 4. Approve ticket successfully


@pytest.mark.asyncio
async def test_approve_ticket(
    approval_service,
    approval_repository,
    email_service,
    manager,
    sample_approval,
):
    approval_repository.get_approval_by_id.return_value = sample_approval
    approval_repository.save_decision.return_value = sample_approval

    result = await approval_service.decide_approval(
        approval_id=1,
        status=ApprovalStatus.APPROVED,
        decision_reason="Approved for replacement",
        current_user=manager,
    )

    assert result.status == ApprovalStatus.APPROVED
    assert result.decision_reason == "Approved for replacement"
    assert result.approved_at is not None
    assert result.ticket.status == "open"

    approval_repository.save_decision.assert_awaited_once()

    history = approval_repository.save_decision.await_args.args[1]

    assert history.old_status == "pending_approval"
    assert history.new_status == "open"
    assert history.changed_by_id == manager.id

    email_service.send_approval_decision.assert_awaited_once_with(
        sample_approval.ticket,
        "approved",
        "Approved for replacement",
    )


# 5. Reject ticket successfully


@pytest.mark.asyncio
async def test_reject_ticket(
    approval_service,
    approval_repository,
    email_service,
    manager,
    sample_approval,
):
    approval_repository.get_approval_by_id.return_value = sample_approval
    approval_repository.save_decision.return_value = sample_approval

    result = await approval_service.decide_approval(
        approval_id=1,
        status=ApprovalStatus.REJECTED,
        decision_reason="Replacement is not required",
        current_user=manager,
    )

    assert result.status == ApprovalStatus.REJECTED
    assert result.decision_reason == "Replacement is not required"
    assert result.approved_at is not None
    assert result.ticket.status == "rejected"

    approval_repository.save_decision.assert_awaited_once()

    history = approval_repository.save_decision.await_args.args[1]

    assert history.old_status == "pending_approval"
    assert history.new_status == "rejected"

    email_service.send_approval_decision.assert_awaited_once_with(
        sample_approval.ticket,
        "rejected",
        "Replacement is not required",
    )


# 6. Cannot decide an already decided approval


@pytest.mark.asyncio
async def test_already_decided_approval(
    approval_service,
    approval_repository,
    manager,
    sample_approval,
):
    sample_approval.status = ApprovalStatus.APPROVED

    approval_repository.get_approval_by_id.return_value = sample_approval

    with pytest.raises(ApprovalAlreadyDecidedError):
        await approval_service.decide_approval(
            approval_id=1,
            status=ApprovalStatus.REJECTED,
            decision_reason="Trying to reject again",
            current_user=manager,
        )

    approval_repository.save_decision.assert_not_awaited()
