"""
Caregiver Pydantic 스키마
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class CaregiverBase(BaseModel):
    """Caregiver 기본 스키마"""
    experience_years: int = Field(default=0, ge=0)
    certifications: Optional[str] = Field(None, max_length=255)
    specialties: Optional[List[str]] = None
    service_region: Optional[str] = Field(None, max_length=50)
    has_vehicle: bool = False
    hourly_rate: Optional[int] = Field(None, gt=0, le=1000000)


class CaregiverCreate(CaregiverBase):
    """Caregiver 생성 스키마"""
    user_id: int


class CaregiverUpdate(BaseModel):
    """Caregiver 수정 스키마"""
    experience_years: Optional[int] = Field(None, ge=0)
    certifications: Optional[str] = Field(None, max_length=255)
    specialties: Optional[List[str]] = None
    service_region: Optional[str] = Field(None, max_length=50)
    has_vehicle: Optional[bool] = None
    hourly_rate: Optional[int] = Field(None, gt=0, le=1000000)


class CaregiverResponse(CaregiverBase):
    """Caregiver 응답 스키마"""
    caregiver_id: int
    user_id: int
    avg_rating: Decimal
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Forward references for detailed response
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.personality import CaregiverPersonalityResponse
    from app.schemas.matching import CaregiverAvailabilityResponse


class CaregiverDetailResponse(CaregiverResponse):
    """Caregiver 상세 응답 스키마 (성향 및 가용시간 포함)"""
    personality: Optional["CaregiverPersonalityResponse"] = None
    availability: List["CaregiverAvailabilityResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)
