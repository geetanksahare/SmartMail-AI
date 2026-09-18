import asyncio

from celery import Task

from app.celery_app import celery_app
from app.database.session import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_delivery import CampaignDelivery
from app.models.subscriber import Subscriber
from app.services.campaign_send_service import (
    claim_delivery_for_sending,
    finalize_campaign_if_complete,
    prepare_campaign_deliveries,
)
from app.services.delivery_service import (
    mark_delivery_failed,
    mark_delivery_queued,
    mark_delivery_sent,
)
from app.services.email.brevo_service import (
    EmailServiceError,
    send_email,
)
from sqlalchemy import select


class SmartMailTask(Task):
    """
    Base task configuration for SmartMail background jobs.
    """

    autoretry_for = ()
    max_retries = 0


@celery_app.task(
    bind=True,
    base=SmartMailTask,
    name="smartmail.dispatch_campaign",
)
def dispatch_campaign(
    self,
    campaign_id: int,
) -> dict:
    """
    Create/reuse campaign delivery records and queue one Celery
    task per eligible delivery.
    """

    db = SessionLocal()

    try:
        campaign = db.scalar(
            select(Campaign).where(
                Campaign.id == campaign_id
            )
        )

        if campaign is None:
            return {
                "campaign_id": campaign_id,
                "status": "not_found",
            }

        if campaign.status != "sending":
            return {
                "campaign_id": campaign_id,
                "status": campaign.status,
                "queued": 0,
            }

        deliveries = prepare_campaign_deliveries(
            db=db,
            campaign=campaign,
        )

        if not deliveries:
            campaign.status = "draft"
            campaign.sent_at = None

            db.commit()

            return {
                "campaign_id": campaign_id,
                "status": "no_active_subscribers",
                "queued": 0,
            }

        queued_count = 0

        for delivery in deliveries:
            if delivery.status == "pending":
                mark_delivery_queued(
                    db=db,
                    delivery=delivery,
                )

            send_campaign_delivery.apply_async(
                args=[delivery.id],
                task_id=(
                    f"campaign-delivery-"
                    f"{delivery.id}"
                ),
            )

            queued_count += 1

        return {
            "campaign_id": campaign_id,
            "status": "queued",
            "queued": queued_count,
        }

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=SmartMailTask,
    name="smartmail.send_campaign_delivery",
)
def send_campaign_delivery(
    self,
    delivery_id: int,
) -> dict:
    """
    Send one campaign delivery through Brevo.

    The delivery is atomically claimed so duplicate Celery
    messages cannot send the same email simultaneously.
    """

    db = SessionLocal()

    try:
        delivery = claim_delivery_for_sending(
            db=db,
            delivery_id=delivery_id,
        )

        if delivery is None:
            return {
                "delivery_id": delivery_id,
                "status": "not_found",
            }

        # Another task may already have completed this delivery.
        if delivery.status != "sending":
            return {
                "delivery_id": delivery_id,
                "status": delivery.status,
            }

        campaign = db.scalar(
            select(Campaign).where(
                Campaign.id == delivery.campaign_id
            )
        )

        subscriber = db.scalar(
            select(Subscriber).where(
                Subscriber.id == delivery.subscriber_id
            )
        )

        if campaign is None or subscriber is None:
            mark_delivery_failed(
                db=db,
                delivery=delivery,
                error_message=(
                    "Campaign or subscriber record "
                    "was not found."
                ),
            )

            finalize_campaign_if_complete(
                db=db,
                campaign_id=delivery.campaign_id,
            )

            return {
                "delivery_id": delivery_id,
                "status": "failed",
            }

        if subscriber.status != "active":
            mark_delivery_failed(
                db=db,
                delivery=delivery,
                error_message=(
                    "Subscriber is no longer active."
                ),
            )

            finalize_campaign_if_complete(
                db=db,
                campaign_id=delivery.campaign_id,
            )

            return {
                "delivery_id": delivery_id,
                "status": "failed",
            }

        try:
            provider_message_id = asyncio.run(
                send_email(
                    to_email=subscriber.email,
                    to_name=subscriber.name,
                    subject=campaign.subject,
                    preview_text=campaign.preview_text,
                    content=campaign.content,
                    cta_text=campaign.cta_text,
                    cta_url=campaign.cta_url,
                )
            )

        except EmailServiceError as error:
            if (
                error.retryable
                and self.request.retries < 2
            ):
                delivery.status = "queued"
                db.commit()

                raise self.retry(
                    exc=error,
                    countdown=(
                        2 ** self.request.retries
                    ),
                )

            mark_delivery_failed(
                db=db,
                delivery=delivery,
                error_message=str(error),
            )

            finalize_campaign_if_complete(
                db=db,
                campaign_id=delivery.campaign_id,
            )

            return {
                "delivery_id": delivery_id,
                "status": "failed",
            }

        mark_delivery_sent(
            db=db,
            delivery=delivery,
            provider_message_id=provider_message_id,
        )

        finalize_campaign_if_complete(
            db=db,
            campaign_id=delivery.campaign_id,
        )

        return {
            "delivery_id": delivery_id,
            "status": "sent",
            "provider_message_id": provider_message_id,
        }

    finally:
        db.close()