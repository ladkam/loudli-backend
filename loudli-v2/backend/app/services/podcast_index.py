import hashlib
import time
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()

PODCAST_INDEX_BASE_URL = "https://api.podcastindex.org/api/1.0"


def _get_auth_headers() -> dict[str, str]:
    """Generate authentication headers for Podcast Index API."""
    if not settings.PODCAST_INDEX_API_KEY or not settings.PODCAST_INDEX_API_SECRET:
        raise ValueError("Podcast Index API credentials not configured")

    api_key = settings.PODCAST_INDEX_API_KEY
    api_secret = settings.PODCAST_INDEX_API_SECRET
    epoch_time = str(int(time.time()))

    # Create the authorization hash
    data_to_hash = api_key + api_secret + epoch_time
    sha1_hash = hashlib.sha1(data_to_hash.encode()).hexdigest()

    return {
        "X-Auth-Key": api_key,
        "X-Auth-Date": epoch_time,
        "Authorization": sha1_hash,
        "User-Agent": "Loudli/2.0",
    }


async def search_podcasts(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    """Search for podcasts by term."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PODCAST_INDEX_BASE_URL}/search/byterm",
            params={"q": query, "max": max_results},
            headers=_get_auth_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        podcasts = []
        for feed in data.get("feeds", []):
            podcasts.append({
                "id": feed.get("id"),
                "title": feed.get("title"),
                "description": feed.get("description"),
                "author": feed.get("author"),
                "image_url": feed.get("image"),
                "rss_feed_url": feed.get("url"),
                "website_url": feed.get("link"),
                "language": feed.get("language"),
                "categories": list(feed.get("categories", {}).values()),
                "episode_count": feed.get("episodeCount"),
            })
        return podcasts


async def get_podcast_by_id(podcast_index_id: int) -> dict[str, Any] | None:
    """Get podcast details by Podcast Index ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PODCAST_INDEX_BASE_URL}/podcasts/byfeedid",
            params={"id": podcast_index_id},
            headers=_get_auth_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        feed = data.get("feed")
        if not feed:
            return None

        return {
            "id": feed.get("id"),
            "title": feed.get("title"),
            "description": feed.get("description"),
            "author": feed.get("author"),
            "image_url": feed.get("image"),
            "rss_feed_url": feed.get("url"),
            "website_url": feed.get("link"),
            "language": feed.get("language"),
            "categories": list(feed.get("categories", {}).values()),
            "episode_count": feed.get("episodeCount"),
        }


async def get_episodes_by_podcast_id(
    podcast_index_id: int, max_results: int = 50
) -> list[dict[str, Any]]:
    """Get episodes for a podcast by Podcast Index ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PODCAST_INDEX_BASE_URL}/episodes/byfeedid",
            params={"id": podcast_index_id, "max": max_results},
            headers=_get_auth_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        episodes = []
        for item in data.get("items", []):
            episodes.append({
                "guid": item.get("guid"),
                "title": item.get("title"),
                "description": item.get("description"),
                "audio_url": item.get("enclosureUrl"),
                "duration_seconds": item.get("duration"),
                "file_size_bytes": item.get("enclosureLength"),
                "published_at": item.get("datePublished"),
                "episode_number": item.get("episode"),
                "season_number": item.get("season"),
            })
        return episodes


async def get_trending_podcasts(
    max_results: int = 20, language: str | None = None
) -> list[dict[str, Any]]:
    """Get trending podcasts."""
    async with httpx.AsyncClient() as client:
        params = {"max": max_results}
        if language:
            params["lang"] = language

        response = await client.get(
            f"{PODCAST_INDEX_BASE_URL}/podcasts/trending",
            params=params,
            headers=_get_auth_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        podcasts = []
        for feed in data.get("feeds", []):
            podcasts.append({
                "id": feed.get("id"),
                "title": feed.get("title"),
                "description": feed.get("description"),
                "author": feed.get("author"),
                "image_url": feed.get("image"),
                "rss_feed_url": feed.get("url"),
                "website_url": feed.get("link"),
                "language": feed.get("language"),
                "categories": list(feed.get("categories", {}).values()),
                "episode_count": feed.get("episodeCount"),
                "trend_score": feed.get("trendScore"),
            })
        return podcasts


async def get_podcast_by_feed_url(feed_url: str) -> dict[str, Any] | None:
    """Get podcast details by RSS feed URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PODCAST_INDEX_BASE_URL}/podcasts/byfeedurl",
            params={"url": feed_url},
            headers=_get_auth_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        feed = data.get("feed")
        if not feed:
            return None

        return {
            "id": feed.get("id"),
            "title": feed.get("title"),
            "description": feed.get("description"),
            "author": feed.get("author"),
            "image_url": feed.get("image"),
            "rss_feed_url": feed.get("url"),
            "website_url": feed.get("link"),
            "language": feed.get("language"),
            "categories": list(feed.get("categories", {}).values()),
            "episode_count": feed.get("episodeCount"),
        }
