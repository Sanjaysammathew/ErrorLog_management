from fastapi import APIRouter, Depends

from app.api.dependency.dependencies import (
    get_approval_service,
    require_roles,
)
from app.models.user import UserRole, user
from app.schemas.ticket_approvalSchema import ApprovalResponse
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending-approvals", response_model=list[ApprovalResponse])
async def get_pending_approvals(
    approval_service: ApprovalService = Depends(get_approval_service),
    current_user: user = Depends(require_roles(UserRole.MANAGER)),
) -> list[ApprovalResponse]:
    """
    Get pending approvals for the authenticated manager.
    """
    return await approval_service.get_pending_approvals(current_user)
