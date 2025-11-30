"""
Schedule Pydantic 스키마
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ScheduleBase(BaseModel):
    """일정 기본 스키마"""
    care_date: date
    is_ai_generated: bool = True
    status: str = Field(default="scheduled", pattern="^(scheduled|completed|cancelled)$")


class ScheduleCreate(ScheduleBase):
    """일정 생성 스키마"""
    patient_id: int
    matching_id: Optional[int] = None


class ScheduleUpdate(BaseModel):
    """일정 수정 스키마"""
    status: Optional[str] = Field(None, pattern="^(scheduled|completed|cancelled)$")


class ScheduleResponse(ScheduleBase):
    """일정 응답 스키마"""
    schedule_id: int
    patient_id: int
    matching_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Forward references for detailed response
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.care_log import CareLogResponse


class ScheduleDetailResponse(ScheduleResponse):
    """일정 상세 응답 스키마 (케어 로그 포함)"""
    care_logs: List["CareLogResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)
