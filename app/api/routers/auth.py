from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependency.dependencies import get_auth_service, get_current_user
from app.core.security import create_access_token
from app.models.user import user
from app.schemas.authSchema import Token
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
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: user = Depends(get_current_user),
) -> user:
    return current_user
