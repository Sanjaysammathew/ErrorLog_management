from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Convert the supplied secret into a secure password hash.

        The hash can be stored and checked without keeping the plain password.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a supplied value against its stored representation.

        This is used to confirm credentials or other protected data.
    """
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str, role: str) -> str:
    """Create a signed access token for the authenticated user.

        The token contains identity and role claims used by protected API routes.
    """
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "role": role, "type": "access", "exp": expires_at}
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(subject: str, role: str) -> str:
    """Create a signed refresh token for the authenticated user.

        The token can be exchanged for a fresh authentication token pair.
    """
    expires_at = datetime.now(UTC) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {"sub": subject, "role": role, "type": "refresh", "exp": expires_at}
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_refresh_token(token: str) -> dict:
    """Decode and validate the supplied refresh token.

        Invalid or expired values are rejected by the security layer.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid refresh token") from exc

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")
    return payload
