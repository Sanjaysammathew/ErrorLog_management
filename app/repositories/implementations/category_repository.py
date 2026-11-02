from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import CategoryAlreadyExistsError
from app.models.ErrorCategory import ErrorCategory
from app.repositories.interfaces.category_interface import CategoryInterface


class CategoryRepository(CategoryInterface):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_name(self, name: str) -> ErrorCategory | None:
        result = await self.db.execute(
            select(ErrorCategory).where(ErrorCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, category: ErrorCategory) -> ErrorCategory:
        self.db.add(category)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise CategoryAlreadyExistsError from exc

        await self.db.refresh(category)
        return category

    async def get_all(self) -> list[ErrorCategory]:
        result = await self.db.execute(select(ErrorCategory))
        return result.scalars().all()

    async def get_by_id(self, category_id: int) -> ErrorCategory | None:
        result = await self.db.execute(
            select(ErrorCategory).where(ErrorCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def update(self, category: ErrorCategory) -> ErrorCategory:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
