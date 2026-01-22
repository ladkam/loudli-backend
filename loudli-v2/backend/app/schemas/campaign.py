from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.models.campaign import CampaignStatus, MessageType


class AttachmentBase(BaseModel):
    filename: str
    file_url: str
    file_type: str | None = None
    file_size_bytes: int | None = None


class Attachment(AttachmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    message_id: int | None = None
    created_at: datetime


class MessageBase(BaseModel):
    content: str | None = None
    message_type: MessageType = MessageType.TEXT
    offer_amount: Decimal | None = None


class MessageCreate(MessageBase):
    campaign_id: int


class Message(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    sender_id: int
    is_read: bool
    created_at: datetime


class MessageWithSender(Message):
    sender_email: str
    sender_name: str | None = None


class CampaignBase(BaseModel):
    title: str
    description: str | None = None
    budget: Decimal | None = None
    price_per_episode: Decimal | None = None
    currency: str = "USD"
    start_date: datetime | None = None
    end_date: datetime | None = None
    episodes_count: int | None = None
    target_demographics: str | None = None


class CampaignCreate(CampaignBase):
    podcast_id: int


class CampaignUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: CampaignStatus | None = None
    budget: Decimal | None = None
    price_per_episode: Decimal | None = None
    currency: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    episodes_count: int | None = None
    target_demographics: str | None = None


class Campaign(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    advertiser_id: int
    podcast_id: int
    status: CampaignStatus
    impressions: int
    clicks: int
    created_at: datetime
    updated_at: datetime


class CampaignWithDetails(Campaign):
    """Campaign with related data"""

    podcast_title: str | None = None
    advertiser_email: str | None = None
    messages: list[Message] = []
    attachments: list[Attachment] = []
    unread_count: int = 0


class CampaignStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_budget: Decimal
    total_impressions: int
    total_clicks: int
