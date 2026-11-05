from app.exceptions.custom_exceptions import PermissionDeniedError, TicketNotFoundError
from app.models.ticket_remark import TicketRemark
from app.models.user import UserRole, user
from app.repositories.interfaces.ticket_interface import TicketInterface
from app.schemas.ticket_remarkSchema import RemarkCreate


class RemarkService:
    """Apply business rules for remark operations.

        The service coordinates validation and the required data access.
    """
    def __init__(self, ticket_repository: TicketInterface) -> None:
        """Initialize the remark service with its collaborators.

            These dependencies provide the business logic with data access and related services.
        """
        self.ticket_repository = ticket_repository

    async def add_remark(
        self, ticket_id: int, data: RemarkCreate, current_user: user
    ) -> TicketRemark:
        """Add a remark to a support ticket.

            The service checks access and records the authenticated user as its author.
        """
        if not current_user.is_active or current_user.role != UserRole.ADMIN:
            raise PermissionDeniedError
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError
        return await self.ticket_repository.create_remark(
            TicketRemark(
                ticket_id=ticket_id,
                user_id=current_user.id,
                remark=data.remark,
            )
        )

    async def get_remarks(
        self, ticket_id: int, current_user: user
    ) -> list[TicketRemark]:
        """Retrieve remarks attached to a ticket.

            The service checks ticket access before returning the discussion.
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError
        if not current_user.is_active or (
            current_user.role == UserRole.EMPLOYEE
            and ticket.user_id != current_user.id
        ):
            raise PermissionDeniedError
        remarks = await self.ticket_repository.get_remarks(ticket_id)
        return remarks
