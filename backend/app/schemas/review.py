"""
Review Pydantic 스키마
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewBase(BaseModel):
    """리뷰 기본 스키마"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """리뷰 생성 스키마"""
    matching_id: int


class ReviewUpdate(BaseModel):
    """리뷰 수정 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    """리뷰 응답 스키마"""
    review_id: int
    matching_id: int
    reviewer_id: int
    reviewer_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
