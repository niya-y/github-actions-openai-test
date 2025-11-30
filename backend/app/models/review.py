"""
리뷰 모델 (schema.sql 기반)
"""

from sqlalchemy import Column, BigInteger, Integer, DateTime, CheckConstraint, Index, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import UserTypeEnum


class Review(Base):
    """리뷰 및 평가"""
    
    __tablename__ = "reviews"
    
    review_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    matching_id = Column(BigInteger, ForeignKey("matching_results.matching_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reviewer_type = Column(SQLEnum(UserTypeEnum, name="user_type_enum"), nullable=False)
    
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    matching = relationship("MatchingResult", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews", foreign_keys=[reviewer_id])
    
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="reviews_rating_check"),
        Index("idx_reviews_matching", "matching_id"),
        Index("idx_reviews_rating", "rating"),
    )
