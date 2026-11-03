from app.models.ticket_approval import TicketApproval
from app.exceptions.custom_exceptions import PermissionDeniedError
from app.models.user import UserRole, user
from app.repositories.interfaces.approval_interface import ApprovalInterface


class ApprovalService:
    def __init__(self, approval_repository: ApprovalInterface) -> None:
        self.approval_repository = approval_repository

    async def get_pending_approvals(
        self, current_user: user
    ) -> list[TicketApproval]:
        if not current_user.is_active or current_user.role != UserRole.MANAGER:
            raise PermissionDeniedError
        return await self.approval_repository.get_pending_approvals(current_user.id)
