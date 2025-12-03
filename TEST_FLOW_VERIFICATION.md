# AI 케어 플랜 생성 통합 테스트 검증 계획

**작성일**: 2025-12-03
**상태**: 📋 구현 완료, 테스트 준비 단계

---

## ✅ 구현 완료 확인

### 1. 백엔드 구현 (Phase 1-2)
**파일**: `backend/app/routes/care_plans.py`

✅ **AI 생성 결과 DB 저장**
- Line 128-197: DB 저장 로직 완전 구현
- 오늘부터 7일간의 `Schedule` 생성
- 각 활동별 `CareLog` 생성
- 활동명 기반 자동 카테고리 분류
- 트랜잭션 처리 및 롤백 로직

**저장되는 데이터:**
```
Schedule (일정 단위)
├─ patient_id: 환자 ID
├─ care_date: 일자
├─ is_ai_generated: true (AI 생성 표시)
└─ status: "scheduled"

CareLog (활동 단위) - Schedule과 1:N 관계
├─ task_name: 활동명
├─ category: medication|meal|exercise|vital_check|hygiene|other
├─ scheduled_time: HH:MM 형식
├─ is_completed: false (초기값)
└─ note: 특수 사항
```

---

### 2. 프론트엔드 구현 (Phase 2 & 3)
**파일**: `frontend/my-app/src/app/care-plans-create-1/page.tsx`

✅ **Patient Personality 개인화** (Phase 2)
- Line 48-73: sessionStorage에서 성향 점수 읽기
- 폴백 로직: 데이터 없으면 기본값 사용
- 콘솔 로그: 사용 중인 점수 추적

**사용되는 성향 점수:**
```
empathy_score: sessionStorage 또는 기본값 75
activity_score: sessionStorage 또는 기본값 55
patience_score: sessionStorage 또는 기본값 80
independence_score: sessionStorage 또는 기본값 45
```

✅ **AI 생성 완료 대기** (Phase 3)
- Line 102-113: async/await로 완료 대기
- 0.5초 후 `generatePlan()` 호출
- API 응답 완료 후 다음 페이지로 이동
- 에러 발생 시에도 진행 (폴백)

---

### 3. 프론트엔드 표시 (care-plans-create-2)
**파일**: `frontend/my-app/src/app/care-plans-create-2/page.tsx`

✅ **데이터 조회 및 표시**
- Line 37-61: `fetchCarePlans()` - GET `/api/patients/{patient_id}/care-plans?type=weekly`
- Line 92-103: `getActivities()` - DB에서 조회한 스케줄을 활동으로 변환
- schedules가 비어있으면 기본 더미 데이터 표시

**데이터 매핑:**
```
Backend Schedule → Frontend Schedule 타입
├─ log_id → schedule_id
├─ task_name → title
├─ scheduled_time (HH:MM) → start_time
├─ category → category
└─ is_completed → is_completed
```

---

## 🔄 데이터 흐름 전체

