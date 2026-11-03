from abc import ABC, abstractmethod

from app.models.ticket_approval import TicketApproval


class ApprovalInterface(ABC):
    @abstractmethod
    async def get_pending_approvals(self, manager_id: int) -> list[TicketApproval]:
        raise NotImplementedError
