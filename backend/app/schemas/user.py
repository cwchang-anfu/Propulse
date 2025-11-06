"""
User Schemas
使用者相關的 Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import SubscriptionTier


class UserBase(BaseModel):
    """使用者基礎 Schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """建立使用者 Schema"""
    password: str


class UserUpdate(BaseModel):
    """更新使用者 Schema"""
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """使用者回應 Schema"""
    id: int
    subscription_tier: SubscriptionTier
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token Schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 內容 Schema"""
    email: Optional[str] = None
