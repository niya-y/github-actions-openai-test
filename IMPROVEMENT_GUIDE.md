# 📖 늘봄케어 앱 개선 가이드

프로젝트에서 발견된 에러와 버그를 단계적으로 해결하기 위한 완전한 가이드입니다.

---

## 🚀 빠른 시작

### 1️⃣ 현재 상황 파악
- **분석 보고서**: [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md)
- 발견된 문제: 56개 (높음 10개, 중간 12개, 낮음 34개)
- 가장 심각한 문제: 에러 처리 부재, 데이터 손실, 부분 실패 처리

### 2️⃣ 개선 계획
- **개선 테스크**: [IMPROVEMENT_TASKS.md](IMPROVEMENT_TASKS.md)
- 3 Phase로 나뉨 (각 1주씩)
- 총 소요 시간: 3주

### 3️⃣ 진행 상황 추적
- 각 Task의 완료 여부를 체크박스로 표시
- PR 체크리스트 확인 후 merge
- 프로덕션 배포 전 테스트

---

## 🎯 주요 문제와 해결책

### 문제 1: API 에러 처리 부재

**증상**: 네트워크 오류 시 앱이 먹통

**빠른 해결** (30분)
```javascript
// ❌ 현재 (api.ts)
export async function apiPut<T>(url: string, body: any): Promise<T> {
    const response = await fetch(`${BASE_URL}${url}`, {...});
    return response.json();  // try-catch 없음
}

// ✅ 개선
export async function apiPut<T>(url: string, body: any): Promise<T> {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch(`${BASE_URL}${url}`, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('요청 타임아웃');
        }
        throw error;
    }
}
```

**관련 Task**: Task 1.1

---

### 문제 2: sessionStorage 데이터 손실

**증상**: 페이지 새로고침 후 데이터 초기화

**빠른 해결** (1시간)
```typescript
// ❌ 현재
useEffect(() => {
    const data = sessionStorage.getItem('matching_results')
    if (data) {
        setMatches(JSON.parse(data))
    }
}, [])

// ✅ 개선
useEffect(() => {
    const fetchData = async () => {
        try {
            // 1. API 호출 우선
            const response = await apiGet('/api/matching/results')
            if (response?.matches) {
                setMatches(response.matches)
                sessionStorage.setItem('matching_results', JSON.stringify(response))
                return
            }
        } catch (err) {
            // 2. API 실패 시 sessionStorage 폴백
            const cached = sessionStorage.getItem('matching_results')
            if (cached) {
                setMatches(JSON.parse(cached))
                return
            }
        }

        // 3. 모두 실패 시 에러
        setError(new Error('데이터를 불러올 수 없습니다'))
    }

    fetchData()
}, [])
```

**관련 Task**: Task 1.3.2, Task 2.2

---

### 문제 3: 부분 실패 처리 부재

**증상**: 케어 플랜이 불완전하게 생성됨

**빠른 해결** (1시간)
```python
# ❌ 현재 (care_plans.py)
for activity in activities:
    try:
        care_log = CareLog(...)
        db.add(care_log)
    except Exception as e:
        logger.warning(f"실패: {e}")
        continue  # 실패해도 계속

db.commit()  # 부분 커밋

# ✅ 개선
failed_logs = []
for activity in activities:
    try:
        care_log = CareLog(...)
        db.add(care_log)
    except Exception as e:
        failed_logs.append({"activity": activity.title, "error": str(e)})

if failed_logs:
    db.rollback()
    raise HTTPException(status_code=500, detail={
        "message": "케어 플랜 생성 실패",
        "failed_activities": failed_logs
    })

db.commit()  # 전체 커밋
```

**관련 Task**: Task 1.2.2

---

## 📅 Phase별 진행 가이드

### Phase 1: 핵심 안정성 (1주)

**우선순위**: 🔴 **긴급**

**목표**: API 에러 처리, 기본 데이터 검증으로 안정성 50% 향상

