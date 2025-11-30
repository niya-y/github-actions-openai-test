"""
Patient API (프론트엔드 계약용)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import Guardian, Patient
from app.models.care_details import HealthCondition, Medication
from app.schemas.patient import (
    PatientCreateRequest,
    PatientInfoResponse,
    HealthStatusUpdateRequest,
    MedicationsCreateRequest,
    MedicationInfoResponse
)

router = APIRouter(prefix="/api", tags=["Patients"])


@router.post("/patients", status_code=status.HTTP_201_CREATED, response_model=PatientInfoResponse)
async def create_patient(
    request: PatientCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 기본 정보 등록
    
    1. 현재 사용자의 guardian_id 가져오기
    2. 나이를 생년월일로 변환
    3. patients 테이블에 저장
    """
    # 1. 현재 사용자의 guardian_id 가져오기
    guardian = db.query(Guardian).filter(
        Guardian.user_id == current_user.user_id
    ).first()
    
    if not guardian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보호자 정보를 먼저 등록해주세요"
        )
    
    # 2. 나이를 생년월일로 변환 (백엔드 로직)
    current_year = date.today().year
    birth_date = date(current_year - request.age, 1, 1)
    
    # 3. patients 테이블에 저장
    patient = Patient(
        guardian_id=guardian.guardian_id,
        name=request.name,
        birth_date=birth_date,
        gender=request.gender,  # validator에서 이미 변환됨 (Male/Female)
        care_address=guardian.address,  # 보호자 주소 사용
        region_code="TBD"  # 나중에 업데이트
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # 4. 응답 반환
    return PatientInfoResponse(
        patient_id=patient.patient_id,
        name=patient.name,
        birth_date=patient.birth_date.isoformat(),
        age=request.age,
        gender=patient.gender.value,  # Enum을 문자열로 변환
        guardian_id=guardian.guardian_id,
        created_at=patient.created_at.isoformat()
    )


@router.get("/patients/me", response_model=dict)
async def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 보호자의 모든 환자 목록 조회 + 가장 최근 환자

    응답:
    {
        "patients": [
            {"patient_id": 1, "name": "김철수", "age": 75, "gender": "Male", ...},
            ...
        ],
        "latest_patient": {...},  # 가장 최근에 생성된 환자
        "total": 3
    }
    """
    # 보호자 정보 가져오기
    guardian = db.query(Guardian).filter(
        Guardian.user_id == current_user.user_id
    ).first()

    if not guardian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보호자 정보를 먼저 등록해주세요"
        )

    # 모든 환자 조회 (최신 순)
    patients = db.query(Patient).filter(
        Patient.guardian_id == guardian.guardian_id
    ).order_by(Patient.created_at.desc()).all()

    if not patients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 환자가 없습니다"
        )

    # 응답 형식으로 변환
    patients_list = [
        {
            "patient_id": p.patient_id,
            "name": p.name,
            "age": (date.today().year - p.birth_date.year) if p.birth_date else None,
            "birth_date": p.birth_date.isoformat() if p.birth_date else None,
            "gender": p.gender.value,
            "created_at": p.created_at.isoformat()
        }
        for p in patients
    ]

    return {
        "patients": patients_list,
        "latest_patient": patients_list[0],  # 가장 최근 환자
        "total": len(patients_list)
    }


@router.get("/patients/{patient_id}", response_model=PatientInfoResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 환자 정보 조회 (권한 확인)

    응답:
    {
        "patient_id": 1,
        "name": "김철수",
        "age": 75,
        "gender": "Male",
        "birth_date": "1950-01-01",
        "guardian_id": 1,
        "created_at": "2025-11-29T10:30:00"
    }
    """
    # 환자 조회 + 권한 확인
    patient = db.query(Patient).join(Guardian).filter(
        Patient.patient_id == patient_id,
        Guardian.user_id == current_user.user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 환자에 대한 접근 권한이 없습니다"
        )

    # 나이 계산
    age = (date.today().year - patient.birth_date.year) if patient.birth_date else 0

    return PatientInfoResponse(
        patient_id=patient.patient_id,
        name=patient.name,
        age=age,
        gender=patient.gender.value,
        birth_date=patient.birth_date.isoformat() if patient.birth_date else None,
        guardian_id=patient.guardian_id,
        created_at=patient.created_at.isoformat()
    )


@router.get("/patients/{patient_id}/health-status", status_code=status.HTTP_200_OK)
async def get_health_status(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 건강 상태 조회

    1. 환자 접근 권한 확인
    2. health_conditions에서 질병 및 거동 상태 조회
    """
    # 1. 환자 접근 권한 확인
    patient = db.query(Patient).join(Guardian).filter(
        Patient.patient_id == patient_id,
        Guardian.user_id == current_user.user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 환자에 대한 접근 권한이 없습니다"
        )

    # 2. health_conditions 조회
    health_conditions = db.query(HealthCondition).filter(
        HealthCondition.patient_id == patient_id
    ).all()

    if not health_conditions:
        # 건강 상태가 없는 경우
        return {
            "patient_id": patient_id,
            "selected_diseases": [],
            "mobility_status": ""
        }

    # 질병 정보 추출
    diseases_list = []
    mobility_status = ""

    for hc in health_conditions:
        diseases_list.append({
            "id": hc.disease_name.lower().replace(" ", "-"),
            "name": hc.disease_name
        })

        # note에서 mobility_status 추출
        if hc.note and "Mobility:" in hc.note:
            mobility_status = hc.note.split("Mobility:")[-1].strip()

    return {
        "patient_id": patient_id,
        "selected_diseases": diseases_list,
        "mobility_status": mobility_status
    }


@router.put("/patients/{patient_id}/health-status", status_code=status.HTTP_200_OK)
async def update_health_status(
    patient_id: int,
    request: HealthStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 건강 상태 업데이트
    
    1. 환자 접근 권한 확인
    2. health_conditions 테이블에 JSONB로 저장
    """
    # 1. 환자 접근 권한 확인
    patient = db.query(Patient).join(Guardian).filter(
        Patient.patient_id == patient_id,
        Guardian.user_id == current_user.user_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 환자에 대한 접근 권한이 없습니다"
        )
    
    # 2. health_conditions 테이블에 저장
    # 기존 건강 상태 삭제 (새로 등록하는 경우)
    db.query(HealthCondition).filter(
        HealthCondition.patient_id == patient_id
    ).delete()

    # selectedDiseases를 개별 레코드로 저장
    diseases_list = []
    for disease in request.selectedDiseases:
        # disease가 Pydantic 모델인 경우 dict로 변환
        if hasattr(disease, 'model_dump'):
            disease_dict = disease.model_dump()
        elif isinstance(disease, dict):
            disease_dict = disease
        else:
            disease_dict = disease.dict() if hasattr(disease, 'dict') else dict(disease)

        disease_name = disease_dict.get('name', disease_dict.get('id', 'Unknown'))

        health_condition = HealthCondition(
            patient_id=patient_id,
            disease_name=disease_name,
            note=f"Mobility: {request.mobility_status}"
        )
        db.add(health_condition)
        diseases_list.append(disease_dict)

    db.commit()

    # 3. 응답 반환
    return {
        "patient_id": patient_id,
        "selected_diseases": diseases_list,
        "mobility_status": request.mobility_status,
        "updated_at": datetime.now().isoformat()
    }


@router.get("/patients/{patient_id}/medications", status_code=status.HTTP_200_OK)
async def get_medications(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 약물 정보 조회

    1. 환자 접근 권한 확인
    2. medications에서 약물 정보 조회
    """
    # 1. 환자 접근 권한 확인
    patient = db.query(Patient).join(Guardian).filter(
        Patient.patient_id == patient_id,
        Guardian.user_id == current_user.user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 환자에 대한 접근 권한이 없습니다"
        )

    # 2. medications 조회
    medication = db.query(Medication).filter(
        Medication.patient_id == patient_id
    ).first()

    if not medication:
        # 약물 정보가 없는 경우
        return {
            "patient_id": patient_id,
            "medicine_names": []
        }

    # medicine_names 반환 (있으면)
    medicine_names = []
    if hasattr(medication, 'medicine_names') and medication.medicine_names:
        medicine_names = medication.medicine_names if isinstance(medication.medicine_names, list) else [medication.medicine_names]

    return {
        "patient_id": patient_id,
        "medicine_names": medicine_names
    }


@router.post("/patients/{patient_id}/medications", status_code=status.HTTP_201_CREATED, response_model=MedicationInfoResponse)
async def create_medications(
    patient_id: int,
    request: MedicationsCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 복용 약물 등록
    
    1. 환자 접근 권한 확인
    2. medications 테이블에 TEXT[] 배열로 저장
    """
    # 1. 환자 접근 권한 확인
    patient = db.query(Patient).join(Guardian).filter(
        Patient.patient_id == patient_id,
        Guardian.user_id == current_user.user_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 환자에 대한 접근 권한이 없습니다"
        )
    
    # 2. medications 테이블에 저장
    # 기존 약물 정보가 있는지 확인
    medication = db.query(Medication).filter(
        Medication.patient_id == patient_id
    ).first()
    
    if not medication:
        # 새로운 약물 정보 생성
        medication = Medication(
            patient_id=patient_id,
            name=None,  # 기존 컬럼은 사용하지 않음
            dosage=None,
            frequency=None,
            intake_method=None
        )
        db.add(medication)
    
    # medicine_names 필드 업데이트 (DB 스키마에 medicine_names 컬럼이 있다고 가정)
    if hasattr(medication, 'medicine_names'):
        medication.medicine_names = request.medicine_names
    
    db.commit()
    db.refresh(medication)
    
    # 3. 응답 반환
    return MedicationInfoResponse(
        patient_id=patient_id,
        med_id=medication.med_id,
        medicine_names=request.medicine_names
    )
