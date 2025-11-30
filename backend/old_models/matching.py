"""
매칭 관련 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class MatchingHistory(Base):
    """매칭 히스토리 모델"""
    
    __tablename__ = "matching_history"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    match_score = Column(DECIMAL(5, 2), nullable=False)  # 매칭 점수 (0.00 ~ 100.00)
    algorithm_version = Column(String(50))  # 알고리즘 버전
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    status = Column(
        String(20),
        default="pending",
        nullable=False
    )  # 'pending', 'accepted', 'rejected', 'completed'
    
    notes = Column(Text)  # 추가 메모
    
    # Relationships
    patient = relationship("Patient", back_populates="matching_history")
    caregiver = relationship("Caregiver", back_populates="matching_history")
    
    def __repr__(self):
        return f"<MatchingHistory(id={self.id}, patient_id={self.patient_id}, caregiver_id={self.caregiver_id}, score={self.match_score})>"
