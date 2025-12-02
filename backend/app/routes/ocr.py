# backend/app/routes/ocr.py (v2 - 식약처 API 연동)
"""
약봉지 OCR API 엔드포인트 (식약처 API 검증 포함)

프론트엔드에서 약봉지 사진을 업로드하면:
1. Azure OCR로 약 이름 추출
2. 식약처 API로 실제 약품인지 검증
3. 검증된 약 정보를 medications 테이블에 저장
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from app.dependencies.database import get_db
from app.models.care_details import Medication
from app.services.ocr_service import get_ocr_service
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


# Response 스키마
class MedicineDetailResponse(BaseModel):
    """약품 상세 정보"""
    item_name: str
    entp_name: str
    item_seq: str
    efficacy: str
    usage: str
    precaution: str
    side_effect: str
    storage: str
    interaction: str
    item_image: str


class OCRResultResponse(BaseModel):
    """OCR 처리 결과"""
    success: bool
    medicines: List[MedicineDetailResponse]
    medicine_names: List[str]  # DB에 저장된 약 이름 목록
    confidence: float
    unverified_names: List[str]
    message: str


@router.post(
    "/patients/{patient_id}/medications/ocr",
    response_model=OCRResultResponse,
    summary="약봉지 사진에서 약 이름 추출 및 검증"
)
async def upload_medication_image(
    patient_id: int,
    file: UploadFile = File(..., description="약봉지 사진 파일 (JPG, PNG)")
):
    """
    약봉지 사진을 업로드하여 OCR + 식약처 API 검증

    **처리 과정:**
    1. 이미지 파일 검증
    2. Azure Document Intelligence OCR 실행
    3. 식약처 의약품개요정보 API로 약품 검증
    4. 검증된 약 정보 반환 (DB 저장은 Frontend form submit 시 수행)
    
    **예시 요청:**
    ```
    POST /api/patients/1/medications/ocr
    Content-Type: multipart/form-data
    
    file: [약봉지 이미지]
    ```
    
    **예시 응답:**
    ```json
    {
        "success": true,
        "medicines": [
            {
                "item_name": "아리셉트정5밀리그램",
                "entp_name": "한국화이자제약(주)",
                "efficacy": "알츠하이머형 치매...",
                "usage": "1일 1회 5mg 복용",
                "precaution": "간장애 환자 주의...",
                ...
            }
        ],
        "medicine_names": ["아리셉트정5밀리그램"],
        "confidence": 0.95,
        "unverified_names": [],
        "message": "1개의 약품이 확인되었습니다."
    }
    ```
    """
    
    # 1. 파일 형식 검증
    allowed_extensions = {"image/jpeg", "image/jpg", "image/png"}
    if file.content_type not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. JPG, PNG 파일만 업로드 가능합니다."
        )
    
    # 2. 파일 크기 검증 (10MB 제한)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="파일 크기가 너무 큽니다. 10MB 이하 파일만 업로드 가능합니다."
        )
    
    try:
        # 3. OCR + 식약처 API 검증 처리
        logger.info(f"환자 ID {patient_id}의 약봉지 OCR 처리 시작")
        ocr_service = get_ocr_service()
        result = await ocr_service.extract_and_validate_medicines(contents)
        
        verified_medicines = result["medicines"]
        confidence = result["confidence"]
        unverified_names = result["unverified_names"]
        
        logger.info(f"OCR 완료 - 검증된 약: {len(verified_medicines)}개")
        
        # 4. 약 이름이 없으면 오류 반환 (OCR 자체가 실패한 경우)
        if not verified_medicines and not unverified_names:
            raise HTTPException(
                status_code=400,
                detail="이미지에서 텍스트를 인식할 수 없습니다. 더 선명한 사진을 촬영해주세요."
            )
        
        # 5. OCR 결과 반환 (DB 저장은 Frontend에서 form submit 시에 수행)
        # 검증된 약과 검증되지 않은 약(단순 텍스트) 모두 이름 목록에 포함하여 프론트엔드 입력창에 표시되도록 함
        medicine_names = [med["item_name"] for med in verified_medicines] + unverified_names
        logger.info(f"OCR 결과 반환: {len(medicine_names)}개 약품 (검증: {len(verified_medicines)}, 미검증: {len(unverified_names)})")

        # 6. 성공 응답
        message = f"총 {len(medicine_names)}개의 약품 이름이 인식되었습니다."
        if unverified_names:
            message += f" (식약처 미등록/불일치: {len(unverified_names)}건 포함)"
        
        return OCRResultResponse(
            success=True,
            medicines=[MedicineDetailResponse(**med) for med in verified_medicines],
            medicine_names=medicine_names,
            confidence=confidence,
            unverified_names=unverified_names,
            message=message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"약봉지 OCR 처리 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"OCR 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/patients/{patient_id}/medications",
    summary="환자의 복용 약 목록 조회"
)
async def get_patient_medications(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    환자의 모든 복용 약 정보를 조회합니다.
    
    **예시 응답:**
    ```json
    {
        "med_id": 123,
        "patient_id": 1,
        "medicine_names": ["아리셉트정5밀리그램", "메트포르민정500밀리그램"],
        "created_at": "2024-11-28T13:45:00"
    }
    ```
    """
    medication = db.query(Medication).filter(
        Medication.patient_id == patient_id
    ).first()
    
    if not medication:
        return {
            "med_id": None,
            "patient_id": patient_id,
            "medicine_names": [],
            "message": "등록된 약이 없습니다."
        }
    
    return {
        "med_id": medication.med_id,
        "patient_id": medication.patient_id,
        "medicine_names": medication.medicine_names,
        "created_at": medication.created_at
    }


@router.get(
    "/medicines/search",
    summary="약품명으로 식약처 정보 검색"
)
async def search_medicine_info(
    item_name: str
):
    """
    약품명으로 식약처 의약품개요정보를 검색합니다.
    
    **예시:**
    ```
    GET /api/medicines/search?item_name=아리셉트
    ```
    
    **응답:**
    ```json
    {
        "item_name": "아리셉트정5밀리그램",
        "entp_name": "한국화이자제약(주)",
        "efficacy": "...",
        ...
    }
    ```
    """
    try:
        ocr_service = get_ocr_service()
        medicine_info = await ocr_service._verify_medicine_with_mfds(item_name)
        
        if not medicine_info:
            raise HTTPException(
                status_code=404,
                detail=f"'{item_name}' 약품을 찾을 수 없습니다."
            )
        
        return medicine_info.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"약품 검색 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"약품 검색 중 오류가 발생했습니다: {str(e)}"
        )
