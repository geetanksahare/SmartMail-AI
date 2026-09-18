from app.schemas.ai import AICampaignAnalysisResponse
from app.services.ai.manager import ai_manager
from app.utils.prompts import (
    build_campaign_analysis_system_prompt,
    build_campaign_analysis_user_prompt,
)


def analyze_campaign(
    *,
    title: str,
    subject: str,
    audience: str | None,
    total_recipients: int,
    sent: int,
    delivered: int,
    opened: int,
    clicked: int,
    bounced: int,
    complained: int,
    unsubscribed: int,
    failed: int,
    delivery_rate: float,
    open_rate: float,
    click_rate: float,
    bounce_rate: float,
    complaint_rate: float,
    unsubscribe_rate: float,
) -> AICampaignAnalysisResponse:

    system_prompt = (
        build_campaign_analysis_system_prompt()
    )

    user_prompt = (
        build_campaign_analysis_user_prompt(
            title=title,
            subject=subject,
            audience=audience,
            total_recipients=total_recipients,
            sent=sent,
            delivered=delivered,
            opened=opened,
            clicked=clicked,
            bounced=bounced,
            complained=complained,
            unsubscribed=unsubscribed,
            failed=failed,
            delivery_rate=delivery_rate,
            open_rate=open_rate,
            click_rate=click_rate,
            bounce_rate=bounce_rate,
            complaint_rate=complaint_rate,
            unsubscribe_rate=unsubscribe_rate,
        )
    )

    return ai_manager.generate_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=AICampaignAnalysisResponse,
    )