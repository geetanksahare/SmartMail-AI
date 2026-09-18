from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(
        String(150),
        nullable=False,
    )

    subject = Column(
        String(255),
        nullable=False,
    )

    preview_text = Column(
        String(300),
        nullable=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    cta_text = Column(
        String(150),
        nullable=True,
    )

    cta_url = Column(
        String(500),
        nullable=True,
    )

    audience_description = Column(
        String(200),
        nullable=True,
    )

    status = Column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
    )

    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sent_at = Column(
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