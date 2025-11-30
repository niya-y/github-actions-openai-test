# 📋 BluedonuLab 간병인 매칭 시스템 - TASK LIST & 구현 계획

## 📌 프로젝트 구조 생성

### TASK 1: 디렉토리 구조 생성
```bash
match/
├── data/                    # 데이터 파일 저장소
│   ├── raw/                 # 원본 CSV 파일
│   └── processed/           # 전처리된 CSV 파일
├── models/                  # 핵심 모듈
│   ├── __init__.py
│   ├── data_loader.py       # 데이터 로딩 및 전처리
│   ├── personality_calculator.py  # 환자 성향 계산
│   ├── caregiver_analyzer.py     # 간병인 스타일 분석
│   └── matching_algorithm.py     # 성향 기반 매칭 알고리즘
├── database/                # DB 관련 모듈
│   ├── __init__.py
│   ├── schema.py            # SQLAlchemy ORM 모델
│   └── connection.py        # DB 연결 관리
├── services/                # 비즈니스 로직
│   ├── __init__.py
│   ├── personality_service.py   # 성향 관련 서비스
│   ├── matching_service.py      # 매칭 관련 서비스
│   └── report_service.py        # 리포트 생성 서비스
├── api/                     # API 엔드포인트
│   ├── __init__.py
│   ├── personality_routes.py
│   ├── matching_routes.py
│   └── report_routes.py
├── tests/                   # 테스트 코드
│   ├── __init__.py
│   ├── test_personality.py
│   ├── test_matching.py
│   └── test_services.py
├── config.py                # 설정 파일
├── main.py                  # 메인 실행 스크립트
├── requirements.txt         # 의존성
├── PRD.md                   # 제품 요구사항 (완료)
├── TASK.md                  # 이 파일
└── README.md                # 사용 설명서
```

---

## 🎯 PHASE 1: 기반 구축 (1주)

### TASK 2: 데이터셋 복사 및 준비
**담당**: Data Engineer
**기간**: 1일
**산출물**: `data/raw/*.csv`

```
[ ] 2.1 Residents.csv 복사
[ ] 2.2 staff.csv 복사
[ ] 2.3 medications.csv 복사
[ ] 2.4 healthcare_dataset.csv 복사 (선택)
[ ] 2.5 데이터 크기 및 품질 확인
```

**체크리스트**:
- Residents: 1,000행 확인
- Staff: 1,000행 확인
- Medications: 2,000행, 60개 결측치 확인

---

### TASK 3: 데이터 전처리 모듈 개발 (`data_loader.py`)
**담당**: Data Engineer
**기간**: 2일
**산출물**: `models/data_loader.py`, `data/processed/*.csv`

```python
# 주요 기능
class DataLoader:
    def load_residents(path: str) -> pd.DataFrame
    def load_staff(path: str) -> pd.DataFrame
    def load_medications(path: str) -> pd.DataFrame

class DataPreprocessor:
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame
    def normalize_numeric_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame
    def categorize_data(df: pd.DataFrame) -> pd.DataFrame
    def validate_data_quality(df: pd.DataFrame) -> dict
```

**구현 세부사항**:
- ✅ **결측치 처리**: Medications.Dosage의 NaN → 약물별 중앙값으로 충전
- ✅ **타입 변환**: Date 컬럼 → datetime 객체
- ✅ **이상치 탐지**: 범위 벗어난 데이터 제거
- ✅ **정규화**: 0~100 범위로 스케일 조정
- ✅ **카테고리화**: 성별, Job Title → 카테고리 변환

**체크리스트**:
```
[ ] 3.1 load_residents() 구현 및 테스트
[ ] 3.2 load_staff() 구현 및 테스트
[ ] 3.3 load_medications() 구현 및 테스트
[ ] 3.4 handle_missing_values() 구현
[ ] 3.5 normalize_numeric_columns() 구현
[ ] 3.6 categorize_data() 구현
[ ] 3.7 validate_data_quality() 구현
[ ] 3.8 전처리된 CSV 생성 및 검증
```

---

### TASK 4: 데이터베이스 스키마 설계 (`schema.py`)
**담당**: Backend Engineer
**기간**: 1.5일
**산출물**: `database/schema.py`

