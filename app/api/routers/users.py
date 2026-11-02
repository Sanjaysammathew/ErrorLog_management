from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.api.dependency.dependencies import (
    get_auth_service,
    get_current_user,
    require_roles,
)
from app.models.user import UserRole, user
from app.schemas.authSchema import Token
from app.schemas.userSchema import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.schemas.userSchema import UserListResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    role_checker: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    return await auth_service.register_user(user_data)


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    auth_service: AuthService = Depends(get_auth_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> UserListResponse:
    return await auth_service.list_users(page, page_size)
