from app.api.routers import (
    approval_router,
    auth_router,
    categories_router,
    health_router,
    history_router,
    remarks_router,
    tickets_router,
    users_router,
)

__all__ = [
    "auth_router",
    "categories_router",
    "health_router",
    "tickets_router",
    "users_router",
    "remarks_router",
    "history_router",
    "approval_router",
]