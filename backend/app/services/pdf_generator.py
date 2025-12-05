"""
PDF 생성 서비스
파일 위치: backend/app/services/pdf_generator.py

Pyppeteer를 사용하여 HTML을 PDF로 변환합니다.
"""
import os
import asyncio
from datetime import datetime
from pyppeteer import launch
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF 생성 클래스"""
    
    def __init__(self):
        """템플릿 파일 경로 설정"""
        self.template_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'templates',
            'care_report_template.html'
        )
        
        # 템플릿 파일 존재 확인
        if not os.path.exists(self.template_path):
            logger.warning(f"⚠️ 템플릿 파일을 찾을 수 없습니다: {self.template_path}")
    
    def _load_template(self) -> str:
        """
        HTML 템플릿 파일 로드
        
        Returns:
            HTML 템플릿 문자열
        """
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            logger.debug("✅ 템플릿 로드 완료")
            return template_content
            
        except FileNotFoundError:
            logger.error(f"❌ 템플릿 파일 없음: {self.template_path}")
            raise
        except Exception as e:
            logger.error(f"❌ 템플릿 로드 실패: {e}")
            raise
    
    def _render_work_log_row(self, log_data: Dict) -> str:
        """
        간병 업무 내역 1개 행 HTML 생성
        
        Args:
            log_data: {
                'date': '25/1/2',
                'start_time': '08:00',
                'end_time': '20:00',
                'tasks': {
                    'meal': True,        # 식사보조
                    'activity': False,   # 활동보조
                    'excretion': True,   # 배변보조
                    'hygiene': False,    # 위생보조
                    'other': False       # 기타
                }
            }
        
        Returns:
            <tr> HTML 문자열
        """
        tasks = log_data.get('tasks', {})
        
        # 체크박스 HTML 생성
        checkbox_html = f"""
        <span class="checkbox-group">
            <span class="checkbox {'checked' if tasks.get('meal') else ''}"></span> 식사보조
        </span>
        <span class="checkbox-group">
            <span class="checkbox {'checked' if tasks.get('activity') else ''}"></span> 활동보조
        </span>
        <span class="checkbox-group">
            <span class="checkbox {'checked' if tasks.get('excretion') else ''}"></span> 배변보조
        </span>
        <span class="checkbox-group">
            <span class="checkbox {'checked' if tasks.get('hygiene') else ''}"></span> 위생보조
        </span>
        <span class="checkbox-group">
            <span class="checkbox {'checked' if tasks.get('other') else ''}"></span> 기타
        </span>
        """
        
        return f"""
        <tr>
            <td class="date-col">{log_data.get('date', '')}</td>
            <td class="time-col">{log_data.get('start_time', '')}</td>
            <td class="time-col">{log_data.get('end_time', '')}</td>
            <td class="task-col">{checkbox_html}</td>
        </tr>
        """
    
    def generate_html(self, data: Dict) -> str:
        """
        데이터를 HTML로 변환
        
        Args:
            data: {
                'patient_name': '김영희',
                'patient_gender': '여',
                'patient_birth_date': '1950-01-15',
                'hospital_name': '늘봄케어 병원',
                
                'caregiver_name': '간병인 김미숙',
                'caregiver_gender': '여',
                'caregiver_birth_date': '1980-05-20',
                'caregiver_phone': '010-1234-5678',
                
                'work_logs': [
                    {
                        'date': '25/1/2',
                        'start_time': '08:00',
                        'end_time': '20:00',
                        'tasks': {'meal': True, 'activity': False, ...}
                    },
                    ...
                ],
                
                'year': '2025',
                'month': '01',
                'day': '02'
            }
        
        Returns:
            완성된 HTML 문자열
        """
        try:
            # 템플릿 로드
            template_content = self._load_template()
            
            # 1. 업무 로그 HTML 생성
            work_logs_html = ""
            for log in data.get('work_logs', []):
                work_logs_html += self._render_work_log_row(log)
            
            # 2. 빈 행 추가 (총 12개 행 유지)
            current_rows = len(data.get('work_logs', []))
            for _ in range(12 - current_rows):
                work_logs_html += """
                <tr>
                    <td class="date-col"></td>
                    <td class="time-col"></td>
                    <td class="time-col"></td>
                    <td class="task-col">
                        <span class="checkbox-group"><span class="checkbox"></span> 식사보조</span>
                        <span class="checkbox-group"><span class="checkbox"></span> 활동보조</span>
                        <span class="checkbox-group"><span class="checkbox"></span> 배변보조</span>
                        <span class="checkbox-group"><span class="checkbox"></span> 위생보조</span>
                        <span class="checkbox-group"><span class="checkbox"></span> 기타</span>
                    </td>
                </tr>
                """
            
            # 3. 템플릿 변수 치환
            html = template_content
            
            # 환자 정보
            html = html.replace('{{PATIENT_NAME}}', data.get('patient_name', ''))
            html = html.replace('{{PATIENT_GENDER}}', data.get('patient_gender', ''))
            html = html.replace('{{PATIENT_BIRTH_DATE}}', data.get('patient_birth_date', ''))
            html = html.replace('{{HOSPITAL_NAME}}', data.get('hospital_name', '늘봄케어 병원'))
            
            # 간병인 정보
            html = html.replace('{{CAREGIVER_NAME}}', data.get('caregiver_name', ''))
            html = html.replace('{{CAREGIVER_GENDER}}', data.get('caregiver_gender', ''))
            html = html.replace('{{CAREGIVER_BIRTH_DATE}}', data.get('caregiver_birth_date', ''))
            html = html.replace('{{CAREGIVER_PHONE}}', data.get('caregiver_phone', ''))
            
            # 업무 로그
            html = html.replace('{{WORK_LOGS}}', work_logs_html)
            
            # 날짜
            html = html.replace('{{YEAR}}', data.get('year', ''))
            html = html.replace('{{MONTH}}', data.get('month', ''))
            html = html.replace('{{DAY}}', data.get('day', ''))
            
            logger.debug("✅ HTML 생성 완료")
            return html
            
        except Exception as e:
            logger.error(f"❌ HTML 생성 실패: {e}")
            raise
    
    async def generate_pdf(self, html_content: str) -> bytes:
        """
        HTML을 PDF로 변환 (비동기)
        
        Args:
            html_content: HTML 문자열
        
        Returns:
            PDF 바이트 데이터
        
        Note:
            - Pyppeteer는 Puppeteer의 Python 포트입니다
            - 첫 실행 시 Chromium을 자동 다운로드합니다
            - 헤드리스 모드로 실행됩니다
        """
        browser = None
        try:
            logger.info("🚀 PDF 생성 시작...")
            
            # Puppeteer 브라우저 실행
            browser = await launch(
                headless=True,  # UI 없이 실행
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',  # Docker 환경 대응
                    '--disable-gpu'
                ]
            )
            
            # 새 페이지 생성
            page = await browser.newPage()
            
            # HTML 콘텐츠 로드
            await page.setContent(html_content)

            # 렌더링 완료 대기
            await asyncio.sleep(0.5)
            
            # PDF 생성
            pdf_bytes = await page.pdf({
                'format': 'A4',           # A4 용지
                'printBackground': True,  # 배경색 포함
                'margin': {
                    'top': '10mm',
                    'bottom': '10mm',
                    'left': '10mm',
                    'right': '10mm'
                }
            })
            
            logger.info(f"✅ PDF 생성 완료 ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ PDF 생성 실패: {e}")
            raise Exception(f"PDF 변환 실패: {str(e)}")
            
        finally:
            # 브라우저 닫기
            if browser:
                await browser.close()
                logger.debug("브라우저 종료")


# ============================================
# 싱글톤 인스턴스 생성
# ============================================
pdf_generator = PDFGenerator()


# ============================================
# 사용 예시
# ============================================
if __name__ == "__main__":
    """테스트 코드"""
    
    async def test():
        """비동기 테스트 함수"""
        
        # 샘플 데이터
        sample_data = {
            'patient_name': '김영희',
            'patient_gender': '여',
            'patient_birth_date': '1950-01-15',
            'hospital_name': '테스트 병원',
            'caregiver_name': '간병인 김미숙',
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
                        'activity': False,
                        'excretion': True,
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
            print("✅ HTML 생성 성공")
            
            # PDF 생성
            pdf_bytes = await pdf_generator.generate_pdf(html)
            print(f"✅ PDF 생성 성공 ({len(pdf_bytes)} bytes)")
            
            # 파일로 저장
            with open('test_report.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("✅ 파일 저장 완료: test_report.pdf")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
    
    # 비동기 함수 실행
    asyncio.run(test())
