from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.subscriber import (
    SubscriberCreate,
    SubscriberListResponse,
    SubscriberResponse,
    SubscriberUpdate,
)
from app.services.subscriber_service import (
    create_subscriber,
    delete_subscriber,
    get_subscriber,
    get_subscribers,
    update_subscriber,
)


router = APIRouter(
    prefix="/subscribers",
    tags=["Subscribers"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "",
    response_model=SubscriberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    request: SubscriberCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return create_subscriber(
            db=db,
            current_user=current_user,
            name=request.name,
            email=request.email,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.get(
    "",
    response_model=SubscriberListResponse,
)
def list_all(
    current_user: CurrentUser,
    db: DatabaseSession,
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of subscribers per page",
    ),
    search: str | None = Query(
        default=None,
        description="Search by subscriber name or email",
    ),
    status: str | None = Query(
        default=None,
        description="Filter by active or inactive status",
    ),
):
    subscribers, total, total_pages = get_subscribers(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    )

    return {
        "items": subscribers,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


@router.get(
    "/{subscriber_id}",
    response_model=SubscriberResponse,
)
def get_one(
    subscriber_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return get_subscriber(
            db=db,
            current_user=current_user,
            subscriber_id=subscriber_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.put(
    "/{subscriber_id}",
    response_model=SubscriberResponse,
)
def update(
    subscriber_id: int,
    request: SubscriberUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return update_subscriber(
            db=db,
            current_user=current_user,
            subscriber_id=subscriber_id,
            name=request.name,
            email=request.email,
            status=request.status,
        )

    except ValueError as error:
        if "already exists" in str(error):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(error),
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{subscriber_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    subscriber_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        delete_subscriber(
            db=db,
            current_user=current_user,
            subscriber_id=subscriber_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )