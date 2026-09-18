from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User


MIN_PASSWORD_LENGTH = 8


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:
    """
    Create a new user with a securely hashed password.
    """

    name = name.strip()
    email = _normalize_email(email)

    if not name:
        raise ValueError("Name is required")

    if not email:
        raise ValueError("Email is required")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            "Password must be at least "
            f"{MIN_PASSWORD_LENGTH} characters long"
        )

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:
        raise ValueError(
            "Email already registered"
        )

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()

    except IntegrityError as error:
        db.rollback()

        raise ValueError(
            "Email already registered"
        ) from error

    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> str:
    """
    Authenticate a user and return a JWT access token.

    Inactive users are not allowed to obtain new tokens.
    """

    email = _normalize_email(email)

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if user is None:
        raise ValueError(
            "Invalid email or password"
        )

    if not user.is_active:
        raise ValueError(
            "Invalid email or password"
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError(
            "Invalid email or password"
        )

    return create_access_token(
        str(user.id)
    )