"""
간병인 관련 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Caregiver(Base):
    """간병인 모델"""
    
    __tablename__ = "caregivers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # 'male' or 'female'
    phone = Column(String(20))
    email = Column(String(255))
    
    experience_years = Column(Integer, nullable=False, default=0)
    certifications = Column(JSONB, default=list)  # 자격증 목록
    specialties = Column(JSONB, default=list)  # 전문 분야
    available_time_slots = Column(JSONB, default=list)  # 가능 시간대
    location = Column(String(255), index=True)  # 활동 지역
    
    rating = Column(DECIMAL(3, 2), default=0.0, index=True)  # 평점
    review_count = Column(Integer, default=0)
    skills = Column(JSONB, default=list)  # 기술/능력
    tags = Column(JSONB, default=list)  # 태그
    
    hourly_rate = Column(Integer)  # 시간당 비용
    is_active = Column(Boolean, default=True, index=True)  # 활동 상태
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    matching_history = relationship("MatchingHistory", back_populates="caregiver", cascade="all, delete-orphan")
    activities = relationship("CareActivity", back_populates="caregiver")
    schedules = relationship("Schedule", back_populates="caregiver")
    
    def __repr__(self):
        return f"<Caregiver(id={self.id}, name={self.name}, rating={self.rating}, location={self.location})>"


class CaregiverRequirements(Base):
    """간병인 요구사항 모델"""
    
    __tablename__ = "caregiver_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    
    care_type = Column(String(50), nullable=False)  # 'nursing-aide', 'nursing-assistant', 'nurse'
    time_slots = Column(JSONB, nullable=False, default=list)  # 희망 시간대
    gender_preference = Column(String(10))  # 'any', 'male', 'female'
    experience_level = Column(String(20))  # 'less1', '1-3', '3-5', '5plus'
    required_skills = Column(JSONB, default=list)  # 필요 기술
    budget = Column(Integer)  # 예산
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="requirements")
    
    def __repr__(self):
        return f"<CaregiverRequirements(id={self.id}, patient_id={self.patient_id}, care_type={self.care_type})>"
