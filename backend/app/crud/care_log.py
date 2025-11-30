"""
CRUD operations for CareLog model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.care_execution import CareLog
from app.schemas.care_log import CareLogCreate, CareLogUpdate, CareLogResponse


def get_care_log(db: Session, log_id: int) -> Optional[CareLog]:
    return db.query(CareLog).filter(CareLog.log_id == log_id).first()


def get_care_logs(db: Session, skip: int = 0, limit: int = 100) -> List[CareLog]:
    return db.query(CareLog).offset(skip).limit(limit).all()


def create_care_log(db: Session, obj_in: CareLogCreate) -> CareLog:
    db_obj = CareLog(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_care_log(db: Session, care_log: CareLog, obj_in: CareLogUpdate) -> CareLog:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(care_log, field, value)
    db.add(care_log)
    db.commit()
    db.refresh(care_log)
    return care_log


def delete_care_log(db: Session, log_id: int) -> None:
    db.query(CareLog).filter(CareLog.log_id == log_id).delete()
    db.commit()
