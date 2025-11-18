"""
BluedonuLab Caregiver Matching System
Main FastAPI Application
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# 모듈 임포트
from database.connection import init_database, DatabaseConnection
from api import personality_routes, matching_routes, report_routes

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="BluedonuLab Caregiver Matching System API",
    description="성향 기반 간병인 매칭 시스템 - 환자와 최적의 간병인을 연결하는 AI 기반 플랫폼",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# =====================================================================
# CORS 설정 (프론트엔드 크로스 도메인 요청 허용)
# =====================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션 환경에서는 특정 도메인만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 정적 파일 마운트 (Google Stitch 생성 UI)
# =====================================================================

page_design_path = Path(__file__).parent / "page_design"
if page_design_path.exists():
    try:
        app.mount("/ui", StaticFiles(directory=str(page_design_path)), name="ui")
        logger.info("✅ UI 페이지 마운트 완료: /ui")
    except Exception as e:
        logger.warning(f"⚠️ UI 페이지 마운트 실패: {e}")

# =====================================================================
# API 라우터 등록
# =====================================================================

# 성향 관련 API
app.include_router(personality_routes.router)

# 매칭 관련 API
app.include_router(matching_routes.router)

# 리포트 관련 API
app.include_router(report_routes.router)

# =====================================================================
# 라우트 핸들러
# =====================================================================


@app.get("/")
async def root():
    """
    루트 엔드포인트 - 기본 정보 반환
    """
    return {
        "name": "BluedonuLab Caregiver Matching System",
        "version": "1.0.0",
        "description": "성향 기반 간병인 매칭 시스템",
        "documentation": {
            "swagger_ui": "/api/docs",
            "redoc": "/api/redoc",
            "openapi_schema": "/api/openapi.json"
        },
        "api_endpoints": {
            "personality": "/api/personality",
            "matching": "/api/matching",
            "report": "/api/report"
        },
        "ui": "/ui"
    }


@app.get("/api")
async def api_root():
    """
    API 루트 엔드포인트
    """
    return {
        "message": "BluedonuLab API에 오신 것을 환영합니다",
        "version": "1.0.0",
        "available_endpoints": {
            "personality": {
                "save_test": "POST /api/personality/test",
                "get_personality": "GET /api/personality/{patient_id}",
                "list_all": "GET /api/personality/list/all",
                "get_stats": "GET /api/personality/stats/summary"
            },
            "matching": {
                "recommend": "GET /api/matching/recommend/{patient_id}",
                "create": "POST /api/matching/create",
                "history": "GET /api/matching/history/{patient_id}",
                "cancel": "DELETE /api/matching/{matching_id}",
                "performance": "GET /api/matching/performance/evaluate"
            },
            "report": {
                "daily": "POST /api/report/daily",
                "weekly": "GET /api/report/weekly/{patient_id}",
                "monthly": "GET /api/report/monthly/performance",
                "health": "GET /api/report/health"
            }
        }
    }


@app.get("/health")
async def health_check():
    """
    서버 헬스 체크 엔드포인트
    """
    try:
        # 데이터베이스 연결 확인
        db_health = DatabaseConnection.health_check()

        return {
            "status": "healthy",
            "service": "BluedonuLab API",
            "version": "1.0.0",
            "database": "healthy" if db_health else "unhealthy"
        }
    except Exception as e:
        logger.error(f"❌ 헬스 체크 실패: {e}")
        return {
            "status": "unhealthy",
            "service": "BluedonuLab API",
            "error": str(e)
        }


@app.get("/api/status")
async def api_status():
    """
    API 상태 조회
    """
    try:
        db_health = DatabaseConnection.health_check()

        return {
            "api": {
                "name": "BluedonuLab Caregiver Matching System API",
                "version": "1.0.0",
                "status": "running",
                "uptime": "active"
            },
            "database": {
                "type": "SQLite",
                "status": "connected" if db_health else "disconnected",
                "path": "data/carehome.db"
            },
            "features": {
                "personality_matching": "enabled",
                "caregiver_recommendation": "enabled",
                "daily_reporting": "enabled",
                "performance_analytics": "enabled"
            }
        }
    except Exception as e:
        logger.error(f"❌ 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# 에러 핸들러
# =====================================================================


@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    """
    404 Not Found 에러 핸들러
    """
    return {
        "error": "Not Found",
        "message": f"요청하신 엔드포인트를 찾을 수 없습니다: {request.url.path}",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_error_exception_handler(request, exc):
    """
    500 Internal Server Error 에러 핸들러
    """
    logger.error(f"❌ 서버 오류: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "서버에서 오류가 발생했습니다",
        "status_code": 500
    }


# =====================================================================
# 애플리케이션 초기화
# =====================================================================


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트
    """
    logger.info("🚀 BluedonuLab API 서버 시작...")

    try:
        # 데이터베이스 초기화
        db_result = init_database(reset=False)

        if db_result:
            logger.info("✅ 데이터베이스 초기화 완료")
        else:
            logger.warning("⚠️ 데이터베이스 초기화 경고")

        logger.info("✅ 애플리케이션 시작 완료")
        logger.info("📚 API 문서: http://localhost:8000/api/docs")
        logger.info("🎨 UI 페이지: http://localhost:8000/ui")

    except Exception as e:
        logger.error(f"❌ 애플리케이션 시작 실패: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트
    """
    logger.info("🛑 BluedonuLab API 서버 종료...")

    try:
        DatabaseConnection.close()
        logger.info("✅ 데이터베이스 연결 종료")
    except Exception as e:
        logger.error(f"⚠️ 종료 중 오류: {e}")


# =====================================================================
# 메인 실행
# =====================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 FastAPI 서버 실행 중...")
    logger.info("📍 주소: http://localhost:8000")
    logger.info("📚 API 문서: http://localhost:8000/api/docs")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
