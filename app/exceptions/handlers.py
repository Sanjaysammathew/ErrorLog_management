from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import (
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


async def user_already_exists_handler(
    _: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def invalid_credentials_handler(
    _: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def invalid_token_handler(_: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def permission_denied_handler(
    _: Request, exc: PermissionDeniedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message},
    )


async def manager_not_found_handler(
    _: Request, exc: ManagerNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def user_not_found_handler(
    _: Request, exc: UserNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def category_already_exists_handler(
    _: Request, exc: CategoryAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def category_not_found_handler(
    _: Request, exc: CategoryNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def ticket_creation_handler(
    _: Request, exc: TicketCreationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def ticket_not_found_handler(
    _: Request, exc: TicketNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def ticket_not_resolved_handler(
    _: Request, exc: TicketNotResolvedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def approval_already_decided_handler(
    _: Request, exc: ApprovalAlreadyDecidedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def email_delivery_handler(
    _: Request, exc: EmailDeliveryError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": exc.message},
    )


async def image_not_found_handler(
    _: Request, exc: ImageNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
    )


async def image_validation_handler(
    _: Request, exc: InvalidImageError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
    )


async def image_storage_handler(
    _: Request, exc: ImageStorageError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )


async def image_creation_handler(
    _: Request, exc: ImageCreationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message}
    )


async def image_deletion_handler(
    _: Request, exc: ImageDeletionError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message}
    )
