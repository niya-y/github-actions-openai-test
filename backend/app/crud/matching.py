"""
CRUD operations for Matching models (MatchingRequest, MatchingResult, CaregiverAvailability).
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.matching import MatchingRequest, MatchingResult, CaregiverAvailability
from app.schemas.matching import (
    MatchingRequestCreate,
    MatchingRequestUpdate,
    MatchingResultCreate,
    MatchingResultUpdate,
    CaregiverAvailabilityCreate,
    CaregiverAvailabilityUpdate,
)

# ------------------- MatchingRequest CRUD -------------------

def get_matching_request(db: Session, request_id: int) -> Optional[MatchingRequest]:
    return db.query(MatchingRequest).filter(MatchingRequest.request_id == request_id).first()


def get_matching_requests(db: Session, skip: int = 0, limit: int = 100) -> List[MatchingRequest]:
    return db.query(MatchingRequest).offset(skip).limit(limit).all()


def create_matching_request(db: Session, obj_in: MatchingRequestCreate) -> MatchingRequest:
    db_obj = MatchingRequest(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_matching_request(db: Session, request: MatchingRequest, obj_in: MatchingRequestUpdate) -> MatchingRequest:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(request, field, value)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def delete_matching_request(db: Session, request_id: int) -> None:
    db.query(MatchingRequest).filter(MatchingRequest.request_id == request_id).delete()
    db.commit()

# ------------------- MatchingResult CRUD -------------------

def get_matching_result(db: Session, result_id: int) -> Optional[MatchingResult]:
    return db.query(MatchingResult).filter(MatchingResult.matching_id == result_id).first()


def get_matching_results(db: Session, skip: int = 0, limit: int = 100) -> List[MatchingResult]:
    return db.query(MatchingResult).offset(skip).limit(limit).all()


def create_matching_result(db: Session, obj_in: MatchingResultCreate) -> MatchingResult:
    db_obj = MatchingResult(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_matching_result(db: Session, result: MatchingResult, obj_in: MatchingResultUpdate) -> MatchingResult:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(result, field, value)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def delete_matching_result(db: Session, result_id: int) -> None:
    db.query(MatchingResult).filter(MatchingResult.matching_id == result_id).delete()
    db.commit()

# ------------------- CaregiverAvailability CRUD -------------------

def get_availability(db: Session, availability_id: int) -> Optional[CaregiverAvailability]:
    return db.query(CaregiverAvailability).filter(CaregiverAvailability.availability_id == availability_id).first()


def get_availabilities(db: Session, skip: int = 0, limit: int = 100) -> List[CaregiverAvailability]:
    return db.query(CaregiverAvailability).offset(skip).limit(limit).all()


def create_availability(db: Session, obj_in: CaregiverAvailabilityCreate) -> CaregiverAvailability:
    db_obj = CaregiverAvailability(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_availability(db: Session, availability: CaregiverAvailability, obj_in: CaregiverAvailabilityUpdate) -> CaregiverAvailability:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(availability, field, value)
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability


def delete_availability(db: Session, availability_id: int) -> None:
    db.query(CaregiverAvailability).filter(CaregiverAvailability.availability_id == availability_id).delete()
    db.commit()
