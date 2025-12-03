# 늘봄케어 개발자 가이드

**작성일**: 2025-12-03
**버전**: 1.0
**대상**: 신규 개발자, 팀원

---

## 📚 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [개발 환경 설정](#2-개발-환경-설정)
3. [프로젝트 구조](#3-프로젝트-구조)
4. [주요 기술 스택](#4-주요-기술-스택)
5. [개발 워크플로우](#5-개발-워크플로우)
6. [API 통신](#6-api-통신)
7. [상태 관리](#7-상태-관리)
8. [컴포넌트 개발](#8-컴포넌트-개발)
9. [에러 처리](#9-에러-처리)
10. [성능 최적화](#10-성능-최적화)
11. [테스트](#11-테스트)
12. [배포](#12-배포)
13. [문제 해결](#13-문제-해결)

---

## 1. 프로젝트 개요

### 프로젝트 정보
- **이름**: 늘봄케어 (Neulbomcare)
- **목적**: 환자 맞춤형 케어 플랜 생성 및 간병인 매칭 플랫폼
- **기술**: React 19 + Next.js 16 (Frontend), Python FastAPI (Backend)
- **배포**: Azure (Database), Vercel (Frontend), Azure App Service (Backend)

### 주요 기능
1. **케어 플랜 생성**: AI (Azure OpenAI)를 활용한 맞춤형 케어 플랜 생성
2. **간병인 매칭**: XGBoost 모델 기반 최적 간병인 추천
3. **일정 관리**: 케어 로그 기반 일정 추적 및 완료 처리
4. **사용자 관리**: Kakao OAuth 기반 회원가입/로그인

---

## 2. 개발 환경 설정

### 2.1 필수 소프트웨어
- Node.js 20+ (LTS)
- npm 10+ 또는 yarn
- Python 3.10+
- Git

### 2.2 Frontend 설정

```bash
# 1. 저장소 클론
git clone https://github.com/sangwon0707/neulbomcare.git
cd neulbomcare/frontend/my-app

# 2. 의존성 설치
npm install

# 3. 환경 변수 설정
cp .env.example .env.local

# 4. 개발 서버 시작
npm run dev
# http://localhost:3000 에서 접근

# 5. 빌드 (프로덕션)
npm run build
npm run start
```

### 2.3 Backend 설정

```bash
# 1. 저장소 클론 (같은 저장소)
cd ../.. # neulbomcare 루트 디렉토리

# 2. 가상 환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 3. 의존성 설치
cd backend
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env

# 5. 데이터베이스 마이그레이션
alembic upgrade head

# 6. 개발 서버 시작
uvicorn app.main:app --reload
# http://localhost:8000 에서 접근
```

### 2.4 .env.local 설정 (Frontend)

```env
# API 서버
NEXT_PUBLIC_API_URL=http://localhost:8000

# Kakao OAuth (로컬 개발용)
NEXT_PUBLIC_KAKAO_REST_API_KEY=your_kakao_key

# 로깅 레벨 (DEBUG, INFO, WARN, ERROR)
NEXT_PUBLIC_LOG_LEVEL=DEBUG
```

---

## 3. 프로젝트 구조

### Frontend 구조
```
frontend/my-app/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # 홈 페이지
│   │   ├── layout.tsx          # 루트 레이아웃 (AppProvider)
│   │   ├── schedule/page.tsx   # 일정 관리 페이지
│   │   ├── care-plans-create-2/ # 케어 플랜 생성 2단계
│   │   └── care-plans-create-4/ # 케어 플랜 생성 4단계
│   │
│   ├── components/             # 재사용 가능한 컴포넌트
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   └── ...
│   │
│   ├── utils/                  # 유틸리티 함수
│   │   ├── api.ts              # API 통신 (기본 + retry + cache)
│   │   ├── retry.ts            # 재시도 로직
│   │   ├── cache.ts            # 캐싱 유틸리티
│   │   ├── logger.ts           # 로깅 시스템
│   │   ├── monitoring.ts       # 모니터링
│   │   └── ...
│   │
│   ├── types/                  # TypeScript 타입 정의
│   │   ├── api.ts              # API 응답 타입
│   │   ├── guards.ts           # 타입 가드 함수
│   │   └── ...
│   │
│   ├── context/                # React Context
│   │   └── AppContext.tsx      # 전역 상태 관리
│   │
│   ├── styles/                 # CSS
│   │   └── globals.css
│   │
│   └── constants/              # 상수
│       └── ...
│
├── public/                     # 정적 파일
├── next.config.ts            # Next.js 설정 (성능 최적화)
├── tailwind.config.ts         # Tailwind CSS 설정
├── tsconfig.json              # TypeScript 설정
└── package.json
```

### Backend 구조
```
backend/
├── app/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── core/
│   │   ├── config.py           # 환경설정 (Pydantic Settings)
│   │   └── security.py         # JWT 인증
│   │
│   ├── models/                 # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── care_execution.py   # CareLog, Schedule
│   │   └── ...
│   │
│   ├── routes/                 # API 라우트 (Router)
│   │   ├── auth.py             # 인증 API
│   │   ├── patients.py         # 환자 API
│   │   ├── care_plans.py       # 케어 플랜 API
│   │   ├── matching.py         # 간병인 매칭 API
│   │   └── ...
│   │
│   ├── services/               # 비즈니스 로직
│   │   ├── care_plan_generation_service.py  # AI 케어 플랜 생성
│   │   ├── xgboost_matching_service.py      # 간병인 매칭
│   │   └── ...
│   │
│   ├── schemas/                # Pydantic 스키마
│   │   ├── request.py          # 요청 모델
│   │   ├── response.py         # 응답 모델
│   │   └── ...
│   │
│   └── dependencies/           # 의존성 주입
│       └── database.py
│
├── migrations/                 # Alembic DB 마이그레이션
├── .env                        # 환경 변수 (git ignore)
├── .env.example               # 환경 변수 템플릿
├── requirements.txt           # Python 의존성
└── main.py                    # 실행 진입점
```

---

## 4. 주요 기술 스택

### Frontend
- **프레임워크**: React 19
- **번들러**: Next.js 16 (App Router)
- **언어**: TypeScript 5
- **스타일링**: Tailwind CSS 4
- **상태 관리**: React Context + localStorage/sessionStorage
- **애니메이션**: Framer Motion
- **UI 컴포넌트**: Radix UI, Lucide React

### Backend
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **데이터베이스**: PostgreSQL
- **인증**: JWT (PyJWT)
- **AI/ML**: Azure OpenAI API, XGBoost
- **문서 지능**: Azure Document Intelligence

### 배포
- **Frontend**: Vercel (Next.js 최적화)
- **Backend**: Azure App Service
- **데이터베이스**: Azure PostgreSQL
- **CDN**: Vercel Edge Network

---

## 5. 개발 워크플로우

### 5.1 Branch 전략 (Git Flow)

```bash
# Feature branch에서 개발
git checkout -b feature/새-기능-이름

# 개발 완료 후 commit
git add .
git commit -m "feat: 기능 설명"

# Pull Request 생성 (GitHub에서)
# - 코드 리뷰 진행
# - 테스트 통과 확인

# develop 브랜치로 merge
git checkout develop
git pull origin develop
git merge feature/새-기능-이름

# 정리
git branch -d feature/새-기능-이름
```

### 5.2 Commit Message 규칙

```
type(scope): subject

feat(auth): 로그인 기능 추가
fix(schedule): 일정 조회 버그 수정
docs(readme): 설치 가이드 업데이트
style(code): 코드 포매팅
refactor(api): API 통신 레이어 개선
test(schedule): 일정 조회 테스트 추가
chore(deps): 의존성 업그레이드

Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build
```

---

## 6. API 통신

### 6.1 기본 API 함수 사용

```typescript
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api';

// GET 요청
const data = await apiGet<ScheduleResponse>('/api/schedules/2025-12-03');

// POST 요청
const response = await apiPost<CreateResponse>(
    '/api/care-plans',
    {
        patient_id: 1,
        requirements: '...',
    },
    { includeAuth: true } // JWT 토큰 자동 포함
);

// PUT 요청
const updated = await apiPut<UpdateResponse>(
    '/api/care-plans/1',
    { status: 'confirmed' }
);

// DELETE 요청
const deleted = await apiDelete<DeleteResponse>('/api/care-plans/1');
```

### 6.2 재시도 기능이 있는 API

```typescript
import { apiGetWithRetry, apiPostWithRetry } from '@/utils/api';

// 자동 재시도 (최대 3회, exponential backoff)
const data = await apiGetWithRetry<ScheduleResponse>(
    '/api/schedules/2025-12-03',
    { maxRetries: 3, baseDelay: 1000 } // 옵션은 생략 가능
);

// POST with retry
const response = await apiPostWithRetry<CreateResponse>(
    '/api/care-plans',
    { patient_id: 1, ... }
);
```

### 6.3 캐싱이 있는 API

```typescript
import { apiGetCached, invalidateCache } from '@/utils/api';

// 5분 캐싱 (기본 TTL)
const data = await apiGetCached<ScheduleResponse>(
    '/api/schedules/2025-12-03'
);

// 강제 새로고침 (캐시 무시)
const freshData = await apiGetCached<ScheduleResponse>(
    '/api/schedules/2025-12-03',
    { forceRefresh: true }
);

// 특정 패턴의 캐시 무효화
invalidateCache(/^\/api\/schedules\//); // 모든 schedule 캐시 제거
```

### 6.4 API 응답 타입 정의

```typescript
// types/api.ts
export interface ApiResponse<T = any> {
    success?: boolean;
    status?: 'success' | 'error';
    data?: T;
    message?: string;
}

export interface ScheduleResponse {
    patient_id: number;
    date: string;
    care_logs: CareLog[];
}

// 타입 가드 함수
export function validateScheduleResponse(
    response: any
): response is ScheduleResponse {
    return (
        typeof response.patient_id === 'number' &&
        Array.isArray(response.care_logs)
    );
}

// 페이지에서 사용
const response = await apiGet<ScheduleResponse>(url);
if (!validateScheduleResponse(response)) {
    throw new Error('유효하지 않은 응답 형식');
}
```

---

## 7. 상태 관리

### 7.1 React Context (전역 상태)

```typescript
// context/AppContext.tsx에서 사용
import { useAppContext } from '@/context/AppContext';

function MyComponent() {
    // 전체 상태
    const { currentPatient, selectedMatching, carePlan } = useAppContext();

    // 또는 전문화된 hook
    const { currentPatient, setCurrentPatient } = useCurrentPatient();
    const { selectedMatching, setSelectedMatching } = useSelectedMatching();
    const { carePlan, setCarePlan } = useCarePlan();

    return (
        <div>
            {currentPatient?.name}
            {carePlan?.status}
        </div>
    );
}
```

### 7.2 상태 자동 동기화

```typescript
// AppContext는 자동으로 sessionStorage와 동기화됨
const { currentPatient, setCurrentPatient } = useCurrentPatient();

// 상태 변경
setCurrentPatient({
    patient_id: 1,
    name: '김철수',
    age: 65,
    // ...
});

// 자동으로 sessionStorage에 저장됨
// sessionStorage.patient_info = JSON.stringify(...)

// 페이지 새로고침 후에도 유지됨
// AppProvider의 hydration으로 자동 복구
```

### 7.3 로컬 상태 (useState)

```typescript
function MyComponent() {
    // 컴포넌트 내부 상태
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    return (
        <div>
            {isLoading && <Spinner />}
            {error && <ErrorMessage error={error} />}
        </div>
    );
}
```

---

## 8. 컴포넌트 개발

### 8.1 컴포넌트 구조

```typescript
// components/MyComponent.tsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';

interface MyComponentProps {
    title: string;
    onSubmit: (data: any) => void;
    isLoading?: boolean;
}

export function MyComponent({
    title,
    onSubmit,
    isLoading = false,
}: MyComponentProps) {
    const [value, setValue] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({ value });
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>{title}</h2>
            <input
                value={value}
                onChange={(e) => setValue(e.target.value)}
            />
            <Button type="submit" disabled={isLoading}>
                {isLoading ? '로딩중...' : '제출'}
            </Button>
        </form>
    );
}

// 사용
<MyComponent title="양식" onSubmit={handleSubmit} isLoading={false} />
```

### 8.2 동적 컴포넌트 로딩

```typescript
import dynamic from 'next/dynamic';

// 느린 컴포넌트를 별도 번들로 분리
const HeavyChart = dynamic(
    () => import('@/components/HeavyChart'),
    {
        loading: () => <div>그래프 로딩중...</div>,
        ssr: false, // SSR 비활성화 (클라이언트만)
    }
);

export function Dashboard() {
    return (
        <div>
            <h1>대시보드</h1>
            <HeavyChart /> {/* 필요할 때만 로드됨 */}
        </div>
    );
}
```

---

## 9. 에러 처리

### 9.1 API 에러 처리

```typescript
import { logger } from '@/utils/logger';

async function fetchData() {
    try {
        const data = await apiGet<Data>('/api/data');
        return data;
    } catch (error) {
        logger.error('데이터 조회 실패', error, 'MyComponent');

        if (error instanceof Error) {
            if (error.message.includes('타임아웃')) {
                // 타임아웃 처리
                throw new Error('요청이 너무 오래 걸렸습니다. 다시 시도해주세요.');
            }
            if (error.message.includes('401')) {
                // 인증 실패 (자동 로그아웃 처리됨)
                throw new Error('세션이 만료되었습니다.');
            }
        }

        throw error;
    }
}
```

### 9.2 컴포넌트 에러 경계 (Error Boundary)

```typescript
// app/error.tsx (Next.js 13+)
'use client';

import { useEffect } from 'react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error(error);
    }, [error]);

    return (
        <div>
            <h2>오류가 발생했습니다</h2>
            <p>{error.message}</p>
            <button onClick={() => reset()}>다시 시도</button>
        </div>
    );
}
```

### 9.3 로깅

```typescript
import { logger } from '@/utils/logger';

logger.debug('디버그 정보', { key: 'value' }, 'ComponentName');
logger.info('정보', { key: 'value' }, 'ComponentName');
logger.warn('경고', { key: 'value' }, 'ComponentName');
logger.error('에러 발생', error, 'ComponentName');

// 개발자 도구에서 조회
window.__logger.getHistory({ limit: 50 });
window.__logger.getStats();
```

---

## 10. 성능 최적화

### 10.1 메모이제이션

```typescript
import { useMemo, useCallback } from 'react';

function MyComponent({ data }) {
    // 비싼 계산을 메모이제이션
    const processed = useMemo(() => {
        return data.map(item => expensiveCalculation(item));
    }, [data]);

    // 콜백 메모이제이션
    const handleClick = useCallback(() => {
        // 처리
    }, []); // 의존성 배열

    return <div>...</div>;
}
```

### 10.2 이미지 최적화

```typescript
import Image from 'next/image';

// ❌ 피하기
<img src="/profile.jpg" alt="Profile" />

// ✅ 권장
<Image
    src="/profile.jpg"
    alt="Profile"
    width={200}
    height={200}
    priority // 중요한 이미지
    quality={80}
/>
```

### 10.3 캐싱 활용

```typescript
// API 응답 캐싱
const schedule = await apiGetCached<ScheduleResponse>(
    '/api/schedules/2025-12-03'
);

// 캐시 무효화
import { invalidateCache } from '@/utils/api';
invalidateCache(/^\/api\/schedules\//);
```

---

## 11. 테스트

### 11.1 단위 테스트 (Jest)

```typescript
// utils/api.test.ts
import { apiGet } from '@/utils/api';

describe('apiGet', () => {
    it('should fetch data successfully', async () => {
        const data = await apiGet('/api/data');
        expect(data).toBeDefined();
    });

    it('should handle errors', async () => {
        await expect(apiGet('/api/invalid')).rejects.toThrow();
    });
});
```

### 11.2 통합 테스트

```typescript
// __tests__/integration/schedule.test.ts
describe('Schedule Page', () => {
    it('should load and display schedule', async () => {
        const { render, screen } = await import('@testing-library/react');
        // render(SchedulePage);
        // expect(screen.getByText('일정')).toBeInTheDocument();
    });
});
```

---

## 12. 배포

### 12.1 Frontend 배포 (Vercel)

```bash
# 1. 로컬에서 빌드 테스트
npm run build

# 2. Vercel에 연결 (처음 1회)
# - GitHub 저장소 연결
# - 환경 변수 설정

# 3. 자동 배포
# - main 브랜치에 merge 시 자동 배포
# - 또는 manual deploy
```

### 12.2 Backend 배포 (Azure App Service)

```bash
# 1. 로컬에서 테스트
python -m pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Azure에 배포
# - GitHub Actions 또는 수동 배포
# - 환경 변수 설정 (Azure Portal)
```

### 12.3 배포 체크리스트

- [ ] 모든 테스트 통과
- [ ] 코드 리뷰 완료
- [ ] 환경 변수 설정 확인
- [ ] 데이터베이스 마이그레이션 완료
- [ ] 번들 크기 확인 (< 500KB gzip)
- [ ] 성능 메트릭 확인

---

## 13. 문제 해결

### 13.1 자주 발생하는 문제

#### 401 Unauthorized 에러
```typescript
// 문제: JWT 토큰 만료
// 해결: localStorage에서 access_token 제거, 로그인 페이지로 리다이렉트
// (api.ts에서 자동으로 처리됨)

localStorage.removeItem('access_token');
window.location.href = '/login';
```

#### API 응답 타입 에러
```typescript
// 문제: API 응답 구조 불일치
// 해결: 타입 가드 함수 사용

if (!validateScheduleResponse(response)) {
    throw new Error('유효하지 않은 응답 형식');
}
```

#### 번들 크기 증가
```bash
# 해결: 번들 분석
npm run build
# webpack-bundle-analyzer를 사용하여 분석
```

#### 느린 API 응답
```typescript
// 해결: 캐싱 + 재시도
const data = await apiGetWithRetry<Data>(
    '/api/data',
    { maxRetries: 3 }
);
```

### 13.2 디버깅 도구

```javascript
// 브라우저 콘솔에서 (F12)

// 로그 확인
window.__logger.getHistory();

// 모니터링 대시보드
window.__monitoring.getDashboard();

// 캐시 상태
window.__logger.getCacheStatus?.();

// 앱 상태
window.__logger.getStats();
```

---

## 14. 유용한 리소스

- [Next.js 공식 문서](https://nextjs.org/docs)
- [React 공식 문서](https://react.dev)
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

**마지막 수정**: 2025-12-03
**담당자**: 개발팀
