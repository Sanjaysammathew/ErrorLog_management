from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket_image import TicketImage
from app.repositories.interfaces.ticket_image_interface import TicketImageInterface


class TicketImageRepository(TicketImageInterface):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_image(self, image: TicketImage) -> TicketImage:
        self.db.add(image)
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        await self.db.refresh(image)
        return image

    async def get_image_by_id(self, image_id: int) -> TicketImage | None:
        result = await self.db.execute(
            select(TicketImage).where(TicketImage.id == image_id)
        )
        return result.scalar_one_or_none()

    async def delete_image(self, image: TicketImage) -> None:
        await self.db.delete(image)
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
