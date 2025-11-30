"""
Meal Plan Pydantic 스키마
"""

from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.care_execution import MealTypeEnum


class MealPlanBase(BaseModel):
    """식사 계획 기본 스키마"""
    meal_date: date
    meal_type: MealTypeEnum
    menu_name: str = Field(..., max_length=200)
    ingredients: Optional[str] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    cooking_tips: Optional[str] = None


class MealPlanCreate(MealPlanBase):
    """식사 계획 생성 스키마"""
    patient_id: int


class MealPlanUpdate(BaseModel):
    """식사 계획 수정 스키마"""
    menu_name: Optional[str] = Field(None, max_length=200)
    ingredients: Optional[str] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    cooking_tips: Optional[str] = None


class MealPlanResponse(MealPlanBase):
    """식사 계획 응답 스키마"""
    plan_id: int
    patient_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
