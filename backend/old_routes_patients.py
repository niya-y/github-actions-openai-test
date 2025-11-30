"""
환자 관리 API 라우터
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.patient import Patient, PatientHealthStatus, PatientDetails
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientCompleteResponse,
    PatientHealthStatusCreate,
    PatientHealthStatusUpdate,
    PatientHealthStatusResponse,
    PatientDetailsCreate,
    PatientDetailsUpdate,
    PatientDetailsResponse,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새 환자 등록
    
    - **name**: 환자 이름
    - **age**: 환자 나이
    - **gender**: 성별 (male/female)
    - **relationship_to_guardian**: 보호자와의 관계
    """
    patient = Patient(
        user_id=current_user.id,
        **patient_data.model_dump()
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    return patient


@router.get("", response_model=List[PatientCompleteResponse])
def list_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 모든 환자 목록 조회
    """
    patients = db.query(Patient).options(
        joinedload(Patient.health_status),
        joinedload(Patient.details)
    ).filter(Patient.user_id == current_user.id).all()
    
    return patients


@router.get("/{patient_id}", response_model=PatientCompleteResponse)
def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 환자 정보 조회 (건강 상태 및 상세 정보 포함)
    """
    patient = db.query(Patient).options(
        joinedload(Patient.health_status),
        joinedload(Patient.details)
    ).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다"
        )
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 기본 정보 수정
    """
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다"
        )
    
    # 수정된 필드만 업데이트
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 정보 삭제
    """
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다"
        )
    
    db.delete(patient)
    db.commit()
    
    return None


# Health Status Endpoints
@router.put("/{patient_id}/health", response_model=PatientHealthStatusResponse)
def update_health_status(
    patient_id: int,
    health_data: PatientHealthStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 건강 상태 정보 업데이트
    """
    # 환자 소유권 확인
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다"
        )
    
    # 기존 건강 상태 조회 또는 생성
    health_status = db.query(PatientHealthStatus).filter(
        PatientHealthStatus.patient_id == patient_id
    ).first()
    
    if health_status:
        # 업데이트
        update_data = health_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(health_status, field, value)
    else:
        # 새로 생성
        health_status = PatientHealthStatus(
            patient_id=patient_id,
            **health_data.model_dump()
        )
        db.add(health_status)
    
    db.commit()
    db.refresh(health_status)
    
    return health_status


# Patient Details Endpoints
@router.put("/{patient_id}/details", response_model=PatientDetailsResponse)
def update_patient_details(
    patient_id: int,
    details_data: PatientDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 상세 정보 업데이트
    """
    # 환자 소유권 확인
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다"
        )
    
    # 기존 상세 정보 조회 또는 생성
    details = db.query(PatientDetails).filter(
        PatientDetails.patient_id == patient_id
    ).first()
    
    if details:
        # 업데이트
        update_data = details_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(details, field, value)
    else:
        # 새로 생성
        details = PatientDetails(
            patient_id=patient_id,
            **details_data.model_dump()
        )
        db.add(details)
    
    db.commit()
    db.refresh(details)
    
    return details
