from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database.base import Base


class CampaignDelivery(Base):
    __tablename__ = "campaign_deliveries"

    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "subscriber_id",
            name="uq_campaign_delivery_campaign_subscriber",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    campaign_id = Column(
        Integer,
        ForeignKey(
            "campaigns.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    subscriber_id = Column(
        Integer,
        ForeignKey(
            "subscribers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    provider = Column(
        String(50),
        nullable=False,
        default="brevo",
    )

    provider_message_id = Column(
        String(500),
        nullable=True,
        unique=True,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    attempt_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    queued_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    opened_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    clicked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    bounced_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    complained_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    unsubscribed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_event_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )