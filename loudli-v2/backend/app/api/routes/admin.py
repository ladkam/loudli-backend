from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.api.deps import DBSession, CurrentSuperuser
from app.models import (
    User, UserProfile, Podcast, Campaign, CampaignStatus,
    SystemSettings, PodcasterAdvertiserMatch
)
from app.models.user import UserType
from app.schemas.admin import (
    Setting, SettingCreate, SettingUpdate, SettingPublic,
    Match, MatchCreate, MatchUpdate, MatchWithDetails,
    AdminStats, AdminUserView
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== Dashboard Stats ====================


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(admin: CurrentSuperuser, db: DBSession):
    """Get admin dashboard statistics."""
    # Total users
    total_users = await db.execute(select(func.count(User.id)))
    total_users = total_users.scalar() or 0

    # Users by type
    podcasters = await db.execute(
        select(func.count(UserProfile.id)).where(UserProfile.user_type == UserType.PODCASTER)
    )
    podcasters = podcasters.scalar() or 0

    advertisers = await db.execute(
        select(func.count(UserProfile.id)).where(UserProfile.user_type == UserType.ADVERTISER)
    )
    advertisers = advertisers.scalar() or 0

    # Podcasts
    total_podcasts = await db.execute(select(func.count(Podcast.id)))
    total_podcasts = total_podcasts.scalar() or 0

    # Campaigns
    total_campaigns = await db.execute(select(func.count(Campaign.id)))
    total_campaigns = total_campaigns.scalar() or 0

    active_statuses = [
        CampaignStatus.PENDING, CampaignStatus.NEGOTIATING,
        CampaignStatus.ACCEPTED, CampaignStatus.IN_PROGRESS
    ]
    active_campaigns = await db.execute(
        select(func.count(Campaign.id)).where(Campaign.status.in_(active_statuses))
    )
    active_campaigns = active_campaigns.scalar() or 0

    # Matches
    total_matches = await db.execute(select(func.count(PodcasterAdvertiserMatch.id)))
    total_matches = total_matches.scalar() or 0

    pending_matches = await db.execute(
        select(func.count(PodcasterAdvertiserMatch.id))
        .where(PodcasterAdvertiserMatch.status == "pending")
    )
    pending_matches = pending_matches.scalar() or 0

    return AdminStats(
        total_users=total_users,
        total_podcasters=podcasters,
        total_advertisers=advertisers,
        total_podcasts=total_podcasts,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        total_matches=total_matches,
        pending_matches=pending_matches,
    )


# ==================== System Settings ====================


@router.get("/settings", response_model=list[SettingPublic])
async def list_settings(admin: CurrentSuperuser, db: DBSession):
    """List all system settings (secrets are masked)."""
    result = await db.execute(select(SystemSettings).order_by(SystemSettings.key))
    settings = result.scalars().all()

    # Mask secret values
    public_settings = []
    for setting in settings:
        value = "••••••••" if setting.is_secret and setting.value else setting.value
        public_settings.append(SettingPublic(
            id=setting.id,
            key=setting.key,
            value=value,
            is_secret=setting.is_secret,
            description=setting.description,
            updated_at=setting.updated_at,
        ))
    return public_settings


@router.post("/settings", response_model=Setting, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting_in: SettingCreate,
    admin: CurrentSuperuser,
    db: DBSession,
):
    """Create a new system setting."""
    # Check if key already exists
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == setting_in.key)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting '{setting_in.key}' already exists",
        )

    setting = SystemSettings(**setting_in.model_dump())
    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return setting


@router.get("/settings/{key}", response_model=SettingPublic)
async def get_setting(key: str, admin: CurrentSuperuser, db: DBSession):
    """Get a specific setting by key."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == key)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found",
        )

    value = "••••••••" if setting.is_secret and setting.value else setting.value
    return SettingPublic(
        id=setting.id,
        key=setting.key,
        value=value,
        is_secret=setting.is_secret,
        description=setting.description,
        updated_at=setting.updated_at,
    )


@router.patch("/settings/{key}", response_model=SettingPublic)
async def update_setting(
    key: str,
    setting_update: SettingUpdate,
    admin: CurrentSuperuser,
    db: DBSession,
):
    """Update a system setting."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == key)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found",
        )

    update_data = setting_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)

    await db.commit()
    await db.refresh(setting)

    value = "••••••••" if setting.is_secret and setting.value else setting.value
    return SettingPublic(
        id=setting.id,
        key=setting.key,
        value=value,
        is_secret=setting.is_secret,
        description=setting.description,
        updated_at=setting.updated_at,
    )


