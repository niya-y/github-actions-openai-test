# 🎨 BluedonuLab 프론트엔드 통합 가이드

## 📌 개요

PHASE 6: 프론트엔드 통합의 첫 번째 단계입니다.

✅ **완료된 것**:
- JavaScript API 클라이언트 (`api-client.js`)
- Welcome 페이지 API 통합
- API 테스트 페이지

📋 **준비 중**:
- 다른 UI 페이지 통합
- React 변환 (선택사항)

---

## 🚀 빠른 시작

### 1단계: FastAPI 서버 실행

```bash
# 터미널 1에서 실행
cd /Users/sangwon/Project/Sesac_class/bluedonulab-01/match

# 옵션 A: 스크립트 사용
./run-dev.sh

# 옵션 B: 직접 실행
source .venv/bin/activate
uvicorn app:app --reload
```

**예상 출력**:
```
INFO:     Application startup complete [Press Enter twice to quit]
Uvicorn running on http://0.0.0.0:8000
```

### 2단계: 브라우저에서 UI 확인

```
🌐 Welcome 페이지:
   http://localhost:8000/ui/welcome_to_bluedonulab_onboarding/code.html

🧪 API 테스트:
   http://localhost:8000/ui/api-test.html

📚 API 문서:
   http://localhost:8000/api/docs
```

---

## 📁 파일 구조

```
page_design/
├── api-client.js                  ← JavaScript API 클라이언트 (모든 페이지에서 사용)
├── api-test.html                  ← API 테스트 페이지
│
├── welcome_to_bluedonulab_onboarding/
│   ├── code.html                  ← ✅ API 통합됨 (Get Started 버튼)
│   └── screen.png
│
├── personality_test:_care_preferences/
│   ├── code.html                  ← 📋 통합 대기중
│   └── screen.png
│
├── personality_test_results/
│   ├── code.html                  ← 📋 통합 대기중
│   └── screen.png
│
├── caregiver_recommendation_list/
│   ├── code.html                  ← 📋 통합 대기중
│   └── screen.png
│
├── detailed_caregiver_profile/
│   ├── code.html                  ← 📋 통합 대기중
│   └── screen.png
│
└── patient_dashboard:_active_matching/
    ├── code.html                  ← 📋 통합 대기중
    └── screen.png
```

---

## 🔌 API 클라이언트 사용 방법

### 1. HTML에 API 클라이언트 로드

```html
<!-- HTML head 또는 body 끝에 추가 -->
<script src="../api-client.js"></script>

<script>
  // 이제 전역 'api' 객체를 사용할 수 있음
  const stats = await api.getPersonalityStats();
  console.log(stats);
</script>
```

### 2. 사용 가능한 API 메서드

#### 성향 API
```javascript
// 성향 저장
await api.savePersonalityTest(patientId, [0, 1, 2, ...]);

// 성향 조회
const personality = await api.getPersonality(patientId);

// 목록 조회
const list = await api.listPersonalities(limit, offset);

// 통계 조회
const stats = await api.getPersonalityStats();
```

#### 매칭 API
```javascript
// 간병인 추천
const recommendations = await api.recommendCaregivers(patientId, limit);

// 매칭 생성
const matching = await api.createMatching(patientId, caregiverId);

// 매칭 이력
const history = await api.getMatchingHistory(patientId);

// 매칭 취소
await api.cancelMatching(matchingId, reason);

// 성능 평가
const performance = await api.getMatchingPerformance(startDate, endDate);
```

#### 리포트 API
```javascript
// 일일 리포트
await api.generateDailyReport({
  matching_id: 1,
  content: "...",
  mood: "Happy",
  ...
});

// 주간 리포트
const weeklyReport = await api.getWeeklyReport(patientId);

// 월간 리포트
const monthlyReport = await api.getMonthlyReport(startDate, endDate);
```

---

## 🧪 API 테스트 페이지 사용

### 접속 방법
```
http://localhost:8000/ui/api-test.html
```

### 기능
1. ✅ **헬스 체크** - API 서버 상태 확인
2. 📊 **성향 통계** - 환자 성향 데이터 조회
3. 🔍 **간병인 추천** - 환자 1에게 추천 간병인 3명 조회
4. 📋 **매칭 이력** - 환자 1의 매칭 이력 조회

