from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import DBSession, CurrentUser
from app.models import Podcast, Episode, Category
from app.schemas.podcast import (
    Podcast as PodcastSchema,
    PodcastCreate,
    PodcastUpdate,
    PodcastWithEpisodes,
    PodcastSearchResult,
    PodcastImportRequest,
    Episode as EpisodeSchema,
    EpisodeCreate,
    EpisodeUpdate,
    Category as CategorySchema,
    CategoryCreate,
)
from app.services import podcast_index, rss_parser

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


# ==================== Podcast Endpoints ====================


@router.get("", response_model=list[PodcastSchema])
async def list_podcasts(
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    search: str | None = None,
):
    """List all podcasts with pagination and optional filters."""
    query = select(Podcast).options(selectinload(Podcast.categories))

    if category_id:
        query = query.where(Podcast.categories.any(Category.id == category_id))

    if search:
        query = query.where(
            Podcast.title.ilike(f"%{search}%") | Podcast.description.ilike(f"%{search}%")
        )

    query = query.where(Podcast.is_active == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PodcastSchema, status_code=status.HTTP_201_CREATED)
async def create_podcast(
    podcast_in: PodcastCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new podcast."""
    podcast = Podcast(
        owner_id=current_user.id,
        title=podcast_in.title,
        description=podcast_in.description,
        website_url=podcast_in.website_url,
        rss_feed_url=podcast_in.rss_feed_url,
        language=podcast_in.language,
        author=podcast_in.author,
        is_explicit=podcast_in.is_explicit,
    )

    if podcast_in.category_ids:
        result = await db.execute(
            select(Category).where(Category.id.in_(podcast_in.category_ids))
        )
        categories = result.scalars().all()
        podcast.categories = list(categories)

    db.add(podcast)
    await db.commit()
    await db.refresh(podcast)
    return podcast


@router.get("/my", response_model=list[PodcastSchema])
async def list_my_podcasts(current_user: CurrentUser, db: DBSession):
    """List current user's podcasts."""
    result = await db.execute(
        select(Podcast)
        .options(selectinload(Podcast.categories))
        .where(Podcast.owner_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/search/external", response_model=list[PodcastSearchResult])
async def search_external_podcasts(
    query: str = Query(..., min_length=2),
    max_results: int = Query(20, ge=1, le=50),
):
    """Search podcasts from Podcast Index API."""
    try:
        results = await podcast_index.search_podcasts(query, max_results)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="External podcast search unavailable",
        )


@router.get("/trending", response_model=list[PodcastSearchResult])
async def get_trending_podcasts(
    max_results: int = Query(20, ge=1, le=50),
    language: str | None = None,
):
    """Get trending podcasts from Podcast Index API."""
    try:
        results = await podcast_index.get_trending_podcasts(max_results, language)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trending podcasts unavailable",
        )


@router.post("/import", response_model=PodcastSchema, status_code=status.HTTP_201_CREATED)
async def import_podcast(
    import_request: PodcastImportRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """Import a podcast from Podcast Index or RSS feed URL."""
    podcast_data = None

    if import_request.podcast_index_id:
        try:
            podcast_data = await podcast_index.get_podcast_by_id(
                import_request.podcast_index_id
            )
        except Exception:
            pass

    if not podcast_data and import_request.rss_feed_url:
        podcast_data = await rss_parser.fetch_and_parse_rss(import_request.rss_feed_url)

    if not podcast_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not fetch podcast data",
        )

    # Create podcast
    podcast = Podcast(
        owner_id=current_user.id,
        title=podcast_data.get("title", "Unknown"),
        description=podcast_data.get("description"),
        cover_image_url=podcast_data.get("image_url"),
        website_url=podcast_data.get("website_url"),
        rss_feed_url=import_request.rss_feed_url or podcast_data.get("rss_feed_url"),
        podcast_index_id=import_request.podcast_index_id or podcast_data.get("id"),
        language=podcast_data.get("language"),
        author=podcast_data.get("author"),
        is_explicit=podcast_data.get("is_explicit", False),
        last_rss_sync=datetime.utcnow(),
    )

    db.add(podcast)
    await db.flush()

    # Import episodes if available
    episodes = podcast_data.get("episodes", [])
    for ep_data in episodes[:50]:  # Limit to 50 episodes
        episode = Episode(
            podcast_id=podcast.id,
            guid=ep_data.get("guid"),
            title=ep_data.get("title", "Untitled"),
            description=ep_data.get("description"),
            audio_url=ep_data.get("audio_url"),
            duration_seconds=ep_data.get("duration_seconds"),
            file_size_bytes=ep_data.get("file_size_bytes"),
            published_at=ep_data.get("published_at"),
            episode_number=ep_data.get("episode_number"),
            season_number=ep_data.get("season_number"),
        )
        db.add(episode)

    podcast.total_episodes = len(episodes)

    await db.commit()
    await db.refresh(podcast)
    return podcast


@router.get("/{podcast_id}", response_model=PodcastWithEpisodes)
async def get_podcast(podcast_id: int, db: DBSession):
    """Get a podcast by ID with its episodes."""
    result = await db.execute(
        select(Podcast)
        .options(selectinload(Podcast.categories), selectinload(Podcast.episodes))
        .where(Podcast.id == podcast_id)
    )
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found",
        )
    return podcast


