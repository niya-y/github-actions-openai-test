# AI 케어 플랜 생성 및 저장 기능 수정 계획

**작성일**: 2025-12-03
**우선순위**: 🔴 높음 (핵심 기능 미동작)
**상태**: 📋 계획 단계

---

## 📊 현재 상황

### ✅ 잘 구현된 부분
- Azure OpenAI (GPT-4o)를 통한 AI 플랜 생성 완벽 구현
- 7일 주간 스케줄 생성 로직 완벽 구현
- 간병인 피드백 생성 로직 완벽 구현
- 프론트엔드 UI/UX 완벽 구현

### ❌ 미구현 부분 (2가지 중대 문제)

#### 🔴 문제 1: AI 생성 결과가 DB에 저장되지 않음

**현재 플로우:**
```
프론트엔드 ─→ /api/care-plans/generate ─→ AI 생성 (메모리) ─→ 응답 반환
                                                            ↓
                                            care-plans-create-2로 이동
                                                            ↓
                                            DB 조회 (데이터 없음) ❌
```

**영향:**
- AI가 생성한 스케줄이 표시되지 않음
- 기본 더미 데이터만 표시됨
- 간병인 피드백도 표시되지 않음

**관련 파일:**
- 백엔드: `backend/app/routes/care_plans.py` (POST /api/care-plans/generate)
- 테이블: `schedules`, `care_logs`

---

#### 🔴 문제 2: Patient Personality가 하드코딩됨

**현재 코드:**
```typescript
// frontend/my-app/src/app/care-plans-create-1/page.tsx:54-59
patient_personality: {
    empathy_score: 75,        // ← 항상 이 값
    activity_score: 55,       // ← 항상 이 값
    patience_score: 80,       // ← 항상 이 값
    independence_score: 45    // ← 항상 이 값
}
```

**문제점:**
- 사용자의 실제 성향 테스트 결과 무시
- DB에 저장된 값 사용 안 함
- sessionStorage의 `personality_scores` 사용 안 함
- 결과: 모든 사용자에게 동일한 플랜 생성

**데이터 위치:**
- sessionStorage: `personality_scores` (성향 테스트 후 저장)
- DB: `patient_personality` 테이블 (저장됨)

---

## 🛠️ 수정 계획

### Phase 1: 백엔드 수정 (AI 생성 결과 저장)

**목표**: `/api/care-plans/generate` 응답 후 DB에 저장

**파일**: `backend/app/routes/care_plans.py`

**수정 사항**:

1. **Schedule 레코드 생성**
   - `weekly_schedule`의 각 day별로 반복
   - 각 activity를 `schedules` 테이블에 INSERT
   - 데이터 매핑:
     ```python
     Schedule(
         patient_id=patient_id,
         caregiver_id=caregiver_id,
         title=activity['title'],
         category=activity['category'] or 'general',
         scheduled_time=activity['time'],  # HH:MM 형식
         notes=activity['note'],
         created_at=datetime.now(),
         updated_at=datetime.now()
     )
     ```

2. **CareLog 레코드 생성**
   - 각 activity에 대한 로그 레코드
   - `care_logs` 테이블에 INSERT
   - 필드:
     ```python
     CareLog(
         patient_id=patient_id,
         caregiver_id=caregiver_id,
         task_name=activity['title'],
         scheduled_time=activity['time'],
         status='pending',  # 또는 'scheduled'
         created_at=datetime.now()
     )
     ```

3. **피드백 저장** (선택사항)
   - `caregiver_feedback` 필드 추가 (JSONB)
   - `care_logs` 또는 새로운 테이블에 저장
   - 구조:
     ```python
     {
         "overall_comment": "...",
         "activity_reviews": [...]
     }
     ```

