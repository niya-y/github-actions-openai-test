"""
케어 플랜 생성 API 라우트
"""

import logging
from datetime import datetime, timedelta, date
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.profile import Patient, Caregiver, Guardian
from app.models.user import User
from app.models.care_execution import Schedule, CareLog, CareCategoryEnum, MealPlan
from app.models.care_details import HealthCondition, Medication, DietaryPreference
from app.models.matching import MatchingResult, MatchingRequest
from app.services.care_plan_generation_service import CarePlanGenerationService
from app.services.meal_recommendation import (
    MealRecommendationService,
    MealRecommendationConfig
)

logger = logging.getLogger(__name__)


def calculate_age(birth_date: date) -> int:
    """생년월일로부터 나이 계산"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def collect_patient_data(patient_id: int, db: Session) -> dict:
    """
    환자 데이터 수집 (질병, 약물, 알레르기)

    Args:
        patient_id: 환자 ID
        db: DB 세션

    Returns:
        dict: 환자 정보, 질병, 약물, 알레르기 데이터

    Raises:
        HTTPException: 환자를 찾을 수 없는 경우
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()

    # 환자 null 체크
    if not patient:
        logger.error(f"Patient not found: patient_id={patient_id}")
        raise HTTPException(
            status_code=404,
            detail=f"환자를 찾을 수 없습니다 (patient_id: {patient_id})"
        )

    # 환자 기본 정보
    patient_data = {
        "name": patient.name,
        "age": (
            datetime.now().year - patient.birth_date.year
            if patient.birth_date else 0
        ),
        "gender": patient.gender.value if patient.gender else "Unknown",
        "care_level": patient.care_level.value if patient.care_level else None
    }

    # 질병 정보
    health_conditions = [
        hc.disease_name
        for hc in db.query(HealthCondition)
            .filter(HealthCondition.patient_id == patient_id)
            .all()
    ]

    # 약물 정보 (PostgreSQL ARRAY 타입)
    medications = []
    meds = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    for med in meds:
        if med.medicine_names:
            medications.extend(med.medicine_names)

    # 알레르기/제한 음식
    dietary = db.query(DietaryPreference).filter(
        DietaryPreference.patient_id == patient_id
    ).first()

    dietary_prefs = {
        "allergy_foods": (
            dietary.allergy_foods
            if dietary and dietary.allergy_foods else []
        ),
        "restriction_foods": (
            dietary.restriction_foods
            if dietary and dietary.restriction_foods else []
        )
    }

    return {
        "patient_data": patient_data,
        "health_conditions": health_conditions,
        "medications": medications,
        "dietary_prefs": dietary_prefs
    }


# Router 생성
router = APIRouter(prefix="/api/care-plans", tags=["care_plans"])


