from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependency.dependencies import (
    get_current_user,
    get_ticket_service,
    require_roles,
)
from app.database.connection import get_db
from app.models.user import UserRole, user
from app.schemas.error_ticketSchema import TicketCreate, TicketResponse
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(get_current_user),
) -> TicketResponse:
    return await ticket_service.create_ticket(db, ticket_data, current_user)


@router.get("/my-tickets", response_model=list[TicketResponse])
async def get_my_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(require_roles(UserRole.EMPLOYEE)),
) -> list[TicketResponse]:
    return await ticket_service.get_my_tickets(current_user)
