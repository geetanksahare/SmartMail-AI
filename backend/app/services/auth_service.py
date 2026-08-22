from sqlalchemy import select
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.core.security import create_access_token, verify_password
from app.models.user import User


password_hash = PasswordHash.recommended()


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("Email already registered")

    hashed_password = password_hash.hash(password)

    user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> str:

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError("Invalid email or password")

    return create_access_token(str(user.id))