```python
# SQLAlchemy ORM 모델
class Resident(Base):
    __tablename__ = 'residents'
    resident_id = Column(Integer, primary_key=True)
    name = Column(String)
    care_level = Column(Enum(CareLevelEnum))
    # ...

class Staff(Base):
    __tablename__ = 'staff'
    staff_id = Column(Integer, primary_key=True)
    name = Column(String)
    job_title = Column(Enum(JobTitleEnum))
    # ...

class PatientPersonality(Base):
    __tablename__ = 'patient_personality'
    patient_id = Column(Integer, primary_key=True)
    empathy = Column(Float)  # 0-100
    activity = Column(Float)
    patience = Column(Float)
    independence = Column(Float)
    personality_type = Column(String)
    # ...

class CaregiverStyle(Base):
    __tablename__ = 'caregiver_style'
    caregiver_id = Column(Integer, primary_key=True)
    empathy = Column(Float)
    activity_support = Column(Float)
    patience = Column(Float)
    independence_support = Column(Float)
    # ...

class PersonalityBasedMatching(Base):
    __tablename__ = 'personality_based_matching'
    matching_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient_personality.patient_id'))
    caregiver_id = Column(Integer, ForeignKey('caregiver_style.caregiver_id'))
    matching_score = Column(Float)  # 0-100
    grade = Column(String)  # A+, A, B+, B, C
    status = Column(Enum(MatchingStatusEnum))
    created_at = Column(DateTime)
    # ...
```

**체크리스트**:
```
[ ] 4.1 Resident ORM 모델 정의
[ ] 4.2 Staff ORM 모델 정의
[ ] 4.3 Medication ORM 모델 정의
[ ] 4.4 PatientPersonality ORM 모델 정의
[ ] 4.5 CaregiverStyle ORM 모델 정의
[ ] 4.6 PersonalityBasedMatching ORM 모델 정의
[ ] 4.7 MatchingHistory ORM 모델 정의
[ ] 4.8 DailyReport ORM 모델 정의
[ ] 4.9 인덱스 설정 (patient_id, caregiver_id, matching_score)
[ ] 4.10 DB 초기화 스크립트 작성
```

---

### TASK 5: DB 연결 관리 모듈 (`connection.py`)
**담당**: Backend Engineer
**기간**: 1일
**산출물**: `database/connection.py`

```python
class DatabaseConnection:
    def __init__(database_url: str)
    def create_session() -> Session
    def initialize_db()
    def close()

# SQLite 사용 (개발용)
# SQLAlchemy의 create_engine 활용
```

**체크리스트**:
```
[ ] 5.1 SQLite 설정 (match/data/carehome.db)
[ ] 5.2 SQLAlchemy 엔진 생성
[ ] 5.3 세션 팩토리 구성
[ ] 5.4 테이블 자동 생성
[ ] 5.5 DB 연결 테스트
```

---

## 🎯 PHASE 2: 핵심 알고리즘 (2주)

### TASK 6: 성향 점수 계산 모듈 (`personality_calculator.py`)
**담당**: ML Engineer / Data Scientist
**기간**: 3일
**산출물**: `models/personality_calculator.py`, `PatientPersonality` 테이블

```python
class PersonalityCalculator:
    def calculate_patient_personality(test_answers: list[int]) -> dict
    def classify_personality_type(scores: dict) -> str
    def generate_personality_description(personality_type: str) -> str

    # 질문별 점수 매핑
    def map_test_answers_to_scores(answers: list) -> dict
```

**성향 계산 알고리즘**:

```
12개 질문 입력
    ↓
각 질문의 선택지에 따라 4개 축에 점수 부여
    ↓
각 축별 점수 합계 → 0~100으로 정규화
    ↓
4개 점수 조합 → 성향 타입 분류
    ↓
AI 기반 설명 생성
```

**테스트 질문 샘플**:
1. 반복된 질문에 대한 대응 → **인내심(Patience)** 축
2. 자립도 → **독립성(Independence)** 축
3. 감정적 유대감 중요도 → **공감도(Empathy)** 축
4. 활동 수준 → **활동성(Activity)** 축

**체크리스트**:
```
[ ] 6.1 12개 테스트 질문 정의
[ ] 6.2 각 선택지의 점수 매핑 테이블 생성
[ ] 6.3 calculate_patient_personality() 구현
[ ] 6.4 성향 타입 분류 로직 구현
    [ ] 6.4.1 공감 중심형 (Empathy > 70 AND Patience > 70)
    [ ] 6.4.2 활동 중심형 (Activity > 70)
    [ ] 6.4.3 자립형 (Independence > 70)
    [ ] 6.4.4 전담형 (Dependency > 70)
[ ] 6.5 AI 기반 설명 생성 함수 구현 (template 기반)
[ ] 6.6 샘플 입력으로 테스트 및 검증
[ ] 6.7 점수 정규화 검증 (0~100 범위)
[ ] 6.8 PatientPersonality 테이블 생성 (1,000명)
```

---

### TASK 7: 간병인 스타일 분석 모듈 (`caregiver_analyzer.py`)
**담당**: ML Engineer / Data Scientist
**기간**: 3일
**산출물**: `models/caregiver_analyzer.py`, `CaregiverStyle` 테이블

