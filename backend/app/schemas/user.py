"""
User Pydantic 스키마 (요청/응답 검증)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """User 기본 스키마"""
    
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    profile_image: Optional[str] = None


class UserResponse(UserBase):
    """User 응답 스키마"""
    
    id: int
    kakao_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Pydantic v2


class TokenResponse(BaseModel):
    """JWT 토큰 응답 스키마"""
    
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
