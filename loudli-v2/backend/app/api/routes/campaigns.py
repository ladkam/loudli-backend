from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.api.deps import DBSession, CurrentUser
from app.models import Campaign, Message, Attachment, Podcast, CampaignStatus, MessageType
from app.models.user import UserType
from app.schemas.campaign import (
    Campaign as CampaignSchema,
    CampaignCreate,
    CampaignUpdate,
    CampaignWithDetails,
    CampaignStats,
    Message as MessageSchema,
    MessageCreate,
    Attachment as AttachmentSchema,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# ==================== Campaign Endpoints ====================


@router.get("", response_model=list[CampaignSchema])
async def list_campaigns(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: CampaignStatus | None = None,
):
    """List campaigns for current user (either as advertiser or podcast owner)."""
    # Get user's podcast IDs
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    query = select(Campaign).where(
        or_(
            Campaign.advertiser_id == current_user.id,
            Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
        )
    )

    if status_filter:
        query = query.where(Campaign.status == status_filter)

    query = query.order_by(Campaign.updated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CampaignSchema, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_in: CampaignCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new campaign (advertisers only)."""
    # Verify podcast exists
    result = await db.execute(
        select(Podcast).where(Podcast.id == campaign_in.podcast_id, Podcast.is_active == True)
    )
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast not found",
        )

    # Can't create campaign for own podcast
    if podcast.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create campaign for your own podcast",
        )

    campaign = Campaign(
        advertiser_id=current_user.id,
        podcast_id=campaign_in.podcast_id,
        title=campaign_in.title,
        description=campaign_in.description,
        budget=campaign_in.budget,
        price_per_episode=campaign_in.price_per_episode,
        currency=campaign_in.currency,
        start_date=campaign_in.start_date,
        end_date=campaign_in.end_date,
        episodes_count=campaign_in.episodes_count,
        target_demographics=campaign_in.target_demographics,
        status=CampaignStatus.PENDING,
    )

    db.add(campaign)
    await db.flush()

    # Create initial system message
    system_message = Message(
        campaign_id=campaign.id,
        sender_id=current_user.id,
        content=f"Campaign '{campaign.title}' created",
        message_type=MessageType.SYSTEM,
    )
    db.add(system_message)

    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/stats", response_model=CampaignStats)
async def get_campaign_stats(current_user: CurrentUser, db: DBSession):
    """Get campaign statistics for current user."""
    # Get user's podcast IDs
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    base_condition = or_(
        Campaign.advertiser_id == current_user.id,
        Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
    )

    # Total campaigns
    total_result = await db.execute(
        select(func.count(Campaign.id)).where(base_condition)
    )
    total_campaigns = total_result.scalar() or 0

    # Active campaigns
    active_statuses = [
        CampaignStatus.PENDING,
        CampaignStatus.NEGOTIATING,
        CampaignStatus.ACCEPTED,
        CampaignStatus.IN_PROGRESS,
    ]
    active_result = await db.execute(
        select(func.count(Campaign.id)).where(
            and_(base_condition, Campaign.status.in_(active_statuses))
        )
    )
    active_campaigns = active_result.scalar() or 0

    # Budget and stats
    stats_result = await db.execute(
        select(
            func.coalesce(func.sum(Campaign.budget), 0),
            func.coalesce(func.sum(Campaign.impressions), 0),
            func.coalesce(func.sum(Campaign.clicks), 0),
        ).where(base_condition)
    )
    row = stats_result.fetchone()
    total_budget = row[0] if row else Decimal("0")
    total_impressions = row[1] if row else 0
    total_clicks = row[2] if row else 0

    return CampaignStats(
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        total_budget=total_budget,
        total_impressions=total_impressions,
        total_clicks=total_clicks,
    )


@router.get("/{campaign_id}", response_model=CampaignWithDetails)
async def get_campaign(campaign_id: int, current_user: CurrentUser, db: DBSession):
    """Get campaign details with messages."""
    # Get user's podcast IDs
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    result = await db.execute(
        select(Campaign)
        .options(
            selectinload(Campaign.messages),
            selectinload(Campaign.attachments),
            selectinload(Campaign.podcast),
            selectinload(Campaign.advertiser),
        )
        .where(
            Campaign.id == campaign_id,
            or_(
                Campaign.advertiser_id == current_user.id,
                Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
            ),
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or you don't have access",
        )

    # Count unread messages
    unread_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.campaign_id == campaign_id,
            Message.sender_id != current_user.id,
            Message.is_read == False,
        )
    )
    unread_count = unread_result.scalar() or 0

    return CampaignWithDetails(
        **{c.name: getattr(campaign, c.name) for c in Campaign.__table__.columns},
        podcast_title=campaign.podcast.title if campaign.podcast else None,
        advertiser_email=campaign.advertiser.email if campaign.advertiser else None,
        messages=campaign.messages,
        attachments=campaign.attachments,
        unread_count=unread_count,
    )


@router.patch("/{campaign_id}", response_model=CampaignSchema)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update a campaign."""
    # Get user's podcast IDs
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            or_(
                Campaign.advertiser_id == current_user.id,
                Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
            ),
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or you don't have access",
        )

    # Status change validation
    if campaign_update.status:
        is_advertiser = campaign.advertiser_id == current_user.id
        is_podcaster = campaign.podcast_id in user_podcast_ids

        # Only podcaster can accept/reject
        if campaign_update.status in [CampaignStatus.ACCEPTED, CampaignStatus.REJECTED]:
            if not is_podcaster:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only podcast owner can accept or reject campaigns",
                )

        # Only advertiser can cancel
        if campaign_update.status == CampaignStatus.CANCELLED:
            if not is_advertiser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only advertiser can cancel campaigns",
                )

    update_data = campaign_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)
    return campaign