```python
class CaregiverAnalyzer:
    def analyze_caregiver_style(staff_id: int, staff_data: dict) -> dict
    def assign_style_scores(job_title: str, experience_years: int) -> dict
    def classify_caregiver_type(scores: dict) -> str

# Job Title별 기본 스코어 테이블
JOB_TITLE_SCORES = {
    'Nurse': {'empathy': 80, 'patience': 85, 'activity_support': 70, 'independence_support': 75},
    'Caregiver': {'empathy': 75, 'patience': 80, 'activity_support': 65, 'independence_support': 70},
    'Therapist': {'empathy': 85, 'patience': 75, 'activity_support': 85, 'independence_support': 80},
    'Doctor': {'empathy': 70, 'patience': 70, 'activity_support': 60, 'independence_support': 85},
    'Administrator': {'empathy': 60, 'patience': 65, 'activity_support': 50, 'independence_support': 70}
}

# 경험도별 보정 계수
def apply_experience_multiplier(base_score: float, experience_years: int) -> float
```

**간병인 스타일 매핑**:
- **Nurse**: 높은 의료 전문성, 인내심, 공감
- **Caregiver**: 균형 잡힌 돌봄 능력
- **Therapist**: 감정 지원 + 활동성 강조
- **Doctor**: 전문성 높음, 감정 지원 낮음
- **Administrator**: 체계적 관리, 감정 지원 낮음

**체크리스트**:
```
[ ] 7.1 Job Title별 기본 스코어 테이블 생성
[ ] 7.2 경험도 계산 (고용일 → 년수 변환)
[ ] 7.3 assign_style_scores() 구현
[ ] 7.4 경험도 보정 로직 구현
[ ] 7.5 간병인 타입 분류 로직 구현
[ ] 7.6 CaregiverStyle 테이블 생성 (1,000명)
[ ] 7.7 샘플로 검증 (Nurse vs Caregiver 비교)
```

---

### TASK 8: 성향 기반 매칭 알고리즘 (`matching_algorithm.py`)
**담당**: ML Engineer
**기간**: 3일
**산출물**: `models/matching_algorithm.py`, `PersonalityBasedMatching` 테이블

```python
class MatchingAlgorithm:
    def calculate_matching_score(patient_id: int, caregiver_id: int) -> dict
    def get_matching_grade(score: float) -> str
    def recommend_caregivers(patient_id: int, top_n: int = 5) -> list[dict]
    def generate_matching_reason(patient_id: int, caregiver_id: int, score: float) -> str

# 매칭도 계산 로직
def calculate_matching_score(patient_personality: dict, caregiver_style: dict) -> float:
    # 1단계: 의료 필요도 적합성
    care_compatibility = calculate_care_level_match(patient_care_level, caregiver_job_title)

    # 2단계: 성향 일치도
    empathy_match = similarity_score(patient_empathy, caregiver_empathy)
    activity_match = similarity_score(patient_activity, caregiver_activity_support)
    patience_match = similarity_score(patient_patience, caregiver_patience)
    independence_match = similarity_score(patient_independence, caregiver_independence_support)

    personality_compatibility = (empathy_match + activity_match + patience_match + independence_match) / 4

    # 최종 점수
    final_score = (care_compatibility * 0.4) + (personality_compatibility * 0.6)
    return final_score

# 등급 판정 기준
def get_matching_grade(score: float) -> str:
    if score >= 90: return "A+"
    elif score >= 85: return "A"
    elif score >= 75: return "B+"
    elif score >= 65: return "B"
    else: return "C"
```

**체크리스트**:
```
[ ] 8.1 Care Level 매칭 로직 구현
    [ ] 8.1.1 High → Nurse, Caregiver (우선순위)
    [ ] 8.1.2 Moderate → Caregiver, Therapist
    [ ] 8.1.3 Low → Caregiver, Therapist, Administrator
[ ] 8.2 성향 유사도 계산 함수 구현 (Euclidean Distance)
[ ] 8.3 calculate_matching_score() 구현 (0.4 + 0.6 가중치)
[ ] 8.4 get_matching_grade() 구현 (A+~C 등급)
[ ] 8.5 recommend_caregivers() 구현 (Top-N 추천)
[ ] 8.6 generate_matching_reason() 구현 (AI 설명 생성)
[ ] 8.7 PersonalityBasedMatching 테이블 생성 (100명 샘플)
[ ] 8.8 평균 매칭도 검증 (목표: 75 이상)
```

**매칭 등급 기준**:
```
A+: 95~100  → 최고의 매칭
A:  85~94   → 매우 좋은 매칭
B+: 75~84   → 좋은 매칭 (권장)
B:  65~74   → 보통 매칭
C:  <65     → 낮은 매칭 (비권장)
```

---

## 🎯 PHASE 3: 서비스 개발 (2주)

### TASK 9: 성향 비즈니스 로직 (`personality_service.py`)
**담당**: Backend Engineer
**기간**: 2일
**산출물**: `services/personality_service.py`

