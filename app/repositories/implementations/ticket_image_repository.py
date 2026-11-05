from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket_image import TicketImage
from app.repositories.interfaces.ticket_image_interface import TicketImageInterface


class TicketImageRepository(TicketImageInterface):
    """Provide database access for ticketimage records.

        The repository implements persistence operations used by services.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the ticketimage repository with its database session.

            The session is used for the repository's persistence operations.
        """
        self.db = db

    async def create_image(self, image: TicketImage) -> TicketImage:
        """Create a database record for a stored ticket image.

            The repository links the image metadata to its ticket.
        """
        self.db.add(image)
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        await self.db.refresh(image)
        return image

    async def get_image_by_id(self, image_id: int) -> TicketImage | None:
        """Find an image attachment by its identifier.

            The result is used to retrieve or remove the attachment.
        """
        result = await self.db.execute(
            select(TicketImage).where(TicketImage.id == image_id)
        )
        return result.scalar_one_or_none()

    async def delete_image(self, image: TicketImage) -> None:
        """Delete or remove image from the application.

            Related access and persistence rules are handled by this operation.
        """
        await self.db.delete(image)
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