**예상 코드 (의사코드):**
```python
@router.post("/api/care-plans/generate")
async def generate_care_plan(request: CarePlanGenerationRequest, db: Session):
    # AI 생성 로직 (기존)
    care_plan = await care_plan_generation_service.generate(...)

    # 신규: DB에 저장
    for day_schedule in care_plan['weekly_schedule']:
        for activity in day_schedule['activities']:
            # 1. Schedule 생성
            schedule = Schedule(
                patient_id=request.patient_id,
                caregiver_id=request.caregiver_id,
                title=activity['title'],
                category=activity.get('category', 'general'),
                scheduled_time=activity['time'],
                notes=activity.get('note'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(schedule)

            # 2. CareLog 생성
            care_log = CareLog(
                patient_id=request.patient_id,
                caregiver_id=request.caregiver_id,
                task_name=activity['title'],
                scheduled_time=activity['time'],
                status='pending',
                created_at=datetime.now()
            )
            db.add(care_log)

    # 피드백 저장 (선택)
    feedback_log = CarePlanFeedback(
        patient_id=request.patient_id,
        caregiver_id=request.caregiver_id,
        feedback_data=care_plan['caregiver_feedback'],
        created_at=datetime.now()
    )
    db.add(feedback_log)

    db.commit()

    # 응답 반환 (기존)
    return care_plan
```

**테이블 확인 완료:** ✅

#### schedules 테이블
```python
class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id: BigInteger (PK)
    patient_id: BigInteger (FK → patients) ✓
    matching_id: BigInteger (FK → matching_results) ✓
    care_date: Date ✓
    is_ai_generated: Boolean (default=True) ✓
    status: String (default='scheduled') ✓
    created_at: DateTime ✓
    updated_at: DateTime ✓

    # Relationships
    care_logs: CareLog[] (cascade delete)
```

#### care_logs 테이블
```python
class CareLog(Base):
    __tablename__ = "care_logs"

    log_id: BigInteger (PK)
    schedule_id: BigInteger (FK → schedules) ✓
    category: CareCategoryEnum ✓
    task_name: String(100) ✓
    scheduled_time: Time ✓
    is_completed: Boolean (default=False) ✓
    completed_at: DateTime ✓
    note: Text ✓
    created_at: DateTime ✓
```

**결론:**
- ✅ 테이블 구조 완벽함
- ✅ AI 생성 결과 저장 가능
- ✅ `is_ai_generated` 플래그로 AI 생성 일정 표시 가능
- ❓ `caregiver_feedback` 저장 방식: care_logs의 `note` 필드 사용 또는 별도 필드 추가 필요

---

### Phase 2: 프론트엔드 수정 (Patient Personality 실제 값 사용)

**목표**: 하드코딩된 성향 점수를 실제 테스트 결과로 변경

**파일**: `frontend/my-app/src/app/care-plans-create-1/page.tsx`

**수정 사항**:

**기존 코드:**
```typescript
let careRequirements = { ... }

if (careRequirementsStr) {
  try {
    careRequirements = JSON.parse(careRequirementsStr)
  } catch (e) {
    console.error("케어 요구사항 파싱 오류", e)
  }
}

// ... API 호출
await apiPost('/api/care-plans/generate', {
  patient_id: patientId ? parseInt(patientId) : 1,
  caregiver_id: caregiverId,
  patient_personality: {
    empathy_score: 75,        // ❌ 하드코딩
    activity_score: 55,       // ❌ 하드코딩
    patience_score: 80,       // ❌ 하드코딩
    independence_score: 45    // ❌ 하드코딩
  },
  care_requirements: careRequirements
})
```

**수정된 코드:**
```typescript
let careRequirements = { ... }

if (careRequirementsStr) {
  try {
    careRequirements = JSON.parse(careRequirementsStr)
  } catch (e) {
    console.error("케어 요구사항 파싱 오류", e)
  }
}

// 신규: sessionStorage에서 성향 점수 읽기
let patientPersonality = {
  empathy_score: 75,        // 기본값
  activity_score: 55,       // 기본값
  patience_score: 80,       // 기본값
  independence_score: 45    // 기본값
}

const personalityScoresStr = sessionStorage.getItem('personality_scores')
if (personalityScoresStr) {
  try {
    const personalityScores = JSON.parse(personalityScoresStr)
    patientPersonality = {
      empathy_score: personalityScores.empathy_score || 75,
      activity_score: personalityScores.activity_score || 55,
      patience_score: personalityScores.patience_score || 80,
      independence_score: personalityScores.independence_score || 45
    }
    console.log('성향 점수 사용:', patientPersonality)
  } catch (e) {
    console.error("성향 점수 파싱 오류", e)
  }
}

// ... API 호출
await apiPost('/api/care-plans/generate', {
  patient_id: patientId ? parseInt(patientId) : 1,
  caregiver_id: caregiverId,
  patient_personality: patientPersonality,  // ✅ 실제 값 사용
  care_requirements: careRequirements
})
```

