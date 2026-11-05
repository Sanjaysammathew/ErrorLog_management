from app.exceptions.custom_exceptions import PermissionDeniedError, TicketNotFoundError
from app.models.ticket_status_history import TicketStatusHistory
from app.models.user import UserRole, user
from app.repositories.interfaces.ticket_interface import TicketInterface


class HistoryService:
    """Apply business rules for history operations.

        The service coordinates validation and the required data access.
    """
    def __init__(self, ticket_repository: TicketInterface) -> None:
        """Initialize the history service with its collaborators.

            These dependencies provide data access and related business services.
        """
        self.ticket_repository = ticket_repository

    async def get_history(
        self, ticket_id: int, current_user: user
    ) -> list[TicketStatusHistory]:
        """Retrieve the recorded status changes for a ticket.

            The service applies the current user's ticket access rules.
        """
        ticket = await self.ticket_repository.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError
        if not current_user.is_active or (
            current_user.role == UserRole.EMPLOYEE
            and ticket.user_id != current_user.id
        ):
            raise PermissionDeniedError
        if current_user.role not in (UserRole.EMPLOYEE, UserRole.ADMIN):
            raise PermissionDeniedError
        return await self.ticket_repository.get_status_history(ticket_id)
