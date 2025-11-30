"""
Care Report Pydantic 스키마
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.care_execution import ReportTypeEnum


class CareReportBase(BaseModel):
    """케어 리포트 기본 스키마"""
    report_type: ReportTypeEnum
    start_date: date
    end_date: date


class CareReportCreate(CareReportBase):
    """케어 리포트 생성 스키마"""
    patient_id: int


class CareReportUpdate(BaseModel):
    """케어 리포트 수정 스키마"""
    medication_completion_rate: Optional[float] = Field(None, ge=0, le=100)
    meal_completion_rate: Optional[float] = Field(None, ge=0, le=100)
    health_status_summary: Optional[str] = None
    improvement_suggestions: Optional[str] = None


class CareReportResponse(CareReportBase):
    """케어 리포트 응답 스키마"""
    report_id: int
    patient_id: int
    medication_completion_rate: Optional[float] = None
    meal_completion_rate: Optional[float] = None
    health_status_summary: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
