from abc import ABC, abstractmethod

from app.models.user import UserRole, user


class UserInterface(ABC):
    """Specify the repository operations for user data.

        Concrete repositories implement this contract for application services.
    """
    @abstractmethod
    async def get_by_email(self, email: str) -> user | None:
        """Find a user account by its email address.

            The repository returns the matching account when one exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_username_or_email(self, username: str, email: str) -> user | None:
        """Find an account matching the supplied username or email.

            This supports duplicate-account checks during registration.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_role(self, role: UserRole) -> user | None:
        """Find a user account with the specified role.

            This supports workflows that need to locate a role holder.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, new_user: user) -> user:
        """Save a new record to the database.

            The repository handles persistence errors and returns the stored record.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, offset: int, limit: int) -> list[user]:
        """Retrieve records from the requested page of a collection.

            The repository applies the supplied pagination limits.
        """
        raise NotImplementedError

    @abstractmethod
    async def count_all(self) -> int:
        """Count the number of all records.

            The count supports application queries and pagination.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> user | None:
        """Find a record by its identifier.

            The repository returns the matching record when it exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, user_id: int, changes: dict) -> user:
        """Persist changes to an existing record.

            The repository applies the supplied fields to the stored entity.
        """
        raise NotImplementedError
