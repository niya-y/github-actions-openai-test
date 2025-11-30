"""
케어 실행 모델 (schema.sql 기반)
"""

from sqlalchemy import Column, BigInteger, String, Integer, Float, Date, Time, Boolean, DateTime, Enum as SQLEnum, CheckConstraint, Index, ForeignKey, Text, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# Enum 타입 정의
class MealTypeEnum(str, enum.Enum):
    """식사 타입"""
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class ReportTypeEnum(str, enum.Enum):
    """보고서 타입"""
    weekly = "weekly"
    monthly = "monthly"


class CareCategoryEnum(str, enum.Enum):
    """케어 카테고리"""
    medication = "medication"
    meal = "meal"
    exercise = "exercise"
    vital_check = "vital_check"
    hygiene = "hygiene"
    other = "other"


class Schedule(Base):
    """케어 일정"""
    
    __tablename__ = "schedules"
    
    schedule_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    matching_id = Column(BigInteger, ForeignKey("matching_results.matching_id", ondelete="CASCADE"), nullable=True)
    
    care_date = Column(Date, nullable=False)
    is_ai_generated = Column(Boolean, default=True)
    
    status = Column(String(20), default="scheduled")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="schedules")
    matching = relationship("MatchingResult", back_populates="schedules")
    care_logs = relationship("CareLog", back_populates="schedule", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("status IN ('scheduled', 'completed', 'cancelled')", name="schedules_status_check"),
        Index("idx_schedules_patient", "patient_id"),
        Index("idx_schedules_matching", "matching_id"),
        Index("idx_schedules_date", "care_date", "status"),
    )


class CareLog(Base):
    """수행 체크리스트"""
    
    __tablename__ = "care_logs"
    
    log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(BigInteger, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), nullable=False)
    
    category = Column(SQLEnum(CareCategoryEnum, name="care_category_enum"), nullable=False)
    task_name = Column(String(100), nullable=False)
    scheduled_time = Column(Time, nullable=True)
    
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    schedule = relationship("Schedule", back_populates="care_logs")
    
    __table_args__ = (
        Index("idx_care_logs_schedule", "schedule_id"),
        Index("idx_care_logs_category", "category"),
    )


class MealPlan(Base):
    """추천 식단"""
    
    __tablename__ = "meal_plans"
    
    plan_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    
    meal_date = Column(Date, nullable=False)
    meal_type = Column(SQLEnum(MealTypeEnum, name="meal_type_enum"), nullable=False)
    
    menu_name = Column(String(200), nullable=False)
    ingredients = Column(Text, nullable=True)
    nutrition_info = Column(JSONB, nullable=True)
    cooking_tips = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="meal_plans")
    
    __table_args__ = (
        Index("idx_meal_plans_patient_date", "patient_id", "meal_date"),
    )


class CareReport(Base):
    """케어 보고서"""
    
    __tablename__ = "care_reports"
    
    report_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    
    report_type = Column(SQLEnum(ReportTypeEnum, name="report_type_enum"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    medication_completion_rate = Column(Float, nullable=True)
    meal_completion_rate = Column(Float, nullable=True)
    health_status_summary = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="care_reports")
    
    __table_args__ = (
        CheckConstraint("start_date < end_date", name="check_report_dates"),
        CheckConstraint("medication_completion_rate IS NULL OR (medication_completion_rate >= 0 AND medication_completion_rate <= 100)", name="check_med_rate"),
        CheckConstraint("meal_completion_rate IS NULL OR (meal_completion_rate >= 0 AND meal_completion_rate <= 100)", name="check_meal_rate"),
        Index("idx_care_reports_patient", "patient_id"),
    )
