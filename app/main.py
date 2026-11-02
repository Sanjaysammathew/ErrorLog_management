from contextlib import asynccontextmanager
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.core.config import settings
from app.database.session import engine
from app.exceptions.custom_exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    ManagerNotFoundError,
    PermissionDeniedError,
    UserAlreadyExistsError,
)
from app.exceptions.handlers import (
    invalid_credentials_handler,
    invalid_token_handler,
    manager_not_found_handler,
    permission_denied_handler,
    user_already_exists_handler,
)
from app.models import ErrorCategory, error_ticket, ticket_approval, ticket_remark
from app.models import ticket_status_history, user
from app.api.routers.users import router as auth_router
from app.scripts.create_admin import create_admin
from app.scripts.create_manager import create_manager
from app.utils.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger = logging.getLogger("app")
    admin_created = await create_admin()
    manager_created = await create_manager()
    logger.info("Admin seed: %s", admin_created)
    logger.info("Manager seed: %s", manager_created)
    logger.info("Application started")

    try:
        yield
    finally:
        await engine.dispose()
        logger.info("Application stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_handler)
app.add_exception_handler(ManagerNotFoundError, manager_not_found_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.include_router(health_router)
app.include_router(auth_router)