class CarePlanGenerationRequest(BaseModel):
    """케어 플랜 생성 요청"""
    patient_id: int = Field(..., description="환자 ID")
    caregiver_id: int = Field(..., description="간병인 ID")
    patient_personality: dict = Field(..., description="환자 성격 점수")
    care_requirements: dict = Field(..., description="돌봄 요구사항")
    care_start_date: str | None = Field(None, description="간병 시작일 (YYYY-MM-DD)")
    care_end_date: str | None = Field(None, description="간병 종료일 (YYYY-MM-DD)")


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

        # 매칭 요청 정보 조회 (matching_requests 테이블에서 care_start_date, care_end_date, preferred_time_slots 조회)
        matching_request = db.query(MatchingRequest).filter(
            MatchingRequest.patient_id == request.patient_id,
            MatchingRequest.is_active == True
        ).order_by(MatchingRequest.created_at.desc()).first()

        if matching_request:
            logger.info(f"📋 매칭 요청 조회 성공: request_id={matching_request.request_id}, "
                       f"care_period={matching_request.care_start_date} ~ {matching_request.care_end_date}, "
                       f"time_slots={matching_request.preferred_time_slots}")

        # 매칭 결과 조회 (MatchingResult - request_id로 연결)
        matching = None
        if matching_request:
            matching = db.query(MatchingResult).filter(
                MatchingResult.request_id == matching_request.request_id,
                MatchingResult.caregiver_id == request.caregiver_id
            ).order_by(MatchingResult.created_at.desc()).first()

        # 간병인으로만 조회 (폴백)
        if not matching:
            matching = db.query(MatchingResult).filter(
                MatchingResult.caregiver_id == request.caregiver_id
            ).order_by(MatchingResult.created_at.desc()).first()

        # 케어 기간 계산 (우선순위: 1.matching_requests DB 2.요청 파라미터 3.기본값 7일)
        start_date_str = None
        end_date_str = None
        preferred_time_slots = None

        # 1. matching_requests 테이블에서 날짜 및 시간대 사용 (DB 우선)
        if matching_request and matching_request.care_start_date and matching_request.care_end_date:
            start_date_str = matching_request.care_start_date.isoformat()
            end_date_str = matching_request.care_end_date.isoformat()
            preferred_time_slots = matching_request.preferred_time_slots
            days_diff = (matching_request.care_end_date - matching_request.care_start_date).days + 1
            logger.info(f"📅 DB(matching_requests) 기간: {start_date_str} ~ {end_date_str} ({days_diff}일), 시간대: {preferred_time_slots}")
        # 2. 프론트엔드에서 전달받은 날짜 사용 (폴백)
        elif request.care_start_date and request.care_end_date:
            start_date_str = request.care_start_date
            end_date_str = request.care_end_date
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            days_diff = (end_dt - start_dt).days + 1
            logger.info(f"📅 프론트엔드 요청 기간: {start_date_str} ~ {end_date_str} ({days_diff}일)")
        # 3. 기본값 7일
        else:
            logger.warning("⚠️ 날짜 정보가 없습니다. 기본 7일로 생성합니다.")

        # preferred_time_slots가 없으면 care_requirements에서 가져오기
        if not preferred_time_slots and request.care_requirements:
            preferred_time_slots = request.care_requirements.get('time_slots', ['morning', 'afternoon'])

        # 환자 정보 구성
        # 나이 계산 (birth_date에서)
        age = calculate_age(patient.birth_date) if patient.birth_date else 65

        # 환자 상세 데이터 수집 (약물, 질병, 식이 정보)
        patient_details = collect_patient_data(request.patient_id, db)

        patient_info = {
            "id": patient.patient_id,
            "name": patient_user.name if patient_user else "환자",
            "age": age,
            "condition": patient.care_level.value if patient.care_level else "일반",
            "special_conditions": ", ".join(patient_details.get("health_conditions", [])),
            "medications": patient_details.get("medications", []),
            "health_conditions": patient_details.get("health_conditions", []),
            "dietary_prefs": patient_details.get("dietary_prefs", {})
        }

        # 간병인 정보 구성
        # specialties는 PostgreSQL ARRAY 타입이므로 이미 list로 저장됨
        specialties_list = caregiver.specialties if isinstance(caregiver.specialties, list) else (caregiver.specialties.split("|") if caregiver.specialties else [])

        caregiver_info = {
            "id": caregiver.caregiver_id,
            "name": caregiver_user.name if caregiver_user else "간병인",
            "experience_years": caregiver.experience_years or 0,
            "specialties": specialties_list,
            "hourly_rate": caregiver.hourly_rate or 0
        }

        # AI 서비스를 사용하여 케어 플랜 생성
        service = CarePlanGenerationService()
        care_plan = service.generate_care_plan(
            patient_info=patient_info,
            caregiver_info=caregiver_info,
            patient_personality=request.patient_personality,
            care_requirements=request.care_requirements,
            start_date=start_date_str,
            end_date=end_date_str,
            preferred_time_slots=preferred_time_slots
        )

        logger.info(f"[케어 플랜 생성 완료] 총 {len(care_plan.weekly_schedule)}일간의 일정 생성")

        # DB에 저장
        saved_schedule_ids = []
        try:
            logger.info("[케어 플랜 저장 시작] DB에 스케줄 및 케어 로그 저장 중...")
            logger.info(f"📊 매칭 ID: {matching.matching_id if matching else 'None'}")

            # 시작일 결정 (요청받은 시작일 or 오늘)
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                logger.info(f"📅 요청받은 시작일 사용: {start_date}")
            else:
                start_date = datetime.now().date()
                logger.info(f"📅 기본 시작일 사용 (오늘): {start_date}")

            # 기존 pending_review 상태의 스케줄 삭제 (중복 방지)
            existing_schedules = db.query(Schedule).filter(
                Schedule.patient_id == request.patient_id,
                Schedule.status == 'pending_review',
                Schedule.care_date >= start_date
            ).all()

            if existing_schedules:
                logger.info(f"🗑️ 기존 pending_review 스케줄 {len(existing_schedules)}개 삭제")
                for sched in existing_schedules:
                    db.delete(sched)
                db.flush()

            # weekly_schedule의 각 day에 대해 반복
            for day_index, day_schedule in enumerate(care_plan.weekly_schedule):
                care_date = start_date + timedelta(days=day_index)

                # Schedule 생성 (매칭 ID 연결)
                schedule = Schedule(
                    patient_id=request.patient_id,
                    matching_id=matching.matching_id if matching else None,
                    care_date=care_date,
                    is_ai_generated=True,
                    status="pending_review"
                )
                db.add(schedule)
                db.flush()  # schedule_id를 얻기 위해 flush
                saved_schedule_ids.append(schedule.schedule_id)
                logger.info(f"📅 Schedule 생성: ID={schedule.schedule_id}, date={care_date}")

                # 각 activity에 대한 CareLog 생성
                # day_schedule과 activity는 Pydantic 모델이므로 속성으로 접근
                activities = day_schedule.activities if hasattr(day_schedule, 'activities') else []
                failed_activities = []  # 실패한 활동 기록

                for activity in activities:
                    try:
                        # activity의 시간 파싱 (HH:MM 형식)
                        scheduled_time = None
                        activity_time = activity.time if hasattr(activity, 'time') else None
                        if activity_time:
                            time_parts = activity_time.split(":")
                            if len(time_parts) >= 2:
                                scheduled_time = f"{time_parts[0]}:{time_parts[1]}:00"

                        # 카테고리 결정 (기본값: "other")
                        category = "other"
                        activity_title = (activity.title if hasattr(activity, 'title') else "").lower()
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
                            task_name=activity.title if hasattr(activity, 'title') else "활동",
                            scheduled_time=scheduled_time,
                            is_completed=False,
                            note=activity.note if hasattr(activity, 'note') else ""
                        )
                        db.add(care_log)

                    except Exception as e:
                        activity_title = activity.title if hasattr(activity, 'title') else "Unknown"
                        logger.error(f"[CareLog 생성 실패] activity: {activity_title}, error: {str(e)}")
                        failed_activities.append({
                            "activity": activity_title,
                            "error": str(e)
                        })

                # CareLog 생성 실패가 있으면 롤백
                if failed_activities:
                    db.rollback()
                    logger.error(f"[케어 플랜 생성 실패] {len(failed_activities)}개 활동 생성 실패로 전체 롤백")
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "message": "케어 플랜 생성 실패 - 일부 활동 생성 중 오류가 발생했습니다",
                            "failed_count": len(failed_activities),
                            "failed_activities": failed_activities
                        }
                    )

            # 트랜잭션 커밋 (try-except로 감싸서 부분 커밋 방지)
            try:
                db.commit()
                logger.info(f"✅ [케어 플랜 저장 완료] 총 {len(care_plan.weekly_schedule)}개 일정, Schedule IDs: {saved_schedule_ids}")
            except Exception as commit_error:
                db.rollback()
                logger.error(f"❌ 트랜잭션 커밋 실패: {str(commit_error)}")
                saved_schedule_ids = []  # 저장 실패 표시
                raise HTTPException(
                    status_code=500,
                    detail="케어 플랜 저장 중 데이터베이스 오류가 발생했습니다"
                )

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 케어 플랜 DB 저장 실패: {e}")
            saved_schedule_ids = []  # 저장 실패 표시
            # DB 저장 실패 시 에러 발생 (프론트엔드에 알림)
            raise HTTPException(
                status_code=500,
                detail=f"케어 플랜 DB 저장 실패: {str(e)}"
            )

        # ============================================
        # 🍽️ 추천 식단 생성 (AI 기반)
        # ============================================
        meal_plan_data = None
        try:
            logger.info(f"[추천 식단 생성 시작] 환자 {request.patient_id}")

            # 1. 환자 데이터 수집
            data = collect_patient_data(request.patient_id, db)

            # 2. AI 식단 생성 서비스 호출
            config = MealRecommendationConfig()
            meal_service = MealRecommendationService(config)

            # 오늘 날짜의 점심 식단 생성
            today = datetime.now().date()
            meal_plan_result = meal_service.recommend_meal(
                patient_id=request.patient_id,
                patient_data=data["patient_data"],
                health_conditions=data["health_conditions"],
                medications=data["medications"],
                dietary_prefs=data["dietary_prefs"],
                meal_date=str(today),
                meal_type="lunch"
            )

            if meal_plan_result:
                # 3. DB 저장
                # ingredients를 문자열로 변환
                ingredients_str = (
                    ', '.join(meal_plan_result['ingredients'])
                    if isinstance(meal_plan_result['ingredients'], list)
                    else meal_plan_result['ingredients']
                )

                new_meal = MealPlan(
                    patient_id=request.patient_id,
                    meal_date=today,
                    meal_type="lunch",
                    menu_name=meal_plan_result['menu_name'],
                    ingredients=ingredients_str,
                    nutrition_info=meal_plan_result['nutrition_info'],
                    cooking_tips=meal_plan_result.get('cooking_tips'),
                    created_at=datetime.now()
                )

                db.add(new_meal)
                db.commit()
                db.refresh(new_meal)

                # 응답에 포함할 데이터 준비
                meal_plan_data = {
                    "plan_id": new_meal.plan_id,
                    "menu_name": new_meal.menu_name,
                    "ingredients": new_meal.ingredients,
                    "nutrition_info": new_meal.nutrition_info,
                    "cooking_tips": new_meal.cooking_tips,
                    "meal_type": new_meal.meal_type.value if hasattr(new_meal.meal_type, 'value') else str(new_meal.meal_type),
                    "meal_date": new_meal.meal_date.isoformat()
                }

                logger.info(f"✅ 추천 식단 생성 완료: {new_meal.menu_name}")
            else:
                logger.warning("⚠️ AI 식단 생성 결과가 없습니다")

        except Exception as e:
            logger.error(f"❌ 추천 식단 생성 실패: {e}")
            # 식단 생성 실패해도 케어 플랜은 정상 반환
            logger.warning("경고: 추천 식단 생성에 실패했으나 케어 플랜은 정상 반환합니다")

        # 응답 반환
        response_data = {
            "success": True,
            "data": care_plan.model_dump(),
            "saved_schedule_ids": saved_schedule_ids,
            "matching_id": matching.matching_id if matching else None,
            "message": "케어 플랜이 생성되었습니다."
        }

        # 식단 데이터가 있으면 응답에 포함
        if meal_plan_data:
            response_data["meal_plan"] = meal_plan_data
            response_data["message"] = "케어 플랜과 추천 식단이 생성되었습니다."

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 케어 플랜 생성 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"케어 플랜 생성 중 오류가 발생했습니다: {str(e)}"
        )


