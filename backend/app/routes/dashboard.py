"""
Dashboard API (마이페이지)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import Guardian, Patient
from app.models.matching import MatchingResult
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardUserInfo,
    DashboardGuardianInfo,
    DashboardPatientInfo,
    DashboardActiveMatching
)

router = APIRouter(prefix="/api", tags=["Dashboard"])


def calculate_age(birth_date: date) -> int:
    """생년월일로부터 나이 계산"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


@router.get("/users/me/dashboard", response_model=DashboardResponse)
async def get_my_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    마이페이지 대시보드 데이터 조회
    
    1. 사용자 정보
    2. 보호자 정보 (user_type이 guardian인 경우)
    3. 환자 목록
    4. 활성 매칭 정보 (status='active')
    """
    # 1. 사용자 정보
    user_info = DashboardUserInfo(
        user_id=current_user.user_id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone_number,
        user_type=current_user.user_type.value  # Enum을 문자열로 변환
    )
    
    guardian_info: Optional[DashboardGuardianInfo] = None
    patients_info: list[DashboardPatientInfo] = []
    active_matching_info: Optional[DashboardActiveMatching] = None
    
    # 2. 보호자 정보 (user_type이 guardian인 경우)
    if current_user.user_type.value == "guardian":
        guardian = db.query(Guardian).filter(
            Guardian.user_id == current_user.user_id
        ).first()
        
        if guardian:
            guardian_info = DashboardGuardianInfo(
                guardian_id=guardian.guardian_id,
                address=guardian.address or "",
                relationship=guardian.relationship_to_patient or ""
            )
            
            # 3. 환자 목록
            patients = db.query(Patient).filter(
                Patient.guardian_id == guardian.guardian_id
            ).all()
            
            for patient in patients:
                age = calculate_age(patient.birth_date)
                patients_info.append(
                    DashboardPatientInfo(
                        patient_id=patient.patient_id,
                        name=patient.name,
                        age=age,
                        care_level=patient.care_level.value if patient.care_level else None
                    )
                )
            
            # 4. 활성 매칭 정보 (첫 번째 환자의 매칭만 고려)
            if patients:
                # MatchingResult와 MatchingRequest, Caregiver, User를 조인하여 간병인 정보 가져오기
                from app.models.profile import Caregiver
                from app.models.matching import MatchingRequest

                matching = db.query(MatchingResult).join(
                    MatchingRequest, MatchingResult.request_id == MatchingRequest.request_id
                ).join(
                    Caregiver, MatchingResult.caregiver_id == Caregiver.caregiver_id
                ).join(
                    User, Caregiver.user_id == User.user_id
                ).filter(
                    MatchingRequest.patient_id == patients[0].patient_id,
                    MatchingResult.status == 'active'
                ).first()
                
                if matching:
                    # 간병인 정보 가져오기
                    caregiver = db.query(Caregiver).join(User).filter(
                        Caregiver.caregiver_id == matching.caregiver_id
                    ).first()
                    
                    if caregiver:
                        caregiver_user = db.query(User).filter(
                            User.user_id == caregiver.user_id
                        ).first()
                        
                        active_matching_info = DashboardActiveMatching(
                            caregiver_name=caregiver_user.name if caregiver_user else "간병인",
                            match_score=float(matching.total_score) if matching.total_score else 0.0,
                            start_date=matching.created_at.date().isoformat()
                        )
    
    # 5. 응답 반환
    return DashboardResponse(
        user=user_info,
        guardian=guardian_info,
        patients=patients_info,
        active_matching=active_matching_info
    )
