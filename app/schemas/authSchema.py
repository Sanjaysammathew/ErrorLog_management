
from pydantic import BaseModel

from app.models.user import UserRole


class Token(BaseModel):
    """Represent the authentication tokens returned after sign-in or refresh.

        The schema describes the bearer token response used by API clients.
    """

    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Represent identity information decoded from an access token.

        The schema provides the authenticated user's token claims.
    """

    email: str | None = None
    role: UserRole | None = None


class RefreshTokenRequest(BaseModel):
    """Represent a request to refresh authentication tokens.

        The schema validates the refresh token submitted by a client.
    """

    refresh_token: str
