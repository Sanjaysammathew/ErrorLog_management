from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import CategoryAlreadyExistsError
from app.models.ErrorCategory import ErrorCategory, IssueType
from app.repositories.interfaces.category_interface import CategoryInterface


class CategoryRepository(CategoryInterface):
    """Provide database access for category records.

        The repository implements persistence operations used by services.
    """
    def __init__(self, db: AsyncSession) -> None:
        """Initialize the category repository with its database session.

            The session is used for the repository's persistence operations.
        """
        self.db = db

    async def get_by_name(self, name: str) -> ErrorCategory | None:
        """Find a category with the specified name.

            This supports category lookup and duplicate-name validation.
        """
        result = await self.db.execute(
            select(ErrorCategory).where(ErrorCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_issue_type(
        self, issue_type: IssueType
    ) -> ErrorCategory | None:
        """Find the category associated with an issue type.

            This supports assigning a ticket to its category.
        """
        result = await self.db.execute(
            select(ErrorCategory).where(
                ErrorCategory.issue_type == issue_type,
                ErrorCategory.is_active.is_(True),
            ).order_by(ErrorCategory.id)
        )
        return result.scalars().first()

    async def get_by_issue_type_any_status(
        self, issue_type: IssueType
    ) -> ErrorCategory | None:
        """Find the category associated with an issue type, including inactive records."""
        result = await self.db.execute(
            select(ErrorCategory)
            .where(ErrorCategory.issue_type == issue_type)
            .order_by(ErrorCategory.id)
        )
        return result.scalars().first()

    async def create(self, category: ErrorCategory) -> ErrorCategory:
        """Save a new record to the database.

            The repository handles persistence errors and returns the stored record.
        """
        self.db.add(category)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise CategoryAlreadyExistsError from exc

        await self.db.refresh(category)
        return category

    async def add_pending(self, category: ErrorCategory) -> ErrorCategory:
        """Store a category or ticket that is waiting for review.

            The repository keeps the pending record available to the review workflow.
        """
        self.db.add(category)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise CategoryAlreadyExistsError from exc
        return category

    async def get_all(self) -> list[ErrorCategory]:
        """Retrieve records from the requested page of a collection.

            The repository applies the supplied pagination limits.
        """
        result = await self.db.execute(select(ErrorCategory))
        return result.scalars().all()

    async def get_by_id(self, category_id: int) -> ErrorCategory | None:
        """Find a record by its identifier.

            The repository returns the matching record when it exists.
        """
        result = await self.db.execute(
            select(ErrorCategory).where(ErrorCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def update(self, category: ErrorCategory) -> ErrorCategory:
        """Persist changes to an existing record.

            The repository applies the supplied fields to the stored entity.
        """
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
