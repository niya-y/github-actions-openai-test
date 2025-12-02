# caregiver-result-list 페이지 구현 계획

## 📋 개요
- **목표**: 매칭된 간병인 리스트를 소스 디자인 기준으로 리디자인하고, 플립 카드 기능으로 매칭 근거를 상세 표시
- **기간**: 약 6-9시간 예상
- **브랜치**: `test-sang-only`

---

## 🎯 주요 요구사항

### 1️⃣ 디자인 개선
- ✅ 소스 디자인(reference) 스타일 적용
- ✅ 카드 레이아웃: 태그, 프로필 사진, 이름, 설명, 시급, 매칭%, 매칭근거버튼
- ✅ "프로필 보기" 버튼 제거
- ✅ "선택하기" 버튼만 유지

### 2️⃣ 플립 카드 기능
- ✅ 앞면: 기본 정보 (현재 화면)
- ✅ 뒷면: 매칭 근거 상세 설명
- ✅ "매칭 근거 확인하기" 버튼 → 플립 카드 토글

### 3️⃣ 매칭 근거 자동 생성
- ✅ 환자의 질병, 성격 점수, 선호도 활용
- ✅ 간병인의 경력, 전문분야, 성격 활용
- ✅ XGBoost 매칭 점수 활용
- ✅ 객관적 지표 + 감정적 톤으로 작성

### 4️⃣ API 데이터 완성
- ✅ DB에서 필요한 모든 정보 가져오기
- ✅ 백엔드 API 응답에 필요한 필드 추가
- ✅ 매칭 근거 동적 생성

---

## 📝 작업 단계별 계획

### Phase 1: 분석 (1시간)
#### 1.1 소스 디자인 분석 완료 ✅
```
파일: /Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-merge-frontend-backend-ai/frontend/my-app/src/app/caregiver-result-list/page.tsx

주요 요소:
- 헤더: 뒤로가기, 제목("추천 간병인"), 알림 버튼
- 타이틀: "{이름}님에게 적합한 간병인", "{count}명의 전문가를 찾았습니다"
- 카드 구조:
  * 태그: 자격증, 경력 (bg-[#18d4c6] 테일)
  * 프로필: 사진(62x62px 원형), 이름, 설명, 시급
  * 매칭: "매칭 근거 확인하기" 버튼, 매칭% (90% 이상 빨간색)
  * 버튼: "프로필 보기" (제거 예정), "선택하기" (선택형)
- 스타일: 테일윈드, border-[#18d4c6], shadow 적용
```

#### 1.2 현재 API 분석
```
엔드포인트: POST /api/matching/recommend-xgboost
응답 필드:
- patient_id (number)
- total_matches (number)
- matches (array)
  * matching_id (number)
  * caregiver_id (number)
  * caregiver_name (string)
  * job_title (string)
  * grade (string): A, B, C
  * match_score (number): 0-100
  * experience_years (number)
  * hourly_rate (number) ⚠️ 필요
  * avg_rating (number) ⚠️ 필요
  * profile_image_url (string) ⚠️ 필요
  * personality_analysis (string) ⚠️ 필요
  * specialties (array) ⚠️ 필요: ["당뇨", "치매" 등]
  * availability (array)
```

---

### Phase 2: 백엔드 API 개선 (2-3시간)

#### 2.1 필요한 필드 추가
파일: `backend/app/routes/xgboost_matching.py`

```python
# CaregiverMatchResult 클래스에 추가 필드 포함
class CaregiverMatchResult(BaseModel):
    caregiver_id: int
    caregiver_name: str
    job_title: str
    grade: str
    match_score: float
    experience_years: int
    hourly_rate: float  # ✅ 추가
    avg_rating: float   # ✅ 추가
    profile_image_url: str  # ✅ 추가
    personality_analysis: str
    specialties: List[str]  # ✅ 추가: ["당뇨", "치매" 등]
    availability: List[str]
    matching_id: Optional[int] = None
    matching_reason: str  # ✅ 추가: 매칭 근거 설명
```

