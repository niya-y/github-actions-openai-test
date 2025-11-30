"""
Matching API Routes
매칭 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date

from services.matching_service import MatchingService

# Pydantic 모델
class MatchingCreateRequest(BaseModel):
    patient_id: int
    caregiver_id: int

    class Config:
        schema_extra = {
            "example": {
                "patient_id": 1,
                "caregiver_id": 1
            }
        }


class MatchingCancelRequest(BaseModel):
    reason: str = "사용자 요청"

    class Config:
        schema_extra = {
            "example": {
                "reason": "간병인 교체 요청"
            }
        }


class PerformanceQuery(BaseModel):
    start_date: date
    end_date: date


router = APIRouter(prefix="/api/matching", tags=["Matching"])


@router.get("/recommend/{patient_id}")
async def get_recommended_caregivers(
    patient_id: int,
    limit: int = Query(5, ge=1, le=20)
):
    """
    환자에게 추천할 간병인 목록 조회

    - **patient_id**: 환자 ID
    - **limit**: 반환할 추천 간병인 수 (기본값: 5, 최대: 20)

    Returns: 추천 간병인 목록 (매칭 점수 포함)
    """
    try:
        result = MatchingService.recommend_caregivers(
            patient_id=patient_id,
            limit=limit
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/create")
async def create_matching(request: MatchingCreateRequest):
    """
    환자와 간병인 간 매칭 생성

    - **patient_id**: 환자 ID
    - **caregiver_id**: 간병인 ID

    Returns: 생성된 매칭 정보
    """
    try:
        result = MatchingService.create_matching(
            patient_id=request.patient_id,
            caregiver_id=request.caregiver_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{patient_id}")
async def get_matching_history(patient_id: int):
    """
    환자의 매칭 이력 조회

    - **patient_id**: 환자 ID

    Returns: 매칭 이력 목록 (현재 및 과거 매칭)
    """
    try:
        result = MatchingService.get_matching_history(patient_id=patient_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{matching_id}")
async def cancel_matching(
    matching_id: int,
    reason: str = Query("사용자 요청", min_length=1)
):
    """
    매칭 취소

    - **matching_id**: 매칭 ID
    - **reason**: 취소 사유

    Returns: 취소된 매칭 정보
    """
    try:
        result = MatchingService.cancel_matching(
            matching_id=matching_id,
            reason=reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/performance/evaluate")
async def get_matching_performance(
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)")
):
    """
    기간별 매칭 성능 평가

    - **start_date**: 시작 날짜 (형식: YYYY-MM-DD)
    - **end_date**: 종료 날짜 (형식: YYYY-MM-DD)

    Returns: 매칭 성능 평가 정보 (평균 점수, 등급 분포 등)
    """
    try:
        result = MatchingService.evaluate_matching_performance(
            start_date=start_date,
            end_date=end_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
