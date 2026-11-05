from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import TicketCreationError
from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.ticket_remark import TicketRemark
from app.repositories.interfaces.ticket_interface import TicketInterface


class TicketRepository(TicketInterface):
    """Provide database access for ticket records.

        The repository implements persistence operations used by services.
    """
    def __init__(self, db: AsyncSession) -> None:
        """Initialize the ticket repository with its database session.

            The session is used for the repository's persistence operations.
        """
        self.db = db

    async def create_ticket(self, new_ticket: ErrorTickets) -> ErrorTickets:
        """Create a support ticket and its initial workflow records.

            The operation applies category, approval, and due-date rules.
        """
        self.db.add(new_ticket)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise TicketCreationError from exc

        return new_ticket

    async def create_status_history(
        self, history: TicketStatusHistory
    ) -> TicketStatusHistory:
        """Record a ticket status change in the database.

            The history entry preserves the ticket workflow timeline.
        """
        self.db.add(history)
        await self.db.flush()
        return history

    async def create_approval(self, approval: TicketApproval) -> TicketApproval:
        """Create an approval request for a ticket.

            The repository stores the request for manager review.
        """
        self.db.add(approval)
        await self.db.flush()
        return approval

    async def get_by_user_id(self, user_id: int) -> list[ErrorTickets]:
        """Find tickets associated with a specific user account.

            The repository returns matching records from the database.
        """
        result = await self.db.execute(
            select(ErrorTickets)
            .options(
                selectinload(ErrorTickets.category),
                selectinload(ErrorTickets.created_by_user),
                selectinload(ErrorTickets.assigned_admin),
            )
            .where(ErrorTickets.user_id == user_id)
            .order_by(ErrorTickets.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_ticket_by_id(self, ticket_id: int) -> ErrorTickets | None:
        """Find a support ticket by its identifier.

            The service checks whether the current user may view it.
        """
        result = await self.db.execute(
            select(ErrorTickets)
            .options(
                selectinload(ErrorTickets.category),
                selectinload(ErrorTickets.created_by_user),
                selectinload(ErrorTickets.assigned_admin),
            )
            .where(ErrorTickets.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_user(self):
        """Find the user account needed by the operation.

            The service returns the matching account or reports that it is missing.
        """
        result = await self.db.execute(
            select(ErrorTickets).options(
                selectinload(ErrorTickets.category),
                selectinload(ErrorTickets.created_by_user),
                selectinload(ErrorTickets.assigned_admin),
            )
        )
        return list(result.scalars().all())

    async def get_overdue_tickets(self) -> list[ErrorTickets]:
        """Find tickets that remain open past their due time.

            The result supports administrative follow-up on overdue work.
        """
        result = await self.db.execute(
            select(ErrorTickets)
            .options(
                selectinload(ErrorTickets.category),
                selectinload(ErrorTickets.created_by_user),
                selectinload(ErrorTickets.assigned_admin),
            )
            .where(
                ErrorTickets.due_at.is_not(None),
                ErrorTickets.due_at < datetime.utcnow(),
                ErrorTickets.status.notin_(("resolved", "rejected", "closed")),
            )
            .order_by(ErrorTickets.due_at.asc())
        )
        return list(result.scalars().all())

    async def save_status_update(
        self,
        ticket: ErrorTickets,
        history: TicketStatusHistory,
        remark: TicketRemark | None = None,
    ) -> ErrorTickets:
        """Persist a ticket status change and its workflow details.

            The repository commits the update to the database.
        """
        self.db.add(ticket)
        self.db.add(history)
        if remark is not None:
            self.db.add(remark)
        await self.db.commit()
        await self.db.refresh(
            ticket, ["category", "created_by_user", "assigned_admin"]
        )
        return ticket

    async def commit(self) -> None:
        """Persist the pending database changes.

            The operation finalizes the current transaction.
        """
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise TicketCreationError from exc

    async def create_remark(self, remark: TicketRemark) -> TicketRemark:
        """Save a remark associated with a ticket.

            The repository preserves the remark and its author relationship.
        """
        self.db.add(remark)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise TicketCreationError from exc
        await self.db.refresh(remark, ["ticket", "user"])
        return remark

    async def get_remarks(self, ticket_id: int) -> list[TicketRemark]:
        """Retrieve remarks attached to a ticket.

            The service checks ticket access before returning the discussion.
        """
        result = await self.db.execute(
            select(TicketRemark)
            .options(
                selectinload(TicketRemark.ticket),
                selectinload(TicketRemark.user),
            )
            .where(TicketRemark.ticket_id == ticket_id)
            .order_by(TicketRemark.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_status_history(
        self, ticket_id: int
    ) -> list[TicketStatusHistory]:
        """Retrieve the status history entries for a ticket.

            The repository returns the recorded workflow transitions in chronological order.
        """
        result = await self.db.execute(
            select(TicketStatusHistory)
            .where(TicketStatusHistory.ticket_id == ticket_id)
            .order_by(TicketStatusHistory.changed_at.asc())
        )
        return list(result.scalars().all())
