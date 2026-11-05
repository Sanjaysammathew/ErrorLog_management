import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers.base import api_router
from app.core.config import settings
from app.database.session import engine
from app.exceptions.register_handlers import register_exception_handlers
from app.middleware.request_logging import log_requests
from app.scripts.create_admin import create_admin
from app.scripts.create_manager import create_manager
from app.utils.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources.

    This context runs initialization before serving requests and cleanup on exit.
    """
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
    description=(
        "A role-based error ticket management API for reporting, tracking, and "
        "resolving application and network issues. It supports ticket "
        "categorization, attachments, remarks, status history, approvals, "
        "overdue-ticket monitoring, and user administration for administrators, "
        "managers, and employees."
    ),
    lifespan=lifespan,
)
app.middleware("http")(log_requests)
register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Employee Management API",
        "status": "Running successfully",
    }
