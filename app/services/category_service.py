from app.exceptions.custom_exceptions import (
    CategoryAlreadyExistsError,
    UserNotFoundError,
)
from app.models.ErrorCategory import ErrorCategory
from app.repositories.interfaces.category_interface import CategoryInterface
from app.schemas.error_categorySchema import CategoryCreate, CategoryUpdate


class CategoryService:
    """Apply business rules for category operations.

        The service coordinates validation and the required data access.
    """
    def __init__(self, category_repository: CategoryInterface) -> None:
        """Initialize the category service with its collaborators.

            These dependencies provide the business logic with data access and related services.
        """
        self.category_repository = category_repository

    async def create_category(self, category_data: CategoryCreate) -> ErrorCategory:
        """Create and persist a ticket category.

            The service checks category rules before saving the new record.
        """
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
        """Retrieve the available ticket categories.

            The list supports category selection and ticket classification.
        """
        return await self.category_repository.get_all()

    async def get_category_by_id(self, category_id: int) -> ErrorCategory | None:
        """Find a ticket category by its identifier.

            The service returns the category or raises a not-found error.
        """
        return await self.category_repository.get_by_id(category_id)

    async def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> ErrorCategory:
        """Update the editable fields of an existing category.

            The service validates the changes and saves the updated category.
        """
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise UserNotFoundError

        changes = category_data.model_dump(exclude_unset=True)
        if "name" in changes:
            existing_category = await self.category_repository.get_by_name(
                changes["name"]
            )
            if existing_category is not None and existing_category.id != category_id:
                raise CategoryAlreadyExistsError

        for field, value in changes.items():
            setattr(category, field, value)
        return await self.category_repository.update(category)

    async def deactivate_category(self, category_id: int) -> ErrorCategory:
        """Deactivate category while preserving its stored record.

            This prevents it from being treated as active by the application.
        """
        category = await self.get_category_by_id(category_id)
        if category is None:
            raise UserNotFoundError

        category.is_active = False
        return await self.category_repository.update(category)
