from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_delivery import CampaignDelivery
from app.models.subscriber import Subscriber


SUCCESS_STATUSES = {
    "sent",
    "delivered",
    "opened",
    "clicked",
}


TERMINAL_STATUSES = {
    "sent",
    "delivered",
    "opened",
    "clicked",
    "bounced",
    "complained",
    "unsubscribed",
    "failed",
}


SENDABLE_CAMPAIGN_STATUSES = {
    "draft",
    "failed",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def claim_campaign_for_sending(
    db: Session,
    *,
    campaign_id: int,
    owner_id: int,
) -> Campaign | None:
    """
    Atomically move a campaign from draft/failed to sending.

    Only one concurrent request can successfully claim the
    campaign because the UPDATE includes the current state
    in its WHERE clause.
    """

    now = _utc_now()

    result = db.execute(
        update(Campaign)
        .where(
            Campaign.id == campaign_id,
            Campaign.owner_id == owner_id,
            Campaign.status.in_(
                SENDABLE_CAMPAIGN_STATUSES
            ),
        )
        .values(
            status="sending",
            sent_at=None,
            updated_at=now,
        )
    )

    if result.rowcount != 1:
        db.rollback()
        return None

    db.commit()

    campaign = db.scalar(
        select(Campaign).where(
            Campaign.id == campaign_id
        )
    )

    return campaign


def reset_campaign_to_draft(
    db: Session,
    *,
    campaign_id: int,
) -> Campaign | None:
    """
    Return a campaign to draft if queueing fails before any
    delivery jobs are successfully scheduled.
    """

    campaign = db.scalar(
        select(Campaign).where(
            Campaign.id == campaign_id
        )
    )

    if campaign is None:
        return None

    if campaign.status != "sending":
        return campaign

    campaign.status = "draft"
    campaign.sent_at = None

    db.commit()
    db.refresh(campaign)

    return campaign


def prepare_campaign_deliveries(
    db: Session,
    campaign: Campaign,
) -> list[CampaignDelivery]:
    """
    Find active subscribers and create delivery records.

    Existing delivery records are reused.

    Failed deliveries are reset for another campaign attempt.
    Delivery records that are already pending, queued, sending,
    sent, delivered, opened, clicked, bounced, complained, or
    unsubscribed are not duplicated.
    """

    subscribers = list(
        db.scalars(
            select(Subscriber)
            .where(
                Subscriber.owner_id == campaign.owner_id,
                Subscriber.status == "active",
            )
            .order_by(
                Subscriber.id
            )
        )
    )

    if not subscribers:
        return []

    subscriber_ids = [
        subscriber.id
        for subscriber in subscribers
    ]

    existing_deliveries = list(
        db.scalars(
            select(CampaignDelivery).where(
                CampaignDelivery.campaign_id
                == campaign.id,
                CampaignDelivery.subscriber_id.in_(
                    subscriber_ids
                ),
            )
        )
    )

    existing_map = {
        delivery.subscriber_id: delivery
        for delivery in existing_deliveries
    }

    deliveries_to_queue: list[CampaignDelivery] = []

    for subscriber in subscribers:
        existing = existing_map.get(
            subscriber.id
        )

        if existing is None:
            delivery = CampaignDelivery(
                campaign_id=campaign.id,
                subscriber_id=subscriber.id,
                provider="brevo",
                status="pending",
                attempt_count=0,
                queued_at=_utc_now(),
            )

            db.add(delivery)
            deliveries_to_queue.append(delivery)

            continue

        # A failed delivery is eligible for another attempt.
        if existing.status == "failed":
            existing.status = "pending"
            existing.provider_message_id = None
            existing.error_message = None
            existing.queued_at = _utc_now()
            existing.sent_at = None
            existing.failed_at = None

            deliveries_to_queue.append(existing)

        # Existing pending/queued records are already part of
        # the current campaign send process.
        elif existing.status in {
            "pending",
            "queued",
        }:
            deliveries_to_queue.append(existing)

    if deliveries_to_queue:
        db.commit()

        for delivery in deliveries_to_queue:
            db.refresh(delivery)

    return deliveries_to_queue


def claim_delivery_for_sending(
    db: Session,
    *,
    delivery_id: int,
) -> CampaignDelivery | None:
    """
    Atomically claim a delivery for one Celery task.

    If two Celery tasks receive the same delivery ID, only the
    first task can transition it into 'sending'.
    """

    result = db.execute(
        update(CampaignDelivery)
        .where(
            CampaignDelivery.id == delivery_id,
            CampaignDelivery.status.in_(
                {
                    "pending",
                    "queued",
                }
            ),
        )
        .values(
            status="sending",
            attempt_count=(
                CampaignDelivery.attempt_count + 1
            ),
        )
    )

    if result.rowcount != 1:
        db.rollback()

        return db.scalar(
            select(CampaignDelivery).where(
                CampaignDelivery.id == delivery_id
            )
        )

    db.commit()

    return db.scalar(
        select(CampaignDelivery).where(
            CampaignDelivery.id == delivery_id
        )
    )


def campaign_is_complete(
    db: Session,
    campaign_id: int,
) -> bool:
    """
    A campaign is complete when all its delivery records are
    in terminal states.
    """

    deliveries = list(
        db.scalars(
            select(CampaignDelivery).where(
                CampaignDelivery.campaign_id
                == campaign_id
            )
        )
    )

    if not deliveries:
        return False

    return all(
        delivery.status in TERMINAL_STATUSES
        for delivery in deliveries
    )


def finalize_campaign_if_complete(
    db: Session,
    campaign_id: int,
) -> Campaign | None:
    """
    Finalize a campaign once every delivery reaches a terminal
    state.

    If at least one delivery succeeded, the campaign becomes
    sent. Otherwise it becomes failed.
    """

    campaign = db.scalar(
        select(Campaign).where(
            Campaign.id == campaign_id
        )
    )

    if campaign is None:
        return None

    if campaign.status != "sending":
        return campaign

    if not campaign_is_complete(
        db=db,
        campaign_id=campaign_id,
    ):
        return campaign

    deliveries = list(
        db.scalars(
            select(CampaignDelivery).where(
                CampaignDelivery.campaign_id
                == campaign_id
            )
        )
    )

    successful_count = sum(
        1
        for delivery in deliveries
        if delivery.status in SUCCESS_STATUSES
    )

    if successful_count > 0:
        campaign.status = "sent"
        campaign.sent_at = _utc_now()
    else:
        campaign.status = "failed"

    db.commit()
    db.refresh(campaign)

    return campaign