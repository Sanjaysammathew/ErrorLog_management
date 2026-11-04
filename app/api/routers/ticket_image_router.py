from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependency.dependencies import (
    get_current_user,
    get_ticket_image_service,
)
from app.models.user import user
from app.schemas.ticket_image import TicketImageResponse
from app.services.ticket_image_service import TicketImageService

router = APIRouter(prefix="/tickets", tags=["ticket images"])


@router.post(
    "/{ticket_id}/images",
    response_model=TicketImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_ticket_image(
    ticket_id: int,
    file: UploadFile = File(...),
    image_service: TicketImageService = Depends(get_ticket_image_service),
    current_user: user = Depends(get_current_user),
) -> TicketImageResponse:
    return await image_service.upload_image(ticket_id, file, current_user)


@router.delete(
    "/{ticket_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ticket_image(
    ticket_id: int,
    image_id: int,
    image_service: TicketImageService = Depends(get_ticket_image_service),
    current_user: user = Depends(get_current_user),
) -> None:
    await image_service.delete_image(ticket_id, image_id, current_user)
