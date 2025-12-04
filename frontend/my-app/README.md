# 늘봄케어 프론트엔드

Next.js 16.0.3 기반 AI 간병인 매칭 플랫폼 프론트엔드

## 기술 스택

- **Next.js 16.0.3** - React 기반 풀스택 프레임워크
- **React 19.2.0** - 최신 React with Server Components
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 유틸리티 기반 스타일링
- **Lucide React** - 아이콘 라이브러리
- **jsPDF** - PDF 생성

## 시작하기

### 의존성 설치

```bash
npm install
```

### 개발 서버 실행

```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)를 열어 결과를 확인하세요.

### 프로덕션 빌드

```bash
# Next.js 16에서 webpack 설정을 사용한 빌드
npm run build -- --webpack

# 빌드된 앱 실행
npm run start
```

## ⚠️ 중요: Next.js 16 빌드 관련

이 프로젝트는 **Next.js 16.0.3**을 사용하며, `next.config.ts`에 webpack 최적화 설정이 포함되어 있습니다.

### 빌드 시 주의사항

Next.js 16은 기본적으로 **Turbopack**을 사용하지만, 이 프로젝트는 webpack 설정을 사용합니다.
따라서 빌드 시 반드시 `--webpack` 플래그를 사용해야 합니다:

```bash
npm run build -- --webpack
```

플래그 없이 빌드하면 다음 에러가 발생합니다:
```
This build is using Turbopack, with a `webpack` config and no `turbopack` config
```

### package.json 빌드 스크립트 업데이트 (선택사항)

매번 플래그를 입력하기 번거롭다면, `package.json`의 빌드 스크립트를 수정할 수 있습니다:

```json
{
  "scripts": {
    "build": "next build --webpack"
  }
}
```

## 프로젝트 구조

```
src/
├── app/              # Next.js App Router 페이지
├── components/       # 재사용 가능한 React 컴포넌트
├── context/         # React Context (전역 상태 관리)
├── types/           # TypeScript 타입 정의
└── utils/           # 유틸리티 함수
```

## 주요 기능

- AI 기반 간병인 매칭
- 실시간 케어 플랜 생성
- 약물 관리 (OCR 포함)
- 간병 일정 관리
- 가족 공유 대시보드
- PDF 보고서 생성

## 환경 변수

프로젝트 루트에 `.env.local` 파일을 생성하고 다음 변수를 설정하세요:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 더 알아보기

- [Next.js Documentation](https://nextjs.org/docs)
- [프로젝트 메인 README](../../README.md) - 전체 프로젝트 설명 및 아키텍처
