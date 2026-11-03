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

    async def get_by_user_id(self, user_id: int) -> list[ErrorTickets]:
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
        result = await self.db.execute(
            select(ErrorTickets).options(
                selectinload(ErrorTickets.category),
                selectinload(ErrorTickets.created_by_user),
                selectinload(ErrorTickets.assigned_admin),
            )
        )
        return list(result.scalars().all())

    async def save_status_update(
        self,
        ticket: ErrorTickets,
        history: TicketStatusHistory,
        remark: TicketRemark | None = None,
    ) -> ErrorTickets:
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
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise TicketCreationError from exc

    async def create_remark(self, remark: TicketRemark) -> TicketRemark:
        self.db.add(remark)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise TicketCreationError from exc
        await self.db.refresh(remark, ["ticket", "user"])
        return remark

    async def get_remarks(self, ticket_id: int) -> list[TicketRemark]:
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
        result = await self.db.execute(
            select(TicketStatusHistory)
            .where(TicketStatusHistory.ticket_id == ticket_id)
            .order_by(TicketStatusHistory.changed_at.asc())
        )
        return list(result.scalars().all())
