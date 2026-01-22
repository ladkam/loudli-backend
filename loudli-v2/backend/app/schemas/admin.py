from datetime import datetime
from pydantic import BaseModel, ConfigDict


# System Settings
class SettingBase(BaseModel):
    key: str
    value: str | None = None
    is_secret: bool = False
    description: str | None = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: str | None = None
    description: str | None = None


class Setting(SettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime


class SettingPublic(BaseModel):
    """Setting with masked secret values"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    value: str | None = None  # Will be masked if is_secret
    is_secret: bool
    description: str | None = None
    updated_at: datetime


# Podcaster-Advertiser Matching
class MatchBase(BaseModel):
    podcast_id: int
    advertiser_id: int
    match_score: float | None = None
    match_reason: str | None = None


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    status: str | None = None
    match_score: float | None = None
    match_reason: str | None = None


class Match(MatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime


class MatchWithDetails(Match):
    """Match with podcast and advertiser details"""
    podcast_title: str | None = None
    podcast_author: str | None = None
    advertiser_email: str | None = None
    advertiser_company: str | None = None


# Admin Dashboard Stats
class AdminStats(BaseModel):
    total_users: int
    total_podcasters: int
    total_advertisers: int
    total_podcasts: int
    total_campaigns: int
    active_campaigns: int
    total_matches: int
    pending_matches: int


# User management for admin
class AdminUserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    user_type: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
