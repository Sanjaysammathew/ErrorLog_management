from fastapi import FastAPI

from app.exceptions.custom_exceptions import (
    AppError,
    ApprovalAlreadyDecidedError,
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    EmailDeliveryError,
    ImageCreationError,
    ImageDeletionError,
    ImageNotFoundError,
    ImageStorageError,
    InvalidCredentialsError,
    InvalidImageError,
    InvalidTokenError,
    InvalidUserLookupError,
    ManagerNotFoundError,
    PermissionDeniedError,
    TicketCreationError,
    TicketNotFoundError,
    TicketNotResolvedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.exceptions.handlers import (
    app_error_handler,
    approval_already_decided_handler,
    category_already_exists_handler,
    category_not_found_handler,
    email_delivery_handler,
    image_creation_handler,
    image_deletion_handler,
    image_not_found_handler,
    image_storage_handler,
    image_validation_handler,
    invalid_credentials_handler,
    invalid_token_handler,
    invalid_user_lookup_handler,
    manager_not_found_handler,
    permission_denied_handler,
    ticket_creation_handler,
    ticket_not_found_handler,
    ticket_not_resolved_handler,
    user_already_exists_handler,
    user_not_found_handler,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register application exception handlers on the FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
    app.add_exception_handler(InvalidTokenError, invalid_token_handler)
    app.add_exception_handler(
        CategoryAlreadyExistsError, category_already_exists_handler
    )
    app.add_exception_handler(ManagerNotFoundError, manager_not_found_handler)
    app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(InvalidUserLookupError, invalid_user_lookup_handler)
    app.add_exception_handler(CategoryNotFoundError, category_not_found_handler)
    app.add_exception_handler(TicketCreationError, ticket_creation_handler)
    app.add_exception_handler(TicketNotFoundError, ticket_not_found_handler)
    app.add_exception_handler(TicketNotResolvedError, ticket_not_resolved_handler)
    app.add_exception_handler(
        ApprovalAlreadyDecidedError, approval_already_decided_handler
    )
    app.add_exception_handler(EmailDeliveryError, email_delivery_handler)
    app.add_exception_handler(ImageNotFoundError, image_not_found_handler)
    app.add_exception_handler(InvalidImageError, image_validation_handler)
    app.add_exception_handler(ImageStorageError, image_storage_handler)
    app.add_exception_handler(ImageCreationError, image_creation_handler)
    app.add_exception_handler(ImageDeletionError, image_deletion_handler)
