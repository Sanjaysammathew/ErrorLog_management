from abc import ABC, abstractmethod

from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory


class TicketInterface(ABC):
    @abstractmethod
    async def create_ticket(self, new_ticket: ErrorTickets) -> ErrorTickets:
        raise NotImplementedError

    @abstractmethod
    async def create_status_history(
        self, history: TicketStatusHistory
    ) -> TicketStatusHistory:
        raise NotImplementedError

    @abstractmethod
    async def create_approval(self, approval: TicketApproval) -> TicketApproval:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
