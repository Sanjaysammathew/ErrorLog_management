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
    """
    Create a ticket category from the details supplied in the request body.
    Only administrators can access this endpoint; it returns the saved category
    with its generated ID and current active state.
    """
    return await category_service.create_category(category_data)


@router.get("", response_model=list[CategoryResponse])
async def get_all_categories(
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(
        require_roles(UserRole.ADMIN, UserRole.EMPLOYEE, UserRole.MANAGER)
    ),
) -> list[CategoryResponse]:
    """
    Retrieve all ticket categories available for classification and management.
    Administrators, employees, and managers can access this endpoint; it returns
    the category records as a list.
    """
    return await category_service.get_all_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(
        require_roles(UserRole.ADMIN, UserRole.EMPLOYEE, UserRole.MANAGER)
    ),
) -> CategoryResponse:
    """
    Retrieve one ticket category by its identifier.
    Administrators, employees, and managers can access it; the endpoint returns
    the category details or an error when the category does not exist.
    """
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
    """
    Update the editable details of an existing ticket category.
    Only administrators can access this endpoint; it returns the category with
    the updated values after the change is saved.
    """
    return await category_service.update_category(category_id, category_data)


@router.patch("/{category_id}/deactivate", response_model=CategoryResponse)
async def deactivate_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    _: user = Depends(require_roles(UserRole.ADMIN)),
) -> CategoryResponse:
    """
    Deactivate a ticket category so it cannot be selected for new tickets.
    Only administrators can access this endpoint; it returns the category with
    its updated inactive state while preserving existing ticket references.
    """
    return await category_service.deactivate_category(category_id)
