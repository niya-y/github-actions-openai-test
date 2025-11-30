"""
CRUD operations for Review model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse


def get_review(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.review_id == review_id).first()


def get_reviews(db: Session, skip: int = 0, limit: int = 100) -> List[Review]:
    return db.query(Review).offset(skip).limit(limit).all()


def create_review(db: Session, obj_in: ReviewCreate, reviewer_id: int, reviewer_type: str) -> Review:
    db_obj = Review(
        **obj_in.dict(),
        reviewer_id=reviewer_id,
        reviewer_type=reviewer_type
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_review(db: Session, review: Review, obj_in: ReviewUpdate) -> Review:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(review, field, value)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int) -> None:
    db.query(Review).filter(Review.review_id == review_id).delete()
    db.commit()
