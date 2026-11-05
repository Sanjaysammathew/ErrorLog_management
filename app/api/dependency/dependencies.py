from collections.abc import Callable

import jwt
from fastapi import Depends
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import oauth2_scheme
from app.database.connection import get_db
from app.exceptions.custom_exceptions import InvalidTokenError as InvalidTokenAppError
from app.exceptions.custom_exceptions import PermissionDeniedError
from app.models.user import UserRole, user
from app.repositories.implementations import (
    CategoryRepository,
    TicketImageRepository,
    TicketRepository,
    UserRepository,
)
from app.repositories.implementations.approval_repository import ApprovalRepository
from app.repositories.interfaces import (
    CategoryInterface,
    TicketInterface,
    UserInterface,
)
from app.repositories.interfaces.approval_interface import ApprovalInterface
from app.repositories.interfaces.ticket_image_interface import TicketImageInterface
from app.services.approval_service import ApprovalService
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.email_service import EmailService
from app.services.history_service import HistoryService
from app.services.remark_service import RemarkService
from app.services.ticket_image_service import TicketImageService
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserInterface:
    """Provide a user repository backed by the request's database session.

        FastAPI injects this dependency wherever a route needs user data access.
    """
    return UserRepository(db)


def get_auth_service(
    user_repository: UserInterface = Depends(get_user_repository),
) -> AuthService:
    """Provide the authentication service with its user repository.

        FastAPI injects the service into routes that handle sign-in and token refresh.
    """
    return AuthService(user_repository)


def get_category_repository(
    db: AsyncSession = Depends(get_db),
) -> CategoryInterface:
    """Provide a category repository backed by the request's database session.

        FastAPI injects this dependency into category operations.
    """
    return CategoryRepository(db)


def get_category_service(
    category_repository: CategoryInterface = Depends(get_category_repository),
) -> CategoryService:
    """Provide the category service with its repository.

        FastAPI injects the service into routes that create or browse categories.
    """
    return CategoryService(category_repository)


def get_email_service() -> EmailService:
    """Provide the email service used to send application notifications.

        FastAPI injects it into routes that send account or ticket notifications.
    """
    return EmailService()


def get_ticket_repository(
    db: AsyncSession = Depends(get_db),
) -> TicketInterface:
    """Provide a ticket repository backed by the request's database session.

        FastAPI injects this dependency into ticket-related services.
    """
    return TicketRepository(db)


def get_ticket_service(
    ticket_repository: TicketInterface = Depends(get_ticket_repository),
    category_repository: CategoryInterface = Depends(get_category_repository),
    user_repository: UserInterface = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> TicketService:
    """Provide the ticket service with its repository and supporting services.

        FastAPI injects it into routes that create and manage tickets.
    """
    return TicketService(
        ticket_repository, category_repository, user_repository, email_service
    )


def get_ticket_image_repository(
    db: AsyncSession = Depends(get_db),
) -> TicketImageInterface:
    """Provide an image repository backed by the request's database session.

        FastAPI injects it into image attachment operations.
    """
    return TicketImageRepository(db)


def get_ticket_image_service(
    image_repository: TicketImageInterface = Depends(get_ticket_image_repository),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketImageService:
    """Provide the image service with its repository and file handling dependencies.

        FastAPI injects it into routes that upload or delete ticket images.
    """
    return TicketImageService(image_repository, ticket_service)


def get_remark_service(
    ticket_repository: TicketInterface = Depends(get_ticket_repository),
) -> RemarkService:
    """Provide the remark service with ticket data access.

        FastAPI injects it into routes that add or retrieve ticket remarks.
    """
    return RemarkService(ticket_repository)


def get_history_service(
    ticket_repository: TicketInterface = Depends(get_ticket_repository),
) -> HistoryService:
    """Provide the history service with ticket data access.

        FastAPI injects it into routes that retrieve status history.
    """
    return HistoryService(ticket_repository)


def get_approval_repository(
    db: AsyncSession = Depends(get_db),
) -> ApprovalInterface:
    """Provide an approval repository backed by the request's database session.

        FastAPI injects this dependency into approval operations.
    """
    return ApprovalRepository(db)


def get_approval_service(
    approval_repository: ApprovalInterface = Depends(get_approval_repository),
    email_service: EmailService = Depends(get_email_service),
) -> ApprovalService:
    """Provide the approval service with its repository and supporting dependencies.

        FastAPI injects it into routes that review and decide approvals.
    """
    return ApprovalService(approval_repository, email_service)


def get_user_service(
    user_repository: UserInterface = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> UserService:
    """Provide the user service with its repository and notification dependencies.

        FastAPI injects it into routes that manage user accounts.
    """
    return UserService(user_repository, email_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserInterface = Depends(get_user_repository),
) -> user:

    """Resolve the user authenticated by the request's access token.

        Invalid or missing credentials prevent access to protected routes.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise InvalidTokenAppError
        if payload.get("type") not in (None, "access"):
            raise InvalidTokenAppError
    except InvalidTokenError as exc:
        raise InvalidTokenAppError from exc

    current_user = await user_repository.get_by_email(email)
    if current_user is None or not current_user.is_active:
        raise InvalidTokenAppError

    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable:
    """Create an access dependency that permits only specified user roles.

        Routes use it to enforce role-based authorization.
    """
    async def role_checker(
        current_user: user = Depends(get_current_user),
    ) -> user:
        """Check that the current user has one of the required roles.

            Requests from users without an allowed role are rejected.
        """
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError
        return current_user

    return role_checker
