from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.models.user import UserRole, user
from app.repositories.interfaces.user_interface import UserInterface


class UserRepository(UserInterface):
    """Provide database access for user records.

        The repository implements persistence operations used by services.
    """
    def __init__(self, db: AsyncSession) -> None:
        """Initialize the user repository with its database session.

            The session is used for the repository's persistence operations.
        """
        self.db = db

    async def get_by_email(self, email: str) -> user | None:
        """Find a user account by its email address.

            The repository returns the matching account when one exists.
        """
        result = await self.db.execute(select(user).where(user.email == email))
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, username: str, email: str) -> user | None:
        """Find an account matching the supplied username or email.

            This supports duplicate-account checks during registration.
        """
        result = await self.db.execute(
            select(user).where((user.username == username) | (user.email == email))
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole) -> user | None:
        """Find a user account with the specified role.

            This supports workflows that need to locate a role holder.
        """
        result = await self.db.execute(select(user).where(user.role == role))
        return result.scalars().first()

    async def create(self, new_user: user) -> user:
        """Save a new record to the database.

            The repository handles persistence errors and returns the stored record.
        """
        self.db.add(new_user)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise UserAlreadyExistsError from exc

        await self.db.refresh(new_user)
        return new_user

    async def get_all(self, offset: int, limit: int) -> list[user]:
        """Retrieve records from the requested page of a collection.

            The repository applies the supplied pagination limits.
        """
        result = await self.db.execute(select(user).offset(offset).limit(limit))
        return result.scalars().all()

    async def count_all(self) -> int:
        """Count the number of all records.

            The count supports application queries and pagination.
        """
        result = await self.db.execute(select(func.count(user.id)))
        return result.scalar_one()

    async def update(self, user_id: int, changes: dict) -> user:
        """Persist changes to an existing record.

            The repository applies the supplied fields to the stored entity.
        """
        result = await self.db.execute(select(user).where(user.id == user_id))
        existing_user = result.scalar_one_or_none()
        if existing_user is None:
            raise UserNotFoundError

        for key, value in changes.items():
            setattr(existing_user, key, value)

        await self.db.commit()
        await self.db.refresh(existing_user)
        return existing_user

    async def get_by_id(self, user_id: int) -> user | None:
        """Find a record by its identifier.

            The repository returns the matching record when it exists.
        """
        result = await self.db.execute(select(user).where(user.id == user_id))
        return result.scalar_one_or_none()