#### 2.2 DB 쿼리 개선
- Caregiver 테이블에서 `hourly_rate` 조회
- User 테이블 또는 Profile에서 `profile_image_url` 조회
- Review 테이블에서 `avg_rating` 계산
- Caregiver 테이블에서 `specialties` 추출
- 매칭 근거 생성 함수 호출

#### 2.3 매칭 근거 생성 함수
```python
def generate_matching_reason(
    patient_info: dict,  # 질병, 성격점수, 선호도
    caregiver_info: dict,  # 경력, 전문분야, 성격
    match_score: float
) -> str:
    """
    환자 정보와 간병인 정보를 기반으로 감정적/객관적 매칭 근거 생성

    예:
    "당뇨병 및 고혈압 관리에 8년의 경험을 가진 미숙님은
     환자분의 꼼꼼한 성격(신뢰성 75%)과 높은 공감 능력(공감도 85%)으로
     완벽한 케어를 제공할 것입니다. 92%의 높은 호환도로 강력히 추천합니다."
    """
    pass
```

---

### Phase 3: 매칭 근거 생성 로직 구현 (2-3시간)

#### 3.1 정보 수집
```python
# 환자 정보 수집
patient_diseases = get_patient_diseases(patient_id)  # ["당뇨", "고혈압"]
patient_personality = get_patient_personality(patient_id)  # {empathy: 75, ...}
patient_preferences = get_patient_preferences(patient_id)  # {gender: "Female", ...}

# 간병인 정보 수집
caregiver_experience = caregiver.experience_years  # 8
caregiver_specialties = caregiver.specialties  # ["당뇨", "고혈압", "치매"]
caregiver_personality = caregiver.personality  # {empathy: 80, ...}
```

#### 3.2 매칭 근거 구성 요소
```
1. 경력 + 전문분야 소개
   "당뇨병 및 고혈압 관리에 8년의 경험을 가진 미숙님은"

2. 환자의 성격 반영
   "환자분의 꼼꼼한 성격(신뢰성 75%)과"

3. 간병인의 성격 강조
   "높은 공감 능력(공감도 85%)으로"

4. 결론
   "완벽한 케어를 제공할 것입니다."

5. 점수 강조
   "92%의 높은 호환도로 강력히 추천합니다."
```

#### 3.3 구현 예시
```python
def generate_matching_reason(patient_info, caregiver_info, match_score):
    diseases = ", ".join(patient_info['diseases'])
    exp_years = caregiver_info['experience_years']
    caregiver_name = caregiver_info['name']

    # 1단계: 경력 소개
    intro = f"{diseases} 관리에 {exp_years}년의 경험을 가진 {caregiver_name}님은"

    # 2단계: 환자 성격
    patient_personality_trait = get_personality_trait(patient_info['personality'])
    personality_part = f"환자분의 {patient_personality_trait}적인 성격으로"

    # 3단계: 간병인 성격
    caregiver_trait = get_personality_trait(caregiver_info['personality'])
    caregiver_part = f"{caregiver_trait}한 케어를 제공할 것입니다."

    # 4단계: 점수
    if match_score >= 90:
        score_part = f"{match_score:.0f}%의 높은 호환도로 강력히 추천합니다."
    elif match_score >= 80:
        score_part = f"{match_score:.0f}%의 좋은 호환도로 추천합니다."
    else:
        score_part = f"{match_score:.0f}%의 호환도입니다."

    return f"{intro} {personality_part} {caregiver_part} {score_part}"
```

---

### Phase 4: 프론트엔드 페이지 리디자인 (2-3시간)

#### 4.1 파일 구조
파일: `frontend/my-app/src/app/caregiver-result-list/page.tsx`

#### 4.2 상태 관리
```typescript
const [matches, setMatches] = useState<CaregiverMatch[]>([])
const [flippedCards, setFlippedCards] = useState<{ [key: number]: boolean }>({})
const [patientName, setPatientName] = useState<string>("")
const [totalCount, setTotalCount] = useState(0)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<Error | null>(null)
```

