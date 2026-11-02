from app.exceptions.custom_exceptions import CategoryAlreadyExistsError
from app.models.ErrorCategory import ErrorCategory
from app.repositories.interfaces.category_interface import CategoryInterface
from app.schemas.error_categorySchema import CategoryCreate


class CategoryService:
    def __init__(self, category_repository: CategoryInterface) -> None:
        self.category_repository = category_repository

    async def create_category(self, category_data: CategoryCreate) -> ErrorCategory:
        existing_category = await self.category_repository.get_by_name(
            category_data.name
        )
        if existing_category is not None:
            raise CategoryAlreadyExistsError

        category = ErrorCategory(
            name=category_data.name,
            issue_type=category_data.issue_type,
            description=category_data.description,
            default_sla_hours=category_data.default_sla_hours,
            requires_approval_default=category_data.requires_approval_default,
            is_active=True,
        )
        return await self.category_repository.create(category)

    async def get_all_categories(self) -> list[ErrorCategory]:
        return await self.category_repository.get_all()
