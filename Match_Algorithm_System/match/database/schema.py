"""
SQLAlchemy ORM Schema for BluedonuLab Caregiver Matching System
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 열거형 값 상수
CARE_LEVELS = ["Low", "Moderate", "High"]
JOB_TITLES = ["Nurse", "Caregiver", "Doctor", "Therapist", "Administrator"]
GENDERS = ["Male", "Female", "Other"]
MATCHING_STATUSES = ["Active", "Completed", "Cancelled", "On Hold"]
PERSONALITY_TYPES = ["공감 중심형", "활동 중심형", "자립형", "전담형", "균형형"]


# =====================================================================
# 기본 데이터 테이블
# =====================================================================

class Resident(Base):
    """주민/환자 정보"""
    __tablename__ = 'residents'

    resident_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(20), nullable=False)  # Male, Female, Other
    admission_date = Column(DateTime, nullable=False)
    room_number = Column(Integer)
    care_level = Column(String(20), nullable=False)  # Low, Moderate, High
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    patient_personality = relationship("PatientPersonality", back_populates="resident", uselist=False)
    matchings = relationship("PersonalityBasedMatching", back_populates="patient")
    reports = relationship("DailyReport", back_populates="resident")

    def __repr__(self):
        return f"<Resident {self.resident_id}: {self.name}>"


class Staff(Base):
    """직원/간병인 정보"""
    __tablename__ = 'staff'

    staff_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(20), nullable=False)  # Male, Female, Other
    job_title = Column(String(50), nullable=False)  # Nurse, Caregiver, Doctor, Therapist, Administrator
    employment_date = Column(DateTime, nullable=False)
    experience_years = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    caregiver_style = relationship("CaregiverStyle", back_populates="staff", uselist=False)
    matchings = relationship("PersonalityBasedMatching", back_populates="caregiver")

    def __repr__(self):
        return f"<Staff {self.staff_id}: {self.name}>"


class Medication(Base):
    """약물 정보"""
    __tablename__ = 'medications'

    medication_id = Column(Integer, primary_key=True)
    medication_name = Column(String(100), nullable=False)
    dosage = Column(String(50))
    prescription_end_date = Column(DateTime)
    resident_id = Column(Integer, ForeignKey('residents.resident_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Medication {self.medication_id}: {self.medication_name}>"


# =====================================================================
# 성향 및 매칭 관련 테이블
# =====================================================================

class PatientPersonality(Base):
    """환자 성향 점수"""
    __tablename__ = 'patient_personality'

    patient_personality_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('residents.resident_id'), unique=True, nullable=False)

    # 성향 점수 (0-100)
    empathy = Column(Float, default=0.0)
    activity = Column(Float, default=0.0)
    patience = Column(Float, default=0.0)
    independence = Column(Float, default=0.0)

    # 성향 분류
    personality_type = Column(String(50))
    description = Column(Text)

    # 메타데이터
    test_completed = Column(Boolean, default=False)
    test_completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    resident = relationship("Resident", back_populates="patient_personality")

    def __repr__(self):
        return f"<PatientPersonality {self.patient_id}>"


class CaregiverStyle(Base):
    """간병인 돌봄 스타일"""
    __tablename__ = 'caregiver_style'

    caregiver_style_id = Column(Integer, primary_key=True)
    caregiver_id = Column(Integer, ForeignKey('staff.staff_id'), unique=True, nullable=False)

    # 스타일 점수 (0-100)
    empathy = Column(Float, default=0.0)
    activity_support = Column(Float, default=0.0)
    patience = Column(Float, default=0.0)
    independence_support = Column(Float, default=0.0)

    # 평균 점수
    average_score = Column(Float, default=0.0)

    # 스타일 분류
    caregiver_type = Column(String(50))
    description = Column(Text)

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    staff = relationship("Staff", back_populates="caregiver_style")

    def __repr__(self):
        return f"<CaregiverStyle {self.caregiver_id}>"


class PersonalityBasedMatching(Base):
    """성향 기반 매칭 결과"""
    __tablename__ = 'personality_based_matching'

    matching_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('residents.resident_id'), nullable=False)
    caregiver_id = Column(Integer, ForeignKey('staff.staff_id'), nullable=False)

    # 매칭 점수
    matching_score = Column(Float, nullable=False)
    grade = Column(String(5))  # A+, A, B+, B, C

    # 상세 점수
    care_compatibility = Column(Float, default=0.0)
    personality_compatibility = Column(Float, default=0.0)
    empathy_match = Column(Float, default=0.0)
    activity_match = Column(Float, default=0.0)
    patience_match = Column(Float, default=0.0)
    independence_match = Column(Float, default=0.0)

    # 매칭 상태
    status = Column(String(20), default="Active")  # Active, Completed, Cancelled, On Hold
    matching_reason = Column(Text)

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    patient = relationship("Resident", back_populates="matchings")
    caregiver = relationship("Staff", back_populates="matchings")
    history = relationship("MatchingHistory", back_populates="matching")
    reports = relationship("DailyReport", back_populates="matching")

    def __repr__(self):
        return f"<PersonalityBasedMatching {self.matching_id}: Patient {self.patient_id} - Caregiver {self.caregiver_id}>"


class MatchingHistory(Base):
    """매칭 이력 기록"""
    __tablename__ = 'matching_history'

    history_id = Column(Integer, primary_key=True)
    matching_id = Column(Integer, ForeignKey('personality_based_matching.matching_id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('residents.resident_id'), nullable=False)
    caregiver_id = Column(Integer, ForeignKey('staff.staff_id'), nullable=False)

    # 상태 기록
    status = Column(String(20), nullable=False)  # Active, Completed, Cancelled, On Hold
    status_reason = Column(String(255))

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    matching = relationship("PersonalityBasedMatching", back_populates="history")

    def __repr__(self):
        return f"<MatchingHistory {self.history_id}>"


# =====================================================================
# 리포트 관련 테이블
# =====================================================================

class DailyReport(Base):
    """일일 리포트"""
    __tablename__ = 'daily_report'

    report_id = Column(Integer, primary_key=True)
    matching_id = Column(Integer, ForeignKey('personality_based_matching.matching_id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('residents.resident_id'), nullable=False)

    # 리포트 내용
    report_date = Column(DateTime, nullable=False)
    content = Column(Text)
    mood = Column(String(50))  # Happy, Neutral, Sad, etc.
    activities = Column(Text)  # 활동 기록
    medications_taken = Column(Boolean, default=True)
    notes = Column(Text)

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))  # 간병인 이름

    # 관계
    matching = relationship("PersonalityBasedMatching", back_populates="reports")
    resident = relationship("Resident", back_populates="reports")

    def __repr__(self):
        return f"<DailyReport {self.report_id}>"


# =====================================================================
# 인덱스 정의
# =====================================================================

def create_indexes():
    """주요 인덱스 생성 (자동으로 SQLAlchemy가 처리)"""
    # ForeignKey 인덱스는 자동으로 생성됨
    # 추가 인덱스는 migration에서 정의
    pass
