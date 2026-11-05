from app.core.config import settings
from app.core.security import hash_password
from app.database.session import sessionLocal
from app.models.user import UserRole, user as UserModel
from app.repositories.implementations import UserRepository


async def create_manager() -> str:
    """Create a manager account for the application.

        This setup task stores the account with manager permissions.
    """
    if (
        settings.MANAGER_USERNAME is None
        or settings.MANAGER_EMAIL is None
        or settings.MANAGER_PASSWORD is None
    ):
        return "skipped"

    async with sessionLocal() as db:
        repository = UserRepository(db)
        existing_manager = await repository.get_by_username_or_email(
            settings.MANAGER_USERNAME, settings.MANAGER_EMAIL
        )
        if existing_manager is not None:
            return "exists"

        await repository.create(
            UserModel(
                username=settings.MANAGER_USERNAME,
                email=settings.MANAGER_EMAIL,
                hashed_password=hash_password(
                    settings.MANAGER_PASSWORD.get_secret_value()
                ),
                role=UserRole.MANAGER,
            )
        )
        return "created"
