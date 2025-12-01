"""
케어 보고서 API
파일 위치: backend/app/routes/care_reports.py

프론트엔드에서 보낸 요청을 받아 PDF를 생성하고
Azure Blob Storage에 업로드한 후 다운로드 URL을 반환합니다.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
import asyncio
import logging

from app.dependencies.database import get_db
from app.models.profile import Patient, Caregiver
from app.models.matching import MatchingResult
from app.models.care_execution import Schedule, CareLog
from app.models.user import User
from app.services.pdf_generator import pdf_generator
from app.utils.azure_blob import get_azure_blob_service
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/care-reports", tags=["Care Reports"])


# ============================================
# Request/Response 스키마
# ============================================

class GeneratePDFRequest(BaseModel):
    """
    PDF 생성 요청
    
    프론트엔드의 handleExportPDF 함수에서 전송하는 데이터
    """
    start_date: str = Field(
        ..., 
        description="시작 날짜 (YYYY-MM-DD 형식)",
        example="2025-01-02"
    )
    end_date: Optional[str] = Field(
        None,
        description="종료 날짜 (YYYY-MM-DD 형식, 미입력 시 start_date와 동일)",
        example="2025-01-08"
    )
    report_type: Optional[str] = Field(
        "daily",
        description="보고서 타입 (daily 또는 weekly)",
        example="daily"
    )


class GeneratePDFResponse(BaseModel):
    """
    PDF 생성 응답
    
    프론트엔드에서 download_url을 사용하여 새 탭에서 PDF 열기
    """
    success: bool = Field(..., description="성공 여부")
    download_url: str = Field(..., description="PDF 다운로드 URL (SAS)")
    file_name: str = Field(..., description="파일명")
    expires_at: str = Field(..., description="URL 만료 시간 (ISO 8601)")
    message: str = Field(..., description="응답 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "download_url": "https://neulbomcare.blob.core.windows.net/care-reports/...",
                "file_name": "간병일지_김영희_20250102.pdf",
                "expires_at": "2025-01-09T00:00:00Z",
                "message": "PDF가 성공적으로 생성되었습니다"
            }
        }


# ============================================
# 헬퍼 함수
# ============================================

def calculate_age(birth_date) -> int:
    """
    생년월일로 나이 계산
    
    Args:
        birth_date: datetime.date 또는 문자열
    
    Returns:
        int: 만 나이
    """
    today = datetime.now().date()
    
    if isinstance(birth_date, str):
        birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
    else:
        birth = birth_date
    
    age = today.year - birth.year
    
    # 생일이 아직 안 지났으면 -1
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    
    return age


def categorize_care_logs(logs: list) -> dict:
    """
    케어 로그를 카테고리별로 분류하여 체크박스 상태 반환
    
    Args:
        logs: CareLog 리스트
    
    Returns:
        {
            'meal': True/False,       # 식사보조
            'activity': True/False,   # 활동보조
            'excretion': True/False,  # 배변보조
            'hygiene': True/False,    # 위생보조
            'other': True/False       # 기타
        }
    """
    categories = {
        'meal': False,
        'activity': False,
        'excretion': False,
        'hygiene': False,
        'other': False
    }
    
    for log in logs:
        # 완료된 로그만 체크 표시
        if not log.is_completed:
            continue
        
        # 카테고리 매핑
        if log.category == 'meal':
            categories['meal'] = True
        elif log.category == 'exercise':  # DB의 exercise -> 활동보조
            categories['activity'] = True
        elif log.category == 'vital_check':  # 임시 매핑
            categories['excretion'] = True
        elif log.category == 'hygiene':
            categories['hygiene'] = True
        elif log.category == 'other':
            categories['other'] = True
    
    return categories


def format_time(time_obj) -> str:
    """
    시간 객체를 HH:MM 형식으로 변환
    
    Args:
        time_obj: datetime.time 또는 None
    
    Returns:
        str: "08:00" 형식 또는 빈 문자열
    """
    if time_obj is None:
        return ""
    
    if isinstance(time_obj, str):
        return time_obj
    
    return time_obj.strftime('%H:%M')


def get_care_report_data(
    db: Session, 
    patient_id: int, 
    start_date: str, 
    end_date: str
) -> dict:
    """
    케어 보고서 생성에 필요한 모든 데이터 조회
    
    Args:
        db: 데이터베이스 세션
        patient_id: 환자 ID
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
    
    Returns:
        dict: {
            'patient': Patient 객체,
            'caregiver': Caregiver 객체 또는 None,
            'caregiver_user': User 객체 또는 None,
            'daily_logs': {날짜: {date, logs}} 딕셔너리
        }
    
    Raises:
        ValueError: 환자를 찾을 수 없는 경우
    """
    
    # 1. 환자 정보 조회
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()
    
    if not patient:
        raise ValueError(f"환자 ID {patient_id}를 찾을 수 없습니다")
    
    logger.info(f"✅ 환자 조회: {patient.name} (ID: {patient_id})")
    
    # 2. 활성 매칭에서 간병인 정보 조회
    active_matching = db.query(MatchingResult)\
        .filter(
            MatchingResult.patient_id == patient_id,
            MatchingResult.status == 'active'
        )\
        .order_by(MatchingResult.created_at.desc())\
        .first()
    
    # 활성 매칭이 없으면 가장 최근 매칭 조회
    if not active_matching:
        active_matching = db.query(MatchingResult)\
            .filter(MatchingResult.patient_id == patient_id)\
            .order_by(MatchingResult.created_at.desc())\
            .first()
    
    caregiver = None
    caregiver_user = None
    
    if active_matching:
        # 간병인 정보
        caregiver = db.query(Caregiver).filter(
            Caregiver.caregiver_id == active_matching.caregiver_id
        ).first()
        
        # 간병인 사용자 정보 (이름, 전화번호 등)
        if caregiver:
            caregiver_user = db.query(User).filter(
                User.user_id == caregiver.user_id
            ).first()
            logger.info(f"✅ 간병인 조회: {caregiver_user.name if caregiver_user else 'Unknown'}")
    else:
        logger.warning(f"⚠️ 환자 {patient_id}의 매칭 정보 없음")
    
    # 3. 지정 기간의 스케줄 조회
    schedules = db.query(Schedule).filter(
        Schedule.patient_id == patient_id,
        Schedule.care_date >= start_date,
        Schedule.care_date <= end_date
    ).order_by(Schedule.care_date).all()
    
    logger.info(f"✅ 스케줄 조회: {len(schedules)}개 ({start_date} ~ {end_date})")
    
    # 4. 날짜별로 케어 로그 그룹화
    daily_logs = {}
    
    for schedule in schedules:
        date_key = schedule.care_date.strftime('%Y-%m-%d')
        
        # 해당 스케줄의 케어 로그 조회
        logs = db.query(CareLog).filter(
            CareLog.schedule_id == schedule.schedule_id
        ).all()
        
        if date_key not in daily_logs:
            daily_logs[date_key] = {
                'date': schedule.care_date,
                'logs': logs
            }
        else:
            # 같은 날짜에 여러 스케줄이 있는 경우
            daily_logs[date_key]['logs'].extend(logs)
    
    logger.info(f"✅ 케어 로그 조회: {sum(len(d['logs']) for d in daily_logs.values())}개")
    
    return {
        'patient': patient,
        'caregiver': caregiver,
        'caregiver_user': caregiver_user,
        'daily_logs': daily_logs
    }


# ============================================
# API 엔드포인트
# ============================================

@router.post("/generate-pdf/{patient_id}", response_model=GeneratePDFResponse)
async def generate_care_report_pdf(
    patient_id: int,
    request: GeneratePDFRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    케어 보고서 PDF 생성 및 다운로드 URL 반환
    
    ## 프론트엔드 요청 예시:
    ```javascript
    const response = await axios.post(
        `/api/care-reports/generate-pdf/${patientId}`,
        {
            start_date: "2025-01-02",
            end_date: "2025-01-02",
            report_type: "daily"
        },
        {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }
    );
    
    // 성공 시
    const { download_url } = response.data;
    window.open(download_url, '_blank');  // 새 탭에서 PDF 열기
    ```
    
    ## 처리 흐름:
    1. 권한 체크 (guardian만 허용)
    2. 데이터베이스에서 환자/간병인/케어 로그 조회
    3. HTML 템플릿 생성
    4. Pyppeteer로 PDF 변환
    5. Azure Blob Storage 업로드
    6. SAS URL 생성 및 반환
    
    ## 응답:
    - download_url: 7일간 유효한 다운로드 링크
    - file_name: 파일명 (예: 간병일지_김영희_20250102.pdf)
    - expires_at: URL 만료 시간
    
    Args:
        patient_id: 환자 ID (URL 경로)
        request: PDF 생성 요청 (start_date, end_date, report_type)
        db: 데이터베이스 세션 (자동 주입)
        current_user: 현재 로그인한 사용자 (자동 주입)
    
    Returns:
        GeneratePDFResponse: PDF 다운로드 URL 포함
    
    Raises:
        HTTPException 403: 권한 없음 (guardian이 아닌 경우)
        HTTPException 404: 환자를 찾을 수 없음
        HTTPException 500: PDF 생성 실패
    """
    try:
        # 1. 권한 체크 (guardian만 허용)
        if current_user.user_type != 'guardian':
            logger.warning(f"⚠️ 권한 없음: {current_user.user_id} ({current_user.user_type})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="보호자만 케어 보고서를 생성할 수 있습니다"
            )
        
        # 2. 날짜 설정
        start_date = request.start_date
        end_date = request.end_date or start_date
        
        logger.info(f"📄 PDF 생성 시작 - 환자: {patient_id}, 기간: {start_date} ~ {end_date}")
        
        # 3. 데이터베이스에서 데이터 조회
        data = get_care_report_data(db, patient_id, start_date, end_date)
        
        patient = data['patient']
        caregiver_user = data['caregiver_user']
        daily_logs = data['daily_logs']
        
        # 4. 템플릿용 데이터 준비
        work_logs = []
        
        for date_key, log_data in sorted(daily_logs.items()):
            # 케어 로그를 카테고리별로 분류
            tasks = categorize_care_logs(log_data['logs'])
            
            # 시작/종료 시간 계산 (실제 로그에서 가장 이른/늦은 시간)
            start_time = "08:00"  # 기본값
            end_time = "20:00"
            
            if log_data['logs']:
                times = [
                    format_time(log.scheduled_time) 
                    for log in log_data['logs'] 
                    if log.scheduled_time
                ]
                if times:
                    start_time = min(times)
                    end_time = max(times)
            
            work_logs.append({
                'date': log_data['date'].strftime('%y/%m/%d'),  # 25/1/2 형식
                'start_time': start_time,
                'end_time': end_time,
                'tasks': tasks
            })
        
        # 5. 템플릿 데이터 구성
        template_data = {
            # 환자 정보
            'patient_name': patient.name,
            'patient_gender': '남' if patient.gender == 'Male' else '여',
            'patient_birth_date': patient.birth_date.strftime('%Y-%m-%d'),
            'hospital_name': patient.care_address or '늘봄케어',
            
            # 간병인 정보
            'caregiver_name': caregiver_user.name if caregiver_user else '간병인',
            'caregiver_gender': '여' if caregiver_user and caregiver_user.gender == 'Female' else '남',
            'caregiver_birth_date': '1980-01-01',  # TODO: 실제 생년월일 필드 추가 시 수정
            'caregiver_phone': caregiver_user.phone_number if caregiver_user else '010-0000-0000',
            
            # 업무 로그
            'work_logs': work_logs,
            
            # 날짜 (작성일)
            'year': datetime.now().strftime('%Y'),
            'month': datetime.now().strftime('%m'),
            'day': datetime.now().strftime('%d')
        }
        
        logger.debug(f"템플릿 데이터: 업무 로그 {len(work_logs)}개")
        
        # 6. HTML 생성
        html_content = pdf_generator.generate_html(template_data)
        
        # 7. PDF 생성 (비동기)
        pdf_bytes = await pdf_generator.generate_pdf(html_content)
        
        # 8. Azure Blob Storage 업로드
        file_name = f"간병일지_{patient.name}_{start_date.replace('-', '')}.pdf"
        blob_name = f"reports/patient_{patient_id}/{file_name}"
        
        _, sas_url = get_azure_blob_service().upload_pdf(
            pdf_bytes=pdf_bytes,
            blob_name=blob_name,
            expiry_days=7  # 7일간 유효
        )
        
        # 9. 만료 시간 계산
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
        
        logger.info(f"✅ PDF 생성 완료 - {file_name}")
        
        # 10. 응답 반환
        return GeneratePDFResponse(
            success=True,
            download_url=sas_url,
            file_name=file_name,
            expires_at=expires_at,
            message="PDF가 성공적으로 생성되었습니다"
        )
        
    except ValueError as e:
        # 환자를 찾을 수 없는 경우
        logger.error(f"❌ 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        # 기타 모든 에러
        logger.error(f"❌ PDF 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    
    서비스가 정상 동작하는지 확인
    """
    return {
        "status": "healthy",
        "service": "Care Report PDF Generator",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/test-pdf")
async def test_pdf_generation():
    """
    PDF 생성 테스트 엔드포인트 (개발용)
    
    실제 데이터 없이 샘플 데이터로 PDF 생성 테스트
    """
    sample_data = {
        'patient_name': '테스트 환자',
        'patient_gender': '여',
        'patient_birth_date': '1950-01-15',
        'hospital_name': '테스트 병원',
        'caregiver_name': '테스트 간병인',
        'caregiver_gender': '여',
        'caregiver_birth_date': '1980-05-20',
        'caregiver_phone': '010-1234-5678',
        'work_logs': [
            {
                'date': '25/1/2',
                'start_time': '08:00',
                'end_time': '20:00',
                'tasks': {
                    'meal': True,
                    'activity': True,
                    'excretion': False,
                    'hygiene': True,
                    'other': False
                }
            }
        ],
        'year': '2025',
        'month': '01',
        'day': '02'
    }
    
    try:
        # HTML 생성
        html = pdf_generator.generate_html(sample_data)
        
        # PDF 생성
        pdf_bytes = await pdf_generator.generate_pdf(html)
        
        # Azure 업로드
        blob_name = f"test/test_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        _, sas_url = get_azure_blob_service().upload_pdf(pdf_bytes, blob_name, expiry_days=1)
        
        return {
            "success": True,
            "message": "테스트 PDF 생성 성공",
            "download_url": sas_url,
            "size_bytes": len(pdf_bytes)
        }
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"테스트 실패: {str(e)}"
        )
