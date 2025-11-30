"""
Matching System Pydantic 스키마
"""

from datetime import date, datetime, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.matching import GradeEnum, MatchingStatusEnum


# ============================================================================
# Caregiver Availability Schemas
# ============================================================================

class CaregiverAvailabilityBase(BaseModel):
    """간병인 가용 시간 기본 스키마"""
    day_of_week: str = Field(..., pattern="^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$")
    start_time: time
    end_time: time
    is_available: bool = True


class CaregiverAvailabilityCreate(CaregiverAvailabilityBase):
    """간병인 가용 시간 생성 스키마"""
    caregiver_id: int


class CaregiverAvailabilityUpdate(BaseModel):
    """간병인 가용 시간 수정 스키마"""
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None


class CaregiverAvailabilityResponse(CaregiverAvailabilityBase):
    """간병인 가용 시간 응답 스키마"""
    availability_id: int
    caregiver_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Matching Request Schemas
# ============================================================================

class MatchingRequestBase(BaseModel):
    """매칭 요청 기본 스키마"""
    required_qualification: Optional[str] = Field(None, max_length=50)
    preferred_regions: Optional[str] = Field(None, max_length=50)
    preferred_days: List[str] = Field(..., min_length=1)
    preferred_time_slots: List[Dict[str, Any]] = Field(..., min_length=1)
    additional_request: Optional[str] = None


class MatchingRequestCreate(MatchingRequestBase):
    """매칭 요청 생성 스키마"""
    patient_id: int


class MatchingRequestUpdate(BaseModel):
    """매칭 요청 수정 스키마"""
    required_qualification: Optional[str] = Field(None, max_length=50)
    preferred_regions: Optional[str] = Field(None, max_length=50)
    preferred_days: Optional[List[str]] = Field(None, min_length=1)
    preferred_time_slots: Optional[List[Dict[str, Any]]] = Field(None, min_length=1)
    additional_request: Optional[str] = None
    is_active: Optional[bool] = None


class MatchingRequestResponse(MatchingRequestBase):
    """매칭 요청 응답 스키마"""
    request_id: int
    patient_id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Matching Result Schemas
# ============================================================================

class MatchingResultBase(BaseModel):
    """매칭 결과 기본 스키마"""
    total_score: float = Field(..., ge=0, le=100)
    grade: GradeEnum
    ai_comment: Optional[str] = None


class MatchingResultCreate(MatchingResultBase):
    """매칭 결과 생성 스키마"""
    request_id: int
    caregiver_id: int


class MatchingResultUpdate(BaseModel):
    """매칭 결과 수정 스키마"""
    status: Optional[MatchingStatusEnum] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None


class MatchingResultResponse(MatchingResultBase):
    """매칭 결과 응답 스키마"""
    matching_id: int
    request_id: int
    caregiver_id: int
    status: MatchingStatusEnum
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Forward references for detailed response
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.caregiver import CaregiverResponse
    from app.schemas.patient import PatientResponse


class MatchingResultDetailResponse(MatchingResultResponse):
    """매칭 결과 상세 응답 스키마 (간병인 및 환자 정보 포함)"""
    caregiver: Optional["CaregiverResponse"] = None
    
    model_config = ConfigDict(from_attributes=True)
