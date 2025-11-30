# 프론트엔드 개발자 Task List

> **담당**: 프론트엔드 개발자
> **기간**: 2025-11-26 ~ (TBD)
> **참고 문서**: `API_CONTRACT.md`, `FRONTEND_TASKS.md` (최신화)

---

## 📋 개발 우선순위

### 🔴 P0 (최우선 - 1주차)

환자 등록 플로우 페이지 수정 및 API 연동

### 🟡 P1 (중요 - 2주차)

매칭 및 성향 테스트 API 연동

### 🟢 P2 (일반 - 3주차)

케어 플랜 및 마이페이지 API 연동

---

## Phase 1: 공통 모듈 구현

### 1.1 API 호출 공통 함수 작성

**우선순위**: 🔴 P0
**예상 시간**: 2시간
**파일**: `frontend/my-app/src/lib/api.ts`

#### Task

```typescript
// frontend/my-app/src/lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

interface APIResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

/**
 * API 호출 공통 함수
 */
export async function callAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const token = getToken(); // localStorage에서 JWT 토큰 가져오기

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    });

    const data: APIResponse<T> = await response.json();

    if (!response.ok || data.status === 'error') {
      throw new APIError(
        data.error?.code || 'UNKNOWN_ERROR',
        data.error?.message || '오류가 발생했습니다.',
        response.status,
        data.error?.details
      );
    }

    return data.data as T;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    console.error('API Error:', error);
    throw new APIError(
      'NETWORK_ERROR',
      '네트워크 오류가 발생했습니다.',
      0
    );
  }
}

/**
 * GET 요청
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
  return callAPI<T>(endpoint, { method: 'GET' });
}

/**
 * POST 요청
 */
export async function apiPost<T>(
  endpoint: string,
  body: any
): Promise<T> {
  return callAPI<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUT 요청
 */
export async function apiPut<T>(
  endpoint: string,
  body: any
): Promise<T> {
  return callAPI<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * DELETE 요청
 */
export async function apiDelete<T>(endpoint: string): Promise<T> {
  return callAPI<T>(endpoint, { method: 'DELETE' });
}

/**
 * JWT 토큰 가져오기
 */
function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * JWT 토큰 저장
 */
export function setToken(token: string): void {
  localStorage.setItem('access_token', token);
}

/**
 * JWT 토큰 삭제
 */
export function removeToken(): void {
  localStorage.removeItem('access_token');
}
```

#### 체크리스트

- [ ] `frontend/my-app/src/lib/api.ts` 생성
- [ ] API 호출 함수 작성 (GET, POST, PUT, DELETE)
- [ ] 에러 클래스 작성
- [ ] 토큰 관리 함수 작성
- [ ] `.env.local`에 `NEXT_PUBLIC_API_BASE_URL` 추가

---

### 1.2 TypeScript 타입 정의 (최신화)

**우선순위**: 🔴 P0
**예상 시간**: 1.5시간
**파일**: `frontend/my-app/src/types/api.ts`

#### Task

