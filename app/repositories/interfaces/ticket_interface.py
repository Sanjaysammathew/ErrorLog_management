from abc import ABC, abstractmethod

from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.ticket_remark import TicketRemark


class TicketInterface(ABC):
    """Specify the repository operations for ticket data.

        Concrete repositories implement this contract for application services.
    """

    @abstractmethod
    async def create_ticket(self, new_ticket: ErrorTickets) -> ErrorTickets:
        """Create a support ticket and its initial workflow records.

            The operation applies category, approval, and due-date rules.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_status_history(
        self, history: TicketStatusHistory
    ) -> TicketStatusHistory:
        """Record a ticket status change in the database.

            The history entry preserves the ticket workflow timeline.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_approval(self, approval: TicketApproval) -> TicketApproval:
        """Create an approval request for a ticket.

            The repository stores the request for manager review.
        """
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Persist the pending database changes.

            The operation finalizes the current transaction.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_by_id(self, ticket_id: int) -> ErrorTickets | None:
        """Find a support ticket by its identifier.

            The service checks whether the current user may view it.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[ErrorTickets]:
        """Find tickets associated with a specific user account.

            The repository returns matching records from the database.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self):
        """Find the user account needed by the operation.

            The service returns the matching account or reports that it is missing.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_overdue_tickets(self) -> list[ErrorTickets]:
        """Find tickets that remain open past their due time.

            The result supports administrative follow-up on overdue work.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_status_update(
        self,
        ticket: ErrorTickets,
        history: TicketStatusHistory,
        remark: TicketRemark | None = None,
    ) -> ErrorTickets:
        """Persist a ticket status change and its workflow details.

            The repository commits the update to the database.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_remark(self, remark: TicketRemark) -> TicketRemark:
        """Save a remark associated with a ticket.

            The repository preserves the remark and its author relationship.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_remarks(self, ticket_id: int) -> list[TicketRemark]:
        """Retrieve remarks attached to a ticket.

            The service checks ticket access before returning the discussion.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_status_history(self, ticket_id: int) -> list[TicketStatusHistory]:
        """Retrieve the status history entries for a ticket.

            The repository returns the recorded workflow transitions in chronological order.
        """
        raise NotImplementedError
