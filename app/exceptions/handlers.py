import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import (
    AppError,
    InvalidCredentialsError,
    InvalidTokenError,
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    ManagerNotFoundError,
    PermissionDeniedError,
    TicketCreationError,
    TicketNotFoundError,
    TicketNotResolvedError,
    ApprovalAlreadyDecidedError,
    EmailDeliveryError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ImageNotFoundError,
    InvalidImageError,
    ImageStorageError,
    ImageCreationError,
    ImageDeletionError,
)

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors without a dedicated handler."""
    logger.error(
        "Unhandled application error (%s) for %s %s",
        type(exc).__name__,
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )


async def user_already_exists_handler(
    request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    """Handle the user already exists error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "User already exists error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    """Handle the invalid credentials error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Invalid credentials error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    """Handle the invalid token error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Invalid token error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def permission_denied_handler(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    """Handle the permission denied error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Permission denied error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message},
    )


async def manager_not_found_handler(
    request: Request, exc: ManagerNotFoundError
) -> JSONResponse:
    """Handle the manager not found error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Manager not found error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def user_not_found_handler(
    request: Request, exc: UserNotFoundError
) -> JSONResponse:
    """Handle the user not found error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "User not found error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def category_already_exists_handler(
    request: Request, exc: CategoryAlreadyExistsError
) -> JSONResponse:
    """Handle the category already exists error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Category already exists error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def category_not_found_handler(
    request: Request, exc: CategoryNotFoundError
) -> JSONResponse:
    """Handle the category not found error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Category not found error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def ticket_creation_handler(
    request: Request, exc: TicketCreationError
) -> JSONResponse:
    """Handle the ticket creation error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Ticket creation error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def ticket_not_found_handler(
    request: Request, exc: TicketNotFoundError
) -> JSONResponse:
    """Handle the ticket not found error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Ticket not found error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def ticket_not_resolved_handler(
    request: Request, exc: TicketNotResolvedError
) -> JSONResponse:
    """Handle the ticket not resolved error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Ticket not resolved error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def approval_already_decided_handler(
    request: Request, exc: ApprovalAlreadyDecidedError
) -> JSONResponse:
    """Handle the approval already decided error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Approval already decided error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def email_delivery_handler(
    request: Request, exc: EmailDeliveryError
) -> JSONResponse:
    """Handle the email delivery error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Email delivery error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": exc.message},
    )


async def image_not_found_handler(
    request: Request, exc: ImageNotFoundError
) -> JSONResponse:
    """Handle the image not found error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Image not found error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
    )


async def image_validation_handler(
    request: Request, exc: InvalidImageError
) -> JSONResponse:
    """Handle the image validation error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Image validation error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
    )


async def image_storage_handler(
    request: Request, exc: ImageStorageError
) -> JSONResponse:
    """Handle the image storage error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Image storage error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )


async def image_creation_handler(
    request: Request, exc: ImageCreationError
) -> JSONResponse:
    """Handle the image creation error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Image creation error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message}
    )


async def image_deletion_handler(
    request: Request, exc: ImageDeletionError
) -> JSONResponse:
    """Handle the image deletion error for an HTTP request.

        The handler logs the failure and returns the matching error response.
    """
    logger.error(
        "Image deletion error (%s) for %s %s",
        type(exc).__name__, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message}
    )
