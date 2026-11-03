from abc import ABC, abstractmethod

from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory


class ApprovalInterface(ABC):
    @abstractmethod
    async def get_pending_approvals(self, manager_id: int) -> list[TicketApproval]:
        raise NotImplementedError

    @abstractmethod
    async def get_approval_by_id(self, approval_id: int) -> TicketApproval | None:
        raise NotImplementedError

    @abstractmethod
    async def save_decision(
        self,
        approval: TicketApproval,
        history: TicketStatusHistory,
    ) -> TicketApproval:
        raise NotImplementedError
