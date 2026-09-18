from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
)
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    decode_access_token,
)
from app.database.session import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: DatabaseSession,
) -> User:
    """
    Validate the JWT, load the user by ID, and ensure the
    account is still active.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = decode_access_token(
            token
        )

    except JWTError:
        raise credentials_exception

    subject = payload.get("sub")

    if not subject:
        raise credentials_exception

    try:
        user_id = int(subject)

    except (TypeError, ValueError):
        raise credentials_exception

    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user