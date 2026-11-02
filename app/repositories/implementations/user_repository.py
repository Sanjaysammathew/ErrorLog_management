from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import UserAlreadyExistsError
from app.models.user import UserRole, user
from app.repositories.interfaces.user_interface import UserInterface
from sqlalchemy import func, select


class UserRepository(UserInterface):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> user | None:
        result = await self.db.execute(select(user).where(user.email == email))
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, username: str, email: str) -> user | None:
        result = await self.db.execute(
            select(user).where((user.username == username) | (user.email == email))
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole) -> user | None:
        result = await self.db.execute(select(user).where(user.role == role))
        return result.scalars().first()

    async def create(self, new_user: user) -> user:
        self.db.add(new_user)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise UserAlreadyExistsError from exc

        await self.db.refresh(new_user)
        return new_user

    async def get_all(self, offset: int, limit: int) -> list[user]:
        result = await self.db.execute(select(user).offset(offset).limit(limit))
        return result.scalars().all()

    async def count_all(self) -> int:
        result = await self.db.execute(select(func.count(user.id)))
        return result.scalar_one()