```
[personality-test 페이지]
         ↓
    sessionStorage 저장
    personality_scores = {
      empathy_score: 75,
      activity_score: 55,
      patience_score: 80,
      independence_score: 45
    }
         ↓
[caregiver-finder 페이지]
         ↓
    간병인 선택
    sessionStorage 저장
    selectedCaregiver = {...}
         ↓
[care-plans-create-1 페이지] ← 우리 구현 시작!
         ↓
    1. sessionStorage에서 성향 점수 읽기 ✅
    2. API: POST /api/care-plans/generate
       {
         patient_id: from sessionStorage
         caregiver_id: from selectedCaregiver
         patient_personality: from sessionStorage (개인화) ✅
         care_requirements: from sessionStorage
       }
         ↓
[백엔드 care_plan_generation_service]
         ↓
    Azure OpenAI로 AI 플랜 생성
    - 환자 정보 (이름, 나이, 건강 상태)
    - 간병인 정보 (이름, 경력, 전문성)
    - 성향 점수 (개인화된 프롬프트)
    - 돌봄 요구사항
         ↓
    AI 응답 예시:
    {
      weekly_schedule: [
        {
          day: "월요일",
          activities: [
            {
              time: "07:00",
              title: "기상 도움",
              category: "hygiene",
              note: ""
            },
            ...
          ]
        },
        ...
      ],
      caregiver_feedback: {...}
    }
         ↓
[DB 저장 로직] ✅ 신규 구현!
         ↓
    for each day in weekly_schedule:
      ├─ Schedule 생성
      │  ├─ patient_id
      │  ├─ care_date (오늘 + N일)
      │  ├─ is_ai_generated = true
      │  └─ status = "scheduled"
      │
      └─ for each activity:
         ├─ CareLog 생성
         │  ├─ schedule_id (위의 Schedule)
         │  ├─ task_name (활동명)
         │  ├─ category (자동 분류)
         │  ├─ scheduled_time (HH:MM)
         │  └─ is_completed = false
         │
         └─ db.commit()

         DB 저장 성공! ✅

         AI 응답 반환
         {
           success: true,
           data: care_plan (AI 생성 내용),
           message: "케어 플랜이 생성되었습니다."
         }
         ↓
[프론트엔드 care-plans-create-1]
         ↓
    API 응답 받음
    3초 프로그래스 바 진행
    프론트엔드로 이동
         ↓
[care-plans-create-2 페이지] ← DB에서 조회!
         ↓
    1. API: GET /api/patients/{patient_id}/care-plans?type=weekly
    2. 백엔드 조회 로직:
       - Schedule 조회 (오늘부터 7일)
       - 각 Schedule의 care_logs 조회
       - CareLog를 Schedule 타입으로 변환
         └─ log_id → schedule_id
         └─ task_name → title
         └─ scheduled_time → start_time
         └─ category → category
         └─ is_completed → is_completed
    3. 결과: schedules 배열
       [
         {
           schedule_id: 1,
           title: "기상 도움",
           start_time: "07:00",
           category: "hygiene",
           is_completed: false
         },
         ...
       ]
         ↓
    4. 프론트엔드에서 활동으로 변환
       activities = schedules.map(schedule => ({
         time: schedule.start_time.slice(0, 5),
         title: schedule.title,
         assignee: `👨‍⚕️ ${schedule.category}`,
         note: schedule.is_completed ? '✅ 완료' : undefined
       }))
         ↓
    5. UI에 표시
       ✅ AI가 생성한 스케줄 표시됨!
```

---

## 📋 테스트 시나리오

### 시나리오 1: 성공 케이스 (모든 구현이 정상 작동)

**전제 조건:**
- 환자 ID: 1 (sessionStorage)
- 간병인 ID: 1 (selectedCaregiver)
- 성향 점수: sessionStorage에 저장됨

**테스트 단계:**
1. [ ] care-plans-create-1 페이지 진입
2. [ ] 콘솔 확인: "[성향 점수] sessionStorage에서 로드됨:"
3. [ ] 콘솔 확인: "AI 케어 플랜 생성 시작..."
4. [ ] 백엔드 로그: "[케어 플랜 생성] 환자 1, 간병인 1"
5. [ ] 백엔드 로그: "[케어 플랜 저장 시작] DB에 스케줄 및 케어 로그 저장 중..."
6. [ ] 백엔드 로그: "[케어 플랜 저장 완료] 총 7개 일정 저장됨"
7. [ ] 프롱엔드 콘솔: "✅ 케어 플랜 생성 및 저장 완료"
8. [ ] care-plans-create-2 페이지로 자동 이동
9. [ ] 백엔드 로그: "🔍 [DEBUG] 케어 플랜 조회 요청: patient_id=1, type=weekly"
10. [ ] 백엔드 로그: "✅ [DEBUG] 조회된 활동 수: 7+" (7일 이상)
11. [ ] care-plans-create-2에 스케줄 표시됨 (기본 더미 데이터가 아닌 AI 생성 데이터)

