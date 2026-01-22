from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SystemSettings
from app.core.config import get_settings

env_settings = get_settings()

# Default settings keys
PODCAST_INDEX_API_KEY = "PODCAST_INDEX_API_KEY"
PODCAST_INDEX_API_SECRET = "PODCAST_INDEX_API_SECRET"


async def get_setting_value(db: AsyncSession, key: str, default: str | None = None) -> str | None:
    """Get a setting value from database, falling back to environment variable."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == key)
    )
    setting = result.scalar_one_or_none()

    if setting and setting.value:
        return setting.value

    # Fall back to environment variable
    env_value = getattr(env_settings, key, None)
    return env_value if env_value else default


async def get_podcast_index_credentials(db: AsyncSession) -> tuple[str | None, str | None]:
    """Get Podcast Index API credentials from database or environment."""
    api_key = await get_setting_value(db, PODCAST_INDEX_API_KEY)
    api_secret = await get_setting_value(db, PODCAST_INDEX_API_SECRET)
    return api_key, api_secret


async def initialize_default_settings(db: AsyncSession) -> None:
    """Initialize default settings if they don't exist."""
    default_settings = [
        {
            "key": PODCAST_INDEX_API_KEY,
            "value": env_settings.PODCAST_INDEX_API_KEY,
            "is_secret": True,
            "description": "Podcast Index API Key (get free at podcastindex.org)",
        },
        {
            "key": PODCAST_INDEX_API_SECRET,
            "value": env_settings.PODCAST_INDEX_API_SECRET,
            "is_secret": True,
            "description": "Podcast Index API Secret",
        },
    ]

    for setting_data in default_settings:
        result = await db.execute(
            select(SystemSettings).where(SystemSettings.key == setting_data["key"])
        )
        if not result.scalar_one_or_none():
            setting = SystemSettings(**setting_data)
            db.add(setting)

    await db.commit()
