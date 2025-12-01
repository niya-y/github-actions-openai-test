"""
FastAPI Routes: 식단 추천 API
================================
파일 위치: backend/app/routes/meal_plans.py
백엔드 팀 컨벤션 100% 준수 버전

작성자: AI/ML 팀
최종 수정: 2024-12
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

# 백엔드 표준 import 경로
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import Guardian, Patient
from app.models.care_details import HealthCondition, Medication, DietaryPreference
from app.models.care_execution import MealPlan
from app.schemas.meal_plan import (
    MealPlanCreate, MealPlanResponse, MealPlanGenerateRequest,
    MealPlanUpdate, DietaryConstraintsResponse
)

# 식단 추천 서비스
from app.services.meal_recommendation import (
    MealRecommendationService,
    MealRecommendationConfig,
    PatientDietaryAnalyzer
)

# APIRouter 생성
router = APIRouter(
    prefix="/api/meal-plans",
    tags=["Meal Plans"]
)

# ============================================
# 헬퍼 함수
# ============================================

def verify_patient_access(
    patient_id: int,
    current_user: User,
    db: Session
) -> tuple[Patient, Guardian]:
    """
    환자 접근 권한 확인
    
    Returns:
        (Patient, Guardian) 튜플
    
    Raises:
        HTTPException: 환자를 찾을 수 없거나 권한이 없을 경우
    """
    # 환자 존재 확인
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다"
        )
    
    # 보호자 권한 확인
    if current_user.user_type.value != "guardian":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="보호자만 접근할 수 있습니다"
        )
    
    guardian = db.query(Guardian).filter(
        Guardian.user_id == current_user.user_id
    ).first()
    
    if not guardian or patient.guardian_id != guardian.guardian_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 환자의 정보를 조회할 권한이 없습니다"
        )
    
    return patient, guardian


def collect_patient_data(patient_id: int, db: Session) -> dict:
    """
    환자 데이터 수집 (질병, 약물, 알레르기)
    
    Args:
        patient_id: 환자 ID
        db: DB 세션
    
    Returns:
        dict: 환자 정보, 질병, 약물, 알레르기 데이터
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
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


# ============================================
# 14.1 환자 식단 목록 조회
# ============================================

@router.get(
    "/patients/{patient_id}/meals",
    response_model=List[MealPlanResponse]
)
async def get_patient_meal_plans(
    patient_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    meal_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자의 식단 목록 조회
    
    **경로 파라미터**:
    - patient_id: 환자 ID
    
    **쿼리 파라미터**:
    - start_date: 시작일 (YYYY-MM-DD, 선택)
    - end_date: 종료일 (YYYY-MM-DD, 선택)
    - meal_type: breakfast, lunch, dinner, snack (선택)
    
    **인증**: 필수 (JWT Bearer Token, guardian만)
    
    **응답**: `MealPlanResponse` 리스트
    """
    # 권한 확인
    verify_patient_access(patient_id, current_user, db)
    
    # 식단 조회
    query = db.query(MealPlan).filter(MealPlan.patient_id == patient_id)
    
    if start_date:
        query = query.filter(MealPlan.meal_date >= start_date)
    if end_date:
        query = query.filter(MealPlan.meal_date <= end_date)
    if meal_type:
        query = query.filter(MealPlan.meal_type == meal_type)
    
    meals = query.order_by(MealPlan.meal_date.desc()).all()
    
    return meals


# ============================================
# 14.2 특정 날짜/시간 식단 조회
# ============================================

@router.get(
    "/patients/{patient_id}/meals/{meal_date}/{meal_type}",
    response_model=MealPlanResponse
)
async def get_specific_meal_plan(
    patient_id: int,
    meal_date: date,
    meal_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 날짜/시간의 식단 조회
    
    **경로 파라미터**:
    - patient_id: 환자 ID
    - meal_date: 식단 날짜 (YYYY-MM-DD)
    - meal_type: breakfast, lunch, dinner, snack
    
    **인증**: 필수 (JWT Bearer Token, guardian만)
    
    **응답**: `MealPlanResponse`
    """
    # 권한 확인
    verify_patient_access(patient_id, current_user, db)
    
    # 식단 조회
    meal = db.query(MealPlan).filter(
        MealPlan.patient_id == patient_id,
        MealPlan.meal_date == meal_date,
        MealPlan.meal_type == meal_type
    ).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="식단을 찾을 수 없습니다"
        )
    
    return meal


# ============================================
# 14.3 AI 식단 생성 (핵심 기능!)
# ============================================

