from fastapi import APIRouter, Depends, HTTPException, Query, status

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
    """Create a user account from the submitted account details.

        Only administrators can register users through this endpoint. Return the
        created user's profile, including the ID assigned to the new account.
    """
    return await user_service.register_user(user_data)


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> UserListResponse:
    """Retrieve a page of user accounts for account administration.

        Only administrators can access this endpoint. Use `page` and `page_size` to
        control the result window; the response includes the users and paging data.
    """
    return await user_service.list_users(page, page_size)


@router.get("/lookup", response_model=UserResponse)
async def get_user(
    user_id: int | None = Query(
        default=None,
        description=" user ID used to identify the account.",
    ),
    email: str | None = Query(
        default=None,
        description=" email address used to identify the account.",
    ),
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    """Retrieve one user profile by either user ID or email address.

        Only administrators can access this endpoint; provide at least one query
        parameter and receive the matching user's account details.
    """
    if user_id is None and email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either user_id or email.",
        )
    return await user_service.get_user(user_id, email)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    """Retrieve one user profile by account ID.

        Only administrators can access this endpoint. Return the user's account
        details, or an error if no account exists for the supplied ID.
    """
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    """Replace the editable details of an existing user account.

        Only administrators can perform this operation. The request supplies the
        updated user data, and the response contains the saved profile.
    """
    return await user_service.update_user(user_id, user_data)


@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    """Update the editable details of an existing user account.

        Only administrators can perform this operation. Submit the user data to be
        applied and receive the resulting profile in the response.
    """
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> user:
    """Deactivate a user account without removing its historical records.

        Only administrators can perform this operation. Return the user's profile
        with the account's updated inactive state.
    """
    return await user_service.deactivate_user(user_id)