#### 4.3 플립 카드 함수
```typescript
const toggleFlip = (caregiverId: number) => {
  setFlippedCards(prev => ({
    ...prev,
    [caregiverId]: !prev[caregiverId]
  }))
}

const isFlipped = (caregiverId: number) => {
  return flippedCards[caregiverId] || false
}
```

#### 4.4 카드 레이아웃

**앞면 (기본 정보)**
```
┌─────────────────────────────────────┐
│ [태그1]  [태그2]                     │
│ [사진] 이름                          │
│        설명                          │
│        ₩25,000/시간                 │
│                                      │
│ [매칭근거] ───────────── 92% 매칭    │
│ ────────────────────────────────────│
│ [프로필보기]      [선택하기]         │
└─────────────────────────────────────┘
```

**뒷면 (매칭 근거)**
```
┌─────────────────────────────────────┐
│                                      │
│ 매칭 근거                            │
│ ───────────────────                 │
│                                      │
│ "당뇨병 및 고혈압 관리에 8년의      │
│  경험을 가진 미숙님은 환자분의      │
│  꼼꼼한 성격으로 완벽한 케어를      │
│  제공할 것입니다. 92%의 높은 호환도 │
│  로 강력히 추천합니다."             │
│                                      │
└─────────────────────────────────────┘
```

#### 4.5 CSS 클래스 구조
```typescript
// 카드 컨테이너 (플립 애니메이션)
className="h-[500px] cursor-pointer perspective"
style={{ transformStyle: "preserve-3d", transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)" }}

// 앞면
className={cn(
  isFlipped ? "hidden" : "block",
  "rounded-[10px] border border-[#18d4c6] bg-white p-4 shadow-[1px_3px_3px_rgba(74,73,73,0.25)]"
)}

// 뒷면
className={cn(
  isFlipped ? "block" : "hidden",
  "rounded-[10px] border border-[#18d4c6] bg-white p-6 shadow-[1px_3px_3px_rgba(74,73,73,0.25)] flex flex-col justify-center"
)}
```

#### 4.6 구성 요소
- **헤더**: 뒤로가기, "추천 간병인" 제목, 알림 버튼
- **타이틀 섹션**: 환자 이름 + 찾은 간병인 수
- **카드 목록**: 매칭된 간병인들의 플립 카드

---

### Phase 5: API 통합 (1시간)

#### 5.1 데이터 로딩
```typescript
useEffect(() => {
  const fetchMatches = async () => {
    try {
      // 세션 스토리지에서 patient_id 및 care_requirements 조회
      const patientId = sessionStorage.getItem('patient_id')
      const careReqs = JSON.parse(sessionStorage.getItem('care_requirements') || '{}')

      // 매칭 결과 조회
      const response = await apiGet<MatchingResponse>('/api/matching/results')

      setMatches(response.matches)
      setTotalCount(response.total_count)
      setPatientName(patientId ? `환자${patientId}` : '고객')
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  fetchMatches()
}, [])
```

#### 5.2 데이터 타입
```typescript
interface CaregiverMatch {
  matching_id: number
  caregiver_id: number
  caregiver_name: string
  job_title: string
  grade: string
  match_score: number
  experience_years: number
  hourly_rate: number
  avg_rating: number
  profile_image_url: string
  specialties: string[]
  matching_reason: string
}

interface MatchingResponse {
  patient_id: number
  total_matches: number
  matches: CaregiverMatch[]
}
```

---

### Phase 6: 테스트 (1시간)

#### 6.1 기능 테스트
- [ ] 간병인 리스트 로드 확인
- [ ] 플립 카드 토글 작동 확인
- [ ] 매칭 근거 올바르게 표시 확인
- [ ] 선택하기 버튼 동작 확인
- [ ] 반응형 디자인 확인

