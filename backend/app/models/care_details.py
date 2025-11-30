"""
성향 및 케어 상세 정보 모델 (schema.sql 기반)
"""

from sqlalchemy import Column, BigInteger, String, Integer, Float, DateTime, CheckConstraint, Index, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class PatientPersonality(Base):
    """환자 성향"""
    
    __tablename__ = "patient_personality"
    
    personality_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    empathy_score = Column(Float, default=0)
    activity_score = Column(Float, default=0)
    patience_score = Column(Float, default=0)
    independence_score = Column(Float, default=0)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="personality")
    
    __table_args__ = (
        CheckConstraint("empathy_score >= 0 AND empathy_score <= 100", name="check_patient_empathy"),
        CheckConstraint("activity_score >= 0 AND activity_score <= 100", name="check_patient_activity"),
        CheckConstraint("patience_score >= 0 AND patience_score <= 100", name="check_patient_patience"),
        CheckConstraint("independence_score >= 0 AND independence_score <= 100", name="check_patient_independence"),
        Index("idx_patient_personality", "patient_id"),
    )


class CaregiverPersonality(Base):
    """간병인 성향"""
    
    __tablename__ = "caregiver_personality"
    
    personality_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    caregiver_id = Column(BigInteger, ForeignKey("caregivers.caregiver_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    empathy_score = Column(Float, default=0)
    activity_score = Column(Float, default=0)
    patience_score = Column(Float, default=0)
    independence_score = Column(Float, default=0)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    caregiver = relationship("Caregiver", back_populates="personality")
    
    __table_args__ = (
        CheckConstraint("empathy_score >= 0 AND empathy_score <= 100", name="check_caregiver_empathy"),
        CheckConstraint("activity_score >= 0 AND activity_score <= 100", name="check_caregiver_activity"),
        CheckConstraint("patience_score >= 0 AND patience_score <= 100", name="check_caregiver_patience"),
        CheckConstraint("independence_score >= 0 AND independence_score <= 100", name="check_caregiver_independence"),
        Index("idx_caregiver_personality", "caregiver_id"),
    )


class HealthCondition(Base):
    """질병 정보"""

    __tablename__ = "health_conditions"

    condition_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)

    disease_name = Column(String(100), nullable=False)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="health_conditions")

    __table_args__ = (
        Index("idx_health_patient", "patient_id"),
    )


class Medication(Base):
    """투약 정보"""
    
    __tablename__ = "medications"
    
    med_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    dosage = Column(String(50), nullable=True)
    frequency = Column(String(50), nullable=True)
    intake_method = Column(String(100), nullable=True)
    
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="medications")
    
    __table_args__ = (
        Index("idx_medications_patient", "patient_id"),
    )


class DietaryPreference(Base):
    """식사 정보"""
    
    __tablename__ = "dietary_preferences"
    
    diet_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    
    allergy_foods = Column(ARRAY(Text), nullable=True)
    restriction_foods = Column(ARRAY(Text), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="dietary_preferences")
    
    __table_args__ = (
        Index("idx_dietary_patient", "patient_id"),
    )
