"""
일정 관리 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Schedule(Base):
    """일정 모델"""
    
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    schedule_type = Column(String(50))  # 'care', 'medication', 'checkup', 'exercise', etc.
    is_completed = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="schedules")
    caregiver = relationship("Caregiver", back_populates="schedules")
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, title={self.title}, start_time={self.start_time}, completed={self.is_completed})>"
