from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# HTTP BEARER AUTHENTICATION
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=True,
)


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against the stored bcrypt hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt password hash.
    """
    return pwd_context.hash(password)


# ============================================================
# ACCESS TOKEN
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ============================================================
# REFRESH TOKEN
# ============================================================

def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.
    """

    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ============================================================
# DECODE JWT TOKEN
# ============================================================

def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )


# ============================================================
# GET CURRENT USER
# ============================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract the Bearer token from the Authorization header,
    validate the JWT, and return the authenticated user.
    """

    # --------------------------------------------------------
    # Extract token
    # --------------------------------------------------------

    token = credentials.credentials

    # --------------------------------------------------------
    # Decode token
    # --------------------------------------------------------

    payload = decode_token(token)

    # --------------------------------------------------------
    # Validate token type
    # --------------------------------------------------------

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------------
    # Get user ID from JWT subject
    # --------------------------------------------------------

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------------
    # Convert user ID safely
    # --------------------------------------------------------

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------------
    # Find user in PostgreSQL
    # --------------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalars().first()

    # --------------------------------------------------------
    # Validate user
    # --------------------------------------------------------

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


# ============================================================
# ROLE-BASED AUTHORIZATION
# ============================================================

class RequireRoles:
    """
    Dependency used to restrict an endpoint to specific roles.

    SUPER_ADMIN automatically has access to all protected
    role-based endpoints.
    """

    def __init__(
        self,
        allowed_roles: List[UserRole],
    ):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:

        # ----------------------------------------------------
        # SUPER_ADMIN has full access
        # ----------------------------------------------------

        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        # ----------------------------------------------------
        # Check allowed roles
        # ----------------------------------------------------

        if current_user.role not in self.allowed_roles:

            role_value = getattr(
                current_user.role,
                "value",
                str(current_user.role),
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User role '{role_value}' "
                    "lacks permission for this action"
                ),
            )

        return current_user