```typescript
// frontend/my-app/src/types/api.ts

// ==================== 보호자 ====================

export interface GuardianCreateRequest {
  name: string;
  phone: string;
  address: string;
  relationship: string;
}

export interface GuardianResponse {
  guardian_id: number;
  user_id: number;
  name: string;
  phone: string;
  address: string;
  relationship: string;
  created_at: string;
}

// ==================== 환자 ====================

// 질병 항목 타입 정의
export interface DiseaseItem {
  id: string;
  name: string;
}

export interface PatientCreateRequest {
  name: string;
  age: number;
  gender: 'Male' | 'Female'; // 백엔드 Enum에 맞춰 변경
  relationship: string;
}

export interface PatientResponse {
  patient_id: number;
  name: string;
  birth_date: string;
  age: number;
  gender: 'Male' | 'Female'; // 백엔드 Enum에 맞춰 변경
  guardian_id: number;
  created_at: string;
}

export interface HealthStatusUpdateRequest { // 변경된 스키마 반영
  selectedDiseases: DiseaseItem[]; // DiseaseItem 배열로 변경
  mobility_status: string; // "independent", "assistive-device", "wheelchair", "bedridden" 중 하나
}

export interface HealthConditionResponse { // 건강 상태 응답
  condition_id: number;
  patient_id: number;
  selected_diseases: DiseaseItem[];
  mobility_status: string;
  created_at: string;
}

export interface MedicationsCreateRequest { // 변경된 스키마 반영
  medicine_names: string[]; // 약물 이름 배열로 변경
}

export interface MedicationResponse { // 약물 응답
  med_id: number;
  patient_id: number;
  medicine_names: string[];
  created_at: string;
}

// ==================== 성향 테스트 ====================

export interface PersonalityTestRequest {
  user_type: 'guardian' | 'caregiver';
  answers: {
    step1: string;
    step2: string;
    step3: string;
  };
}

export interface PersonalityTestResponse {
  test_id: number;
  user_id: number;
  scores: {
    empathy_score: number;
    activity_score: number;
    patience_score: number;
    independence_score: number;
  };
  ai_analysis: string;
  created_at: string;
}

// ==================== 매칭 ====================

export interface MatchingRequirements {
  care_type: string;
  time_slots: string[];
  gender: 'Male' | 'Female' | 'any'; // 백엔드 Enum에 맞춰 변경 및 'any' 추가
  experience: string;
  skills: string[];
}

export interface MatchingRequest {
  patient_id: number;
  requirements: MatchingRequirements;
}

export interface CaregiverMatch { // MatchingResultResponse와 매핑
  matching_id: number;
  caregiver_id: number;
  caregiver_name: string;
  grade: string;
  match_score: number;
  experience_years: number;
  specialties: string[];
  hourly_rate: number;
  avg_rating: number;
  profile_image_url: string;
}

export interface MatchingResponse { // 매칭 API 응답은 MatchResultResponse[] 형태
  matches: CaregiverMatch[];
  total_count: number;
}

// ==================== 리뷰 ====================

export interface ReviewCreateRequest {
  rating: number;
  comment: string;
}

export interface ReviewResponse {
  review_id: number;
  matching_id: number;
  rating: number;
  comment: string;
  created_at: string;
}

// ==================== 케어 플랜 ====================

export interface Schedule {
  schedule_id: number;
  title: string;
  start_time: string;
  end_time: string;
  category: string;
  is_completed: boolean;
}

export interface MealPlan {
  meal_plan_id: number;
  meal_date: string;
  meal_type: string;
  menu_name: string;
  nutrition_info: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
}

export interface CarePlansResponse {
  type: 'weekly' | 'monthly';
  schedules: Schedule[];
  meal_plans: MealPlan[];
}

// ==================== 마이페이지 ====================

export interface DashboardResponse {
  user: {
    user_id: number;
    name: string;
    email: string;
    phone: string;
    user_type: string;
    gender?: 'Male' | 'Female'; // User 모델 gender 추가
  };
  guardian: {
    guardian_id: number;
    address: string;
    relationship: string;
  } | null;
  patients: Array<{
    patient_id: number;
    name: string;
    age: number;
    care_level: string;
  }>;
  active_matching: {
    caregiver_name: string;
    match_score: number;
    start_date: string;
  } | null;
}
```

#### 체크리스트

- [ ] `frontend/my-app/src/types/api.ts` 생성
- [ ] 모든 API 요청/응답 타입 정의 (최신화)
- [ ] 타입 export 확인

---

### 1.3 에러 핸들링 UI 컴포넌트

**우선순위**: 🔴 P0
**예상 시간**: 1시간
**파일**: `frontend/my-app/src/components/ErrorAlert.tsx`

#### Task

```typescript
// frontend/my-app/src/components/ErrorAlert.tsx
'use client';

import { useEffect } from 'react';

interface ErrorAlertProps {
  error: Error | null;
  onClose?: () => void;
}

export default function ErrorAlert({ error, onClose }: ErrorAlertProps) {
  useEffect(() => {
    if (error && onClose) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000); // 5초 후 자동 닫힘

      return () => clearTimeout(timer);
    }
  }, [error, onClose]);

  if (!error) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-red-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-800">오류</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error.message}</p>
            </div>
          </div>
          {onClose && (
            <div className="ml-auto pl-3">
              <button
                onClick={onClose}
                className="inline-flex rounded-md bg-red-50 p-1.5 text-red-500 hover:bg-red-100"
              >
                <span className="sr-only">닫기</span>
                <svg
                  className="h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

#### 체크리스트

- [ ] `ErrorAlert.tsx` 컴포넌트 생성
- [ ] 자동 닫힘 기능 구현
- [ ] 스타일 적용

---

## Phase 2: 보호자 & 환자 등록 페이지 수정 (P0)

### 2.1 matching/page.tsx 수정

**우선순위**: 🔴 P0
**예상 시간**: 1시간
**파일**: `frontend/my-app/src/app/matching/page.tsx`

#### 문제점

입력 필드에 `name` 속성이 없음

#### 수정 사항

```tsx
// 현재 코드 (잘못됨)
<Input type="text" placeholder="홍길동" />

