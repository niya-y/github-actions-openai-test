"""
프로필 관련 데이터베이스 모델 (schema.sql 기반)
"""

from sqlalchemy import Column, BigInteger, String, Integer, Date, Boolean, DateTime, Enum as SQLEnum, CheckConstraint, Index, ForeignKey, DECIMAL, Text, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# Enum 타입 정의
class GenderEnum(str, enum.Enum):
    """성별"""
    Male = "Male"
    Female = "Female"


class CareLevelEnum(str, enum.Enum):
    """장기요양등급"""
    LEVEL_1 = "1등급"
    LEVEL_2 = "2등급"
    LEVEL_3 = "3등급"
    LEVEL_4 = "4등급"
    LEVEL_5 = "5등급"
    COGNITIVE = "인지지원등급"
    OUT_OF_GRADE = "등급외"


class Guardian(Base):
    """보호자 상세 정보"""
    
    __tablename__ = "guardians"
    
    guardian_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    address = Column(String(255), nullable=True)
    relationship_to_patient = Column(String(50), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="guardian")
    patients = relationship("Patient", back_populates="guardian", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_guardians_user", "user_id"),
    )
    
    def __repr__(self):
        return f"<Guardian(guardian_id={self.guardian_id}, user_id={self.user_id})>"


class Patient(Base):
    """환자(시니어) 상세 정보"""
    
    __tablename__ = "patients"
    
    patient_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    guardian_id = Column(BigInteger, ForeignKey("guardians.guardian_id", ondelete="CASCADE"), nullable=False)
    
    # 기본 정보
    name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(SQLEnum(GenderEnum, name="gender_enum"), nullable=False)
    
    # 신체 정보
    height = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    
    # 주소 및 지역
    care_address = Column(String(255), nullable=False)
    region_code = Column(String(50), nullable=False)
    
    # 요양 정보
    care_level = Column(SQLEnum(CareLevelEnum, name="care_level_enum"), nullable=True)
    profile_image_url = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    guardian = relationship("Guardian", back_populates="patients")
    personality = relationship("PatientPersonality", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    health_conditions = relationship("HealthCondition", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    dietary_preferences = relationship("DietaryPreference", back_populates="patient", cascade="all, delete-orphan")
    matching_requests = relationship("MatchingRequest", back_populates="patient", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="patient", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="patient", cascade="all, delete-orphan")
    care_reports = relationship("CareReport", back_populates="patient", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("birth_date <= CURRENT_DATE", name="check_birth_date"),
        CheckConstraint("height IS NULL OR (height > 0 AND height < 300)", name="check_height"),
        CheckConstraint("weight IS NULL OR (weight > 0 AND weight < 500)", name="check_weight"),
        Index("idx_patients_guardian", "guardian_id"),
        Index("idx_patients_region", "region_code"),
        Index("idx_patients_care_level", "care_level"),
    )
    
    def __repr__(self):
        return f"<Patient(patient_id={self.patient_id}, name={self.name})>"


class Caregiver(Base):
    """간병인 상세 정보"""
    
    __tablename__ = "caregivers"
    
    caregiver_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 경력 및 자격
    experience_years = Column(Integer, default=0)
    certifications = Column(String(255), nullable=True)
    specialties = Column(ARRAY(Text), nullable=True)
    
    # 서비스 지역
    service_region = Column(String(50), nullable=True)
    has_vehicle = Column(Boolean, default=False)
    
    # 시급
    hourly_rate = Column(Integer, nullable=True)
    
    # 평가
    avg_rating = Column(DECIMAL(3, 2), default=0.00)
    total_reviews = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="caregiver")
    personality = relationship("CaregiverPersonality", back_populates="caregiver", uselist=False, cascade="all, delete-orphan")
    availability = relationship("CaregiverAvailability", back_populates="caregiver", cascade="all, delete-orphan")
    matching_results = relationship("MatchingResult", back_populates="caregiver", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("experience_years >= 0", name="check_experience"),
        CheckConstraint("hourly_rate IS NULL OR (hourly_rate > 0 AND hourly_rate <= 1000000)", name="check_hourly_rate"),
        CheckConstraint("avg_rating >= 0 AND avg_rating <= 5", name="check_avg_rating"),
        Index("idx_caregivers_user", "user_id"),
        Index("idx_caregivers_region", "service_region"),
        Index("idx_caregivers_rating", "avg_rating"),
    )
    
    def __repr__(self):
        return f"<Caregiver(caregiver_id={self.caregiver_id}, user_id={self.user_id})>"
