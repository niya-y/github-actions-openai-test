from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import engine, Base
from app.routes import auth, profile, matching, care_execution, review, guardians, patients, dashboard, xgboost_matching, personality, care_plans, ocr, meal_plans, care_reports

settings = get_settings()

app = FastAPI(
    title="BluedonuLab API",
    description="환자-간병인 매칭 시스템 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:4000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4000",
        "https://happy-hill-0c145d200.3.azurestaticapps.net",
        "https://nbcare.vercel.app",
        "https://neulbomcare-web.purplecliff-dc92193b.koreacentral.azurecontainerapps.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(profile.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(care_execution.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(personality.router, prefix="/api")
# 새로운 프론트엔드 API 라우터
app.include_router(guardians.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(dashboard.router)
# XGBoost 매칭 API 라우터
app.include_router(xgboost_matching.router)
# 케어 플랜 생성 API 라우터
app.include_router(care_plans.router)
# OCR 라우터 (약봉지 인식)
app.include_router(ocr.router, prefix="/api", tags=["OCR"])
# 식단 추천 API 라우터
app.include_router(meal_plans.router)
# 케어 보고서 PDF 생성 API 라우터
app.include_router(care_reports.router)


# @app.on_event("startup")
# def startup_event():
#     """애플리케이션 시작 시 데이터베이스 테이블 생성"""
#     Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "BluedonuLab API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
