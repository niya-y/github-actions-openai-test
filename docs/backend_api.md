# 늘봄케어 백엔드 API 문서

> BluedonuLab API - 환자-간병인 매칭 시스템
>
> Version: 1.0.0

## 목차

1. [개요](#개요)
2. [인증](#인증)
3. [API 엔드포인트](#api-엔드포인트)
   - [인증 (Auth)](#1-인증-auth)
   - [보호자 (Guardians)](#2-보호자-guardians)
   - [환자 (Patients)](#3-환자-patients)
   - [OCR 및 의약품 검색](#4-ocr-및-의약품-검색)
   - [대시보드 (Dashboard)](#5-대시보드-dashboard)
   - [프로필 관리 (Profiles)](#6-프로필-관리-profiles)
   - [매칭 (Matching)](#7-매칭-matching)
   - [XGBoost 매칭](#8-xgboost-매칭)
   - [케어 실행 (Care Execution)](#9-케어-실행-care-execution)
   - [리뷰 (Reviews)](#10-리뷰-reviews)
   - [성격 테스트 (Personality)](#11-성격-테스트-personality)
   - [케어 플랜 생성 (Care Plans)](#12-케어-플랜-생성-care-plans)
   - [헬스 체크](#13-헬스-체크)
4. [스키마 정의](#스키마-정의)
5. [외부 연동](#외부-연동)

---

## 개요

### 기본 정보

- **Base URL**: `/api` (대부분의 엔드포인트)
- **Content-Type**: `application/json`
- **인코딩**: UTF-8

### CORS 설정

```
Allow Origins: settings.FRONTEND_URL, http://localhost:3000
Allow Credentials: True
Allow Methods: All
Allow Headers: All
```

### 응답 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 201 | 생성됨 (POST 성공) |
| 204 | 내용 없음 (DELETE 성공) |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스를 찾을 수 없음 |
| 500 | 서버 내부 오류 |

---

## 인증

### 인증 방식

1. **JWT Bearer Token** (권장)
   ```
   Authorization: Bearer <token>
   ```

2. **HttpOnly Cookie** (대체)
   - 쿠키 이름: `access_token`
   - SameSite: lax
   - Secure: True
   - Max Age: 7일 (604,800초)

### JWT 설정

- **알고리즘**: HS256
- **만료 시간**: 7일 (60 * 24 * 7분)
- **Secret Key**: 환경 변수에서 로드

### 비밀번호 보안

- Bcrypt 해싱 사용
- Passlib 컨텍스트로 검증

---

## API 엔드포인트

### 1. 인증 (Auth)

**파일 위치**: `backend/app/routes/auth.py`

#### 1.1 카카오 OAuth 로그인 URL 조회

```
GET /auth/kakao/login
```

**인증**: 불필요

**응답**:
```json
{
  "url": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code"
}
```

---

#### 1.2 카카오 OAuth 콜백

```
GET /auth/kakao/callback
```

**인증**: 불필요

**쿼리 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| code | string | O | 카카오 인증 코드 |

**응답**: 프론트엔드로 리다이렉트 (JWT 토큰 포함 쿠키 설정)

---

#### 1.3 이메일/비밀번호 로그인

```
POST /auth/login
```

**인증**: 불필요

**요청 본문** (`LoginRequest`):
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답** (`LoginResponse`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### 1.4 현재 사용자 조회

```
GET /auth/me
```

**인증**: 필수 (JWT Bearer Token)

**응답** (`UserResponse`):
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "phone_number": "010-1234-5678",
  "user_type": "guardian",
  "profile_image_url": "https://...",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| user_id | integer | 사용자 ID |
| email | string (optional) | 이메일 |
| name | string | 이름 |
| phone_number | string (optional) | 전화번호 |
| user_type | enum | "guardian" 또는 "caregiver" |
| profile_image_url | string (optional) | 프로필 이미지 URL |
| is_active | boolean | 활성화 상태 |
| created_at | datetime | 생성일시 |
| updated_at | datetime | 수정일시 |

---

### 2. 보호자 (Guardians)

**파일 위치**: `backend/app/routes/guardians.py`

#### 2.1 보호자 정보 등록/수정

```
POST /api/guardians
```

**인증**: 필수 (JWT Bearer Token)

**요청 본문** (`GuardianCreateRequest`):
```json
{
  "name": "홍길동",
  "phone": "010-1234-5678",
  "address": "서울시 강남구 테헤란로 123",
  "relationship": "자녀"
}
```

| 필드 | 타입 | 필수 | 유효성 검사 | 설명 |
|------|------|------|-------------|------|
| name | string | O | 1-50자 | 보호자 이름 |
| phone | string | O | `010-\d{4}-\d{4}` 패턴 | 전화번호 |
| address | string | O | 1-255자 | 주소 |
| relationship | string | O | - | 환자와의 관계 |

**응답** (`GuardianInfoResponse`):
```json
{
  "guardian_id": 1,
  "user_id": 1,
  "name": "홍길동",
  "phone": "010-1234-5678",
  "address": "서울시 강남구 테헤란로 123",
  "relationship": "자녀",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### 2.2 내 보호자 정보 조회

```
GET /api/guardians/me
```

**인증**: 필수 (JWT Bearer Token)

**응답**: `GuardianInfoResponse` (2.1과 동일)

---

### 3. 환자 (Patients)

**파일 위치**: `backend/app/routes/patients.py`

#### 3.1 환자 등록

```
POST /api/patients
```

**인증**: 필수 (JWT Bearer Token)

**요청 본문** (`PatientCreateRequest`):
```json
{
  "name": "김환자",
  "age": 75,
  "gender": "male",
  "relationship": "부모"
}
```

| 필드 | 타입 | 필수 | 유효성 검사 | 설명 |
|------|------|------|-------------|------|
| name | string | O | 1-50자 | 환자 이름 |
| age | integer | O | 0-150 | 나이 |
| gender | string | O | `male\|female` | 성별 |
| relationship | string | O | - | 보호자와의 관계 |

**응답** (`PatientInfoResponse`):
```json
{
  "patient_id": 1,
  "name": "김환자",
  "birth_date": "1949-01-01",
  "age": 75,
  "gender": "Male",
  "guardian_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### 3.2 내 환자 목록 조회

```
GET /api/patients/me
```

**인증**: 필수 (JWT Bearer Token)

**응답**:
```json
{
  "patients": [
    {
      "patient_id": 1,
      "name": "김환자",
      "birth_date": "1949-01-01",
      "age": 75,
      "gender": "Male",
      "guardian_id": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "latest_patient": { ... },
  "total": 1
}
```

---

#### 3.3 특정 환자 조회

```
GET /api/patients/{patient_id}
```

**인증**: 필수 (JWT Bearer Token)

**경로 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 ID |

**응답**: `PatientInfoResponse` (3.1과 동일)

---

#### 3.4 환자 건강 상태 조회

```
GET /api/patients/{patient_id}/health-status
```

**인증**: 필수 (JWT Bearer Token)

**경로 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 ID |

**응답**:
```json
{
  "patient_id": 1,
  "selected_diseases": [
    { "id": "diabetes", "name": "당뇨" },
    { "id": "hypertension", "name": "고혈압" }
  ],
  "mobility_status": "wheelchair"
}
```

---

#### 3.5 환자 건강 상태 수정

```
PUT /api/patients/{patient_id}/health-status
```

**인증**: 필수 (JWT Bearer Token)

**경로 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 ID |

**요청 본문** (`HealthStatusUpdateRequest`):
```json
{
  "selectedDiseases": [
    { "id": "diabetes", "name": "당뇨" },
    { "id": "hypertension", "name": "고혈압" }
  ],
  "mobility_status": "wheelchair"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| selectedDiseases | array of DiseaseItem | 선택된 질환 목록 |
| mobility_status | string | 이동 상태: `independent`, `assistive-device`, `wheelchair`, `bedridden` |

**응답**:
```json
{
  "patient_id": 1,
  "selected_diseases": [...],
  "mobility_status": "wheelchair",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### 3.6 환자 복용 약물 조회

```
GET /api/patients/{patient_id}/medications
```

**인증**: 필수 (JWT Bearer Token)

**경로 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 ID |

**응답**:
```json
{
  "patient_id": 1,
  "medicine_names": ["아스피린", "메트포르민", "리피토"]
}
```

---

#### 3.7 환자 복용 약물 등록/수정

```
POST /api/patients/{patient_id}/medications
```

**인증**: 필수 (JWT Bearer Token)

**경로 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 ID |

**요청 본문** (`MedicationsCreateRequest`):
```json
{
  "medicine_names": ["아스피린", "메트포르민", "리피토"]
}
```

| 필드 | 타입 | 필수 | 유효성 검사 | 설명 |
|------|------|------|-------------|------|
| medicine_names | array of string | O | 최소 1개 | 약품명 목록 |

**응답** (`MedicationInfoResponse`):
```json
{
  "patient_id": 1,
  "med_id": 1,
  "medicine_names": ["아스피린", "메트포르민", "리피토"]
}
```

---

### 4. OCR 및 의약품 검색

**파일 위치**: `backend/app/routes/ocr.py`

#### 4.1 약물 이미지 OCR 분석

```
POST /api/patients/{patient_id}/medications/ocr
```

**인증**: 불필요

**경로 파라미터**:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| patient_id | integer | 환자 ID |

**요청**: Multipart form-data

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | UploadFile | O | 이미지 파일 (JPG, PNG, 최대 10MB) |

**응답** (`OCRResultResponse`):
```json
{
  "success": true,
  "medicines": [
    {
      "item_name": "아스피린정",
      "entp_name": "바이엘코리아",
      "item_seq": "123456789",
      "efficacy": "해열, 진통, 소염",
      "usage": "1일 3회, 1회 1정",
      "precaution": "위장장애 주의",
      "side_effect": "위장장애, 출혈",
      "storage": "실온보관",
      "interaction": "항응고제와 병용 주의",
      "item_image": "https://..."
    }
  ],
  "medicine_names": ["아스피린정"],
  "confidence": 0.95,
  "unverified_names": [],
  "message": "1개의 약품이 인식되었습니다."
}
```

---

#### 4.2 의약품 정보 검색

```
GET /api/medicines/search
```

**인증**: 불필요

**쿼리 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| item_name | string | O | 검색할 약품명 |

**응답**: 식약처 MFDS API 응답 형식

---

### 5. 대시보드 (Dashboard)

**파일 위치**: `backend/app/routes/dashboard.py`

#### 5.1 내 대시보드 조회

```
GET /api/users/me/dashboard
```

**인증**: 필수 (JWT Bearer Token)

**응답** (`DashboardResponse`):
```json
{
  "user": {
    "user_id": 1,
    "name": "홍길동",
    "email": "user@example.com",
    "phone": "010-1234-5678",
    "user_type": "guardian",
    "gender": "male"
  },
  "guardian": {
    "guardian_id": 1,
    "address": "서울시 강남구",
    "relationship": "자녀"
  },
  "patients": [
    {
      "patient_id": 1,
      "name": "김환자",
      "age": 75,
      "care_level": "중증"
    }
  ],
  "active_matching": {
    "caregiver_name": "박간병",
    "match_score": 85.5,
    "start_date": "2024-01-15"
  }
}
```

---

### 6. 프로필 관리 (Profiles)

**파일 위치**: `backend/app/routes/profile.py`

#### 6.1 보호자 프로필

##### 보호자 목록 조회
```
GET /api/profiles/guardians
```

**쿼리 파라미터**:

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| skip | integer | 0 | 건너뛸 항목 수 |
| limit | integer | 100 | 최대 조회 수 |

**응답**: `GuardianResponse[]`

---

##### 특정 보호자 조회
```
GET /api/profiles/guardians/{guardian_id}
```

**응답**: `GuardianResponse`

---

##### 보호자 생성
```
POST /api/profiles/guardians
```

**요청**: `GuardianCreate`

**응답**: `GuardianResponse` (201 Created)

---

##### 보호자 수정
```
PUT /api/profiles/guardians/{guardian_id}
```

**요청**: `GuardianUpdate`

**응답**: `GuardianResponse`

---

##### 보호자 삭제
```
DELETE /api/profiles/guardians/{guardian_id}
```

**응답**: 204 No Content

---

#### 6.2 환자 프로필

##### 환자 목록 조회
```
GET /api/profiles/patients
```

**응답**: `PatientResponse[]`

---

##### 특정 환자 조회
```
GET /api/profiles/patients/{patient_id}
```

**응답**: `PatientResponse`

---

##### 환자 생성
```
POST /api/profiles/patients
```

**요청**: `PatientCreate`

**응답**: `PatientResponse` (201 Created)

---

##### 환자 수정
```
PUT /api/profiles/patients/{patient_id}
```

**요청**: `PatientUpdate`

**응답**: `PatientResponse`

---

##### 환자 삭제
```
DELETE /api/profiles/patients/{patient_id}
```

**응답**: 204 No Content

---

#### 6.3 간병인 프로필

##### 간병인 목록 조회
```
GET /api/profiles/caregivers
```

**응답**: `CaregiverResponse[]`

---

##### 특정 간병인 조회
```
GET /api/profiles/caregivers/{caregiver_id}
```

**응답**: `CaregiverResponse`

---

##### 간병인 생성
```
POST /api/profiles/caregivers
```

**요청**: `CaregiverCreate`

**응답**: `CaregiverResponse` (201 Created)

---

##### 간병인 수정
```
PUT /api/profiles/caregivers/{caregiver_id}
```

**요청**: `CaregiverUpdate`

**응답**: `CaregiverResponse`

---

##### 간병인 삭제
```
DELETE /api/profiles/caregivers/{caregiver_id}
```

**응답**: 204 No Content

---

### 7. 매칭 (Matching)

**파일 위치**: `backend/app/routes/matching.py`

#### 7.1 간병인 가용성 (Availability)

##### 가용성 목록 조회
```
GET /api/matching/availability
```

**쿼리 파라미터**:

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| skip | integer | 0 | 건너뛸 항목 수 |
| limit | integer | 100 | 최대 조회 수 |

**응답**: `CaregiverAvailabilityResponse[]`

---

##### 특정 가용성 조회
```
GET /api/matching/availability/{availability_id}
```

**응답**: `CaregiverAvailabilityResponse`

---

##### 가용성 생성
```
POST /api/matching/availability
```

**요청**: `CaregiverAvailabilityCreate`

**응답**: `CaregiverAvailabilityResponse` (201 Created)

---

##### 가용성 수정
```
PUT /api/matching/availability/{availability_id}
```

**요청**: `CaregiverAvailabilityUpdate`

**응답**: `CaregiverAvailabilityResponse`

---

##### 가용성 삭제
```
DELETE /api/matching/availability/{availability_id}
```

**응답**: 204 No Content

---

#### 7.2 매칭 요청 (Requests)

##### 매칭 요청 목록 조회
```
GET /api/matching/requests
```

**응답**: `MatchingRequestResponse[]`

---

##### 특정 매칭 요청 조회
```
GET /api/matching/requests/{request_id}
```

**응답**: `MatchingRequestResponse`

---

##### 매칭 요청 생성
```
POST /api/matching/requests
```

**요청**: `MatchingRequestCreate`

**응답**: `MatchingRequestResponse` (201 Created)

---

##### 매칭 요청 수정
```
PUT /api/matching/requests/{request_id}
```

**요청**: `MatchingRequestUpdate`

**응답**: `MatchingRequestResponse`

---

##### 매칭 요청 삭제
```
DELETE /api/matching/requests/{request_id}
```

**응답**: 204 No Content

---

#### 7.3 매칭 결과 (Results)

##### 매칭 결과 목록 조회
```
GET /api/matching/results
```

**응답**: `MatchingResultResponse[]`

---

##### 특정 매칭 결과 조회
```
GET /api/matching/results/{result_id}
```

**응답**: `MatchingResultResponse`

---

##### 매칭 결과 생성
```
POST /api/matching/results
```

**요청**: `MatchingResultCreate`

**응답**: `MatchingResultResponse` (201 Created)

---

##### 매칭 결과 수정
```
PUT /api/matching/results/{result_id}
```

**요청**: `MatchingResultUpdate`

**응답**: `MatchingResultResponse`

---

##### 매칭 결과 삭제
```
DELETE /api/matching/results/{result_id}
```

**응답**: 204 No Content

---

##### 향상된 매칭 결과 조회
```
GET /api/matching/results-enhanced
```

**쿼리 파라미터**:

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| skip | integer | 0 | 건너뛸 항목 수 |
| limit | integer | 100 | 최대 조회 수 |

**응답**: 프론트엔드 형식으로 포맷된 간병인 데이터 배열

---

### 8. XGBoost 매칭

**파일 위치**: `backend/app/routes/xgboost_matching.py`

#### 8.1 간병인 AI 추천

```
POST /api/matching/recommend-xgboost
```

**인증**: 불필요

**요청 본문** (`XGBoostMatchingRequest`):
```json
{
  "patient_id": 1,
  "patient_personality": {
    "empathy_score": 75.0,
    "activity_score": 60.0,
    "patience_score": 80.0,
    "independence_score": 45.0
  },
  "requirements": {
    "care_type": "time",
    "time_slots": ["morning", "afternoon"],
    "gender": "female",
    "experience": "3years+",
    "skills": ["치매케어", "물리치료보조"]
  },
  "preferred_days": ["월", "화", "수", "목", "금"],
  "preferred_time_slots": ["09:00-12:00", "14:00-18:00"],
  "care_start_date": "2024-02-01",
  "care_end_date": "2024-03-01",
  "top_k": 5
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| patient_id | integer | O | 환자 ID |
| patient_personality | object | O | 환자 성격 점수 (0-100) |
| requirements | object | X | 케어 요구사항 |
| preferred_days | array of string | O | 선호 요일 |
| preferred_time_slots | array of string | O | 선호 시간대 |
| care_start_date | date | X | 케어 시작일 (YYYY-MM-DD) |
| care_end_date | date | X | 케어 종료일 (YYYY-MM-DD) |
| top_k | integer | X | 반환할 최대 간병인 수 (1-20, 기본값: 5) |

**requirements 상세**:

| 필드 | 타입 | 설명 |
|------|------|------|
| care_type | string | "time" (시간제) 또는 "live-in" (입주) |
| time_slots | array of string | 시간대 목록 |
| gender | string | 선호 성별 |
| experience | string | 필요 경력 |
| skills | array of string | 필요 기술/자격 |

**응답** (`XGBoostMatchingResponse`):
```json
{
  "patient_id": 1,
  "total_matches": 3,
  "matches": [
    {
      "caregiver_id": 5,
      "caregiver_name": "박간병",
      "job_title": "요양보호사",
      "grade": "A",
      "match_score": 92.5,
      "experience_years": 5,
      "hourly_rate": 15000,
      "avg_rating": 4.8,
      "profile_image_url": "https://...",
      "personality_analysis": "환자의 성격과 매우 잘 맞습니다...",
      "specialties": ["치매케어", "물리치료보조"],
      "availability": ["월", "화", "수", "목", "금"]
    }
  ],
  "algorithm_version": "XGBoost_v3",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| grade | string | 매칭 등급: "A", "B", "C" |
| match_score | float | 매칭 점수 (0-100) |
| personality_analysis | string | AI 생성 성격 분석 |

---

#### 8.2 매칭 서비스 헬스 체크

```
GET /api/matching/health
```

**인증**: 불필요

**응답**:
```json
{
  "status": "healthy",
  "message": "XGBoost matching service is operational",
  "model_status": "loaded",
  "algorithm_version": "XGBoost_v3",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| status | string | "healthy", "warning", "error" |
| model_status | string | "loaded", "unavailable", "failed" |

---

#### 8.3 예측 테스트

```
POST /api/matching/test-prediction
```

**인증**: 불필요

**요청 본문**:
```json
{
  "patient_personality": {
    "empathy_score": 75.0,
    "activity_score": 60.0,
    "patience_score": 80.0,
    "independence_score": 45.0
  },
  "caregiver_personality": {
    "empathy_score": 80.0,
    "activity_score": 70.0,
    "patience_score": 85.0,
    "independence_score": 50.0
  }
}
```

**응답**:
```json
{
  "patient_personality": { ... },
  "caregiver_personality": { ... },
  "compatibility_score": 88.5,
  "grade": "A",
  "analysis": "두 성격이 매우 호환됩니다...",
  "features": {
    "empathy_diff": 5.0,
    "activity_diff": 10.0,
    "patience_diff": 5.0,
    "independence_diff": 5.0
  }
}
```

---

### 9. 케어 실행 (Care Execution)

**파일 위치**: `backend/app/routes/care_execution.py`

#### 9.1 스케줄 (Schedules)

##### 스케줄 목록 조회
```
GET /api/care/schedules
```

**응답**: `ScheduleResponse[]`

---

##### 특정 스케줄 조회
```
GET /api/care/schedules/{schedule_id}
```

**응답**: `ScheduleResponse`

---

##### 스케줄 생성
```
POST /api/care/schedules
```

**요청**: `ScheduleCreate`

**응답**: `ScheduleResponse` (201 Created)

---

##### 스케줄 수정
```
PUT /api/care/schedules/{schedule_id}
```

**요청**: `ScheduleUpdate`

**응답**: `ScheduleResponse`

---

##### 스케줄 삭제
```
DELETE /api/care/schedules/{schedule_id}
```

**응답**: 204 No Content

---

#### 9.2 케어 로그 (Care Logs)

##### 케어 로그 목록 조회
```
GET /api/care/care_logs
```

**응답**: `CareLogResponse[]`

---

##### 특정 케어 로그 조회
```
GET /api/care/care_logs/{log_id}
```

**응답**: `CareLogResponse`

---

##### 케어 로그 생성
```
POST /api/care/care_logs
```

**요청**: `CareLogCreate`

**응답**: `CareLogResponse` (201 Created)

---

##### 케어 로그 수정
```
PUT /api/care/care_logs/{log_id}
```

**요청**: `CareLogUpdate`

**응답**: `CareLogResponse`

---

##### 케어 로그 삭제
```
DELETE /api/care/care_logs/{log_id}
```

**응답**: 204 No Content

---

#### 9.3 식단 계획 (Meal Plans)

##### 식단 계획 목록 조회
```
GET /api/care/meal_plans
```

**응답**: `MealPlanResponse[]`

---

##### 특정 식단 계획 조회
```
GET /api/care/meal_plans/{plan_id}
```

**응답**: `MealPlanResponse`

---

##### 식단 계획 생성
```
POST /api/care/meal_plans
```

**요청**: `MealPlanCreate`

**응답**: `MealPlanResponse` (201 Created)

---

##### 식단 계획 수정
```
PUT /api/care/meal_plans/{plan_id}
```

**요청**: `MealPlanUpdate`

**응답**: `MealPlanResponse`

---

##### 식단 계획 삭제
```
DELETE /api/care/meal_plans/{plan_id}
```

**응답**: 204 No Content

---

#### 9.4 케어 리포트 (Care Reports)

##### 케어 리포트 목록 조회
```
GET /api/care/care_reports
```

**응답**: `CareReportResponse[]`

---

##### 특정 케어 리포트 조회
```
GET /api/care/care_reports/{report_id}
```

**응답**: `CareReportResponse`

---

##### 케어 리포트 생성
```
POST /api/care/care_reports
```

**요청**: `CareReportCreate`

**응답**: `CareReportResponse` (201 Created)

---

##### 케어 리포트 수정
```
PUT /api/care/care_reports/{report_id}
```

**요청**: `CareReportUpdate`

**응답**: `CareReportResponse`

---

##### 케어 리포트 삭제
```
DELETE /api/care/care_reports/{report_id}
```

**응답**: 204 No Content

---

### 10. 리뷰 (Reviews)

**파일 위치**: `backend/app/routes/review.py`

#### 10.1 리뷰 목록 조회

```
GET /api/reviews
```

**인증**: 불필요

**쿼리 파라미터**:

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| skip | integer | 0 | 건너뛸 항목 수 |
| limit | integer | 100 | 최대 조회 수 |

**응답** (`ReviewResponse[]`):
```json
[
  {
    "review_id": 1,
    "matching_id": 5,
    "reviewer_id": 1,
    "reviewer_type": "guardian",
    "rating": 5,
    "comment": "매우 친절하고 전문적입니다.",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

#### 10.2 특정 리뷰 조회

```
GET /api/reviews/{review_id}
```

**인증**: 불필요

**응답**: `ReviewResponse`

---

#### 10.3 리뷰 작성

```
POST /api/reviews
```

**인증**: 필수 (JWT Bearer Token)

**요청 본문** (`ReviewCreate`):
```json
{
  "matching_id": 5,
  "rating": 5,
  "comment": "매우 친절하고 전문적입니다."
}
```

| 필드 | 타입 | 필수 | 유효성 검사 | 설명 |
|------|------|------|-------------|------|
| matching_id | integer | O | - | 매칭 ID |
| rating | integer | O | 1-5 | 평점 |
| comment | string | X | - | 리뷰 내용 |

**응답**: `ReviewResponse` (201 Created)

---

#### 10.4 리뷰 수정

```
PUT /api/reviews/{review_id}
```

**인증**: 필수 (JWT Bearer Token, 본인 리뷰만)

**요청 본문** (`ReviewUpdate`):
```json
{
  "rating": 4,
  "comment": "수정된 리뷰 내용"
}
```

**응답**: `ReviewResponse`

---

#### 10.5 리뷰 삭제

```
DELETE /api/reviews/{review_id}
```

**인증**: 필수 (JWT Bearer Token, 본인 리뷰만)

**응답**: 204 No Content

---

### 11. 성격 테스트 (Personality)

**파일 위치**: `backend/app/routes/personality.py`

#### 11.1 성격 테스트 제출

```
POST /api/personality/tests
```

**인증**: 필수 (JWT Bearer Token)

**요청 본문** (`PersonalityTestRequest`):
```json
{
  "user_type": "guardian",
  "answers": {
    "q1": { "empathy": 4, "activity": 3, "patience": 5, "independence": 2 },
    "q2": { "empathy": 5, "activity": 4, "patience": 4, "independence": 3 },
    "q3": { "empathy": 3, "activity": 5, "patience": 3, "independence": 4 },
    "q4": { "empathy": 4, "activity": 2, "patience": 5, "independence": 3 },
    "q5": { "empathy": 5, "activity": 3, "patience": 4, "independence": 2 },
    "q6": { "empathy": 4, "activity": 4, "patience": 5, "independence": 3 },
    "q7": { "empathy": 3, "activity": 5, "patience": 3, "independence": 5 },
    "q8": { "empathy": 5, "activity": 3, "patience": 4, "independence": 2 },
    "q9": { "empathy": 4, "activity": 4, "patience": 5, "independence": 3 },
    "q10": { "empathy": 5, "activity": 2, "patience": 4, "independence": 4 },
    "q11": { "empathy": 4, "activity": 3, "patience": 5, "independence": 2 },
    "q12": { "empathy": 5, "activity": 4, "patience": 4, "independence": 3 }
  }
}
```

| 필드 | 타입 | 필수 | 유효성 검사 | 설명 |
|------|------|------|-------------|------|
| user_type | string | O | `guardian\|caregiver` | 사용자 유형 |
| answers | object | O | q1-q12 | 12개 질문 응답 |

**응답 (guardian인 경우)** (`PatientPersonalityResponse`):
```json
{
  "personality_id": 1,
  "patient_id": 1,
  "empathy_score": 75.0,
  "activity_score": 60.0,
  "patience_score": 80.0,
  "independence_score": 45.0,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**응답 (caregiver인 경우)** (`CaregiverPersonalityResponse`):
```json
{
  "personality_id": 1,
  "caregiver_id": 1,
  "empathy_score": 80.0,
  "activity_score": 70.0,
  "patience_score": 85.0,
  "independence_score": 50.0,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 12. 케어 플랜 생성 (Care Plans)

**파일 위치**: `backend/app/routes/care_plans.py`

#### 12.1 AI 케어 플랜 생성

```
POST /api/care-plans/generate
```

**인증**: 불필요

**요청 본문** (`CarePlanGenerationRequest`):
```json
{
  "patient_id": 1,
  "caregiver_id": 5,
  "patient_personality": {
    "empathy_score": 75.0,
    "activity_score": 60.0,
    "patience_score": 80.0,
    "independence_score": 45.0
  },
  "care_requirements": {
    "care_type": "time",
    "time_slots": ["09:00-12:00", "14:00-18:00"],
    "gender": "female",
    "skills": ["치매케어", "물리치료보조"]
  }
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| patient_id | integer | O | 환자 ID |
| caregiver_id | integer | O | 간병인 ID |
| patient_personality | object | O | 환자 성격 점수 |
| care_requirements | object | O | 케어 요구사항 |

**응답**:
```json
{
  "success": true,
  "data": {
    "care_plan": "생성된 케어 플랜 내용...",
    "daily_schedule": [...],
    "recommendations": [...]
  },
  "message": "케어 플랜이 성공적으로 생성되었습니다."
}
```

---

### 13. 헬스 체크

#### 13.1 루트 엔드포인트

```
GET /
```

**응답**:
```json
{
  "message": "BluedonuLab API"
}
```

---

#### 13.2 헬스 체크

```
GET /health
```

**응답**:
```json
{
  "status": "healthy"
}
```

---

## 스키마 정의

### 핵심 엔티티 스키마

#### User 스키마

| 스키마명 | 용도 |
|----------|------|
| UserBase | 기본 사용자 필드 |
| UserCreate | 사용자 생성 요청 |
| UserUpdate | 사용자 수정 요청 |
| UserResponse | 사용자 응답 |

#### Guardian 스키마

| 스키마명 | 용도 |
|----------|------|
| GuardianBase | 기본 보호자 필드 |
| GuardianCreate | 보호자 생성 요청 |
| GuardianUpdate | 보호자 수정 요청 |
| GuardianResponse | 보호자 응답 |
| GuardianCreateRequest | 프론트엔드 API용 생성 요청 |
| GuardianInfoResponse | 프론트엔드 API용 응답 |

#### Patient 스키마

| 스키마명 | 용도 |
|----------|------|
| PatientBase | 기본 환자 필드 |
| PatientCreate | 환자 생성 요청 |
| PatientUpdate | 환자 수정 요청 |
| PatientResponse | 환자 응답 |
| PatientCreateRequest | 프론트엔드 API용 생성 요청 |
| PatientInfoResponse | 프론트엔드 API용 응답 |
| PatientDetailResponse | 건강 정보 포함 상세 응답 |
| HealthStatusUpdateRequest | 건강 상태 수정 요청 |
| MedicationsCreateRequest | 약물 등록 요청 |
| MedicationInfoResponse | 약물 정보 응답 |

#### Caregiver 스키마

| 스키마명 | 용도 |
|----------|------|
| CaregiverBase | 기본 간병인 필드 |
| CaregiverCreate | 간병인 생성 요청 |
| CaregiverUpdate | 간병인 수정 요청 |
| CaregiverResponse | 간병인 응답 |
| CaregiverDetailResponse | 성격/가용성 포함 상세 응답 |

#### Matching 스키마

| 스키마명 | 용도 |
|----------|------|
| CaregiverAvailabilityBase | 기본 가용성 필드 |
| CaregiverAvailabilityCreate | 가용성 생성 요청 |
| CaregiverAvailabilityUpdate | 가용성 수정 요청 |
| CaregiverAvailabilityResponse | 가용성 응답 |
| MatchingRequestBase | 기본 매칭 요청 필드 |
| MatchingRequestCreate | 매칭 요청 생성 |
| MatchingRequestUpdate | 매칭 요청 수정 |
| MatchingRequestResponse | 매칭 요청 응답 |
| MatchingResultBase | 기본 매칭 결과 필드 |
| MatchingResultCreate | 매칭 결과 생성 |
| MatchingResultUpdate | 매칭 결과 수정 |
| MatchingResultResponse | 매칭 결과 응답 |
| MatchingResultDetailResponse | 상세 매칭 결과 응답 |

#### Personality 스키마

| 스키마명 | 용도 |
|----------|------|
| PersonalityScoreBase | 기본 성격 점수 필드 |
| PersonalityTestRequest | 성격 테스트 요청 |
| PatientPersonalityCreate | 환자 성격 생성 |
| PatientPersonalityUpdate | 환자 성격 수정 |
| PatientPersonalityResponse | 환자 성격 응답 |
| CaregiverPersonalityCreate | 간병인 성격 생성 |
| CaregiverPersonalityUpdate | 간병인 성격 수정 |
| CaregiverPersonalityResponse | 간병인 성격 응답 |

#### Care Execution 스키마

| 스키마명 | 용도 |
|----------|------|
| ScheduleBase/Create/Update/Response | 스케줄 관련 |
| ScheduleDetailResponse | 스케줄 상세 |
| CareLogBase/Create/Update/Response | 케어 로그 관련 |
| MealPlanBase/Create/Update/Response | 식단 계획 관련 |
| CareReportBase/Create/Update/Response | 케어 리포트 관련 |

#### Review 스키마

| 스키마명 | 용도 |
|----------|------|
| ReviewBase | 기본 리뷰 필드 |
| ReviewCreate | 리뷰 생성 요청 |
| ReviewUpdate | 리뷰 수정 요청 |
| ReviewResponse | 리뷰 응답 |

#### Health Information 스키마

| 스키마명 | 용도 |
|----------|------|
| HealthConditionBase/Create/Update/Response | 건강 상태 관련 |
| MedicationBase/Create/Update/Response | 약물 관련 |
| DietaryPreferenceBase/Create/Update/Response | 식이 선호도 관련 |

#### Dashboard 스키마

| 스키마명 | 용도 |
|----------|------|
| DashboardUserInfo | 대시보드 사용자 정보 |
| DashboardGuardianInfo | 대시보드 보호자 정보 |
| DashboardPatientInfo | 대시보드 환자 정보 |
| DashboardActiveMatching | 대시보드 활성 매칭 정보 |
| DashboardResponse | 대시보드 전체 응답 |

#### OCR 스키마

| 스키마명 | 용도 |
|----------|------|
| MedicineDetailResponse | 의약품 상세 정보 |
| OCRResultResponse | OCR 결과 응답 |

#### XGBoost Matching 스키마

| 스키마명 | 용도 |
|----------|------|
| PersonalityScores | 성격 점수 객체 |
| MatchingRequirements | 매칭 요구사항 |
| XGBoostMatchingRequest | XGBoost 매칭 요청 |
| CaregiverMatchResult | 간병인 매칭 결과 |
| XGBoostMatchingResponse | XGBoost 매칭 응답 |

---

## 외부 연동

### 1. Kakao OAuth

카카오 소셜 로그인을 통한 사용자 인증

- **인증 URL**: `https://kauth.kakao.com/oauth/authorize`
- **토큰 URL**: `https://kauth.kakao.com/oauth/token`
- **사용자 정보 URL**: `https://kapi.kakao.com/v2/user/me`

### 2. Azure OpenAI

AI 기반 성격 분석 및 케어 플랜 생성

- 성격 테스트 결과 분석
- 맞춤형 케어 플랜 생성
- 매칭 호환성 분석 텍스트 생성

### 3. Azure Document Intelligence

약물 이미지 OCR 처리

- 약병/처방전 이미지에서 텍스트 추출
- 의약품명 인식

### 4. 식약처 (MFDS) API

의약품 정보 검증 및 조회

- 의약품명으로 상세 정보 검색
- 효능, 용법, 주의사항 등 조회

---

## 엔드포인트 요약

| 카테고리 | 엔드포인트 수 | 기본 경로 |
|----------|--------------|-----------|
| 인증 | 4 | `/auth` |
| 보호자 | 2 | `/api/guardians` |
| 환자 | 7 | `/api/patients` |
| OCR/의약품 | 2 | `/api/patients/*/medications/ocr`, `/api/medicines` |
| 대시보드 | 1 | `/api/users/me/dashboard` |
| 프로필 관리 | 15 | `/api/profiles` |
| 매칭 | 16 | `/api/matching` |
| XGBoost 매칭 | 3 | `/api/matching` |
| 케어 실행 | 20 | `/api/care` |
| 리뷰 | 5 | `/api/reviews` |
| 성격 테스트 | 1 | `/api/personality` |
| 케어 플랜 | 1 | `/api/care-plans` |
| 헬스 체크 | 2 | `/`, `/health` |
| **총계** | **79** | - |
