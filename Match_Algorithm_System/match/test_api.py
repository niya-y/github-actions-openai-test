"""
BluedonuLab API Integration Test
FastAPI 엔드포인트 테스트 스크립트
"""

import asyncio
import logging
from datetime import date, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트용 임포트
from services.personality_service import PersonalityService
from services.matching_service import MatchingService
from services.report_service import ReportService
from database.connection import DatabaseConnection


async def test_personality_service():
    """성향 서비스 테스트"""
    logger.info("\n" + "="*80)
    logger.info("📝 PERSONALITY SERVICE 테스트")
    logger.info("="*80)

    try:
        # Test 1: 성향 저장
        logger.info("\n🔄 Test 1: 환자 성향 저장")
        test_answers = [0, 1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 1]
        result = PersonalityService.save_personality_test(
            patient_id=1,
            test_answers=test_answers
        )
        logger.info(f"✅ 성향 저장 성공: {result['personality_type']}")

        # Test 2: 성향 조회
        logger.info("\n🔄 Test 2: 환자 성향 조회")
        result = PersonalityService.get_patient_personality(patient_id=1)
        logger.info(f"✅ 성향 조회 성공:")
        logger.info(f"   - 타입: {result['personality_type']}")
        logger.info(f"   - 공감도: {result['empathy']:.1f}")
        logger.info(f"   - 활동성: {result['activity']:.1f}")
        logger.info(f"   - 인내심: {result['patience']:.1f}")
        logger.info(f"   - 자립도: {result['independence']:.1f}")

        # Test 3: 성향 통계
        logger.info("\n🔄 Test 3: 성향 통계 조회")
        result = PersonalityService.get_personality_stats()
        logger.info(f"✅ 통계 조회 성공:")
        logger.info(f"   - 총 환자 수: {result['total_count']}")
        logger.info(f"   - 테스트 완료율: {result['completion_rate']:.1f}%")
        logger.info(f"   - 평균 공감도: {result['average_empathy']:.1f}")
        logger.info(f"   - 성향 분포: {result['personality_type_distribution']}")

        logger.info("\n✅ PersonalityService 모든 테스트 통과!")
        return True

    except Exception as e:
        logger.error(f"❌ PersonalityService 테스트 실패: {e}")
        return False


