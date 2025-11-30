"""
CRUD operations for Schedule model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.care_execution import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse


def get_schedule(db: Session, schedule_id: int) -> Optional[Schedule]:
    return db.query(Schedule).filter(Schedule.schedule_id == schedule_id).first()


def get_schedules(db: Session, skip: int = 0, limit: int = 100) -> List[Schedule]:
    return db.query(Schedule).offset(skip).limit(limit).all()


def create_schedule(db: Session, obj_in: ScheduleCreate) -> Schedule:
    db_obj = Schedule(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_schedule(db: Session, schedule: Schedule, obj_in: ScheduleUpdate) -> Schedule:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(schedule, field, value)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def delete_schedule(db: Session, schedule_id: int) -> None:
    db.query(Schedule).filter(Schedule.schedule_id == schedule_id).delete()
    db.commit()