# 스케줄 상태 전환 규칙 정의
VALID_STATUS_TRANSITIONS = {
    'pending_review': ['under_review', 'confirmed'],  # 케어 플랜 요청 시 또는 바로 확정
    'under_review': ['reviewed', 'confirmed'],  # 검토 중 → 검토 완료 또는 확정
    'reviewed': ['confirmed'],  # 검토 완료 → 확정
    'confirmed': ['scheduled', 'cancelled'],  # 확정 → 스케줄 진행 또는 취소
    'scheduled': ['completed', 'cancelled'],  # 진행 중 → 완료 또는 취소
    'completed': [],  # 최종 상태
    'cancelled': [],  # 최종 상태
}

def validate_status_transition(current_status: str, new_status: str) -> tuple[bool, str]:
    """
    상태 전환이 유효한지 검증합니다.

    Returns:
        (is_valid, error_message)
    """
    # 상태가 동일한 경우는 허용
    if current_status == new_status:
        return True, ""

    # 현재 상태가 유효한지 확인
    if current_status not in VALID_STATUS_TRANSITIONS:
        return False, f"현재 상태 '{current_status}'는 유효하지 않습니다"

    # 전환 가능한 상태인지 확인
    allowed_transitions = VALID_STATUS_TRANSITIONS[current_status]
    if new_status not in allowed_transitions:
        return False, f"'{current_status}' 상태에서 '{new_status}' 상태로 직접 전환할 수 없습니다. 가능한 상태: {', '.join(allowed_transitions)}"

    return True, ""