```python
class PersonalityService:
    def save_personality_test(patient_id: int, test_answers: list[int]) -> PatientPersonality
    def get_patient_personality(patient_id: int) -> PatientPersonality
    def update_personality(patient_id: int, test_answers: list[int]) -> PatientPersonality
    def list_all_personalities() -> list[PatientPersonality]
    def get_personality_stats() -> dict
```

**체크리스트**:
```
[ ] 9.1 save_personality_test() 구현
[ ] 9.2 get_patient_personality() 구현
[ ] 9.3 update_personality() 구현 (月1회 재평가)
[ ] 9.4 list_all_personalities() 구현
[ ] 9.5 get_personality_stats() 구현 (평균, 분포 등)
[ ] 9.6 트랜잭션 관리
[ ] 9.7 에러 처리 (404, 400 등)
```

---

### TASK 10: 매칭 비즈니스 로직 (`matching_service.py`)
**담당**: Backend Engineer
**기간**: 2일
**산출물**: `services/matching_service.py`

```python
class MatchingService:
    def create_matching(patient_id: int, caregiver_id: int) -> PersonalityBasedMatching
    def recommend_caregivers(patient_id: int, limit: int = 5) -> list[PersonalityBasedMatching]
    def get_matching_history(patient_id: int) -> list[MatchingHistory]
    def cancel_matching(matching_id: int) -> bool
    def evaluate_matching_performance(start_date: date, end_date: date) -> dict
```

**체크리스트**:
```
[ ] 10.1 create_matching() 구현
[ ] 10.2 recommend_caregivers() 구현 (Top-5)
[ ] 10.3 get_matching_history() 구현
[ ] 10.4 cancel_matching() 구현 (상태 변경)
[ ] 10.5 evaluate_matching_performance() 구현
[ ] 10.6 매칭 유효성 검증 (중복 방지)
[ ] 10.7 상태 관리 (Active, Cancelled, Completed)
```

---

### TASK 11: 리포트 생성 로직 (`report_service.py`)
**담당**: Backend Engineer
**기간**: 1.5일
**산출물**: `services/report_service.py`

```python
class ReportService:
    def generate_daily_report(matching_id: int, date: date) -> DailyReport
    def generate_weekly_report(patient_id: int, week_date: date) -> dict
    def generate_monthly_performance_report(start_date: date, end_date: date) -> dict
    def export_report_to_pdf(report_id: int) -> bytes
```

**리포트 템플릿**:
- **일일 리포트**: 성향에 맞춘 케어 활동 요약
- **주간 리포트**: 만족도, 이슈 분석
- **월간 리포트**: 성과 지표, 개선사항

**체크리스트**:
```
[ ] 11.1 generate_daily_report() 구현
[ ] 11.2 성향 기반 리포트 템플릿 작성
[ ] 11.3 generate_weekly_report() 구현
[ ] 11.4 generate_monthly_performance_report() 구현
[ ] 11.5 PDF 내보내기 기능 (선택)
```

---

### TASK 12: API 엔드포인트 개발
**담당**: Backend Engineer
**기간**: 2.5일
**산출물**: `api/*.py`

#### 12.1 성향 API (`personality_routes.py`)
```python
@app.post("/api/personality/test")
def save_personality_test(patient_id: int, test_answers: list)

@app.get("/api/personality/{patient_id}")
def get_patient_personality(patient_id: int)

@app.get("/api/personality/stats")
def get_personality_stats()
```

#### 12.2 매칭 API (`matching_routes.py`)
```python
@app.get("/api/matching/recommend/{patient_id}")
def get_recommended_caregivers(patient_id: int, limit: int = 5)

@app.post("/api/matching/create")
def create_matching(patient_id: int, caregiver_id: int)

@app.get("/api/matching/history/{patient_id}")
def get_matching_history(patient_id: int)

@app.get("/api/matching/performance")
def get_matching_performance(start_date: date, end_date: date)
```

#### 12.3 리포트 API (`report_routes.py`)
```python
@app.get("/api/report/daily/{matching_id}")
def get_daily_report(matching_id: int, date: date)

@app.get("/api/report/weekly/{patient_id}")
def get_weekly_report(patient_id: int, week_date: date)

@app.get("/api/report/monthly")
def get_monthly_performance_report(start_date: date, end_date: date)
```

**체크리스트**:
```
[ ] 12.1 FastAPI 프로젝트 설정
[ ] 12.2 personality_routes 구현
[ ] 12.3 matching_routes 구현
[ ] 12.4 report_routes 구현
[ ] 12.5 요청/응답 Pydantic 모델 정의
[ ] 12.6 에러 처리 및 로깅
[ ] 12.7 CORS 설정 (프론트엔드 연동)
```

---

## 🎯 PHASE 4: 테스트 & 통합 (1주)

### TASK 13: 단위 테스트 작성
**담당**: QA Engineer
**기간**: 2일
**산출물**: `tests/test_*.py`

