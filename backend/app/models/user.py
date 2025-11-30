"""
사용자 관련 데이터베이스 모델 (schema.sql 기반)
"""

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Enum as SQLEnum, CheckConstraint, Index, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# Enum 타입 정의
class UserTypeEnum(str, enum.Enum):
    """사용자 유형"""
    guardian = "guardian"
    caregiver = "caregiver"


class SocialProviderEnum(str, enum.Enum):
    """소셜 로그인 제공자"""
    kakao = "kakao"
    naver = "naver"
    google = "google"
    apple = "apple"


class User(Base):
    """통합 사용자 모델 (보호자 + 간병인)"""
    
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # 계정 정보
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    
    # 기본 정보
    name = Column(String(50), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    
    # 사용자 유형
    user_type = Column(SQLEnum(UserTypeEnum, name="user_type_enum"), nullable=False)
    profile_image_url = Column(String, nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    personality_tests = relationship("PersonalityTest", back_populates="user", cascade="all, delete-orphan")
    guardian = relationship("Guardian", back_populates="user", uselist=False, cascade="all, delete-orphan")
    caregiver = relationship("Caregiver", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    
    __table_args__ = (
        CheckConstraint(
            "(email IS NOT NULL) OR (phone_number IS NOT NULL)",
            name="check_email_or_phone"
        ),
        Index("idx_users_email", "email", postgresql_where=Column("email").isnot(None)),
        Index("idx_users_phone", "phone_number", postgresql_where=Column("phone_number").isnot(None)),
        Index("idx_users_type", "user_type"),
        Index("idx_users_active", "is_active", postgresql_where=Column("is_active") == True),
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, name={self.name}, type={self.user_type})>"


class SocialAccount(Base):
    """소셜 로그인 연동 정보"""
    
    __tablename__ = "social_accounts"
    
    social_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    provider = Column(SQLEnum(SocialProviderEnum, name="social_provider_enum"), nullable=False)
    provider_user_id = Column(String(100), nullable=False)
    
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="social_accounts")
    
    __table_args__ = (
        Index("idx_social_user", "user_id"),
        Index("idx_social_provider", "provider", "provider_user_id"),
        {"schema": None}  # 기본 스키마 사용
    )
    
    def __repr__(self):
        return f"<SocialAccount(social_id={self.social_id}, provider={self.provider}, user_id={self.user_id})>"


class PersonalityTest(Base):
    """성향 테스트 결과"""
    
    __tablename__ = "personality_tests"
    
    test_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    # 성향 점수
    empathy_score = Column(Float, default=0)
    activity_score = Column(Float, default=0)
    patience_score = Column(Float, default=0)
    independence_score = Column(Float, default=0)
    
    # AI 분석
    raw_test_answers = Column(JSONB, nullable=True)
    ai_analysis_text = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="personality_tests")
    
    __table_args__ = (
        CheckConstraint("empathy_score >= 0 AND empathy_score <= 100", name="check_test_empathy"),
        CheckConstraint("activity_score >= 0 AND activity_score <= 100", name="check_test_activity"),
        CheckConstraint("patience_score >= 0 AND patience_score <= 100", name="check_test_patience"),
        CheckConstraint("independence_score >= 0 AND independence_score <= 100", name="check_test_independence"),
        Index("idx_personality_tests_user", "user_id"),
    )
    
    def __repr__(self):
        return f"<PersonalityTest(test_id={self.test_id}, user_id={self.user_id})>"
