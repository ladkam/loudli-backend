from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String,
    DateTime,
    Text,
    ForeignKey,
    Integer,
    Enum,
    Numeric,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class MessageType(str, enum.Enum):
    TEXT = "text"
    AUDIO = "audio"
    FILE = "file"
    OFFER = "offer"
    SYSTEM = "system"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    advertiser_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    podcast_id: Mapped[int] = mapped_column(ForeignKey("podcasts.id"), index=True)

    # Campaign details
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True
    )

    # Budget and pricing
    budget: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_per_episode: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Campaign duration
    start_date: Mapped[datetime | None] = mapped_column(DateTime)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    episodes_count: Mapped[int | None] = mapped_column(Integer)

    # Targeting
    target_demographics: Mapped[str | None] = mapped_column(Text)  # JSON string

    # Stats
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    advertiser: Mapped["User"] = relationship(back_populates="campaigns")
    podcast: Mapped["Podcast"] = relationship(back_populates="campaigns")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    content: Mapped[str | None] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.TEXT
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # For offers
    offer_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    message_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"), index=True)

    filename: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(String(1000))
    file_type: Mapped[str | None] = mapped_column(String(100))
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="attachments")


# Import at the bottom to avoid circular imports
from app.models.user import User  # noqa: E402, F401
from app.models.podcast import Podcast  # noqa: E402, F401
