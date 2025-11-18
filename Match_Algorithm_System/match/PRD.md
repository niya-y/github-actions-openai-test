# 🎯 BluedonuLab 간병인 매칭 시스템 - PRD (Product Requirements Document)

## 1. 개요

### 1.1 제품명
**BluedonuLab Caregiver Matching System** - 성향 기반 간병인 매칭 플랫폼

### 1.2 핵심 가치 제안
기존 간병 서비스는 의료 필요도(Care Level)만 고려했다면, BluedonuLab은:
- 환자의 **심리적 성향** (공감 요구, 독립성, 활동성, 인내심) 파악
- 간병인의 **돌봄 스타일** 분석
- **성향 매칭도** 기반 최적 배정 → 높은 만족도 & 신뢰 구축

---

## 2. 주요 기능 요구사항

### 2.1 환자 성향 테스트 시스템
**기능**: 환자의 심리적 성향을 4가지 축으로 측정
- **공감도(Empathy)**: 감정적 지지 필요도 (0~100)
- **활동성(Activity)**: 활동적이고 싶은 정도 (0~100)
- **인내심(Patience)**: 간병인의 인내심 필요도 (0~100)
- **독립성(Independence)**: 자립하고자 하는 정도 (0~100)

**입력**: 12개 질문에 대한 선택지 답변
**출력**: 성향 점수 + 성향 타입 분류 + AI 기반 설명

### 2.2 간병인 스타일 분석
**기능**: 간병인의 돌봄 특성을 4가지 차원으로 분석
- **공감 능력(Empathy)**: 감정 이입도
- **활동 지원(Activity Support)**: 활동 유도 능력
- **인내심(Patience)**: 반복된 요청에 대한 인내
- **독립 지원(Independence Support)**: 자립 지원 정도

**입력**: Staff 데이터셋 + Job Title 분석 + 경험도
**출력**: 스타일 점수 + 돌봄 성향 분류

### 2.3 성향 기반 매칭 알고리즘
**기능**: 환자와 간병인의 성향 일치도 계산
- **2단계 매칭**:
  1. **1단계 (의료 필요도)**: Care Level과 Job Title 기반 기본 후보 필터링
  2. **2단계 (성향 매칭)**: 성향 점수 기반 최적 매칭도 계산

**계산 로직**:
```
최종 매칭도 = (의료적합도 × 0.4) + (성향일치도 × 0.6)
```

**출력**: 상위 N명의 추천 간병인 + 매칭도 + 추천 이유

### 2.4 매칭 결과 관리
**기능**: 매칭 이력 저장 및 조회
- 매칭 생성 & 취소 관리
- 매칭 히스토리 조회
- 일일 리포트 생성
- 매칭 성과 지표 모니터링

---

## 3. 데이터 요구사항

### 3.1 입력 데이터셋

| 파일명 | 규모 | 용도 | 필수 |
|--------|------|------|-----|
| `Residents.csv` | 1,000명 | 환자 기본정보 + Care Level | ✅ |
| `staff.csv` | 1,000명 | 간병인 기본정보 + Job Title | ✅ |
| `medications.csv` | 2,000개 | 약물 복잡도 지표 | ⭐ |
| `healthcare_dataset.csv` | 50,000+ | 의료 상태별 확장 데이터 | 선택 |

### 3.2 출력 데이터셋

| 테이블명 | 설명 | 주요 컬럼 |
|---------|------|---------|
| `PatientPersonality` | 환자 성향 점수 | PatientID, Empathy, Activity, Patience, Independence, Type |
| `CaregiverStyle` | 간병인 스타일 분석 | CaregiverID, Empathy, ActivitySupport, Patience, IndependenceSupport |
| `PersonalityBasedMatching` | 매칭 결과 | MatchingID, PatientID, CaregiverID, MatchingScore, Grade, Status |
| `MatchingHistory` | 매칭 이력 | HistoryID, MatchingID, PatientID, CaregiverID, CreatedAt, Status |
| `DailyReport` | 일일 리포트 | ReportID, MatchingID, Date, Content, Status |

---

## 4. 시스템 아키텍처

### 4.1 데이터 흐름
```
원본 CSV 파일
    ↓
데이터 전처리 & 정규화
    ↓
환자 성향 계산 (PatientPersonality 생성)
간병인 스타일 분석 (CaregiverStyle 생성)
    ↓
매칭 알고리즘 실행
    ↓
PersonalityBasedMatching 테이블 생성
    ↓
추천 결과 & 리포트 생성
```

