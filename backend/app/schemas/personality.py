"""
Personality Pydantic 스키마
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PersonalityScoreBase(BaseModel):
    """성향 점수 기본 스키마"""
    empathy_score: float = Field(..., ge=0, le=100)
    activity_score: float = Field(..., ge=0, le=100)
    patience_score: float = Field(..., ge=0, le=100)
    independence_score: float = Field(..., ge=0, le=100)


class PersonalityTestRequest(BaseModel):
    """성향 테스트 요청 스키마 (12문제 Likert 척도)"""
    user_type: str = Field(..., pattern="^(guardian|caregiver)$")
    answers: dict = Field(..., description="12개 질문의 답변 (1-5 Likert scale)")
    # Example: {"q1": 4, "q2": 3, ..., "q12": 5}


class PersonalityQuestionBank(BaseModel):
    """12개 성향 테스트 질문 정보"""
    question_id: str = Field(..., description="질문 ID (q1-q12)")
    question_text: str = Field(..., description="질문 텍스트")
    dimension: str = Field(..., description="측정 차원 (empathy|activity|patience|independence)")
    category: str = Field(..., description="카테고리")


class PersonalityAnalysisResult(BaseModel):
    """AI 분석 결과"""
    empathy_score: float = Field(..., ge=0, le=100)
    activity_score: float = Field(..., ge=0, le=100)
    patience_score: float = Field(..., ge=0, le=100)
    independence_score: float = Field(..., ge=0, le=100)
    analysis_text: str = Field(..., description="상세 분석 텍스트 (한국어)")
    recommendation: str = Field(..., description="간병인 추천 유형")


# ============================================================================
# Patient Personality Schemas
# ============================================================================

class PatientPersonalityCreate(PersonalityScoreBase):
    """환자 성향 생성 스키마"""
    patient_id: int


class PatientPersonalityUpdate(BaseModel):
    """환자 성향 수정 스키마"""
    empathy_score: Optional[float] = Field(None, ge=0, le=100)
    activity_score: Optional[float] = Field(None, ge=0, le=100)
    patience_score: Optional[float] = Field(None, ge=0, le=100)
    independence_score: Optional[float] = Field(None, ge=0, le=100)


class PatientPersonalityResponse(PersonalityScoreBase):
    """환자 성향 응답 스키마"""
    personality_id: int
    patient_id: int
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Caregiver Personality Schemas
# ============================================================================

class CaregiverPersonalityCreate(PersonalityScoreBase):
    """간병인 성향 생성 스키마"""
    caregiver_id: int


class CaregiverPersonalityUpdate(BaseModel):
    """간병인 성향 수정 스키마"""
    empathy_score: Optional[float] = Field(None, ge=0, le=100)
    activity_score: Optional[float] = Field(None, ge=0, le=100)
    patience_score: Optional[float] = Field(None, ge=0, le=100)
    independence_score: Optional[float] = Field(None, ge=0, le=100)


class CaregiverPersonalityResponse(PersonalityScoreBase):
    """간병인 성향 응답 스키마"""
    personality_id: int
    caregiver_id: int
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
