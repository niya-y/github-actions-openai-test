"""
Health Information Pydantic 스키마
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Health Condition Schemas
# ============================================================================

class HealthConditionBase(BaseModel):
    """건강 상태 기본 스키마"""
    disease_name: str = Field(..., max_length=100)
    note: Optional[str] = None


class HealthConditionCreate(HealthConditionBase):
    """건강 상태 생성 스키마"""
    patient_id: int


class HealthConditionUpdate(BaseModel):
    """건강 상태 수정 스키마"""
    disease_name: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = None


class HealthConditionResponse(HealthConditionBase):
    """건강 상태 응답 스키마"""
    condition_id: int
    patient_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Medication Schemas
# ============================================================================

class MedicationBase(BaseModel):
    """복약 정보 기본 스키마"""
    name: str = Field(..., max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=50)
    intake_method: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = None


class MedicationCreate(MedicationBase):
    """복약 정보 생성 스키마"""
    patient_id: int


class MedicationUpdate(BaseModel):
    """복약 정보 수정 스키마"""
    name: Optional[str] = Field(None, max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=50)
    intake_method: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = None


class MedicationResponse(MedicationBase):
    """복약 정보 응답 스키마"""
    med_id: int
    patient_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Dietary Preference Schemas
# ============================================================================

class DietaryPreferenceBase(BaseModel):
    """식이 선호도 기본 스키마"""
    allergy_foods: Optional[List[str]] = None
    restriction_foods: Optional[List[str]] = None


class DietaryPreferenceCreate(DietaryPreferenceBase):
    """식이 선호도 생성 스키마"""
    patient_id: int


class DietaryPreferenceUpdate(DietaryPreferenceBase):
    """식이 선호도 수정 스키마"""
    pass


class DietaryPreferenceResponse(DietaryPreferenceBase):
    """식이 선호도 응답 스키마"""
    diet_id: int
    patient_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
