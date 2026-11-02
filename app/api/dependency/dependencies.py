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
from app.services.auth_service import AuthService


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserInterface:
    return UserRepository(db)


def get_auth_service(
    user_repository: UserInterface = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


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
