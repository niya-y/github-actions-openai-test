"""
케어 플랜 생성 API 라우트
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.profile import Patient, Caregiver, Guardian
from app.models.user import User
from app.models.care_execution import Schedule, CareLog, CareCategoryEnum
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

        # DB에 저장
        try:
            logger.info("[케어 플랜 저장 시작] DB에 스케줄 및 케어 로그 저장 중...")

            # 오늘 날짜부터 시작
            start_date = datetime.now().date()

            # weekly_schedule의 각 day에 대해 반복
            for day_index, day_schedule in enumerate(care_plan.weekly_schedule):
                care_date = start_date + timedelta(days=day_index)

                # Schedule 생성
                schedule = Schedule(
                    patient_id=request.patient_id,
                    matching_id=None,  # 매칭 ID는 선택사항
                    care_date=care_date,
                    is_ai_generated=True,
                    status="scheduled"
                )
                db.add(schedule)
                db.flush()  # schedule_id를 얻기 위해 flush

                # 각 activity에 대한 CareLog 생성
                for activity in day_schedule.get("activities", []):
                    try:
                        # activity의 시간 파싱 (HH:MM 형식)
                        scheduled_time = None
                        if activity.get("time"):
                            time_parts = activity["time"].split(":")
                            if len(time_parts) >= 2:
                                scheduled_time = f"{time_parts[0]}:{time_parts[1]}:00"

                        # 카테고리 결정 (기본값: "other")
                        category = "other"
                        activity_title = activity.get("title", "").lower()
                        if "약" in activity_title or "medication" in activity_title:
                            category = "medication"
                        elif "식사" in activity_title or "meal" in activity_title:
                            category = "meal"
                        elif "운동" in activity_title or "exercise" in activity_title:
                            category = "exercise"
                        elif "체크" in activity_title or "vital" in activity_title:
                            category = "vital_check"
                        elif "위생" in activity_title or "hygiene" in activity_title:
                            category = "hygiene"

                        # CareLog 생성
                        care_log = CareLog(
                            schedule_id=schedule.schedule_id,
                            category=category,
                            task_name=activity.get("title", "활동"),
                            scheduled_time=scheduled_time,
                            is_completed=False,
                            note=activity.get("note", "")
                        )
                        db.add(care_log)

                    except Exception as e:
                        logger.warning(f"[CareLog 생성 실패] activity: {activity}, error: {e}")
                        # 하나의 활동 실패가 전체 프로세스를 중단하지 않도록
                        continue

            # 트랜잭션 커밋
            db.commit()
            logger.info(f"[케어 플랜 저장 완료] 총 {len(care_plan.weekly_schedule)}개 일정 저장됨")

        except Exception as e:
            db.rollback()
            logger.error(f"❌ 케어 플랜 DB 저장 실패: {e}")
            # DB 저장 실패해도 응답은 계속 반환 (AI 생성은 성공했으므로)
            logger.warning("경고: DB 저장에 실패했으나 AI 생성 결과는 반환합니다")

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