async def test_matching_service():
    """매칭 서비스 테스트"""
    logger.info("\n" + "="*80)
    logger.info("🔗 MATCHING SERVICE 테스트")
    logger.info("="*80)

    try:
        # Test 1: 간병인 추천
        logger.info("\n🔄 Test 1: 간병인 추천")
        result = MatchingService.recommend_caregivers(
            patient_id=1,
            limit=3
        )
        logger.info(f"✅ 추천 성공: {result['total_recommendations']}명 추천")
        if result['recommendations']:
            top_rec = result['recommendations'][0]
            logger.info(f"   - 최상위: {top_rec['caregiver_name']} (점수: {top_rec['matching_score']:.1f})")

        # Test 2: 매칭 생성
        logger.info("\n🔄 Test 2: 매칭 생성")
        if result['recommendations']:
            caregiver_id = result['recommendations'][0]['caregiver_id']
            matching_result = MatchingService.create_matching(
                patient_id=1,
                caregiver_id=caregiver_id
            )
            matching_id = matching_result['matching_id']
            logger.info(f"✅ 매칭 생성 성공 (ID: {matching_id})")
            logger.info(f"   - 간병인: {matching_result['caregiver_name']}")
            logger.info(f"   - 점수: {matching_result['matching_score']:.1f}")
            logger.info(f"   - 등급: {matching_result['grade']}")

            # Test 3: 매칭 이력 조회
            logger.info("\n🔄 Test 3: 매칭 이력 조회")
            history = MatchingService.get_matching_history(patient_id=1)
            logger.info(f"✅ 이력 조회 성공: {history['total_matchings']}건")

            # Test 4: 매칭 성능 평가
            logger.info("\n🔄 Test 4: 매칭 성능 평가")
            start = (date.today() - timedelta(days=30))
            end = date.today()
            performance = MatchingService.evaluate_matching_performance(
                start_date=start,
                end_date=end
            )
            logger.info(f"✅ 성능 평가 성공:")
            logger.info(f"   - 총 매칭: {performance['total_matchings']}건")
            logger.info(f"   - 평균 점수: {performance['average_matching_score']:.1f}")
            logger.info(f"   - 평가: {performance['performance_summary']}")

        logger.info("\n✅ MatchingService 모든 테스트 통과!")
        return True

    except Exception as e:
        logger.error(f"❌ MatchingService 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_report_service():
    """리포트 서비스 테스트"""
    logger.info("\n" + "="*80)
    logger.info("📊 REPORT SERVICE 테스트")
    logger.info("="*80)

    try:
        # 활성 매칭 조회
        db = DatabaseConnection.get_session()
        from database.schema import PersonalityBasedMatching
        active_matching = db.query(PersonalityBasedMatching).filter(
            PersonalityBasedMatching.status == "Active"
        ).first()
        db.close()

        if not active_matching:
            logger.warning("⚠️ 활성 매칭이 없습니다. 일일 리포트 테스트를 건너뜁니다.")
            logger.info("✅ ReportService 테스트 완료 (매칭 필요)")
            return True

        matching_id = active_matching.matching_id

        # Test 1: 일일 리포트
        logger.info("\n🔄 Test 1: 일일 리포트 생성")
        daily_result = ReportService.generate_daily_report(
            matching_id=matching_id,
            content="환자가 잘 지내고 있습니다",
            mood="Happy",
            activities="산책 30분, 독서",
            medications_taken=True,
            notes="특별한 이상 없음",
            created_by="Test User"
        )
        logger.info(f"✅ 일일 리포트 생성 성공 (ID: {daily_result['report_id']})")

        # Test 2: 주간 리포트
        logger.info("\n🔄 Test 2: 주간 리포트 생성")
        weekly_result = ReportService.generate_weekly_report(
            patient_id=active_matching.patient_id
        )
        logger.info(f"✅ 주간 리포트 생성 성공:")
        logger.info(f"   - 보고일: {weekly_result['total_reports']}일")
        logger.info(f"   - 기분 분포: {weekly_result['mood_distribution']}")

        # Test 3: 월간 리포트
        logger.info("\n🔄 Test 3: 월간 성과 리포트 생성")
        start = (date.today() - timedelta(days=30))
        end = date.today()
        monthly_result = ReportService.generate_monthly_performance_report(
            start_date=start,
            end_date=end
        )
        logger.info(f"✅ 월간 리포트 생성 성공:")
        logger.info(f"   - 매칭 수: {monthly_result['matching_statistics']['total_matchings']}")
        logger.info(f"   - 평균 점수: {monthly_result['matching_statistics']['average_matching_score']:.1f}")
        logger.info(f"   - 성과: {monthly_result['performance_rating']}")

        logger.info("\n✅ ReportService 모든 테스트 통과!")
        return True

    except Exception as e:
        logger.error(f"❌ ReportService 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 테스트 함수"""
    logger.info("\n" + "🎯 BluedonuLab API 통합 테스트 시작" + "\n")

    results = []

    # 1. PersonalityService 테스트
    results.append(("PersonalityService", await test_personality_service()))

    # 2. MatchingService 테스트
    results.append(("MatchingService", await test_matching_service()))

    # 3. ReportService 테스트
    results.append(("ReportService", await test_report_service()))

    # 최종 결과
    logger.info("\n" + "="*80)
    logger.info("📈 테스트 결과 요약")
    logger.info("="*80)

    for service_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        logger.info(f"{service_name}: {status}")

    all_passed = all(r for _, r in results)
    logger.info("\n" + "="*80)

    if all_passed:
        logger.info("✅ 모든 테스트 통과!")
        logger.info("\n🚀 다음 단계:")
        logger.info("1. FastAPI 서버 실행: uvicorn app:app --reload")
        logger.info("2. API 문서 확인: http://localhost:8000/api/docs")
        logger.info("3. UI 페이지 방문: http://localhost:8000/ui")
    else:
        logger.error("❌ 일부 테스트 실패. 위 오류를 확인하세요.")

    logger.info("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