// 수정 후
<Input
  name="patientName"
  type="text"
  placeholder="홍길동"
  value={formData.patientName}
  onChange={(e) => setFormData({ ...formData, patientName: e.target.value })}
/>

<Input
  name="age"
  type="number"
  placeholder="75"
  value={formData.age}
  onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) })}
/>

<Input
  name="region"
  type="text"
  placeholder="서울시 강남구"
  value={formData.region}
  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
/>

<Input
  name="careRequirements"
  type="text"
  placeholder="예: 치매, 거동 불편"
  value={formData.careRequirements}
  onChange={(e) => setFormData({ ...formData, careRequirements: e.target.value })}
/>
```

#### 체크리스트

- [ ] 모든 Input 컴포넌트에 `name` 속성 추가
- [ ] useState로 formData 상태 관리
- [ ] onChange 핸들러 구현

---

### 2.2 guardians/page.tsx API 연동

**우선순위**: 🔴 P0
**예상 시간**: 1.5시간
**파일**: `frontend/my-app/src/app/guardians/page.tsx`

#### Task

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api';
import ErrorAlert from '@/components/ErrorAlert';
import type { GuardianCreateRequest, GuardianResponse } from '@/types/api';

export default function GuardiansPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
    relationship: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 유효성 검증
    if (!formData.name || !formData.phone || !formData.address || !formData.relationship) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiPost<GuardianResponse>(
        '/api/guardians',
        formData
      );

      console.log('보호자 정보 등록 성공:', response);

      // 다음 페이지로 이동
      router.push('/patient-condition-1');
    } catch (err) {
      console.error('보호자 정보 등록 실패:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <form onSubmit={handleSubmit}>
        {/* 기존 UI 유지 */}
        <Input
          name="name"
          type="text"
          placeholder="김영수"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />

        <select
          name="relationship"
          value={formData.relationship}
          onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
        >
          <option value="">선택해주세요</option>
          <option value="배우자">배우자</option>
          <option value="자녀">자녀</option>
          <option value="부모">부모</option>
          <option value="형제자매">형제자매</option>
          <option value="손자/손녀">손자/손녀</option>
          <option value="기타">기타</option>
        </select>

        <Input
          name="phone"
          type="text"
          placeholder="010-1234-5678"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
        />

        <Input
          name="address"
          type="text"
          placeholder="서울시 강남구 테헤란로 123"
          value={formData.address}
          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
        />

        <button type="submit" disabled={loading}>
          {loading ? '등록 중...' : '다음'}
        </button>
      </form>
    </div>
  );
}
```

#### 체크리스트

- [ ] API 호출 함수 연동
- [ ] 로딩 상태 관리
- [ ] 에러 핸들링
- [ ] 성공 시 페이지 이동

---

### 2.3 patient-condition-1/page.tsx API 연동

**우선순위**: 🔴 P0
**예상 시간**: 1.5시간
**파일**: `frontend/my-app/src/app/patient-condition-1/page.tsx`

#### Task

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api';
import ErrorAlert from '@/components/ErrorAlert';
import type { PatientCreateRequest, PatientResponse } from '@/types/api';