**진행 순서**:
1. **Task 1.1** (2일): API 유틸리티 강화
   - [ ] apiPut, apiDelete에 try-catch 추가
   - [ ] 타임아웃 처리
   - [ ] 테스트 완료

2. **Task 1.2** (2일): Backend 안정성
   - [ ] patient null 체크
   - [ ] CareLog 실패 시 롤백
   - [ ] 커밋 전 트랜잭션 래핑

3. **Task 1.3** (2일): Frontend 3개 페이지 수정
   - [ ] care-plans-create-4: API 성공 확인
   - [ ] caregiver-result-list: API 폴백
   - [ ] care-plans-create-2: 응답 검증

4. **Task 1.4** (1일): AI 서비스 기본 수정
   - [ ] JSON 파싱 에러 처리
   - [ ] 폴백 데이터 개선 (7일 스케줄)

5. **Task 1.5** (1일): 테스트 및 배포
   - [ ] 통합 테스트
   - [ ] 수동 테스트
   - [ ] 프로덕션 배포

**배포 일정**: 1주차 말 (금요일)

---

### Phase 2: 데이터 무결성 (2주)

**우선순위**: 🟡 **중요**

**목표**: 타입 시스템, 전역 상태 관리로 데이터 무결성 80% 향상

**진행 순서**:
1. **Task 2.1** (2일): API 응답 타입 정의
   - [ ] 타입 정의 파일 작성
   - [ ] 타입 가드 함수
   - [ ] 기존 페이지에 적용

2. **Task 2.2** (3일): React Context 전역 상태 관리
   - [ ] AppContext 작성
   - [ ] 모든 페이지 적용
   - [ ] sessionStorage → Context로 전환

3. **Task 2.3** (2일): Backend 상태 검증
   - [ ] ScheduleStatus Enum
   - [ ] 상태 전환 검증
   - [ ] API 응답 표준화

4. **Task 2.4, 2.5** (1일): Azure OpenAI, XGBoost
   - [ ] Azure OpenAI 타임아웃
   - [ ] XGBoost 모델 경로 환경 변수화

**배포 일정**: 2주차 말 (금요일)

---

### Phase 3: 운영 안정성 (3주)

**우선순위**: 🟢 **개선**

**목표**: 성능, 모니터링으로 운영 안정성 강화

**진행 순서**:
1. **Task 3.1** (2일): 재시도 로직
2. **Task 3.2** (1일): 캐싱
3. **Task 3.3** (2일): 로깅 및 모니터링
4. **Task 3.4** (1일): 성능 최적화
5. **Task 3.5** (1일): 문서화

**배포 일정**: 3주차 말 (금요일)

---

## 📊 문제별 심각도 및 영향도

### 🔴 높음 (즉시 해결 필수)

| # | 문제 | 파일 | 영향 | Task |
|---|------|------|------|------|
| 1 | API 에러 처리 부재 | api.ts | 90% 사용자 | 1.1 |
| 2 | sessionStorage 의존 | 페이지 전체 | 80% 사용자 | 1.3.2 |
| 3 | 부분 실패 처리 | care_plans.py | 데이터 손실 | 1.2.2 |
| 4 | patient null 체크 부재 | care_plans.py | 500 에러 | 1.2.1 |
| 5 | 부분 커밋 위험 | care_plans.py | 데이터 불일치 | 1.2.3 |

### 🟡 중간 (1-2주 내 해결)

| # | 문제 | 파일 | 영향 | Task |
|---|------|------|------|------|
| 6 | JSON 파싱 실패 | care_plan_generation_service.py | AI 기능 | 1.4.1 |
| 7 | 폴백 데이터 부족 | care_plan_generation_service.py | 데이터 손실 | 1.4.2 |
| 8 | 타입 검증 부재 | 페이지 전체 | 타입 에러 | 2.1 |
| 9 | 상태 전환 검증 없음 | care_plans.py | 데이터 무결성 | 2.3 |
| 10 | XGBoost 경로 하드코딩 | xgboost_service.py | 배포 불가 | 2.5 |

