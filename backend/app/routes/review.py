"""
Review FastAPI router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.crud.review import (
    get_review,
    get_reviews,
    create_review,
    update_review,
    delete_review,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("", response_model=list[ReviewResponse])
def list_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 리뷰 조회"""
    return get_reviews(db, skip=skip, limit=limit)


@router.get("/{review_id}", response_model=ReviewResponse)
def read_review(review_id: int, db: Session = Depends(get_db)):
    """특정 리뷰 조회"""
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_new_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새 리뷰 생성 (인증 필요)"""
    # reviewer_type은 user_type에서 가져옴
    reviewer_type = current_user.user_type.value
    return create_review(db, payload, current_user.user_id, reviewer_type)


@router.put("/{review_id}", response_model=ReviewResponse)
def update_existing_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """리뷰 수정 (본인만 가능)"""
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # 본인 확인
    if review.reviewer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this review")
    
    return update_review(db, review, payload)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """리뷰 삭제 (본인만 가능)"""
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # 본인 확인
    if review.reviewer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    
    delete_review(db, review_id)
    return None
