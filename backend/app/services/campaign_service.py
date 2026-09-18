from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.user import User


def create_campaign(
    db: Session,
    current_user: User,
    title: str,
    subject: str,
    preview_text: str | None,
    content: str,
    cta_text: str | None,
    cta_url: str | None,
    audience_description: str | None,
) -> Campaign:

    campaign = Campaign(
        owner_id=current_user.id,
        title=title,
        subject=subject,
        preview_text=preview_text,
        content=content,
        cta_text=cta_text,
        cta_url=cta_url,
        audience_description=audience_description,
        status="draft",
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return campaign


def get_campaigns(
    db: Session,
    current_user: User,
) -> list[Campaign]:

    return list(
        db.scalars(
            select(Campaign)
            .where(
                Campaign.owner_id == current_user.id,
            )
            .order_by(
                Campaign.created_at.desc(),
            )
        )
    )


def get_campaign(
    db: Session,
    current_user: User,
    campaign_id: int,
) -> Campaign:

    campaign = db.scalar(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.owner_id == current_user.id,
        )
    )

    if campaign is None:
        raise ValueError("Campaign not found")

    return campaign


def update_campaign(
    db: Session,
    current_user: User,
    campaign_id: int,
    title: str | None = None,
    subject: str | None = None,
    preview_text: str | None = None,
    content: str | None = None,
    cta_text: str | None = None,
    cta_url: str | None = None,
    audience_description: str | None = None,
) -> Campaign:

    campaign = get_campaign(
        db=db,
        current_user=current_user,
        campaign_id=campaign_id,
    )

    if campaign.status not in {"draft", "failed"}:
        raise ValueError(
            "Only draft or failed campaigns can be edited"
        )

    if title is not None:
        campaign.title = title

    if subject is not None:
        campaign.subject = subject

    if preview_text is not None:
        campaign.preview_text = preview_text

    if content is not None:
        campaign.content = content

    if cta_text is not None:
        campaign.cta_text = cta_text

    if cta_url is not None:
        campaign.cta_url = cta_url

    if audience_description is not None:
        campaign.audience_description = (
            audience_description
        )

    db.commit()
    db.refresh(campaign)

    return campaign


def delete_campaign(
    db: Session,
    current_user: User,
    campaign_id: int,
) -> None:

    campaign = get_campaign(
        db=db,
        current_user=current_user,
        campaign_id=campaign_id,
    )

    if campaign.status not in {"draft", "failed"}:
        raise ValueError(
            "Only draft or failed campaigns can be deleted"
        )

    db.delete(campaign)
    db.commit()