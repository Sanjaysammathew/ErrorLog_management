from datetime import UTC, datetime

from app.exceptions.custom_exceptions import (
    ApprovalAlreadyDecidedError,
    InvalidTicketStatusTransitionError,
    PermissionDeniedError,
    TicketNotFoundError,
)
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import ApprovalStatus, UserRole, user
from app.repositories.interfaces.approval_interface import ApprovalInterface
from app.services.email_service import EmailService


class ApprovalService:
    """Apply business rules for approval operations.

        The service coordinates validation and the required data access.
    """
    def __init__(
        self,
        approval_repository: ApprovalInterface,
        email_service: EmailService,
    ) -> None:
        """Initialize the approval service with its collaborators.

            These dependencies provide data access and related business services.
        """
        self.approval_repository = approval_repository
        self.email_service = email_service

    async def get_pending_approvals(self, current_user: user) -> list[TicketApproval]:
        """Retrieve approval requests that are waiting for a manager's decision.

            The service or repository returns pending requests for review.
        """
        if not current_user.is_active or current_user.role != UserRole.MANAGER:
            raise PermissionDeniedError
        return await self.approval_repository.get_pending_approvals(current_user.id)

    async def get_approval_by_id(
        self, approval_id: int, current_user: user
    ) -> TicketApproval:
        """Find one approval request by its identifier.

            The service checks manager access before returning its details.
        """
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
        """Record a manager's approval or rejection decision.

            The decision updates the request and the related ticket workflow.
        """
        if not current_user.is_active or current_user.role != UserRole.MANAGER:
            raise PermissionDeniedError

        approval = await self.approval_repository.get_approval_by_id(approval_id)
        if approval is None or approval.manager_id != current_user.id:
            raise TicketNotFoundError
        if approval.status != ApprovalStatus.PENDING:
            raise ApprovalAlreadyDecidedError
        if approval.ticket.status != "pending_approval":
            raise InvalidTicketStatusTransitionError(
                "Only pending-approval tickets can receive an approval decision"
            )

        decision_at = datetime.now(UTC).replace(tzinfo=None)
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

        decided_approval = await self.approval_repository.save_decision(
            approval, history
        )
        await self.email_service.send_approval_decision(
            decided_approval.ticket,
            status.value,
            decision_reason,
        )
        return decided_approval
