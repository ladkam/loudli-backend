from datetime import datetime
from typing import Any

import feedparser
import httpx
from dateutil.parser import parse as parse_date


async def fetch_and_parse_rss(feed_url: str) -> dict[str, Any] | None:
    """Fetch and parse an RSS feed URL."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(feed_url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            content = response.text
    except httpx.HTTPError:
        return None

    feed = feedparser.parse(content)

    if feed.bozo and not feed.entries:
        return None

    channel = feed.feed

    podcast_data = {
        "title": channel.get("title"),
        "description": channel.get("description") or channel.get("summary"),
        "author": channel.get("author") or channel.get("itunes_author"),
        "website_url": channel.get("link"),
        "image_url": None,
        "language": channel.get("language"),
        "is_explicit": channel.get("itunes_explicit", "no").lower() in ("yes", "true"),
        "categories": [],
        "episodes": [],
    }

    # Get image
    if hasattr(channel, "image") and channel.image:
        podcast_data["image_url"] = channel.image.get("href")
    elif hasattr(channel, "itunes_image"):
        podcast_data["image_url"] = channel.itunes_image.get("href")

    # Get categories
    if hasattr(channel, "tags"):
        podcast_data["categories"] = [tag.term for tag in channel.tags if tag.term]

    # Parse episodes
    for entry in feed.entries:
        episode = {
            "guid": entry.get("id") or entry.get("guid"),
            "title": entry.get("title"),
            "description": entry.get("description") or entry.get("summary"),
            "audio_url": None,
            "duration_seconds": None,
            "file_size_bytes": None,
            "published_at": None,
            "episode_number": None,
            "season_number": None,
        }

        # Get audio URL from enclosures
        for enclosure in entry.get("enclosures", []):
            if enclosure.get("type", "").startswith("audio/"):
                episode["audio_url"] = enclosure.get("href") or enclosure.get("url")
                episode["file_size_bytes"] = (
                    int(enclosure.get("length")) if enclosure.get("length") else None
                )
                break

        # If no enclosure, try links
        if not episode["audio_url"]:
            for link in entry.get("links", []):
                if link.get("type", "").startswith("audio/"):
                    episode["audio_url"] = link.get("href")
                    break

        # Parse duration
        duration_str = entry.get("itunes_duration")
        if duration_str:
            episode["duration_seconds"] = _parse_duration(duration_str)

        # Parse published date
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            episode["published_at"] = datetime(*published[:6])
        elif entry.get("published"):
            try:
                episode["published_at"] = parse_date(entry.get("published"))
            except (ValueError, TypeError):
                pass

        # Episode/season numbers
        episode["episode_number"] = (
            int(entry.get("itunes_episode")) if entry.get("itunes_episode") else None
        )
        episode["season_number"] = (
            int(entry.get("itunes_season")) if entry.get("itunes_season") else None
        )

        if episode["audio_url"]:  # Only add episodes with audio
            podcast_data["episodes"].append(episode)

    return podcast_data


def _parse_duration(duration_str: str) -> int | None:
    """Parse duration string to seconds."""
    if not duration_str:
        return None

    try:
        # Try as integer (already in seconds)
        return int(duration_str)
    except ValueError:
        pass

    # Try HH:MM:SS or MM:SS format
    parts = duration_str.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        pass

    return None