```python
# tests/test_personality.py
def test_calculate_patient_personality()
def test_classify_personality_type()
def test_personality_score_normalization()

# tests/test_matching.py
def test_calculate_matching_score()
def test_get_matching_grade()
def test_recommend_caregivers()

# tests/test_services.py
def test_save_personality_test()
def test_create_matching()
def test_generate_daily_report()
```

**테스트 체크리스트**:
```
[ ] 13.1 test_personality.py 작성 (최소 10개 케이스)
[ ] 13.2 test_matching.py 작성 (최소 10개 케이스)
[ ] 13.3 test_services.py 작성 (최소 8개 케이스)
[ ] 13.4 통합 테스트 작성
[ ] 13.5 커버리지 80% 이상 검증
[ ] 13.6 CI/CD 파이프라인 설정
```

---

### TASK 14: 통합 테스트 및 성과 검증
**담당**: QA Engineer / Project Manager
**기간**: 2일
**산출물**: `test_results.md`

```
[ ] 14.1 End-to-End 테스트 (성향 입력 → 매칭 추천)
[ ] 14.2 1,000명 데이터 대량 처리 테스트
[ ] 14.3 성능 테스트 (응답시간 < 1초)
[ ] 14.4 데이터 품질 검증 (결측치 < 2%)
[ ] 14.5 평균 매칭도 검증 (목표: 75 이상)
[ ] 14.6 성능 벤치마크 리포트 작성
```

---

### TASK 15: 문서화 및 배포
**담당**: Technical Writer / DevOps
**기간**: 1.5일
**산출물**: `README.md`, `requirements.txt`

```
[ ] 15.1 README.md 작성
    [ ] 15.1.1 프로젝트 개요
    [ ] 15.1.2 설치 가이드
    [ ] 15.1.3 사용 예제
    [ ] 15.1.4 API 문서
    [ ] 15.1.5 트러블슈팅
[ ] 15.2 requirements.txt 생성
[ ] 15.3 Docker 설정 (선택)
[ ] 15.4 배포 가이드 작성
```

---

## 📊 일정 요약

```
Week 1 (PHASE 1): 기반 구축
├─ Task 2: 데이터 복사 (1일)
├─ Task 3: 데이터 전처리 (2일)
├─ Task 4: DB 스키마 (1.5일)
└─ Task 5: DB 연결 (1일)

Week 2-3 (PHASE 2): 핵심 알고리즘
├─ Task 6: 성향 계산 (3일)
├─ Task 7: 간병인 분석 (3일)
└─ Task 8: 매칭 알고리즘 (3일)

Week 4-5 (PHASE 3): 서비스 개발
├─ Task 9: 성향 서비스 (2일)
├─ Task 10: 매칭 서비스 (2일)
├─ Task 11: 리포트 서비스 (1.5일)
└─ Task 12: API 개발 (2.5일)

Week 6 (PHASE 4): 테스트 & 배포
├─ Task 13: 단위 테스트 (2일)
├─ Task 14: 통합 테스트 (2일)
└─ Task 15: 문서화 & 배포 (1.5일)
```

---

## ✅ 성공 기준

| 기준 | 목표 | 검증 방법 |
|------|------|---------|
| 데이터 품질 | 결측치 < 2% | validate_data_quality() |
| 성향 계산 | 정확도 > 95% | unit test (10 cases) |
| 매칭도 | 평균 > 75 | evaluate_matching_performance() |
| API 성능 | 응답시간 < 1초 | load test |
| 테스트 커버리지 | > 80% | coverage report |
| 문서 완성도 | 100% | README, API docs |

---

## 📝 주요 의존성

```
pandas==1.3.0
numpy==1.21.0
sqlalchemy==1.4.23
fastapi==0.68.0
uvicorn==0.15.0
pytest==6.2.4
python-dateutil==2.8.2
```

---

## 🔄 진행 상황 추적

| Task | Status | 담당자 | 완료일 | 비고 |
|------|--------|--------|--------|------|
| Task 2 | ⬜ | - | - | - |
| Task 3 | ⬜ | - | - | - |
| Task 4 | ⬜ | - | - | - |
| Task 5 | ⬜ | - | - | - |
| Task 6 | ⬜ | - | - | - |
| Task 7 | ⬜ | - | - | - |
| Task 8 | ⬜ | - | - | - |
| Task 9 | ⬜ | - | - | - |
| Task 10 | ⬜ | - | - | - |
| Task 11 | ⬜ | - | - | - |
| Task 12 | ⬜ | - | - | - |
| Task 13 | ⬜ | - | - | - |
| Task 14 | ⬜ | - | - | - |
| Task 15 | ⬜ | - | - | - |

---

## 🎯 PHASE 4: 서비스 개발 (2주)

### TASK 9: 성향 비즈니스 로직 (`services/personality_service.py`) ✅ **완료**
**담당**: Backend Engineer
**기간**: 2일
**산출물**: `services/personality_service.py` (370+ 줄)

