from app.api.routers.auth import router as auth_router
from app.api.routers.categories import router as categories_router
from app.api.routers.health import router as health_router
from app.api.routers.users import router as users_router

__all__ = [
    "auth_router",
    "categories_router",
    "health_router",
    "users_router",
]