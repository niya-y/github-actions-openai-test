"""
케어 활동 로그 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CareActivity(Base):
    """케어 활동 로그 모델"""
    
    __tablename__ = "care_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id", ondelete="SET NULL"), nullable=True)
    
    activity_type = Column(String(50), nullable=False)  # 'blood_pressure', 'meal', 'medication', 'exercise', etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    data = Column(JSONB, default=dict)  # 활동별 상세 데이터 (혈압 수치, 식사량 등)
    notes = Column(Text)  # 추가 메모
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="activities")
    caregiver = relationship("Caregiver", back_populates="activities")
    
    def __repr__(self):
        return f"<CareActivity(id={self.id}, patient_id={self.patient_id}, type={self.activity_type}, timestamp={self.timestamp})>"