# ==================== Message Endpoints ====================


@router.post("/{campaign_id}/messages", response_model=MessageSchema)
async def send_message(
    campaign_id: int,
    message_in: MessageCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Send a message in a campaign."""
    # Verify access
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            or_(
                Campaign.advertiser_id == current_user.id,
                Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
            ),
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or you don't have access",
        )

    # Update campaign status if sending first message
    if campaign.status == CampaignStatus.PENDING:
        campaign.status = CampaignStatus.NEGOTIATING

    message = Message(
        campaign_id=campaign_id,
        sender_id=current_user.id,
        content=message_in.content,
        message_type=message_in.message_type,
        offer_amount=message_in.offer_amount,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/{campaign_id}/messages", response_model=list[MessageSchema])
async def list_messages(
    campaign_id: int,
    current_user: CurrentUser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List messages in a campaign."""
    # Verify access
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    campaign_result = await db.execute(
        select(Campaign.id).where(
            Campaign.id == campaign_id,
            or_(
                Campaign.advertiser_id == current_user.id,
                Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
            ),
        )
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or you don't have access",
        )

    result = await db.execute(
        select(Message)
        .where(Message.campaign_id == campaign_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/{campaign_id}/messages/read")
async def mark_messages_read(
    campaign_id: int,
    current_user: CurrentUser,
    db: DBSession,
):
    """Mark all messages as read in a campaign."""
    # Verify access
    podcast_result = await db.execute(
        select(Podcast.id).where(Podcast.owner_id == current_user.id)
    )
    user_podcast_ids = [row[0] for row in podcast_result.fetchall()]

    campaign_result = await db.execute(
        select(Campaign.id).where(
            Campaign.id == campaign_id,
            or_(
                Campaign.advertiser_id == current_user.id,
                Campaign.podcast_id.in_(user_podcast_ids) if user_podcast_ids else False,
            ),
        )
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or you don't have access",
        )

    # Mark messages from other users as read
    result = await db.execute(
        select(Message).where(
            Message.campaign_id == campaign_id,
            Message.sender_id != current_user.id,
            Message.is_read == False,
        )
    )
    messages = result.scalars().all()

    for message in messages:
        message.is_read = True

    await db.commit()
    return {"marked_read": len(messages)}
