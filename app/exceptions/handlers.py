from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    ManagerNotFoundError,
    PermissionDeniedError,
    UserAlreadyExistsError,
    UserNotFoundError,
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
