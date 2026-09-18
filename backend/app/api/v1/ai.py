from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.ai import (
    AICampaignAnalysisResponse,
    AIGenerateRequest,
    AIGenerateResponse,
)
from app.services.ai.manager import (
    AIServiceError,
    ai_manager,
)
from app.services.ai_analysis_service import (
    analyze_campaign,
)
from app.services.analytics_service import (
    get_campaign_analytics,
)
from app.utils.prompts import (
    build_newsletter_system_prompt,
    build_newsletter_user_prompt,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
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
    "/generate",
    response_model=AIGenerateResponse,
)
def generate_newsletter(
    request: AIGenerateRequest,
    current_user: CurrentUser,
):
    system_prompt = (
        build_newsletter_system_prompt()
    )

    user_prompt = build_newsletter_user_prompt(
        topic=request.topic,
        audience=request.audience,
        tone=request.tone,
        length=request.length,
        key_points=request.key_points,
    )

    try:
        return ai_manager.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=AIGenerateResponse,
        )

    except AIServiceError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "AI service is temporarily unavailable."
            ),
        ) from error


@router.post(
    "/analyze-campaign/{campaign_id}",
    response_model=AICampaignAnalysisResponse,
)
def analyze_campaign_endpoint(
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

    analytics = get_campaign_analytics(
        db=db,
        campaign_id=campaign_id,
    )

    try:
        return analyze_campaign(
            title=campaign.title,
            subject=campaign.subject,
            audience=(
                campaign.audience_description
            ),
            total_recipients=analytics[
                "total_recipients"
            ],
            sent=analytics["sent"],
            delivered=analytics["delivered"],
            opened=analytics["opened"],
            clicked=analytics["clicked"],
            bounced=analytics["bounced"],
            complained=analytics["complained"],
            unsubscribed=analytics[
                "unsubscribed"
            ],
            failed=analytics["failed"],
            delivery_rate=analytics[
                "delivery_rate"
            ],
            open_rate=analytics["open_rate"],
            click_rate=analytics[
                "click_rate"
            ],
            bounce_rate=analytics[
                "bounce_rate"
            ],
            complaint_rate=analytics[
                "complaint_rate"
            ],
            unsubscribe_rate=analytics[
                "unsubscribe_rate"
            ],
        )

    except AIServiceError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "AI analysis service is "
                "temporarily unavailable."
            ),
        ) from error