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
from app.repositories.implementations import UserRepository
from app.repositories.interfaces import UserInterface
from app.repositories.implementations import CategoryRepository
from app.repositories.implementations import TicketRepository
from app.repositories.interfaces import CategoryInterface
from app.repositories.interfaces import TicketInterface
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.user_service import UserService
from app.services.ticket_service import TicketService
from app.services.remark_service import RemarkService
from app.services.history_service import HistoryService
from app.repositories.implementations.approval_repository import ApprovalRepository
from app.repositories.interfaces.approval_interface import ApprovalInterface
from app.services.approval_service import ApprovalService
from app.services.email_service import EmailService


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserInterface:
    return UserRepository(db)


def get_auth_service(
    user_repository: UserInterface = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


def get_category_repository(
    db: AsyncSession = Depends(get_db),
) -> CategoryInterface:
    return CategoryRepository(db)


def get_category_service(
    category_repository: CategoryInterface = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(category_repository)


def get_email_service() -> EmailService:
    return EmailService()


def get_ticket_repository(
    db: AsyncSession = Depends(get_db),
) -> TicketInterface:
    return TicketRepository(db)


def get_ticket_service(
    ticket_repository: TicketInterface = Depends(get_ticket_repository),
    category_repository: CategoryInterface = Depends(get_category_repository),
    user_repository: UserInterface = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> TicketService:
    return TicketService(
        ticket_repository, category_repository, user_repository, email_service
    )


def get_remark_service(
    ticket_repository: TicketInterface = Depends(get_ticket_repository),
) -> RemarkService:
    return RemarkService(ticket_repository)


def get_history_service(
    ticket_repository: TicketInterface = Depends(get_ticket_repository),
) -> HistoryService:
    return HistoryService(ticket_repository)


def get_approval_repository(
    db: AsyncSession = Depends(get_db),
) -> ApprovalInterface:
    return ApprovalRepository(db)


def get_approval_service(
    approval_repository: ApprovalInterface = Depends(get_approval_repository),
    email_service: EmailService = Depends(get_email_service),
) -> ApprovalService:
    return ApprovalService(approval_repository, email_service)


def get_user_service(
    user_repository: UserInterface = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> UserService:
    return UserService(user_repository, email_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserInterface = Depends(get_user_repository),
) -> user:

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise InvalidTokenAppError
    except InvalidTokenError as exc:
        raise InvalidTokenAppError from exc

    current_user = await user_repository.get_by_email(email)
    if current_user is None:
        raise InvalidTokenAppError

    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable:
    async def role_checker(
        current_user: user = Depends(get_current_user),
    ) -> user:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError
        return current_user

    return role_checker
