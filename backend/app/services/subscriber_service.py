from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscriber import Subscriber
from app.models.user import User

from math import ceil
from sqlalchemy import func, select

def create_subscriber(
    db: Session,
    current_user: User,
    name: str,
    email: str,
) -> Subscriber:

    existing_subscriber = db.scalar(
        select(Subscriber).where(
            Subscriber.owner_id == current_user.id,
            Subscriber.email == email,
        )
    )

    if existing_subscriber:
        raise ValueError(
            "Subscriber with this email already exists"
        )

    subscriber = Subscriber(
        owner_id=current_user.id,
        name=name,
        email=email,
        status="active",
    )

    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    return subscriber


def get_subscribers(
    db: Session,
    current_user: User,
    page: int,
    page_size: int,
    search: str | None = None,
    status: str | None = None,
) -> tuple[list[Subscriber], int, int]:

    filters = [
        Subscriber.owner_id == current_user.id,
    ]

    if search:
        search_pattern = f"%{search.strip()}%"

        filters.append(
            (
                Subscriber.name.ilike(search_pattern)
                | Subscriber.email.ilike(search_pattern)
            )
        )

    if status:
        filters.append(
            Subscriber.status == status
        )

    total = db.scalar(
        select(func.count())
        .select_from(Subscriber)
        .where(*filters)
    ) or 0

    offset = (page - 1) * page_size

    subscribers = list(
        db.scalars(
            select(Subscriber)
            .where(*filters)
            .order_by(Subscriber.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
    )

    total_pages = ceil(total / page_size) if total else 0

    return subscribers, total, total_pages


def get_subscriber(
    db: Session,
    current_user: User,
    subscriber_id: int,
) -> Subscriber:

    subscriber = db.scalar(
        select(Subscriber).where(
            Subscriber.id == subscriber_id,
            Subscriber.owner_id == current_user.id,
        )
    )

    if subscriber is None:
        raise ValueError("Subscriber not found")

    return subscriber


def update_subscriber(
    db: Session,
    current_user: User,
    subscriber_id: int,
    name: str | None = None,
    email: str | None = None,
    status: str | None = None,
) -> Subscriber:

    subscriber = get_subscriber(
        db=db,
        current_user=current_user,
        subscriber_id=subscriber_id,
    )

    if email is not None and email != subscriber.email:
        existing_subscriber = db.scalar(
            select(Subscriber).where(
                Subscriber.owner_id == current_user.id,
                Subscriber.email == email,
                Subscriber.id != subscriber_id,
            )
        )

        if existing_subscriber:
            raise ValueError(
                "Subscriber with this email already exists"
            )

        subscriber.email = email

    if name is not None:
        subscriber.name = name

    if status is not None:
        subscriber.status = status

    db.commit()
    db.refresh(subscriber)

    return subscriber


def delete_subscriber(
    db: Session,
    current_user: User,
    subscriber_id: int,
) -> None:

    subscriber = get_subscriber(
        db=db,
        current_user=current_user,
        subscriber_id=subscriber_id,
    )

    db.delete(subscriber)
    db.commit()