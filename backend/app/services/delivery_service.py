from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.campaign_delivery import (
    CampaignDelivery,
)


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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_utc(
    value: datetime,
) -> datetime:
    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def _message_id_variants(
    provider_message_id: str,
) -> list[str]:
    """
    Return common representations of a message ID.

    Some systems preserve angle brackets around an RFC
    Message-ID while another layer may omit them.
    """

    raw = str(
        provider_message_id
    ).strip()

    if not raw:
        return []

    variants = [raw]

    if (
        raw.startswith("<")
        and raw.endswith(">")
        and len(raw) > 2
    ):
        without_brackets = raw[1:-1].strip()

        if without_brackets:
            variants.append(
                without_brackets
            )
    else:
        variants.append(
            f"<{raw}>"
        )

    return list(
        dict.fromkeys(variants)
    )


def _find_delivery_by_message_id(
    db: Session,
    provider_message_id: str,
) -> CampaignDelivery | None:
    """
    Find a delivery using both the exact provider ID
    and the common bracketed/unbracketed representation.
    """

    variants = _message_id_variants(
        provider_message_id
    )

    if not variants:
        return None

    return db.scalar(
        select(CampaignDelivery).where(
            CampaignDelivery.provider_message_id.in_(
                variants
            )
        )
    )


def create_delivery_records(
    db: Session,
    campaign_id: int,
    subscriber_ids: list[int],
) -> list[CampaignDelivery]:
    """
    Create one delivery record per subscriber.

    Duplicate campaign/subscriber combinations
    are skipped.
    """

    if not subscriber_ids:
        return []

    unique_subscriber_ids = list(
        dict.fromkeys(
            subscriber_ids
        )
    )

    existing_ids = set(
        db.scalars(
            select(
                CampaignDelivery.subscriber_id
            ).where(
                CampaignDelivery.campaign_id
                == campaign_id,
                CampaignDelivery.subscriber_id.in_(
                    unique_subscriber_ids
                ),
            )
        )
    )

    now = _utc_now()

    deliveries: list[
        CampaignDelivery
    ] = []

    for subscriber_id in unique_subscriber_ids:
        if subscriber_id in existing_ids:
            continue

        delivery = CampaignDelivery(
            campaign_id=campaign_id,
            subscriber_id=subscriber_id,
            provider="brevo",
            status="pending",
            attempt_count=0,
            queued_at=now,
        )

        db.add(delivery)
        deliveries.append(delivery)

    if deliveries:
        db.commit()

        for delivery in deliveries:
            db.refresh(delivery)

    return deliveries


def mark_delivery_queued(
    db: Session,
    delivery: CampaignDelivery,
) -> CampaignDelivery:
    """
    Mark a delivery as waiting in the background queue.
    """

    if delivery.queued_at is None:
        delivery.queued_at = _utc_now()

    delivery.status = "queued"

    db.commit()
    db.refresh(delivery)

    return delivery


def mark_delivery_sending(
    db: Session,
    delivery: CampaignDelivery,
) -> CampaignDelivery:
    """
    Mark a delivery as actively being sent.
    """

    delivery.status = "sending"
    delivery.attempt_count += 1

    db.commit()
    db.refresh(delivery)

    return delivery


def mark_delivery_sent(
    db: Session,
    delivery: CampaignDelivery,
    provider_message_id: str,
) -> CampaignDelivery:
    """
    Mark the email as accepted by Brevo.
    """

    now = _utc_now()

    normalized_id = str(
        provider_message_id
    ).strip()

    delivery.status = "sent"
    delivery.provider_message_id = (
        normalized_id
    )
    delivery.sent_at = now
    delivery.last_event_at = now
    delivery.error_message = None

    db.commit()
    db.refresh(delivery)

    return delivery


def mark_delivery_failed(
    db: Session,
    delivery: CampaignDelivery,
    error_message: str,
) -> CampaignDelivery:
    """
    Mark a delivery as permanently failed after retries.
    """

    now = _utc_now()

    delivery.status = "failed"
    delivery.error_message = (
        error_message
    )
    delivery.failed_at = now
    delivery.last_event_at = now

    db.commit()
    db.refresh(delivery)

    return delivery


def update_delivery_from_event(
    db: Session,
    *,
    provider_message_id: str,
    event: str,
    event_time: datetime,
) -> CampaignDelivery | None:
    """
    Update delivery state from a Brevo webhook event.

    Event handling is intentionally idempotent:
    receiving the same webhook multiple times will not
    create additional delivery records.
    """

    delivery = (
        _find_delivery_by_message_id(
            db=db,
            provider_message_id=provider_message_id,
        )
    )

    if delivery is None:
        return None

    event_time = _ensure_utc(
        event_time
    )

    normalized_event = (
        str(event).strip()
    )

    event_key = (
        normalized_event.lower()
    )

    delivery.last_event_at = event_time

    # Sent/request
    if event_key in {
        "request",
        "sent",
    }:
        if delivery.sent_at is None:
            delivery.sent_at = event_time

        if delivery.status in {
            "pending",
            "queued",
            "sending",
            "failed",
        }:
            delivery.status = "sent"

    # Delivered
    elif event_key == "delivered":
        if delivery.delivered_at is None:
            delivery.delivered_at = (
                event_time
            )

        if delivery.status not in {
            "opened",
            "clicked",
            "bounced",
            "complained",
            "unsubscribed",
        }:
            delivery.status = (
                "delivered"
            )

    # Opened
    elif event_key in {
        "opened",
        "uniqueopened",
        "unique_opened",
        "firstopening",
        "first_opening",
        "proxyopen",
        "proxy_open",
        "uniqueproxyopen",
        "unique_proxy_open",
    }:
        if delivery.opened_at is None:
            delivery.opened_at = (
                event_time
            )

        if delivery.status not in {
            "clicked",
            "bounced",
            "complained",
            "unsubscribed",
        }:
            delivery.status = "opened"

    # Clicked
    elif event_key in {
        "click",
        "clicked",
    }:
        if delivery.clicked_at is None:
            delivery.clicked_at = (
                event_time
            )

        delivery.status = "clicked"

    # Bounce / blocked / invalid / deferred / error
    elif event_key in {
        "hardbounce",
        "hard_bounce",
        "softbounce",
        "soft_bounce",
        "blocked",
        "invalid",
        "invalid_email",
        "deferred",
        "error",
    }:
        if delivery.bounced_at is None:
            delivery.bounced_at = (
                event_time
            )

        delivery.status = "bounced"

    # Complaint / spam
    elif event_key in {
        "spam",
        "complaint",
    }:
        if delivery.complained_at is None:
            delivery.complained_at = (
                event_time
            )

        delivery.status = "complained"

    # Unsubscribe
    elif event_key in {
        "unsubscribed",
        "unsubscribe",
    }:
        if delivery.unsubscribed_at is None:
            delivery.unsubscribed_at = (
                event_time
            )

        delivery.status = "unsubscribed"

    else:
        # Unknown but valid webhook event.
        # Keep the record untouched apart from
        # last_event_at.
        db.commit()
        db.refresh(delivery)

        return delivery

    db.commit()
    db.refresh(delivery)

    return delivery