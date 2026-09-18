from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.campaign_delivery import CampaignDelivery


def _percentage(
    numerator: int,
    denominator: int,
) -> float:
    if denominator <= 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        2,
    )


def get_campaign_analytics(
    db: Session,
    campaign_id: int,
) -> dict:
    sent_case = case(
        (
            CampaignDelivery.sent_at.is_not(None),
            1,
        ),
        else_=None,
    )

    delivered_case = case(
        (
            CampaignDelivery.delivered_at.is_not(None),
            1,
        ),
        else_=None,
    )

    opened_case = case(
        (
            CampaignDelivery.opened_at.is_not(None),
            1,
        ),
        else_=None,
    )

    clicked_case = case(
        (
            CampaignDelivery.clicked_at.is_not(None),
            1,
        ),
        else_=None,
    )

    bounced_case = case(
        (
            CampaignDelivery.bounced_at.is_not(None),
            1,
        ),
        else_=None,
    )

    complained_case = case(
        (
            CampaignDelivery.complained_at.is_not(None),
            1,
        ),
        else_=None,
    )

    unsubscribed_case = case(
        (
            CampaignDelivery.unsubscribed_at.is_not(None),
            1,
        ),
        else_=None,
    )

    failed_case = case(
        (
            CampaignDelivery.failed_at.is_not(None),
            1,
        ),
        else_=None,
    )

    statement = select(
        func.count(
            CampaignDelivery.id
        ).label("total_recipients"),

        func.count(
            sent_case
        ).label("sent"),

        func.count(
            delivered_case
        ).label("delivered"),

        func.count(
            opened_case
        ).label("opened"),

        func.count(
            clicked_case
        ).label("clicked"),

        func.count(
            bounced_case
        ).label("bounced"),

        func.count(
            complained_case
        ).label("complained"),

        func.count(
            unsubscribed_case
        ).label("unsubscribed"),

        func.count(
            failed_case
        ).label("failed"),
    ).where(
        CampaignDelivery.campaign_id == campaign_id
    )

    result = db.execute(statement).one()

    total_recipients = int(
        result.total_recipients or 0
    )

    sent = int(
        result.sent or 0
    )

    delivered = int(
        result.delivered or 0
    )

    opened = int(
        result.opened or 0
    )

    clicked = int(
        result.clicked or 0
    )

    bounced = int(
        result.bounced or 0
    )

    complained = int(
        result.complained or 0
    )

    unsubscribed = int(
        result.unsubscribed or 0
    )

    failed = int(
        result.failed or 0
    )

    return {
        "campaign_id": campaign_id,
        "total_recipients": total_recipients,
        "sent": sent,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "bounced": bounced,
        "complained": complained,
        "unsubscribed": unsubscribed,
        "failed": failed,

        "delivery_rate": _percentage(
            delivered,
            sent,
        ),

        "open_rate": _percentage(
            opened,
            delivered,
        ),

        "click_rate": _percentage(
            clicked,
            delivered,
        ),

        "bounce_rate": _percentage(
            bounced,
            sent,
        ),

        "complaint_rate": _percentage(
            complained,
            sent,
        ),

        "unsubscribe_rate": _percentage(
            unsubscribed,
            delivered,
        ),
    }