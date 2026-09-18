from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CampaignStatus = Literal[
    "draft",
    "scheduled",
    "sending",
    "sent",
    "failed",
]


class CampaignCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=150,
    )

    subject: str = Field(
        min_length=1,
        max_length=255,
    )

    preview_text: str | None = Field(
        default=None,
        max_length=300,
    )

    content: str = Field(
        min_length=1,
    )

    cta_text: str | None = Field(
        default=None,
        max_length=150,
    )

    cta_url: str | None = Field(
        default=None,
        max_length=500,
    )

    audience_description: str | None = Field(
        default=None,
        max_length=200,
    )


class CampaignUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    subject: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    preview_text: str | None = Field(
        default=None,
        max_length=300,
    )

    content: str | None = Field(
        default=None,
        min_length=1,
    )

    cta_text: str | None = Field(
        default=None,
        max_length=150,
    )

    cta_url: str | None = Field(
        default=None,
        max_length=500,
    )

    audience_description: str | None = Field(
        default=None,
        max_length=200,
    )


class CampaignResponse(BaseModel):
    id: int
    title: str
    subject: str
    preview_text: str | None
    content: str
    cta_text: str | None
    cta_url: str | None
    audience_description: str | None
    status: CampaignStatus
    scheduled_at: datetime | None
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class CampaignSendResponse(BaseModel):
    message: str
    campaign_id: int
    task_id: str
    status: CampaignStatus