export default function PatientCondition1Page() {
  const router = useRouter();
  const [formData, setFormData] = useState<PatientCreateRequest>({
    name: '',
    age: 0,
    gender: 'Female', // 백엔드 Enum에 맞춰 변경
    relationship: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.age || !formData.relationship) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiPost<PatientResponse>(
        '/api/patients',
        formData
      );

      console.log('환자 정보 등록 성공:', response);

      // patient_id를 세션 스토리지에 저장 (다음 페이지에서 사용)
      sessionStorage.setItem('patient_id', response.patient_id.toString());

      router.push('/patient-condition-2');
    } catch (err) {
      console.error('환자 정보 등록 실패:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <form onSubmit={handleSubmit}>
        <Input
          name="name"
          type="text"
          placeholder="예: 김영희"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Input
          name="age"
          type="number"
          placeholder="예: 78"
          value={formData.age || ''}
          onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || 0 })}
          required
        />

        {/* 성별 선택 */}
        <div>
          <label>성별</label>
          <div onClick={() => setFormData({ ...formData, gender: 'Female' })}>
            여성 {formData.gender === 'Female' && '✓'}
          </div>
          <div onClick={() => setFormData({ ...formData, gender: 'Male' })}>
            남성 {formData.gender === 'Male' && '✓'}
          </div>
        </div>

        <select
          name="relationship"
          value={formData.relationship}
          onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
          required
        >
          <option value="">선택해주세요</option>
          <option value="어머니">어머니</option>
          <option value="아버지">아버지</option>
          <option value="배우자">배우자</option>
          <option value="조부모">조부모</option>
          <option value="기타">기타</option>
        </select>

        <button type="submit" disabled={loading}>
          {loading ? '등록 중...' : '다음'}
        </button>
      </form>
    </div>
  );
}
```

#### 체크리스트

- [ ] API 호출 함수 연동
- [ ] patient_id를 sessionStorage에 저장
- [ ] 성별 값 ('Female', 'Male') 확인
- [ ] 성공 시 페이지 이동

---

### 2.4 patient-condition-2/page.tsx API 연동 (최신화)

**우선순위**: 🔴 P0
**예상 시간**: 2시간
**파일**: `frontend/my-app/src/app/patient-condition-2/page.tsx`

#### Task

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPut } from '@/lib/api';
import ErrorAlert from '@/components/ErrorAlert';
import type { HealthStatusUpdateRequest, DiseaseItem, HealthConditionResponse } from '@/types/api';

const diseasesOptions: DiseaseItem[] = [
  { id: 'dementia', name: '치매/인지장애' },
  { id: 'stroke', name: '뇌졸중/중풍' },
  { id: 'cancer', name: '암' },
  { id: 'diabetes', name: '당뇨병' },
  { id: 'hypertension', name: '고혈압' },
  { id: 'parkinsons', name: '파킨슨병' },
  { id: 'arthritis', name: '관절염' },
  { id: 'other', name: '기타' }
];

const mobilityOptions = [
  { id: 'independent', icon: '🚶', label: '혼자 걸을 수 있음', desc: '보조 없이 독립 보행 가능' },
  { id: 'assistive-device', icon: '🦯', label: '보조 기구 필요', desc: '지팡이, 워커 등 사용' },
  { id: 'wheelchair', icon: '♿', label: '휠체어 사용', desc: '휠체어로 이동' },
  { id: 'bedridden', icon: '🛏️', label: '침상 생활', desc: '거동 불가, 침대에서만 생활' }
];

export default function PatientCondition2Page() {
  const router = useRouter();
  const [selectedDiseases, setSelectedDiseases] = useState<DiseaseItem[]>([]); // 객체 배열로 변경
  const [selectedMobility, setSelectedMobility] = useState<string>(''); // string ID
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const patientId = sessionStorage.getItem('patient_id');
    if (!patientId) {
      alert('환자 정보를 먼저 등록해주세요.');
      router.push('/patient-condition-1');
      return;
    }

    if (selectedDiseases.length === 0 || !selectedMobility) {
        alert('질병 정보와 거동 상태를 모두 선택해주세요.');
        return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: HealthStatusUpdateRequest = {
        selectedDiseases: selectedDiseases, // 객체 배열 그대로 전송
        mobility_status: selectedMobility
      };

      await apiPut<HealthConditionResponse>(`/api/patients/${patientId}/health-status`, payload);

      console.log('건강 상태 업데이트 성공');
      router.push('/patient-condition-3');
    } catch (err) {
      console.error('건강 상태 업데이트 실패:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDisease = (disease: DiseaseItem) => {
    setSelectedDiseases((prev) =>
      prev.some(d => d.id === disease.id) // ID로 비교
        ? prev.filter((d) => d.id !== disease.id)
        : [...prev, disease]
    );
  };

  return (
    <div>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <form onSubmit={handleSubmit}>
        {/* 질병 선택 */}
        <div>
          <h3>주요 질병</h3>
          {diseasesOptions.map(
            (disease) => (
              <div
                key={disease.id}
                onClick={() => toggleDisease(disease)}
                className={selectedDiseases.some(d => d.id === disease.id) ? 'selected' : ''}
              >
                {disease.name} {selectedDiseases.some(d => d.id === disease.id) && '✓'}
              </div>
            )
          )}
        </div>
        
        {/* 거동 상태 */}
        <div>
          <h3>거동 상태</h3>
          {mobilityOptions.map((mobility) => (
            <div
              key={mobility.id}
              onClick={() => setSelectedMobility(mobility.id)}
              className={selectedMobility === mobility.id ? 'selected' : ''}
            >
              {mobility.label} {selectedMobility === mobility.id && '✓'}
            </div>
          ))}
        </div>

        <button type="submit" disabled={loading}>
          {loading ? '저장 중...' : '다음'}
        </button>
      </form>
    </div>
  );
}
```

