# 🗄️ 매칭 시스템 데이터베이스 설계

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [테이블 설계](#테이블-설계)
3. [데이터 흐름](#데이터-흐름)
4. [SQLAlchemy 구현](#sqlalchemy-구현)
5. [사용 예제](#사용-예제)

---

## 시스템 개요

### 매칭 프로세스
```
1. 사용자 등록
   ├─ 환자 정보 입력 (기본 정보, 케어 요구사항)
   └─ 간병인 정보 입력 (경력, 자격증, 스타일)

2. 성향 진단
   ├─ 환자: 12개 질문 → 4개 성향 축 점수
   └─ 간병인: 경력/자격 → 케어 스타일 점수

3. AI 매칭
   ├─ 최적 모델(XGBoost V3) 로드
   ├─ 성향 + 케어 호환도 계산
   └─ 추천 간병인 제시 (상위 5명)

4. 매칭 확정
   ├─ 사용자가 간병인 선택
   ├─ 계약 생성
   └─ 매칭 이력 저장
```

---

## 테이블 설계

### 1️⃣ Users 테이블
**역할**: 환자와 간병인 모두의 계정 관리

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,

    -- 기본 정보
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,

    -- 타입 (environment: 환자 or 간병인)
    user_type ENUM('patient', 'caregiver') NOT NULL,

    -- 상태
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',

    -- 타임스탬프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- 인덱스
    INDEX idx_user_type (user_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**예시 데이터:**
```
user_id | name      | phone        | user_type | status
1       | 김영희    | 010-1234-5678| patient   | active
2       | 이미숙    | 010-2345-6789| caregiver | active
3       | 박지은    | 010-3456-7890| caregiver | active
```

---

### 2️⃣ Patients 테이블
**역할**: 환자의 상세 정보

```sql
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER UNIQUE NOT NULL,

    -- 건강 정보
    age INTEGER,
    gender ENUM('M', 'F'),
    medical_condition VARCHAR(500),  -- 주요 질병 (당뇨병, 고혈압 등)
    mobility_level ENUM('independent', 'partial', 'fully_dependent'),

    -- 케어 요구사항
    care_level ENUM('light', 'moderate', 'heavy') NOT NULL,
    required_hours_per_day INTEGER,  -- 하루 필요 간병 시간
    special_needs TEXT,  -- 특수한 요구사항 (언어, 종교 등)

    -- 선호도
    preferred_gender ENUM('M', 'F', 'no_preference') DEFAULT 'no_preference',
    preferred_age_range VARCHAR(50),  -- "30-50세" 등

    -- 주소 정보
    address VARCHAR(500),
    district VARCHAR(100),

    -- 타임스탐프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_care_level (care_level),
    INDEX idx_address (address)
);
```

**예시 데이터:**
```
patient_id | user_id | age | care_level | required_hours_per_day
1          | 1       | 75  | moderate   | 8
2          | 4       | 82  | heavy      | 12
```

---

### 3️⃣ PatientPersonality 테이블
**역할**: 환자의 성향 점수 저장 (4개 축)

```sql
CREATE TABLE patient_personality (
    personality_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    patient_id INTEGER UNIQUE NOT NULL,

    -- 4가지 성향 축 (0-100)
    empathy FLOAT NOT NULL,          -- 공감도 (감정적 유대감)
    patience FLOAT NOT NULL,         -- 인내심 (반복되는 일에 대응)
    activity FLOAT NOT NULL,         -- 활동성 (신체 활동)
    independence FLOAT NOT NULL,     -- 자립도 (독립적 생활)

    -- 성향 유형
    personality_type VARCHAR(50),    -- "공감형", "활동형" 등

    -- 테스트 정보
    test_answers JSON,               -- 12개 질문 답변 저장
    test_completed_at DATETIME,      -- 테스트 완료 시간

    -- 타임스탐프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_personality_type (personality_type)
);
```

**예시 데이터:**
```
personality_id | patient_id | empathy | patience | activity | independence | personality_type
1              | 1          | 72.5    | 68.3     | 45.2     | 55.8         | 공감인내형
2              | 2          | 60.1    | 75.4     | 70.2     | 48.5         | 인내활동형
```

---

### 4️⃣ Caregivers 테이블
**역할**: 간병인의 상세 정보

```sql
CREATE TABLE caregivers (
    caregiver_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER UNIQUE NOT NULL,

    -- 기본 정보
    age INTEGER,
    gender ENUM('M', 'F'),

    -- 경력
    experience_years INTEGER NOT NULL,  -- 간병 경력 (년)
    experience_level ENUM('entry', 'intermediate', 'expert'),

    -- 자격증
    certifications VARCHAR(500),  -- "간호조무사, 요양보호사" 등

    -- 케어 스타일
    specialization VARCHAR(500),  -- "치매, 신체 활동" 등

    -- 근무 방식
    working_style ENUM('full_time', 'part_time', 'flexible') DEFAULT 'flexible',
    available_hours_per_week INTEGER,

    -- 지역
    area_of_service VARCHAR(500),  -- 서비스 가능 지역

    -- 추가 정보
    has_vehicle BOOLEAN DEFAULT FALSE,
    languages JSON,  -- ["한국어", "영어"]

    -- 타임스탐프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_experience_level (experience_level),
    INDEX idx_area (area_of_service(100)),
    INDEX idx_certifications (certifications(100))
);
```

**예시 데이터:**
```
caregiver_id | user_id | experience_years | experience_level | certifications
1            | 2       | 5                | intermediate     | 요양보호사
2            | 3       | 8                | expert           | 간호조무사, 요양보호사
```

---

### 5️⃣ CaregiverPersonality 테이블
**역할**: 간병인의 성향 점수 (자동 계산 또는 자체 진단)

```sql
CREATE TABLE caregiver_personality (
    personality_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    caregiver_id INTEGER UNIQUE NOT NULL,

    -- 4가지 성향 축 (0-100)
    empathy FLOAT,                   -- 공감도
    patience FLOAT,                  -- 인내심
    activity FLOAT,                  -- 활동성
    independence FLOAT,              -- 독립적 간병 능력

    -- 계산 방식
    calculation_method ENUM('self_test', 'auto_calculated', 'manual_input') DEFAULT 'auto_calculated',

    -- 경력 기반 자동 계산값 (경력이 높을수록 점수 높음)
    -- 예: experience_years * 10 + certifications_count * 5

    -- 타임스탐프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (caregiver_id) REFERENCES caregivers(caregiver_id) ON DELETE CASCADE
);
```

**예시 데이터:**
```
personality_id | caregiver_id | empathy | patience | activity | independence | calculation_method
1              | 1            | 78.5    | 82.3     | 65.4     | 75.2         | auto_calculated
2              | 2            | 85.2    | 88.1     | 72.5     | 82.0         | auto_calculated
```

---

### 6️⃣ MatchingResults 테이블
**역할**: AI 매칭 결과 저장

```sql
CREATE TABLE matching_results (
    matching_id INTEGER PRIMARY KEY AUTO_INCREMENT,

    -- 매칭 대상
    patient_id INTEGER NOT NULL,
    caregiver_id INTEGER NOT NULL,

    -- 매칭 점수
    total_score FLOAT NOT NULL,          -- 최종 점수 (0-100)
    personality_compatibility FLOAT,    -- 성향 호환도 (60% 가중치)
    care_compatibility FLOAT,           -- 케어 호환도 (40% 가중치)

    -- 매칭 등급
    grade ENUM('A+', 'A', 'B+', 'B', 'C') NOT NULL,
    -- A+: 95-100, A: 85-94, B+: 75-84, B: 65-74, C: <65

    -- 상태
    status ENUM('recommended', 'selected', 'active', 'completed', 'cancelled') DEFAULT 'recommended',

    -- AI 모델 정보
    model_version VARCHAR(50),  -- "v3_xgboost"
    model_accuracy FLOAT,       -- 이 매칭에 대한 모델의 신뢰도

    -- 타임스탐프
    matching_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    selected_date DATETIME,     -- 사용자가 선택한 시간
    contract_start_date DATE,   -- 계약 시작일
    contract_end_date DATE,     -- 계약 종료일 (null이면 미정)

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (caregiver_id) REFERENCES caregivers(caregiver_id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_caregiver_id (caregiver_id),
    INDEX idx_status (status),
    INDEX idx_grade (grade),
    INDEX idx_total_score (total_score),
    UNIQUE KEY unique_active_matching (patient_id, caregiver_id, status) -- 환자당 활성 매칭은 1개만
);
```

**예시 데이터:**
```
matching_id | patient_id | caregiver_id | total_score | grade | status | model_version
1           | 1          | 1            | 88.6        | A     | selected | v3_xgboost
2           | 1          | 2            | 81.2        | B+    | recommended | v3_xgboost
3           | 1          | 3            | 76.5        | B+    | recommended | v3_xgboost
4           | 2          | 1            | 72.3        | B     | recommended | v3_xgboost
5           | 2          | 2            | 85.1        | A     | selected | v3_xgboost
```

---

### 7️⃣ MatchingHistory 테이블
**역할**: 모든 매칭 변경 이력 추적 (감사 목적)

```sql
CREATE TABLE matching_history (
    history_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    matching_id INTEGER NOT NULL,

    -- 변경 정보
    action VARCHAR(50) NOT NULL,  -- "created", "selected", "cancelled", "completed"
    old_status VARCHAR(50),
    new_status VARCHAR(50),

    -- 변경 사유
    reason TEXT,  -- "사용자 요청", "계약 종료" 등
    changed_by VARCHAR(100),  -- 누가 변경했는지 (시스템/사용자)

    -- 상세 정보
    details JSON,  -- 추가 정보 저장

    -- 타임스탐프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (matching_id) REFERENCES matching_results(matching_id) ON DELETE CASCADE,
    INDEX idx_matching_id (matching_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);
```

**예시 데이터:**
```
history_id | matching_id | action   | old_status  | new_status | reason
1          | 1           | created  | NULL        | recommended | AI 매칭 완료
2          | 1           | selected | recommended | selected   | 사용자 선택
3          | 1           | started  | selected    | active     | 계약 시작
```

---

### 8️⃣ MatchingRecommendations 테이블 (선택사항)
**역할**: 매칭 추천 로그 (성능 분석용)

```sql
CREATE TABLE matching_recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTO_INCREMENT,

    -- 추천 정보
    patient_id INTEGER NOT NULL,
    caregiver_id INTEGER NOT NULL,

    -- 점수 상세
    score FLOAT NOT NULL,
    rank INTEGER,  -- 추천 순위 (1위, 2위, 3위...)

    -- 클릭 여부 (사용자 반응)
    was_clicked BOOLEAN DEFAULT FALSE,
    was_selected BOOLEAN DEFAULT FALSE,

    -- AI 모델
    model_version VARCHAR(50),

    -- 타임스탐프
    recommended_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (caregiver_id) REFERENCES caregivers(caregiver_id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_recommended_at (recommended_at)
);
```

---

## 데이터 흐름

### 신규 매칭 프로세스

```
1️⃣ 사용자 등록
   INSERT INTO users (name, phone, user_type)
   INSERT INTO patients (user_id, care_level, ...)  또는
   INSERT INTO caregivers (user_id, experience_years, ...)

2️⃣ 성향 진단
   INSERT INTO patient_personality (patient_id, empathy, patience, ...)
   INSERT INTO caregiver_personality (caregiver_id, empathy, patience, ...)

3️⃣ AI 매칭 (Python)
   SELECT * FROM patient_personality WHERE patient_id = ?
   SELECT * FROM caregiver_personality
   -- XGBoost 모델로 점수 계산
   INSERT INTO matching_results (patient_id, caregiver_id, total_score, ...)
   INSERT INTO matching_recommendations (patient_id, caregiver_id, score, rank, ...)

4️⃣ 사용자 선택
   UPDATE matching_results
   SET status = 'selected', selected_date = NOW()
   WHERE matching_id = ?

   INSERT INTO matching_history (matching_id, action, new_status, ...)

5️⃣ 계약 시작
   UPDATE matching_results
   SET status = 'active', contract_start_date = ?
   WHERE matching_id = ?

   INSERT INTO matching_history (matching_id, action, new_status, ...)
```

---

## SQLAlchemy 구현

### models.py
```python
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(120), unique=True)
    user_type = Column(Enum('patient', 'caregiver'), nullable=False)
    status = Column(Enum('active', 'inactive', 'suspended'), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    patient = relationship('Patient', back_populates='user', uselist=False)
    caregiver = relationship('Caregiver', back_populates='user', uselist=False)


class Patient(Base):
    __tablename__ = 'patients'

    patient_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(Enum('M', 'F'))
    medical_condition = Column(String(500))
    mobility_level = Column(Enum('independent', 'partial', 'fully_dependent'))
    care_level = Column(Enum('light', 'moderate', 'heavy'), nullable=False)
    required_hours_per_day = Column(Integer)
    special_needs = Column(String(1000))
    preferred_gender = Column(Enum('M', 'F', 'no_preference'), default='no_preference')
    preferred_age_range = Column(String(50))
    address = Column(String(500))
    district = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    user = relationship('User', back_populates='patient')
    personality = relationship('PatientPersonality', back_populates='patient', uselist=False)
    matching_results = relationship('MatchingResult', back_populates='patient', foreign_keys='MatchingResult.patient_id')


class PatientPersonality(Base):
    __tablename__ = 'patient_personality'

    personality_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), unique=True, nullable=False)
    empathy = Column(Float, nullable=False)
    patience = Column(Float, nullable=False)
    activity = Column(Float, nullable=False)
    independence = Column(Float, nullable=False)
    personality_type = Column(String(50))
    test_answers = Column(JSON)
    test_completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    patient = relationship('Patient', back_populates='personality')


class Caregiver(Base):
    __tablename__ = 'caregivers'

    caregiver_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(Enum('M', 'F'))
    experience_years = Column(Integer, nullable=False)
    experience_level = Column(Enum('entry', 'intermediate', 'expert'))
    certifications = Column(String(500))
    specialization = Column(String(500))
    working_style = Column(Enum('full_time', 'part_time', 'flexible'), default='flexible')
    available_hours_per_week = Column(Integer)
    area_of_service = Column(String(500))
    has_vehicle = Column(Boolean, default=False)
    languages = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    user = relationship('User', back_populates='caregiver')
    personality = relationship('CaregiverPersonality', back_populates='caregiver', uselist=False)
    matching_results = relationship('MatchingResult', back_populates='caregiver', foreign_keys='MatchingResult.caregiver_id')


class CaregiverPersonality(Base):
    __tablename__ = 'caregiver_personality'

    personality_id = Column(Integer, primary_key=True)
    caregiver_id = Column(Integer, ForeignKey('caregivers.caregiver_id'), unique=True, nullable=False)
    empathy = Column(Float)
    patience = Column(Float)
    activity = Column(Float)
    independence = Column(Float)
    calculation_method = Column(Enum('self_test', 'auto_calculated', 'manual_input'), default='auto_calculated')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    caregiver = relationship('Caregiver', back_populates='personality')


class MatchingResult(Base):
    __tablename__ = 'matching_results'

    matching_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    caregiver_id = Column(Integer, ForeignKey('caregivers.caregiver_id'), nullable=False)
    total_score = Column(Float, nullable=False)
    personality_compatibility = Column(Float)
    care_compatibility = Column(Float)
    grade = Column(Enum('A+', 'A', 'B+', 'B', 'C'), nullable=False)
    status = Column(Enum('recommended', 'selected', 'active', 'completed', 'cancelled'), default='recommended')
    model_version = Column(String(50))
    model_accuracy = Column(Float)
    matching_date = Column(DateTime, default=datetime.utcnow)
    selected_date = Column(DateTime)
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    patient = relationship('Patient', back_populates='matching_results', foreign_keys=[patient_id])
    caregiver = relationship('Caregiver', back_populates='matching_results', foreign_keys=[caregiver_id])
    history = relationship('MatchingHistory', back_populates='matching_result')

    # 제약조건
    __table_args__ = (
        UniqueConstraint('patient_id', 'caregiver_id', 'status', name='unique_active_matching'),
    )


class MatchingHistory(Base):
    __tablename__ = 'matching_history'

    history_id = Column(Integer, primary_key=True)
    matching_id = Column(Integer, ForeignKey('matching_results.matching_id'), nullable=False)
    action = Column(String(50), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50))
    reason = Column(String(500))
    changed_by = Column(String(100))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    matching_result = relationship('MatchingResult', back_populates='history')
```

---

## 사용 예제

### 1️⃣ 새로운 환자 등록

```python
from sqlalchemy.orm import Session
from models import User, Patient, PatientPersonality

def register_patient(db: Session, patient_info):
    # 사용자 생성
    user = User(
        name="김영희",
        phone="010-1234-5678",
        user_type="patient"
    )
    db.add(user)
    db.flush()  # user_id 생성

    # 환자 정보 추가
    patient = Patient(
        user_id=user.user_id,
        age=75,
        gender="F",
        care_level="moderate",
        medical_condition="당뇨병, 고혈압",
        address="서울시 강남구"
    )
    db.add(patient)
    db.commit()

    return user, patient
```

### 2️⃣ 환자 성향 진단 후 저장

```python
def save_patient_personality(db: Session, patient_id, test_answers):
    # 12개 질문 답변 → 4개 축 점수 계산
    scores = calculate_personality_from_answers(test_answers)

    personality = PatientPersonality(
        patient_id=patient_id,
        empathy=scores['empathy'],
        patience=scores['patience'],
        activity=scores['activity'],
        independence=scores['independence'],
        personality_type=classify_personality_type(scores),
        test_answers=test_answers
    )
    db.add(personality)
    db.commit()

    return personality
```

### 3️⃣ AI 매칭 실행

```python
import numpy as np
from models import MatchingResult, MatchingRecommendation

def run_matching(db: Session, patient_id):
    # 환자 정보 가져오기
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    patient_personality = patient.personality

    # 모든 간병인 가져오기
    caregivers = db.query(Caregiver).all()

    # XGBoost 모델 로드
    model = load_xgboost_model()  # v3_xgboost

    # 각 간병인과의 매칭 점수 계산
    matching_scores = []

    for caregiver in caregivers:
        caregiver_personality = caregiver.personality

        # 특성 준비
        features = prepare_features(patient_personality, caregiver_personality)

        # 모델 추론
        prediction = model.predict([features])[0]

        # 성향 호환도 계산 (60%)
        personality_compatibility = calculate_personality_compatibility(
            patient_personality,
            caregiver_personality
        )

        # 케어 호환도 계산 (40%)
        care_compatibility = calculate_care_compatibility(
            patient,
            caregiver
        )

        # 최종 점수
        total_score = (personality_compatibility * 0.6) + (care_compatibility * 0.4)
        grade = assign_grade(total_score)

        matching_scores.append({
            'caregiver_id': caregiver.caregiver_id,
            'total_score': total_score,
            'personality_compatibility': personality_compatibility,
            'care_compatibility': care_compatibility,
            'grade': grade,
            'model_version': 'v3_xgboost'
        })

    # 점수로 정렬 후 상위 5개 저장
    matching_scores.sort(key=lambda x: x['total_score'], reverse=True)

    for rank, score_info in enumerate(matching_scores[:5], 1):
        matching = MatchingResult(
            patient_id=patient_id,
            caregiver_id=score_info['caregiver_id'],
            total_score=score_info['total_score'],
            personality_compatibility=score_info['personality_compatibility'],
            care_compatibility=score_info['care_compatibility'],
            grade=score_info['grade'],
            model_version=score_info['model_version'],
            status='recommended'
        )
        db.add(matching)

        # 추천 로그
        recommendation = MatchingRecommendation(
            patient_id=patient_id,
            caregiver_id=score_info['caregiver_id'],
            score=score_info['total_score'],
            rank=rank,
            model_version='v3_xgboost'
        )
        db.add(recommendation)

    db.commit()

    return matching_scores[:5]
```

### 4️⃣ 사용자 매칭 선택 및 기록

```python
from datetime import datetime

def select_matching(db: Session, matching_id):
    matching = db.query(MatchingResult).filter(MatchingResult.matching_id == matching_id).first()

    # 상태 업데이트
    matching.status = 'selected'
    matching.selected_date = datetime.utcnow()

    # 매칭 이력 기록
    history = MatchingHistory(
        matching_id=matching_id,
        action='selected',
        old_status='recommended',
        new_status='selected',
        reason='사용자 선택',
        changed_by='user'
    )

    db.add(history)
    db.commit()

    return matching
```

### 5️⃣ 활성 매칭 조회

```python
def get_active_matching(db: Session, patient_id):
    matching = db.query(MatchingResult).filter(
        (MatchingResult.patient_id == patient_id) &
        (MatchingResult.status.in_(['active', 'selected']))
    ).first()

    if matching:
        caregiver = matching.caregiver
        return {
            'matching_id': matching.matching_id,
            'caregiver_name': caregiver.user.name,
            'caregiver_phone': caregiver.user.phone,
            'matching_score': matching.total_score,
            'status': matching.status,
            'contract_start_date': matching.contract_start_date
        }

    return None
```

---

## 설정 및 초기화

### config.py
```python
import os
from urllib.parse import quote_plus

# PostgreSQL (프로덕션)
POSTGRES_USER = os.getenv('POSTGRES_USER', 'neulbom')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'neulbom_matching')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLite (개발)
# DATABASE_URL = "sqlite:///./matching_system.db"

# SQLAlchemy 설정
SQLALCHEMY_ECHO = True
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
```

### database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """테이블 생성"""
    from models import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 마이그레이션 (Alembic)

```bash
# 초기화
alembic init alembic

# 첫 마이그레이션 생성
alembic revision --autogenerate -m "Initial schema"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 상태 확인
alembic current
```

---

## 정리

### DB 설계 요약

| 테이블 | 용도 | 핵심 컬럼 |
|--------|------|----------|
| users | 계정 관리 | user_id, user_type, status |
| patients | 환자 정보 | age, care_level, medical_condition |
| patient_personality | 환자 성향 | empathy, patience, activity, independence |
| caregivers | 간병인 정보 | experience_years, certifications, area_of_service |
| caregiver_personality | 간병인 성향 | empathy, patience, activity, independence |
| matching_results | 매칭 결과 | total_score, grade, status |
| matching_history | 변경 이력 | action, old_status, new_status |
| matching_recommendations | 추천 로그 | score, rank, was_clicked |

### 다음 단계

1. ✅ 테이블 설계 (위 내용)
2. 🔄 FastAPI 백엔드 구현
3. 🔄 프론트엔드 통합
4. 🔄 성능 최적화 (인덱싱, 쿼리 최적화)
5. 🔄 테스트 및 배포