```python
class PersonalityService:
    def save_personality_test(patient_id: int, test_answers: list[int]) -> PatientPersonality
    def get_patient_personality(patient_id: int) -> PatientPersonality
    def update_personality(patient_id: int, test_answers: list[int]) -> PatientPersonality
    def list_all_personalities() -> list[PatientPersonality]
    def get_personality_stats() -> dict
```

**체크리스트**:
```
[x] 9.1 save_personality_test() 구현 ✅
[x] 9.2 get_patient_personality() 구현 ✅
[x] 9.3 update_personality() 구현 (月1회 재평가) ✅
[x] 9.4 list_all_personalities() 구현 ✅
[x] 9.5 get_personality_stats() 구현 (평균, 분포 등) ✅
[x] 9.6 트랜잭션 관리 ✅
[x] 9.7 에러 처리 (404, 400 등) ✅
```

---

### TASK 10: 매칭 비즈니스 로직 (`services/matching_service.py`) ✅ **완료**
**담당**: Backend Engineer
**기간**: 2일
**산출물**: `services/matching_service.py` (450+ 줄)

```python
class MatchingService:
    def create_matching(patient_id: int, caregiver_id: int) -> PersonalityBasedMatching
    def recommend_caregivers(patient_id: int, limit: int = 5) -> list[PersonalityBasedMatching]
    def get_matching_history(patient_id: int) -> list[MatchingHistory]
    def cancel_matching(matching_id: int) -> bool
    def evaluate_matching_performance(start_date: date, end_date: date) -> dict
```

**체크리스트**:
```
[x] 10.1 create_matching() 구현 ✅
[x] 10.2 recommend_caregivers() 구현 (Top-5) ✅
[x] 10.3 get_matching_history() 구현 ✅
[x] 10.4 cancel_matching() 구현 (상태 변경) ✅
[x] 10.5 evaluate_matching_performance() 구현 ✅
[x] 10.6 매칭 유효성 검증 (중복 방지) ✅
[x] 10.7 상태 관리 (Active, Cancelled, Completed) ✅
```

---

### TASK 11: 리포트 생성 로직 (`services/report_service.py`) ✅ **완료**
**담당**: Backend Engineer
**기간**: 1.5일
**산출물**: `services/report_service.py` (380+ 줄)

```python
class ReportService:
    def generate_daily_report(matching_id: int, date: date) -> DailyReport
    def generate_weekly_report(patient_id: int, week_date: date) -> dict
    def generate_monthly_performance_report(start_date: date, end_date: date) -> dict
    def export_report_to_pdf(report_id: int) -> bytes
```

**체크리스트**:
```
[x] 11.1 generate_daily_report() 구현 ✅
[x] 11.2 성향 기반 리포트 템플릿 작성 ✅
[x] 11.3 generate_weekly_report() 구현 ✅
[x] 11.4 generate_monthly_performance_report() 구현 ✅
[ ] 11.5 PDF 내보내기 기능 (선택사항)
```

---

## 🎯 PHASE 5: API & 프론트엔드 통합 (2주)

### TASK 12: FastAPI 애플리케이션 개발 (`app.py`) ✅ **완료**
**담당**: Backend Engineer
**기간**: 3일
**산출물**: `app.py` (320줄), `api/` routes (3개 파일, 375줄)

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="BluedonuLab Caregiver Matching API",
    description="성향 기반 간병인 매칭 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트 (Google Stitch 생성 UI)
app.mount("/static", StaticFiles(directory="page_design"), name="static")
```

**API 엔드포인트**:

#### 12.1 성향 API (`api/personality_routes.py`)
```python
@app.post("/api/personality/test")
def save_personality_test(patient_id: int, test_answers: list)

@app.get("/api/personality/{patient_id}")
def get_patient_personality(patient_id: int)

@app.get("/api/personality/stats")
def get_personality_stats()
```

#### 12.2 매칭 API (`api/matching_routes.py`)
```python
@app.get("/api/matching/recommend/{patient_id}")
def get_recommended_caregivers(patient_id: int, limit: int = 5)

@app.post("/api/matching/create")
def create_matching(patient_id: int, caregiver_id: int)

@app.get("/api/matching/history/{patient_id}")
def get_matching_history(patient_id: int)

@app.get("/api/matching/performance")
def get_matching_performance(start_date: date, end_date: date)
```

#### 12.3 리포트 API (`api/report_routes.py`)
```python
@app.get("/api/report/daily/{matching_id}")
def get_daily_report(matching_id: int, date: date)

@app.get("/api/report/weekly/{patient_id}")
def get_weekly_report(patient_id: int, week_date: date)

