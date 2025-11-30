# backend/app/services/ocr_service.py (v2 - 식약처 API 연동)
"""
약봉지 이미지에서 약 이름을 추출하고 식약처 API로 검증하는 OCR 서비스

처리 과정:
1. Azure Document Intelligence로 텍스트 추출
2. 약 이름 패턴 필터링
3. 식약처 의약품개요정보 API로 검증
4. 검증된 약 정보 반환 (효능, 용법, 주의사항 포함)
"""

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
import re
import requests
from typing import List, Dict, Optional
import logging
from urllib.parse import quote
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MedicineInfo:
    """약품 상세 정보 클래스"""
    def __init__(self, data: dict):
        self.item_name = data.get('itemName', '')  # 제품명
        self.entp_name = data.get('entpName', '')  # 업체명
        self.item_seq = data.get('itemSeq', '')    # 품목기준코드
        
        # 효능, 용법 등 (HTML 태그 제거)
        self.efficacy = self._clean_html(data.get('efcyQesitm', ''))  # 효능
        self.usage = self._clean_html(data.get('useMethodQesitm', ''))  # 사용법
        self.precaution = self._clean_html(data.get('atpnQesitm', ''))  # 주의사항
        self.side_effect = self._clean_html(data.get('seQesitm', ''))  # 부작용
        self.storage = self._clean_html(data.get('depositMethodQesitm', ''))  # 보관법
        self.interaction = self._clean_html(data.get('intrcQesitm', ''))  # 상호작용
        
        # 낱알 이미지 (있으면)
        self.item_image = data.get('itemImage', '')
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        if not text:
            return ''
        # <p>, </p> 태그 제거
        text = re.sub(r'<p>|</p>', '', text)
        # 기타 HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'item_name': self.item_name,
            'entp_name': self.entp_name,
            'item_seq': self.item_seq,
            'efficacy': self.efficacy,
            'usage': self.usage,
            'precaution': self.precaution,
            'side_effect': self.side_effect,
            'storage': self.storage,
            'interaction': self.interaction,
            'item_image': self.item_image
        }


