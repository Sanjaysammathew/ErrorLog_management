from fastapi import APIRouter

from app.api.routers.approval import router as approval_router
from app.api.routers.auth import router as auth_router
from app.api.routers.categories import router as categories_router
from app.api.routers.health import router as health_router
from app.api.routers.history import router as history_router
from app.api.routers.remarks import router as remarks_router
from app.api.routers.ticket_image_router import router as ticket_image_router
from app.api.routers.tickets import router as tickets_router
from app.api.routers.users import router as users_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(tickets_router)
api_router.include_router(remarks_router)
api_router.include_router(history_router)
api_router.include_router(approval_router)
api_router.include_router(ticket_image_router)
