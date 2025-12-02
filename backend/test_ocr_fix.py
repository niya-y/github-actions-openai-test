#!/usr/bin/env python3
"""
OCR 필터 수정 테스트
약품명 필터링 로직이 제대로 작동하는지 확인
"""

import sys
import asyncio
from app.services.ocr_service import OCRService
from app.core.config import get_settings
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트용 OCR 결과 시뮬레이션
test_ocr_lines = [
    "아리셉트정5밀리그램",
    "타이레놀500mg",
    "아스피린",
    "메트포민500",
    "다이아트라",
    "복용법 : 하루 2회",
    "사용방법 식후 30분",
    "주의사항",
    "경고",
]

print("=" * 80)
print("🧪 OCR 약품명 필터 테스트")
print("=" * 80)

try:
    # OCR 서비스 초기화
    ocr_service = OCRService()

    print("\n📋 테스트 입력:")
    for line in test_ocr_lines:
        print(f"  • {line}")

    # 필터 테스트
    print("\n🔍 필터링 중...")
    medicine_names = ocr_service._filter_medicine_names(test_ocr_lines)

    print(f"\n✅ 추출된 약품명 ({len(medicine_names)}개):")
    for name in medicine_names:
        print(f"  • {name}")

    # 결과 검증
    print("\n📊 검증 결과:")
    expected = {"아리셉트정5밀리그램", "타이레놀500mg", "아스피린", "메트포민500"}
    extracted = set(medicine_names)

    print(f"  예상: {expected}")
    print(f"  추출: {extracted}")
    print(f"  일치: {expected == extracted}")

    if expected <= extracted:  # 예상값이 추출값의 부분집합
        print("\n✅ 필터가 올바르게 작동합니다!")
    else:
        missing = expected - extracted
        print(f"\n⚠️  누락된 약품: {missing}")

except Exception as e:
    print(f"\n❌ 오류: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
