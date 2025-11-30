#!/usr/bin/env python3
"""
OCR 엔드포인트를 실제 약봉지 이미지로 테스트
"""

import requests
import json
from pathlib import Path

# 테스트 설정
BACKEND_URL = "http://localhost:8000"
PATIENT_ID = 1  # 테스트용 환자 ID

print("=" * 80)
print("🧪 OCR 엔드포인트 실제 이미지 테스트")
print("=" * 80)

# 1. 이미지 파일 확인
print("\n📋 [Step 1] 이미지 파일 확인")
print("-" * 80)

# 임시 테스트 이미지 경로
image_path = Path("/tmp/test_prescription.jpg")

if not image_path.exists():
    print("⚠️  이미지 파일이 없습니다.")
    print("다음 명령으로 이미지를 저장해주세요:")
    print("  1. 이미지를 /tmp/prescription_image.jpg 에 저장")
    print("  2. 다시 이 스크립트를 실행")
    import sys
    sys.exit(1)

print(f"✓ 이미지 파일: {image_path}")
print(f"✓ 파일 크기: {image_path.stat().st_size / 1024:.2f} KB")

# 2. OCR 엔드포인트 테스트
print("\n📋 [Step 2] OCR API 엔드포인트 테스트")
print("-" * 80)

try:
    # OCR 요청
    ocr_url = f"{BACKEND_URL}/api/patients/{PATIENT_ID}/medications/ocr"
    
    print(f"📤 OCR 요청 중...")
    print(f"   URL: {ocr_url}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(ocr_url, files=files, timeout=30)
    
    print(f"✓ 응답 상태: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ OCR 처리 성공!")
        print(f"\n📊 결과:")
        print(f"   - 성공: {data.get('success')}")
        print(f"   - 메시지: {data.get('message')}")
        print(f"   - 신뢰도: {(data.get('confidence', 0) * 100):.1f}%")
        
        # 검증된 약물
        medicines = data.get('medicines', [])
        if medicines:
            print(f"\n💊 검증된 약물 ({len(medicines)}개):")
            for med in medicines:
                print(f"   • {med.get('item_name')} ({med.get('entp_name')})")
        
        # 미검증 약물
        unverified = data.get('unverified_names', [])
        if unverified:
            print(f"\n⚠️  미검증 약물 ({len(unverified)}개):")
            for name in unverified:
                print(f"   • {name}")
        
        # 전체 응답
        print(f"\n📋 전체 응답:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    elif response.status_code == 422:
        print(f"❌ 유효성 검사 오류: {response.status_code}")
        print(f"   응답: {response.text[:300]}")
    elif response.status_code == 401:
        print(f"❌ 인증 오류: {response.status_code}")
        print(f"   응답: {response.text[:300]}")
    else:
        print(f"❌ 오류: {response.status_code}")
        print(f"   응답: {response.text[:300]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 실패: {str(e)}")

print("\n" + "=" * 80)
