from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import (
    AppError,
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    ManagerNotFoundError,
    PermissionDeniedError,
    TicketCreationError,
)
from app.models.error_ticket import ErrorTickets
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import ApprovalStatus, UserRole, user
from app.repositories.interfaces.category_interface import CategoryInterface
from app.repositories.interfaces.ticket_interface import TicketInterface
from app.repositories.interfaces.user_interface import UserInterface
from app.schemas.error_ticketSchema import TicketCreate, TicketStatus
from app.scripts.ticket_number import generate_ticket_number


class TicketService:
    APPROVAL_KEYWORDS = ("paid software", "hardware replacement")
    SLA_KEYWORDS = (
        ("hardware replacement", 24),
        ("paid software", 8),
        ("network", 2),
        ("keyboard", 8),
    )

    @classmethod
    def _requires_approval(cls, ticket_data: TicketCreate) -> bool:
        searchable_text = " ".join(
            value for value in (ticket_data.title, ticket_data.description) if value
        ).casefold()
        return any(keyword in searchable_text for keyword in cls.APPROVAL_KEYWORDS)

    @classmethod
    def _get_sla_hours(cls, ticket_data: TicketCreate, fallback: int) -> int:
        searchable_text = " ".join(
            value for value in (ticket_data.title, ticket_data.description) if value
        ).casefold()
        for keyword, hours in cls.SLA_KEYWORDS:
            if keyword in searchable_text:
                return hours
        return fallback

    def __init__(
        self,
        ticket_repository: TicketInterface,
        category_repository: CategoryInterface,
        user_repository: UserInterface,
    ) -> None:
        self.ticket_repository = ticket_repository
        self.category_repository = category_repository
        self.user_repository = user_repository

    async def create_ticket(
        self, db: AsyncSession, ticket_data: TicketCreate, current_user: user
    ) -> ErrorTickets:
        if not current_user.is_active or current_user.role != UserRole.EMPLOYEE:
            raise PermissionDeniedError

        category = await self.category_repository.get_by_issue_type(
            ticket_data.issue_type
        )
        if category is None:
            category = ErrorCategory(
                name=f"{ticket_data.issue_type.value.title()} Issues",
                issue_type=ticket_data.issue_type,
            )
            try:
                await self.category_repository.add_pending(category)
            except CategoryAlreadyExistsError:
                await db.rollback()
                category = await self.category_repository.get_by_issue_type(
                    ticket_data.issue_type
                )
                if category is None:
                    raise CategoryNotFoundError
        if category is None or not category.is_active:
            raise CategoryNotFoundError

        # Database DateTime columns are timezone-naive; store UTC consistently.
        created_at = datetime.now(timezone.utc).replace(tzinfo=None)
        sla_hours = self._get_sla_hours(ticket_data, category.default_sla_hours)
        due_at = created_at + timedelta(hours=sla_hours)
        requires_approval = self._requires_approval(ticket_data)
        initial_status = (
            TicketStatus.PENDING_APPROVAL.value
            if requires_approval
            else TicketStatus.OPEN.value
        )

        manager = None
        if requires_approval:
            if current_user.manager_id is None:
                await db.rollback()
                raise ManagerNotFoundError
            manager = await self.user_repository.get_by_id(current_user.manager_id)
            if (
                manager is None
                or not manager.is_active
                or manager.role != UserRole.MANAGER
            ):
                await db.rollback()
                raise ManagerNotFoundError

        try:
            ticket = ErrorTickets(
                title=ticket_data.title,
                description=ticket_data.description,
                priority=ticket_data.priority.value,
                category_id=category.id,
                user_id=current_user.id,
                status=initial_status,
                requires_approval=requires_approval,
                due_at=due_at,
                created_at=created_at,
                updated_at=created_at,
            )
            await self.ticket_repository.create_ticket(ticket)
            ticket.ticket_number = generate_ticket_number(ticket.id, created_at)
            await self.ticket_repository.create_status_history(
                TicketStatusHistory(
                    ticket_id=ticket.id,
                    changed_by_id=current_user.id,
                    old_status=None,
                    new_status=initial_status,
                    remarks="Ticket created",
                    changed_at=created_at,
                )
            )

            if manager is not None:
                await self.ticket_repository.create_approval(
                    TicketApproval(
                        ticket_id=ticket.id,
                        manager_id=manager.id,
                        status=ApprovalStatus.PENDING,
                    )
                )

            await self.ticket_repository.commit()
            await db.refresh(ticket, ["category", "created_by_user"])
            return ticket
        except AppError:
            await db.rollback()
            raise
        except SQLAlchemyError as exc:
            await db.rollback()
            raise TicketCreationError from exc

    async def get_my_tickets(self, current_user: user) -> list[ErrorTickets]:
        if not current_user.is_active or current_user.role != UserRole.EMPLOYEE:
            raise PermissionDeniedError

        return await self.ticket_repository.get_by_user_id(current_user.id)
