"""
매칭 시스템 모델 (schema.sql 기반)
"""

from sqlalchemy import Column, BigInteger, String, Float, Date, Boolean, DateTime, Enum as SQLEnum, CheckConstraint, Index, ForeignKey, Text, Time
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# Enum 타입 정의
class GradeEnum(str, enum.Enum):
    """매칭 등급"""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"


class MatchingStatusEnum(str, enum.Enum):
    """매칭 상태"""
    recommended = "recommended"
    selected = "selected"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class MatchingRequest(Base):
    """매칭 요청서"""

    __tablename__ = "matching_requests"

    request_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)

    required_qualification = Column(String(50), nullable=True)
    preferred_regions = Column(String(50), nullable=True)

    preferred_days = Column(JSONB, nullable=False)
    preferred_time_slots = Column(JSONB, nullable=False)

    # 간병 기간
    care_start_date = Column(Date, nullable=True)
    care_end_date = Column(Date, nullable=True)

    additional_request = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="matching_requests")
    matching_results = relationship("MatchingResult", back_populates="request", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "jsonb_typeof(preferred_days) = 'array' AND jsonb_array_length(preferred_days) > 0",
            name="check_days_format"
        ),
        CheckConstraint(
            "jsonb_typeof(preferred_time_slots) = 'array' AND jsonb_array_length(preferred_time_slots) > 0",
            name="check_slots_format"
        ),
        CheckConstraint(
            "care_start_date IS NULL OR care_end_date IS NULL OR care_start_date < care_end_date",
            name="check_care_dates"
        ),
        Index("idx_matching_requests_patient", "patient_id"),
        Index("idx_matching_requests_active", "is_active", postgresql_where=Column("is_active") == True),
        Index("idx_matching_requests_care_dates", "care_start_date", "care_end_date"),
    )


class MatchingResult(Base):
    """AI 추천 결과"""
    
    __tablename__ = "matching_results"
    
    matching_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    request_id = Column(BigInteger, ForeignKey("matching_requests.request_id", ondelete="CASCADE"), nullable=False)
    caregiver_id = Column(BigInteger, ForeignKey("caregivers.caregiver_id", ondelete="CASCADE"), nullable=False)
    
    total_score = Column(Float, nullable=False)
    grade = Column(SQLEnum(GradeEnum, name="grade_enum"), nullable=False)
    ai_comment = Column(Text, nullable=True)
    
    status = Column(SQLEnum(MatchingStatusEnum, name="matching_status_enum"), default=MatchingStatusEnum.recommended)
    
    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    request = relationship("MatchingRequest", back_populates="matching_results")
    caregiver = relationship("Caregiver", back_populates="matching_results")
    reviews = relationship("Review", back_populates="matching", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="matching", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("total_score >= 0 AND total_score <= 100", name="check_score"),
        CheckConstraint(
            "contract_start_date IS NULL OR contract_end_date IS NULL OR contract_start_date < contract_end_date",
            name="check_contract_dates"
        ),
        Index("idx_matching_request", "request_id"),
        Index("idx_matching_caregiver", "caregiver_id"),
        Index("idx_matching_status", "status"),
        Index("idx_matching_score", "total_score"),
    )


class CaregiverAvailability(Base):
    """간병인 가용 시간"""
    
    __tablename__ = "caregiver_availability"
    
    availability_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    caregiver_id = Column(BigInteger, ForeignKey("caregivers.caregiver_id", ondelete="CASCADE"), nullable=False)
    
    day_of_week = Column(String(3), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    caregiver = relationship("Caregiver", back_populates="availability")
    
    __table_args__ = (
        CheckConstraint("day_of_week IN ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')", name="caregiver_availability_day_of_week_check"),
        CheckConstraint("start_time < end_time", name="check_time_range"),
        Index("idx_caregiver_avail", "caregiver_id", "day_of_week", "is_available"),
    )
