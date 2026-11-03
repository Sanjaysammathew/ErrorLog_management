from app.api.dependency.dependencies import (
    get_auth_service,
    get_category_repository,
    get_category_service,
    get_current_user,
    get_ticket_repository,
    get_ticket_service,
    get_remark_service,
    get_history_service,
    get_user_repository,
    get_user_service,
    require_roles,
)

__all__ = [
    "get_auth_service",
    "get_category_repository",
    "get_category_service",
    "get_current_user",
    "get_ticket_repository",
    "get_ticket_service",
    "get_remark_service",
    "get_history_service",
    "get_user_repository",
    "get_user_service",
    "require_roles",
]