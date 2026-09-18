from pydantic import BaseModel, Field


class CampaignAnalyticsResponse(BaseModel):
    campaign_id: int

    total_recipients: int

    sent: int
    delivered: int
    opened: int
    clicked: int
    bounced: int
    complained: int
    unsubscribed: int
    failed: int

    delivery_rate: float = Field(
        ge=0,
        le=100,
    )

    open_rate: float = Field(
        ge=0,
        le=100,
    )

    click_rate: float = Field(
        ge=0,
        le=100,
    )

    bounce_rate: float = Field(
        ge=0,
        le=100,
    )

    complaint_rate: float = Field(
        ge=0,
        le=100,
    )

    unsubscribe_rate: float = Field(
        ge=0,
        le=100,
    )