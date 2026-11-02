from fastapi import APIRouter, Depends, status

from app.api.dependency.dependencies import get_category_service, require_roles
from app.models.user import UserRole, user
from app.schemas.error_categorySchema import CategoryCreate, CategoryResponse
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
