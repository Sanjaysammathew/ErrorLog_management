from abc import ABC, abstractmethod

from app.models.ticket_image import TicketImage


class TicketImageInterface(ABC):
    """Specify the repository operations for ticketimage data.

        Concrete repositories implement this contract for application services.
    """

    @abstractmethod
    async def create_image(self, image: TicketImage) -> TicketImage:
        """Create a database record for a stored ticket image.

            The repository links the image metadata to its ticket.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_image_by_id(self, image_id: int) -> TicketImage | None:
        """Find an image attachment by its identifier.

            The result is used to retrieve or remove the attachment.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_image(self, image: TicketImage) -> None:
        """Delete or remove image from the application.

            Related access and persistence rules are handled by this operation.
        """
        raise NotImplementedError