#### 6.2 API 테스트
- [ ] 백엔드 API 응답 필드 확인
- [ ] 매칭 근거 생성 정확성 확인
- [ ] 이미지 로딩 확인
- [ ] 평가점수 계산 확인

#### 6.3 디자인 테스트
- [ ] 소스 디자인과 비교
- [ ] 색상 정확도 확인 (#18d4c6, #353535, #828282)
- [ ] 레이아웃 정렬 확인
- [ ] 그림자 및 테두리 확인

---

## 🔄 프로세스 플로우

```
1. 소스 디자인 분석
   ↓
2. 백엔드 API 수정
   ├─ 필드 추가
   ├─ DB 쿼리 개선
   └─ 매칭 근거 생성
   ↓
3. 매칭 근거 로직 구현
   ├─ 함수 작성
   ├─ 테스트 데이터로 검증
   └─ 감정적 톤 적용
   ↓
4. 프론트엔드 개발
   ├─ 카드 레이아웃
   ├─ 플립 기능
   ├─ 상태 관리
   └─ 스타일 적용
   ↓
5. API 통합
   ├─ 데이터 로딩
   ├─ 에러 처리
   └─ 세션 관리
   ↓
6. 테스트 및 배포
   ├─ 기능 테스트
   ├─ 디자인 검증
   └─ 커밋/푸시
```

---

## 📌 주의사항

### ⚠️ 필수 확인
- [ ] 백엔드 DB에서 `hourly_rate` 필드 존재 확인
- [ ] User 테이블에서 `profile_image_url` 또는 프로필 이미지 저장 위치 확인
- [ ] Review 테이블 구조 확인 (평가 점수 계산)
- [ ] Caregiver 테이블에서 `specialties` 저장 방식 확인 (JSON 또는 별도 테이블)

### 🛡️ 에러 처리
- 이미지 로드 실패 시 기본 이미지 표시
- 매칭 근거 생성 실패 시 기본 메시지 표시
- API 오류 시 사용자 친화적 메시지 표시

### 🎨 디자인 일관성
- 색상: #18d4c6 (테일), #353535 (진한 글씨), #828282 (회색 글씨)
- 테두리: border-[#18d4c6]
- 그림자: shadow-[1px_3px_3px_rgba(74,73,73,0.25)]
- 모서리: rounded-[10px]

---

## 📊 완료 체크리스트

### Phase 1: 분석
- [x] 소스 디자인 분석 완료
- [x] 현재 API 분석 완료
- [ ] 필드 매핑 완료

### Phase 2: 백엔드 개선
- [ ] 필드 추가 (CaregiverMatchResult)
- [ ] DB 쿼리 개선
- [ ] 매칭 근거 생성 함수 작성
- [ ] API 테스트

### Phase 3: 매칭 근거 로직
- [ ] 함수 구현
- [ ] 감정적 톤 적용
- [ ] 테스트 및 검증

### Phase 4: 프론트엔드
- [ ] 헤더 구현
- [ ] 타이틀 섹션 구현
- [ ] 카드 레이아웃 구현
- [ ] 플립 기능 구현
- [ ] 스타일 적용

### Phase 5: 통합
- [ ] 데이터 로딩
- [ ] 상태 관리
- [ ] 에러 처리

### Phase 6: 테스트
- [ ] 기능 테스트
- [ ] 디자인 검증
- [ ] 최종 QA

### Phase 7: 배포
- [ ] 커밋
- [ ] 푸시

---

## 📚 참고 자료

### 소스 디자인 위치
```
/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-merge-frontend-backend-ai/frontend/my-app/src/app/caregiver-result-list/page.tsx
```

### 현재 파일 위치
```
/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/frontend/my-app/src/app/caregiver-result-list/page.tsx
/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/backend/app/routes/xgboost_matching.py
```

### 관련 타입 정의
```
frontend/my-app/src/types/api.ts
```

---

**작성일**: 2025-12-02
**상태**: 준비 완료 ✅
**예상 소요시간**: 6-9시간
