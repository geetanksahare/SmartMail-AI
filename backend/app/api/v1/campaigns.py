from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.campaign import Campaign
from app.models.subscriber import Subscriber
from app.models.user import User
from app.schemas.analytics import (
    CampaignAnalyticsResponse,
)
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignSendResponse,
    CampaignUpdate,
)
from app.services.analytics_service import (
    get_campaign_analytics,
)
from app.services.campaign_send_service import (
    claim_campaign_for_sending,
    reset_campaign_to_draft,
)
from app.services.campaign_service import (
    create_campaign,
    delete_campaign,
    get_campaign,
    get_campaigns,
    update_campaign,
)
from app.tasks.email_tasks import dispatch_campaign


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"],
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
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    request: CampaignCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    return create_campaign(
        db=db,
        current_user=current_user,
        title=request.title,
        subject=request.subject,
        preview_text=request.preview_text,
        content=request.content,
        cta_text=request.cta_text,
        cta_url=request.cta_url,
        audience_description=(
            request.audience_description
        ),
    )


@router.get(
    "",
    response_model=list[CampaignResponse],
)
def list_all(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    return get_campaigns(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
def get_one(
    campaign_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return get_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
def update(
    campaign_id: int,
    request: CampaignUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return update_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
            title=request.title,
            subject=request.subject,
            preview_text=request.preview_text,
            content=request.content,
            cta_text=request.cta_text,
            cta_url=request.cta_url,
            audience_description=(
                request.audience_description
            ),
        )

    except ValueError as error:
        message = str(error)

        if "Only draft" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )


@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    campaign_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        delete_campaign(
            db=db,
            current_user=current_user,
            campaign_id=campaign_id,
        )

    except ValueError as error:
        message = str(error)

        if "Only draft" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )


@router.post(
    "/{campaign_id}/send",
    response_model=CampaignSendResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def send_campaign(
    campaign_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    # First verify the campaign exists and belongs to the user.
    campaign = db.scalar(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.owner_id == current_user.id,
        )
    )

    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # Don't allow campaigns that are already being processed
    # or completed to be sent again.
    if campaign.status not in {
        "draft",
        "failed",
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Campaign is already being processed "
                "or has already been sent."
            ),
        )

    active_subscriber_count = db.scalar(
        select(func.count())
        .select_from(Subscriber)
        .where(
            Subscriber.owner_id == current_user.id,
            Subscriber.status == "active",
        )
    ) or 0

    if active_subscriber_count == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Campaign cannot be sent because "
                "there are no active subscribers."
            ),
        )

    # IMPORTANT:
    # This is an atomic database state transition.
    #
    # If two requests arrive simultaneously, only one of
    # them can change draft/failed -> sending.
    claimed_campaign = claim_campaign_for_sending(
        db=db,
        campaign_id=campaign_id,
        owner_id=current_user.id,
    )

    if claimed_campaign is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Campaign is already being processed "
                "or has already been sent."
            ),
        )

    try:
        task = dispatch_campaign.delay(
            claimed_campaign.id
        )

    except Exception as error:
        reset_campaign_to_draft(
            db=db,
            campaign_id=claimed_campaign.id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Unable to queue campaign for sending."
            ),
        ) from error

    return {
        "message": "Campaign queued for sending.",
        "campaign_id": claimed_campaign.id,
        "task_id": task.id,
        "status": "sending",
    }


@router.get(
    "/{campaign_id}/analytics",
    response_model=CampaignAnalyticsResponse,
)
def analytics(
    campaign_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    campaign = db.scalar(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.owner_id == current_user.id,
        )
    )

    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    return get_campaign_analytics(
        db=db,
        campaign_id=campaign_id,
    )