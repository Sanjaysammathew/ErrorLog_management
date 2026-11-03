from datetime import datetime, timezone

from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.exceptions.custom_exceptions import (
    ApprovalAlreadyDecidedError,
    PermissionDeniedError,
    TicketNotFoundError,
)
from app.models.user import UserRole, user
from app.models.user import ApprovalStatus
from app.repositories.interfaces.approval_interface import ApprovalInterface


class ApprovalService:
    def __init__(self, approval_repository: ApprovalInterface) -> None:
        self.approval_repository = approval_repository

    async def get_pending_approvals(self, current_user: user) -> list[TicketApproval]:
        if not current_user.is_active or current_user.role != UserRole.MANAGER:
            raise PermissionDeniedError
        return await self.approval_repository.get_pending_approvals(current_user.id)

    async def get_approval_by_id(
        self, approval_id: int, current_user: user
    ) -> TicketApproval:
        if not current_user.is_active or current_user.role != UserRole.MANAGER:
            raise PermissionDeniedError

        approval = await self.approval_repository.get_approval_by_id(approval_id)
        if approval is None or approval.manager_id != current_user.id:
            raise TicketNotFoundError

        return approval

    async def decide_approval(
        self,
        approval_id: int,
        status: ApprovalStatus,
        decision_reason: str | None,
        current_user: user,
    ) -> TicketApproval:
        if not current_user.is_active or current_user.role != UserRole.MANAGER:
            raise PermissionDeniedError

        approval = await self.approval_repository.get_approval_by_id(approval_id)
        if approval is None or approval.manager_id != current_user.id:
            raise TicketNotFoundError
        if approval.status != ApprovalStatus.PENDING:
            raise ApprovalAlreadyDecidedError

        decision_at = datetime.now(timezone.utc).replace(tzinfo=None)
        new_ticket_status = (
            "open" if status == ApprovalStatus.APPROVED else "rejected"
        )
        old_ticket_status = approval.ticket.status

        approval.status = status
        approval.decision_reason = decision_reason
        approval.approved_at = decision_at
        approval.ticket.status = new_ticket_status
        approval.ticket.updated_at = decision_at
        history = TicketStatusHistory(
            ticket_id=approval.ticket.id,
            changed_by_id=current_user.id,
            old_status=old_ticket_status,
            new_status=new_ticket_status,
            changed_at=decision_at,
        )

        return await self.approval_repository.save_decision(
            approval, history
        )
