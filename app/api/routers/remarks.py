from fastapi import APIRouter, Depends, status

from app.api.dependency.dependencies import get_current_user, get_remark_service
from app.models.user import user
from app.schemas.ticket_remarkSchema import RemarkCreate, RemarkResponse
from app.services.remark_service import RemarkService

router = APIRouter(prefix="/tickets", tags=["remarks"])


@router.post(
    "/{ticket_id}/remarks",
    response_model=RemarkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_remark(
    ticket_id: int,
    data: RemarkCreate,
    service: RemarkService = Depends(get_remark_service),
    current_user: user = Depends(get_current_user),
) -> RemarkResponse:
    """Add a comment or update to the specified ticket.

        The authenticated user's access to the ticket is checked before saving.
        Return the new remark, including its author and creation details.
    """
    return await service.add_remark(ticket_id, data, current_user)


@router.get("/{ticket_id}/remarks", response_model=list[RemarkResponse])
async def get_remarks(
    ticket_id: int,
    service: RemarkService = Depends(get_remark_service),
    current_user: user = Depends(get_current_user),
) -> list[RemarkResponse]:
    """Retrieve the discussion remarks attached to a ticket.

        The authenticated user's access to the ticket is checked by the service.
        Return the remarks as a list, including their authors and timestamps.
    """
    return await service.get_remarks(ticket_id, current_user)
