from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# Many-to-many relationship table for podcast categories
podcast_categories = Table(
    "podcast_categories",
    Base.metadata,
    Column("podcast_id", ForeignKey("podcasts.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    podcasts: Mapped[list["Podcast"]] = relationship(
        secondary=podcast_categories, back_populates="categories"
    )


class Podcast(Base):
    __tablename__ = "podcasts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    website_url: Mapped[str | None] = mapped_column(String(500))
    rss_feed_url: Mapped[str | None] = mapped_column(String(500))

    # External IDs
    podcast_index_id: Mapped[int | None] = mapped_column(Integer, index=True)
    itunes_id: Mapped[int | None] = mapped_column(Integer, index=True)

    # Stats
    total_episodes: Mapped[int] = mapped_column(Integer, default=0)
    average_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    subscriber_count: Mapped[int | None] = mapped_column(Integer)

    # Metadata
    language: Mapped[str | None] = mapped_column(String(10))
    author: Mapped[str | None] = mapped_column(String(255))
    is_explicit: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_rss_sync: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="podcasts")
    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="podcast", cascade="all, delete-orphan"
    )
    categories: Mapped[list["Category"]] = relationship(
        secondary=podcast_categories, back_populates="podcasts"
    )
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="podcast")


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    podcast_id: Mapped[int] = mapped_column(ForeignKey("podcasts.id"), index=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    audio_url: Mapped[str] = mapped_column(String(1000))
    episode_number: Mapped[int | None] = mapped_column(Integer)
    season_number: Mapped[int | None] = mapped_column(Integer)

    # Duration and size
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)

    # External IDs
    guid: Mapped[str | None] = mapped_column(String(500), index=True)

    # Timestamps
    published_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    podcast: Mapped["Podcast"] = relationship(back_populates="episodes")


# Import at the bottom to avoid circular imports
from app.models.user import User  # noqa: E402, F401
from app.models.campaign import Campaign  # noqa: E402, F401
