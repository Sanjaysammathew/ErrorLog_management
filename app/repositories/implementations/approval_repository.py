from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import ApprovalStatus
from app.repositories.interfaces.approval_interface import ApprovalInterface


class ApprovalRepository(ApprovalInterface):
    """Provide database access for approval records.

        The repository implements persistence operations used by services.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the approval repository with its database session.

            The session is used for the repository's persistence operations.
        """
        self.db = db

    async def get_pending_approvals(self, manager_id: int) -> list[TicketApproval]:
        """Retrieve approval requests that are waiting for a manager's decision.

            The service or repository returns pending requests for review.
        """
        result = await self.db.execute(
            select(TicketApproval)
            .options(
                selectinload(TicketApproval.ticket).selectinload(ErrorTickets.category),
                selectinload(TicketApproval.ticket).selectinload(
                    ErrorTickets.created_by_user
                ),
                selectinload(TicketApproval.ticket).selectinload(
                    ErrorTickets.assigned_admin
                ),
            )
            .where(
                TicketApproval.manager_id == manager_id,
                TicketApproval.status == ApprovalStatus.PENDING,
            )
            .order_by(TicketApproval.id.asc())
        )
        return list(result.scalars().all())

    async def get_approval_by_id(self, approval_id: int) -> TicketApproval | None:
        """Find one approval request by its identifier.

            The service checks manager access before returning its details.
        """
        result = await self.db.execute(
            select(TicketApproval)
            .options(
                selectinload(TicketApproval.ticket).selectinload(ErrorTickets.category),
                selectinload(TicketApproval.ticket).selectinload(
                    ErrorTickets.created_by_user
                ),
                selectinload(TicketApproval.ticket).selectinload(
                    ErrorTickets.assigned_admin
                ),
            )
            .where(TicketApproval.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def save_decision(
        self,
        approval: TicketApproval,
        history: TicketStatusHistory,
    ) -> TicketApproval:
        """Persist a manager decision on an approval request.

            The repository saves the approval state and related ticket history.
        """
        self.db.add(approval)
        self.db.add(approval.ticket)
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(
            approval,
            ["ticket"],
        )
        return approval
