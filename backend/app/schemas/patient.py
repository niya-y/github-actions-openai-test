"""
Patient Pydantic 스키마 (프론트엔드 API 계약용)
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.profile import GenderEnum, CareLevelEnum


class PatientBase(BaseModel):
    """Patient 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=50)
    birth_date: date
    gender: GenderEnum
    height: Optional[int] = Field(None, gt=0, lt=300)
    weight: Optional[int] = Field(None, gt=0, lt=500)
    care_address: str = Field(..., max_length=255)
    region_code: str = Field(..., max_length=50)
    care_level: Optional[CareLevelEnum] = None
    profile_image_url: Optional[str] = None


class PatientCreate(PatientBase):
    """Patient 생성 스키마"""
    guardian_id: int


class PatientUpdate(BaseModel):
    """Patient 수정 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    height: Optional[int] = Field(None, gt=0, lt=300)
    weight: Optional[int] = Field(None, gt=0, lt=500)
    care_address: Optional[str] = Field(None, max_length=255)
    region_code: Optional[str] = Field(None, max_length=50)
    care_level: Optional[CareLevelEnum] = None
    profile_image_url: Optional[str] = None


class PatientResponse(PatientBase):
    """Patient 응답 스키마"""
    patient_id: int
    guardian_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Forward references for detailed response
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.health import HealthConditionResponse, MedicationResponse, DietaryPreferenceResponse
    from app.schemas.personality import PatientPersonalityResponse


class PatientDetailResponse(PatientResponse):
    """Patient 상세 응답 스키마 (건강 정보 포함)"""
    personality: Optional["PatientPersonalityResponse"] = None
    health_conditions: List["HealthConditionResponse"] = []
    medications: List["MedicationResponse"] = []
    dietary_preferences: List["DietaryPreferenceResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 프론트엔드 API 계약용 스키마 ====================

class DiseaseItem(BaseModel):
    """질병 항목"""
    id: str
    name: str


class PatientCreateRequest(BaseModel):
    """환자 기본 정보 등록 요청 (프론트엔드)"""
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=150, description="환자 나이")
    gender: str = Field(..., pattern=r'^(male|female)$', description="성별 (male/female)")
    relationship: str = Field(..., description="보호자와의 관계")
    
    @field_validator('gender')
    @classmethod
    def convert_gender(cls, v: str) -> str:
        """프론트엔드 성별 값을 DB Enum 값으로 변환"""
        mapping = {'female': 'Female', 'male': 'Male'}
        return mapping.get(v, v)


class PatientInfoResponse(BaseModel):
    """환자 정보 응답 (프론트엔드)"""
    patient_id: int
    name: str
    birth_date: str  # ISO 8601 형식
    age: int
    gender: str  # "Male" or "Female"
    guardian_id: int
    created_at: str  # ISO 8601 형식


class HealthStatusUpdateRequest(BaseModel):
    """환자 건강 상태 업데이트 요청 (프론트엔드)"""
    selectedDiseases: List[DiseaseItem] = Field(default_factory=list, description="선택된 질병 목록")
    mobility_status: str = Field(..., description="거동 상태")  # independent, assistive-device, wheelchair, bedridden


class MedicationsCreateRequest(BaseModel):
    """환자 복용 약물 등록 요청 (프론트엔드)"""
    medicine_names: List[str] = Field(..., min_length=1, description="약물 목록")


class MedicationInfoResponse(BaseModel):
    """약물 정보 응답 (프론트엔드)"""
    patient_id: int
    med_id: int
    medicine_names: List[str]


class DietaryPreferencesCreateRequest(BaseModel):
    """환자 식이 선호 등록 요청 (프론트엔드)"""
    allergy_foods: List[str] = Field(default_factory=list, description="알레르기 음식 목록")
    restriction_foods: List[str] = Field(default_factory=list, description="식이 제한 음식 목록")


class DietaryPreferencesResponse(BaseModel):
    """식이 선호 응답 (프론트엔드)"""
    patient_id: int
    diet_id: int
    allergy_foods: List[str]
    restriction_foods: List[str]
