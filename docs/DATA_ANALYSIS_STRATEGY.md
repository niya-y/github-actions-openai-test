# 📊 BluedonuLab 프로젝트 - 데이터셋 분석 및 활용 전략

## 📋 목차
1. [프로젝트 비전 & UI 흐름](#프로젝트-비전--ui-흐름)
2. [현재 보유 데이터셋 개요](#현재-보유-데이터셋-개요)
3. [성향 테스트 시스템 설계](#성향-테스트-시스템-설계)
4. [간병인 매칭 시스템 활용 방안](#간병인-매칭-시스템-활용-방안)
5. [성향 기반 매칭 알고리즘](#성향-기반-매칭-알고리즘)
6. [데이터 통합 스키마](#데이터-통합-스키마)
7. [UI별 데이터 활용 전략](#ui별-데이터-활용-전략)
8. [즉시 구현 가능한 마일스톤](#즉시-구현-가능한-마일스톤)
9. [데이터 흐름 및 자동화](#데이터-흐름-및-자동화)
10. [기술 스택 및 구현 가이드](#기술-스택-및-구현-가이드)
11. [다음 단계](#다음-단계)

---

## 프로젝트 비전 & UI 흐름

### 🎯 BluedonuLab의 핵심 가치 제안


**"성향 기반 간병인 매칭으로 환자와 간병인의 신뢰 관계 구축"**

기존 간병 서비스는 의료 필요도(Care Level)만 고려했다면, BluedonuLab은:
- 환자의 **심리적 성향** (공감 요구, 독립성, 활동성 등) 파악
- 간병인의 **돌봄 스타일** 분석
- **성향 매칭도** 기반 최적 배정 → 높은 만족도 & 신뢰 구축

---

### 🎨 전체 UI 흐름 & 데이터 연계

```
┌─────────────────────────────────────────────────────────────┐
│  1️⃣ 온보딩 / 성향 테스트 화면                               │
│  └─ 환자의 케어 성향 빠르게 파악                            │
│     Data: 심리 성향 저장 → ProfileDB                       │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  2️⃣ 나의 성향 결과 화면                                     │
│  └─ 성향 요약 + 그래프 시각화                              │
│     Data: 성향 점수 계산 → AI 분석                        │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  3️⃣ 간병인 탐색 / 매칭 화면                                │
│  └─ 환자 성향과 맞는 간병인 추천 + 필터 검색              │
│     Data: 성향 매칭도 계산 → 상위 N명 추천                │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  4️⃣ 간병인 상세 프로필 화면                                │
│  └─ 신뢰감 강조 + AI 추천 이유 설명                       │
│     Data: 프로필 데이터 + 성향 일치율 + 이전 리뷰         │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  5️⃣ 일정 관리 / 리포트 확인 화면                            │
│  └─ 매칭 후 일정 관리 + 일일 리포트                        │
│     Data: 케어 기록 → 자동 리포트 생성                    │
└────────────────┬────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  6️⃣ 관리형 대시보드 (가족/운영자용)                         │
│  └─ 환자별 리포트 + 간병 품질 관리                         │
│     Data: 모든 매칭 & 케어 데이터 시각화                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 현재 보유 데이터셋 개요

### A. CAREHOME 데이터셋 (핵심 운영 데이터)

#### Residents.csv
- **규모**: 1,000명
- **주요 컬럼**:
  - `ResidentID` (PK): 주민 고유 ID
  - `Name`: 성명
  - `Date of Birth`: 생년월일 (1920~1960년)
  - `Gender`: 성별 (Male/Female/Other)
  - `Admission Date`: 입원 날짜 (2018~현재)
  - `Room Number`: 방 번호 (100~500)
  - `Care Level`: **케어 수준 (Low/Moderate/High)** ⭐
    - Low: 35% (기본 일상 지원)
    - Moderate: 40% (중간 수준 도움)
    - High: 25% (집중 케어 필요)

#### Staff.csv
- **규모**: 1,000명
- **주요 컬럼**:
  - `StaffID` (PK): 직원 고유 ID
  - `Name`: 성명
  - `Date of Birth`: 생년월일 (1950~1990년)
  - `Gender`: 성별
  - `Job Title`: **직급** ⭐
    - Nurse: 10% (간호사 - 고급 의료 케어)
    - Caregiver: 40% (간병인 - 기본 일상 지원)
    - Doctor: 15% (의사 - 의료 감독)
    - Therapist: 20% (치료사 - 재활 치료)
    - Administrator: 15% (관리자)
  - `Employment Date`: 고용 시작일 (2010~현재)

#### Medications.csv
- **규모**: 2,000개 약물 처방
- **주요 컬럼**:
  - `MedicationID` (PK): 약물 처방 ID
  - `Medication Name`: 약물명 (Metformin, Lisinopril, Atorvastatin, Amlodipine, Allopurinol)
  - `Dosage`: 용량 (500mg, 10mg, 20mg, 5mg, 100mg)
    - **⚠️ 결측치**: 60개 (3%) - 전처리 필요
  - `Prescription End Date`: 처방 종료 날짜
  - `ResidentID` (FK): 주민 참조 → Residents 테이블 링크

#### CareHomeDatabase.ipynb
- **용도**: 데이터 생성 로직 및 전처리 참고용
- **포함 내용**:
  - 난수 데이터 생성 함수
  - Pandas DataFrame 생성 및 조작
  - CSV 저장 로직

---

### B. Healthcare Dataset (공개 데이터)

- **규모**: 50,000+ 행
- **주요 컬럼**:
  - `Age`: 나이
  - `Gender`: 성별
  - `Blood Type`: 혈액형
  - `Medical Condition`: **의료 상태** ⭐
    - Cancer (암)
    - Diabetes (당뇨)
    - Obesity (비만)
    - Asthma (천식)
    - Arthritis (관절염)
    - Hypertension (고혈압)
  - `Date of Admission`: 입원 날짜
  - `Doctor`: 담당 의사
  - `Hospital`: 병원명
  - `Insurance Provider`: 보험사
  - `Billing Amount`: 청구액
  - `Room Number`: 방 번호
  - `Admission Type`: 입원 유형 (Urgent/Emergency/Elective)
  - `Discharge Date`: 퇴원 날짜
  - `Medication`: 약물
  - `Test Results`: 검사 결과 (Normal/Abnormal/Inconclusive)

**활용 가치**:
- 다양한 의료 상태별 환자 프로필 시뮬레이션
- 간병 난이도 매핑 (질병 종류별)
- 청구 및 보험 데이터로 프리미엄 간병비 책정

---

### C. Home Health Care - State by State Data (벤치마크 데이터)

- **규모**: 50개 미국 주(State) 데이터
- **주요 KPI 지표**:
  - `PatientStarRating`: 환자 만족도 (2.5~4.0점, 평균 3.2점) ⭐
  - `BeganPatientsCare`: 환자 케어 시작률 (평균 92.5%)
  - `TaughtAboutDrugs`: 약물 교육률 (평균 95.5%)
  - `RiskOfFalling`: 낙상 위험 관리 (평균 99.1%)
  - `Depression`: 우울증 모니터링 (평균 97.7%)
  - `FluShot`: 독감 예방접종률 (평균 70.5%)
  - `PneumoniaShot`: 폐렴 예방접종률 (평균 75.3%)
  - `FootCare`: 발 관리율 (평균 95.4%)
  - `Pain`: 통증 관리 (평균 98.8%)
  - `TreatedPain`: 통증 치료율 (평균 98.8%)
  - `HeartFailure`: 심부전 관리 (평균 97.9%)
  - `BedSores`: 욕창 관리 (평균 97.8%)
  - `PreventBedSores`: 욕창 예방 (평균 98.0%)
  - `BedSoresRisk`: 욕창 위험 관리 (평균 98.6%)
  - `Walking`: 보행 능력 (평균 66.9%) ⭐
  - `InOutBed`: 침대 출입 능력 (평균 62.7%)
  - `Bathing`: 목욕 지원 (평균 70.5%)
  - `MovingAround`: 이동 능력 (평균 70.0%)
  - `BreathingImproved`: 호흡 개선 (평균 71.1%)
  - `Wounds`: 상처 치료 (평균 89.8%)
  - `TakingDrugs`: 약물 복용 관리 (평균 57.0%)
  - `Hospital`: 입원 재발률 (평균 15.8%)
  - `ER`: ER 방문율 (평균 12.8%)

**활용 가치**:
- 지역별 케어 품질 벤치마크 설정
- 간병인 성과 평가 기준
- 의료 개입 필요 지역 파악 (ER 방문율 높은 곳)

---

## 성향 테스트 시스템 설계

### 📋 성향 테스트 구조

BluedonuLab의 핵심은 **환자의 성향**을 빠르게 파악하고 간병인 매칭에 반영하는 것입니다.

#### 1️⃣ 테스트 문항 설계 (12개 문항)

**성향 분류 (4가지 축)**

```
축 1: 감정 공감 (Empathy)
  - 질문: "간병인이 당신의 감정을 얼마나 이해해야 한다고 생각하나요?"
  - Low (자립형): "내가 스스로 해결하고 싶다"
  - High (공감형): "감정적인 지지가 정말 필요하다"

축 2: 활동성 (Activity)
  - 질문: "하루에 얼마나 활동적이고 싶으신가요?"
  - Low (휴식형): "최소한의 활동으로 충분"
  - High (활동형): "많은 활동과 자극 필요"

축 3: 차분함 / 인내 (Patience)
  - 질문: "반복되는 질문이나 요청을 할 때 간병인이 어떻게 하길 원하나요?"
  - Low (급한 성격): "빠르고 효율적으로"
  - High (차분함): "차분하고 몇 번이고 설명해주는 것"

축 4: 독립성 (Independence)
  - 질문: "도움을 받을 때 얼마나 자주 도움이 필요한가요?"
  - Low (의존형): "자주, 자세한 지원 필요"
  - High (독립형): "가능하면 스스로 하되, 필요할 때만")
```

#### 2️⃣ 테스트 문항 예시 (질문-답변 카드 형식)

**문항 1**: "환자가 반복해서 같은 질문을 할 때 당신은?"
- ☐ 차분히 다시 설명한다 (패티언스 +10)
- ☐ 짜증이 나지만 참는다 (패티언스 +5)
- ☐ 바로 대화를 돌린다 (패티언스 -10)

**문항 2**: "혼자 할 수 있는 것은 최대한 혼자 하고 싶다"
- ☐ 완전히 동의 (독립성 +10)
- ☐ 약간 동의 (독립성 +5)
- ☐ 동의하지 않음 (독립성 -10)

**문항 3**: "간병인과의 감정적인 유대감이 얼마나 중요한가요?"
- ☐ 매우 중요하다 (공감 +10)
- ☐ 어느 정도 중요하다 (공감 +5)
- ☐ 중요하지 않다 (공감 -10)

**문항 4**: "하루를 어떻게 보내고 싶으신가요?"
- ☐ 활동적이고 바쁘게 (활동성 +10)
- ☐ 적당히 활동 (활동성 +5)
- ☐ 조용히 쉬면서 (활동성 -10)

#### 3️⃣ 성향 점수 계산 로직

```python
def calculate_patient_profile(test_answers: list) -> dict:
    """
    12개 테스트 답변 → 4가지 성향 점수 계산

    Output:
    {
        'empathy': 75,          # 공감 요구도 (0~100)
        'activity': 55,         # 활동성 (0~100)
        'patience': 85,         # 간병인의 인내심 필요 (0~100)
        'independence': 60,     # 독립성 (0~100)
        'type': '공감형-인내심형',  # 주요 성향 분류
        'description': "당신은 감정적 지지가..."  # AI 생성 설명
    }
    """

    # 1. 각 축별 점수 계산
    empathy_score = calculate_axis_score(test_answers, axis='empathy')
    activity_score = calculate_axis_score(test_answers, axis='activity')
    patience_score = calculate_axis_score(test_answers, axis='patience')
    independence_score = calculate_axis_score(test_answers, axis='independence')

    # 2. 성향 분류
    personality_type = classify_patient_type(
        empathy_score, activity_score, patience_score, independence_score
    )

    # 3. AI 기반 설명 생성
    ai_description = generate_profile_description(personality_type)

    return {
        'empathy': empathy_score,
        'activity': activity_score,
        'patience': patience_score,
        'independence': independence_score,
        'type': personality_type,
        'description': ai_description
    }

# 예시 결과:
# {
#     'empathy': 80,
#     'activity': 40,
#     'patience': 90,
#     'independence': 35,
#     'type': '공감 중심형 + 차분함',
#     'description': "당신은 감정적 지지가 매우 중요하며,
#                     간병인의 인내심과 따뜻함을 원하는 공감 중심형입니다.
#                     천천히, 여러 번이라도 설명해주는 스타일의 간병인과 잘 맞을 것 같습니다."
# }
```

#### 4️⃣ 성향 분류 (4가지 타입)

```
┌─────────────────────────────────────────────────────────────┐
│                 성향 분류 매트릭스                             │
├─────────────────────────────────────────────────────────────┤
│                    │   독립성 높음   │   의존성 높음          │
├────────────────────┼─────────────────┼─────────────────────┤
│ 공감 요구 높음      │  자립 + 공감형  │  의존 + 공감형      │
│ (Empathy High)     │ → "든든함 원함"  │ → "따뜻함 원함"     │
├────────────────────┼─────────────────┼─────────────────────┤
│ 공감 요구 낮음      │  자립 + 효율형  │  의존 + 효율형      │
│ (Empathy Low)      │ → "프로답음"    │ → "체계적 관리"     │
└─────────────────────────────────────────────────────────────┘

타입 1: 공감 중심형 (Empathy-Driven)
  └─ 특징: 감정적 유대감 중요, 인내심 필요
  └─ 권장 간병인: Caregiver with high empathy, Therapist
  └─ 리포트 스타일: "오늘도 미소가 많았습니다 😊"

타입 2: 활동 중심형 (Activity-Driven)
  └─ 특징: 다양한 활동 & 자극 원함
  └─ 권장 간병인: Therapist, Active Caregiver
  └─ 리포트 스타일: "오늘 30분 산책했습니다!"

타입 3: 자립형 (Independence-Focused)
  └─ 특징: 혼자 할 수 있으면 스스로, 필요할 때만 도움
  └─ 권장 간병인: Professional Caregiver
  └─ 리포트 스타일: "필요한 도움만 제공했습니다"

타입 4: 전담형 (Care-Dependent)
  └─ 특징: 자주 도움 필요, 세심한 관리 필요
  └─ 권장 간병인: Nurse, Specialist Caregiver
  └─ 리포트 스타일: "매시간 상태 확인했습니다"
```

---

## 간병인 매칭 시스템 활용 방안

### 핵심 아이디어: 3계층 데이터 통합

```
┌─────────────────────────────────────────────────────────────┐
│                   CAREHOME (실제 운영)                        │
│  Residents (케어 수준) + Staff (직급/경험) + Medications   │
│                      ↓                                       │
│            기본 매칭 후보 풀 생성                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           Healthcare Dataset (시뮬레이션/확장)                │
│  다양한 의료 상태별 환자 프로필 → 간병 난이도 매핑           │
│            난이도 정밀화 및 확장성 확보                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│        Home Health Care Data (품질 벤치마크)                  │
│  지역별 성과 기준으로 간병인 평가 및 목표 설정               │
│              최종 매칭 점수 계산                             │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 활용 매핑

| 데이터셋 | CAREHOME | Healthcare | Home Health Care |
|---------|----------|-----------|-----------------|
| **환자 난이도 산정** | Care_Level | Medical_Condition | PatientStarRating, Risk_Factors |
| **간병인 역량 평가** | Job_Title, YearsExp | - | JobTitle_Quality_Benchmark |
| **매칭 점수 계산** | 기본 점수 | 난이도 보정 | 최종 가중치 적용 |
| **성과 평가** | 기록 추적 | 예상 난이도 | 실제 만족도 비교 |

---

## 성향 기반 매칭 알고리즘

### 🎯 알고리즘 개요: 2단계 매칭

```
Step 1: 의료 필요도 매칭 (Medical Necessity)
  ├─ 환자 Care Level + 질병 vs 간병인 직급/경험
  └─ 가중치: 40%

Step 2: 성향 호환도 매칭 (Personality Compatibility)
  ├─ 환자 성향 (Empathy, Activity, Patience, Independence)
  ├─ 간병인 돌봄 스타일 (측정 또는 프로필 기반)
  └─ 가중치: 60% ⭐ (BluedonuLab의 차별화 포인트)

결과: 최종 매칭 점수 = 의료필요도(40%) + 성향호환도(60%)
```

### Step 1: 환자 성향 점수 계산

```python
def calculate_patient_personality_score(patient_id: int) -> dict:
    """
    환자의 성향 테스트 결과 → 4개 축 점수 추출

    Output:
    {
        'patient_id': 101,
        'empathy': 80,          # 공감 요구도 (0~100)
        'activity': 40,         # 활동성
        'patience': 85,         # 간병인 인내심 필요도
        'independence': 35,     # 독립성
    }
    """
    patient_profile = db.query(PatientProfile).filter(PatientID=patient_id).first()
    return {
        'patient_id': patient_id,
        'empathy': patient_profile.empathy_score,
        'activity': patient_profile.activity_score,
        'patience': patient_profile.patience_required_score,
        'independence': patient_profile.independence_score,
    }
```

### Step 2: 간병인 돌봄 스타일 점수 계산

```python
def calculate_caregiver_style_score(caregiver_id: int) -> dict:
    """
    간병인의 과거 리뷰/평가 → 돌봄 스타일 점수 추출

    간병인의 돌봄 스타일은 다음 3가지 방식으로 측정:
    1️⃣ 이전 환자 리뷰 분석 (AI 감정 분석)
    2️⃣ 간병인 자기소개/프로필 텍스트 분석
    3️⃣ 실시간 케어 기록 분석

    Output:
    {
        'caregiver_id': 50,
        'empathy_score': 85,        # 감정 공감력
        'activity_score': 55,       # 활동성
        'patience_score': 90,       # 인내심
        'independence_support': 40, # 자립성 존중도
    }
    """

    # 방법 1: 이전 리뷰 분석
    reviews = db.query(Review).filter(CaregiverID=caregiver_id).all()
    empathy_from_reviews = analyze_review_sentiment(reviews, dimension='empathy')

    # 방법 2: 자기소개 텍스트 분석
    profile = db.query(CaregiverProfile).filter(CaregiverID=caregiver_id).first()
    empathy_from_bio = analyze_text_sentiment(profile.bio, dimension='empathy')

    # 방법 3: 케어 기록 분석 (예: 리포트에 감정 표현이 많은가?)
    care_records = db.query(CareLog).filter(CaregiverID=caregiver_id).all()
    empathy_from_logs = analyze_care_logs(care_records, dimension='empathy')

    # 가중 평균
    empathy_score = (
        empathy_from_reviews * 0.5 +
        empathy_from_bio * 0.3 +
        empathy_from_logs * 0.2
    )

    return {
        'caregiver_id': caregiver_id,
        'empathy_score': empathy_score,
        'activity_score': ...,
        'patience_score': ...,
        'independence_support': ...,
    }
```

### Step 3: 성향 호환도 점수 계산

```python
def calculate_personality_compatibility(
    patient_personality: dict,
    caregiver_style: dict
) -> float:
    """
    환자 성향과 간병인 스타일의 호환도 계산 (0~100)

    핵심: 각 축별 점수의 유사성을 코사인 유사도로 계산

    Output:
    {
        'compatibility_score': 87,  # 최종 호환도 (0~100)
        'details': {
            'empathy_match': 95,     # 공감 축 호환도
            'activity_match': 60,    # 활동 축 호환도
            'patience_match': 92,    # 인내심 축 호환도
            'independence_match': 85 # 독립성 축 호환도
        }
    }
    """

    # 1. 각 축별 호환도 계산 (유사도)
    empathy_match = 100 - abs(patient_personality['empathy'] - caregiver_style['empathy_score'])
    activity_match = 100 - abs(patient_personality['activity'] - caregiver_style['activity_score'])
    patience_match = 100 - abs(patient_personality['patience'] - caregiver_style['patience_score'])
    independence_match = 100 - abs(patient_personality['independence'] - caregiver_style['independence_support'])

    # 2. 가중 평균 (각 축이 동등하게 중요)
    personality_compatibility = (
        empathy_match * 0.25 +
        activity_match * 0.25 +
        patience_match * 0.25 +
        independence_match * 0.25
    )

    return {
        'compatibility_score': round(personality_compatibility, 1),
        'details': {
            'empathy_match': round(empathy_match, 1),
            'activity_match': round(activity_match, 1),
            'patience_match': round(patience_match, 1),
            'independence_match': round(independence_match, 1)
        }
    }

# 예시:
# 환자 성향: empathy=80, activity=40, patience=85, independence=35
# 간병인 스타일: empathy=85, activity=55, patience=90, independence=40
#
# empathy_match: 100 - |80-85| = 95
# activity_match: 100 - |40-55| = 85
# patience_match: 100 - |85-90| = 95
# independence_match: 100 - |35-40| = 95
#
# 최종: (95 + 85 + 95 + 95) / 4 = 92.5 ✨ 우수한 호환도!
```

### Step 4: 최종 매칭 점수 계산

```python
def calculate_final_matching_score(
    patient_id: int,
    caregiver_id: int,
    patient_difficulty: dict,  # 의료 필요도
    personality_compatibility: dict
) -> dict:
    """
    최종 매칭 점수: 의료필요도(40%) + 성향호환도(60%)

    Output:
    {
        'patient_id': 101,
        'caregiver_id': 50,
        'final_score': 82,
        'medical_fit': 76,          # 의료 필요도 적합성
        'personality_fit': 87,      # 성향 호환도
        'grade': '⭐⭐⭐⭐⭐',
        'recommendation': "당신과 성향이 87% 일치합니다 💫"
    }
    """

    # 1. 의료 필요도 적합성 (기존 알고리즘)
    medical_fit = calculate_medical_necessity_fit(patient_id, caregiver_id)
    # → 환자 Care Level + 질병 vs 간병인 직급/경험

    # 2. 성향 호환도 (성향 매칭)
    personality_fit = personality_compatibility['compatibility_score']

    # 3. 최종 점수 (BluedonuLab 차별화)
    final_score = (medical_fit * 0.40) + (personality_fit * 0.60)

    # 4. 등급 및 추천 이유 생성
    grade = get_matching_grade(final_score)
    recommendation = generate_matching_reason(
        patient_personality, caregiver_style, personality_fit
    )

    return {
        'patient_id': patient_id,
        'caregiver_id': caregiver_id,
        'final_score': round(final_score, 1),
        'medical_fit': round(medical_fit, 1),
        'personality_fit': round(personality_fit, 1),
        'grade': grade['stars'],
        'label': grade['label'],
        'recommendation': recommendation
    }

def generate_matching_reason(
    patient_personality: dict,
    caregiver_style: dict,
    compatibility_score: float
) -> str:
    """
    AI 기반 매칭 추천 이유 생성

    예시 생성 결과:
    "당신은 공감 중심형으로 감정적 지지가 중요한데,
    김OO 간병인은 공감 능력이 높아 잘 맞을 가능성이 높습니다.
    비슷한 성향의 환자들이 만족했던 매칭입니다. 💫"
    """

    patient_type = classify_patient_type(patient_personality)
    caregiver_strengths = identify_caregiver_strengths(caregiver_style)

    prompt = f"""
    환자 타입: {patient_type}
    간병인 강점: {caregiver_strengths}
    호환도: {compatibility_score}%

    위 정보를 바탕으로 따뜻하고 인간적인 추천 이유를
    한 문장(최대 2문장)으로 생성해줄래?
    """

    reason = azure_openai_call(prompt)
    return reason
```

---

## 데이터 통합 스키마

### 추가된 테이블 (성향 기반 매칭을 위해)

```sql
-- ===== 환자 성향 프로필 =====
CREATE TABLE PatientPersonality (
    PersonalityID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL UNIQUE,

    -- 4개 성향 축 점수 (0~100)
    EmpathyScore INT,           # 공감 요구도
    ActivityScore INT,          # 활동성
    PatienceRequiredScore INT,  # 간병인 인내심 필요
    IndependenceScore INT,      # 독립성

    -- 성향 분류
    PersonalityType VARCHAR(50),  # "공감형", "활동형", "자립형", "전담형"
    PersonalityDescription TEXT,  # AI 생성 설명

    -- 성향 테스트 메타
    TestCompletedAt TIMESTAMP,
    NextReviewDate DATE,          # 6개월마다 재테스트 권장

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

-- ===== 간병인 돌봄 스타일 =====
CREATE TABLE CaregiverStyle (
    StyleID INT PRIMARY KEY AUTO_INCREMENT,
    CaregiverID INT NOT NULL UNIQUE,

    -- 4개 스타일 축 점수 (0~100)
    EmpathyScore DECIMAL(5,2),      # 감정 공감력
    ActivityScore DECIMAL(5,2),     # 활동성
    PatienceScore DECIMAL(5,2),     # 인내심
    IndependenceSupportScore DECIMAL(5,2),  # 자립성 존중도

    -- 스타일 출처 (계산 방식)
    StyleSourceType VARCHAR(50),    # "review_based", "bio_based", "care_log_based", "hybrid"
    LastCalculatedAt TIMESTAMP,

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (CaregiverID) REFERENCES Caregivers(CaregiverID)
);

-- ===== 성향 기반 매칭 이력 =====
CREATE TABLE PersonalityBasedMatching (
    MatchingID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    CaregiverID INT NOT NULL,

    -- 점수 분석
    MedicalFitScore DECIMAL(5,2),      # 의료 필요도 적합성 (0~100)
    PersonalityFitScore DECIMAL(5,2),  # 성향 호환도 (0~100)
    FinalScore DECIMAL(5,2),            # 최종 점수 (0~100)

    -- 성향별 세부 호환도
    EmpathyCompatibility DECIMAL(5,2),
    ActivityCompatibility DECIMAL(5,2),
    PatienceCompatibility DECIMAL(5,2),
    IndependenceCompatibility DECIMAL(5,2),

    -- 매칭 상태
    MatchingDate DATE,
    StartDate DATE,
    EndDate DATE,
    Status VARCHAR(20),                 # "Proposed", "Active", "Completed", "Terminated"

    -- 매칭 결과 평가
    PatientSatisfaction INT,            # 1-5 scale
    CaregiverPerformanceRating INT,     # 1-5 scale
    PersonalityFitValidation INT,       # 예측한 호환도와 실제 호환도 검증

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (CaregiverID) REFERENCES Caregivers(CaregiverID)
);

-- ===== 성향 기반 매칭 추천 후보 =====
CREATE TABLE PersonalityBasedCandidates (
    CandidateID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    CaregiverID INT NOT NULL,

    Rank INT,                          # 1순위, 2순위, ...
    FinalScore DECIMAL(5,2),
    PersonalityFitScore DECIMAL(5,2),
    Status VARCHAR(20),                # "Recommended", "Clicked", "Applied", "Rejected", "Accepted"

    -- 추천 이유 (AI 생성)
    MatchingReasonAI TEXT,  # "당신과 성향이 87% 일치합니다..."

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (CaregiverID) REFERENCES Caregivers(CaregiverID)
);
```

---

## UI별 데이터 활용 전략

### 1️⃣ 온보딩 / 성향 테스트 UI

**화면 목적**: 환자가 자신의 성향을 빠르게 체크 → 프로필 DB에 반영

**데이터 흐름**:
```
사용자 입력 (12개 문항)
    ↓
점수 계산 (EmpathyScore, ActivityScore, PatientceScore, IndependenceScore)
    ↓
PatientPersonality 테이블 저장
    ↓
AI 성향 설명 생성 (Azure OpenAI)
    ↓
"당신은 공감 중심형 환자입니다 💬" 결과 화면 표시
```

**핵심 데이터**:
- `PatientPersonality.EmpathyScore`
- `PatientPersonality.ActivityScore`
- `PatientPersonality.PatienceRequiredScore`
- `PatientPersonality.IndependenceScore`
- `PatientPersonality.PersonalityDescription` (AI 생성)

**UI 구성 (권장)**: 파스텔 톤 (민트, 라이트 베이지) 버튼 문구는 인간적인 톤

---

### 2️⃣ 나의 성향 결과 화면

**화면 목적**: 성향 요약 + 저장

**데이터 흐름**:
```
PatientPersonality 테이블에서 읽음
    ↓
4개 축 점수 → 레이더 차트 시각화
    ↓
성향 타입 + AI 설명 표시
    ↓
[프로필에 저장] 버튼
```

**시각화 데이터**:
```javascript
// 레이더 차트 데이터
{
  labels: ['공감 요구', '활동성', '인내심 필요', '독립성'],
  datasets: [{
    label: '당신의 성향',
    data: [80, 40, 85, 35]  // PatientPersonality 점수
  }]
}
```

---

### 3️⃣ 간병인 탐색 / 매칭 화면

**화면 목적**: 환자 성향과 맞는 간병인 추천 + 필터 검색

**데이터 흐름**:
```
환자의 PatientPersonality 조회
    ↓
모든 활성 간병인의 CaregiverStyle 조회
    ↓
PersonalityBasedMatching 알고리즘 실행
    ↓
PersonalityBasedCandidates 저장 (상위 10~20명)
    ↓
간병인 리스트 UI에 표시
    ├─ 간병인 프로필 사진 / 이름
    ├─ 지역 / 직급 배지
    ├─ 성향 호환도 표시 ("당신과 87% 일치 💫")
    ├─ 별점 & 리뷰 수
    └─ [자세히 보기] 버튼
```

**필터링 로직**:
```python
def get_recommended_caregivers(
    patient_id: int,
    filters: dict = {}  # {"region": "Seoul", "job_title": "Caregiver"}
) -> list:
    """
    필터 조건을 만족하면서 PersonalityFitScore가 높은 간병인 반환
    """

    # 1. 기본 필터 (지역, 직급, 활성 상태)
    base_query = db.query(Caregivers).filter(
        Caregivers.Status == 'Active',
        Caregivers.Region == filters.get('region'),
        Caregivers.JobTitle == filters.get('job_title')
    )

    # 2. 성향 호환도 점수 계산
    candidates = []
    for caregiver in base_query:
        matching_score = calculate_final_matching_score(patient_id, caregiver.CaregiverID)
        candidates.append(matching_score)

    # 3. 점수 순으로 정렬
    candidates.sort(key=lambda x: x['final_score'], reverse=True)

    return candidates[:10]  # 상위 10명 반환
```

**핵심 데이터**:
- `PersonalityBasedCandidates`: 추천 순위, 점수
- `PersonalityBasedCandidates.MatchingReasonAI`: AI 생성 추천 문구

---

### 4️⃣ 간병인 상세 프로필 UI

**화면 목적**: 신뢰감 강조 + AI 추천 이유 설명

**데이터 흐름**:
```
간병인 ID 조회
    ↓
기본 정보 (Caregivers): 사진, 이름, 나이, 근무 지역
    ↓
자기소개 (CaregiverProfile): 자연어 텍스트
    ↓
돌봄 스타일 (CaregiverStyle): 공감력, 활동성, 인내심, 독립성 존중
    ↓
이전 리뷰 (Review): 리뷰 요약, 별점 통계
    ↓
경력 연표 (EmploymentDate 기반 시각화)
    ↓
[AI 추천 이유] 사이드바
    └─ "당신은 공감 중심형, 김OO 간병인은 공감력이 높아..."
        (PersonalityBasedCandidates.MatchingReasonAI 활용)
```

**시각화 예시**:
```
프로필 카드:
- 프로필 사진 (저장된 이미지)
- 이름, 나이, 근무 지역
- 직급 배지 (Caregiver / Nurse / Therapist)

돌봄 스타일 (CaregiverStyle 시각화):
┌────────────────────────────────┐
│  감정 공감  ████████░░ 85%     │
│  활동성     █████░░░░░ 55%     │
│  인내심     █████████░ 90%     │
│  독립 존중  ████░░░░░░ 40%     │
└────────────────────────────────┘

리뷰 요약:
- 평균 별점: 4.8/5.0 (52개 리뷰)
- 리뷰 하이라이트:
  ✓ "매우 따뜻하고 공감해주세요"
  ✓ "전문성이 있어서 안심됩니다"
  ✓ "항상 우리 할머니를 존중해줍니다"
```

---

### 5️⃣ 일정 관리 / 리포트 확인 UI

**화면 목적**: 매칭 후 일정 관리 + 일일 리포트

**데이터 흐름**:
```
활성 매칭 정보 (PersonalityBasedMatching) 조회
    ↓
캘린더에 일정 표시
    ├─ 간병인 이름
    ├─ 근무 시간대
    └─ 상태 (진행 중 / 완료)
    ↓
일정 클릭 시 리포트 팝업
    ├─ 환자 상태: 안정적 / 주의 필요 / 의료 개입 필요
    ├─ 활동량: 30% (목표 대비)
    ├─ 식사량: 보통
    ├─ 기분: 밝음 😊
    ├─ IoT 데이터 (체온, 심박수 등)
    └─ [가족에게 전송] 버튼
```

**AI 리포트 생성**:
```python
def generate_daily_report(matching_id: int) -> dict:
    """
    케어 기록 + IoT 데이터 → AI 기반 일일 리포트 생성

    Output:
    {
        'date': '2024-11-05',
        'summary': '오늘도 미소가 많았습니다 😊',  # AI 생성
        'health_status': 'Stable',
        'activity_level': 30,
        'meal_intake': 'Normal',
        'mood': 'Positive',
        'iot_data': {
            'body_temp': 36.5,
            'heart_rate': 72,
            'blood_pressure': '138/82'
        },
        'caregiver_notes': '반복된 질문도 차분히 설명해줬습니다',
        'suggestions': '계속 현재 케어 유지'
    }
    """

    matching = db.query(PersonalityBasedMatching).filter(MatchingID=matching_id).first()
    care_logs = db.query(CareLog).filter(
        MatchingID=matching_id,
        CareDate==today
    ).all()
    iot_data = db.query(IoTData).filter(
        PatientID=matching.PatientID,
        MeasurementTime>=today
    ).all()

    # AI 리포트 생성
    prompt = f"""
    간병인 성향: {matching.caregiver_style}
    환자 성향: {matching.patient_personality}
    오늘의 케어 기록: {care_logs}
    IoT 데이터: {iot_data}

    위 정보를 바탕으로 가족이 읽기 좋은 일일 리포트를 생성해줄래?
    형식: {{'summary': '한 문장 요약', 'details': '세부사항'}}
    """

    report = azure_openai_call(prompt)
    return report
```

---

### 6️⃣ 관리형 대시보드 (가족/운영자용)

**화면 목적**: 환자별 리포트 + 간병 품질 관리

**데이터 흐름**:
```
환자 목록 조회
    ↓
각 환자별 최근 매칭 정보
    ├─ 현재 간병인
    ├─ 성향 호환도
    └─ 매칭 만족도
    ↓
그래프 시각화
    ├─ 환자 컨디션 추이 (일주일)
    ├─ 감정 변화 (Mood tracking)
    ├─ 간병인 교체 이력
    └─ AI 분석 요약
    ↓
KPI 통계
    ├─ 평균 매칭 성공률
    ├─ 평균 성향 호환도
    ├─ 평균 만족도
    └─ 재계약 비율
```

**대시보드 쿼리 예시**:
```sql
-- 환자별 현재 매칭 정보
SELECT
    p.PatientID,
    p.Name,
    c.CaregiverID,
    c.Name AS CaregiverName,
    pbm.FinalScore,
    pbm.PersonalityFitScore,
    pbm.PatientSatisfaction,
    pbm.StartDate,
    pp.PersonalityType
FROM Patients p
LEFT JOIN PersonalityBasedMatching pbm
    ON p.PatientID = pbm.PatientID AND pbm.Status = 'Active'
LEFT JOIN Caregivers c ON pbm.CaregiverID = c.CaregiverID
LEFT JOIN PatientPersonality pp ON p.PatientID = pp.PatientID
ORDER BY pbm.FinalScore DESC;

-- 지난 7일간 환자 컨디션 추이
SELECT
    DATE(MeasurementTime) AS Date,
    PatientID,
    AVG(BodyTemperature) AS AvgTemp,
    AVG(HeartRate) AS AvgHeartRate,
    AVG(Mood) AS AvgMood  -- 1-5 scale
FROM IoTData
WHERE PatientID = ? AND MeasurementTime >= DATEADD(day, -7, GETDATE())
GROUP BY DATE(MeasurementTime), PatientID
ORDER BY Date;
```

---

## 매칭 알고리즘 상세 설계 (의료 필요도 기반)

### Step 1: 환자 프로필 → 간병 난이도 계산

```python
# 입력: CAREHOME + Healthcare 통합 데이터
환자_프로필 = {
    'ResidentID': 101,
    'Name': 'John Smith',
    'Age': 78,                           # Date of Birth에서 계산
    'Care_Level': 'High',                # CAREHOME.Care_Level
    'Medical_Condition': 'Diabetes',     # Healthcare에서 확장
    'Medications': [
        {'name': 'Metformin', 'dosage': '500mg'},
        {'name': 'Lisinopril', 'dosage': '10mg'}
    ],
    'Admission_Date': '2023-09-07',
}

# 처리: 간병 난이도 점수 계산 (0~100)
난이도_요소 = {
    'age_score': calculate_age_risk(78),           # 나이 위험도
    'care_level_score': {                           # 케어 수준
        'Low': 20,
        'Moderate': 50,
        'High': 80
    }[Care_Level],
    'medication_complexity': len(medications) * 10,  # 약물 복잡도
    'condition_severity': {                         # 질병 심각도
        'Diabetes': 60,
        'Cancer': 85,
        'Hypertension': 40,
        'Asthma': 30,
        'Arthritis': 35,
        'Obesity': 50
    }.get(Medical_Condition, 50),
}

# 출력: 최종 난이도 점수 (가중평균)
총_난이도 = (
    age_score * 0.25 +
    care_level_score * 0.35 +
    medication_complexity * 0.20 +
    condition_severity * 0.20
)
# 예시: 총_난이도 = 68/100 (중상 수준 난이도)
```

### Step 2: 간병인 프로필 → 역량 평가

```python
# 입력: CAREHOME Staff 데이터
간병인_프로필 = {
    'StaffID': 50,
    'Name': 'Jane Johnson',
    'Age': 45,
    'Job_Title': 'Caregiver',            # CAREHOME.Staff
    'Employment_Date': '2017-06-15',
    'Years_Experience': 2024 - 2017,     # 7년
}

# 처리: 역량 점수 계산 (0~100)
역량_요소 = {
    'experience_score': min(years_experience * 10, 80),  # 최대 80점
    'qualification_score': {                             # 직급별 점수
        'Nurse': 85,
        'Therapist': 75,
        'Caregiver': 65,
        'Doctor': 95,
        'Administrator': 60
    }[Job_Title],
    'quality_score': benchmark_quality_rating,           # Home Health Care 기준
}

# 출력: 최종 역량 점수 (가중평균)
총_역량 = (
    experience_score * 0.30 +
    qualification_score * 0.40 +
    quality_score * 0.30
)
# 예시: 총_역량 = 72/100 (중상 수준 역량)
```

### Step 3: 매칭 점수 계산

```python
# 입력: 환자 난이도 + 간병인 역량
매칭_요소 = {
    # 난이도 적합성: 환자 난이도 ≈ 간병인 역량이면 높은 점수
    '난이도_적합성': max(0, 100 - abs(총_난이도 - 총_역량)),

    # 전문성 일치도: 질병 특화 직급이면 가산점
    '전문성_일치': calculate_specialization_match(
        Medical_Condition,
        Job_Title
    ),
    # 예: Job_Title='Nurse' and Care_Level='High' → +20점
    # 예: Job_Title='Caregiver' and Care_Level in ['Low','Moderate'] → +15점

    # 경험도: 경험이 많을수록 높은 점수
    '경험_점수': years_experience,

    # 질적 성과: Home Health Care 벤치마크 기반
    '질적_성과': quality_rating * 20,  # 4.0 max → 80점
}

# 출력: 최종 매칭 점수 (가중합)
최종_매칭_점수 = (
    난이도_적합성 * 0.40 +        # 적합성: 40%
    전문성_일치 * 0.20 +          # 전문성: 20%
    (경험_점수 / 10) * 0.20 +     # 경험: 20%
    (질적_성과 / 4) * 0.20        # 품질: 20%
)

# 예시: 최종_매칭_점수 = 76/100 (우수한 매칭)
```

### 매칭 결과 인터프리테이션

| 점수 범위 | 등급 | 추천 | 설명 |
|----------|------|------|------|
| 85-100 | ⭐⭐⭐⭐⭐ | 최우선 추천 | 모든 면에서 최적 매칭 |
| 75-84 | ⭐⭐⭐⭐ | 강력 추천 | 좋은 매칭, 즉시 배정 가능 |
| 65-74 | ⭐⭐⭐ | 추천 | 무난한 매칭, 대기 가능 |
| 55-64 | ⭐⭐ | 약한 추천 | 다른 후보 먼저 검토 |
| <55 | ⭐ | 비추천 | 재배정 권장 |

---

## 데이터 통합 스키마

### 데이터베이스 설계 (ERD)

```sql
-- ===== CORE TABLES (CAREHOME 기본 데이터) =====

CREATE TABLE Patients (
    PatientID INT PRIMARY KEY,           -- Residents.ResidentID
    Name VARCHAR(100) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender VARCHAR(20),                  -- Male/Female/Other
    CareLevel VARCHAR(20) NOT NULL,      -- Low/Moderate/High
    AdmissionDate DATE NOT NULL,
    RoomNumber INT,
    CurrentStatus VARCHAR(20),           -- Active/Inactive/Discharged
    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP
);

CREATE TABLE Caregivers (
    CaregiverID INT PRIMARY KEY,         -- Staff.StaffID
    Name VARCHAR(100) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender VARCHAR(20),
    JobTitle VARCHAR(50) NOT NULL,       -- Nurse/Caregiver/Doctor/Therapist/Admin
    EmploymentDate DATE NOT NULL,
    YearsExperience INT GENERATED ALWAYS AS (YEAR(CURDATE()) - YEAR(EmploymentDate)),
    Status VARCHAR(20),                  -- Active/On_Leave/Resigned
    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP
);

CREATE TABLE Medications (
    MedicationID INT PRIMARY KEY,
    PatientID INT NOT NULL,
    MedicationName VARCHAR(100) NOT NULL,
    Dosage VARCHAR(50),
    PrescriptionStartDate DATE,
    PrescriptionEndDate DATE NOT NULL,
    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

-- ===== EXTENDED TABLES (Healthcare Dataset 통합) =====

CREATE TABLE PatientMedicalProfile (
    ProfileID INT PRIMARY KEY,
    PatientID INT NOT NULL UNIQUE,
    MedicalCondition VARCHAR(100),       -- Cancer/Diabetes/Obesity/Asthma/etc
    AdmissionType VARCHAR(50),           -- Urgent/Emergency/Elective
    BloodType VARCHAR(10),
    InsuranceProvider VARCHAR(100),
    BillingAmount DECIMAL(10, 2),
    TestResults VARCHAR(50),             -- Normal/Abnormal/Inconclusive
    Doctor VARCHAR(100),
    Hospital VARCHAR(100),
    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

-- ===== QUALITY METRICS TABLES (Home Health Care 벤치마크) =====

CREATE TABLE QualityMetrics (
    MetricID INT PRIMARY KEY AUTO_INCREMENT,
    CaregiverID INT NOT NULL,
    PatientID INT NOT NULL,
    Month INT,
    Year INT,
    State VARCHAR(2),                    -- US State code for benchmarking

    -- Patient Satisfaction & Care initiation
    PatientSatisfactionRating DECIMAL(2,1),  -- 2.5-4.0 scale (Home Health Care baseline)
    CareInitiationRate DECIMAL(5,2),         -- %

    -- Health Education
    MedicationEducationRate DECIMAL(5,2),    -- % taught about drugs

    -- Risk & Condition Management
    FallRiskManagementRate DECIMAL(5,2),     -- %
    DepressionMonitoringRate DECIMAL(5,2),   -- %

    -- Preventive Care
    FluShotRate DECIMAL(5,2),                -- %
    PneumoniaShotRate DECIMAL(5,2),          -- %
    FootCareRate DECIMAL(5,2),               -- %

    -- Pain & Symptom Management
    PainManagementRate DECIMAL(5,2),         -- %
    TreatedPainRate DECIMAL(5,2),            -- %

    -- Chronic Condition Management
    HeartFailureRate DECIMAL(5,2),           -- %

    -- Wound Care
    BedSoresRate DECIMAL(5,2),               -- %
    PreventBedSoresRate DECIMAL(5,2),        -- %
    BedSoresRiskRate DECIMAL(5,2),           -- %
    WoundTreatmentRate DECIMAL(5,2),         -- %

    -- Mobility & ADL (Activities of Daily Living)
    WalkingRate DECIMAL(5,2),                -- % improved
    InOutBedRate DECIMAL(5,2),               -- % capable
    BathingRate DECIMAL(5,2),                -- % capable
    MovingAroundRate DECIMAL(5,2),           -- % capable

    -- Health Outcomes
    BreathingImprovedRate DECIMAL(5,2),      -- %
    MedicationComplianceRate DECIMAL(5,2),   -- %

    -- Hospitalization Metrics
    HospitalizationReadmissionRate DECIMAL(5,2),  -- %
    ERVisitRate DECIMAL(5,2),                     -- %

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (CaregiverID) REFERENCES Caregivers(CaregiverID),
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

-- ===== MATCHING & TRACKING TABLES =====

CREATE TABLE MatchingHistory (
    MatchingID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    CaregiverID INT NOT NULL,
    MatchingDate DATE NOT NULL,

    -- Matching Scores
    DifficultyLevel INT,                 -- 0-100 (calculated from patient profile)
    CompetencyLevel INT,                 -- 0-100 (calculated from caregiver profile)
    MatchingScore INT,                   -- 0-100 (final matching score)

    -- Assignment Details
    StartDate DATE NOT NULL,
    EndDate DATE,
    Duration INT,                        -- days
    AssignmentStatus VARCHAR(50),        -- Active/Completed/Terminated

    -- Outcome
    PatientSatisfactionFeedback INT,     -- 1-5 scale
    CaregiverPerformanceRating INT,      -- 1-5 scale
    Notes TEXT,

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (CaregiverID) REFERENCES Caregivers(CaregiverID)
);

CREATE TABLE MatchingCandidates (
    CandidateID INT PRIMARY KEY AUTO_INCREMENT,
    MatchingID INT NOT NULL,
    CaregiverID INT NOT NULL,
    Rank INT,                            -- 1st choice, 2nd choice, etc
    CandidateScore INT,                  -- 0-100
    ScoreBreakdown JSON,                 -- {difficulty_fit: 40, specialization: 15, ...}
    Status VARCHAR(20),                  -- Proposed/Accepted/Rejected
    Notes TEXT,

    CreatedAt TIMESTAMP,
    UpdatedAt TIMESTAMP,
    FOREIGN KEY (MatchingID) REFERENCES MatchingHistory(MatchingID),
    FOREIGN KEY (CaregiverID) REFERENCES Caregivers(CaregiverID)
);

-- ===== INDEX 최적화 =====

CREATE INDEX idx_patients_care_level ON Patients(CareLevel);
CREATE INDEX idx_caregivers_job_title ON Caregivers(JobTitle);
CREATE INDEX idx_medications_patient_id ON Medications(PatientID);
CREATE INDEX idx_matching_patient_id ON MatchingHistory(PatientID);
CREATE INDEX idx_matching_caregiver_id ON MatchingHistory(CaregiverID);
CREATE INDEX idx_quality_metrics_state ON QualityMetrics(State);
```

### 데이터 흐름 다이어그램

```
┌──────────────────────────────────────────────────────────────┐
│                      데이터 수집 및 입력                       │
├──────────────────────────────────────────────────────────────┤
│ ├─ CAREHOME 데이터 (Residents, Staff, Medications)          │
│ ├─ Healthcare Dataset (의료 상태, 청구 정보)                │
│ └─ Home Health Care KPI (지역별 벤치마크)                   │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                      데이터 전처리 & 정규화                    │
├──────────────────────────────────────────────────────────────┤
│ ├─ 결측치 처리 (Medications.Dosage)                         │
│ ├─ 데이터 타입 변환                                          │
│ ├─ 이상치 탐지 (Z-score, IQR)                               │
│ └─ 정규화 (Min-Max, Standard Scaler)                        │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                   데이터 통합 & 프로필 생성                    │
├──────────────────────────────────────────────────────────────┤
│ ├─ PatientMedicalProfile 생성 (환자 의료 정보)              │
│ ├─ CaregiverQualityMetrics 계산 (간병인 성과)               │
│ └─ 환자 난이도 & 간병인 역량 점수 산정                       │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    매칭 알고리즘 실행                          │
├──────────────────────────────────────────────────────────────┤
│ ├─ Step 1: 환자 난이도 계산                                  │
│ ├─ Step 2: 간병인 역량 평가                                  │
│ ├─ Step 3: 매칭 점수 계산                                    │
│ └─ Step 4: 상위 N명 후보 추천                                │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    매칭 결과 저장 & 추적                       │
├──────────────────────────────────────────────────────────────┤
│ ├─ MatchingHistory 기록                                      │
│ ├─ MatchingCandidates 저장                                   │
│ └─ 추천 상태 추적 (Proposed/Accepted/Rejected)              │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    성과 평가 & 피드백                          │
├──────────────────────────────────────────────────────────────┤
│ ├─ QualityMetrics 업데이트 (월별)                           │
│ ├─ 만족도 조사 및 기록                                       │
│ ├─ Home Health Care 벤치마크와 비교                         │
│ └─ 알고리즘 개선 인사이트 도출                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 즉시 구현 가능한 마일스톤

### Phase 1: 데이터 통합 (1주)

#### Task 1.1: CAREHOME 데이터 정제

**Residents 데이터 분석**
```
케어 수준 분포:
- Low: 350명 (35%) → 간병인 1명/2주
- Moderate: 400명 (40%) → 간병인 1명/주
- High: 250명 (25%) → 간병인 1명/2일

나이 분포 (Date of Birth 기반):
- 60-70세: 30%
- 70-80세: 40%
- 80세+: 30%

성별 분포:
- Male: ~50%
- Female: ~35%
- Other: ~15%
```

**Staff 데이터 분석**
```
직급 분포:
- Nurse (간호사): 100명 (10%)
- Caregiver (간병인): 400명 (40%) ← 주요 매칭 대상
- Doctor (의사): 150명 (15%)
- Therapist (치료사): 200명 (20%)
- Administrator (관리자): 150명 (15%)

경력 분포 (Employment_Date 기반):
- 0-2년: 20%
- 2-5년: 30%
- 5-10년: 35%
- 10년+: 15%
```

**Medications 데이터 정제**
```
결측치 처리:
- Dosage 결측: 60개 (3%)
  → 각 약물별 중앙값으로 impute
  → Metformin: 500mg 또는 100mg (중앙값)
  → Lisinopril: 20mg (중앙값)
  → Atorvastatin: 20mg (중앙값)
  → Amlodipine: 10mg (중앙값)
  → Allopurinol: 100mg (중앙값)

약물별 ResidentID 매핑 검증:
- ResidentID 범위: 1~1000 ✓
- 중복 제거 및 유효성 확인
```

#### Task 1.2: Healthcare Dataset 매핑

```python
의료 상태별 간병 난이도 매핑:

'Cancer': {                          # 암
    'base_difficulty': 85,
    'care_level_adjustment': High → +10,
    'medication_complexity': +15,
    'required_specialization': ['Nurse', 'Doctor']
},

'Diabetes': {                        # 당뇨
    'base_difficulty': 60,
    'care_level_adjustment': Moderate → 0,
    'medication_complexity': +12,
    'required_specialization': ['Nurse', 'Caregiver']
},

'Obesity': {                         # 비만
    'base_difficulty': 50,
    'care_level_adjustment': Moderate → 0,
    'medication_complexity': +8,
    'required_specialization': ['Caregiver', 'Therapist']
},

'Asthma': {                          # 천식
    'base_difficulty': 35,
    'care_level_adjustment': Low → -5,
    'medication_complexity': +10,
    'required_specialization': ['Caregiver', 'Nurse']
},

'Arthritis': {                       # 관절염
    'base_difficulty': 40,
    'care_level_adjustment': Low → -5,
    'medication_complexity': +8,
    'required_specialization': ['Therapist', 'Caregiver']
},

'Hypertension': {                    # 고혈압
    'base_difficulty': 45,
    'care_level_adjustment': Moderate → 0,
    'medication_complexity': +10,
    'required_specialization': ['Nurse', 'Caregiver']
}
```

#### Task 1.3: Home Health Care 벤치마크 추출

```
지역별 KPI 통계:

📊 환자 만족도 (PatientStarRating):
- 최고: NJ (4.0/4.0)
- 평균: 3.2/4.0
- 최저: AK (2.5/4.0)

🎯 케어 품질 지표:
- 낙상 위험 관리: 99.1% (목표: >99%)
- 약물 교육: 95.5% (목표: >95%)
- 우울증 모니터링: 97.7% (목표: >97%)

🏃 운동 능력 (Walking):
- 최고: UT (71.1%)
- 평균: 66.9%
- 최저: TX (59.9%)

🏥 의료 개입:
- 평균 입원율: 15.8%
- 평균 ER 방문: 12.8%
- 목표: 입원율 <15%, ER <12%

🌍 지역별 성과 그룹 분류:
- A 그룹 (High: 만족도 3.5+): NJ, CT, FL, AL, AZ, CA, CO...
- B 그룹 (Medium: 3.0~3.5): ...
- C 그룹 (Low: <3.0): AK, OR, NM...
```

---

### Phase 2: 매칭 알고리즘 개발 (2주)

#### Task 2.1: 환자 난이도 엔진 구현

```python
def calculate_patient_difficulty(patient_id):
    """
    환자 프로필 기반 난이도 점수 계산

    출력: 0~100 점수
    """

    # 1. CAREHOME 데이터 조회
    patient = db.query(Patients).filter(PatientID=patient_id)
    medications = db.query(Medications).filter(PatientID=patient_id)

    # 2. Healthcare 프로필 조회
    medical_profile = db.query(PatientMedicalProfile).filter(PatientID=patient_id)

    # 3. 각 요소별 점수 계산
    care_level_score = {
        'Low': 20,
        'Moderate': 50,
        'High': 80
    }[patient.CareLevel]

    age = calculate_age(patient.DateOfBirth)
    age_score = min(age - 60, 40) if age > 60 else max(0, (age - 50) * 2)

    medication_count = len(medications)
    medication_score = min(medication_count * 8, 40)

    condition_severity = medical_condition_difficulty_map.get(
        medical_profile.MedicalCondition, 50
    )

    # 4. 가중 평균
    total_difficulty = (
        care_level_score * 0.40 +      # 케어 수준: 40%
        age_score * 0.20 +             # 나이: 20%
        medication_score * 0.20 +      # 약물 복잡도: 20%
        condition_severity * 0.20      # 질병 심각도: 20%
    )

    return {
        'patient_id': patient_id,
        'total_difficulty': round(total_difficulty, 1),
        'breakdown': {
            'care_level': care_level_score,
            'age': age_score,
            'medication': medication_score,
            'condition': condition_severity
        }
    }

# 테스트 예시:
# Input: PatientID = 101 (John Smith, Age 78, Care_Level=High, 2 medications, Diabetes)
# Output: {'total_difficulty': 68.2, 'breakdown': {...}}
```

#### Task 2.2: 간병인 역량 평가 엔진 구현

```python
def calculate_caregiver_competency(caregiver_id):
    """
    간병인 프로필 기반 역량 점수 계산

    출력: 0~100 점수
    """

    # 1. CAREHOME 데이터 조회
    caregiver = db.query(Caregivers).filter(CaregiverID=caregiver_id)

    # 2. Home Health Care 벤치마크 조회
    quality_metrics = db.query(QualityMetrics).filter(CaregiverID=caregiver_id)

    # 3. 각 요소별 점수 계산
    experience_years = caregiver.YearsExperience
    experience_score = min(experience_years * 10, 80)

    job_title_score = {
        'Nurse': 85,
        'Therapist': 75,
        'Caregiver': 65,
        'Doctor': 95,
        'Administrator': 60
    }[caregiver.JobTitle]

    # Home Health Care 벤치마크 기반 평가
    latest_metrics = quality_metrics.order_by(Month, Year).desc().first()
    quality_score = (
        (latest_metrics.PatientSatisfactionRating / 4.0) * 100 * 0.5 +
        (latest_metrics.WalkingRate / 100) * 100 * 0.3 +
        (latest_metrics.MedicationComplianceRate / 100) * 100 * 0.2
    ) if latest_metrics else 50

    # 4. 가중 평균
    total_competency = (
        experience_score * 0.30 +      # 경험: 30%
        job_title_score * 0.40 +       # 직급: 40%
        quality_score * 0.30           # 품질: 30%
    )

    return {
        'caregiver_id': caregiver_id,
        'total_competency': round(total_competency, 1),
        'breakdown': {
            'experience': experience_score,
            'job_title': job_title_score,
            'quality': quality_score
        }
    }

# 테스트 예시:
# Input: CaregiverID = 50 (Jane Johnson, Caregiver, 7 years experience, Rating 3.6/4.0)
# Output: {'total_competency': 72.4, 'breakdown': {...}}
```

#### Task 2.3: 매칭 점수 계산 엔진 구현

```python
def calculate_matching_score(patient_id, caregiver_id):
    """
    환자와 간병인 간 최종 매칭 점수 계산

    출력: 0~100 점수 + 상세 분석
    """

    # 1. 난이도 및 역량 조회
    patient_difficulty = calculate_patient_difficulty(patient_id)
    caregiver_competency = calculate_caregiver_competency(caregiver_id)

    # 2. 난이도 적합성
    difficulty_fit = max(0, 100 - abs(
        patient_difficulty['total_difficulty'] -
        caregiver_competency['total_competency']
    ))

    # 3. 전문성 일치도
    patient = db.query(Patients).filter(PatientID=patient_id)
    caregiver = db.query(Caregivers).filter(CaregiverID=caregiver_id)
    medical_profile = db.query(PatientMedicalProfile).filter(PatientID=patient_id)

    specialization_match = 0
    required_specializations = specialization_map.get(
        medical_profile.MedicalCondition,
        ['Caregiver']
    )

    if caregiver.JobTitle in required_specializations:
        specialization_match = 20
    elif caregiver.JobTitle == 'Nurse':  # 간호사는 대부분의 고난이도 케어에 적합
        if patient.CareLevel == 'High':
            specialization_match = 18
        else:
            specialization_match = 10
    else:
        specialization_match = 5

    # 4. 경험도
    experience_score = min(caregiver.YearsExperience / 10 * 20, 20)

    # 5. 질적 성과
    quality_metrics = db.query(QualityMetrics).filter(CaregiverID=caregiver_id)
    latest = quality_metrics.order_by(Month, Year).desc().first()
    quality_score = (latest.PatientSatisfactionRating / 4.0 * 20) if latest else 10

    # 6. 최종 매칭 점수
    total_matching_score = (
        difficulty_fit * 0.40 +         # 적합성: 40%
        specialization_match * 1.0 +    # 전문성: 최대 20점
        experience_score +              # 경험: 최대 20점
        quality_score                   # 품질: 최대 20점
    )

    return {
        'patient_id': patient_id,
        'caregiver_id': caregiver_id,
        'total_score': round(min(total_matching_score, 100), 1),
        'breakdown': {
            'difficulty_fit': round(difficulty_fit, 1),
            'specialization_match': specialization_match,
            'experience_score': round(experience_score, 1),
            'quality_score': round(quality_score, 1)
        },
        'grade': get_matching_grade(total_matching_score)  # ⭐⭐⭐⭐⭐
    }

def get_matching_grade(score):
    """점수를 등급으로 변환"""
    if score >= 85:
        return {'stars': '⭐⭐⭐⭐⭐', 'label': '최우선 추천', 'priority': 1}
    elif score >= 75:
        return {'stars': '⭐⭐⭐⭐', 'label': '강력 추천', 'priority': 2}
    elif score >= 65:
        return {'stars': '⭐⭐⭐', 'label': '추천', 'priority': 3}
    elif score >= 55:
        return {'stars': '⭐⭐', 'label': '약한 추천', 'priority': 4}
    else:
        return {'stars': '⭐', 'label': '비추천', 'priority': 5}

# 테스트 예시:
# Input: PatientID=101, CaregiverID=50
# Output: {'total_score': 76.2, 'grade': {'stars': '⭐⭐⭐⭐', 'label': '강력 추천'}}
```

#### Task 2.4: 상위 N명 후보 추천

```python
def recommend_top_caregivers(patient_id, top_n=5):
    """
    특정 환자에 대해 상위 N명의 간병인 후보 추천

    출력: 상위 N명 간병인 + 점수 + 이유
    """

    # 1. 모든 활성 간병인 조회
    active_caregivers = db.query(Caregivers).filter(Status='Active')

    # 2. 각 간병인과의 매칭 점수 계산
    matching_scores = []
    for caregiver in active_caregivers:
        score = calculate_matching_score(patient_id, caregiver.CaregiverID)
        matching_scores.append(score)

    # 3. 점수로 정렬 및 상위 N명 선택
    top_matches = sorted(
        matching_scores,
        key=lambda x: x['total_score'],
        reverse=True
    )[:top_n]

    # 4. 추천 저장
    for rank, match in enumerate(top_matches, start=1):
        candidate = MatchingCandidates(
            patient_id=patient_id,
            caregiver_id=match['caregiver_id'],
            rank=rank,
            candidate_score=match['total_score'],
            score_breakdown=match['breakdown'],
            status='Proposed'
        )
        db.add(candidate)
    db.commit()

    return top_matches

# 테스트 예시:
# Input: PatientID=101
# Output: [
#   {'caregiver_id': 50, 'total_score': 82.3, 'grade': ⭐⭐⭐⭐⭐, ...},
#   {'caregiver_id': 75, 'total_score': 79.1, 'grade': ⭐⭐⭐⭐, ...},
#   {'caregiver_id': 42, 'total_score': 76.5, 'grade': ⭐⭐⭐⭐, ...},
#   ...
# ]
```

#### Task 2.5: 성능 메트릭 및 A/B 테스트

```python
def evaluate_matching_performance(start_date, end_date):
    """
    특정 기간의 매칭 성과 평가
    """

    # 1. 완료된 매칭 조회
    completed_matches = db.query(MatchingHistory).filter(
        MatchingHistory.AssignmentStatus == 'Completed',
        MatchingHistory.EndDate >= start_date,
        MatchingHistory.EndDate <= end_date
    )

    # 2. 성과 지표 계산
    metrics = {
        'total_matchings': completed_matches.count(),

        'average_matching_score': completed_matches.with_entities(
            func.avg(MatchingHistory.MatchingScore)
        ).scalar(),

        'success_rate': (
            completed_matches.filter(
                MatchingHistory.PatientSatisfactionFeedback >= 4
            ).count() / completed_matches.count() * 100
        ),

        'satisfaction_scores': [
            m.PatientSatisfactionFeedback for m in completed_matches
        ],

        'performance_ratings': [
            m.CaregiverPerformanceRating for m in completed_matches
        ],

        # 각 difficulty 범위별 성공률
        'by_difficulty': calculate_success_rate_by_difficulty(completed_matches),

        # 각 caregiver job title별 성공률
        'by_job_title': calculate_success_rate_by_job_title(completed_matches),
    }

    # 3. 목표 대비 비교
    benchmarks = {
        'target_matching_score': 75,
        'target_success_rate': 80,
        'target_satisfaction': 3.5,
    }

    return {
        'metrics': metrics,
        'benchmarks': benchmarks,
        'performance': {
            'matching_score_vs_target': metrics['average_matching_score'] >= benchmarks['target_matching_score'],
            'success_rate_vs_target': metrics['success_rate'] >= benchmarks['target_success_rate'],
        }
    }

# 테스트 예시:
# Input: start_date='2024-01-01', end_date='2024-01-31'
# Output: {
#   'metrics': {
#     'total_matchings': 150,
#     'average_matching_score': 78.2,
#     'success_rate': 85.3,
#     'average_satisfaction': 3.7/4.0,
#     ...
#   },
#   'performance': {'matching_score_vs_target': True, 'success_rate_vs_target': True}
# }
```

---

### Phase 3: 대시보드 및 리포팅 (2주)

#### Task 3.1: 관리자 대시보드

**주요 화면**

```
┌─────────────────────────────────────────────────────────────────┐
│                   간병인 매칭 성과 대시보드                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 핵심 지표 (KPI)                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 전체 매칭 건수: 1,000건        평균 점수: 78/100         │  │
│  │ 성공률: 85% (목표: 80%)         만족도: 3.6/4.0         │  │
│  │ 평균 배정 기간: 15일            환자 이탈률: 5%          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📈 매칭 점수 분포                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ⭐⭐⭐⭐⭐ (85-100): 300건 (30%) 🟩 최우선               │  │
│  │ ⭐⭐⭐⭐ (75-84): 450건 (45%) 🟩 강력 추천              │  │
│  │ ⭐⭐⭐ (65-74): 200건 (20%) 🟨 추천                    │  │
│  │ ⭐⭐ (55-64): 45건 (4.5%) 🟥 약한 추천                │  │
│  │ ⭐ (<55): 5건 (0.5%) 🟥 비추천                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  👥 케어 수준별 분포 및 성과                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Care Level │ 매칭 수 │ 평균 점수 │ 만족도 │ 성공률      │  │
│  │─────────────────────────────────────────────────────────│  │
│  │ Low        │ 350    │ 82.3     │ 3.8   │ 88%         │  │
│  │ Moderate   │ 400    │ 77.9     │ 3.6   │ 85%         │  │
│  │ High       │ 250    │ 71.4     │ 3.2   │ 80%         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  👨‍⚕️ 직급별 성과 비교                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Job Title  │ 활성 수 │ 평균 점수 │ 만족도 │ 완료율      │  │
│  │─────────────────────────────────────────────────────────│  │
│  │ Nurse      │ 100    │ 84.2     │ 3.9   │ 92%         │  │
│  │ Caregiver  │ 400    │ 76.1     │ 3.5   │ 84%         │  │
│  │ Therapist  │ 200    │ 79.3     │ 3.7   │ 87%         │  │
│  │ Doctor     │ 150    │ 81.5     │ 3.8   │ 90%         │  │
│  │ Admin      │ 150    │ 72.0     │ 3.2   │ 75%         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🌍 지역별 성과 (Home Health Care 벤치마크 비교)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 우리 서비스 평균 만족도: 3.6/4.0                          │  │
│  │ Home Health Care 평균: 3.2/4.0 (상위 12%)               │  │
│  │                                                          │  │
│  │ Walking 능력 개선:                                       │  │
│  │ - 우리: 72% (목표 달성 ✓)                                │  │
│  │ - 벤치마크: 66.9%                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📋 최근 매칭 현황                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Patient      │ Caregiver    │ Score │ Status    │ Days   │  │
│  │──────────────────────────────────────────────────────────│  │
│  │ John Smith   │ Jane Johnson  │ 82    │ ✓ Active  │ 30     │  │
│  │ Mary Brown   │ Tom Williams  │ 78    │ ✓ Active  │ 15     │  │
│  │ Robert Jones │ Sarah Davis   │ 71    │ ✓ Active  │ 5      │  │
│  │ ...          │ ...           │ ...   │ ...       │ ...    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Task 3.2: 환자/가족용 주간 리포트

**리포트 샘플**

```
════════════════════════════════════════════════════════════════════
                     주간 간병인 케어 리포트
                    (2024년 11월 1주차)
════════════════════════════════════════════════════════════════════

📋 환자 정보
─────────────────────────────────────────────────────────────────
이름: John Smith (78세, 남성)
입원일: 2023-09-07
현재 케어 수준: High
담당 간병인: Jane Johnson (간호사, 경력 10년)
방 번호: 254

⭐ 매칭 평가: ⭐⭐⭐⭐⭐ (82/100 - 우수)

───────────────────────────────────────────────────────────────────

📋 이번 주 케어 현황

✅ 약물 복약 관리
  목표: 100% | 달성: 100% ✓
  약물: Metformin (500mg), Lisinopril (10mg)
  복약 시간: 오전 7시, 저녁 7시
  누락: 0건

✅ 식사 지원
  목표: 3회/일 | 달성: 3회/일 ✓
  월: 3회 | 화: 3회 | 수: 3회 | 목: 3회 | 금: 3회 | 토: 3회 | 일: 3회

✅ 운동 및 활동
  목표: 3회/주 | 달성: 3회/주 ✓
  월요일: 20분 산책 ✓
  수요일: 30분 물리치료 ✓
  금요일: 20분 산책 ✓

✅ 개인위생
  목표: 2회/주 | 달성: 2회/주 ✓
  월요일: 목욕 ✓
  목요일: 샤워 ✓

───────────────────────────────────────────────────────────────────

📊 건강 지표

혈당 관리 (당뇨 모니터링)
  평균: 120 mg/dL
  상태: Good ✓ (목표범위: 100-150)
  추세: ↘ 개선 중

혈압 (고혈압 관리)
  평균: 138/82 mmHg
  상태: Good ✓ (목표범위: <140/90)
  추세: → 안정적

심박수
  평균: 72 bpm
  상태: Good ✓ (정상범위: 60-100)

통증 관리
  통증 정도: 2/10 (낮음)
  진통제 사용: 필요시 1-2회

낙상 위험
  위험도: Low ✓
  낙상 사건: 0건
  추천: 계속 현재 케어 유지

우울증 모니터링
  증상: None ✓
  기분: 긍정적, 사회적 상호작용 증가

───────────────────────────────────────────────────────────────────

👨‍⚕️ 간병인 평가

이번 주 Jane Johnson의 성과:
⭐⭐⭐⭐⭐ (5/5)

세부 평가:
- 친절함과 전문성: ⭐⭐⭐⭐⭐ 매우 만족
- 작업 신뢰도: ⭐⭐⭐⭐⭐ 매우 높음
- 의사소통: ⭐⭐⭐⭐⭐ 우수
- 위생 관리: ⭐⭐⭐⭐⭐ 우수
- 응급 상황 대처: ⭐⭐⭐⭐⭐ 우수

가족 코멘트: "Jane은 아버지를 매우 잘 돌봐줍니다.
항상 친절하고 전문적입니다."

───────────────────────────────────────────────────────────────────

⚠️ 주의 사항 및 권장사항

✓ 현재 상태: 안정적
✓ 약물: 정상 복용 중
✓ 식사: 영양 균형 양호
✓ 활동: 목표 달성

특이사항: 없음

다음 주 권장사항:
1. 현재 약물 및 케어 플랜 유지
2. 운동량 유지 (산책 및 물리치료)
3. 정기 혈당 모니터링 계속
4. 2주마다 의사 진료 스케줄 유지

───────────────────────────────────────────────────────────────────

📞 긴급 연락처

- 간병인 Jane Johnson: 010-1234-5678
- 담당 의사 (Dr. Smith): 02-1234-5678
- 응급상황: 119

════════════════════════════════════════════════════════════════════
```

---

## 데이터 흐름 및 자동화

### 실시간 데이터 수집 및 업데이트

```
1️⃣ 일일 케어 기록 입력
   ↓
   간병인이 모바일 앱에서 입력:
   - 식사 횟수 및 내용
   - 약물 복약 시간
   - 운동 및 활동
   - 환자 상태 변화
   - 특이 사항
   ↓
   DB에 자동 저장 (Medications, Care_Records 테이블)

2️⃣ IoT 센서 데이터 수집
   ↓
   웨어러블 기기에서 자동 수집:
   - 체온 (체온계)
   - 심박수 (스마트 밴드)
   - 혈압 (혈압계)
   - 수면 패턴 (수면 추적기)
   - 낙상 감지 (낙상 센서)
   ↓
   Azure IoT Hub를 통해 DB에 저장

3️⃣ 월별 만족도 조사
   ↓
   자동으로 이메일/SMS 발송:
   - 환자/가족: 간병인 평가 (1-5점)
   - 간병인: 업무 만족도 조사
   - 의료 담당자: 환자 상태 평가
   ↓
   응답 데이터 → QualityMetrics 테이블 업데이트

4️⃣ 월간 알고리즘 재학습
   ↓
   [매달 1회 자동 실행]
   - 수집된 모든 데이터 분석
   - 매칭 성공/실패 사례 검토
   - 새로운 가중치 재계산
   - 모델 개선
   ↓
   새로운 매칭 추천 생성

5️⃣ 실시간 대시보드 업데이트
   ↓
   [매시간 자동 갱신]
   - 현재 활성 매칭 상태
   - 성과 지표 (KPI) 계산
   - Home Health Care 벤치마크 비교
   - 알림 생성 (이상 상황 감지)

6️⃣ 정기 리포트 생성
   ↓
   [주간/월간 자동 생성]
   - Azure OpenAI 기반 자동 요약
   - 환자/가족용 리포트
   - 관리자용 분석 리포트
   - 의료 담당자용 상세 리포트
   ↓
   이메일 및 앱 푸시 알림 발송
```

### 자동화 워크플로우 (Scheduled Jobs)

```python
# task_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
import datetime

scheduler = BackgroundScheduler()

# 1. 매일 오전 6시: IoT 데이터 동기화
@scheduler.scheduled_job('cron', hour=6, minute=0)
def sync_iot_data():
    """IoT Hub에서 센서 데이터 수집"""
    iot_manager.fetch_data()
    db.update_health_metrics()
    check_abnormalities()

# 2. 매일 오후 12시: 일일 케어 현황 정리
@scheduler.scheduled_job('cron', hour=12, minute=0)
def summarize_daily_care():
    """일일 케어 기록 정리 및 통계"""
    daily_care_stats()
    detect_anomalies()

# 3. 매주 금요일: 주간 리포트 생성
@scheduler.scheduled_job('cron', day_of_week='fri', hour=18, minute=0)
def generate_weekly_report():
    """가족/환자용 주간 리포트 생성"""
    for patient_id in get_active_patients():
        report = generate_patient_report(patient_id, period='weekly')
        send_to_family(patient_id, report)

# 4. 매월 1일: 만족도 조사 발송
@scheduler.scheduled_job('cron', day=1, hour=9, minute=0)
def send_monthly_survey():
    """환자/간병인 만족도 조사 발송"""
    for patient_id in get_active_patients():
        send_survey_email(patient_id, survey_type='patient')
    for caregiver_id in get_active_caregivers():
        send_survey_email(caregiver_id, survey_type='caregiver')

# 5. 매월 15일: 알고리즘 재학습
@scheduler.scheduled_job('cron', day=15, hour=22, minute=0)
def retrain_matching_algorithm():
    """매칭 알고리즘 개선"""
    training_data = collect_training_data()
    model = train_matching_model(training_data)
    save_new_model(model)
    generate_new_recommendations()

# 6. 매시간: 대시보드 KPI 업데이트
@scheduler.scheduled_job('interval', hours=1)
def update_dashboard_kpi():
    """실시간 대시보드 데이터 갱신"""
    update_matching_scores()
    update_quality_metrics()
    check_alerts()

# 7. 매일 오전 8시: 이상 감지 및 알림
@scheduler.scheduled_job('cron', hour=8, minute=0)
def detect_and_alert():
    """이상 상황 감지 및 알림 발송"""
    check_health_anomalies()
    check_medication_compliance()
    check_activity_changes()
    send_alerts_to_admin()

scheduler.start()
```

---

## 기술 스택 및 구현 가이드

### 기술 스택 매트릭스

| 계층 | 기술 | 역할 | 선택 이유 |
|------|------|------|---------|
| **Data Processing** | Pandas + NumPy | CSV 정제, 결측치 처리, 통계 분석 | 데이터 조작에 최적화 |
| **Data Pipeline** | Apache Airflow / Prefect | ETL 워크플로우 자동화 | 복잡한 데이터 흐름 관리 |
| **Machine Learning** | Scikit-learn | 분류, 거리 기반 매칭 | 가볍고 빠른 알고리즘 |
| **Deep Learning** (확장) | TensorFlow / PyTorch | 복잡한 패턴 인식 | 향후 고도화용 |
| **Database** | Azure SQL / PostgreSQL | 구조화된 데이터 저장 | ACID 보장, 확장성 |
| **API** | FastAPI / Django REST | 매칭 추천 및 데이터 조회 API | 빠른 성능, 자동 문서화 |
| **Scheduling** | APScheduler / Celery | 정기 작업 (월간 리포트, 알고리즘 재학습) | 배경 작업 처리 |
| **Frontend** | React + TypeScript | 관리자/환자 대시보드 | 반응형, 모던 UI |
| **Visualization** | Chart.js / D3.js | 그래프 및 차트 | 풍부한 시각화 |
| **AI/NLP** | Azure OpenAI / GPT | 리포트 자동 요약, 질문 응답 | 자연스러운 텍스트 생성 |
| **Cloud** | Microsoft Azure | 전체 인프라 | 프로젝트 아키텍처 통일 |
| **CI/CD** | GitHub Actions / Azure DevOps | 자동 테스트 및 배포 | 개발 효율성 증대 |

### 프로젝트 폴더 구조

```
bluedonulab/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI 앱 진입점
│   │   ├── config.py                        # 설정 (DB, API 키 등)
│   │   ├── database.py                      # DB 연결 설정
│   │   ├── models/
│   │   │   ├── patient.py                   # Patient 모델
│   │   │   ├── caregiver.py                 # Caregiver 모델
│   │   │   ├── medication.py                # Medication 모델
│   │   │   ├── matching.py                  # MatchingHistory 모델
│   │   │   └── quality_metrics.py           # QualityMetrics 모델
│   │   ├── schemas/
│   │   │   ├── patient_schema.py            # Patient 요청/응답 스키마
│   │   │   ├── matching_schema.py           # Matching 요청/응답 스키마
│   │   │   └── ...
│   │   ├── routes/
│   │   │   ├── patients.py                  # /api/patients 엔드포인트
│   │   │   ├── caregivers.py                # /api/caregivers 엔드포인트
│   │   │   ├── matching.py                  # /api/matching 엔드포인트
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── patient_service.py           # 환자 비즈니스 로직
│   │   │   ├── caregiver_service.py         # 간병인 비즈니스 로직
│   │   │   ├── matching_engine.py           # 매칭 알고리즘 핵심
│   │   │   ├── data_processing.py           # 데이터 정제 및 전처리
│   │   │   └── quality_evaluation.py        # 품질 평가 로직
│   │   └── utils/
│   │       ├── decorators.py                # 커스텀 데코레이터
│   │       ├── exceptions.py                # 커스텀 예외 처리
│   │       └── helpers.py                   # 유틸리티 함수
│   ├── jobs/
│   │   ├── scheduler.py                     # APScheduler 설정
│   │   ├── daily_tasks.py                   # 일일 작업
│   │   ├── weekly_tasks.py                  # 주간 작업
│   │   ├── monthly_tasks.py                 # 월간 작업
│   │   └── iot_sync.py                      # IoT 데이터 동기화
│   ├── tests/
│   │   ├── test_matching_engine.py          # 매칭 알고리즘 테스트
│   │   ├── test_patient_service.py          # 환자 서비스 테스트
│   │   └── ...
│   ├── requirements.txt                      # Python 의존성
│   └── Dockerfile                            # 도커 이미지
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── index.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   │   ├── AdminDashboard.tsx       # 관리자 대시보드
│   │   │   │   ├── PatientDashboard.tsx     # 환자 대시보드
│   │   │   │   └── ...
│   │   │   ├── Forms/
│   │   │   ├── Charts/
│   │   │   └── ...
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.ts                       # API 클라이언트
│   │   ├── styles/
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
│
├── data/
│   ├── raw/
│   │   ├── healthcare_dataset.csv
│   │   ├── HomeHealthCare-StatebyStateData.csv
│   │   ├── Residents.csv
│   │   ├── Staff.csv
│   │   ├── Medications.csv
│   │   └── ...
│   ├── processed/
│   │   ├── patients_processed.csv
│   │   ├── caregivers_processed.csv
│   │   └── ...
│   └── scripts/
│       ├── data_cleaning.py                 # 데이터 정제
│       ├── data_integration.py              # 데이터 통합
│       └── data_loading.py                  # DB 로딩
│
├── notebooks/
│   ├── 01_data_exploration.ipynb            # 데이터 탐색
│   ├── 02_matching_algorithm_dev.ipynb      # 알고리즘 개발
│   ├── 03_performance_analysis.ipynb        # 성과 분석
│   └── ...
│
├── docs/
│   ├── architecture.md                      # 아키텍처 설계
│   ├── api_documentation.md                 # API 문서
│   ├── data_dictionary.md                   # 데이터 사전
│   └── user_guide.md                        # 사용 설명서
│
├── docker-compose.yml                        # 도커 구성
├── .env.example                              # 환경 변수 예제
├── .gitignore
└── README.md
```

---

## 다음 단계

### 우선순위별 구현 로드맵

#### ✅ Phase 1: 데이터 기초 (1주)
- [ ] CAREHOME 데이터 정제 및 검증
- [ ] Healthcare Dataset 매핑 테이블 생성
- [ ] Home Health Care 벤치마크 데이터 로드
- [ ] 통합 DB 스키마 설계 및 구현

#### ✅ Phase 2: 알고리즘 개발 (2주)
- [ ] 환자 난이도 계산 엔진 구현
- [ ] 간병인 역량 평가 엔진 구현
- [ ] 매칭 점수 계산 로직 구현
- [ ] 상위 N명 추천 알고리즘 구현
- [ ] 단위 테스트 및 통합 테스트

#### ✅ Phase 3: 백엔드 API (1주)
- [ ] FastAPI 프로젝트 초기화
- [ ] Patients, Caregivers, Matching 엔드포인트 구현
- [ ] API 인증 및 권한 설정
- [ ] API 문서화 (Swagger)

#### ✅ Phase 4: 대시보드 (2주)
- [ ] React 프로젝트 초기화
- [ ] 관리자 대시보드 UI 구현
- [ ] 환자/가족 포털 UI 구현
- [ ] 차트 및 시각화 구현

#### ✅ Phase 5: 자동화 및 배포 (1주)
- [ ] 정기 작업 스케줄러 설정
- [ ] Azure 클라우드 배포
- [ ] CI/CD 파이프라인 구성
- [ ] 모니터링 및 로깅 설정

---

## 참고 자료

### 데이터셋 요약
- **CAREHOME**: 1,000명 거주자 + 1,000명 직원 + 2,000개 약물 처방
- **Healthcare**: 50,000+ 행의 다양한 의료 상태 환자 정보
- **Home Health Care**: 50개 주의 케어 품질 KPI 벤치마크

### 핵심 메트릭
- 매칭 점수: 0~100점 (목표: 75점 이상)
- 성공률: 목표 80% 이상
- 환자 만족도: 목표 3.5/4.0 이상
- Home Health Care 벤치마크 대비: 상위 10% 이상

---

**문서 작성일**: 2024년 11월 5일
**마지막 업데이트**: 2024년 11월 5일
**버전**: 1.0