class ScheduleStatusUpdateRequest(BaseModel):
    """스케줄 상태 업데이트 요청"""
    patient_id: int = Field(..., description="환자 ID")
    status: str = Field(..., description="변경할 상태 (pending_review, under_review, reviewed, confirmed 등)")


@router.put("/schedules/status")
async def update_schedules_status(
    request: ScheduleStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    환자의 모든 pending_review/under_review/reviewed 상태 스케줄의 상태를 일괄 업데이트합니다.

    - care-plans-create-2에서 "요청하기" 버튼 클릭 시: pending_review → under_review
    - care-plans-create-4에서 "완료된 일정보기" 버튼 클릭 시: under_review/reviewed → confirmed

    상태 전환 규칙 검증:
    - pending_review → under_review
    - under_review → reviewed, confirmed
    - reviewed → confirmed
    - confirmed → scheduled, cancelled
    - scheduled → completed, cancelled
    - completed, cancelled → (최종 상태)
    """
    try:
        logger.info(f"📝 스케줄 상태 업데이트 시작: patient_id={request.patient_id}, new_status={request.status}")

        # 환자 확인
        patient = db.query(Patient).filter(Patient.patient_id == request.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다.")

        # 대상 상태가 유효한지 확인
        if request.status not in VALID_STATUS_TRANSITIONS:
            logger.error(f"❌ 유효하지 않은 대상 상태: {request.status}")
            raise HTTPException(
                status_code=400,
                detail=f"유효하지 않은 상태입니다: {request.status}"
            )

        # 업데이트할 스케줄 조회 (pending_review, under_review, reviewed 상태만)
        schedules = db.query(Schedule).filter(
            Schedule.patient_id == request.patient_id,
            Schedule.status.in_(['pending_review', 'under_review', 'reviewed'])
        ).all()

        if not schedules:
            logger.warning(f"⚠️ 업데이트할 스케줄이 없습니다: patient_id={request.patient_id}")
            return {
                "success": True,
                "status": "success",
                "updated_count": 0,
                "message": "업데이트할 스케줄이 없습니다."
            }

        # 상태 전환 검증 및 일괄 업데이트
        updated_count = 0
        failed_transitions = []

        for schedule in schedules:
            # 상태 전환 유효성 검증
            is_valid, error_msg = validate_status_transition(schedule.status, request.status)

            if not is_valid:
                logger.warning(f"⚠️ 상태 전환 실패 [schedule_id={schedule.schedule_id}]: {error_msg}")
                failed_transitions.append({
                    "schedule_id": schedule.schedule_id,
                    "current_status": schedule.status,
                    "attempted_status": request.status,
                    "error": error_msg
                })
                continue

            schedule.status = request.status
            updated_count += 1
            logger.info(f"✅ 상태 업데이트 [schedule_id={schedule.schedule_id}]: {schedule.status} → {request.status}")

        # 트랜잭션 커밋
        try:
            db.commit()
            logger.info(f"✅ 스케줄 상태 업데이트 완료: {updated_count}개 스케줄 → {request.status}")
        except Exception as commit_error:
            db.rollback()
            logger.error(f"❌ 트랜잭션 커밋 실패: {str(commit_error)}")
            raise HTTPException(
                status_code=500,
                detail="스케줄 상태 업데이트 중 데이터베이스 오류가 발생했습니다"
            )

        # 응답 반환
        if failed_transitions:
            logger.warning(f"⚠️ 일부 스케줄의 상태 전환에 실패했습니다: {len(failed_transitions)}개")
            return {
                "success": True,
                "status": "success",
                "updated_count": updated_count,
                "failed_count": len(failed_transitions),
                "failed_transitions": failed_transitions,
                "message": f"{updated_count}개의 스케줄이 {request.status} 상태로 변경되었습니다. ({len(failed_transitions)}개 실패)"
            }

        return {
            "success": True,
            "status": "success",
            "updated_count": updated_count,
            "message": f"{updated_count}개의 스케줄이 {request.status} 상태로 변경되었습니다."
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 스케줄 상태 업데이트 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"스케줄 상태 업데이트 중 오류가 발생했습니다: {str(e)}"
        )
