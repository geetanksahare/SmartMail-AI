from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.email import TestEmailResponse
from app.services.email.brevo_service import (
    EmailServiceError,
    send_email,
)


router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


@router.post(
    "/test",
    response_model=TestEmailResponse,
)
async def test_email(
    current_user: CurrentUser,
):
    try:
        message_id = await send_email(
            to_email=settings.EMAIL_TEST_RECIPIENT,
            to_name=current_user.name,
            subject="SmartMail AI Test Email",
            preview_text=(
                "Your Brevo email integration is working."
            ),
            content=(
                "Congratulations!\n\n"
                "Your SmartMail AI backend successfully "
                "connected to Brevo.\n\n"
                "This email was sent through the final "
                "SmartMail AI email service."
            ),
        )

        return {
            "message": "Test email sent successfully.",
            "message_id": message_id,
        }

    except EmailServiceError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
                if error.retryable
                else status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error