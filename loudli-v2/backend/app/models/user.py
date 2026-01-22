from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class UserType(str, enum.Enum):
    PODCASTER = "podcaster"
    ADVERTISER = "advertiser"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Profile info
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)
    podcasts: Mapped[list["Podcast"]] = relationship(back_populates="owner")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="advertiser")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), default=UserType.PODCASTER)

    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    company_name: Mapped[str | None] = mapped_column(String(200))
    bio: Mapped[str | None] = mapped_column(Text)
    profile_image_url: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(20))
    website: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="profile")


# Import at the bottom to avoid circular imports
from app.models.podcast import Podcast  # noqa: E402, F401
from app.models.campaign import Campaign  # noqa: E402, F401
