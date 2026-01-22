from datetime import datetime
from sqlalchemy import String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemSettings(Base):
    """Store system-wide settings like API keys"""
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str | None] = mapped_column(Text)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PodcasterAdvertiserMatch(Base):
    """Track recommended matches between podcasters and advertisers"""
    __tablename__ = "podcaster_advertiser_matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    podcast_id: Mapped[int] = mapped_column(index=True)
    advertiser_id: Mapped[int] = mapped_column(index=True)
    match_score: Mapped[float | None] = mapped_column()  # 0-100 compatibility score
    match_reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, sent, accepted, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