#### 체크리스트

- [ ] API 호출 함수 연동
- [ ] sessionStorage에서 patient_id 가져오기
- [ ] `selectedDiseases` (객체 배열) 및 `mobility_status` (string ID) 관리
- [ ] 성공 시 페이지 이동

---

### 2.5 patient-condition-3/page.tsx API 연동 (최신화)

**우선순위**: 🔴 P0
**예상 시간**: 1.5시간
**파일**: `frontend/my-app/src/app/patient-condition-3/page.tsx`

#### Task

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api';
import ErrorAlert from '@/components/ErrorAlert';
import type { MedicationsCreateRequest, MedicationResponse } from '@/types/api'; // MedicationResponse는 단일 객체 응답

export default function PatientCondition3Page() {
  const router = useRouter();
  const [currentMed, setCurrentMed] = useState('');
  const [medicine_names, setMedicineNames] = useState<string[]>([]); // 약물 이름 배열로 변경
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleAddMedication = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && currentMed.trim()) {
      e.preventDefault();
      setMedicineNames([...medicine_names, currentMed.trim()]);
      setCurrentMed('');
    }
  };

  const handleRemoveMedication = (index: number) => {
    setMedicineNames(medicine_names.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const patientId = sessionStorage.getItem('patient_id');
    if (!patientId) {
      alert('환자 정보를 먼저 등록해주세요.');
      router.push('/patient-condition-1');
      return;
    }

    if (medicine_names.length === 0) {
      alert('최소 1개 이상의 약물을 등록해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: MedicationsCreateRequest = {
        medicine_names: medicine_names, // 변경된 필드명 사용
      };

      // API 응답 타입이 MedicationResponse (단일 객체)로 변경됨
      const response = await apiPost<MedicationResponse>(
        `/api/patients/${patientId}/medications`,
        payload
      );

      console.log('약물 정보 등록 성공:', response);
      router.push('/personality-test');
    } catch (err) {
      console.error('약물 정보 등록 실패:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <ErrorAlert error={error} onClose={() => setError(null)} />

      <form onSubmit={handleSubmit}>
        {/* 약물 입력 */}
        <Input
          name="currentMed"
          type="text"
          placeholder="약 이름을 입력하세요 (예: 아스피린, 메트포민...)"
          value={currentMed}
          onChange={(e) => setCurrentMed(e.target.value)}
          onKeyDown={handleAddMedication}
        />

        {/* 약물 목록 */}
        <div>
          {medicine_names.map((med, index) => (
            <div key={index} className="medication-chip">
              {med}
              <button type="button" onClick={() => handleRemoveMedication(index)}>
                ×
              </button>
            </div>
          ))}
        </div>

        <button type="submit" disabled={loading}>
          {loading ? '저장 중...' : '다음'}
        </button>
      </form>
    </div>
  );
}
```

#### 체크리스트

- [ ] API 호출 함수 연동
- [ ] `medicine_names` (string 배열) 관리 (추가/삭제)
- [ ] `notes` 필드 제거 확인
- [ ] Enter 키로 약물 추가 기능
- [ ] 성공 시 페이지 이동

---

## Phase 3: 성향 테스트 & 매칭 API 연동 (P1)

### 3.1 personality-test/page.tsx API 연동

**우선순위**: 🟡 P1
**예상 시간**: 2시간
**파일**: `frontend/my-app/src/app/personality-test/page.tsx`

#### Task

```tsx
const handleSubmit = async () => {
  setLoading(true);
  setError(null);

  try {
    const payload: PersonalityTestRequest = {
      user_type: 'guardian',
      answers: {
        step1: answers.step1 || '',
        step2: answers.step2 || '',
        step3: answers.step3 || ''
      }
    };

    const response = await apiPost<PersonalityTestResponse>(
      '/api/personality-tests',
      payload
    );

    console.log('성향 테스트 완료:', response);

    // 결과 페이지로 이동 (또는 다음 페이지)
    router.push('/caregiver-finder');
  } catch (err) {
    console.error('성향 테스트 실패:', err);
    setError(err as Error);
  } finally {
    setLoading(false);
  }
};
```

#### 체크리스트

- [ ] 3단계 답변 수집
- [ ] API 호출 함수 연동
- [ ] 성공 시 페이지 이동

---

### 3.2 caregiver-finder/page.tsx API 연동

**우선순위**: 🟡 P1
**예상 시간**: 2.5시간
**파일**: `frontend/my-app/src/app/caregiver-finder/page.tsx`

#### Task

```tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  const patientId = sessionStorage.getItem('patient_id');
  if (!patientId) {
    alert('환자 정보를 찾을 수 없습니다.');
    return;
  }

  setLoading(true);
  setError(null);

  try {
    const payload: MatchingRequest = {
      patient_id: parseInt(patientId),
      requirements: {
        care_type: careType,
        time_slots: timeSlots,
        gender: gender, // 'Male', 'Female', 'any' 중 하나
        experience: experience,
        skills: skills
      }
    };

    const response = await apiPost<MatchingResponse> ( // MatchingResponse는 CaregiverMatch[]를 포함
      '/api/matching',
      payload
    );

    console.log('매칭 성공:', response);

    // 매칭 결과 페이지로 이동
    router.push('/matching');
  } catch (err) {
    console.error('매칭 실패:', err);
    setError(err as Error);
  } finally {
    setLoading(false);
  }
};
```

#### 체크리스트

- [ ] 요구사항 폼 데이터 수집
- [ ] API 호출 함수 연동
- [ ] `gender` 필드값 ('Male', 'Female', 'any') 확인
- [ ] 성공 시 매칭 결과 페이지로 이동

---

### 3.3 matching/page.tsx (매칭 결과 조회)

**우선순위**: 🟡 P1
**예상 시간**: 2시간

#### Task

```tsx
'use client';

import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api';
import type { MatchingResponse } from '@/types/api';

export default function MatchingPage() {
  const [matches, setMatches] = useState<MatchingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchMatches = async () => {
      const patientId = sessionStorage.getItem('patient_id');
      if (!patientId) {
        alert('환자 정보를 찾을 수 없습니다.');
        return;
      }

      try {
        // 백엔드는 MatchingResultResponse 배열을 직접 반환
        const response = await apiGet<MatchingResponse> ( // API_CONTRACT.md에 따르면 배열을 data로 감싸서 응답
          `/api/patients/${patientId}/matching-results?status=recommended`
        );
        // data 필드에 배열이 담겨있으므로, 그 배열을 setMatches에 전달
        setMatches(response); // MatchingResponse는 { matches: CaregiverMatch[], total_count: number } 구조를 가정
      } catch (err) {
        console.error('매칭 결과 조회 실패:', err);
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  if (loading) return <div>로딩 중...</div>;
  if (error) return <ErrorAlert error={error} />;
  if (!matches || matches.matches.length === 0) return <div>매칭 결과가 없습니다.</div>;

  return (
    <div>
      <h1>AI 추천 간병인 ({matches.total_count}명)</h1>
      {matches.matches.map((match) => (
        <div key={match.matching_id} className="caregiver-card">
          <img src={match.profile_image_url} alt={match.caregiver_name} />
          <h2>{match.caregiver_name}</h2>
          <p>등급: {match.grade}</p>
          <p>매칭 점수: {match.match_score}점</p>
          <p>경력: {match.experience_years}년</p>
          <p>전문 분야: {match.specialties.join(', ')}</p>
          <p>시급: {match.hourly_rate.toLocaleString()}원</p>
          <p>평점: {match.avg_rating}/5.0</p>
        </div>
      ))}
    </div>
  );
}
```

#### 체크리스트

- [ ] useEffect로 페이지 로드 시 자동 조회
- [ ] 매칭 결과 리스트 렌더링
- [ ] 로딩/에러 상태 처리

---

## Phase 4: 케어 플랜 & 리뷰 API 연동 (P2)

### 4.1 care-plans-create-2/page.tsx API 연동

**우선순위**: 🟢 P2
**예상 시간**: 2시간

#### Task

```tsx
useEffect(() => {
  const fetchCarePlans = async () => {
    const patientId = sessionStorage.getItem('patient_id');
    if (!patientId) return;

    try {
      const response = await apiGet<CarePlansResponse>(
        `/api/patients/${patientId}/care-plans?type=${activeTab}`
      );

      setSchedules(response.schedules);
      setMealPlans(response.meal_plans);
    } catch (err) {
      console.error('케어 플랜 조회 실패:', err);
      setError(err as Error);
    }
  };

  fetchCarePlans();
}, [activeTab]);
```

#### 체크리스트

- [ ] 주간/월간 탭 전환 시 API 재호출
- [ ] 일정 및 식단 데이터 렌더링

---

### 4.2 care-plans-create-3/page.tsx 리뷰 API 연동

**우선순위**: 🟢 P2
**예상 시간**: 2시간

#### Task

```tsx
const feedbackToRating: Record<string, number> = {
  'appropriate': 5,
  'adjustment': 3,
  'inappropriate': 1,
  'suggestion': 4
};

const handleSubmit = async () => {
  const matchingId = sessionStorage.getItem('matching_id');
  if (!matchingId) {
    alert('매칭 정보를 찾을 수 없습니다.');
    return;
  }

  setLoading(true);
  setError(null);

  try {
    const payload: ReviewCreateRequest = {
      rating: feedbackToRating[selectedFeedback],
      comment: `${suggestion}\n\n전체 의견: ${overallFeedback}`
    };

    const response = await apiPost<ReviewResponse>(
      `/api/matching/${matchingId}/reviews`,
      payload
    );

    console.log('리뷰 등록 성공:', response);
    router.push('/care-plans-create-4');
  } catch (err) {
    console.error('리뷰 등록 실패:', err);
    setError(err as Error);
  } finally {
    setLoading(false);
  }
};
```

#### 체크리스트

- [ ] selectedFeedback → rating 변환
- [ ] 리뷰 제출 API 연동
- [ ] 성공 시 다음 페이지 이동

---

### 4.3 mypage-dashboard/page.tsx API 연동

**우선순위**: 🟢 P2
**예상 시간**: 2시간

#### Task

```tsx
useEffect(() => {
  const fetchDashboard = async () => {
    try {
      const response = await apiGet<DashboardResponse>('/api/users/me/dashboard');

      setDashboardData(response);
    } catch (err) {
      console.error('대시보드 조회 실패:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  fetchDashboard();
}, []);
```

#### 체크리스트

- [ ] 대시보드 데이터 조회
- [ ] 사용자 정보 렌더링
- [ ] 환자 목록 렌더링
- [ ] 활성 매칭 정보 렌더링

---

## 최종 체크리스트

### Phase 1: 공통 모듈
- [ ] API 호출 함수 작성 (api.ts)
- [ ] TypeScript 타입 정의 (api.ts)
- [ ] 에러 핸들링 컴포넌트 (ErrorAlert.tsx)

### Phase 2: P0 API (보호자 & 환자 등록)
- [ ] matching/page.tsx name 속성 추가
- [ ] guardians/page.tsx API 연동
- [ ] patient-condition-1/page.tsx API 연동
- [ ] patient-condition-2/page.tsx API 연동
- [ ] patient-condition-3/page.tsx API 연동

### Phase 3: P1 API (성향 테스트 & 매칭)
- [ ] personality-test/page.tsx API 연동
- [ ] caregiver-finder/page.tsx API 연동
- [ ] matching/page.tsx 매칭 결과 조회

### Phase 4: P2 API (케어 플랜 & 리뷰)
- [ ] care-plans-create-2/page.tsx API 연동
- [ ] care-plans-create-3/page.tsx 리뷰 API 연동
- [ ] mypage-dashboard/page.tsx API 연동

### 통합 테스트
- [ ] 전체 플로우 테스트 (guardians → patient → matching)
- [ ] 에러 케이스 검증
- [ ] 백엔드와 통합 테스트

---

**작성 완료**
**날짜**: 2025-11-26 (업데이트)
**담당**: 프론트엔드 개발자