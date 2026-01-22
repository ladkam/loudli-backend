from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl


class CategoryBase(BaseModel):
    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EpisodeBase(BaseModel):
    title: str
    description: str | None = None
    audio_url: str
    episode_number: int | None = None
    season_number: int | None = None
    duration_seconds: int | None = None


class EpisodeCreate(EpisodeBase):
    podcast_id: int


class EpisodeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    audio_url: str | None = None
    episode_number: int | None = None
    season_number: int | None = None


class Episode(EpisodeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    podcast_id: int
    guid: str | None = None
    file_size_bytes: int | None = None
    published_at: datetime | None = None
    created_at: datetime


class PodcastBase(BaseModel):
    title: str
    description: str | None = None
    website_url: str | None = None
    rss_feed_url: str | None = None
    language: str | None = None
    author: str | None = None
    is_explicit: bool = False


class PodcastCreate(PodcastBase):
    category_ids: list[int] | None = None


class PodcastUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    website_url: str | None = None
    rss_feed_url: str | None = None
    language: str | None = None
    author: str | None = None
    is_explicit: bool | None = None
    category_ids: list[int] | None = None


class Podcast(PodcastBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    cover_image_url: str | None = None
    podcast_index_id: int | None = None
    itunes_id: int | None = None
    total_episodes: int
    average_duration_seconds: int | None = None
    subscriber_count: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_rss_sync: datetime | None = None
    categories: list[Category] = []


class PodcastWithEpisodes(Podcast):
    episodes: list[Episode] = []


class PodcastSearchResult(BaseModel):
    """Schema for podcast search results from Podcast Index API"""

    id: int
    title: str
    description: str | None = None
    author: str | None = None
    image_url: str | None = None
    rss_feed_url: str | None = None
    website_url: str | None = None
    language: str | None = None
    categories: list[str] = []
    episode_count: int | None = None


class PodcastImportRequest(BaseModel):
    """Request to import a podcast from external source"""

    podcast_index_id: int | None = None
    rss_feed_url: str | None = None
