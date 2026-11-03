from abc import ABC, abstractmethod

from app.models.error_ticket import ErrorTickets
from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory
from app.models.ticket_remark import TicketRemark


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

    @abstractmethod
    async def get_ticket_by_id(self, ticket_id: int) -> ErrorTickets | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[ErrorTickets]:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self):
        raise NotImplementedError

    @abstractmethod
    async def save_status_update(
        self,
        ticket: ErrorTickets,
        history: TicketStatusHistory,
        remark: TicketRemark | None = None,
    ) -> ErrorTickets:
        raise NotImplementedError

    @abstractmethod
    async def create_remark(self, remark: TicketRemark) -> TicketRemark:
        raise NotImplementedError

    @abstractmethod
    async def get_remarks(self, ticket_id: int) -> list[TicketRemark]:
        raise NotImplementedError

    @abstractmethod
    async def get_status_history(
        self, ticket_id: int
    ) -> list[TicketStatusHistory]:
        raise NotImplementedError
