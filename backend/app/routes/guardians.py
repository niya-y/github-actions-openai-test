"""
Guardian (보호자) FastAPI router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import Guardian
from app.schemas.guardian import GuardianCreateRequest, GuardianInfoResponse

router = APIRouter(prefix="/api", tags=["Guardians"])


@router.post("/guardians", status_code=status.HTTP_201_CREATED, response_model=GuardianInfoResponse)
async def create_guardian(
    request: GuardianCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    보호자 정보 등록
    
    1. users 테이블 업데이트 (name, phone_number)
    2. guardians 테이블에 저장 (address, relationship_to_patient)
    """
    # 1. users 테이블 업데이트
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    user.name = request.name
    user.phone_number = request.phone
    
    # 2. guardians 테이블에 저장
    # 기존 보호자 정보가 있는지 확인
    existing_guardian = db.query(Guardian).filter(Guardian.user_id == user.user_id).first()
    if existing_guardian:
        # 이미 보호자 정보가 있으면 업데이트
        existing_guardian.address = request.address
        existing_guardian.relationship_to_patient = request.relationship
        db.commit()
        db.refresh(user)
        db.refresh(existing_guardian)
        guardian = existing_guardian
    else:
        # 새로운 보호자 정보 생성
        guardian = Guardian(
            user_id=user.user_id,
            address=request.address,
            relationship_to_patient=request.relationship
        )
        db.add(guardian)
        db.commit()
        db.refresh(user)
        db.refresh(guardian)
    
    # 3. 응답 반환
    return GuardianInfoResponse(
        guardian_id=guardian.guardian_id,
        user_id=user.user_id,
        name=user.name,
        phone=user.phone_number,
        address=guardian.address,
        relationship=guardian.relationship_to_patient,
        created_at=guardian.created_at
    )


@router.get("/guardians/me", response_model=GuardianInfoResponse)
async def get_my_guardian_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 보호자 정보 조회
    """
    guardian = db.query(Guardian).filter(
        Guardian.user_id == current_user.user_id
    ).first()
    
    if not guardian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보호자 정보가 없습니다"
        )
    
    return GuardianInfoResponse(
        guardian_id=guardian.guardian_id,
        user_id=current_user.user_id,
        name=current_user.name,
        phone=current_user.phone_number,
        address=guardian.address,
        relationship=guardian.relationship_to_patient,
        created_at=guardian.created_at
    )
