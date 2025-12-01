"""
Pydantic Schemas: 식단 추천 API
==================================
파일 위치: backend/app/schemas/meal_plan.py
백엔드 팀 컨벤션 100% 준수 버전

작성자: AI/ML 팀
최종 수정: 2024-12
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


# ============================================
# Enum 정의
# ============================================

class MealTypeEnum(str, Enum):
    """식사 유형"""
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


# ============================================
# Base Schemas
# ============================================

class NutritionInfo(BaseModel):
    """영양 정보"""
    calories: Optional[float] = Field(None, description="칼로리 (kcal)")
    protein_g: Optional[float] = Field(None, description="단백질 (g)")
    carbs_g: Optional[float] = Field(None, description="탄수화물 (g)")
    fat_g: Optional[float] = Field(None, description="지방 (g)")
    sodium_mg: Optional[float] = Field(None, description="나트륨 (mg)")
    fiber_g: Optional[float] = Field(None, description="식이섬유 (g)")
    
    class Config:
        schema_extra = {
            "example": {
                "calories": 450.0,
                "protein_g": 25.0,
                "carbs_g": 55.0,
                "fat_g": 12.0,
                "sodium_mg": 800.0,
                "fiber_g": 8.0
            }
        }


class MealPlanBase(BaseModel):
    """식단 계획 기본 필드"""
    patient_id: int = Field(..., description="환자 ID")
    meal_date: date = Field(..., description="식단 날짜 (YYYY-MM-DD)")
    meal_type: MealTypeEnum = Field(..., description="식사 유형")
    menu_name: str = Field(..., max_length=200, description="메뉴명")
    ingredients: Optional[str] = Field(None, description="재료 목록")
    nutrition_info: Optional[Dict[str, Any]] = Field(None, description="영양 정보 JSON")
    cooking_tips: Optional[str] = Field(None, description="조리 팁")


# ============================================
# Request Schemas (API 요청)
# ============================================

class MealPlanGenerateRequest(BaseModel):
    """AI 식단 생성 요청"""
    meal_date: date = Field(..., description="식단 날짜 (YYYY-MM-DD)")
    meal_type: MealTypeEnum = Field(..., description="식사 유형")
    
    class Config:
        schema_extra = {
            "example": {
                "meal_date": "2025-01-15",
                "meal_type": "lunch"
            }
        }


class MealPlanCreate(MealPlanBase):
    """식단 생성 요청 (수동 입력용)"""
    pass


class MealPlanUpdate(BaseModel):
    """식단 수정 요청"""
    menu_name: Optional[str] = Field(None, max_length=200, description="메뉴명")
    ingredients: Optional[str] = Field(None, description="재료 목록")
    nutrition_info: Optional[Dict[str, Any]] = Field(None, description="영양 정보 JSON")
    cooking_tips: Optional[str] = Field(None, description="조리 팁")
    
    class Config:
        schema_extra = {
            "example": {
                "menu_name": "수정된 메뉴명",
                "ingredients": "수정된 재료 목록",
                "cooking_tips": "수정된 조리 팁"
            }
        }


# ============================================
# Response Schemas (API 응답)
# ============================================

class MealPlanResponse(MealPlanBase):
    """식단 계획 응답"""
    plan_id: int = Field(..., description="식단 계획 ID")
    created_at: datetime = Field(..., description="생성일시")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "plan_id": 1,
                "patient_id": 1,
                "meal_date": "2025-01-15",
                "meal_type": "lunch",
                "menu_name": "현미밥, 두부조림, 시금치나물, 된장국",
                "ingredients": "현미, 두부, 시금치, 된장, 무, 파",
                "nutrition_info": {
                    "calories": 450.0,
                    "protein_g": 25.0,
                    "carbs_g": 55.0,
                    "fat_g": 12.0,
                    "sodium_mg": 800.0,
                    "fiber_g": 8.0
                },
                "cooking_tips": "1. 현미는 6시간 이상 불립니다...",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class DietaryConstraintsResponse(BaseModel):
    """환자 식단 제약사항 응답"""
    patient_id: int = Field(..., description="환자 ID")
    patient_name: str = Field(..., description="환자 이름")
    
    # 절대 금지 음식
    allergy_foods: List[str] = Field(
        default_factory=list,
        description="알레르기 음식 (절대 금지)"
    )
    restriction_foods: List[str] = Field(
        default_factory=list,
        description="식이 제한 음식 (절대 금지)"
    )
    
    # 약물 관련
    drug_avoid_foods: List[str] = Field(
        default_factory=list,
        description="약물-음식 상호작용으로 피해야 할 음식"
    )
    drug_recommend_foods: List[str] = Field(
        default_factory=list,
        description="복용 중인 약물에 좋은 음식"
    )
    
    # 질병 관련
    disease_avoid_foods: List[str] = Field(
        default_factory=list,
        description="질병으로 인해 피해야 할 음식"
    )
    disease_recommend_foods: List[str] = Field(
        default_factory=list,
        description="질병 관리에 도움되는 음식"
    )
    
    # 통합 리스트
    all_avoid_foods: List[str] = Field(
        default_factory=list,
        description="모든 피해야 할 음식 (중복 제거)"
    )
    all_recommend_foods: List[str] = Field(
        default_factory=list,
        description="모든 추천 음식 (중복 제거)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": 1,
                "patient_name": "김할머니",
                "allergy_foods": ["땅콩", "새우"],
                "restriction_foods": ["밀가루"],
                "drug_avoid_foods": ["자몽", "술", "카페인"],
                "drug_recommend_foods": ["오트밀", "연어", "아몬드"],
                "disease_avoid_foods": ["소금", "설탕", "가공식품"],
                "disease_recommend_foods": ["현미", "채소", "등푸른생선"],
                "all_avoid_foods": [
                    "땅콩", "새우", "밀가루", "자몽", "술", 
                    "카페인", "소금", "설탕", "가공식품"
                ],
                "all_recommend_foods": [
                    "오트밀", "연어", "아몬드", "현미", 
                    "채소", "등푸른생선"
                ]
            }
        }


# ============================================
# 주간 식단 생성 요청 (선택 사항)
# ============================================

class WeeklyMealPlanGenerateRequest(BaseModel):
    """주간 식단 일괄 생성 요청"""
    start_date: date = Field(..., description="시작일 (월요일)")
    
    @validator('start_date')
    def validate_monday(cls, v):
        """시작일이 월요일인지 확인"""
        if v.weekday() != 0:  # 0 = Monday
            raise ValueError('start_date는 월요일이어야 합니다')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2025-01-13"  # 월요일
            }
        }