---

## 🛠️ 개발자 체크리스트

### 코드 작성 전
- [ ] 관련 분석 보고서 읽음
- [ ] Task 상세 요구사항 이해
- [ ] 기존 코드 검토

### 코드 작성 중
- [ ] 에러 처리 추가 (try-catch)
- [ ] 타입 정의 포함
- [ ] 로깅 추가
- [ ] 주석 작성

### 코드 작성 후
- [ ] 단위 테스트 작성 (50% 이상 coverage)
- [ ] 통합 테스트 실행
- [ ] 수동 테스트 완료
- [ ] PR 생성 및 리뷰 요청

### PR 체크리스트
- [ ] 코드 리뷰 2명 이상
- [ ] CI/CD 통과
- [ ] 테스트 커버리지 >= 50%
- [ ] 문서 업데이트

### 배포 전
- [ ] 스테이징 환경 테스트
- [ ] 성능 측정
- [ ] 보안 검토
- [ ] 롤백 계획 수립

---

## 📝 문서 구조

```
프로젝트 루트/
├── ANALYSIS_REPORT.md          # 상세 분석 보고서
├── IMPROVEMENT_TASKS.md        # Task 상세 정의
├── IMPROVEMENT_GUIDE.md        # 이 파일 (개발자 가이드)
├── docs/
│   ├── API.md                  # API 문서화
│   ├── DEVELOPER_GUIDE.md      # 개발자 가이드
│   └── OPERATIONS_GUIDE.md     # 운영 가이드
└── .github/
    └── ISSUE_TEMPLATE/         # 이슈 템플릿
```

---

## 🤔 자주 묻는 질문

### Q1: 모든 Task를 다 해야 하나요?
**A**: Phase 1은 필수입니다. Phase 2, 3은 리소스 상황에 따라 조정 가능합니다.

### Q2: Task 순서를 바꿀 수 있나요?
**A**: Phase 1 내에서는 순서대로 진행하세요. Phase 2, 3은 병렬 진행 가능합니다.

### Q3: 테스트는 얼마나 필요한가요?
**A**: Phase 1은 50% 이상, Phase 2는 70% 이상, Phase 3는 80% 이상을 목표로 합니다.

### Q4: 배포 후 롤백이 필요하면?
**A**: 각 Phase 배포마다 롤백 계획을 준비하세요. Git tag를 사용하여 이전 버전으로 복귀 가능하게 합니다.

### Q5: 기존 기능이 깨질까봐 걱정됩니다.
**A**: 모든 변경사항을 별도 branch에서 테스트하고, CI/CD를 통과한 후만 merge합니다.

---

## 📞 추가 지원

### 문제 발생 시
1. ANALYSIS_REPORT.md에서 유사한 문제 찾기
2. IMPROVEMENT_TASKS.md에서 관련 Task 찾기
3. 팀원에 문의

### 진행 상황 보고
- 주 1회 프로젝트 진행 상황 체크인
- 각 Phase 완료 후 회고(Retrospective) 진행

### 성과 측정
- Phase 1: 에러율 50% 감소 목표
- Phase 2: 데이터 손실 80% 감소 목표
- Phase 3: 성능 30% 향상 목표

---

## 🎉 마무리

이 가이드를 따라 진행하면:
- ✅ 앱의 안정성이 크게 향상됩니다
- ✅ 사용자 경험이 개선됩니다
- ✅ 개발 생산성이 증가합니다
- ✅ 유지보수가 용이해집니다

**화이팅! 🚀**

---

**문서 버전**: 1.0
**마지막 수정**: 2025-12-03
**관련 문서**:
- [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md)
- [IMPROVEMENT_TASKS.md](IMPROVEMENT_TASKS.md)