class OCRService:
    """약봉지 OCR 처리 및 식약처 API 검증 서비스"""
    
    def __init__(self):
        """Azure Document Intelligence 및 식약처 API 클라이언트 초기화"""
        # 설정 로드
        settings = get_settings()

        # Azure OCR
        endpoint = settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
        key = settings.AZURE_DOCUMENT_INTELLIGENCE_KEY

        if not endpoint or not key:
            raise ValueError("Azure Document Intelligence 환경 변수가 설정되지 않았습니다.")

        self.ocr_client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

        # 식약처 API
        self.mfds_api_key = settings.MFDS_API_KEY  # 공공데이터포털 API 키
        if not self.mfds_api_key:
            logger.warning("식약처 API 키가 설정되지 않았습니다. 검증 기능이 제한됩니다.")
        
        self.mfds_api_url = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
        
        # 한국 약품명 패턴 (한글 + 숫자 + 단위)
        self.medicine_pattern = re.compile(
            r'[가-힣]{2,}(?:\d+(?:mg|밀리그램|정|캡슐|정제|㎎)?)?'
        )
        
        # 제외할 일반 단어 (확장됨)
        self.exclude_words = {
            '복용법', '주의사항', '복용시간', '식후', '식전', '하루', 
            '아침', '점심', '저녁', '취침전', '병원', '약국', '처방전',
            '환자', '보관방법', '유효기간', '제조사', '성분', '효능',
            '부작용', '용법', '용량', '투여', '경고', '의사', '약사',
            '복용', '주의', '성인', '소아', '어린이', '임산부', '수유부',
            '복약', '지도', '상담', '문의', '제조', '번호', '유통기한'
        }
    
    async def extract_and_validate_medicines(
        self, 
        image_bytes: bytes
    ) -> Dict[str, any]:
        """
        약봉지 이미지에서 약 이름 추출 및 식약처 API로 검증
        
        Args:
            image_bytes: 이미지 파일의 바이트 데이터
            
        Returns:
            {
                "medicines": [
                    {
                        "item_name": "아리셉트정5밀리그램",
                        "entp_name": "한국화이자제약(주)",
                        "efficacy": "알츠하이머형 치매 증상의 치료",
                        "usage": "1일 1회 5mg...",
                        ...
                    }
                ],
                "raw_ocr_text": "전체 OCR 텍스트",
                "confidence": 0.95,
                "unverified_names": ["검증 실패한 약 이름들"]
            }
        """
        try:
            # 1단계: Azure OCR로 텍스트 추출
            logger.info("🔍 1단계: Azure OCR 시작")
            ocr_result = await self._extract_text_from_image(image_bytes)
            
            raw_text = ocr_result["raw_text"]
            candidate_names = ocr_result["candidate_names"]
            confidence = ocr_result["confidence"]
            
            logger.info(f"📝 OCR 추출 완료: {len(candidate_names)}개 후보 약 이름")
            
            # 2단계: 식약처 API로 검증
            logger.info("✅ 2단계: 식약처 API 검증 시작")
            verified_medicines = []
            unverified_names = []
            
            for name in candidate_names:
                medicine_info = await self._verify_medicine_with_mfds(name)
                if medicine_info:
                    verified_medicines.append(medicine_info.to_dict())
                    logger.info(f"✓ 검증 성공: {name}")
                else:
                    unverified_names.append(name)
                    logger.warning(f"✗ 검증 실패: {name}")
            
            logger.info(f"🎉 검증 완료: {len(verified_medicines)}개 약품 확인")
            
            return {
                "medicines": verified_medicines,
                "raw_ocr_text": raw_text,
                "confidence": confidence,
                "unverified_names": unverified_names
            }
            
        except Exception as e:
            logger.error(f"OCR 처리 중 오류: {str(e)}")
            raise
    
    async def _extract_text_from_image(self, image_bytes: bytes) -> Dict:
        """Azure Document Intelligence로 텍스트 추출"""
        # OCR 실행
        poller = self.ocr_client.begin_analyze_document(
            "prebuilt-read",
            image_bytes
        )
        result = poller.result()
        
        # 텍스트 추출
        all_text = []
        total_confidence = 0
        line_count = 0
        
        for page in result.pages:
            for line in page.lines:
                all_text.append(line.content)
                total_confidence += line.confidence if hasattr(line, 'confidence') else 0.9
                line_count += 1
        
        raw_text = "\n".join(all_text)
        avg_confidence = total_confidence / line_count if line_count > 0 else 0
        
        # 약 이름 필터링
        candidate_names = self._filter_medicine_names(all_text)
        
        return {
            "raw_text": raw_text,
            "candidate_names": candidate_names,
            "confidence": round(avg_confidence, 2)
        }
    
    def _filter_medicine_names(self, text_lines: List[str]) -> List[str]:
        """OCR 결과에서 약 이름 후보 필터링"""
        medicine_names = set()
        
        for line in text_lines:
            # 한글 약품명 패턴 매칭
            matches = self.medicine_pattern.findall(line)
            
            for match in matches:
                # 제외 단어 필터링
                if match not in self.exclude_words:
                    # 너무 짧은 단어 제외 (2글자 이하)
                    clean_match = re.sub(r'\d+|mg|밀리그램|정|캡슐|정제|㎎', '', match)
                    if len(clean_match) >= 2:
                        medicine_names.add(match)
        
        return sorted(list(medicine_names))
    
    async def _verify_medicine_with_mfds(
        self, 
        medicine_name: str
    ) -> Optional[MedicineInfo]:
        """
        식약처 API로 약품 정보 검증 및 조회
        
        Args:
            medicine_name: 약품명 (예: "아리셉트", "아리셉트정5밀리그램")
            
        Returns:
            MedicineInfo 객체 또는 None (검증 실패 시)
        """
        if not self.mfds_api_key:
            logger.warning("식약처 API 키가 없어 검증을 건너뜁니다.")
            return None
        
        try:
            # API 요청 파라미터
            params = {
                'serviceKey': self.mfds_api_key,
                'itemName': medicine_name,  # 제품명으로 검색
                'pageNo': 1,
                'numOfRows': 10,
                'type': 'json'
            }
            
            # API 호출
            response = requests.get(
                self.mfds_api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"식약처 API 오류: {response.status_code}")
                return None
            
            data = response.json()
            
            # 응답 파싱
            body = data.get('body', {})
            items = body.get('items', [])
            
            if not items:
                # 정확히 일치하는 약이 없으면 부분 검색 시도
                # 예: "아리셉트" → "아리셉트정5밀리그램"
                base_name = re.sub(r'\d+|mg|밀리그램|정|캡슐|정제|㎎', '', medicine_name)
                if len(base_name) >= 2 and base_name != medicine_name:
                    return await self._verify_medicine_with_mfds(base_name)
                return None
            
            # 첫 번째 매칭 결과 반환
            item = items[0] if isinstance(items, list) else items
            return MedicineInfo(item)
            
        except Exception as e:
            logger.error(f"식약처 API 조회 실패 ({medicine_name}): {str(e)}")
            return None


# 싱글톤 인스턴스
_ocr_service = None

def get_ocr_service() -> OCRService:
    """OCR 서비스 싱글톤 인스턴스 반환"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
