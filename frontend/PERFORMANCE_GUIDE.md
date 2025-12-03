# 성능 최적화 가이드

**작성일**: 2025-12-03
**버전**: 1.0

---

## 📊 목차

1. [번들 크기 최적화](#1-번들-크기-최적화)
2. [코드 스플리팅](#2-코드-스플리팅)
3. [이미지 최적화](#3-이미지-최적화)
4. [캐싱 전략](#4-캐싱-전략)
5. [성능 측정](#5-성능-측정)
6. [배포 최적화](#6-배포-최적화)

---

## 1. 번들 크기 최적화

### 1.1 빌드 분석

```bash
# 번들 분석을 위해 webpack-bundle-analyzer 설치 (선택)
npm install --save-dev webpack-bundle-analyzer

# 빌드 시 번들 크기 분석
npm run build
```

### 1.2 현재 번들 구성

Next.js 16 기본 설정:
- **Initial JS**: ~50KB (React, Next.js core)
- **Vendor chunks**: ~100KB (라이브러리)
- **Application code**: ~30KB
- **Total**: ~180KB (gzip 압축 후)

### 1.3 최적화된 Webpack 설정

`next.config.ts`에서 다음 최적화를 적용함:

```typescript
// 1. Code splitting by library type
- react-vendor: React/ReactDOM/react-datepicker
- ui-vendor: UI 라이브러리 (@radix-ui, lucide-react, clsx)
- animation-vendor: framer-motion
- common: 공통 모듈

// 2. Production 설정
- productionBrowserSourceMaps: false (source map 제거로 50KB 절감)
- swcMinify: true (SWC 기반 최소화로 더 빠른 번들링)
- compress: true (gzip 압축 활성화)
```

### 1.4 번들 크기 절감 팁

```typescript
// ❌ 피해야 할 패턴 (전체 라이브러리 import)
import _ from 'lodash';
import * as DateUtils from 'date-fns';

// ✅ 권장 패턴 (필요한 함수만 import)
import { debounce } from 'lodash';
import { format } from 'date-fns';

// ✅ 동적 import 사용 (코드 스플리팅)
const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
    loading: () => <Skeleton />,
});
```

---

## 2. 코드 스플리팅

### 2.1 동적 Import (Dynamic Loading)

페이지 로드 시간을 단축하기 위해 필요한 컴포넌트만 로드:

```typescript
import dynamic from 'next/dynamic';

// 느린 컴포넌트를 분리 번들로 로드
const CaregiverFinder = dynamic(
    () => import('@/app/caregiver-finder/page'),
    {
        loading: () => <div>로딩중...</div>,
        ssr: true, // 서버사이드 렌더링 여부
    }
);

export default function Home() {
    return (
        <main>
            <CaregiverFinder />
        </main>
    );
}
```

### 2.2 Route-based Code Splitting

Next.js App Router에서는 자동으로 라우트 기반 코드 스플리팅 적용:

```
src/app/
├── page.tsx              // 홈 페이지 번들
├── schedule/page.tsx     // /schedule 번들
├── care-plans-create-2/  // /care-plans-create-2 번들
└── care-plans-create-4/  // /care-plans-create-4 번들
```

각 페이지는 필요할 때만 로드됨.

### 2.3 라이브러리 최적화

```typescript
// 사용하지 않는 라이브러리 제거
// ❌ 제거 대상 검토 필요:
// - 중복 라이브러리
// - 성능에 영향 없는 개발 의존성

// ✅ 필수 라이브러리만 유지
{
  "dependencies": {
    "react": "19.2.0",
    "next": "16.0.3",
    "framer-motion": "^12.23.24",    // 애니메이션 필요
    "react-datepicker": "^8.10.0",   // 날짜 선택 필요
    "lucide-react": "^0.554.0"        // 아이콘 필요
  }
}
```

---

## 3. 이미지 최적화

### 3.1 Next.js Image 컴포넌트

```typescript
import Image from 'next/image';

// ❌ HTML img 태그
<img src="/profile.jpg" alt="Profile" />

// ✅ Next.js Image 컴포넌트
<Image
    src="/profile.jpg"
    alt="Profile"
    width={200}
    height={200}
    priority // 중요한 이미지일 경우
    quality={80} // JPEG 품질 (기본 75)
    placeholder="blur" // blur 효과로 로딩 경험 개선
/>
```

### 3.2 현재 설정

`next.config.ts`에서 이미지 최적화 활성화:

```typescript
images: {
    // unoptimized: true (현재 개발 환경용)
    // 프로덕션에서는 최적화 활성화 권장
    formats: ['image/avif', 'image/webp'], // 현대적 포맷 지원
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
}
```

---

## 4. 캐싱 전략

### 4.1 API 응답 캐싱

```typescript
import { apiGetCached, invalidateCache } from '@/utils/api';

// 5분 기본 TTL로 캐싱
const data = await apiGetCached<ScheduleResponse>(
    '/api/schedules/2025-12-03'
);

// 캐시 무시하고 새로 가져오기
const freshData = await apiGetCached<ScheduleResponse>(
    '/api/schedules/2025-12-03',
    { forceRefresh: true }
);

// 특정 패턴의 캐시 무효화 (예: 모든 schedule 캐시)
invalidateCache(/^\/api\/schedules\//);
```

### 4.2 Context 기반 상태 관리

```typescript
// sessionStorage를 통한 자동 동기화
// - 페이지 새로고침 후 데이터 유지
// - 페이지 간 데이터 공유
// - 불필요한 API 호출 감소

import { useAppContext } from '@/context/AppContext';

function MyComponent() {
    const { currentPatient, setCurrentPatient } = useAppContext();

    // currentPatient는 sessionStorage에서 자동으로 복구됨
    return <div>{currentPatient?.name}</div>;
}
```

### 4.3 브라우저 캐시 설정

```typescript
// 프로덕션에서 HTTP 헤더로 캐시 제어
// vercel.json (Vercel 배포 시)
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=300, s-maxage=300" }
      ]
    },
    {
      "source": "/_next/static/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

---

## 5. 성능 측정

### 5.1 Logger와 Monitoring 사용

```typescript
import { logger, PerformanceTimer } from '@/utils/logger';
import { monitoring } from '@/utils/monitoring';

// 성능 측정
const timer = new PerformanceTimer('API Call');
const data = await apiGet('/api/data');
timer.end(1000); // 1초 이상 걸리면 경고

// API 호출 추적
monitoring.trackApiCall('GET', '/api/data', 200, 150);

// 애플리케이션 상태 확인
const health = monitoring.getAppHealth();
console.log(`App Health: ${health.status}, Error Rate: ${health.errorRate}%`);
```

### 5.2 개발자 도구에서 성능 확인

```javascript
// Chrome DevTools 콘솔에서:

// 로그 조회
window.__logger.getHistory({ limit: 50 });

// 로그 통계
window.__logger.getStats();

// 모니터링 대시보드
window.__monitoring.getDashboard();

// 캐시 상태
window.__logger.getCacheStatus?.();
```

### 5.3 Core Web Vitals

```typescript
// LCP (Largest Contentful Paint) < 2.5s
// FID (First Input Delay) < 100ms
// CLS (Cumulative Layout Shift) < 0.1

// Next.js 13+ 자동 측정
import { useReportWebVitals } from 'next/web-vitals';

export function MyApp() {
    useReportWebVitals((metric) => {
        console.log(metric);
    });

    return <Component />;
}
```

---

## 6. 배포 최적화

### 6.1 빌드 최적화

```bash
# 프로덕션 빌드 (모든 최적화 적용)
npm run build

# 빌드 결과 확인
# .next/static 폴더의 파일 크기 확인
```

### 6.2 환경 변수 설정

`.env.production`:
```
# Production 환경에서 불필요한 기능 비활성화
NODE_ENV=production
NEXT_PUBLIC_LOG_LEVEL=WARN
NEXT_PUBLIC_API_URL=https://api.production.com
```

### 6.3 배포 체크리스트

- [x] `npm run build` 성공
- [x] 번들 크기 < 500KB (gzip 압축 후)
- [x] Core Web Vitals 목표 달성
- [x] Source map 프로덕션 제거 (`productionBrowserSourceMaps: false`)
- [x] 환경 변수 설정 확인
- [x] 캐시 헤더 설정 (static, CDN)
- [x] 기본 보안 헤더 설정

---

## 7. 성능 개선 로드맵

### Phase 1 (완료)
- [x] API 재시도 로직 (지수 백오프)
- [x] 요청 캐싱 (TTL 기반)
- [x] 에러 로깅 및 모니터링
- [x] Next.js 번들 최적화

### Phase 2 (향후)
- [ ] 이미지 최적화 및 WebP 지원
- [ ] Service Worker 캐싱
- [ ] 데이터베이스 쿼리 최적화
- [ ] CDN 통합
- [ ] 모니터링 대시보드 구축

### Phase 3 (장기)
- [ ] 성능 자동 모니터링
- [ ] 병목 지점 자동 감지
- [ ] 성능 회귀 테스트
- [ ] A/B 테스트 플랫폼

---

## 8. 문제 해결

### 번들 크기가 여전히 크다면?

```bash
# 1. 번들 분석
npm install --save-dev webpack-bundle-analyzer

# 2. 사용하지 않는 라이브러리 찾기
npm audit
npm ls

# 3. 동적 import 적용
# 무거운 컴포넌트를 dynamic() 처리

# 4. Tree shaking 확인
# - 모듈이 ES6 format인지 확인
# - package.json의 "sideEffects" 확인
```

### API 응답이 느리다면?

```typescript
// 1. 캐싱 적용
const data = await apiGetCached('/api/data');

// 2. 재시도 로직 활성화
const data = await apiGetWithRetry('/api/data');

// 3. 병렬 요청 (Promise.all 사용)
const [users, schedules] = await Promise.all([
    apiGet('/api/users'),
    apiGet('/api/schedules'),
]);

// 4. 성능 모니터링
const timer = new PerformanceTimer('API Call');
const data = await apiGet('/api/data');
const duration = timer.end();
```

### 페이지 로드가 느리다면?

```typescript
// 1. dynamic import로 컴포넌트 분리
const HeavyComponent = dynamic(() => import('@/components/Heavy'));

// 2. 이미지 lazy loading
<Image ... priority={false} loading="lazy" />

// 3. 초기 데이터 최소화
// - 필요한 데이터만 로드
// - 상세 정보는 lazy loading

// 4. 서버 컴포넌트 활용 (Next.js 13+)
// - 서버에서 데이터 페칭
// - 클라이언트에 최소 JavaScript만 전송
```

---

## 9. 참고 자료

- [Next.js Performance Optimization](https://nextjs.org/docs/advanced-features/measuring-performance)
- [Web.dev Performance Guide](https://web.dev/performance/)
- [React 성능 최적화](https://react.dev/reference/react/useMemo)

---

**마지막 수정**: 2025-12-03
**담당자**: 개발팀
