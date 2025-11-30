"""
Personality-Based Matching Algorithm for BluedonuLab Caregiver Matching System
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================================================
# 매칭 관련 상수
# =====================================================================

CARE_LEVEL_MAPPING = {
    'Low': 1,
    'Moderate': 2,
    'High': 3
}

JOB_TITLE_CARE_LEVEL_MAPPING = {
    'Nurse': [3, 2, 1],              # High, Moderate, Low 모두 가능 (우선순위 높음)
    'Caregiver': [3, 2, 1],          # High, Moderate, Low 모두 가능 (중간)
    'Therapist': [2, 1],             # Moderate, Low (활동성 지원)
    'Doctor': [3, 2],                # High, Moderate (의료 전문성)
    'Administrator': [1]              # Low (행정 지원)
}

MATCHING_GRADE_THRESHOLDS = {
    'A+': (95, 100),
    'A': (85, 95),
    'B+': (75, 85),
    'B': (65, 75),
    'C': (0, 65)
}


class MatchingAlgorithm:
    """성향 기반 매칭 알고리즘"""

    @staticmethod
    def similarity_score(patient_value: float, caregiver_value: float, max_diff: float = 100) -> float:
        """
        두 점수 간의 유사도 계산 (코사인 유사도 기반)

        Args:
            patient_value: 환자 점수 (0-100)
            caregiver_value: 간병인 점수 (0-100)
            max_diff: 최대 차이값

        Returns:
            유사도 점수 (0-100)
        """
        diff = abs(patient_value - caregiver_value)
        similarity = (1 - (diff / max_diff)) * 100
        return np.clip(similarity, 0, 100)

    @staticmethod
    def calculate_care_level_compatibility(patient_care_level: str, caregiver_job_title: str) -> float:
        """
        의료 필요도(Care Level) 기반 적합성 계산

        Args:
            patient_care_level: 환자 Care Level (Low, Moderate, High)
            caregiver_job_title: 간병인 Job Title

        Returns:
            적합성 점수 (0-100)
        """
        patient_level = CARE_LEVEL_MAPPING.get(patient_care_level, 1)

        # 간병인이 환자의 Care Level을 지원할 수 있는지 확인
        supported_levels = JOB_TITLE_CARE_LEVEL_MAPPING.get(caregiver_job_title, [1])

        if patient_level in supported_levels:
            # 우선순위에 따른 점수 할당
            priority = len(supported_levels) - supported_levels.index(patient_level)
            compatibility = (priority / len(supported_levels)) * 100
            return compatibility
        else:
            return 0.0  # 지원 불가

    @staticmethod
    def calculate_personality_compatibility(patient_personality: Dict, caregiver_style: Dict) -> float:
        """
        성향 기반 적합성 계산

        Args:
            patient_personality: {'empathy': float, 'activity': float, 'patience': float, 'independence': float}
            caregiver_style: {'empathy': float, 'activity_support': float, 'patience': float, 'independence_support': float}

        Returns:
            적합성 점수 (0-100)
        """
        # 축별 유사도 계산
        empathy_match = MatchingAlgorithm.similarity_score(
            patient_personality['empathy'],
            caregiver_style['empathy']
        )
        activity_match = MatchingAlgorithm.similarity_score(
            patient_personality['activity'],
            caregiver_style['activity_support']
        )
        patience_match = MatchingAlgorithm.similarity_score(
            patient_personality['patience'],
            caregiver_style['patience']
        )
        independence_match = MatchingAlgorithm.similarity_score(
            patient_personality['independence'],
            caregiver_style['independence_support']
        )

        # 평균 계산
        personality_compatibility = np.mean([
            empathy_match,
            activity_match,
            patience_match,
            independence_match
        ])

        return personality_compatibility

    @staticmethod
    def calculate_matching_score(
        patient_care_level: str,
        patient_personality: Dict,
        caregiver_job_title: str,
        caregiver_style: Dict,
        care_weight: float = 0.4,
        personality_weight: float = 0.6
    ) -> Dict:
        """
        최종 매칭도 계산 (2단계 매칭)

        Args:
            patient_care_level: 환자 Care Level
            patient_personality: 환자 성향 프로필
            caregiver_job_title: 간병인 Job Title
            caregiver_style: 간병인 스타일 프로필
            care_weight: 의료 필요도 가중치 (기본: 0.4)
            personality_weight: 성향 일치도 가중치 (기본: 0.6)

        Returns:
            {
                'care_compatibility': float,
                'personality_compatibility': float,
                'matching_score': float (0-100),
                'empathy_match': float,
                'activity_match': float,
                'patience_match': float,
                'independence_match': float
            }
        """
        # 1단계: 의료 필요도 적합성
        care_compatibility = MatchingAlgorithm.calculate_care_level_compatibility(
            patient_care_level,
            caregiver_job_title
        )

        # 2단계: 성향 일치도 (상세 정보 포함)
        empathy_match = MatchingAlgorithm.similarity_score(
            patient_personality['empathy'],
            caregiver_style['empathy']
        )
        activity_match = MatchingAlgorithm.similarity_score(
            patient_personality['activity'],
            caregiver_style['activity_support']
        )
        patience_match = MatchingAlgorithm.similarity_score(
            patient_personality['patience'],
            caregiver_style['patience']
        )
        independence_match = MatchingAlgorithm.similarity_score(
            patient_personality['independence'],
            caregiver_style['independence_support']
        )

        personality_compatibility = np.mean([
            empathy_match,
            activity_match,
            patience_match,
            independence_match
        ])

        # 최종 점수
        final_score = (care_compatibility * care_weight) + (personality_compatibility * personality_weight)
        final_score = np.clip(final_score, 0, 100)

        return {
            'care_compatibility': round(care_compatibility, 1),
            'personality_compatibility': round(personality_compatibility, 1),
            'matching_score': round(final_score, 1),
            'empathy_match': round(empathy_match, 1),
            'activity_match': round(activity_match, 1),
            'patience_match': round(patience_match, 1),
            'independence_match': round(independence_match, 1)
        }

    @staticmethod
    def get_matching_grade(score: float) -> str:
        """
        매칭도 점수 → 등급 변환

        Args:
            score: 매칭도 점수 (0-100)

        Returns:
            등급 (A+, A, B+, B, C)
        """
        for grade, (min_score, max_score) in MATCHING_GRADE_THRESHOLDS.items():
            if min_score <= score < max_score:
                return grade
        return 'C'

    @staticmethod
    def generate_matching_reason(
        patient_personality: Dict,
        caregiver_style: Dict,
        matching_scores: Dict,
        caregiver_name: str = "이 간병인"
    ) -> str:
        """
        매칭 이유 생성 (AI 기반 설명)

        Args:
            patient_personality: 환자 성향
            caregiver_style: 간병인 스타일
            matching_scores: 매칭 점수 상세
            caregiver_name: 간병인 이름

        Returns:
            매칭 이유 텍스트
        """
        matching_score = matching_scores['matching_score']
        grade = MatchingAlgorithm.get_matching_grade(matching_score)

        reason = f"**등급: {grade}** (매칭도: {matching_score:.1f}점)\n\n"

        # 강점 분석
        strengths = []

        if matching_scores['empathy_match'] > 75:
            strengths.append(f"🤝 감정적 유대감이 잘 맞습니다 ({matching_scores['empathy_match']:.0f}점)")
        elif matching_scores['empathy_match'] > 60:
            strengths.append(f"🤝 감정적으로 비교적 맞는 편입니다 ({matching_scores['empathy_match']:.0f}점)")

        if matching_scores['activity_match'] > 75:
            strengths.append(f"🏃 활동 지원 방식이 잘 맞습니다 ({matching_scores['activity_match']:.0f}점)")
        elif matching_scores['activity_match'] > 60:
            strengths.append(f"🏃 활동 지원이 적절합니다 ({matching_scores['activity_match']:.0f}점)")

        if matching_scores['patience_match'] > 75:
            strengths.append(f"⏳ 간병인의 차분함이 당신의 성향과 잘 맞습니다 ({matching_scores['patience_match']:.0f}점)")
        elif matching_scores['patience_match'] > 60:
            strengths.append(f"⏳ 간병인의 인내심이 충분합니다 ({matching_scores['patience_match']:.0f}점)")

        if matching_scores['independence_match'] > 75:
            strengths.append(f"🦅 자립성 지원 방식이 잘 맞습니다 ({matching_scores['independence_match']:.0f}점)")
        elif matching_scores['independence_match'] > 60:
            strengths.append(f"🦅 자립성을 존중합니다 ({matching_scores['independence_match']:.0f}점)")

        if strengths:
            reason += "**장점:**\n" + "\n".join([f"• {s}" for s in strengths]) + "\n\n"

        # 주의사항
        weaknesses = []

        if matching_scores['empathy_match'] < 50:
            weaknesses.append(f"감정적 유대감이 약할 수 있습니다 ({matching_scores['empathy_match']:.0f}점)")

        if matching_scores['activity_match'] < 50:
            weaknesses.append(f"활동 지원 방식이 맞지 않을 수 있습니다 ({matching_scores['activity_match']:.0f}점)")

        if matching_scores['patience_match'] < 50:
            weaknesses.append(f"간병인의 인내심이 부족할 수 있습니다 ({matching_scores['patience_match']:.0f}점)")

        if weaknesses:
            reason += "**주의사항:**\n" + "\n".join([f"• {w}" for w in weaknesses]) + "\n"

        return reason

    @staticmethod
    def recommend_caregivers(
        patient_id: int,
        patient_care_level: str,
        patient_personality: Dict,
        caregivers_df: pd.DataFrame,
        top_n: int = 5
    ) -> List[Dict]:
        """
        환자에게 매칭 가능한 간병인 추천 (Top-N)

        Args:
            patient_id: 환자 ID
            patient_care_level: 환자 Care Level
            patient_personality: 환자 성향 프로필
            caregivers_df: 간병인 스타일 정보 DataFrame
            top_n: 추천할 상위 간병인 수

        Returns:
            [{
                'rank': int,
                'caregiver_id': int,
                'caregiver_name': str,
                'job_title': str,
                'matching_score': float,
                'grade': str,
                'care_compatibility': float,
                'personality_compatibility': float,
                'reason': str
            }, ...]
        """
        recommendations = []

        for _, caregiver in caregivers_df.iterrows():
            # 성향 매칭 점수 계산
            matching_info = MatchingAlgorithm.calculate_matching_score(
                patient_care_level,
                patient_personality,
                caregiver['job_title'],
                {
                    'empathy': caregiver['empathy'],
                    'activity_support': caregiver['activity_support'],
                    'patience': caregiver['patience'],
                    'independence_support': caregiver['independence_support']
                }
            )

            grade = MatchingAlgorithm.get_matching_grade(matching_info['matching_score'])

            reason = MatchingAlgorithm.generate_matching_reason(
                patient_personality,
                {
                    'empathy': caregiver['empathy'],
                    'activity_support': caregiver['activity_support'],
                    'patience': caregiver['patience'],
                    'independence_support': caregiver['independence_support']
                },
                matching_info,
                caregiver.get('name', '간병인')
            )

            recommendations.append({
                'patient_id': patient_id,
                'caregiver_id': caregiver['staff_id'],
                'caregiver_name': caregiver.get('name', 'N/A'),
                'job_title': caregiver['job_title'],
                'experience_years': caregiver['experience_years'],
                'matching_score': matching_info['matching_score'],
                'grade': grade,
                'care_compatibility': matching_info['care_compatibility'],
                'personality_compatibility': matching_info['personality_compatibility'],
                'empathy_match': matching_info['empathy_match'],
                'activity_match': matching_info['activity_match'],
                'patience_match': matching_info['patience_match'],
                'independence_match': matching_info['independence_match'],
                'reason': reason
            })

        # 매칭도 기준 정렬 (높은 순서)
        recommendations.sort(key=lambda x: x['matching_score'], reverse=True)

        # Top-N 선택 및 순위 부여
        for i, rec in enumerate(recommendations[:top_n], 1):
            rec['rank'] = i

        return recommendations[:top_n]


# =====================================================================
# 테스트 코드
# =====================================================================

if __name__ == "__main__":
    # 샘플 데이터
    patient_care_level = "Moderate"
    patient_personality = {
        'empathy': 80,
        'activity': 55,
        'patience': 85,
        'independence': 60
    }

    caregiver_job_title = "Caregiver"
    caregiver_style = {
        'empathy': 75,
        'activity_support': 65,
        'patience': 80,
        'independence_support': 70
    }

    # 매칭도 계산
    matching_info = MatchingAlgorithm.calculate_matching_score(
        patient_care_level,
        patient_personality,
        caregiver_job_title,
        caregiver_style
    )

    grade = MatchingAlgorithm.get_matching_grade(matching_info['matching_score'])

    print("=" * 60)
    print("📊 매칭도 분석")
    print("=" * 60)
    print(f"\n의료 필요도 적합성: {matching_info['care_compatibility']:.1f}점")
    print(f"성향 일치도: {matching_info['personality_compatibility']:.1f}점")
    print(f"  - 공감도: {matching_info['empathy_match']:.1f}점")
    print(f"  - 활동성: {matching_info['activity_match']:.1f}점")
    print(f"  - 인내심: {matching_info['patience_match']:.1f}점")
    print(f"  - 독립성: {matching_info['independence_match']:.1f}점")
    print(f"\n📈 최종 매칭도: {matching_info['matching_score']:.1f}점")
    print(f"등급: {grade}")

    # 매칭 이유 생성
    reason = MatchingAlgorithm.generate_matching_reason(
        patient_personality,
        caregiver_style,
        matching_info,
        "박수진 간병인"
    )

    print(f"\n📝 매칭 이유:\n{reason}")
    print("=" * 60)
