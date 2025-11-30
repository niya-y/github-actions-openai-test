"""
CRUD operations for MealPlan model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.care_execution import MealPlan
from app.schemas.meal_plan import MealPlanCreate, MealPlanUpdate, MealPlanResponse


def get_meal_plan(db: Session, plan_id: int) -> Optional[MealPlan]:
    return db.query(MealPlan).filter(MealPlan.plan_id == plan_id).first()


def get_meal_plans(db: Session, skip: int = 0, limit: int = 100) -> List[MealPlan]:
    return db.query(MealPlan).offset(skip).limit(limit).all()


def create_meal_plan(db: Session, obj_in: MealPlanCreate) -> MealPlan:
    db_obj = MealPlan(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_meal_plan(db: Session, meal_plan: MealPlan, obj_in: MealPlanUpdate) -> MealPlan:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(meal_plan, field, value)
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)
    return meal_plan


def delete_meal_plan(db: Session, plan_id: int) -> None:
    db.query(MealPlan).filter(MealPlan.plan_id == plan_id).delete()
    db.commit()
