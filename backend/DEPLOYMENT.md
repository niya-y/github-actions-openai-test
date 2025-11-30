# 🚀 Azure App Service 배포 가이드

## 📋 목차
1. [사전 요구사항](#사전-요구사항)
2. [Azure App Service 생성](#1️⃣-azure-app-service-생성)
3. [환경 변수 설정](#2️⃣-환경-변수-설정)
4. [Startup Command 설정](#3️⃣-startup-command-설정)
5. [GitHub 설정](#4️⃣-github-설정)
6. [배포 실행](#5️⃣-배포-실행)
7. [문제 해결](#🔧-문제-해결)

---

## 사전 요구사항

- ✅ Azure 구독 (무료 체험판 가능)
- ✅ GitHub 계정
- ✅ Azure CLI 설치 (선택사항)

---

## 1️⃣ Azure App Service 생성

### Option A: Azure Portal 사용 (권장)

1. **Azure Portal** 접속: https://portal.azure.com
2. **"리소스 만들기"** → **"웹앱"** 검색
3. 다음 설정으로 생성:

```
기본 사항:
- 구독: 본인의 Azure 구독
- 리소스 그룹: bluedonulab-rg (신규 생성)
- 이름: bluedonulab-api (전역적으로 고유해야 함)
- 게시: 코드
- 런타임 스택: Python 3.12
- 운영 체제: Linux
- 지역: Korea Central (또는 가까운 지역)

App Service 플랜:
- Linux 플랜: bluedonulab-plan (신규 생성)
- 가격 책정 계층: B1 (기본) - 약 ₩15,000/월
  (개발용은 F1 무료 등급 사용 가능)
```

4. **"검토 + 만들기"** → **"만들기"**

### Option B: Azure CLI 사용

```bash
# Azure 로그인
az login

# 리소스 그룹 생성
az group create \
  --name bluedonulab-rg \
  --location koreacentral

# App Service 플랜 생성
az appservice plan create \
  --name bluedonulab-plan \
  --resource-group bluedonulab-rg \
  --sku B1 \
  --is-linux

# Web App 생성
az webapp create \
  --resource-group bluedonulab-rg \
  --plan bluedonulab-plan \
  --name bluedonulab-api \
  --runtime "PYTHON:3.12"
```

---

## 2️⃣ 환경 변수 설정

### Azure Portal에서 설정

1. Azure Portal → **App Service** → **bluedonulab-api** 선택
2. 좌측 메뉴 → **설정** → **구성**
3. **"새 애플리케이션 설정"** 클릭하여 다음 항목 추가:

```bash
DATABASE_URL = postgresql://user:password@server.postgres.database.azure.com:5432/dbname?sslmode=require
SECRET_KEY = your-super-secret-key-change-this
DEBUG = False
KAKAO_REST_API_KEY = your-kakao-rest-api-key
KAKAO_REDIRECT_URI = https://bluedonulab-api.azurewebsites.net/auth/kakao/callback
KAKAO_CLIENT_SECRET = your-kakao-client-secret-if-needed
FRONTEND_URL = https://your-frontend-domain.com
JWT_ALGORITHM = HS256
JWT_EXPIRE_MINUTES = 10080
```

4. **"저장"** 클릭

### Azure CLI로 설정

```bash
az webapp config appsettings set \
  --resource-group bluedonulab-rg \
  --name bluedonulab-api \
  --settings \
    DATABASE_URL="postgresql://..." \
    SECRET_KEY="your-secret-key" \
    DEBUG="False" \
    KAKAO_REST_API_KEY="..." \
    KAKAO_REDIRECT_URI="https://bluedonulab-api.azurewebsites.net/auth/kakao/callback" \
    FRONTEND_URL="https://your-frontend-domain.com"
```

---

## 3️⃣ Startup Command 설정

### Azure Portal에서 설정

1. Azure Portal → **App Service** → **bluedonulab-api**
2. 좌측 메뉴 → **설정** → **구성**
3. **"일반 설정"** 탭 선택
4. **"시작 명령"** 항목에 입력:

```bash
/home/site/wwwroot/startup.sh
```

5. **"저장"** 클릭

### Azure CLI로 설정

```bash
az webapp config set \
  --resource-group bluedonulab-rg \
  --name bluedonulab-api \
  --startup-file "/home/site/wwwroot/startup.sh"
```

---

## 4️⃣ GitHub 설정

### 4.1. Publish Profile 다운로드

1. Azure Portal → **App Service** → **bluedonulab-api**
2. 상단 메뉴 → **게시 프로필 가져오기** 클릭
3. `.PublishSettings` 파일 다운로드

### 4.2. GitHub Secret 등록

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **"New repository secret"** 클릭
3. 다음 Secret 추가:

```
Name: AZURE_PUBLISH_PROFILE
Value: (다운로드한 .PublishSettings 파일의 전체 내용 복사-붙여넣기)
```

### 4.3. GitHub Workflow 확인

다음 파일이 생성되었는지 확인:
- `.github/workflows/deploy-backend.yml` ✅

---

## 5️⃣ 배포 실행

### 방법 1: Git Push로 자동 배포

```bash
cd /Users/sangwon/Project/Sesac_class/bluedonulab-01

# 변경사항 확인
git status

# 모든 변경사항 커밋
git add backend/ .github/
git commit -m "feat: Add Azure App Service deployment configuration"

# main 브랜치에 푸시 (자동 배포 시작)
git push origin main
```

### 방법 2: 수동 Workflow 실행

1. GitHub 저장소 → **Actions** 탭
2. 좌측 메뉴 → **"Deploy Backend to Azure App Service"** 선택
3. **"Run workflow"** → **"Run workflow"** 클릭

### 배포 진행 상황 확인

1. GitHub → **Actions** 탭에서 실시간 로그 확인
2. Azure Portal → **App Service** → **배포 센터**에서도 확인 가능

---

## 6️⃣ 배포 확인

### 배포 완료 후 테스트

```bash
# 1. Root 엔드포인트
curl https://bluedonulab-api.azurewebsites.net/

# 2. Health Check
curl https://bluedonulab-api.azurewebsites.net/health

# 3. API Docs (Swagger UI)
# 브라우저에서 열기:
https://bluedonulab-api.azurewebsites.net/docs
```

### 로그 확인

```bash
# Azure CLI로 실시간 로그 스트리밍
az webapp log tail \
  --resource-group bluedonulab-rg \
  --name bluedonulab-api
```

또는 **Azure Portal**:
- App Service → **모니터링** → **로그 스트림**

---

## 🔧 문제 해결

### 문제 1: uvicorn이 인식되지 않음

**증상:**
```
bash: uvicorn: command not found
```

**해결책:**
1. `requirements.txt`에 `uvicorn[standard]==0.24.0`과 `gunicorn==21.2.0` 확인
2. `startup.sh`가 제대로 설정되었는지 확인
3. Azure Portal → **구성** → **일반 설정** → **시작 명령** 확인:
   ```
   /home/site/wwwroot/startup.sh
   ```

### 문제 2: 데이터베이스 연결 실패

**증상:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결책:**
1. Azure Portal → **구성** → **애플리케이션 설정**에서 `DATABASE_URL` 확인
2. PostgreSQL에서 Azure App Service IP 방화벽 규칙 추가:
   - Azure PostgreSQL → **연결 보안** → **방화벽 규칙** → **Azure 서비스 방문 허용** 체크

### 문제 3: Cold Start (느린 첫 요청)

**증상:** 첫 번째 요청이 30초 이상 걸림

**해결책:**
1. **Always On** 기능 활성화 (B1 이상 플랜 필요):
   - Azure Portal → **구성** → **일반 설정** → **Always On: 켜기**
2. 또는 Health Check 엔드포인트 설정:
   - **상태 확인** → **상태 확인 사용: 예** → 경로: `/health`

### 문제 4: GitHub Actions 실패

**증상:** Deployment 단계에서 실패

**해결책:**
1. GitHub Secret `AZURE_PUBLISH_PROFILE`이 올바른지 확인
2. Azure에서 Publish Profile 재다운로드 후 업데이트
3. `.github/workflows/deploy-backend.yml`의 `AZURE_WEBAPP_NAME` 확인

### 문제 5: Oryx 빌드 실패

**증상:**
```
Error: Failed to build the app
```

**해결책:**
1. `runtime.txt`와 `.python-version` 파일 확인
2. `requirements.txt` 문법 오류 확인:
   ```bash
   pip install -r requirements.txt  # 로컬에서 테스트
   ```
3. Azure Portal → **배포 센터** → **로그**에서 상세 오류 확인

---

## 📚 참고 자료

- [Azure App Service for Python](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Oryx Build System](https://github.com/microsoft/Oryx)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

---

## ✅ 체크리스트

배포 전 확인:
- [ ] Azure App Service 생성 완료
- [ ] 모든 환경 변수 설정 완료
- [ ] Startup command 설정 완료
- [ ] GitHub Secret 등록 완료
- [ ] `runtime.txt` 파일 생성
- [ ] `.python-version` 파일 생성
- [ ] `startup.sh` 실행 권한 확인
- [ ] `requirements.txt`에 gunicorn, uvicorn 포함
- [ ] `.gitignore`에 `.env`, `.venv` 포함
- [ ] Git에 커밋 및 푸시

배포 후 확인:
- [ ] GitHub Actions 빌드 성공
- [ ] Health endpoint 응답 확인
- [ ] API Docs 접근 가능
- [ ] 데이터베이스 연결 확인
- [ ] 로그 스트림 정상 작동

---

**마지막 업데이트:** 2025-01-25
