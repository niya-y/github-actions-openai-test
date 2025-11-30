"""
Personality API Routes
성향 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel

from services.personality_service import PersonalityService

# Pydantic 모델
class PersonalityTestRequest(BaseModel):
    patient_id: int
    test_answers: List[int]

    class Config:
        schema_extra = {
            "example": {
                "patient_id": 1,
                "test_answers": [0, 1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 1]
            }
        }


class PersonalityResponse(BaseModel):
    patient_id: int
    personality_type: str
    empathy: float
    activity: float
    patience: float
    independence: float
    description: str
    test_completed_at: str


class PersonalityDetailResponse(BaseModel):
    patient_id: int
    resident_name: str
    personality_type: str
    empathy: float
    activity: float
    patience: float
    independence: float
    description: str
    test_completed: bool
    test_completed_at: str
    created_at: str
    updated_at: str


router = APIRouter(prefix="/api/personality", tags=["Personality"])


@router.post("/test", response_model=PersonalityResponse)
async def save_personality_test(request: PersonalityTestRequest):
    """
    환자의 성향 테스트 결과 저장

    - **patient_id**: 환자 ID
    - **test_answers**: 12개 질문에 대한 답변 (0-2 점수)

    Returns: 저장된 성향 정보
    """
    try:
        result = PersonalityService.save_personality_test(
            patient_id=request.patient_id,
            test_answers=request.test_answers
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{patient_id}", response_model=PersonalityDetailResponse)
async def get_patient_personality(patient_id: int):
    """
    환자의 성향 정보 조회

    - **patient_id**: 환자 ID

    Returns: 성향 정보 상세
    """
    try:
        result = PersonalityService.get_patient_personality(patient_id=patient_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/list/all")
async def list_all_personalities(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    모든 환자의 성향 정보 목록 조회

    - **limit**: 반환할 최대 개수 (기본값: 100)
    - **offset**: 시작 위치 (기본값: 0)

    Returns: 성향 정보 목록
    """
    try:
        result = PersonalityService.list_all_personalities(
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats/summary")
async def get_personality_stats():
    """
    성향 통계 정보 조회

    Returns: 성향 통계 정보 (평균, 분포, 범위 등)
    """
    try:
        result = PersonalityService.get_personality_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
