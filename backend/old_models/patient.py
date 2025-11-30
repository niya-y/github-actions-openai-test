"""
환자 관련 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Patient(Base):
    """환자 모델"""
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # 'male' or 'female'
    relationship_to_guardian = Column(String(50), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="patients")
    health_status = relationship("PatientHealthStatus", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    details = relationship("PatientDetails", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    requirements = relationship("CaregiverRequirements", back_populates="patient", cascade="all, delete-orphan")
    matching_history = relationship("MatchingHistory", back_populates="patient", cascade="all, delete-orphan")
    activities = relationship("CareActivity", back_populates="patient", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.name}, age={self.age}, gender={self.gender})>"


class PatientHealthStatus(Base):
    """환자 건강 상태 모델"""
    
    __tablename__ = "patient_health_status"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, unique=True)
    diagnoses = Column(JSONB, default=list)  # 진단명 목록
    mobility_level = Column(String(50))  # 거동 능력
    cognitive_level = Column(String(50))  # 인지 기능
    adl = Column(JSONB, default=dict)  # 일상생활 수행능력
    medical_history = Column(Text)  # 병력
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="health_status")
    
    def __repr__(self):
        return f"<PatientHealthStatus(id={self.id}, patient_id={self.patient_id})>"


class PatientDetails(Base):
    """환자 상세 정보 모델"""
    
    __tablename__ = "patient_details"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, unique=True)
    special_care_needs = Column(JSONB, default=list)  # 특별 케어 사항
    medications = Column(JSONB, default=list)  # 복용 약물
    allergies = Column(JSONB, default=list)  # 알레르기
    assistive_devices = Column(JSONB, default=list)  # 보조기구
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="details")
    
    def __repr__(self):
        return f"<PatientDetails(id={self.id}, patient_id={self.patient_id})>"
