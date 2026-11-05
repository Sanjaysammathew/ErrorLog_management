from app.core.config import settings
from app.core.security import hash_password
from app.database.session import sessionLocal
from app.models.user import UserRole
from app.models.user import user as UserModel
from app.repositories.implementations import UserRepository


async def create_admin() -> str:
    """Create the initial administrator account for the application.

        This setup task stores the account with administrator permissions.
    """
    if (
        settings.ADMIN_USERNAME is None
        or settings.ADMIN_EMAIL is None
        or settings.ADMIN_PASSWORD is None
    ):
        return "skipped"

    async with sessionLocal() as db:
        repository = UserRepository(db)
        existing_admin = await repository.get_by_username_or_email(
            settings.ADMIN_USERNAME, settings.ADMIN_EMAIL
        )
        if existing_admin is not None:
            return "exists"

        await repository.create(
            UserModel(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=hash_password(
                    settings.ADMIN_PASSWORD.get_secret_value()
                ),
                role=UserRole.ADMIN,
            )
        )
        return "created"