@router.delete("/settings/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(key: str, admin: CurrentSuperuser, db: DBSession):
    """Delete a system setting."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == key)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found",
        )

    await db.delete(setting)
    await db.commit()


# ==================== User Management ====================


@router.get("/users", response_model=list[AdminUserView])
async def list_users(
    admin: CurrentSuperuser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_type: str | None = None,
    search: str | None = None,
):
    """List all users with filters."""
    query = select(User).options(selectinload(User.profile))

    if search:
        query = query.where(User.email.ilike(f"%{search}%"))

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    # Filter by user_type if specified (need to do after loading profiles)
    user_views = []
    for user in users:
        if user_type and user.profile and user.profile.user_type.value != user_type:
            continue
        user_views.append(AdminUserView(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            user_type=user.profile.user_type.value if user.profile else None,
            first_name=user.profile.first_name if user.profile else None,
            last_name=user.profile.last_name if user.profile else None,
            company_name=user.profile.company_name if user.profile else None,
        ))

    return user_views


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: int, admin: CurrentSuperuser, db: DBSession):
    """Toggle a user's active status."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )

    user.is_active = not user.is_active
    await db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.patch("/users/{user_id}/make-admin")
async def make_user_admin(user_id: int, admin: CurrentSuperuser, db: DBSession):
    """Grant or revoke admin privileges."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own admin status",
        )

    user.is_superuser = not user.is_superuser
    await db.commit()
    return {"id": user.id, "is_superuser": user.is_superuser}


# ==================== Podcaster-Advertiser Matching ====================


@router.get("/matches", response_model=list[MatchWithDetails])
async def list_matches(
    admin: CurrentSuperuser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str | None = None,
):
    """List all matches with details."""
    query = select(PodcasterAdvertiserMatch)

    if status_filter:
        query = query.where(PodcasterAdvertiserMatch.status == status_filter)

    query = query.offset(skip).limit(limit).order_by(
        PodcasterAdvertiserMatch.created_at.desc()
    )
    result = await db.execute(query)
    matches = result.scalars().all()

    # Enrich with details
    match_details = []
    for match in matches:
        # Get podcast details
        podcast_result = await db.execute(
            select(Podcast).where(Podcast.id == match.podcast_id)
        )
        podcast = podcast_result.scalar_one_or_none()

        # Get advertiser details
        advertiser_result = await db.execute(
            select(User).options(selectinload(User.profile))
            .where(User.id == match.advertiser_id)
        )
        advertiser = advertiser_result.scalar_one_or_none()

        match_details.append(MatchWithDetails(
            id=match.id,
            podcast_id=match.podcast_id,
            advertiser_id=match.advertiser_id,
            match_score=match.match_score,
            match_reason=match.match_reason,
            status=match.status,
            created_at=match.created_at,
            updated_at=match.updated_at,
            podcast_title=podcast.title if podcast else None,
            podcast_author=podcast.author if podcast else None,
            advertiser_email=advertiser.email if advertiser else None,
            advertiser_company=advertiser.profile.company_name if advertiser and advertiser.profile else None,
        ))

    return match_details


@router.post("/matches", response_model=Match, status_code=status.HTTP_201_CREATED)
async def create_match(
    match_in: MatchCreate,
    admin: CurrentSuperuser,
    db: DBSession,
):
    """Create a new podcaster-advertiser match."""
    # Verify podcast exists
    podcast_result = await db.execute(
        select(Podcast).where(Podcast.id == match_in.podcast_id)
    )
    if not podcast_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found",
        )

    # Verify advertiser exists and is an advertiser
    advertiser_result = await db.execute(
        select(User).options(selectinload(User.profile))
        .where(User.id == match_in.advertiser_id)
    )
    advertiser = advertiser_result.scalar_one_or_none()
    if not advertiser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advertiser not found",
        )
    if advertiser.profile and advertiser.profile.user_type != UserType.ADVERTISER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an advertiser",
        )

    match = PodcasterAdvertiserMatch(**match_in.model_dump())
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match


@router.patch("/matches/{match_id}", response_model=Match)
async def update_match(
    match_id: int,
    match_update: MatchUpdate,
    admin: CurrentSuperuser,
    db: DBSession,
):
    """Update a match."""
    result = await db.execute(
        select(PodcasterAdvertiserMatch).where(PodcasterAdvertiserMatch.id == match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )

    update_data = match_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(match, field, value)

    await db.commit()
    await db.refresh(match)
    return match


@router.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: int, admin: CurrentSuperuser, db: DBSession):
    """Delete a match."""
    result = await db.execute(
        select(PodcasterAdvertiserMatch).where(PodcasterAdvertiserMatch.id == match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )

    await db.delete(match)
    await db.commit()


# ==================== Podcast Management ====================


@router.get("/podcasts", response_model=list[dict])
async def list_all_podcasts(
    admin: CurrentSuperuser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all podcasts for admin."""
    result = await db.execute(
        select(Podcast)
        .options(selectinload(Podcast.owner))
        .offset(skip)
        .limit(limit)
        .order_by(Podcast.created_at.desc())
    )
    podcasts = result.scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "author": p.author,
            "owner_email": p.owner.email if p.owner else None,
            "total_episodes": p.total_episodes,
            "is_active": p.is_active,
            "created_at": p.created_at,
        }
        for p in podcasts
    ]


@router.patch("/podcasts/{podcast_id}/toggle-active")
async def toggle_podcast_active(podcast_id: int, admin: CurrentSuperuser, db: DBSession):
    """Toggle a podcast's active status."""
    result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found",
        )

    podcast.is_active = not podcast.is_active
    await db.commit()
    return {"id": podcast.id, "is_active": podcast.is_active}
