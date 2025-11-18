"""
Report API Routes
리포트 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date
from typing import Optional

from services.report_service import ReportService

# Pydantic 모델
class DailyReportRequest(BaseModel):
    matching_id: int
    report_date: Optional[date] = None
    content: str = ""
    mood: str = "Neutral"
    activities: str = ""
    medications_taken: bool = True
    notes: str = ""
    created_by: str = "System"

    class Config:
        schema_extra = {
            "example": {
                "matching_id": 1,
                "report_date": "2024-11-12",
                "content": "환자가 잘 지내고 있습니다",
                "mood": "Happy",
                "activities": "산책 30분, 독서 1시간",
                "medications_taken": True,
                "notes": "특별한 이상 없음",
                "created_by": "Nurse Kim"
            }
        }


router = APIRouter(prefix="/api/report", tags=["Report"])


@router.post("/daily")
async def create_daily_report(request: DailyReportRequest):
    """
    일일 리포트 생성

    - **matching_id**: 매칭 ID
    - **report_date**: 리포트 날짜 (선택사항, 기본값: 오늘)
    - **content**: 리포트 내용
    - **mood**: 환자 기분 (Happy, Neutral, Sad)
    - **activities**: 활동 기록
    - **medications_taken**: 약물 복용 여부 (기본값: True)
    - **notes**: 추가 메모
    - **created_by**: 작성자 (기본값: System)

    Returns: 생성된 리포트 정보
    """
    try:
        result = ReportService.generate_daily_report(
            matching_id=request.matching_id,
            report_date=request.report_date,
            content=request.content,
            mood=request.mood,
            activities=request.activities,
            medications_taken=request.medications_taken,
            notes=request.notes,
            created_by=request.created_by
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/weekly/{patient_id}")
async def get_weekly_report(
    patient_id: int,
    week_start_date: Optional[date] = Query(None, description="주간 시작 날짜 (YYYY-MM-DD, 선택사항)")
):
    """
    주간 리포트 조회

    - **patient_id**: 환자 ID
    - **week_start_date**: 주간 시작 날짜 (선택사항, 기본값: 지난 월요일)

    Returns: 주간 리포트 정보 (기분 분포, 활동 요약, 주간 평가 등)
    """
    try:
        result = ReportService.generate_weekly_report(
            patient_id=patient_id,
            week_start_date=week_start_date
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/monthly/performance")
async def get_monthly_performance_report(
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)")
):
    """
    월간 성과 리포트 조회

    - **start_date**: 시작 날짜 (형식: YYYY-MM-DD)
    - **end_date**: 종료 날짜 (형식: YYYY-MM-DD)

    Returns: 월간 성과 리포트 (매칭 통계, 케어 통계, 성능 평가 등)
    """
    try:
        result = ReportService.generate_monthly_performance_report(
            start_date=start_date,
            end_date=end_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    API 헬스 체크

    Returns: 서버 상태 정보
    """
    return {
        "status": "healthy",
        "service": "BluedonuLab Caregiver Matching API",
        "version": "1.0.0"
    }
