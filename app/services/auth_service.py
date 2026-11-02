from app.core.security import verify_password
from app.exceptions.custom_exceptions import InvalidCredentialsError
from app.models.user import user
from app.repositories.interfaces.user_interface import UserInterface


class AuthService:
    def __init__(self, user_repository: UserInterface) -> None:
        self.user_repository = user_repository

    async def authenticate_user(self, login: str, password: str) -> user:
        current_user = await self.user_repository.get_by_username_or_email(login, login)
        if current_user is None or not verify_password(
            password, current_user.hashed_password
        ):
            raise InvalidCredentialsError

        return current_user