@router.post(
    "/patients/{patient_id}/generate",
    response_model=MealPlanResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_ai_meal_plan(
    patient_id: int,
    request: MealPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🤖 Azure OpenAI 기반 맞춤 식단 생성
    
    **경로 파라미터**:
    - patient_id: 환자 ID
    
    **요청 본문** (`MealPlanGenerateRequest`):
    ```json
    {
        "meal_date": "2025-01-15",
        "meal_type": "lunch"
    }
    ```
    
    **프로세스**:
    1. 환자 정보 수집 (질병, 약물, 알레르기)
    2. 약물-음식 상호작용 분석
    3. 질병별 추천/회피 음식 파악
    4. Azure OpenAI GPT-4o로 맞춤 식단 생성
    5. DB 저장 후 반환
    
    **인증**: 필수 (JWT Bearer Token, guardian만)
    
    **응답**: `MealPlanResponse` (201 Created)
    """
    # 1. 권한 확인
    verify_patient_access(patient_id, current_user, db)
    
    # 2. 환자 데이터 수집
    data = collect_patient_data(patient_id, db)
    
    # 3. AI 식단 생성 서비스 호출
    config = MealRecommendationConfig()
    service = MealRecommendationService(config)
    
    try:
        meal_plan_data = service.recommend_meal(
            patient_id=patient_id,
            patient_data=data["patient_data"],
            health_conditions=data["health_conditions"],
            medications=data["medications"],
            dietary_prefs=data["dietary_prefs"],
            meal_date=str(request.meal_date),
            meal_type=request.meal_type
        )
        
        if not meal_plan_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI 식단 생성에 실패했습니다"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 식단 생성 중 오류가 발생했습니다: {str(e)}"
        )
    
    # 4. DB 저장
    # ingredients를 문자열로 변환
    ingredients_str = (
        ', '.join(meal_plan_data['ingredients']) 
        if isinstance(meal_plan_data['ingredients'], list)
        else meal_plan_data['ingredients']
    )
    
    new_meal = MealPlan(
        patient_id=patient_id,
        meal_date=request.meal_date,
        meal_type=request.meal_type,
        menu_name=meal_plan_data['menu_name'],
        ingredients=ingredients_str,
        nutrition_info=meal_plan_data['nutrition_info'],
        cooking_tips=meal_plan_data.get('cooking_tips'),
        created_at=datetime.now()
    )
    
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    
    return new_meal


# ============================================
# 14.4 환자 식단 제약사항 조회
# ============================================

@router.get(
    "/patients/{patient_id}/dietary-constraints",
    response_model=DietaryConstraintsResponse
)
async def get_patient_dietary_constraints(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자의 식단 제약사항 요약 조회
    
    프론트엔드에서 식단 제약사항을 표시할 때 사용
    
    **경로 파라미터**:
    - patient_id: 환자 ID
    
    **인증**: 필수 (JWT Bearer Token, guardian만)
    
    **응답** (`DietaryConstraintsResponse`):
    ```json
    {
        "patient_id": 1,
        "patient_name": "김할머니",
        "allergy_foods": ["땅콩", "새우"],
        "restriction_foods": ["밀가루"],
        "drug_avoid_foods": ["자몽", "술"],
        "drug_recommend_foods": ["오트밀", "연어"],
        "disease_avoid_foods": ["소금", "설탕"],
        "disease_recommend_foods": ["현미", "채소"],
        "all_avoid_foods": [...],
        "all_recommend_foods": [...]
    }
    ```
    """
    # 권한 확인
    patient, _ = verify_patient_access(patient_id, current_user, db)
    
    # 환자 데이터 수집
    data = collect_patient_data(patient_id, db)
    
    # 제약사항 분석
    analyzer = PatientDietaryAnalyzer()
    constraints = analyzer.analyze_patient_constraints(
        patient_id=patient_id,
        patient_data=data["patient_data"],
        health_conditions=data["health_conditions"],
        medications=data["medications"],
        dietary_prefs=data["dietary_prefs"]
    )
    
    # patient_name 추가
    constraints['patient_name'] = patient.name
    
    return constraints


# ============================================
# 14.5 식단 수정
# ============================================

@router.put(
    "/meals/{plan_id}",
    response_model=MealPlanResponse
)
async def update_meal_plan(
    plan_id: int,
    update_data: MealPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    기존 식단 수정
    
    **경로 파라미터**:
    - plan_id: 식단 계획 ID
    
    **요청 본문** (`MealPlanUpdate`):
    ```json
    {
        "menu_name": "수정된 메뉴명",
        "ingredients": "수정된 재료",
        "cooking_tips": "수정된 조리 팁"
    }
    ```
    
    **인증**: 필수 (JWT Bearer Token, guardian만)
    
    **응답**: `MealPlanResponse`
    """
    # 식단 조회
    meal = db.query(MealPlan).filter(MealPlan.plan_id == plan_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="식단을 찾을 수 없습니다"
        )
    
    # 권한 확인
    verify_patient_access(meal.patient_id, current_user, db)
    
    # 수정
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(meal, key, value)
    
    db.commit()
    db.refresh(meal)
    
    return meal


# ============================================
# 14.6 식단 삭제
# ============================================

@router.delete(
    "/meals/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_meal_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    식단 삭제
    
    **경로 파라미터**:
    - plan_id: 식단 계획 ID
    
    **인증**: 필수 (JWT Bearer Token, guardian만)
    
    **응답**: 204 No Content
    """
    # 식단 조회
    meal = db.query(MealPlan).filter(MealPlan.plan_id == plan_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="식단을 찾을 수 없습니다"
        )
    
    # 권한 확인
    verify_patient_access(meal.patient_id, current_user, db)
    
    # 삭제
    db.delete(meal)
    db.commit()
    
    return None
