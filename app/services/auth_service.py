from app.core.security import verify_password
from app.exceptions.custom_exceptions import InvalidCredentialsError
from app.models.user import user
from app.repositories.interfaces.user_interface import UserInterface


class AuthService:
    """Apply business rules for auth operations.

        The service coordinates validation and the required data access.
    """
    def __init__(self, user_repository: UserInterface) -> None:
        """Initialize the auth service with its collaborators.

            These dependencies provide the business logic with data access and related services.
        """
        self.user_repository = user_repository

    async def authenticate_user(self, login: str, password: str) -> user:
        """Verify a user's login credentials.

            Inactive accounts and incorrect credentials are rejected before tokens are issued.
        """
        current_user = await self.user_repository.get_by_username_or_email(login, login)
        if current_user is None or not verify_password(
            password, current_user.hashed_password
        ):
            raise InvalidCredentialsError

        return current_user
