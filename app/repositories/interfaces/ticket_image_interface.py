from abc import ABC, abstractmethod

from app.models.ticket_image import TicketImage


class TicketImageInterface(ABC):
    @abstractmethod
    async def create_image(self, image: TicketImage) -> TicketImage:
        raise NotImplementedError

    @abstractmethod
    async def get_image_by_id(self, image_id: int) -> TicketImage | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_image(self, image: TicketImage) -> None:
        raise NotImplementedError