@app.get("/api/report/monthly")
def get_monthly_performance_report(start_date: date, end_date: date)
```

**체크리스트**:
```
[x] 12.1 FastAPI 프로젝트 설정 ✅
[x] 12.2 personality_routes 구현 ✅
[x] 12.3 matching_routes 구현 ✅
[x] 12.4 report_routes 구현 ✅
[x] 12.5 요청/응답 Pydantic 모델 정의 ✅
[x] 12.6 에러 처리 및 로깅 ✅
[x] 12.7 CORS 설정 (프론트엔드 연동) ✅
```

---

### TASK 13: 프론트엔드 통합 (`page_design/`) 📋 **대기중**
**담당**: Frontend Engineer
**기간**: 3일
**산출물**: 완전한 웹 애플리케이션

**Google Stitch로 생성된 페이지**:
```
page_design/
├── welcome_to_bluedonulab_onboarding/
│   ├── screen.png          # 설계 미리보기
│   └── code.html           # 생성된 HTML
├── personality_test_care_preferences/
├── personality_test_results/
├── caregiver_recommendation_list/
├── detailed_caregiver_profile/
└── patient_dashboard_active_matching/
```

**통합 작업**:
```
[ ] 13.1 HTML 페이지 분석 및 구조화
[ ] 13.2 API 연동 JavaScript 작성
[ ] 13.3 상태 관리 (localStorage 또는 Context API)
[ ] 13.4 폼 데이터 검증
[ ] 13.5 로딩 및 에러 상태 UI
[ ] 13.6 반응형 디자인 확인
[ ] 13.7 페이지 간 네비게이션 구현
[ ] 13.8 데이터 표시 및 업데이트
```

---

### TASK 14: React 컴포넌트 변환 (선택사항)
**담당**: Frontend Engineer
**기간**: 4일
**산출물**: `frontend/` React 애플리케이션

```
frontend/
├── src/
│   ├── components/
│   │   ├── Onboarding.jsx
│   │   ├── PersonalityTest.jsx
│   │   ├── PersonalityResults.jsx
│   │   ├── CaregiverList.jsx
│   │   ├── CaregiverProfile.jsx
│   │   └── PatientDashboard.jsx
│   ├── pages/
│   ├── services/
│   │   └── api.js           # API 호출 함수들
│   ├── hooks/
│   └── App.jsx
├── package.json
└── vite.config.js
```

**체크리스트**:
```
[ ] 14.1 React 프로젝트 초기화 (Vite)
[ ] 14.2 페이지별 컴포넌트 작성
[ ] 14.3 API 서비스 계층 구현
[ ] 14.4 상태 관리 (Zustand 또는 Redux)
[ ] 14.5 라우팅 설정 (React Router)
[ ] 14.6 폼 검증 (React Hook Form)
[ ] 14.7 UI 라이브러리 통합 (Tailwind CSS)
[ ] 14.8 테스트 작성 (Jest + React Testing Library)
```

---

## 🎯 PHASE 6: 테스트 & 배포 (1주)

### TASK 15: 단위 테스트 작성
**담당**: QA Engineer
**기간**: 2일
**산출물**: `tests/`

```python
# tests/test_personality.py
def test_calculate_patient_personality()
def test_classify_personality_type()
def test_personality_score_normalization()

# tests/test_matching.py
def test_calculate_matching_score()
def test_get_matching_grade()
def test_recommend_caregivers()

# tests/test_services.py
def test_save_personality_test()
def test_create_matching()
def test_generate_daily_report()
```

**체크리스트**:
```
[ ] 15.1 test_personality.py 작성 (최소 10개 케이스)
[ ] 15.2 test_matching.py 작성 (최소 10개 케이스)
[ ] 15.3 test_services.py 작성 (최소 8개 케이스)
[ ] 15.4 API 엔드포인트 테스트 (pytest-asyncio)
[ ] 15.5 통합 테스트 작성
[ ] 15.6 커버리지 80% 이상 검증
```

---

### TASK 16: 통합 테스트 및 성과 검증
**담당**: QA Engineer / Project Manager
**기간**: 2일
**산출물**: `test_results.md`

```
[ ] 16.1 End-to-End 테스트 (성향 입력 → 매칭 추천)
[ ] 16.2 1,000명 데이터 대량 처리 테스트
[ ] 16.3 성능 테스트 (응답시간 < 1초)
[ ] 16.4 데이터 품질 검증 (결측치 < 2%)
[ ] 16.5 평균 매칭도 검증 (목표: 75 이상)
[ ] 16.6 UI/UX 사용성 테스트
[ ] 16.7 성능 벤치마크 리포트 작성
```

---

### TASK 17: 문서화 및 배포
**담당**: Technical Writer / DevOps
**기간**: 2일
**산출물**: `README.md`, `DEPLOYMENT.md`, `requirements.txt`

```
[ ] 17.1 README.md 업데이트
    [ ] 17.1.1 프로젝트 개요
    [ ] 17.1.2 설치 가이드
    [ ] 17.1.3 사용 예제
    [ ] 17.1.4 API 문서
    [ ] 17.1.5 트러블슈팅
