from fastapi import APIRouter, Depends

from app.api.dependency.dependencies import (
    get_approval_service,
    require_roles,
)
from app.models.user import UserRole, user
from app.schemas.ticket_approvalSchema import ApprovalAction, ApprovalResponse
from app.models.user import ApprovalStatus
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending-approvals", response_model=list[ApprovalResponse])
async def get_pending_approvals(
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user: user = Depends(require_roles(UserRole.MANAGER)),
) -> list[ApprovalResponse]:
    """List approval requests that are waiting for the current manager's decision.

        Only managers can access this endpoint. Return pending approvals assigned
        to the authenticated manager so they can review the related tickets.
    """
    return await approval_service.get_pending_approvals(current_user)


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval_by_id(
    approval_id: int,
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user: user = Depends(require_roles(UserRole.MANAGER)),
) -> ApprovalResponse:
    """Retrieve the details of a specific approval request by ID.

        Only managers can access this endpoint, and the service verifies that the
        approval is available to the current manager before returning its details.
    """
    return await approval_service.get_approval_by_id(approval_id, current_user)


@router.patch("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_approval(
    approval_id: int,
    decision: ApprovalAction | None = None,
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user: user = Depends(require_roles(UserRole.MANAGER)),
) -> ApprovalResponse:
    """Approve the ticket associated with the specified approval request.

        Only managers can decide approvals. An optional decision reason is stored
        with the decision, and the updated approval record is returned.
    """
    return await approval_service.decide_approval(
        approval_id,
        ApprovalStatus.APPROVED,
        decision.decision_reason if decision else None,
        current_user,
    )


@router.patch("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_approval(
    approval_id: int,
    decision: ApprovalAction | None = None,
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user: user = Depends(require_roles(UserRole.MANAGER)),
) -> ApprovalResponse:
    """Reject the ticket associated with the specified approval request.

        Only managers can decide approvals. An optional decision reason is stored
        with the decision, and the updated approval record is returned.
    """
    return await approval_service.decide_approval(
        approval_id,
        ApprovalStatus.REJECTED,
        decision.decision_reason if decision else None,
        current_user,
    )
