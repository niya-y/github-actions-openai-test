"""
케어 플랜 생성 API 라우트
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.profile import Patient, Caregiver, Guardian
from app.models.user import User
from app.services.care_plan_generation_service import CarePlanGenerationService

logger = logging.getLogger(__name__)

# Router 생성
router = APIRouter(prefix="/api/care-plans", tags=["care_plans"])


class CarePlanGenerationRequest(BaseModel):
    """케어 플랜 생성 요청"""
    patient_id: int = Field(..., description="환자 ID")
    caregiver_id: int = Field(..., description="간병인 ID")
    patient_personality: dict = Field(..., description="환자 성격 점수")
    care_requirements: dict = Field(..., description="돌봄 요구사항")


@router.post("/generate")
async def generate_care_plan(
    request: CarePlanGenerationRequest,
    db: Session = Depends(get_db),
):
    """
    AI를 사용하여 케어 플랜을 생성합니다.

    환자 정보, 간병인 정보, 성격 점수, 돌봄 요구사항을 기반으로
    Azure OpenAI를 사용하여 맞춤형 케어 플랜을 생성합니다.

    ## 요청 예제
    ```json
    {
        "patient_id": 1,
        "caregiver_id": 1,
        "patient_personality": {
            "empathy_score": 75,
            "activity_score": 55,
            "patience_score": 80,
            "independence_score": 45
        },
        "care_requirements": {
            "care_type": "nursing-aide",
            "time_slots": ["morning", "afternoon"],
            "gender": "Female",
            "skills": ["dementia", "diabetes"]
        }
    }
    ```
    """

    try:
        logger.info(f"[케어 플랜 생성] 환자 {request.patient_id}, 간병인 {request.caregiver_id}")

        # 환자 정보 조회
        patient = db.query(Patient).filter(
            Patient.patient_id == request.patient_id
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="환자 정보를 찾을 수 없습니다")

        # 환자 보호자 정보 조회 후 사용자 정보 조회
        guardian = db.query(Guardian).filter(
            Guardian.guardian_id == patient.guardian_id
        ).first()

        patient_user = None
        if guardian:
            patient_user = db.query(User).filter(
                User.user_id == guardian.user_id
            ).first()

        # 간병인 정보 조회
        caregiver = db.query(Caregiver).filter(
            Caregiver.caregiver_id == request.caregiver_id
        ).first()

        if not caregiver:
            raise HTTPException(status_code=404, detail="간병인 정보를 찾을 수 없습니다")

        # 간병인 사용자 정보 조회
        caregiver_user = db.query(User).filter(
            User.user_id == caregiver.user_id
        ).first()

        # 환자 정보 구성
        patient_info = {
            "id": patient.patient_id,
            "name": patient_user.name if patient_user else "환자",
            "age": patient.age,
            "condition": patient.care_level or "일반",
            "special_conditions": patient.medical_conditions or ""
        }

        # 간병인 정보 구성
        caregiver_info = {
            "id": caregiver.caregiver_id,
            "name": caregiver_user.name if caregiver_user else "간병인",
            "experience_years": caregiver.experience_years or 0,
            "specialties": caregiver.specialties.split("|") if caregiver.specialties else [],
            "hourly_rate": caregiver.hourly_rate or 0
        }

        # AI 서비스를 사용하여 케어 플랜 생성
        service = CarePlanGenerationService()
        care_plan = service.generate_care_plan(
            patient_info=patient_info,
            caregiver_info=caregiver_info,
            patient_personality=request.patient_personality,
            care_requirements=request.care_requirements
        )

        logger.info(f"[케어 플랜 생성 완료] 총 {len(care_plan.weekly_schedule)}일간의 일정 생성")

        # 응답 반환
        return {
            "success": True,
            "data": care_plan.model_dump(),
            "message": "케어 플랜이 생성되었습니다."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 케어 플랜 생성 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"케어 플랜 생성 중 오류가 발생했습니다: {str(e)}"
        )
