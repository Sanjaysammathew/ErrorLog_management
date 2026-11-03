from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import TicketCreationError
from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.repositories.interfaces.ticket_interface import TicketInterface


class TicketRepository(TicketInterface):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_ticket(self, new_ticket: ErrorTickets) -> ErrorTickets:
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
        self.db.add(history)
        await self.db.flush()
        return history

    async def create_approval(self, approval: TicketApproval) -> TicketApproval:
        self.db.add(approval)
        await self.db.flush()
        return approval

    async def commit(self) -> None:
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise TicketCreationError from exc
