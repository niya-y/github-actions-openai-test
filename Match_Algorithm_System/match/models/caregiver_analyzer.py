"""
Caregiver Style Analyzer for BluedonuLab Caregiver Matching System
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================================================
# Job Title별 기본 스타일 점수 테이블
# =====================================================================

JOB_TITLE_BASE_SCORES = {
    'Nurse': {
        'empathy': 80,              # 높은 감정 이입
        'activity_support': 70,     # 중간 활동 지원
        'patience': 85,             # 매우 높은 인내심
        'independence_support': 75  # 높은 자립 지원
    },
    'Caregiver': {
        'empathy': 75,              # 중상 감정 이입
        'activity_support': 65,     # 중간 활동 지원
        'patience': 80,             # 높은 인내심
        'independence_support': 70  # 중상 자립 지원
    },
    'Therapist': {
        'empathy': 85,              # 매우 높은 감정 이입
        'activity_support': 85,     # 매우 높은 활동 지원
        'patience': 75,             # 중상 인내심
        'independence_support': 80  # 높은 자립 지원
    },
    'Doctor': {
        'empathy': 70,              # 중간 감정 이입
        'activity_support': 60,     # 낮은 활동 지원
        'patience': 70,             # 중간 인내심
        'independence_support': 85  # 매우 높은 자립 지원
    },
    'Administrator': {
        'empathy': 60,              # 낮은 감정 이입
        'activity_support': 50,     # 낮은 활동 지원
        'patience': 65,             # 중간 인내심
        'independence_support': 70  # 중상 자립 지원
    }
}


class CaregiverAnalyzer:
    """간병인 돌봄 스타일 분석"""

    @staticmethod
    def apply_experience_multiplier(base_score: float, experience_years: float) -> float:
        """
        경험도 보정 계수 적용

        Args:
            base_score: 기본 점수
            experience_years: 경험 년수

        Returns:
            경험도가 보정된 점수 (0-100)
        """
        # 경험이 많을수록 점수 상승 (최대 10% 상승)
        if experience_years < 1:
            multiplier = 0.95  # 1년 미만: 5% 감소
        elif experience_years < 3:
            multiplier = 0.98  # 1-3년: 2% 감소
        elif experience_years < 5:
            multiplier = 1.0   # 3-5년: 동일
        elif experience_years < 10:
            multiplier = 1.05  # 5-10년: 5% 증가
        else:
            multiplier = 1.10  # 10년 이상: 10% 증가

        adjusted_score = base_score * multiplier
        return np.clip(adjusted_score, 0, 100)

    @staticmethod
    def assign_style_scores(job_title: str, experience_years: float) -> Dict[str, float]:
        """
        Job Title과 경험도 → 돌봄 스타일 점수 할당

        Args:
            job_title: 직급 (Nurse, Caregiver, Doctor, Therapist, Administrator)
            experience_years: 경험 년수

        Returns:
            {'empathy': float, 'activity_support': float, 'patience': float, 'independence_support': float}
        """
        if job_title not in JOB_TITLE_BASE_SCORES:
            logger.warning(f"⚠️ 알려지지 않은 Job Title: {job_title}, 기본값으로 대체")
            job_title = 'Caregiver'

        base_scores = JOB_TITLE_BASE_SCORES[job_title]
        adjusted_scores = {}

        for dimension, base_score in base_scores.items():
            adjusted_score = CaregiverAnalyzer.apply_experience_multiplier(base_score, experience_years)
            adjusted_scores[dimension] = round(adjusted_score, 1)

        return adjusted_scores

    @staticmethod
    def classify_caregiver_type(scores: Dict[str, float]) -> str:
        """
        돌봄 스타일 점수 → 간병인 타입 분류

        Args:
            scores: {'empathy': float, 'activity_support': float, 'patience': float, 'independence_support': float}

        Returns:
            간병인 타입 문자열
        """
        empathy = scores['empathy']
        activity_support = scores['activity_support']
        patience = scores['patience']
        independence_support = scores['independence_support']

        characteristics = []

        if empathy > 75:
            characteristics.append('공감 능력 높음')
        elif empathy < 65:
            characteristics.append('전문가형')

        if activity_support > 75:
            characteristics.append('활동 지원 강함')
        elif activity_support < 60:
            characteristics.append('기본 돌봄형')

        if patience > 75:
            characteristics.append('차분형')
        elif patience < 65:
            characteristics.append('효율형')

        if independence_support > 75:
            characteristics.append('자립 지원형')
        elif independence_support < 65:
            characteristics.append('전담형')

        if not characteristics:
            return '균형형 간병인'

        return ' + '.join(characteristics[:2])

    @staticmethod
    def generate_caregiver_description(scores: Dict[str, float], job_title: str, caregiver_type: str) -> str:
        """
        간병인 프로필 설명 생성

        Args:
            scores: 돌봄 스타일 점수
            job_title: 직급
            caregiver_type: 간병인 타입

        Returns:
            설명 텍스트
        """
        empathy = scores['empathy']
        activity_support = scores['activity_support']
        patience = scores['patience']
        independence_support = scores['independence_support']

        description = f"**{job_title}**: {caregiver_type}\n\n"

        # 공감 능력
        if empathy > 75:
            description += f"• 🤝 공감 능력 ({empathy:.0f}): 환자의 감정을 잘 이해하고 공감합니다. 따뜻하고 감정적 지지를 잘 제공합니다.\n"
        elif empathy >= 65:
            description += f"• 🤝 공감 능력 ({empathy:.0f}): 적절한 수준의 감정 지원을 제공합니다.\n"
        else:
            description += f"• 🎯 공감 능력 ({empathy:.0f}): 전문가적 태도로 효율적인 돌봄을 제공합니다.\n"

        # 활동 지원
        if activity_support > 75:
            description += f"• 🏃 활동 지원 ({activity_support:.0f}): 환자의 활동을 적극 지원하고 독려합니다. 산책, 취미 등을 함께합니다.\n"
        elif activity_support >= 60:
            description += f"• 🏃 활동 지원 ({activity_support:.0f}): 필요한 활동을 지원합니다.\n"
        else:
            description += f"• 🛏️ 활동 지원 ({activity_support:.0f}): 기본적인 돌봄에 집중합니다.\n"

        # 인내심
        if patience > 75:
            description += f"• ⏳ 인내심 ({patience:.0f}): 반복되는 요청도 차분하게 처리합니다. 매우 인내심이 강합니다.\n"
        elif patience >= 65:
            description += f"• ⏳ 인내심 ({patience:.0f}): 적절한 수준의 인내심을 갖추고 있습니다.\n"
        else:
            description += f"• ⚡ 인내심 ({patience:.0f}): 빠르고 효율적으로 업무를 처리합니다.\n"

        # 자립 지원
        if independence_support > 75:
            description += f"• 🦅 자립 지원 ({independence_support:.0f}): 환자의 독립성을 존중하고 최대한 자립을 도와줍니다.\n"
        elif independence_support >= 65:
            description += f"• 🦅 자립 지원 ({independence_support:.0f}): 필요할 때 도움을 주면서 자립을 격려합니다.\n"
        else:
            description += f"• 🤝 자립 지원 ({independence_support:.0f}): 세심한 관리와 함께 지원합니다.\n"

        return description

    @staticmethod
    def analyze_caregiver_style(staff_id: int, job_title: str, experience_years: float) -> Dict:
        """
        직원 데이터 → 간병인 돌봄 스타일 프로필 계산

        Args:
            staff_id: 직원 ID
            job_title: 직급
            experience_years: 경험 년수

        Returns:
            {
                'staff_id': int,
                'job_title': str,
                'experience_years': float,
                'empathy': float (0-100),
                'activity_support': float (0-100),
                'patience': float (0-100),
                'independence_support': float (0-100),
                'type': str,
                'description': str,
                'average_score': float
            }
        """
        # 1. 스타일 점수 할당
        scores = CaregiverAnalyzer.assign_style_scores(job_title, experience_years)

        # 2. 간병인 타입 분류
        caregiver_type = CaregiverAnalyzer.classify_caregiver_type(scores)

        # 3. 설명 생성
        description = CaregiverAnalyzer.generate_caregiver_description(scores, job_title, caregiver_type)

        # 4. 평균 점수 계산
        average_score = np.mean(list(scores.values()))

        return {
            'staff_id': staff_id,
            'job_title': job_title,
            'experience_years': round(experience_years, 1),
            'empathy': scores['empathy'],
            'activity_support': scores['activity_support'],
            'patience': scores['patience'],
            'independence_support': scores['independence_support'],
            'type': caregiver_type,
            'description': description,
            'average_score': round(average_score, 1)
        }

    @staticmethod
    def analyze_all_caregivers(staff_df: pd.DataFrame) -> pd.DataFrame:
        """
        전체 Staff 데이터 → 모든 간병인의 돌봄 스타일 분석

        Args:
            staff_df: Staff DataFrame (StaffID, Name, Job Title, Experience_Years 포함)

        Returns:
            CaregiverStyle DataFrame
        """
        logger.info("\n🔄 모든 간병인의 돌봄 스타일 분석 중...")

        results = []

        for _, row in staff_df.iterrows():
            staff_id = row['StaffID']
            job_title = row['Job Title']
            experience_years = row.get('Experience_Years', 0)

            style_profile = CaregiverAnalyzer.analyze_caregiver_style(
                staff_id, job_title, experience_years
            )
            results.append(style_profile)

        caregiver_style_df = pd.DataFrame(results)

        logger.info(f"✅ {len(caregiver_style_df)}명의 간병인 분석 완료")
        logger.info(f"   - 평균 공감도: {caregiver_style_df['empathy'].mean():.1f}")
        logger.info(f"   - 평균 활동 지원: {caregiver_style_df['activity_support'].mean():.1f}")
        logger.info(f"   - 평균 인내심: {caregiver_style_df['patience'].mean():.1f}")
        logger.info(f"   - 평균 자립 지원: {caregiver_style_df['independence_support'].mean():.1f}")

        return caregiver_style_df


# =====================================================================
# 테스트 코드
# =====================================================================

if __name__ == "__main__":
    # 샘플 1: Nurse with 5년 경험
    sample1 = CaregiverAnalyzer.analyze_caregiver_style(1, 'Nurse', 5.0)

    print("=" * 60)
    print("🏥 간병인 스타일 프로필 (샘플 1)")
    print("=" * 60)
    print(f"직급: {sample1['job_title']}")
    print(f"경험: {sample1['experience_years']}년")
    print(f"\n공감도 (Empathy): {sample1['empathy']:.1f}")
    print(f"활동 지원 (Activity Support): {sample1['activity_support']:.1f}")
    print(f"인내심 (Patience): {sample1['patience']:.1f}")
    print(f"자립 지원 (Independence Support): {sample1['independence_support']:.1f}")
    print(f"평균 점수: {sample1['average_score']:.1f}")
    print(f"\n타입: {sample1['type']}")
    print(f"\n{sample1['description']}")

    # 샘플 2: Therapist with 2년 경험
    print("\n" + "=" * 60)
    sample2 = CaregiverAnalyzer.analyze_caregiver_style(2, 'Therapist', 2.0)
    print("🏥 간병인 스타일 프로필 (샘플 2)")
    print("=" * 60)
    print(f"직급: {sample2['job_title']}")
    print(f"경험: {sample2['experience_years']}년")
    print(f"\n공감도 (Empathy): {sample2['empathy']:.1f}")
    print(f"활동 지원 (Activity Support): {sample2['activity_support']:.1f}")
    print(f"인내심 (Patience): {sample2['patience']:.1f}")
    print(f"자립 지원 (Independence Support): {sample2['independence_support']:.1f}")
    print(f"평균 점수: {sample2['average_score']:.1f}")
    print(f"\n타입: {sample2['type']}")
    print(f"\n{sample2['description']}")
    print("\n" + "=" * 60)
