class AppError(Exception):
    """Base class for application errors with a safe client-facing message."""

    default_message = "An application error occurred"

    def __init__(self, message: str | None = None) -> None:
        """Initialize the apperror error with its client-facing message.

            The message is retained for logging and API error handling.
        """
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
    """Represent an attempt to access a user account that does not exist.

        The exception is translated into a not-found API response.
    """
    default_message = "User not found"


class InvalidUserLookupError(AppError):
    """Represent a user lookup request without an identifier.

    The exception is translated into a bad request API response.
    """

    default_message = "Provide either user_id or email."


class CategoryAlreadyExistsError(AppError):
    """Represent a category name conflict during category creation.

        The exception is translated into a conflict API response.
    """
    default_message = "Category name is already registered"


class CategoryNotFoundError(AppError):
    """Represent an attempt to access a category that does not exist.

        The exception is translated into a not-found API response.
    """
    default_message = "Category not found"


class TicketCreationError(AppError):
    """Represent a failure to create a support ticket.

        The exception is translated into a ticket creation error response.
    """
    default_message = "Ticket could not be created"


class TicketNotFoundError(AppError):
    """Represent an attempt to access a ticket that does not exist.

        The exception is translated into a not-found API response.
    """
    default_message = "Ticket not found"


class TicketNotResolvedError(AppError):
    """Represent an attempt to close a ticket before it is resolved.

        The exception prevents closure until the ticket reaches the required state.
    """
    default_message = "Only resolved tickets can be closed"


class ApprovalAlreadyDecidedError(AppError):
    """Represent an approval request that already has a decision.

        The exception prevents a second decision from replacing the first.
    """
    default_message = "This approval has already been decided"


class EmailDeliveryError(AppError):
    """Represent a failure while delivering an email notification.

        The exception is translated into an email delivery error response.
    """
    default_message = "Email notification could not be sent"


class ImageNotFoundError(AppError):
    """Represent an attempt to access an image attachment that does not exist.

        The exception is translated into a not-found API response.
    """
    default_message = "Image not found"


class InvalidImageError(AppError):
    """Represent an uploaded image that fails validation.

        The exception is translated into a request validation error.
    """
    default_message = "Invalid image"


class ImageStorageError(AppError):
    """Represent a failure while storing or reading an image file.

        The exception indicates that image storage could not complete.
    """
    default_message = "Image storage operation failed"


class ImageCreationError(AppError):
    """Represent a failure while creating an image attachment record.

        The exception is translated into an image creation error response.
    """
    default_message = "Image could not be created"


class ImageDeletionError(AppError):
    """Represent a failure while deleting an image attachment.

        The exception is translated into an image deletion error response.
    """
    default_message = "Image could not be deleted"
