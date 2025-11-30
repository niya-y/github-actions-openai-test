"""
CRUD operations for Patient model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.profile import Patient
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse


def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.patient_id == patient_id).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100) -> List[Patient]:
    return db.query(Patient).offset(skip).limit(limit).all()


def create_patient(db: Session, obj_in: PatientCreate) -> Patient:
    db_obj = Patient(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_patient(db: Session, patient: Patient, obj_in: PatientUpdate) -> Patient:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(patient, field, value)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient_id: int) -> None:
    db.query(Patient).filter(Patient.patient_id == patient_id).delete()
    db.commit()
