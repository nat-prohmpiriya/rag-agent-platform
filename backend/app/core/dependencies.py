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
) -> int:
    """
    Dependency to get current user ID from JWT token.

    Raises:
        InvalidCredentialsError: If token is invalid or missing
    """
    if not token:
        raise InvalidCredentialsError()

    payload = decode_token(token)
    if not payload:
        raise InvalidCredentialsError()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError()

    return int(user_id)


async def get_optional_user_id(
    token: str | None = Depends(oauth2_scheme),
) -> int | None:
    """
    Dependency to get current user ID if authenticated.
    Returns None if not authenticated (no exception raised).
    """
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return int(user_id)
