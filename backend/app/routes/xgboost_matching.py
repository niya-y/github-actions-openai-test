"""
XGBoost 기반 매칭 API 라우트

P11 (간병인 찾기) → P12 (로딩) → P13 (결과 리스트)의 API 엔드포인트

늘봄케어 매칭 모델 (XGBoost R²=0.9159) 통합
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, date
import logging
import re

from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.matching.nuelbom_predictor import get_nuelbom_predictor, NuelbomMatchingPredictor
from app.dependencies.database import get_db
from app.models.profile import Caregiver
from app.models.user import User
from app.models.care_details import CaregiverPersonality
from app.models.matching import MatchingRequest, MatchingResult

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


def generate_matching_reason(
    caregiver_name: str,
    experience_years: int,
    specialties: List[str],
    match_score: float,
    personality_analysis: str = ""
) -> str:
    """
    매칭 근거를 감정적/객관적 톤으로 자동 생성

    Args:
        caregiver_name: 간병인 이름
        experience_years: 경력 년수
        specialties: 전문 분야 리스트
        match_score: 매칭 점수 (0-100)
        personality_analysis: 성격 분석 내용

    Returns:
        감정적/객관적 매칭 근거 설명
    """
    try:
        # 전문 분야 문자열화
        specialties_str = ", ".join(specialties) if specialties else "돌봄 서비스"

        # 경력 표현
        if experience_years >= 10:
            experience_phrase = f"{experience_years}년의 풍부한 경험을 가진"
        elif experience_years >= 5:
            experience_phrase = f"{experience_years}년의 경험을 가진"
        elif experience_years >= 1:
            experience_phrase = f"{experience_years}년의 경험을 가진"
        else:
            experience_phrase = "열정적인"

        # 점수 기반 표현
        if match_score >= 95:
            score_phrase = f"{match_score:.0f}%의 매우 높은 호환도로 최우선 추천합니다."
            confidence_tone = "완벽하게"
        elif match_score >= 90:
            score_phrase = f"{match_score:.0f}%의 높은 호환도로 강력히 추천합니다."
            confidence_tone = "탁월하게"
        elif match_score >= 85:
            score_phrase = f"{match_score:.0f}%의 좋은 호환도로 추천합니다."
            confidence_tone = "효과적으로"
        elif match_score >= 80:
            score_phrase = f"{match_score:.0f}%의 호환도입니다."
            confidence_tone = "능숙하게"
        else:
            score_phrase = f"{match_score:.0f}%의 호환도입니다."
            confidence_tone = "성실하게"

        # 최종 문구 구성
        matching_reason = (
            f"{specialties_str} 관리에 "
            f"{experience_phrase} {caregiver_name}님은 "
            f"환자분의 다양한 필요를 {confidence_tone} 이해하고 "
            f"맞춤형 돌봄을 제공할 것입니다. "
            f"{score_phrase}"
        )

        return matching_reason

    except Exception as e:
        logger.error(f"❌ 매칭 근거 생성 실패: {e}")
        return f"{caregiver_name}님은 환자분을 위해 최선의 돌봄을 제공할 것입니다."

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
    matching_id: Optional[int] = None
    matching_reason: str = Field(..., description="매칭 근거 설명")


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
        from sqlalchemy.orm import joinedload
        caregivers = db.query(Caregiver)\
            .join(User)\
            .outerjoin(CaregiverPersonality)\
            .options(joinedload(Caregiver.user))\
            .filter(Caregiver.certifications.ilike(f'%{cert_keyword}%'))\
            .limit(request.top_k * 2)\
            .all()  # 필터링을 위해 더 많이 조회

        logger.info(f"[XGBoost 추천] 조회된 간병인 수: {len(caregivers)}")
        if caregivers:
            first_caregiver = caregivers[0]
            logger.info(f"[XGBoost 추천] 첫 번째 간병인: {first_caregiver.caregiver_id}")
            logger.info(f"[XGBoost 추천] Specialties 칼럼값: {first_caregiver.specialties} (type: {type(first_caregiver.specialties)})")
            if first_caregiver.specialties:
                logger.info(f"[XGBoost 추천] Specialties 길이: {len(first_caregiver.specialties)}")

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

            # specialties 파싱: PostgreSQL ARRAY 타입을 처리
            # DB에서 {항목1,항목2,항목3} 또는 [항목1, 항목2] 형태로 올 수 있음
            specialties = []
            if caregiver.specialties:
                try:
                    # 이미 리스트/튜플인 경우
                    if isinstance(caregiver.specialties, (list, tuple)):
                        specialties = [str(s).strip() for s in caregiver.specialties if s]
                    else:
                        # 문자열인 경우: {항목1,항목2} 형태
                        specs_str = str(caregiver.specialties)
                        if specs_str.startswith('{') and specs_str.endswith('}'):
                            specs_str = specs_str[1:-1]  # {} 제거
                        # 쉼표로 구분된 항목 파싱
                        specialties = [s.strip() for s in specs_str.split(',') if s.strip()]
                except Exception as e:
                    logger.warning(f"[XGBoost] specialties 파싱 실패: {caregiver.caregiver_id}, error: {e}")
                    specialties = []

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
                "specialties": specialties,
            })

        # 늘봄케어 XGBoost 매칭 추천 (R²=0.9159)
        predictor = get_nuelbom_predictor()
        recommendations = predictor.recommend_caregivers_with_db_personality(
            patient_id=request.patient_id,
            patient_personality={
                "empathy_score": request.patient_personality.empathy_score,
                "activity_score": request.patient_personality.activity_score,
                "patience_score": request.patient_personality.patience_score,
                "independence_score": request.patient_personality.independence_score,
            },
            caregivers_with_personality=caregivers_with_personality,
            top_n=request.top_k,
        )

        # 응답 포맷 변환 (기존 API 스키마에 맞춤)
        matches = []
        for rec in recommendations:
            # 매칭 근거 생성
            matching_reason = generate_matching_reason(
                caregiver_name=rec.get("caregiver_name", ""),
                experience_years=rec.get("experience_years", 0),
                specialties=rec.get("specialties", []),
                match_score=rec.get("predicted_score", 0),
                personality_analysis=rec.get("ai_comment", "")
            )

            matches.append({
                "caregiver_id": rec["caregiver_id"],
                "caregiver_name": rec.get("caregiver_name", ""),
                "job_title": rec.get("job_title", ""),
                "grade": rec.get("grade", "B"),
                "match_score": rec.get("predicted_score", 0),
                "experience_years": rec.get("experience_years", 0),
                "hourly_rate": rec.get("hourly_rate", 0),
                "avg_rating": rec.get("avg_rating", 0),
                "profile_image_url": rec.get("profile_image_url", ""),
                "personality_analysis": rec.get("ai_comment", ""),
                "specialties": rec.get("specialties", []),
                "availability": rec.get("availability", []),
                "matching_reason": matching_reason,
            })

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

            # 매칭 결과(MatchingResult) 저장
            saved_matches = []
            for match in matches:
                try:
                    matching_result = MatchingResult(
                        request_id=matching_request.request_id,
                        caregiver_id=match['caregiver_id'],
                        status="recommended",
                        total_score=match['match_score'],
                        grade=match['grade'],
                        ai_comment=match['personality_analysis']
                    )
                    db.add(matching_result)
                    db.commit()
                    db.refresh(matching_result)
                    
                    # 응답 객체에 matching_id 설정
                    match['matching_id'] = matching_result.matching_id
                    saved_matches.append(match)
                except Exception as e:
                    logger.error(f"[매칭 결과 저장 실패] caregiver_id={match.get('caregiver_id')}: {e}")
                    # 실패해도 다른 매칭은 계속 저장 시도
            
            # matches 리스트 업데이트
            matches = saved_matches
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

    늘봄케어 XGBoost 모델이 정상적으로 로드되었는지 확인합니다.
    """
    try:
        predictor = get_nuelbom_predictor()
        status = predictor.get_status()

        if not status.get("model_loaded"):
            return {
                "status": "warning",
                "message": "XGBoost 모델 미로드",
                "model_status": "unavailable",
                "details": status
            }

        return {
            "status": "healthy",
            "message": "늘봄케어 XGBoost 매칭 서비스 정상 (R²=0.9159)",
            "model_status": "loaded",
            "algorithm_version": "Nuelbom_XGBoost_v1",
            "azure_openai_available": status.get("azure_openai_available", False),
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
        from app.services.matching.feature_engineering import FeatureEngineer

        predictor = get_nuelbom_predictor()
        engineer = FeatureEngineer()

        # Feature 생성
        patient_dict = patient_personality.dict()
        caregiver_dict = caregiver_personality.dict()

        features = engineer.create_features_from_db_data(
            patient_personality=patient_dict,
            caregiver_data=caregiver_dict
        )

        # 예측 (단일 간병인 추천)
        recommendations = predictor.recommend_caregivers_with_db_personality(
            patient_id=0,  # 테스트용
            patient_personality=patient_dict,
            caregivers_with_personality=[{
                "caregiver_id": 0,
                "caregiver_name": "테스트 간병인",
                "job_title": "요양보호사",
                "experience_years": 5,
                **caregiver_dict,
                "hourly_rate": 25000,
                "avg_rating": 4.5,
                "profile_image_url": "",
                "specialties": [],
            }],
            top_n=1,
        )

        if recommendations:
            rec = recommendations[0]
            score = rec.get("predicted_score", 0)
            grade = rec.get("grade", "B")
            analysis = rec.get("ai_comment", "")
        else:
            score = 70.0
            grade = "B+"
            analysis = "테스트 분석 결과입니다."

        return {
            "patient_personality": patient_dict,
            "caregiver_personality": caregiver_dict,
            "compatibility_score": round(score, 1),
            "grade": grade,
            "analysis": analysis,
            "features": {k: round(v, 2) for k, v in features.items()},
            "model_version": "Nuelbom_XGBoost_v1"
        }

    except Exception as e:
        logger.error(f"❌ 테스트 예측 실패: {e}")
        raise HTTPException(status_code=500, detail=f"예측 실패: {str(e)}")