### 4.2 모듈 구조
```
match/
├── data/
│   ├── Residents.csv           (복사본)
│   ├── staff.csv               (복사본)
│   ├── medications.csv         (복사본)
│   ├── healthcare_dataset.csv  (선택사항)
│   └── processed_data/         (전처리된 데이터)
│       ├── residents_processed.csv
│       ├── staff_processed.csv
│       └── medications_processed.csv
├── models/
│   ├── data_loader.py          (데이터 로딩 및 전처리)
│   ├── personality_calculator.py (성향 점수 계산)
│   ├── caregiver_analyzer.py   (간병인 스타일 분석)
│   └── matching_algorithm.py   (매칭 알고리즘)
├── database/
│   ├── schema.py               (DB 스키마 정의)
│   └── connection.py           (DB 연결 관리)
├── services/
│   ├── personality_service.py  (성향 관련 비즈니스 로직)
│   ├── matching_service.py     (매칭 관련 비즈니스 로직)
│   └── report_service.py       (리포트 생성 로직)
├── api/
│   ├── personality_routes.py   (성향 API 엔드포인트)
│   ├── matching_routes.py      (매칭 API 엔드포인트)
│   └── report_routes.py        (리포트 API 엔드포인트)
├── tests/
│   ├── test_personality.py
│   ├── test_matching.py
│   └── test_services.py
├── config.py                   (설정 파일)
├── main.py                     (메인 실행 파일)
├── PRD.md                      (이 문서)
├── TASK.md                     (구현 계획)
└── README.md                   (사용 설명서)
```

---

## 5. 성향 분류 체계

### 5.1 4가지 축 (Dimensions)

#### 축 1: 공감도 (Empathy)
- **Low** (자립형): "내가 스스로 해결하고 싶다"
- **High** (공감형): "감정적인 지지가 정말 필요하다"

#### 축 2: 활동성 (Activity)
- **Low** (휴식형): "최소한의 활동으로 충분"
- **High** (활동형): "많은 활동과 자극 필요"

#### 축 3: 인내심 (Patience)
- **Low** (급한 성격): "빠르고 효율적으로"
- **High** (차분함): "차분하고 몇 번이고 설명해주는 것"

#### 축 4: 독립성 (Independence)
- **Low** (의존형): "자주, 자세한 지원 필요"
- **High** (독립형): "가능하면 스스로 하되, 필요할 때만"

### 5.2 성향 타입 분류 (4가지)

| 타입 | 특징 | 권장 간병인 | 리포트 스타일 |
|------|------|-----------|-------------|
| **공감 중심형** | 감정적 유대감 중요, 인내심 필요 | Caregiver + 높은 공감 | "오늘도 미소가 많았습니다 😊" |
| **활동 중심형** | 다양한 활동 & 자극 원함 | Therapist + Active | "오늘 30분 산책했습니다!" |
| **자립형** | 혼자 할 수 있으면 스스로, 필요할 때만 도움 | Professional Caregiver | "필요한 도움만 제공했습니다" |
| **전담형** | 자주 도움 필요, 세심한 관리 필요 | Nurse + Specialist | "매시간 상태 확인했습니다" |

---

## 6. 성과 지표 (KPIs)

### 6.1 매칭 성과
- **평균 매칭도**: 목표 75 이상
- **성공률**: 매칭 후 만족도 80% 이상
- **재매칭율**: 30일 이내 5% 이하

### 6.2 시스템 성과
- **데이터 품질**: 결측치 < 2%
- **응답시간**: 매칭 조회 < 1초
- **가용성**: 99.9% 이상

---

## 7. 제약사항 및 가정

### 7.1 제약사항
- 초기 데이터는 CSV 파일 기반
- 환자와 간병인의 성향 재평가는 월 1회
- 매칭은 Care Level 적합성이 우선

### 7.2 가정
- 환자 성향은 12개 질문으로 충분히 파악 가능
- 간병인 Job Title이 스타일을 대표한다고 가정
- 매칭도 계산에는 의료도(40%) + 성향도(60%)의 비율 적용

---

## 8. 마일스톤

| 단계 | 기간 | 목표 | 산출물 |
|------|------|------|--------|
| **Phase 1: 기반 구축** | 1주 | 데이터 전처리 완료 | Processed CSV, DB Schema |
| **Phase 2: 핵심 알고리즘** | 2주 | 성향 계산 & 매칭 알고리즘 | Personality, Matching Models |
| **Phase 3: 서비스 개발** | 2주 | API & Business Logic | Services, Routes |
| **Phase 4: 테스트 & 배포** | 1주 | 통합 테스트 완료 | Tests, Documentation |

---

## 9. 성공 기준

✅ **Functional Success**
- 성향 테스트 점수 계산 정확도 > 95%
- 매칭 알고리즘이 상위 5명을 정확히 추천
- 모든 API 엔드포인트가 작동

✅ **Performance Success**
- 매칭 조회 응답시간 < 1초
- 일일 리포트 생성 < 5초
- 1,000명 이상 데이터 처리 가능

✅ **User Success**
- 추천 간병인에 대한 만족도 80% 이상
- 사용자 온보딩 완료율 > 90%

---

## 10. 향후 확장 사항

- [ ] 실시간 성향 조정 (피드백 기반)
- [ ] AI/ML 기반 매칭도 최적화
- [ ] 간병인 교육 프로그램 연동
- [ ] 다국어 지원
- [ ] 모바일 앱 네이티브 버전
- [ ] IoT 센서 데이터 연동
