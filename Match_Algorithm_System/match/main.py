"""
Main execution script for BluedonuLab Caregiver Matching System
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# 상대 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

from models.data_loader import preprocess_all_data, ResidentsPreprocessor, StaffPreprocessor, MedicationsPreprocessor
from models.personality_calculator import PersonalityCalculator
from models.caregiver_analyzer import CaregiverAnalyzer
from models.matching_algorithm import MatchingAlgorithm
from database.connection import DatabaseConnection, init_database
from database.schema import (
    Resident, Staff, Medication, PatientPersonality, CaregiverStyle,
    PersonalityBasedMatching, MatchingHistory
)
from config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, DATABASE_URL, RESIDENTS_CSV,
    STAFF_CSV, MEDICATIONS_CSV
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_preprocess_data():
    """데이터 로드 및 전처리"""
    logger.info("\n" + "=" * 80)
    logger.info("📊 STEP 1: 데이터 로드 및 전처리")
    logger.info("=" * 80)

    try:
        residents, staff, medications = preprocess_all_data(
            raw_data_dir=str(RAW_DATA_DIR),
            output_dir=str(PROCESSED_DATA_DIR)
        )
        logger.info("\n✅ 데이터 로드 및 전처리 완료")
        return residents, staff, medications
    except Exception as e:
        logger.error(f"❌ 데이터 전처리 실패: {e}")
        raise


def populate_database(residents, staff, medications):
    """데이터베이스에 데이터 저장"""
    logger.info("\n" + "=" * 80)
    logger.info("🗄️  STEP 2: 데이터베이스에 데이터 저장")
    logger.info("=" * 80)

    try:
        # DB 연결 초기화
        DatabaseConnection(DATABASE_URL)
        db = DatabaseConnection.get_session()

        # Residents 저장
        logger.info(f"📝 {len(residents)}명의 환자 정보 저장 중...")
        for _, row in residents.iterrows():
            resident = Resident(
                resident_id=row['ResidentID'],
                name=row['Name'],
                date_of_birth=row['Date of Birth'],
                gender=row['Gender'],
                admission_date=row['Admission Date'],
                room_number=row['Room Number'],
                care_level=row['Care Level']
            )
            db.merge(resident)
        db.commit()
        logger.info(f"✅ {len(residents)}명의 환자 정보 저장 완료")

        # Staff 저장
        logger.info(f"📝 {len(staff)}명의 간병인 정보 저장 중...")
        for _, row in staff.iterrows():
            staff_member = Staff(
                staff_id=row['StaffID'],
                name=row['Name'],
                date_of_birth=row['Date of Birth'],
                gender=row['Gender'],
                job_title=row['Job Title'],
                employment_date=row['Employment Date'],
                experience_years=row.get('Experience_Years', 0)
            )
            db.merge(staff_member)
        db.commit()
        logger.info(f"✅ {len(staff)}명의 간병인 정보 저장 완료")

        # Medications 저장
        logger.info(f"📝 {len(medications)}개의 약물 정보 저장 중...")
        for _, row in medications.iterrows():
            medication = Medication(
                medication_id=row['MedicationID'],
                medication_name=row['Medication Name'],
                dosage=row['Dosage'],
                prescription_end_date=row['Prescription End Date'],
                resident_id=row['ResidentID']
            )
            db.merge(medication)
        db.commit()
        logger.info(f"✅ {len(medications)}개의 약물 정보 저장 완료")

        db.close()
        logger.info("\n✅ 데이터베이스 저장 완료")

    except Exception as e:
        logger.error(f"❌ 데이터베이스 저장 실패: {e}")
        raise


def calculate_patient_personalities(residents):
    """환자 성향 계산"""
    logger.info("\n" + "=" * 80)
    logger.info("🧠 STEP 3: 환자 성향 계산 (테스트 데이터)")
    logger.info("=" * 80)

    try:
        db = DatabaseConnection.get_session()

        logger.info(f"🔄 {len(residents)}명의 환자 성향 계산 중...")

        for idx, (_, resident) in enumerate(residents.iterrows()):
            # 샘플 테스트 답변 생성 (실제로는 환자가 입력하는 것)
            import random
            test_answers = [random.randint(0, 2) for _ in range(12)]

            # 성향 계산
            personality_profile = PersonalityCalculator.calculate_patient_personality(test_answers)

            # DB 저장
            patient_personality = PatientPersonality(
                patient_id=resident['ResidentID'],
                empathy=personality_profile['empathy'],
                activity=personality_profile['activity'],
                patience=personality_profile['patience'],
                independence=personality_profile['independence'],
                personality_type=personality_profile['type'],
                description=personality_profile['description'],
                test_completed=True,
                test_completed_at=datetime.utcnow()
            )
            db.merge(patient_personality)

            if (idx + 1) % 100 == 0:
                logger.info(f"  📊 {idx + 1}/{len(residents)} 처리됨...")

        db.commit()
        db.close()
        logger.info(f"✅ {len(residents)}명의 환자 성향 계산 완료")

    except Exception as e:
        logger.error(f"❌ 환자 성향 계산 실패: {e}")
        raise


def analyze_caregiver_styles(staff):
    """간병인 돌봄 스타일 분석"""
    logger.info("\n" + "=" * 80)
    logger.info("💼 STEP 4: 간병인 돌봄 스타일 분석")
    logger.info("=" * 80)

    try:
        db = DatabaseConnection.get_session()

        logger.info(f"🔄 {len(staff)}명의 간병인 스타일 분석 중...")

        caregiver_style_df = CaregiverAnalyzer.analyze_all_caregivers(staff)

        for _, caregiver_info in caregiver_style_df.iterrows():
            caregiver_style = CaregiverStyle(
                caregiver_id=caregiver_info['staff_id'],
                empathy=caregiver_info['empathy'],
                activity_support=caregiver_info['activity_support'],
                patience=caregiver_info['patience'],
                independence_support=caregiver_info['independence_support'],
                average_score=caregiver_info['average_score'],
                caregiver_type=caregiver_info['type'],
                description=caregiver_info['description']
            )
            db.merge(caregiver_style)

        db.commit()
        db.close()
        logger.info(f"✅ {len(staff)}명의 간병인 스타일 분석 완료")

    except Exception as e:
        logger.error(f"❌ 간병인 스타일 분석 실패: {e}")
        raise


def perform_matching_sample(residents, staff, limit: int = 10):
    """샘플 매칭 수행"""
    logger.info("\n" + "=" * 80)
    logger.info("🔗 STEP 5: 성향 기반 매칭 (샘플)")
    logger.info("=" * 80)

    try:
        db = DatabaseConnection.get_session()

        # DB에서 성향 및 스타일 데이터 로드
        patient_personalities = db.query(PatientPersonality).limit(limit).all()
        caregiver_styles = db.query(CaregiverStyle).all()

        logger.info(f"🔄 {len(patient_personalities)}명의 환자에 대해 매칭 수행 중...")

        matchings_saved = 0

        for patient_personality in patient_personalities:
            resident = db.query(Resident).filter(Resident.resident_id == patient_personality.patient_id).first()

            if not resident:
                continue

            # 간병인 스타일을 DataFrame으로 변환
            caregiver_data = []
            for cs in caregiver_styles:
                caregiver_data.append({
                    'staff_id': cs.caregiver_id,
                    'job_title': 'Caregiver',  # 기본값
                    'experience_years': 0,
                    'empathy': cs.empathy,
                    'activity_support': cs.activity_support,
                    'patience': cs.patience,
                    'independence_support': cs.independence_support
                })
            caregiver_styles_df = pd.DataFrame(caregiver_data)

            # 해당 환자와 매칭 가능한 간병인 찾기
            recommendations = MatchingAlgorithm.recommend_caregivers(
                patient_id=resident.resident_id,
                patient_care_level=resident.care_level,
                patient_personality={
                    'empathy': patient_personality.empathy,
                    'activity': patient_personality.activity,
                    'patience': patient_personality.patience,
                    'independence': patient_personality.independence
                },
                caregivers_df=caregiver_styles_df,
                top_n=1  # 상위 1명만 저장
            )

            # 최상위 추천 간병인과 매칭 저장
            if recommendations and len(recommendations) > 0:
                top_rec = recommendations[0]

                # PersonalityBasedMatching 저장
                matching = PersonalityBasedMatching(
                    patient_id=resident.resident_id,
                    caregiver_id=top_rec['caregiver_id'],
                    matching_score=top_rec['matching_score'],
                    grade=top_rec['grade'],
                    care_compatibility=top_rec['care_compatibility'],
                    personality_compatibility=top_rec['personality_compatibility'],
                    empathy_match=top_rec['empathy_match'],
                    activity_match=top_rec['activity_match'],
                    patience_match=top_rec['patience_match'],
                    independence_match=top_rec['independence_match'],
                    matching_reason=top_rec['reason'],
                    started_at=datetime.utcnow()
                )
                db.add(matching)
                matchings_saved += 1

        db.commit()
        db.close()
        logger.info(f"✅ {matchings_saved}개의 매칭 저장 완료")

    except Exception as e:
        logger.error(f"❌ 매칭 수행 실패: {e}")
        raise


def print_summary():
    """요약 출력"""
    logger.info("\n" + "=" * 80)
    logger.info("📈 최종 요약")
    logger.info("=" * 80)

    db = DatabaseConnection.get_session()

    try:
        residents_count = db.query(Resident).count()
        staff_count = db.query(Staff).count()
        medications_count = db.query(Medication).count()
        personalities_count = db.query(PatientPersonality).count()
        caregiver_styles_count = db.query(CaregiverStyle).count()
        matchings_count = db.query(PersonalityBasedMatching).count()

        logger.info(f"\n📊 데이터 통계:")
        logger.info(f"  • 환자 수: {residents_count}")
        logger.info(f"  • 간병인 수: {staff_count}")
        logger.info(f"  • 약물 정보: {medications_count}개")
        logger.info(f"  • 성향 계산 완료: {personalities_count}명")
        logger.info(f"  • 스타일 분석 완료: {caregiver_styles_count}명")
        logger.info(f"  • 매칭 결과: {matchings_count}개")

        # 매칭 성과 지표
        if matchings_count > 0:
            avg_matching_score = db.query(PersonalityBasedMatching).all()
            avg_score = sum([m.matching_score for m in avg_matching_score]) / len(avg_matching_score)
            logger.info(f"\n📈 매칭 성과 지표:")
            logger.info(f"  • 평균 매칭도: {avg_score:.1f}점")
            logger.info(f"  • 목표값: 75.0점 이상")
            if avg_score >= 75:
                logger.info(f"  ✅ 목표 달성!")
            else:
                logger.info(f"  ⚠️  목표 미달성 (현재: {avg_score:.1f}점)")

        logger.info("\n" + "=" * 80)
        logger.info("✅ 모든 처리 완료!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ 요약 출력 실패: {e}")
    finally:
        db.close()


def main():
    """메인 실행 함수"""
    logger.info("\n" + "🎯 BluedonuLab Caregiver Matching System - 메인 실행")
    logger.info("=" * 80)

    try:
        # Step 1: 데이터 로드 및 전처리
        residents, staff, medications = load_and_preprocess_data()

        # Step 2: 데이터베이스 초기화
        logger.info("\n" + "=" * 80)
        logger.info("🗄️  데이터베이스 초기화")
        logger.info("=" * 80)
        init_database(DATABASE_URL, reset=False)

        # Step 3: 데이터베이스에 데이터 저장
        populate_database(residents, staff, medications)

        # Step 4: 환자 성향 계산
        calculate_patient_personalities(residents)

        # Step 5: 간병인 스타일 분석
        analyze_caregiver_styles(staff)

        # Step 6: 매칭 수행 (샘플)
        perform_matching_sample(residents, staff, limit=50)

        # Step 7: 최종 요약
        print_summary()

    except Exception as e:
        logger.error(f"\n❌ 실행 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
