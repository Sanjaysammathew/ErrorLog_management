from fastapi import APIRouter, Depends, Query, status

from app.api.dependency.dependencies import get_user_service, require_roles
from app.models.user import UserRole, user
from app.schemas.userSchema import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    return await user_service.register_user(user_data)


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> UserListResponse:
    return await user_service.list_users(page, page_size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    return await user_service.update_user(user_id, user_data)


@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    return await user_service.deactivate_user(user_id)
