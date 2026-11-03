from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import ApprovalStatus
from app.repositories.interfaces.approval_interface import ApprovalInterface


class ApprovalRepository(ApprovalInterface):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_pending_approvals(self, manager_id: int) -> list[TicketApproval]:
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
        self.db.add(approval)
        self.db.add(approval.ticket)
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(
            approval,
            ["ticket"],
        )
        return approval
