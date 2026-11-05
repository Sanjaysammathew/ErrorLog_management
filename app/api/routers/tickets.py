from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependency.dependencies import (
    get_current_user,
    get_ticket_service,
    require_roles,
)
from app.database.connection import get_db
from app.models.user import UserRole, user
from app.schemas.error_ticketSchema import (
    TicketCreate,
    TicketResponse,
    TicketUpdateStatus,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(get_current_user),
) -> TicketResponse:
    """Submit a new support ticket for the authenticated user.

        The request body provides the issue details, and the current user becomes
        the ticket owner. Return the created ticket with its generated identifiers.
    """
    return await ticket_service.create_ticket(db, ticket_data, current_user)


@router.get("/my-tickets", response_model=list[TicketResponse])
async def get_my_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(require_roles(UserRole.EMPLOYEE)),
) -> list[TicketResponse]:
    """List the support tickets created by the authenticated employee.

        The endpoint is limited to employee accounts and returns only tickets owned
        by the current user.
    """
    return await ticket_service.get_my_tickets(current_user)


@router.get("/all-tickets", response_model=list[TicketResponse])
async def get_all_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(require_roles(UserRole.ADMIN)),
) -> list[TicketResponse]:
    """Retrieve the complete support ticket list for administration.

        Only administrators can access this endpoint. Return tickets across users
        so administrators can review and manage the overall queue.
    """
    return await ticket_service.get_all_tickets()


@router.get("/overdue", response_model=list[TicketResponse])
async def get_overdue_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(require_roles(UserRole.ADMIN)),
) -> list[TicketResponse]:
    """Retrieve tickets that have passed their due date and remain overdue.

        Only administrators can access this endpoint. Return the overdue tickets
        so they can be prioritized for follow-up.
    """
    return await ticket_service.get_overdue_tickets(current_user)


@router.patch("/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(require_roles(UserRole.ADMIN)),
) -> TicketResponse:
    """Close the support ticket identified by `ticket_id`.

        Only administrators can close tickets. The service records the closure and
        returns the ticket with its updated status.
    """
    return await ticket_service.close_ticket(ticket_id, current_user)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: int,
    update_data: TicketUpdateStatus,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(require_roles(UserRole.ADMIN)),
) -> TicketResponse:
    """Change a ticket's workflow status using `pending_approval`, `open`,
        `in_progress`, `resolved`, or `rejected`, and optionally record a remark.

        Only administrators can use this endpoint. Use the separate close endpoint
        to close a ticket after it has been resolved.
    """
    return await ticket_service.update_ticket_status(
        ticket_id,
        update_data.status,
        update_data.status_change_remark,
        current_user,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket_by_id(
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: user = Depends(get_current_user),
) -> TicketResponse:
    """Retrieve the details of a support ticket using its ID.

        The caller must be authenticated, and the service checks whether they may
        view that ticket. Return the ticket details when access is allowed.
    """
    return await ticket_service.get_ticket_by_id(ticket_id, current_user)
