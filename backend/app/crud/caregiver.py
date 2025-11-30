"""
CRUD operations for Caregiver model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.profile import Caregiver
from app.schemas.caregiver import CaregiverCreate, CaregiverUpdate, CaregiverResponse


def get_caregiver(db: Session, caregiver_id: int) -> Optional[Caregiver]:
    return db.query(Caregiver).filter(Caregiver.caregiver_id == caregiver_id).first()


def get_caregivers(db: Session, skip: int = 0, limit: int = 100) -> List[Caregiver]:
    return db.query(Caregiver).offset(skip).limit(limit).all()


def create_caregiver(db: Session, obj_in: CaregiverCreate) -> Caregiver:
    db_obj = Caregiver(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_caregiver(db: Session, caregiver: Caregiver, obj_in: CaregiverUpdate) -> Caregiver:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(caregiver, field, value)
    db.add(caregiver)
    db.commit()
    db.refresh(caregiver)
    return caregiver


def delete_caregiver(db: Session, caregiver_id: int) -> None:
    db.query(Caregiver).filter(Caregiver.caregiver_id == caregiver_id).delete()
    db.commit()