**확인 항목:**
- [ ] DB에 Schedules 테이블에 7개 row 생성됨
- [ ] DB에 CareLogs 테이블에 50개+ row 생성됨 (일당 활동 수만큼)
- [ ] CareLog의 scheduled_time이 올바르게 저장됨
- [ ] CareLog의 category가 올바르게 분류됨

---

### 시나리오 2: 성향 점수 없음 (폴백)

**전제 조건:**
- sessionStorage에 personality_scores가 없음

**기대 결과:**
- [ ] 콘솔: "[성향 점수] sessionStorage에 데이터 없음, 기본값 사용"
- [ ] AI에 기본값으로 요청됨
- [ ] 정상 작동 (기본값 성향의 플랜 생성)

---

### 시나리오 3: DB 저장 실패 (에러 처리)

**시뮬레이션:**
- DB 연결 끊김 또는 제약 조건 위반

**기대 결과:**
- [ ] 콘솔: "❌ 케어 플랜 DB 저장 실패: {에러}"
- [ ] 콘솔: "경고: DB 저장에 실패했으나 AI 생성 결과는 반환합니다"
- [ ] 프론트엔드는 여전히 AI 응답 데이터 받음 (응답 반환)
- [ ] care-plans-create-2로 이동 (기본 더미 데이터 표시)

---

### 시나리오 4: API 호출 실패

**시뮬레이션:**
- `/api/care-plans/generate` 실패

**기대 결과:**
- [ ] 콘솔: "❌ 케어 플랜 생성 실패: {에러}"
- [ ] care-plans-create-2로 여전히 이동 (폴백 동작)
- [ ] 기본 더미 데이터 표시

---

## 🔧 매칭 확인사항

### 백엔드 응답 ↔ 프론트엔드 타입

**Issue 발견:**
프론트엔드 Schedule 타입:
```typescript
export interface Schedule {
  schedule_id: number;
  title: string;
  start_time: string;        // ⚠️ "HH:MM" 형식
  end_time: string;          // ⚠️ 백엔드에서 응답하지 않음
  category: string;
  is_completed: boolean;
}
```

백엔드 응답:
```python
{
    "schedule_id": log.log_id,
    "title": log.task_name,
    "start_time": log.scheduled_time.strftime("%H:%M"),  # ✓ 매칭됨
    # "end_time" 없음
    "category": log.category.value,
    "is_completed": log.is_completed,
    # "note" 추가됨 (타입 정의 없음)
}
```

**해결 방안:**
- 타입 정의에서 `end_time` 제거하거나 선택사항 처리
- `note` 필드 추가 (프론트엔드에서 사용)

---

## 📊 테스트 결과 기록

### 테스트 환경
- 프론트엔드: localhost:3000
- 백엔드: localhost:8000
- 데이터베이스: PostgreSQL

### 테스트 실행 체크리스트

- [ ] 시나리오 1 테스트 통과
- [ ] 시나리오 2 테스트 통과
- [ ] 시나리오 3 테스트 통과
- [ ] 시나리오 4 테스트 통과
- [ ] 브라우저 콘솔 에러 없음
- [ ] 백엔드 로그 확인됨
- [ ] DB에 데이터 저장 확인됨

---

## 🚀 다음 단계

1. **로컬 테스트 실행** (위 시나리오들 따라 수동 테스트)
2. **프론트엔드 타입 정의 수정** (end_time 처리)
3. **자동화 테스트 작성** (선택사항)
4. **git push** (테스트 통과 후)
5. **배포** (통합 환경에서 최종 검증)

---

**상태**: 🟡 구현 완료, 로컬 테스트 대기

다음: 실제 브라우저에서 통합 테스트 실행
