from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import UserType


class UserProfileBase(BaseModel):
    user_type: UserType = UserType.PODCASTER
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
    bio: str | None = None
    phone: str | None = None
    website: str | None = None
    location: str | None = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    user_type: UserType | None = None
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
    bio: str | None = None
    phone: str | None = None
    website: str | None = None
    location: str | None = None


class UserProfile(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    profile_image_url: str | None = None


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    profile: UserProfileCreate | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    profile: UserProfile | None = None


class UserInDB(User):
    hashed_password: str


# Auth schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
