"""
Dashboard Pydantic 스키마 (마이페이지)
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class DashboardUserInfo(BaseModel):
    """대시보드 사용자 정보"""
    user_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_type: str
    gender: Optional[str] = None


class DashboardGuardianInfo(BaseModel):
    """대시보드 보호자 정보"""
    guardian_id: int
    address: str
    relationship: str


class DashboardPatientInfo(BaseModel):
    """대시보드 환자 정보"""
    patient_id: int
    name: str
    age: int
    care_level: Optional[str] = None


class DashboardActiveMatching(BaseModel):
    """대시보드 활성 매칭 정보"""
    caregiver_name: str
    match_score: float
    start_date: str  # ISO 8601 형식


class DashboardResponse(BaseModel):
    """마이페이지 대시보드 응답"""
    user: DashboardUserInfo
    guardian: Optional[DashboardGuardianInfo] = None
    patients: List[DashboardPatientInfo] = []
    active_matching: Optional[DashboardActiveMatching] = None
