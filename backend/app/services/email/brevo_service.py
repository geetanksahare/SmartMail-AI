from typing import Any

import httpx

from app.core.config import settings
from app.services.email.renderer import (
    render_newsletter_email,
)


BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


class EmailServiceError(Exception):
    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)

        self.retryable = retryable
        self.status_code = status_code


async def send_email(
    *,
    to_email: str,
    to_name: str | None,
    subject: str,
    preview_text: str | None,
    content: str,
    cta_text: str | None = None,
    cta_url: str | None = None,
) -> str:

    html_content = render_newsletter_email(
        preview_text=preview_text,
        content=content,
        cta_text=cta_text,
        cta_url=cta_url,
    )

    payload: dict[str, Any] = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {
                "email": to_email,
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
    }

    if to_name:
        payload["to"][0]["name"] = to_name

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:
            response = await client.post(
                BREVO_SEND_URL,
                json=payload,
                headers=headers,
            )

    except (
        httpx.TimeoutException,
        httpx.NetworkError,
    ) as error:
        raise EmailServiceError(
            "Unable to connect to Brevo.",
            retryable=True,
        ) from error

    if response.status_code in {
        429,
        500,
        502,
        503,
        504,
    }:
        raise EmailServiceError(
            f"Brevo temporary error: "
            f"{response.status_code}",
            retryable=True,
            status_code=response.status_code,
        )

    if response.status_code >= 400:
        try:
            error_data = response.json()
            message = error_data.get(
                "message",
                "Brevo request failed.",
            )
        except ValueError:
            message = "Brevo request failed."

        raise EmailServiceError(
            message,
            retryable=False,
            status_code=response.status_code,
        )

    try:
        data = response.json()
    except ValueError as error:
        raise EmailServiceError(
            "Brevo returned an invalid response.",
            retryable=False,
        ) from error

    message_id = data.get("messageId")

    if not message_id:
        raise EmailServiceError(
            "Brevo did not return a messageId.",
            retryable=False,
        )

    return message_id