@router.patch("/{podcast_id}", response_model=PodcastSchema)
async def update_podcast(
    podcast_id: int,
    podcast_update: PodcastUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update a podcast."""
    result = await db.execute(
        select(Podcast).where(Podcast.id == podcast_id, Podcast.owner_id == current_user.id)
    )
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found or you don't have permission",
        )

    update_data = podcast_update.model_dump(exclude_unset=True, exclude={"category_ids"})
    for field, value in update_data.items():
        setattr(podcast, field, value)

    if podcast_update.category_ids is not None:
        result = await db.execute(
            select(Category).where(Category.id.in_(podcast_update.category_ids))
        )
        categories = result.scalars().all()
        podcast.categories = list(categories)

    await db.commit()
    await db.refresh(podcast)
    return podcast


@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_podcast(podcast_id: int, current_user: CurrentUser, db: DBSession):
    """Delete a podcast."""
    result = await db.execute(
        select(Podcast).where(Podcast.id == podcast_id, Podcast.owner_id == current_user.id)
    )
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found or you don't have permission",
        )

    await db.delete(podcast)
    await db.commit()


@router.post("/{podcast_id}/sync", response_model=PodcastSchema)
async def sync_podcast_rss(podcast_id: int, current_user: CurrentUser, db: DBSession):
    """Sync podcast episodes from RSS feed."""
    result = await db.execute(
        select(Podcast)
        .options(selectinload(Podcast.episodes))
        .where(Podcast.id == podcast_id, Podcast.owner_id == current_user.id)
    )
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found or you don't have permission",
        )

    if not podcast.rss_feed_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Podcast has no RSS feed URL",
        )

    feed_data = await rss_parser.fetch_and_parse_rss(podcast.rss_feed_url)
    if not feed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not fetch RSS feed",
        )

    # Get existing episode GUIDs
    existing_guids = {ep.guid for ep in podcast.episodes if ep.guid}

    # Add new episodes
    new_count = 0
    for ep_data in feed_data.get("episodes", []):
        if ep_data.get("guid") and ep_data["guid"] in existing_guids:
            continue

        episode = Episode(
            podcast_id=podcast.id,
            guid=ep_data.get("guid"),
            title=ep_data.get("title", "Untitled"),
            description=ep_data.get("description"),
            audio_url=ep_data.get("audio_url"),
            duration_seconds=ep_data.get("duration_seconds"),
            file_size_bytes=ep_data.get("file_size_bytes"),
            published_at=ep_data.get("published_at"),
            episode_number=ep_data.get("episode_number"),
            season_number=ep_data.get("season_number"),
        )
        db.add(episode)
        new_count += 1

    podcast.last_rss_sync = datetime.utcnow()
    podcast.total_episodes = len(podcast.episodes) + new_count

    await db.commit()
    await db.refresh(podcast)
    return podcast


# ==================== Episode Endpoints ====================


@router.get("/{podcast_id}/episodes", response_model=list[EpisodeSchema])
async def list_podcast_episodes(
    podcast_id: int,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List episodes for a podcast."""
    result = await db.execute(
        select(Episode)
        .where(Episode.podcast_id == podcast_id)
        .order_by(Episode.published_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post(
    "/{podcast_id}/episodes",
    response_model=EpisodeSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_episode(
    podcast_id: int,
    episode_in: EpisodeCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new episode."""
    # Verify ownership
    result = await db.execute(
        select(Podcast).where(Podcast.id == podcast_id, Podcast.owner_id == current_user.id)
    )
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found or you don't have permission",
        )

    episode = Episode(
        podcast_id=podcast_id,
        title=episode_in.title,
        description=episode_in.description,
        audio_url=episode_in.audio_url,
        episode_number=episode_in.episode_number,
        season_number=episode_in.season_number,
        duration_seconds=episode_in.duration_seconds,
    )
    db.add(episode)

    # Update episode count
    podcast.total_episodes += 1

    await db.commit()
    await db.refresh(episode)
    return episode


@router.get("/episodes/{episode_id}", response_model=EpisodeSchema)
async def get_episode(episode_id: int, db: DBSession):
    """Get an episode by ID."""
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found",
        )
    return episode


@router.patch("/episodes/{episode_id}", response_model=EpisodeSchema)
async def update_episode(
    episode_id: int,
    episode_update: EpisodeUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update an episode."""
    result = await db.execute(
        select(Episode)
        .join(Podcast)
        .where(Episode.id == episode_id, Podcast.owner_id == current_user.id)
    )
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found or you don't have permission",
        )

    update_data = episode_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(episode, field, value)

    await db.commit()
    await db.refresh(episode)
    return episode


@router.delete("/episodes/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(episode_id: int, current_user: CurrentUser, db: DBSession):
    """Delete an episode."""
    result = await db.execute(
        select(Episode)
        .join(Podcast)
        .where(Episode.id == episode_id, Podcast.owner_id == current_user.id)
    )
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found or you don't have permission",
        )

    await db.delete(episode)
    await db.commit()


# ==================== Category Endpoints ====================


@router.get("/categories/all", response_model=list[CategorySchema])
async def list_categories(db: DBSession):
    """List all categories."""
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post(
    "/categories",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(category_in: CategoryCreate, db: DBSession):
    """Create a new category."""
    # Check if category exists
    result = await db.execute(select(Category).where(Category.name == category_in.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists",
        )

    category = Category(name=category_in.name, description=category_in.description)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category
