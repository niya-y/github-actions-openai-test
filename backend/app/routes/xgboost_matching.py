"""
XGBoost 기반 매칭 API 라우트

P11 (간병인 찾기) → P12 (로딩) → P13 (결과 리스트)의 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, date
import logging
import re

from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.enhanced_matching_service import EnhancedMatchingService
from app.services.xgboost_matching_service import XGBoostMatchingService
from app.dependencies.database import get_db
from app.models.profile import Caregiver
from app.models.user import User
from app.models.care_details import CaregiverPersonality
from app.models.matching import MatchingRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Care type to certification mapping
CARE_TYPE_TO_CERTIFICATION = {
    'nursing-aide': '요양보호사',      # matches 요양보호사 1급, 요양보호사 2급, etc.
    'nursing-assistant': '간호조무사',  # matches 간호조무사
    'nurse': '간호사'                  # matches 간호사
}


def extract_matching_job_title(certifications: str, cert_keyword: str) -> str:
    """
    자격증 문자열에서 매칭되는 직업을 추출합니다.
    예: "요양보호사 1급|물리치료사" + "요양보호사" → "요양보호사 1급"
    """
    if not certifications:
        return "케어기버"

    # 파이프로 구분된 각 자격증을 확인
    for cert in certifications.split('|'):
        cert = cert.strip()
        if cert_keyword in cert:
            return cert

    return "케어기버"

# Router 생성
router = APIRouter(prefix="/api/matching", tags=["matching"])


# ============================================================================
# Pydantic 스키마
# ============================================================================

class PersonalityScores(BaseModel):
    """성격 점수 스키마"""
    empathy_score: float = Field(..., ge=0, le=100, description="공감도 (0-100)")
    activity_score: float = Field(..., ge=0, le=100, description="활동성 (0-100)")
    patience_score: float = Field(..., ge=0, le=100, description="인내심 (0-100)")
    independence_score: float = Field(..., ge=0, le=100, description="자립성 (0-100)")


class MatchingRequirements(BaseModel):
    """매칭 요구사항"""
    care_type: str = Field(..., description="간병 유형: time, live-in")
    time_slots: Optional[List[str]] = Field(None, description="선호 시간대")
    gender: Optional[str] = Field(None, description="선호 성별")
    experience: Optional[str] = Field(None, description="경력 요구사항")
    skills: Optional[List[str]] = Field(None, description="필요 스킬")


class XGBoostMatchingRequest(BaseModel):
    """XGBoost 기반 매칭 요청"""
    patient_id: int = Field(..., description="환자 ID")
    patient_personality: PersonalityScores = Field(..., description="환자 성격 정보")
    requirements: Optional[MatchingRequirements] = Field(None, description="매칭 요구사항")
    preferred_days: List[str] = Field(..., description="선호하는 요일 (예: ['Monday', 'Tuesday'])")
    preferred_time_slots: List[str] = Field(..., description="선호하는 시간대 (예: ['morning', 'afternoon'])")
    care_start_date: Optional[date] = Field(None, description="간병 시작 날짜 (YYYY-MM-DD)")
    care_end_date: Optional[date] = Field(None, description="간병 종료 날짜 (YYYY-MM-DD)")
    top_k: int = Field(5, ge=1, le=20, description="반환할 최대 간병인 수")

    @validator('care_end_date')
    def validate_care_dates(cls, v, values):
        """간병 시작일이 종료일보다 이전인지 확인"""
        if 'care_start_date' in values and values['care_start_date'] and v:
            if values['care_start_date'] >= v:
                raise ValueError('care_start_date must be before care_end_date')
        return v


class CaregiverMatchResult(BaseModel):
    """간병인 매칭 결과"""
    caregiver_id: int
    caregiver_name: str
    job_title: str
    grade: str = Field(..., description="등급 (A, B, C)")
    match_score: float = Field(..., description="호환도 점수 (0-100)")
    experience_years: int
    hourly_rate: float
    avg_rating: float
    profile_image_url: str
    personality_analysis: str
    specialties: List[str] = []
    availability: List[str] = []


class XGBoostMatchingResponse(BaseModel):
    """XGBoost 매칭 응답"""
    patient_id: int
    total_matches: int
    matches: List[CaregiverMatchResult]
    algorithm_version: str = "XGBoost_v3"
    timestamp: datetime


# ============================================================================
# 엔드포인트
# ============================================================================

@router.post("/recommend-xgboost", response_model=XGBoostMatchingResponse)
async def recommend_caregivers_xgboost(
    request: XGBoostMatchingRequest,
    db: Session = Depends(get_db),
):
    """
    XGBoost 기반 간병인 추천 - 실제 데이터베이스 기반

    ## 요청 예제
    ```json
    {
        "patient_id": 1,
        "patient_personality": {
            "empathy_score": 75,
            "activity_score": 55,
            "patience_score": 80,
            "independence_score": 45
        },
        "requirements": {
            "care_type": "time",
            "time_slots": ["morning", "afternoon"],
            "gender": "Female",
            "experience": "3-5",
            "skills": ["wound_care"]
        },
        "top_k": 5
    }
    ```
    """

    try:
        logger.info(f"[XGBoost 추천] 환자 {request.patient_id} 매칭 요청 - 돌봄유형: {request.requirements.care_type if request.requirements else 'N/A'}")

        # 돌봄 유형에 따른 자격증 필터링
        care_type = request.requirements.care_type if request.requirements else 'nursing-aide'
        cert_keyword = CARE_TYPE_TO_CERTIFICATION.get(care_type, '요양보호사')

        # SQL LIKE 필터를 사용하여 실제 간병인 데이터 조회 (성격 정보 포함)
        # 예: 요양보호사 검색 시 "요양보호사 1급", "요양보호사 2급" 등 모두 매칭
        caregivers = db.query(Caregiver).join(User).outerjoin(CaregiverPersonality).filter(
            Caregiver.certifications.ilike(f'%{cert_keyword}%')
        ).limit(request.top_k).all()

        if not caregivers:
            logger.warning(f"[XGBoost 추천] 조회된 간병인 없음")
            return XGBoostMatchingResponse(
                patient_id=request.patient_id,
                total_matches=0,
                matches=[],
                algorithm_version="XGBoost_v3",
                timestamp=datetime.utcnow()
            )

        # 조회된 데이터를 처리
        caregivers_with_personality = []
        for caregiver in caregivers:
            # 선택된 돌봄유형에 맞는 자격증만 추출
            job_title = extract_matching_job_title(caregiver.certifications, cert_keyword)

            # 실제 성격 정보 조회 (또는 기본값)
            personality = caregiver.personality
            empathy_score = personality.empathy_score if personality else 50
            activity_score = personality.activity_score if personality else 50
            patience_score = personality.patience_score if personality else 50
            independence_score = personality.independence_score if personality else 50

            caregivers_with_personality.append({
                "caregiver_id": caregiver.caregiver_id,
                "caregiver_name": caregiver.user.name if caregiver.user else "Unknown",
                "job_title": job_title,
                "experience_years": caregiver.experience_years or 0,
                "empathy_score": empathy_score,
                "activity_score": activity_score,
                "patience_score": patience_score,
                "independence_score": independence_score,
                "hourly_rate": caregiver.hourly_rate or 25000,
                "avg_rating": float(caregiver.avg_rating) if caregiver.avg_rating else 4.5,
                "profile_image_url": (caregiver.user.profile_image_url or "") if caregiver.user else "",
            })

        # XGBoost 매칭 추천
        recommendations = EnhancedMatchingService.recommend_caregivers_xgboost(
            patient_id=request.patient_id,
            patient_personality={
                "empathy_score": request.patient_personality.empathy_score,
                "activity_score": request.patient_personality.activity_score,
                "patience_score": request.patient_personality.patience_score,
                "independence_score": request.patient_personality.independence_score,
            },
            caregivers_with_personality=caregivers_with_personality,
            limit=request.top_k,
        )

        # 응답 포맷 변환
        matches = [
            EnhancedMatchingService.format_matching_result(rec)
            for rec in recommendations
        ]

        logger.info(f"[XGBoost 추천] {len(matches)}명의 간병인 추천 완료")

        # 매칭 요청을 데이터베이스에 저장 (care period dates 포함)
        try:
            matching_request = MatchingRequest(
                patient_id=request.patient_id,
                required_qualification=request.requirements.care_type if request.requirements else None,
                preferred_regions=None,
                preferred_days=request.preferred_days,
                preferred_time_slots=request.preferred_time_slots,
                care_start_date=request.care_start_date,
                care_end_date=request.care_end_date,
                additional_request=None,
                is_active=True
            )
            db.add(matching_request)
            db.commit()
            db.refresh(matching_request)
            logger.info(f"[매칭 요청 저장] request_id={matching_request.request_id}, patient_id={request.patient_id}, "
                       f"care_period={request.care_start_date} ~ {request.care_end_date}")
        except Exception as e:
            logger.error(f"[매칭 요청 저장 실패] {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"매칭 요청 저장 실패: {str(e)}")

        return XGBoostMatchingResponse(
            patient_id=request.patient_id,
            total_matches=len(matches),
            matches=matches,
            algorithm_version="XGBoost_v3",
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"❌ XGBoost 매칭 실패: {e}")
        raise HTTPException(status_code=500, detail=f"매칭 실패: {str(e)}")


@router.get("/health")
async def health_check():
    """
    매칭 서비스 상태 확인

    XGBoost 모델이 정상적으로 로드되었는지 확인합니다.
    """
    try:
        if EnhancedMatchingService.xgboost_service is None:
            return {
                "status": "warning",
                "message": "XGBoost 서비스 미초기화",
                "model_status": "unavailable"
            }

        # 모델 상태 확인
        service = XGBoostMatchingService()
        if service._model is None:
            return {
                "status": "error",
                "message": "XGBoost 모델 로드 실패",
                "model_status": "failed"
            }

        return {
            "status": "healthy",
            "message": "XGBoost 매칭 서비스 정상",
            "model_status": "loaded",
            "algorithm_version": "XGBoost_v3",
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"❌ 상태 확인 실패: {e}")
        return {
            "status": "error",
            "message": str(e),
            "model_status": "error"
        }


@router.post("/test-prediction")
async def test_prediction(
    patient_personality: PersonalityScores,
    caregiver_personality: PersonalityScores,
):
    """
    XGBoost 예측 테스트

    환자와 간병인의 성격 정보로 호환도 점수를 테스트합니다.

    ## 사용 목적
    - 모델 성능 검증
    - 성격 점수의 영향도 확인
    - 디버깅

    ## 응답 예제
    ```json
    {
        "patient_personality": {...},
        "caregiver_personality": {...},
        "compatibility_score": 78.5,
        "grade": "A",
        "analysis": "공감 능력이 잘 맞습니다 | 인내심 수준이 유사합니다",
        "features": {
            "empathy_diff": 3.0,
            "patience_diff": 2.0,
            ...
        }
    }
    ```
    """
    try:
        service = XGBoostMatchingService()

        # Feature 생성
        features = service.generate_features(
            patient_personality.dict(),
            caregiver_personality.dict()
        )

        # 예측
        score = service.predict_compatibility(
            patient_personality.dict(),
            caregiver_personality.dict()
        )

        # 등급
        grade = service.get_grade_from_score(score)

        # 분석
        analysis = service.get_analysis_from_features(features)

        return {
            "patient_personality": patient_personality.dict(),
            "caregiver_personality": caregiver_personality.dict(),
            "compatibility_score": round(score, 1),
            "grade": grade,
            "analysis": analysis,
            "features": {k: round(v, 2) for k, v in features.items()}
        }

    except Exception as e:
        logger.error(f"❌ 테스트 예측 실패: {e}")
        raise HTTPException(status_code=500, detail=f"예측 실패: {str(e)}")
