from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


SubscriberStatus = Literal["active", "inactive"]


class SubscriberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class SubscriberUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    status: SubscriberStatus | None = None


class SubscriberResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    status: SubscriberStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriberListResponse(BaseModel):
    items: list[SubscriberResponse]
    page: int
    page_size: int
    total: int
    total_pages: int