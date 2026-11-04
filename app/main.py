from contextlib import asynccontextmanager
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.auth import router as auth_router
from app.api.routers.categories import router as categories_router
from app.core.config import settings
from app.database.session import engine
from app.exceptions.custom_exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    CategoryAlreadyExistsError,
    ManagerNotFoundError,
    PermissionDeniedError,
    UserAlreadyExistsError,
    UserNotFoundError,
    CategoryNotFoundError,
    TicketCreationError,
    TicketNotFoundError,
    TicketNotResolvedError,
    ApprovalAlreadyDecidedError,
    EmailDeliveryError,
    ImageNotFoundError,
    InvalidImageError,
    ImageStorageError,
    ImageCreationError,
    ImageDeletionError,
)
from app.exceptions.handlers import (
    invalid_credentials_handler,
    invalid_token_handler,
    category_already_exists_handler,
    manager_not_found_handler,
    permission_denied_handler,
    user_already_exists_handler,
    user_not_found_handler,
    category_not_found_handler,
    ticket_creation_handler,
    ticket_not_found_handler,
    ticket_not_resolved_handler,
    approval_already_decided_handler,
    email_delivery_handler,
    image_not_found_handler,
    image_validation_handler,
    image_storage_handler,
    image_creation_handler,
    image_deletion_handler,
)
from app.models import ErrorCategory, error_ticket, ticket_approval, ticket_remark
from app.models import ticket_status_history, user
from app.models import ticket_image
from app.api.routers.users import router as users_router
from app.api.routers.tickets import router as tickets_router
from app.api.routers.remarks import router as remarks_router
from app.api.routers.history import router as history_router
from app.api.routers.approval import router as approval_router
from app.api.routers.ticket_image_router import router as ticket_image_router
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
app.add_exception_handler(
    CategoryAlreadyExistsError, category_already_exists_handler
)
app.add_exception_handler(ManagerNotFoundError, manager_not_found_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(UserNotFoundError, user_not_found_handler)
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
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(tickets_router)
app.include_router(remarks_router)
app.include_router(history_router)
app.include_router(approval_router)
app.include_router(ticket_image_router)
