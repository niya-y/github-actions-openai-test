"""
Care Log Pydantic 스키마
"""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.care_execution import CareCategoryEnum


class CareLogBase(BaseModel):
    """케어 로그 기본 스키마"""
    category: CareCategoryEnum
    task_name: str = Field(..., max_length=100)
    scheduled_time: Optional[time] = None
    note: Optional[str] = None


class CareLogCreate(CareLogBase):
    """케어 로그 생성 스키마"""
    schedule_id: int


class CareLogUpdate(BaseModel):
    """케어 로그 수정 스키마"""
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    note: Optional[str] = None


class CareLogResponse(CareLogBase):
    """케어 로그 응답 스키마"""
    log_id: int
    schedule_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
