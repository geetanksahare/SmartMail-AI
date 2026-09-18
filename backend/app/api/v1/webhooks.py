from datetime import datetime, timezone
import secrets
from typing import Any

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Request,
    status,
)

from app.core.config import settings
from app.database.session import SessionLocal
from app.services.campaign_send_service import (
    finalize_campaign_if_complete,
)
from app.services.delivery_service import (
    update_delivery_from_event,
)


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


def _parse_event_time(
    payload: dict[str, Any],
) -> datetime:
    """
    Convert Brevo's webhook timestamp into UTC.

    Brevo commonly provides:
    - ts_event
    - ts
    - ts_epoch
    """

    for key, divisor in (
        ("ts_event", 1),
        ("ts", 1),
        ("ts_epoch", 1000),
    ):
        value = payload.get(key)

        if value is None:
            continue

        try:
            return datetime.fromtimestamp(
                float(value) / divisor,
                tz=timezone.utc,
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            continue

    return datetime.now(timezone.utc)


def _extract_message_id(
    payload: dict[str, Any],
) -> str | None:
    """
    Extract Brevo's message identifier.

    Brevo documents `message-id`; several aliases
    are accepted defensively.
    """

    possible_keys = (
        "message-id",
        "messageId",
        "message_id",
        "messageID",
        "smtp-id",
        "smtpId",
    )

    for key in possible_keys:
        value = payload.get(key)

        if value is None:
            continue

        value = str(value).strip()

        if value:
            return value

    return None


def _extract_event(
    payload: dict[str, Any],
) -> str | None:
    """
    Extract the webhook event name.

    `event` is the official Brevo field.
    event_name/status are tolerated as fallbacks.
    """

    possible_keys = (
        "event",
        "event_name",
        "eventName",
        "status",
    )

    for key in possible_keys:
        value = payload.get(key)

        if value is None:
            continue

        value = str(value).strip()

        if value:
            return value

    return None


def _authorization_is_valid(
    authorization: str | None,
) -> bool:
    """
    Validate a Bearer token using constant-time comparison.
    """

    expected_token = (
        settings.BREVO_WEBHOOK_TOKEN or ""
    ).strip()

    if not expected_token:
        return False

    if not authorization:
        return False

    parts = authorization.strip().split(
        maxsplit=1
    )

    if len(parts) != 2:
        return False

    scheme, provided_token = parts

    if scheme.lower() != "bearer":
        return False

    provided_token = provided_token.strip()

    return secrets.compare_digest(
        provided_token,
        expected_token,
    )


def _normalize_payloads(
    body: Any,
) -> list[dict[str, Any]]:
    """
    Normalize both single-event and batched
    webhook bodies into a list of dictionaries.
    """

    if isinstance(body, dict):
        return [body]

    if isinstance(body, list):
        return [
            item
            for item in body
            if isinstance(item, dict)
        ]

    return []


@router.post(
    "/brevo",
    status_code=status.HTTP_200_OK,
)
async def brevo_webhook(
    request: Request,
    authorization: str | None = Header(
        default=None,
    ),
):
    """
    Receive Brevo transactional webhook events.

    The endpoint:
    - validates the configured Bearer token
    - accepts single or batched events
    - tolerates common Brevo field aliases
    - ignores malformed/unknown events safely
    - updates the matching delivery record
    - finalizes the campaign when appropriate
    """

    if not _authorization_is_valid(
        authorization
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook authorization.",
        )

    try:
        body = await request.json()
    except Exception:
        # Returning 200 prevents pointless retry loops for
        # malformed requests while keeping the webhook endpoint
        # resilient.
        return {
            "status": "ignored",
            "reason": "invalid_json",
        }

    payloads = _normalize_payloads(body)

    if not payloads:
        return {
            "status": "ignored",
            "reason": "unsupported_payload",
        }

    processed = 0
    ignored = 0
    results: list[dict[str, Any]] = []

    db = SessionLocal()

    try:
        for payload in payloads:
            event = _extract_event(payload)
            message_id = _extract_message_id(
                payload
            )

            # Do not throw 400s for events that cannot be
            # correlated. There is nothing useful we can do
            # with them, and retrying the same malformed payload
            # indefinitely does not help.
            if not event:
                ignored += 1

                results.append(
                    {
                        "status": "ignored",
                        "reason": "missing_event",
                    }
                )

                continue

            if not message_id:
                ignored += 1

                results.append(
                    {
                        "status": "ignored",
                        "reason": "missing_message_id",
                        "event": event,
                    }
                )

                continue

            event_time = _parse_event_time(
                payload
            )

            delivery = (
                update_delivery_from_event(
                    db=db,
                    provider_message_id=message_id,
                    event=event,
                    event_time=event_time,
                )
            )

            if delivery is None:
                # The provider event may belong to an older
                # campaign, a deleted record, or a message that
                # was sent before our local delivery record existed.
                ignored += 1

                results.append(
                    {
                        "status": "ignored",
                        "reason": "unknown_message_id",
                        "event": event,
                        "message_id": message_id,
                    }
                )

                continue

            finalize_campaign_if_complete(
                db=db,
                campaign_id=delivery.campaign_id,
            )

            processed += 1

            results.append(
                {
                    "status": "processed",
                    "event": event,
                    "message_id": message_id,
                    "delivery_id": delivery.id,
                }
            )

        return {
            "status": "processed",
            "processed": processed,
            "ignored": ignored,
            "results": results,
        }

    finally:
        db.close()