from app.api.routers.auth import router as auth_router
from app.api.routers.categories import router as categories_router
from app.api.routers.health import router as health_router
from app.api.routers.users import router as users_router
from app.api.routers.tickets import router as tickets_router
from app.api.routers.remarks import router as remarks_router
from app.api.routers.history import router as history_router
from app.api.routers.approval import router as approval_router

__all__ = [
    "auth_router",
    "categories_router",
    "health_router",
    "users_router",
    "tickets_router",
    "remarks_router",
    "history_router",
    "approval_router",
]