**선택 사항: DB에서 직접 조회**
```typescript
// 더 안전한 방법: DB에서 직접 가져오기
// /api/patients/{patient_id}/personality GET 엔드포인트 추가 필요
try {
  const patientPersonalityData = await apiGet(
    `/api/patients/${patientId}/personality`
  )
  patientPersonality = patientPersonalityData
} catch (err) {
  console.warn('DB에서 성향 점수 조회 실패, sessionStorage 사용:', err)
  // sessionStorage 사용으로 폴백
}
```

---

### Phase 3: 프론트엔드 수정 (AI 생성 완료 대기)

**파일**: `frontend/my-app/src/app/care-plans-create-1/page.tsx`

**현재 문제:**
- 3초 타이머로 자동 이동
- AI 생성 완료 여부 확인 안 함
- 네트워크 느림 시 데이터 미로드

**수정 방법:**

**기존 코드:**
```typescript
const timer = setTimeout(() => {
  generatePlan()
  router.push('/care-plans-create-2')
}, 3000)
```

**수정된 코드:**
```typescript
const timer = setTimeout(async () => {
  try {
    await generatePlan()  // 완료 대기
    console.log("케어 플랜 생성 및 저장 완료")
    router.push('/care-plans-create-2')
  } catch (err) {
    console.error("케어 플랜 생성 실패:", err)
    // 실패해도 진행 (또는 에러 표시)
    router.push('/care-plans-create-2')
  }
}, 500)  // 0.5초 후 시작 (화면 로딩 시간)
```

---

## 📈 구현 순서

1. **Phase 1-1**: 테이블 구조 확인
   - [ ] `schedules` 테이블 스키마 확인
   - [ ] `care_logs` 테이블 스키마 확인
   - [ ] 필요한 필드 추가/수정

2. **Phase 1-2**: 백엔드 `/api/care-plans/generate` 수정
   - [ ] AI 생성 로직 유지
   - [ ] DB 저장 로직 추가
   - [ ] 트랜잭션 처리

3. **Phase 2**: 프론트엔드 성향 점수 수정
   - [ ] sessionStorage에서 읽기 추가
   - [ ] 폴백 로직 추가
   - [ ] 테스트

4. **Phase 3**: 타이밍 이슈 수정
   - [ ] async/await 적용
   - [ ] 에러 처리 개선

5. **테스트**:
   - [ ] 케어 플랜 생성 후 DB 저장 확인
   - [ ] care-plans-create-2에서 데이터 표시 확인
   - [ ] 성향 점수별로 다른 플랜 생성 확인
   - [ ] 네트워크 느린 상황에서도 정상 작동 확인

---

## 🎯 예상 결과

**수정 전:**
```
사용자 → AI 플랜 생성 → DB 미저장 → care-plans-create-2에서 기본 데이터만 표시 ❌
```

**수정 후:**
```
사용자 → AI 플랜 생성 → DB에 저장 ✅ → care-plans-create-2에서 AI 플랜 표시 ✅
     ↓
  성향 점수 (실제 값) ✅ → AI가 개인화된 플랜 생성 ✅
```

---

## 📝 관련 파일 목록

### 백엔드
- `backend/app/routes/care_plans.py` - AI 생성 API
- `backend/app/services/care_plan_generation_service.py` - AI 생성 로직
- `backend/app/models/*.py` - Schedule, CareLog 모델
- `backend/app/database/models.py` - DB 테이블 정의

### 프론트엔드
- `frontend/my-app/src/app/care-plans-create-1/page.tsx` - 로딩 및 AI 생성 요청
- `frontend/my-app/src/app/care-plans-create-2/page.tsx` - 결과 표시
- `frontend/my-app/src/app/personality-test/page.tsx` - 성향 점수 저장
- `frontend/my-app/src/types/api.ts` - 타입 정의

---

## ✅ 체크리스트

- [ ] 현재 테이블 구조 파악
- [ ] Phase 1 백엔드 수정 완료
- [ ] Phase 2 프론트엔드 수정 완료
- [ ] Phase 3 타이밍 수정 완료
- [ ] 로컬 테스트 완료
- [ ] 수정사항 커밋 및 푸시

---

**다음 단계**: Phase 1-1 테이블 구조 확인 시작
