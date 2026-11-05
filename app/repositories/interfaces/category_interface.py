from abc import ABC, abstractmethod

from app.models.ErrorCategory import ErrorCategory, IssueType


class CategoryInterface(ABC):
    """Specify the repository operations for category data.

        Concrete repositories implement this contract for application services.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> ErrorCategory | None:
        """Find a category with the specified name.

            This supports category lookup and duplicate-name validation.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_issue_type(self, issue_type: IssueType) -> ErrorCategory | None:
        """Find the category associated with an issue type.

            This supports assigning a ticket to its category.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, category: ErrorCategory) -> ErrorCategory:
        """Save a new record to the database.

            The repository handles persistence errors and returns the stored record.
        """
        raise NotImplementedError

    @abstractmethod
    async def add_pending(self, category: ErrorCategory) -> ErrorCategory:
        """Store a category or ticket that is waiting for review.

            The repository keeps the pending record available to the review workflow.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[ErrorCategory]:
        """Retrieve records from the requested page of a collection.

            The repository applies the supplied pagination limits.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, category_id: int) -> ErrorCategory | None:
        """Find a record by its identifier.

            The repository returns the matching record when it exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, category: ErrorCategory) -> ErrorCategory:
        """Persist changes to an existing record.

            The repository applies the supplied fields to the stored entity.
        """
        raise NotImplementedError
