# 늘봄케어 운영 가이드

**작성일**: 2025-12-03
**버전**: 1.0
**대상**: DevOps, 운영팀, 시스템 관리자

---

## 📚 목차

1. [배포 절차](#1-배포-절차)
2. [환경별 설정](#2-환경별-설정)
3. [모니터링](#3-모니터링)
4. [로깅](#4-로깅)
5. [문제 해결](#5-문제-해결)
6. [백업 및 복구](#6-백업-및-복구)
7. [보안](#7-보안)
8. [성능 튜닝](#8-성능-튜닝)
9. [운영 체크리스트](#9-운영-체크리스트)

---

## 1. 배포 절차

### 1.1 Frontend 배포 (Vercel)

#### 자동 배포 설정

1. **GitHub 연동**
   ```
   Repository: https://github.com/sangwon0707/neulbomcare
   Branch: main (프로덕션), develop (스테이징)
   ```

2. **배포 트리거**
   - `main` 브랜치에 push → 프로덕션 배포
   - `develop` 브랜치에 push → 스테이징 배포

3. **배포 확인**
   ```
   Vercel Dashboard > Deployments
   - Status: Ready (성공) / Error (실패)
   - URL: https://neulbomcare.vercel.app
   ```

#### 수동 배포

```bash
# 1. 로컬에서 빌드 검증
npm run build

# 2. Vercel CLI로 배포
npm i -g vercel
vercel --prod

# 3. 배포 확인
vercel ls
```

#### 배포 설정 (vercel.json)

```json
{
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": {
      "production": "https://api.production.com",
      "preview": "https://api.staging.com"
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=300, s-maxage=300"
        }
      ]
    }
  ]
}
```

### 1.2 Backend 배포 (Azure App Service)

#### 배포 방법 선택

**방법 1: GitHub Actions (권장)**

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to Azure

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run tests
        run: |
          pytest backend/tests

      - name: Deploy to Azure
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'neulbomcare-api'
          slot-name: 'production'
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
```

**방법 2: Azure CLI (수동)**

```bash
# 1. Azure에 로그인
az login

# 2. 리소스 그룹 확인
az group list

# 3. App Service에 배포
az webapp up \
  --resource-group neulbomcare-rg \
  --name neulbomcare-api \
  --runtime "PYTHON|3.10"

# 4. 환경 변수 설정
az webapp config appsettings set \
  --resource-group neulbomcare-rg \
  --name neulbomcare-api \
  --settings \
    DATABASE_URL="postgresql://..." \
    AZURE_OPENAI_API_KEY="..." \
    SECRET_KEY="..."
```

#### 배포 확인

```bash
# Azure Portal
# App Service > Overview > Default domain 확인
# https://neulbomcare-api.azurewebsites.net

# 또는 CLI로 확인
az webapp show \
  --resource-group neulbomcare-rg \
  --name neulbomcare-api \
  --query defaultHostName
```

### 1.3 데이터베이스 마이그레이션

#### 스테이징 환경에서 먼저 테스트

```bash
# 1. 현재 상태 확인
alembic current

# 2. 마이그레이션 상태 확인
alembic history

# 3. 스테이징에서 마이그레이션 실행
alembic upgrade head

# 4. 결과 검증
# - 쿼리 성능 테스트
# - 데이터 무결성 확인
```

#### 프로덕션 마이그레이션

```bash
# 1. 백업 생성
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 마이그레이션 실행 (오프 타임 스케줄)
alembic upgrade head

# 3. 롤백 계획 준비
# - 이전 버전 마이그레이션 스크립트 확보
# - 롤백 절차 문서화
```

---

## 2. 환경별 설정

### 2.1 개발 환경 (.env.development)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/neulbomcare_dev

# Application
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Azure OpenAI
AZURE_OPENAI_API_KEY=dev-key
AZURE_OPENAI_ENDPOINT=https://dev-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=dev-deployment
AZURE_OPENAI_TIMEOUT=30

# XGBoost
XGBOOST_MODEL_PATH=./models/xgboost_model.pkl
XGBOOST_MODEL_FALLBACK=True

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# Features
ENABLE_AI_CARE_PLAN=True
ENABLE_MATCHING_ALGORITHM=True
```

### 2.2 스테이징 환경 (.env.staging)

```env
# Database (Azure PostgreSQL)
DATABASE_URL=postgresql://admin@staging-server:password@staging-server.postgres.database.azure.com:5432/neulbomcare?sslmode=require

# Application
DEBUG=False
SECRET_KEY=staging-secret-key-change-in-production

# Azure OpenAI (Staging 배포)
AZURE_OPENAI_API_KEY=staging-key
AZURE_OPENAI_ENDPOINT=https://staging-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=staging-deployment
AZURE_OPENAI_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/neulbomcare/app.log

# Features
ENABLE_AI_CARE_PLAN=True
ENABLE_MATCHING_ALGORITHM=True
```

### 2.3 프로덕션 환경 (.env.production)

```env
# Database (Azure PostgreSQL - 높은 가용성)
DATABASE_URL=postgresql://admin@prod-server:password@prod-server.postgres.database.azure.com:5432/neulbomcare?sslmode=require&connect_timeout=10

# Application
DEBUG=False
SECRET_KEY=production-secret-key-must-be-secure-random

# Azure OpenAI (Production 배포)
AZURE_OPENAI_API_KEY=prod-key-from-vault
AZURE_OPENAI_ENDPOINT=https://prod-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=prod-deployment
AZURE_OPENAI_TIMEOUT=45

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/neulbomcare/app.log

# Security
CORS_ALLOWED_ORIGINS=https://neulbomcare.com,https://www.neulbomcare.com
ALLOWED_HOSTS=neulbomcare.azurewebsites.net

# Features
ENABLE_AI_CARE_PLAN=True
ENABLE_MATCHING_ALGORITHM=True
```

### 2.4 Azure Key Vault 사용 (권장)

```bash
# 1. Key Vault 생성
az keyvault create \
  --name neulbomcare-kv \
  --resource-group neulbomcare-rg

# 2. 시크릿 저장
az keyvault secret set \
  --vault-name neulbomcare-kv \
  --name DatabaseURL \
  --value "postgresql://..."

az keyvault secret set \
  --vault-name neulbomcare-kv \
  --name AzureOpenaiKey \
  --value "..."

# 3. App Service에서 Key Vault 참조
az webapp config appsettings set \
  --name neulbomcare-api \
  --resource-group neulbomcare-rg \
  --settings DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://neulbomcare-kv.vault.azure.net/secrets/DatabaseURL/)"
```

---

## 3. 모니터링

### 3.1 Frontend 모니터링 (Vercel Analytics)

```
Vercel Dashboard > Analytics
- Page performance
- Web Vitals (LCP, FID, CLS)
- Real User Monitoring (RUM)
```

### 3.2 Backend 모니터링 (Application Insights)

```python
# backend/app/core/telemetry.py
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Application Insights 설정
configure_azure_monitor()
tracer = trace.get_tracer(__name__)

# 사용 예
@app.get("/api/data")
async def get_data():
    with tracer.start_as_current_span("fetch_data") as span:
        # 요청 처리
        pass
```

### 3.3 로그 모니터링

```bash
# 1. 로그 조회
# Azure Portal > App Service > Log stream

# 2. 로그 검색
# Application Insights > Logs (KQL)
customMetrics
| where name == "api_request_duration"
| summarize avg(value) by bin(timestamp, 5m)

# 3. 알림 설정
# Application Insights > Alerts > New alert rule
```

### 3.4 Health Check 설정

```python
# backend/app/routes/health.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Azure App Service > Health check
# Path: /health
# Interval: 60 seconds
```

---

## 4. 로깅

### 4.1 로그 레벨 설정

```python
# backend/app/core/logger.py
import logging

logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 4.2 구조화된 로깅

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# 사용
logger.info("user_login", user_id=123, ip="192.168.1.1")
```

### 4.3 로그 저장소

```
- Development: 파일 (logs/app.log)
- Staging: Azure Monitor (Application Insights)
- Production: Azure Monitor + Long-term storage
```

---

## 5. 문제 해결

### 5.1 API가 응답하지 않음

```bash
# 1. 서비스 상태 확인
az webapp show --name neulbomcare-api --resource-group neulbomcare-rg

# 2. 로그 확인
az webapp log tail --name neulbomcare-api --resource-group neulbomcare-rg

# 3. 재시작
az webapp restart --name neulbomcare-api --resource-group neulbomcare-rg

# 4. 상태 확인
curl https://neulbomcare-api.azurewebsites.net/health
```

### 5.2 데이터베이스 연결 실패

```bash
# 1. 연결 문자열 확인
echo $DATABASE_URL

# 2. 연결 테스트
psql -d "$DATABASE_URL" -c "SELECT 1"

# 3. 방화벽 규칙 확인
# Azure Portal > Azure Database for PostgreSQL > Connection security
# - Allow Azure services: ON
# - Client IP: 확인 및 추가

# 4. 연결 풀 확인
# Django/FastAPI 연결 풀 설정 검토
```

### 5.3 높은 응답 시간

```bash
# 1. 느린 쿼리 로그 확인
SHOW slow_query_log;
SET SESSION long_query_time = 2;

# 2. 인덱스 확인
EXPLAIN ANALYZE SELECT ...;

# 3. 캐싱 활성화 확인
# Redis 연결 테스트
redis-cli ping

# 4. 데이터베이스 통계 업데이트
ANALYZE;
```

### 5.4 메모리 부족

```bash
# 1. 메모리 사용률 확인
az metrics list-definitions --resource neulbomcare-api --resource-group neulbomcare-rg

# 2. 메모리 누수 검사
# - Python: memory_profiler
# - Node.js: clinic.js

# 3. 스케일링
# App Service Plan 크기 조정
az appservice plan update --name neulbomcare-plan --sku P1V2
```

---

## 6. 백업 및 복구

### 6.1 데이터베이스 백업

```bash
# 수동 백업
pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# 자동 백업 (Azure)
# Azure Portal > Azure Database for PostgreSQL > Backup
# - Backup retention period: 35 days (기본값)
# - Geo-redundant backup: Enabled

# 백업 복구
gunzip < backup_20251203_120000.sql.gz | psql $DATABASE_URL
```

### 6.2 애플리케이션 복구

```bash
# 1. 이전 배포로 롤백 (Vercel)
# Vercel Dashboard > Deployments > 이전 배포 선택 > Promote

# 2. 환경 변수 확인
# Vercel > Project Settings > Environment Variables

# 3. 재배포
vercel --prod
```

### 6.3 재해 복구 계획 (DR)

**RTO (Recovery Time Objective)**: 1시간
**RPO (Recovery Point Objective)**: 15분

```
1. 모니터링 경고 발생
   ↓
2. 문제 진단 (10분)
   ↓
3. 롤백 결정
   ↓
4. 이전 버전 배포 (15분)
   ↓
5. 검증 (10분)
   ↓
6. 복구 완료
```

---

## 7. 보안

### 7.1 의존성 취약점 스캔

```bash
# Frontend
npm audit
npm audit fix

# Backend
pip install --upgrade pip
pip install safety
safety check

# 또는 Dependabot (GitHub에서 자동)
```

### 7.2 환경 변수 보안

```bash
# ❌ 피하기
# - 환경 변수를 코드에 커밋
# - 개발 환경 키를 프로덕션에서 사용

# ✅ 권장
# - .env 파일은 .gitignore에 추가
# - Key Vault 사용
# - 정기적인 키 로테이션

# 키 로테이션
az keyvault secret set \
  --vault-name neulbomcare-kv \
  --name AzureOpenaiKey \
  --value "new-key"
```

### 7.3 CORS 설정

```python
# backend/app/core/config.py
CORS_ALLOWED_ORIGINS = [
    "https://neulbomcare.com",
    "https://www.neulbomcare.com",
]

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7.4 SSL/TLS 인증서

```bash
# Azure App Service (자동 관리)
# - Microsoft 인증서 (기본): *.azurewebsites.net
# - 커스텀 도메인: HTTPS 자동 설정

# 인증서 갱신 확인
# Azure Portal > App Service > Custom domains
```

---

## 8. 성능 튜닝

### 8.1 데이터베이스 최적화

```sql
-- 인덱스 생성
CREATE INDEX idx_patient_id ON care_logs(patient_id);
CREATE INDEX idx_schedule_date ON schedules(schedule_date);

-- 쿼리 성능 분석
EXPLAIN ANALYZE SELECT * FROM care_logs WHERE patient_id = 1;

-- 통계 업데이트
ANALYZE;
```

### 8.2 API 성능 최적화

```python
# FastAPI response caching
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/api/schedules/{date}")
@cached(expire=300)  # 5분 캐싱
async def get_schedules(date: str):
    return {...}
```

### 8.3 리소스 스케일링

```bash
# 1. 현재 리소스 확인
az appservice plan show --name neulbomcare-plan --resource-group neulbomcare-rg

# 2. SKU 업그레이드
# S1 → P1V2 (Production 권장)
az appservice plan update --name neulbomcare-plan --sku P1V2

# 3. 자동 스케일링 설정
az monitor autoscale create \
  --resource-group neulbomcare-rg \
  --resource neulbomcare-api \
  --resource-type "Microsoft.Web/serverFarms" \
  --min-count 2 \
  --max-count 10
```

---

## 9. 운영 체크리스트

### 일일 (Daily)

- [ ] 서비스 상태 확인
  ```bash
  curl -I https://neulbomcare.azurewebsites.net/health
  ```
- [ ] 에러율 확인 (< 1%)
- [ ] 평균 응답 시간 (< 500ms)
- [ ] 로그 검토 (에러 메시지)

### 주간 (Weekly)

- [ ] 의존성 취약점 스캔 (`npm audit`, `safety check`)
- [ ] 성능 메트릭 분석
- [ ] 백업 상태 확인
- [ ] 용량 모니터링 (디스크, 메모리)

### 월간 (Monthly)

- [ ] 보안 업데이트 검토
- [ ] 데이터베이스 유지보수
  ```sql
  VACUUM ANALYZE;
  ```
- [ ] 성능 최적화 검토
- [ ] 비용 분석
- [ ] 장애 발생 기록 검토

### 분기별 (Quarterly)

- [ ] 재해 복구 드릴
- [ ] 보안 감사
- [ ] 용량 계획 검토
- [ ] 버전 업그레이드 계획

### 연간 (Annually)

- [ ] 아키텍처 리뷰
- [ ] 비용 최적화 분석
- [ ] 규정 준수 확인
- [ ] 장기 로드맵 검토

---

## 10. 연락처 및 응급 절차

### 긴급 상황 연락처
- **CTO**: [연락처]
- **DevOps 담당자**: [연락처]
- **데이터베이스 관리자**: [연락처]

### 긴급 대응 절차
1. 문제 감지 (모니터링 알림)
2. 담당자에게 알림
3. 근본 원인 분석
4. 임시 해결책 실행
5. 영구 해결책 구현
6. 사후 분석 (Postmortem)

---

**마지막 수정**: 2025-12-03
**담당자**: DevOps 팀
