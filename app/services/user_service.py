from app.core.security import hash_password
from app.exceptions.custom_exceptions import (
    InvalidUserLookupError,
    ManagerNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.user import UserRole, user
from app.repositories.interfaces.user_interface import UserInterface
from app.schemas.userSchema import UserCreate, UserUpdate
from app.services.email_service import EmailService


class UserService:
    """Apply business rules for user operations.

        The service coordinates validation and the required data access.
    """
    def __init__(
        self, user_repository: UserInterface, email_service: EmailService
    ) -> None:
        """Initialize the user service with its collaborators.

            These dependencies provide data access and related business services.
        """
        self.user_repository = user_repository
        self.email_service = email_service

    async def register_user(self, user_data: UserCreate) -> user:
        """Create a user account from validated registration data.

            The service stores the account and performs required onboarding steps.
        """
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

        created_user = await self.user_repository.create(
            user(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hash_password(user_data.password),
                role=user_data.role,
                department=user_data.department,
                manager_id=manager_id,
            )
        )
        if created_user.role == UserRole.EMPLOYEE:
            await self.email_service.send_account_created(created_user)
        return created_user

    async def list_users(self, page: int = 1, page_size: int = 10) -> dict:
        """Retrieve a paginated list of user accounts.

            The service combines the selected users with pagination information.
        """
        offset = (page - 1) * page_size
        users = await self.user_repository.get_all(offset, page_size)
        total_count = await self.user_repository.count_all()
        return {
            "items": users,
            "total": total_count,
            "page": page,
            "page_size": page_size,
        }

    async def get_user(
        self, user_id: int | None = None, email: str | None = None
    ) -> user:
        """Find the user account needed by the operation.

            The service returns the matching account or reports that it is missing.
        """
        if email is not None:
            existing_user = await self.user_repository.get_by_email(email)
        elif user_id is not None:
            existing_user = await self.user_repository.get_by_id(user_id)
        else:
            raise InvalidUserLookupError
        if existing_user is None:
            raise UserNotFoundError
        return existing_user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> user:
        """Update an existing user account.

            The service applies allowed account changes and returns the updated user.
        """
        existing_user = await self.get_user(user_id)
        changes = user_data.model_dump(exclude_unset=True)
        if "password" in changes:
            changes["hashed_password"] = hash_password(changes.pop("password"))
        if existing_user.role == UserRole.EMPLOYEE and existing_user.manager_id is None:
            manager = await self.user_repository.get_by_role(UserRole.MANAGER)
            if manager is not None:
                changes["manager_id"] = manager.id
        return await self.user_repository.update(user_id, changes)

    async def deactivate_user(self, user_id: int) -> user:
        """Deactivate user while preserving its stored record.

            This prevents it from being treated as active by the application.
        """
        await self.get_user(user_id)
        return await self.user_repository.update(user_id, {"is_active": False})
