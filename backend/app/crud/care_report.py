"""
CRUD operations for CareReport model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.care_execution import CareReport
from app.schemas.report import CareReportCreate, CareReportUpdate, CareReportResponse


def get_care_report(db: Session, report_id: int) -> Optional[CareReport]:
    return db.query(CareReport).filter(CareReport.report_id == report_id).first()


def get_care_reports(db: Session, skip: int = 0, limit: int = 100) -> List[CareReport]:
    return db.query(CareReport).offset(skip).limit(limit).all()


def create_care_report(db: Session, obj_in: CareReportCreate) -> CareReport:
    db_obj = CareReport(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_care_report(db: Session, report: CareReport, obj_in: CareReportUpdate) -> CareReport:
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(report, field, value)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def delete_care_report(db: Session, report_id: int) -> None:
    db.query(CareReport).filter(CareReport.report_id == report_id).delete()
    db.commit()
