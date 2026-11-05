from fastapi import APIRouter, Depends

from app.api.dependency.dependencies import get_current_user, get_history_service
from app.models.user import user
from app.schemas.ticket_status_historySchema import StatusHistoryResponse
from app.services.history_service import HistoryService

router = APIRouter(prefix="/tickets", tags=["history"])


@router.get("/{ticket_id}/history", response_model=list[StatusHistoryResponse])
async def get_history(
    ticket_id: int,
    service: HistoryService = Depends(get_history_service),
    current_user: user = Depends(get_current_user),
) -> list[StatusHistoryResponse]:
    """Retrieve the chronological status changes recorded for a ticket.

        The authenticated user's access to the ticket is checked by the service.
        Return each recorded status change as a history entry.
    """
    return await service.get_history(ticket_id, current_user)
