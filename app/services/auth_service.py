from app.core.security import hash_password, verify_password
from app.exceptions.custom_exceptions import (
    InvalidCredentialsError,
    ManagerNotFoundError,
    UserAlreadyExistsError,
)
from app.models.user import UserRole, user
from app.repositories.interfaces.user_interface import UserInterface
from app.schemas.userSchema import UserCreate


class AuthService:
    def __init__(self, user_repository: UserInterface) -> None:
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate) -> user:
        existing_user = await self.user_repository.get_by_username_or_email(
            user_data.username, user_data.email
        )
        if existing_user is not None:
            raise UserAlreadyExistsError

        manager_id = None
        if user_data.role == UserRole.EMPLOYEE:
            manager = await self.user_repository.get_by_role(UserRole.MANAGER)
            if manager is None:
                raise ManagerNotFoundError
            manager_id = manager.id

        new_user = user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
            department=user_data.department,
            manager_id=manager_id,
        )
        return await self.user_repository.create(new_user)

    async def authenticate_user(self, login: str, password: str) -> user:
        current_user = await self.user_repository.get_by_username_or_email(login, login)
        if current_user is None or not verify_password(
            password, current_user.hashed_password
        ):
            raise InvalidCredentialsError

        return current_user

    async def list_users(
        self, offset: int = 0, limit: int = 10
    ) -> tuple[list[user], int]:
        users = await self.user_repository.get_all(offset, limit)
        total_count = await self.user_repository.count_all()
        return {
            "items": users,
            "total": total_count,
            "page": offset // limit + 1,
            "page_size": limit,
        }
