import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.exceptions import InvalidCredentialsError
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user_id(
    token: str | None = Depends(oauth2_scheme),
) -> uuid.UUID:
    """
    Dependency to get current user ID from JWT token.

    Raises:
        InvalidCredentialsError: If token is invalid or missing
    """
    if not token:
        raise InvalidCredentialsError("Not authenticated")

    payload = decode_token(token)
    if not payload:
        raise InvalidCredentialsError("Invalid token")

    # Ensure it's an access token, not a refresh token
    if payload.get("type") != "access":
        raise InvalidCredentialsError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError("Invalid token")

    return uuid.UUID(user_id)


async def get_optional_user_id(
    token: str | None = Depends(oauth2_scheme),
) -> uuid.UUID | None:
    """
    Dependency to get current user ID if authenticated.
    Returns None if not authenticated (no exception raised).
    """
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    if payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return uuid.UUID(user_id)


async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency to get current user from database.

    Raises:
        InvalidCredentialsError: If user not found or inactive
    """
    from sqlalchemy import select

    from app.models.user import User

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise InvalidCredentialsError("User not found")

    if not user.is_active:
        raise InvalidCredentialsError("User account is disabled")

    return user


async def require_admin(
    current_user=Depends(get_current_user),
):
    """
    Dependency to require admin privileges.

    Raises:
        InvalidCredentialsError: If user is not a superuser
    """
    from app.core.exceptions import ForbiddenError

    if not current_user.is_superuser:
        raise ForbiddenError("Admin access required")

    return current_user


class RequestMetadata:
    """Request metadata for audit logging."""

    def __init__(self, ip_address: str | None, user_agent: str | None):
        self.ip_address = ip_address
        self.user_agent = user_agent


async def get_request_metadata(request=None) -> RequestMetadata:
    """
    Dependency to get request metadata for audit logging.

    Note: This needs the Request object, so it should be called with
    request parameter when used directly.
    """
    from fastapi import Request

    if request is None or not isinstance(request, Request):
        return RequestMetadata(ip_address=None, user_agent=None)

    # Get client IP (considering proxies)
    ip_address = request.client.host if request.client else None
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()

    user_agent = request.headers.get("user-agent")

    return RequestMetadata(ip_address=ip_address, user_agent=user_agent)