[ ] 17.2 DEPLOYMENT.md 작성
    [ ] 17.2.1 로컬 개발 환경 구성
    [ ] 17.2.2 Docker 설정
    [ ] 17.2.3 프로덕션 배포 가이드
    [ ] 17.2.4 환경 변수 설정
[ ] 17.3 requirements.txt 업데이트
[ ] 17.4 API 스웨거 문서 생성
```

---

## 📊 전체 일정 요약

```
Week 1 (PHASE 1): 기반 구축 ✅
├─ Task 2: 데이터 복사 (1일)
├─ Task 3: 데이터 전처리 (2일)
├─ Task 4: DB 스키마 (1.5일)
└─ Task 5: DB 연결 (1일)

Week 2-3 (PHASE 2): 핵심 알고리즘 ✅
├─ Task 6: 성향 계산 (3일)
├─ Task 7: 간병인 분석 (3일)
└─ Task 8: 매칭 알고리즘 (3일)

Week 4-5 (PHASE 3): 서비스 & API 개발 (🔄 진행중)
├─ Task 9: 성향 서비스 (2일)
├─ Task 10: 매칭 서비스 (2일)
├─ Task 11: 리포트 서비스 (1.5일)
└─ Task 12: FastAPI 개발 (3일)

Week 5-6 (PHASE 4): 프론트엔드 통합 (📋 대기중)
├─ Task 13: 프론트엔드 통합 (3일)
├─ Task 14: React 변환 (4일)

Week 7 (PHASE 5): 테스트 & 배포 (📋 대기중)
├─ Task 15: 단위 테스트 (2일)
├─ Task 16: 통합 테스트 (2일)
└─ Task 17: 문서화 & 배포 (2일)
```

---

## ✅ 성공 기준

| 기준 | 목표 | 검증 방법 |
|------|------|---------|
| 데이터 품질 | 결측치 < 2% | validate_data_quality() |
| 성향 계산 | 정확도 > 95% | unit test (10 cases) |
| 매칭도 | 평균 > 75 | evaluate_matching_performance() |
| API 성능 | 응답시간 < 1초 | load test |
| UI 반응성 | First Paint < 2초 | Lighthouse |
| 테스트 커버리지 | > 80% | coverage report |
| 문서 완성도 | 100% | README, API docs |

---

## 📝 주요 의존성

```
# Backend
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
python-dateutil>=2.8.2
pydantic>=2.0.0

# Frontend (선택사항)
react>=18.0.0
react-router-dom>=6.0.0
zustand>=4.0.0
axios>=1.0.0
tailwindcss>=3.0.0
```

---

## 🚀 시작하기

### 백엔드 실행
```bash
# 가상환경 활성화
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python main.py

# FastAPI 서버 실행
uvicorn app:app --reload

# API 문서 보기
# http://localhost:8000/docs
```

### 프론트엔드 실행 (React)
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build
```

---

## 🔄 진행 상황 추적

| Phase | Task | Status | 담당자 | 완료일 | 비고 |
|-------|------|--------|--------|--------|------|
| 1 | Task 2 | ✅ | - | 2024-11-11 | 데이터 복사 완료 |
| 1 | Task 3 | ✅ | - | 2024-11-11 | 전처리 완료 |
| 1 | Task 4 | ✅ | - | 2024-11-11 | 스키마 완료 |
| 1 | Task 5 | ✅ | - | 2024-11-11 | DB 연결 완료 |
| 2 | Task 6 | ✅ | - | 2024-11-11 | 성향 계산 완료 |
| 2 | Task 7 | ✅ | - | 2024-11-11 | 간병인 분석 완료 |
| 2 | Task 8 | ✅ | - | 2024-11-11 | 매칭 알고리즘 완료 |
| 4 | Task 9 | ✅ | - | 2024-11-12 | PersonalityService 완료 |
| 4 | Task 10 | ✅ | - | 2024-11-12 | MatchingService 완료 |
| 4 | Task 11 | ✅ | - | 2024-11-12 | ReportService 완료 |
| 5 | Task 12 | ✅ | - | 2024-11-12 | FastAPI 앱 완료 |
| 5 | Task 13 | ✅ | - | 2024-11-12 | 성향 라우터 완료 |
| 5 | Task 14 | ✅ | - | 2024-11-12 | 매칭 라우터 완료 |
| 5 | Task 15 | ✅ | - | 2024-11-12 | 리포트 라우터 완료 |
| 5 | Task 16 | ✅ | - | 2024-11-12 | API 통합 테스트 완료 (100% 통과) |
| 6 | Task 17 | 📋 | - | - | 프론트엔드 통합 (대기중) |
| 6 | Task 18 | 📋 | - | - | React 변환 (선택사항, 대기중) |
| 6 | Task 19 | 📋 | - | - | 테스트 & 배포 (대기중) |
