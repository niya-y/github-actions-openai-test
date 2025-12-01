"""
Azure Blob Storage 유틸리티
파일 위치: backend/app/utils/azure_blob.py

케어 보고서 PDF를 Azure Blob Storage에 업로드하고 
안전한 다운로드 URL(SAS)을 생성합니다.
"""
import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class AzureBlobService:
    """Azure Blob Storage 서비스 클래스"""
    
    def __init__(self):
        """
        환경 변수에서 Azure Storage 설정 로드
        
        필수 환경 변수:
        - AZURE_STORAGE_CONNECTION_STRING
        - AZURE_STORAGE_CONTAINER_NAME (기본값: 2sesacdonut)
        """
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "2sesacdonut")
        
        if not self.connection_string:
            raise ValueError(
                "AZURE_STORAGE_CONNECTION_STRING 환경 변수가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )
        
        # Blob Service Client 생성
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        
        # 컨테이너가 없으면 자동 생성
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """컨테이너가 존재하지 않으면 생성"""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            
            # 컨테이너 존재 여부 확인
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"✅ 컨테이너 '{self.container_name}' 생성 완료")
            else:
                logger.debug(f"컨테이너 '{self.container_name}' 이미 존재")
                
        except Exception as e:
            logger.warning(f"⚠️ 컨테이너 확인/생성 중 오류: {e}")
    
    def upload_pdf(
        self, 
        pdf_bytes: bytes, 
        blob_name: str,
        expiry_days: int = 7
    ) -> Tuple[str, str]:
        """
        PDF 파일을 Blob Storage에 업로드하고 SAS URL 반환
        
        Args:
            pdf_bytes: PDF 파일의 바이트 데이터
            blob_name: Blob 저장 경로/이름 
                      (예: "reports/patient_1/report_20250102.pdf")
            expiry_days: SAS URL 만료 기간 (일 단위, 기본값: 7일)
        
        Returns:
            Tuple[blob_url, sas_url]
            - blob_url: 일반 Blob URL (인증 필요)
            - sas_url: SAS 토큰이 포함된 다운로드 URL (인증 불필요, 기간 제한)
        
        Example:
            >>> pdf_data = open('report.pdf', 'rb').read()
            >>> url, sas = service.upload_pdf(
            ...     pdf_data, 
            ...     "reports/patient_1/report.pdf",
            ...     expiry_days=7
            ... )
            >>> print(sas)  # 프론트엔드로 이 URL 전송
        """
        try:
            # Blob 클라이언트 생성
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # PDF 업로드 (기존 파일 덮어쓰기)
            blob_client.upload_blob(
                pdf_bytes,
                overwrite=True,
                content_settings={
                    'content_type': 'application/pdf',
                    'content_disposition': f'attachment; filename="{blob_name.split("/")[-1]}"'
                }
            )
            
            logger.info(f"✅ PDF 업로드 완료: {blob_name} ({len(pdf_bytes)} bytes)")
            
            # SAS 토큰 생성 (읽기 전용, 기간 제한)
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),  # 읽기 전용
                expiry=datetime.utcnow() + timedelta(days=expiry_days)
            )
            
            # SAS URL 생성
            sas_url = f"{blob_client.url}?{sas_token}"
            
            logger.debug(f"SAS URL 생성 완료 (만료: {expiry_days}일 후)")
            
            return blob_client.url, sas_url
            
        except Exception as e:
            logger.error(f"❌ PDF 업로드 실패: {e}")
            raise Exception(f"Azure Blob Storage 업로드 실패: {str(e)}")
    
    def delete_blob(self, blob_name: str):
        """
        Blob 삭제 (필요 시 사용)
        
        Args:
            blob_name: 삭제할 Blob 경로
        
        Example:
            >>> service.delete_blob("reports/patient_1/old_report.pdf")
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"✅ Blob 삭제 완료: {blob_name}")
            
        except Exception as e:
            logger.error(f"❌ Blob 삭제 실패: {e}")
            raise
    
    def list_blobs(self, prefix: str = "") -> list:
        """
        특정 prefix로 시작하는 Blob 목록 조회
        
        Args:
            prefix: Blob 이름 prefix (예: "reports/patient_1/")
        
        Returns:
            Blob 이름 리스트
        
        Example:
            >>> blobs = service.list_blobs("reports/patient_1/")
            >>> print(blobs)
            ['reports/patient_1/report_20250102.pdf', ...]
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            
            blob_list = []
            for blob in container_client.list_blobs(name_starts_with=prefix):
                blob_list.append(blob.name)
            
            logger.debug(f"Blob 목록 조회 완료: {len(blob_list)}개")
            return blob_list
            
        except Exception as e:
            logger.error(f"❌ Blob 목록 조회 실패: {e}")
            return []


# ============================================
# 싱글톤 인스턴스 (지연 초기화)
# ============================================
# 애플리케이션 전체에서 하나의 인스턴스만 사용
_azure_blob_service = None


def get_azure_blob_service() -> AzureBlobService:
    """
    Azure Blob Service 싱글톤 인스턴스 반환 (지연 초기화)

    환경 변수가 로드된 후에 초기화되도록 함수로 래핑
    """
    global _azure_blob_service
    if _azure_blob_service is None:
        _azure_blob_service = AzureBlobService()
    return _azure_blob_service


# ============================================
# 사용 예시
# ============================================
if __name__ == "__main__":
    """테스트 코드"""

    # 테스트 PDF 생성
    test_pdf = b"%PDF-1.4 test content"

    try:
        # 서비스 인스턴스 가져오기
        service = get_azure_blob_service()

        # 업로드 테스트
        blob_url, sas_url = service.upload_pdf(
            pdf_bytes=test_pdf,
            blob_name="test/test_report.pdf",
            expiry_days=1
        )

        print("✅ 업로드 성공!")
        print(f"Blob URL: {blob_url}")
        print(f"SAS URL: {sas_url}")

        # 목록 조회 테스트
        blobs = service.list_blobs("test/")
        print(f"✅ Blob 목록: {blobs}")

        # 삭제 테스트
        service.delete_blob("test/test_report.pdf")
        print("✅ 삭제 완료!")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
