"""
Care Execution (Schedule, CareLog, MealPlan, CareReport) FastAPI router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db

# Schedule imports
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.crud.schedule import (
    get_schedule,
    get_schedules,
    create_schedule,
    update_schedule,
    delete_schedule,
)

# CareLog imports
from app.schemas.care_log import CareLogCreate, CareLogUpdate, CareLogResponse
from app.crud.care_log import (
    get_care_log,
    get_care_logs,
    create_care_log,
    update_care_log,
    delete_care_log,
)

# MealPlan imports
from app.schemas.meal_plan import MealPlanCreate, MealPlanUpdate, MealPlanResponse
from app.crud.meal_plan import (
    get_meal_plan,
    get_meal_plans,
    create_meal_plan,
    update_meal_plan,
    delete_meal_plan,
)

# CareReport imports
from app.schemas.report import CareReportCreate, CareReportUpdate, CareReportResponse
from app.crud.care_report import (
    get_care_report,
    get_care_reports,
    create_care_report,
    update_care_report,
    delete_care_report,
)

router = APIRouter(prefix="/care", tags=["Care Execution"])

# ---------------------------------------------------------------------------
# Schedule endpoints
# ---------------------------------------------------------------------------

@router.get("/schedules", response_model=list[ScheduleResponse])
def list_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_schedules(db, skip=skip, limit=limit)

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
def read_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_new_schedule(payload: ScheduleCreate, db: Session = Depends(get_db)):
    return create_schedule(db, payload)

@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_existing_schedule(schedule_id: int, payload: ScheduleUpdate, db: Session = Depends(get_db)):
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return update_schedule(db, schedule, payload)

@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    delete_schedule(db, schedule_id)
    return None

# ---------------------------------------------------------------------------
# CareLog endpoints
# ---------------------------------------------------------------------------

@router.get("/care_logs", response_model=list[CareLogResponse])
def list_care_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_care_logs(db, skip=skip, limit=limit)

@router.get("/care_logs/{log_id}", response_model=CareLogResponse)
def read_care_log(log_id: int, db: Session = Depends(get_db)):
    log = get_care_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="CareLog not found")
    return log

@router.post("/care_logs", response_model=CareLogResponse, status_code=status.HTTP_201_CREATED)
def create_new_care_log(payload: CareLogCreate, db: Session = Depends(get_db)):
    return create_care_log(db, payload)

@router.put("/care_logs/{log_id}", response_model=CareLogResponse)
def update_existing_care_log(log_id: int, payload: CareLogUpdate, db: Session = Depends(get_db)):
    log = get_care_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="CareLog not found")
    return update_care_log(db, log, payload)

@router.delete("/care_logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_care_log(log_id: int, db: Session = Depends(get_db)):
    log = get_care_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="CareLog not found")
    delete_care_log(db, log_id)
    return None

# ---------------------------------------------------------------------------
# MealPlan endpoints
# ---------------------------------------------------------------------------

@router.get("/meal_plans", response_model=list[MealPlanResponse])
def list_meal_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_meal_plans(db, skip=skip, limit=limit)

@router.get("/meal_plans/{plan_id}", response_model=MealPlanResponse)
def read_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = get_meal_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="MealPlan not found")
    return plan

@router.post("/meal_plans", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
def create_new_meal_plan(payload: MealPlanCreate, db: Session = Depends(get_db)):
    return create_meal_plan(db, payload)

@router.put("/meal_plans/{plan_id}", response_model=MealPlanResponse)
def update_existing_meal_plan(plan_id: int, payload: MealPlanUpdate, db: Session = Depends(get_db)):
    plan = get_meal_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="MealPlan not found")
    return update_meal_plan(db, plan, payload)

@router.delete("/meal_plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = get_meal_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="MealPlan not found")
    delete_meal_plan(db, plan_id)
    return None

# ---------------------------------------------------------------------------
# CareReport endpoints
# ---------------------------------------------------------------------------

@router.get("/care_reports", response_model=list[CareReportResponse])
def list_care_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_care_reports(db, skip=skip, limit=limit)

@router.get("/care_reports/{report_id}", response_model=CareReportResponse)
def read_care_report(report_id: int, db: Session = Depends(get_db)):
    report = get_care_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="CareReport not found")
    return report

@router.post("/care_reports", response_model=CareReportResponse, status_code=status.HTTP_201_CREATED)
def create_new_care_report(payload: CareReportCreate, db: Session = Depends(get_db)):
    return create_care_report(db, payload)

@router.put("/care_reports/{report_id}", response_model=CareReportResponse)
def update_existing_care_report(report_id: int, payload: CareReportUpdate, db: Session = Depends(get_db)):
    report = get_care_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="CareReport not found")
    return update_care_report(db, report, payload)

@router.delete("/care_reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_care_report(report_id: int, db: Session = Depends(get_db)):
    report = get_care_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="CareReport not found")
    delete_care_report(db, report_id)
    return None
