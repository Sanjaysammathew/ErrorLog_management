from fastapi import APIRouter, Depends, status

from app.api.dependency.dependencies import get_category_service, require_roles
from app.models.user import UserRole, user
from app.schemas.error_categorySchema import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> CategoryResponse:
    return await category_service.create_category(category_data)


@router.get("", response_model=list[CategoryResponse])
async def get_all_categories(
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(
        require_roles(UserRole.ADMIN, UserRole.EMPLOYEE, UserRole.MANAGER)
    ),
) -> list[CategoryResponse]:
    return await category_service.get_all_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(
        require_roles(UserRole.ADMIN, UserRole.EMPLOYEE, UserRole.MANAGER)
    ),
) -> CategoryResponse:
    category = await category_service.get_category_by_id(category_id)
    if category is None:
        raise ValueError(f"Category with ID {category_id} not found.")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> CategoryResponse:
    return await category_service.update_category(category_id, category_data)


@router.patch("/{category_id}/deactivate", response_model=CategoryResponse)
async def deactivate_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> CategoryResponse:
    return await category_service.deactivate_category(category_id)
