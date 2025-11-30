"""
User & Authentication Pydantic 스키마
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserTypeEnum, SocialProviderEnum


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """User 기본 스키마"""
    email: Optional[EmailStr] = None
    name: str = Field(..., min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    user_type: UserTypeEnum
    profile_image_url: Optional[str] = None


class UserCreate(UserBase):
    """User 생성 스키마"""
    password: Optional[str] = Field(None, min_length=8)


class UserUpdate(BaseModel):
    """User 수정 스키마"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_image_url: Optional[str] = None


class UserResponse(UserBase):
    """User 응답 스키마"""
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Social Account Schemas
# ============================================================================

class SocialAccountBase(BaseModel):
    """소셜 계정 기본 스키마"""
    provider: SocialProviderEnum
    provider_user_id: str = Field(..., max_length=100)


class SocialAccountCreate(SocialAccountBase):
    """소셜 계정 생성 스키마"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class SocialAccountResponse(SocialAccountBase):
    """소셜 계정 응답 스키마"""
    social_id: int
    user_id: int
    connected_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Personality Test Schemas
# ============================================================================

class PersonalityTestBase(BaseModel):
    """성향 테스트 기본 스키마"""
    empathy_score: float = Field(..., ge=0, le=100)
    activity_score: float = Field(..., ge=0, le=100)
    patience_score: float = Field(..., ge=0, le=100)
    independence_score: float = Field(..., ge=0, le=100)


class PersonalityTestCreate(PersonalityTestBase):
    """성향 테스트 생성 스키마"""
    raw_test_answers: Optional[dict] = None


class PersonalityTestResponse(PersonalityTestBase):
    """성향 테스트 응답 스키마"""
    test_id: int
    user_id: int
    ai_analysis_text: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Authentication Schemas
# ============================================================================

class TokenResponse(BaseModel):
    """JWT 토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class KakaoLoginRequest(BaseModel):
    """카카오 로그인 요청 스키마"""
    code: str
    redirect_uri: str


class KakaoLoginResponse(BaseModel):
    """카카오 로그인 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_new_user: bool
