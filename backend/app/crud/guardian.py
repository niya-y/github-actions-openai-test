"""
CRUD operations for Guardian model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.profile import Guardian
from app.schemas.guardian import GuardianCreate, GuardianUpdate, GuardianResponse


def get_guardian(db: Session, guardian_id: int) -> Optional[Guardian]:
    return db.query(Guardian).filter(Guardian.guardian_id == guardian_id).first()


def get_guardians(db: Session, skip: int = 0, limit: int = 100) -> List[Guardian]:
    return db.query(Guardian).offset(skip).limit(limit).all()


def create_guardian(db: Session, obj_in: GuardianCreate) -> Guardian:
    db_obj = Guardian(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_guardian(db: Session, guardian: Guardian, obj_in: GuardianUpdate) -> Guardian:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(guardian, field, value)
    db.add(guardian)
    db.commit()
    db.refresh(guardian)
    return guardian


def delete_guardian(db: Session, guardian_id: int) -> None:
    db.query(Guardian).filter(Guardian.guardian_id == guardian_id).delete()
    db.commit()
