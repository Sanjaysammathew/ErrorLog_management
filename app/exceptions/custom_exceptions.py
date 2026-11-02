class AppError(Exception):
    """Base class for application errors with a safe client-facing message."""

    default_message = "An application error occurred"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class UserAlreadyExistsError(AppError):
    """Raised when a username or email is already registered."""

    default_message = "Username or email is already registered"


class InvalidCredentialsError(AppError):
    """Raised when login credentials are invalid."""

    default_message = "Incorrect email or password"


class InvalidTokenError(AppError):
    """Raised when an access token is invalid."""

    default_message = "Could not validate credentials"


class PermissionDeniedError(AppError):
    """Raised when a user lacks the required role."""

    default_message = "You do not have permission to perform this action"


class ManagerNotFoundError(AppError):
    """Raised when an employee cannot be assigned a manager."""

    default_message = "No manager is available for employee assignment"


class UserNotFoundError(AppError):
    default_message = "User not found"


class CategoryAlreadyExistsError(AppError):
    default_message = "Category name is already registered"
