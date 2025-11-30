"""
Guardian Pydantic 스키마
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GuardianBase(BaseModel):
    """Guardian 기본 스키마"""
    address: Optional[str] = Field(None, max_length=255)
    relationship_to_patient: Optional[str] = Field(None, max_length=50)
    emergency_contact: Optional[str] = Field(None, max_length=20)


class GuardianCreate(GuardianBase):
    """Guardian 생성 스키마"""
    user_id: int


class GuardianUpdate(GuardianBase):
    """Guardian 수정 스키마"""
    pass


class GuardianResponse(GuardianBase):
    """Guardian 응답 스키마"""
    guardian_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# 프론트엔드 API 계약용 스키마
class GuardianCreateRequest(BaseModel):
    """보호자 정보 등록 요청 (프론트엔드)"""
    name: str = Field(..., min_length=1, max_length=50, description="보호자 이름")
    phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$', description="연락처")
    address: str = Field(..., min_length=1, max_length=255, description="주소")
    relationship: str = Field(..., description="환자와의 관계")


class GuardianInfoResponse(BaseModel):
    """보호자 정보 응답 (프론트엔드)"""
    guardian_id: int
    user_id: int
    name: str
    phone: str
    address: str
    relationship: str
    created_at: datetime

