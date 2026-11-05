from abc import ABC, abstractmethod

from app.models.ticket_approval import TicketApproval
from app.models.ticket_status_history import TicketStatusHistory


class ApprovalInterface(ABC):
    """Specify the repository operations for approval data.

        Concrete repositories implement this contract for application services.
    """
    @abstractmethod
    async def get_pending_approvals(self, manager_id: int) -> list[TicketApproval]:
        """Retrieve approval requests that are waiting for a manager's decision.

            The service or repository returns pending requests for review.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_approval_by_id(self, approval_id: int) -> TicketApproval | None:
        """Find one approval request by its identifier.

            The service checks manager access before returning its details.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_decision(
        self,
        approval: TicketApproval,
        history: TicketStatusHistory,
    ) -> TicketApproval:
        """Persist a manager decision on an approval request.

            The repository saves the approval state and related ticket history.
        """
        raise NotImplementedError
