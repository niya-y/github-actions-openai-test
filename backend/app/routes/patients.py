"""
Patient API (프론트엔드 계약용)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import Guardian, Patient, Caregiver
from app.models.care_details import HealthCondition, Medication, DietaryPreference
from app.schemas.patient import (
    PatientCreateRequest,
    PatientInfoResponse,
    HealthStatusUpdateRequest,
    MedicationsCreateRequest,
    MedicationInfoResponse,
    DietaryPreferencesCreateRequest,
    DietaryPreferencesResponse
)

router = APIRouter(tags=["Patients"])

# 질병 한글 이름 → ID 매핑
DISEASE_MAPPING = {
    '치매/인지장애': 'dementia',
    '뇌졸중/중풍': 'stroke',
    '암': 'cancer',
    '파킨슨병': 'parkinsons',
    '고혈압': 'hypertension',
    '당뇨병': 'diabetes'
}


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
    """
    print(f"🔍 [DEBUG] get_my_patients 호출됨. User ID: {current_user.user_id}, Name: {current_user.name}")

    # 보호자 정보 가져오기 (ORM 관계 활용)
    guardian = current_user.guardian

    if not guardian:
        # 혹시 관계 로딩이 안 되었을 수 있으므로 직접 쿼리 시도
        guardian = db.query(Guardian).filter(Guardian.user_id == current_user.user_id).first()

    print(f"🔍 [DEBUG] Guardian 조회 결과: {guardian}")

    if not guardian:
        print(f"⚠️ [WARN] Guardian 정보를 찾을 수 없음! (User ID: {current_user.user_id}) -> 자동 생성 시도")
        try:
            # 보호자 정보가 없으면 자동 생성 (사용자 편의성)
            phone = getattr(current_user, 'phone_number', "010-0000-0000")
            guardian = Guardian(
                user_id=current_user.user_id,
                name=current_user.name,
                phone=phone,
                address="주소를 입력해주세요",
                relationship="본인"
            )
            db.add(guardian)
            db.commit()
            db.refresh(guardian)
            print(f"✅ [INFO] 보호자 정보 자동 생성 완료: {current_user.user_id}")
        except Exception as e:
            print(f"⚠️ [WARN] 보호자 자동 생성 실패 (이미 존재할 수 있음): {e}")
            db.rollback()
            # 생성 실패 시 다시 조회 시도
            guardian = db.query(Guardian).filter(Guardian.user_id == current_user.user_id).first()
            
        if not guardian:
             # 그래도 없으면 에러
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="보호자 정보를 생성할 수 없습니다."
            )

    # 모든 환자 조회 (최신 순)
    patients = db.query(Patient).filter(
        Patient.guardian_id == guardian.guardian_id
    ).order_by(Patient.created_at.desc()).all()

    if not patients:
        # 환자가 없으면 빈 리스트 반환 (404 에러 아님)
        return {
            "patients": [],
            "latest_patient": None,
            "total": 0
        }

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
        # 매핑된 ID 또는 기본값 사용
        disease_id = DISEASE_MAPPING.get(hc.disease_name, hc.disease_name.lower().replace(" ", "-"))
        diseases_list.append({
            "id": disease_id,
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
            medicine_names=None,
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


@router.get("/patients/{patient_id}/dietary-preferences", status_code=status.HTTP_200_OK)
async def get_dietary_preferences(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 식이 선호 조회

    1. 환자 접근 권한 확인
    2. dietary_preferences에서 알러지/제한 음식 조회
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

    # 2. dietary_preferences 조회
    dietary_pref = db.query(DietaryPreference).filter(
        DietaryPreference.patient_id == patient_id
    ).first()

    if not dietary_pref:
        # 식이 선호 정보가 없는 경우
        return {
            "patient_id": patient_id,
            "allergy_foods": [],
            "restriction_foods": []
        }

    return {
        "patient_id": patient_id,
        "diet_id": dietary_pref.diet_id,
        "allergy_foods": dietary_pref.allergy_foods or [],
        "restriction_foods": dietary_pref.restriction_foods or []
    }


@router.post("/patients/{patient_id}/dietary-preferences", status_code=status.HTTP_201_CREATED, response_model=DietaryPreferencesResponse)
async def create_dietary_preferences(
    patient_id: int,
    request: DietaryPreferencesCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자 식이 선호 등록

    1. 환자 접근 권한 확인
    2. dietary_preferences 테이블에 TEXT[] 배열로 저장
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

    # 2. dietary_preferences 테이블에 저장
    # 기존 식이 선호 정보가 있는지 확인
    dietary_pref = db.query(DietaryPreference).filter(
        DietaryPreference.patient_id == patient_id
    ).first()

    if not dietary_pref:
        # 새로운 식이 선호 정보 생성
        dietary_pref = DietaryPreference(
            patient_id=patient_id,
            allergy_foods=request.allergy_foods,
            restriction_foods=request.restriction_foods
        )
        db.add(dietary_pref)
    else:
        # 기존 정보 업데이트
        dietary_pref.allergy_foods = request.allergy_foods
        dietary_pref.restriction_foods = request.restriction_foods

    db.commit()
    db.refresh(dietary_pref)

    # 3. 응답 반환
    return DietaryPreferencesResponse(
        patient_id=patient_id,
        diet_id=dietary_pref.diet_id,
        allergy_foods=dietary_pref.allergy_foods or [],
        restriction_foods=dietary_pref.restriction_foods or []
    )


@router.get("/patients/{patient_id}/caregiver", status_code=status.HTTP_200_OK)
async def get_patient_caregiver(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    환자에게 할당된 현재 간병인 정보 조회

    matching_results에서 status='active' 또는 'selected'인 가장 최신 매칭을 조회합니다.

    응답:
    {
        "caregiver_id": 1,
        "caregiver_name": "박간병",
        "experience_years": 5,
        "specialties": ["치매 케어", "당뇨 관리"],
        "hourly_rate": 18000,
        "avg_rating": 4.8,
        "matching_id": 123,
        "status": "active"
    }
    또는 간병인이 없으면 null 반환
    """
    from app.models.profile import Patient, Guardian
    from app.models.matching import MatchingRequest, MatchingResult
    from app.models.user import User as UserModel

    print(f"🔍 [DEBUG] get_patient_caregiver 호출: patient_id={patient_id}, user_id={current_user.user_id}")

    # 1. 환자 접근 권한 확인 (로직 개선)
    guardian = current_user.guardian
    if not guardian:
        guardian = db.query(Guardian).filter(Guardian.user_id == current_user.user_id).first()
    
    if not guardian:
        print(f"❌ [DEBUG] 보호자 정보 없음")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="보호자 정보가 없습니다"
        )

    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.guardian_id == guardian.guardian_id
    ).first()

    if not patient:
        print(f"❌ [DEBUG] 환자 정보 없음 또는 권한 없음: patient_id={patient_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 환자에 대한 접근 권한이 없습니다"
        )

    print(f"✅ [DEBUG] 환자 확인 완료: {patient.name}")

    # 2. matching_results에서 status='active' 또는 'selected'인 최신 매칭 조회
    matching_result = db.query(MatchingResult).filter(
        MatchingResult.status.in_(['active', 'selected']),
        MatchingResult.request_id.in_(
            db.query(MatchingRequest.request_id).filter(
                MatchingRequest.patient_id == patient_id
            )
        )
    ).order_by(MatchingResult.updated_at.desc()).first()

    print(f"🔍 [DEBUG] 매칭 결과 조회: {matching_result}")

    if not matching_result:
        # 할당된 간병인이 없으면 빈 응답
        return {
            "caregiver_id": None,
            "caregiver_name": None,
            "experience_years": None,
            "specialties": [],
            "hourly_rate": None,
            "avg_rating": None,
            "matching_id": None,
            "status": None
        }

    # 3. 간병인 정보 조회
    caregiver = db.query(Caregiver).filter(
        Caregiver.caregiver_id == matching_result.caregiver_id
    ).first()

    if not caregiver:
        return {
            "caregiver_id": None,
            "caregiver_name": None,
            "experience_years": None,
            "specialties": [],
            "hourly_rate": None,
            "avg_rating": None,
            "matching_id": matching_result.matching_id,
            "status": matching_result.status
        }

    # 4. 간병인 사용자 정보 조회
    caregiver_user = db.query(UserModel).filter(
        UserModel.user_id == caregiver.user_id
    ).first()

    # 5. 응답 반환
    return {
        "caregiver_id": caregiver.caregiver_id,
        "caregiver_name": caregiver_user.name if caregiver_user else "간병인",
        "experience_years": caregiver.experience_years or 0,
        "specialties": caregiver.specialties.split("|") if caregiver.specialties else [],
        "hourly_rate": caregiver.hourly_rate or 0,
        "avg_rating": float(caregiver.avg_rating) if caregiver.avg_rating else 0,
        "matching_id": matching_result.matching_id,
        "status": matching_result.status
    }


@router.get("/patients/{patient_id}/care-plans")
async def get_patient_care_plans(
    patient_id: int,
    type: str = "weekly",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    환자의 케어 플랜(일정) 조회
    
    현재는 빈 리스트를 반환하여 프론트엔드에서 기본 데이터를 표시하도록 함.
    추후 DB 연동 필요.
    """
    from app.models.care_execution import Schedule, CareLog
    from datetime import date

    print(f"🔍 [DEBUG] 케어 플랜 조회 요청: patient_id={patient_id}, type={type}")
    
    # 오늘 날짜 이후의 스케줄 조회 (일주일치)
    today = date.today()
    schedules = db.query(Schedule).filter(
        Schedule.patient_id == patient_id,
        Schedule.care_date >= today
    ).order_by(Schedule.care_date).limit(7).all()

    result_list = []
    for schedule in schedules:
        # care_logs가 로딩되지 않았을 수 있으므로 접근하여 로딩 유도 (Lazy Loading)
        logs = schedule.care_logs
        for log in logs:
            result_list.append({
                "schedule_id": log.log_id, # 프론트엔드에서는 개별 활동을 schedule로 취급
                "title": log.task_name,
                "start_time": log.scheduled_time.strftime("%H:%M") if log.scheduled_time else "",
                "category": log.category.value if hasattr(log.category, 'value') else str(log.category),
                "is_completed": log.is_completed,
                "note": log.note
            })
    
    print(f"✅ [DEBUG] 조회된 활동 수: {len(result_list)}")

    return {
        "patient_id": patient_id,
        "schedules": result_list
    }
