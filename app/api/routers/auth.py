from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependency.dependencies import get_auth_service, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.exceptions.custom_exceptions import InvalidTokenError
from app.models.user import user
from app.schemas.authSchema import RefreshTokenRequest, Token
from app.schemas.userSchema import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    current_user = await auth_service.authenticate_user(
        form_data.username, form_data.password
    )
    return Token(
        access_token=create_access_token(current_user.email, current_user.role.value),
        refresh_token=create_refresh_token(
            current_user.email, current_user.role.value
        ),
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    try:
        payload = decode_refresh_token(token_data.refresh_token)
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise InvalidTokenError
        current_user = await auth_service.user_repository.get_by_email(email)
        if current_user is None or not current_user.is_active:
            raise InvalidTokenError
    except ValueError as exc:
        raise InvalidTokenError from exc

    return Token(
        access_token=create_access_token(current_user.email, current_user.role.value),
        refresh_token=create_refresh_token(
            current_user.email, current_user.role.value
        ),
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: user = Depends(get_current_user),
) -> user:
    return current_user
