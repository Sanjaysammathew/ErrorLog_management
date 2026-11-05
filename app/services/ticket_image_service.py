from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.custom_exceptions import (
    ImageCreationError,
    ImageDeletionError,
    ImageNotFoundError,
    PermissionDeniedError,
    TicketImageUploadNotAllowedError,
)
from app.models.ticket_image import TicketImage
from app.models.user import UserRole, user
from app.repositories.interfaces.ticket_image_interface import TicketImageInterface
from app.schemas.error_ticketSchema import TicketStatus
from app.scripts.file_handler import delete_image, save_image, validate_image
from app.services.ticket_service import TicketService


class TicketImageService:
    """Apply business rules for ticketimage operations.

        The service coordinates validation and the required data access.
    """
    def __init__(
        self,
        image_repository: TicketImageInterface,
        ticket_service: TicketService,
    ) -> None:
        """Initialize the ticketimage service with its collaborators.

            These dependencies provide data access and related business services.
        """
        self.image_repository = image_repository
        self.ticket_service = ticket_service

    async def upload_image(
        self, ticket_id: int, upload_file: UploadFile, current_user: user
    ) -> TicketImage:
        """Store an uploaded image and associate it with an eligible ticket.

            Resolved, rejected, and closed tickets do not accept new images. The
            service validates the file and records its metadata for other statuses.
        """
        ticket = await self.ticket_service.get_ticket_by_id(ticket_id, current_user)
        if ticket.status in {
            TicketStatus.RESOLVED.value,
            TicketStatus.REJECTED.value,
            TicketStatus.CLOSED.value,
        }:
            raise TicketImageUploadNotAllowedError

        original_filename, content_type = validate_image(upload_file)
        file_path, size_bytes = await save_image(upload_file)
        image = TicketImage(
            ticket_id=ticket.id,
            uploaded_by_id=current_user.id,
            original_filename=original_filename,
            file_path=file_path,
            content_type=content_type,
            size_bytes=size_bytes,
        )
        try:
            return await self.image_repository.create_image(image)
        except SQLAlchemyError as exc:
            await delete_image(file_path)
            raise ImageCreationError from exc

    async def delete_image(
        self, ticket_id: int, image_id: int, current_user: user
    ) -> None:
        """Delete or remove image from the application.

            Related access and persistence rules are handled by this operation.
        """
        ticket = await self.ticket_service.get_ticket_by_id(ticket_id, current_user)
        image = await self.image_repository.get_image_by_id(image_id)
        if image is None or image.ticket_id != ticket_id:
            raise ImageNotFoundError
        if (
            current_user.role != UserRole.ADMIN
            and ticket.user_id != current_user.id
            and image.uploaded_by_id != current_user.id
        ):
            raise PermissionDeniedError

        await delete_image(image.file_path)
        try:
            await self.image_repository.delete_image(image)
        except SQLAlchemyError as exc:
            raise ImageDeletionError from exc
