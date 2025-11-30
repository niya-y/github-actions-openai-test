"""
간병인 관리 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.caregiver import Caregiver
from app.schemas.caregiver import (
    CaregiverCreate,
    CaregiverUpdate,
    CaregiverResponse,
)

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])


@router.get("", response_model=List[CaregiverResponse])
def list_caregivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    location: Optional[str] = None,
    gender: Optional[str] = Query(None, pattern="^(male|female)$"),
    min_experience: Optional[int] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    간병인 목록 조회 (필터링 지원)
    
    - **location**: 지역 필터
    - **gender**: 성별 필터
    - **min_experience**: 최소 경력
    - **min_rating**: 최소 평점
    - **is_active**: 활동 중인 간병인만
    """
    query = db.query(Caregiver)
    
    # 필터 적용
    filters = []
    if is_active:
        filters.append(Caregiver.is_active == True)
    if location:
        filters.append(Caregiver.location.ilike(f"%{location}%"))
    if gender:
        filters.append(Caregiver.gender == gender)
    if min_experience is not None:
        filters.append(Caregiver.experience_years >= min_experience)
    if min_rating is not None:
        filters.append(Caregiver.rating >= min_rating)
    
    if filters:
        query = query.filter(and_(*filters))
    
    caregivers = query.offset(skip).limit(limit).all()
    
    return caregivers


@router.get("/{caregiver_id}", response_model=CaregiverResponse)
def get_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 간병인 정보 조회
    """
    caregiver = db.query(Caregiver).filter(Caregiver.id == caregiver_id).first()
    
    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="간병인을 찾을 수 없습니다"
        )
    
    return caregiver


@router.post("", response_model=CaregiverResponse, status_code=status.HTTP_201_CREATED)
def create_caregiver(
    caregiver_data: CaregiverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    새 간병인 등록 (관리자 전용 기능)
    """
    caregiver = Caregiver(**caregiver_data.model_dump())
    db.add(caregiver)
    db.commit()
    db.refresh(caregiver)
    
    return caregiver


@router.put("/{caregiver_id}", response_model=CaregiverResponse)
def update_caregiver(
    caregiver_id: int,
    caregiver_data: CaregiverUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    간병인 정보 수정 (관리자 전용 기능)
    """
    caregiver = db.query(Caregiver).filter(Caregiver.id == caregiver_id).first()
    
    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="간병인을 찾을 수 없습니다"
        )
    
    # 수정된 필드만 업데이트
    update_data = caregiver_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(caregiver, field, value)
    
    db.commit()
    db.refresh(caregiver)
    
    return caregiver


@router.delete("/{caregiver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    간병인 정보 삭제 (관리자 전용 기능)
    """
    caregiver = db.query(Caregiver).filter(Caregiver.id == caregiver_id).first()
    
    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="간병인을 찾을 수 없습니다"
        )
    
    db.delete(caregiver)
    db.commit()
    
    return None
