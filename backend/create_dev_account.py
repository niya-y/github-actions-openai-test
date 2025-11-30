"""
개발용 임시 계정 생성 스크립트
사용법: python create_dev_account.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# .env 파일 로드
load_dotenv()

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.models.profile import Guardian, Patient
from app.core.security import get_password_hash

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

print(f"📊 데이터베이스 연결 중: {DATABASE_URL[:50]}...")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_dev_account():
    """개발용 임시 계정 생성"""

    # 1. 기존 dev 계정 확인
    existing_user = db.query(User).filter(User.email == "dev@test.com").first()

    if existing_user:
        print("ℹ️  dev@test.com 계정이 이미 존재합니다.")
        print(f"   User ID: {existing_user.user_id}")
        dev_user = existing_user
        user_created = False
    else:
        # 2. 새로운 dev 사용자 생성
        dev_user = User(
            email="dev@test.com",
            username="dev_user",
            user_type="guardian",
            password=get_password_hash("dev1234"),  # 비밀번호: dev1234
            is_active=True,
            is_verified=True
        )
        db.add(dev_user)
        db.flush()  # user_id 생성을 위해 flush

        print(f"✅ User 생성 완료")
        print(f"   Email: dev@test.com")
        print(f"   Password: dev1234")
        print(f"   User ID: {dev_user.user_id}")
        user_created = True

    # 3. Guardian 프로필 확인 및 생성
    guardian = db.query(Guardian).filter(Guardian.user_id == dev_user.user_id).first()

    if guardian:
        print(f"ℹ️  Guardian 프로필이 이미 존재합니다.")
        print(f"   Guardian ID: {guardian.guardian_id}")
    else:
        guardian = Guardian(
            user_id=dev_user.user_id,
            address="서울시 강남구",
            relationship_to_patient="자녀",
            emergency_contact="01012345678"
        )
        db.add(guardian)
        db.flush()

        print(f"✅ Guardian 프로필 생성 완료")
        print(f"   Guardian ID: {guardian.guardian_id}")

    # 4. Patient 프로필 확인 및 생성
    from datetime import date
    patient = db.query(Patient).filter(Patient.guardian_id == guardian.guardian_id).first()

    if patient:
        print(f"ℹ️  Patient 프로필이 이미 존재합니다.")
        print(f"   Patient ID: {patient.patient_id}")
    else:
        patient = Patient(
            guardian_id=guardian.guardian_id,
            name="테스트 시니어",
            birth_date=date(1950, 1, 1),
            gender="Male",
            care_address="서울시 강남구 테헤란로",
            region_code="11"
        )
        db.add(patient)
        db.flush()

        print(f"✅ Patient 프로필 생성 완료")
        print(f"   Patient ID: {patient.patient_id}")

    # 5. 커밋
    db.commit()
    db.close()

    print("\n" + "="*50)
    print("✅ 개발용 임시 계정 설정 완료!")
    print("="*50)
    print("\n테스트 로그인 정보:")
    print("  이메일: dev@test.com")
    print("  비밀번호: dev1234")
    print("\n이제 이 계정으로 성향 테스트를 진행할 수 있습니다.\n")

if __name__ == "__main__":
    create_dev_account()