### 예상 결과
```
✅ 헬스 체크
   API 상태: running
   데이터베이스: connected

📊 성향 통계
   총 환자: 1000명
   완료: 1000명
   완료율: 100.0%

🔍 간병인 추천
   1위: James Davis (점수: 89.9, 등급: A)
   2위: Mary Johnson (점수: 88.5, 등급: A)
   3위: John Smith (점수: 87.3, 등급: A)

📋 매칭 이력
   총 매칭: 2건
   1. James Davis (점수: 89.9, 상태: Active)
```

---

## 💡 Welcome 페이지 통합 예시

### 구현된 코드
```javascript
document.getElementById("getStartedBtn").addEventListener("click", async function() {
  try {
    // 1. API 서버 상태 확인
    const status = await api.getAPIStatus();

    // 2. 성향 통계 조회
    const stats = await api.getPersonalityStats();

    // 3. 성공 메시지 표시
    alert(`
✅ BluedonuLab 시스템 작동 확인!

📊 시스템 상태:
- API: ${status.api.status}
- DB: ${status.database.status}

📈 데이터:
- 총 환자: ${stats.total_count}명
- 완료율: ${stats.completion_rate}%
    `);

    // 4. 다음 페이지로 이동 (구현 예정)
    // window.location.href = "../personality_test:_care_preferences/code.html";
  } catch (error) {
    alert("❌ 오류: " + error.message);
  }
});
```

---

## 📊 데이터 흐름

```
┌─────────────────────────────────────────────────────┐
│                   HTML Pages                         │
│  (Google Stitch 생성 + API 통합)                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓ fetch() / axios
┌──────────────────────────────────────────────────────┐
│              JavaScript API Client                   │
│             (api-client.js - 매개역할)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓ REST API
┌──────────────────────────────────────────────────────┐
│          FastAPI Backend                             │
│  (app.py + services + models)                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓ ORM Query
┌──────────────────────────────────────────────────────┐
│         SQLite Database                              │
│  (data/carehome.db)                                 │
└──────────────────────────────────────────────────────┘
```

---

## 🐛 트러블슈팅

### 문제 1: "Cannot find api-client.js"
**해결**:
```html
<!-- 파일 경로 확인 -->
<!-- ../api-client.js  (상위 디렉토리) -->
<!-- ./api-client.js   (같은 디렉토리) -->
```

### 문제 2: "CORS error"
**해결**: 이미 app.py에서 CORS 설정됨
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 문제 3: "Cannot connect to server"
**확인**:
1. FastAPI 서버가 실행 중인가?
   ```
   http://localhost:8000/api/docs
   ```
2. 포트 8000이 사용 중인가?
   ```bash
   lsof -i :8000
   ```

### 문제 4: "GET http://localhost:8000/... 404"
**원인**: API 엔드포인트 경로 오류
**확인**: `http://localhost:8000/api/docs` 에서 올바른 경로 확인

---

## ✨ 다음 단계

### PHASE 6-2: 다른 페이지 통합
- [ ] Personality Test 페이지
- [ ] Caregiver Recommendation 페이지
- [ ] Patient Dashboard 페이지

### PHASE 6-3: React 변환 (선택사항)
- [ ] React 프로젝트 초기화
- [ ] 컴포넌트 변환
- [ ] 상태 관리

### PHASE 6-4: 배포
- [ ] Docker 구성
- [ ] CI/CD 파이프라인
- [ ] 프로덕션 배포

---

## 📚 참고 자료

### API 문서
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 코드 파일
- `api-client.js` - JavaScript API 클라이언트
- `app.py` - FastAPI 메인 애플리케이션
- `services/` - 비즈니스 로직
- `api/` - REST API 엔드포인트

### 문서
- `README.md` - 프로젝트 개요
- `TASK.md` - 구현 계획
- `IMPLEMENTATION_SUMMARY.md` - 완료 보고서

---

## 💬 문제 발생 시

**콘솔 로그 확인**:
```javascript
// 브라우저 F12 → Console 탭
// api-client.js의 console.log() 메시지 확인
✅ BluedonuLab API 클라이언트 로드됨
```

**네트워크 탭 확인**:
```
F12 → Network 탭
API 요청 선택 → Response 확인
```

**서버 로그 확인**:
```
터미널에서 FastAPI 서버 출력 확인
```

---

**작성 일자**: 2024년 11월 12일
**상태**: 🟢 PHASE 6-1 완료 / PHASE 6-2 준비 중
**다음 예정**: 다른 UI 페이지 API 통합
