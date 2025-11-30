"""
Profile (Guardian, Patient, Caregiver) FastAPI router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db

# Guardian imports
from app.schemas.guardian import GuardianCreate, GuardianUpdate, GuardianResponse
from app.crud.guardian import (
    get_guardian,
    get_guardians,
    create_guardian,
    update_guardian,
    delete_guardian,
)

# Patient imports
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.crud.patient import (
    get_patient,
    get_patients,
    create_patient,
    update_patient,
    delete_patient,
)

# Caregiver imports
from app.schemas.caregiver import CaregiverCreate, CaregiverUpdate, CaregiverResponse
from app.crud.caregiver import (
    get_caregiver,
    get_caregivers,
    create_caregiver,
    update_caregiver,
    delete_caregiver,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])

# ---------------------------------------------------------------------------
# Guardian endpoints
# ---------------------------------------------------------------------------

@router.get("/guardians", response_model=list[GuardianResponse])
def list_guardians(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_guardians(db, skip=skip, limit=limit)


@router.get("/guardians/{guardian_id}", response_model=GuardianResponse)
def read_guardian(guardian_id: int, db: Session = Depends(get_db)):
    guardian = get_guardian(db, guardian_id)
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return guardian


@router.post("/guardians", response_model=GuardianResponse, status_code=status.HTTP_201_CREATED)
def create_new_guardian(payload: GuardianCreate, db: Session = Depends(get_db)):
    return create_guardian(db, payload)


@router.put("/guardians/{guardian_id}", response_model=GuardianResponse)
def update_existing_guardian(guardian_id: int, payload: GuardianUpdate, db: Session = Depends(get_db)):
    guardian = get_guardian(db, guardian_id)
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return update_guardian(db, guardian, payload)


@router.delete("/guardians/{guardian_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_guardian(guardian_id: int, db: Session = Depends(get_db)):
    guardian = get_guardian(db, guardian_id)
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    delete_guardian(db, guardian_id)
    return None

# ---------------------------------------------------------------------------
# Patient endpoints
# ---------------------------------------------------------------------------

@router.get("/patients", response_model=list[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_patients(db, skip=skip, limit=limit)


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_new_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    return create_patient(db, payload)


@router.put("/patients/{patient_id}", response_model=PatientResponse)
def update_existing_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return update_patient(db, patient, payload)


@router.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    delete_patient(db, patient_id)
    return None

# ---------------------------------------------------------------------------
# Caregiver endpoints
# ---------------------------------------------------------------------------

@router.get("/caregivers", response_model=list[CaregiverResponse])
def list_caregivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_caregivers(db, skip=skip, limit=limit)


@router.get("/caregivers/{caregiver_id}", response_model=CaregiverResponse)
def read_caregiver(caregiver_id: int, db: Session = Depends(get_db)):
    caregiver = get_caregiver(db, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return caregiver


@router.post("/caregivers", response_model=CaregiverResponse, status_code=status.HTTP_201_CREATED)
def create_new_caregiver(payload: CaregiverCreate, db: Session = Depends(get_db)):
    return create_caregiver(db, payload)


@router.put("/caregivers/{caregiver_id}", response_model=CaregiverResponse)
def update_existing_caregiver(caregiver_id: int, payload: CaregiverUpdate, db: Session = Depends(get_db)):
    caregiver = get_caregiver(db, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return update_caregiver(db, caregiver, payload)


@router.delete("/caregivers/{caregiver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_caregiver(caregiver_id: int, db: Session = Depends(get_db)):
    caregiver = get_caregiver(db, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    delete_caregiver(db, caregiver_id)
    return None
