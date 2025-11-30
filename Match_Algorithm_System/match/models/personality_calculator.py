"""
Patient Personality Calculator for BluedonuLab Caregiver Matching System
"""

import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================================================
# 성향 테스트 질문 및 점수 매핑
# =====================================================================

PERSONALITY_TEST_QUESTIONS = [
    {
        'id': 1,
        'question': '반복해서 같은 질문을 할 때 간병인이 어떻게 하길 원하나요?',
        'axis': 'patience',
        'choices': [
            {'text': '차분히 다시 설명한다', 'score': 10},
            {'text': '짜증이 나지만 참는다', 'score': 5},
            {'text': '바로 대화를 돌린다', 'score': -10}
        ]
    },
    {
        'id': 2,
        'question': '혼자 할 수 있는 것은 최대한 혼자 하고 싶다',
        'axis': 'independence',
        'choices': [
            {'text': '완전히 동의', 'score': 10},
            {'text': '약간 동의', 'score': 5},
            {'text': '동의하지 않음', 'score': -10}
        ]
    },
    {
        'id': 3,
        'question': '간병인과의 감정적인 유대감이 얼마나 중요한가요?',
        'axis': 'empathy',
        'choices': [
            {'text': '매우 중요하다', 'score': 10},
            {'text': '어느 정도 중요하다', 'score': 5},
            {'text': '중요하지 않다', 'score': -10}
        ]
    },
    {
        'id': 4,
        'question': '하루를 어떻게 보내고 싶으신가요?',
        'axis': 'activity',
        'choices': [
            {'text': '활동적이고 바쁘게', 'score': 10},
            {'text': '적당히 활동', 'score': 5},
            {'text': '조용히 쉬면서', 'score': -10}
        ]
    },
    {
        'id': 5,
        'question': '당신의 감정 상태를 이해해주는 간병인이 필요한가요?',
        'axis': 'empathy',
        'choices': [
            {'text': '정말 필요하다', 'score': 10},
            {'text': '어느 정도 필요하다', 'score': 5},
            {'text': '필요 없다', 'score': -10}
        ]
    },
    {
        'id': 6,
        'question': '새로운 활동이나 취미를 시도하고 싶으신가요?',
        'axis': 'activity',
        'choices': [
            {'text': '자주 시도하고 싶다', 'score': 10},
            {'text': '가끔 시도하고 싶다', 'score': 5},
            {'text': '특별히 원하지 않는다', 'score': -10}
        ]
    },
    {
        'id': 7,
        'question': '복잡한 의료 절차를 여러 번 설명해야 할 때 어떻게 하길 원하나요?',
        'axis': 'patience',
        'choices': [
            {'text': '몇 번이라도 차분하게 설명', 'score': 10},
            {'text': '2-3번 설명 후 간단히', 'score': 5},
            {'text': '한 번만 설명', 'score': -10}
        ]
    },
    {
        'id': 8,
        'question': '도움이 필요할 때 간병인에게 자주 도움을 청하는가요?',
        'axis': 'independence',
        'choices': [
            {'text': '가능한 스스로 하려 한다', 'score': 10},
            {'text': '필요할 때 도움을 청한다', 'score': 5},
            {'text': '자주 도움이 필요하다', 'score': -10}
        ]
    },
    {
        'id': 9,
        'question': '간병인과의 관계에서 친밀함이 어느 정도 중요한가요?',
        'axis': 'empathy',
        'choices': [
            {'text': '매우 중요 (친구 같은 관계)', 'score': 10},
            {'text': '어느 정도 중요 (따뜻한 관계)', 'score': 5},
            {'text': '중요하지 않음 (전문적 관계)', 'score': -10}
        ]
    },
    {
        'id': 10,
        'question': '물리 치료, 운동, 산책 등 신체 활동을 얼마나 하고 싶으신가요?',
        'axis': 'activity',
        'choices': [
            {'text': '매일 적극적으로', 'score': 10},
            {'text': '주 3-4회 적당히', 'score': 5},
            {'text': '최소한의 활동만', 'score': -10}
        ]
    },
    {
        'id': 11,
        'question': '실수를 했을 때 간병인이 어떻게 하길 원하나요?',
        'axis': 'patience',
        'choices': [
            {'text': '차분하게 다시 설명해준다', 'score': 10},
            {'text': '가볍게 넘어간다', 'score': 5},
            {'text': '지적하고 넘어간다', 'score': -10}
        ]
    },
    {
        'id': 12,
        'question': '간병인의 지원 없이도 독립적으로 생활하고 싶은가요?',
        'axis': 'independence',
        'choices': [
            {'text': '완전히 동의한다', 'score': 10},
            {'text': '어느 정도 동의한다', 'score': 5},
            {'text': '동의하지 않는다', 'score': -10}
        ]
    }
]


class PersonalityCalculator:
    """환자 성향 점수 계산"""

    @staticmethod
    def calculate_axis_score(test_answers: List[int]) -> Dict[str, float]:
        """
        테스트 답변 → 4개 축별 점수 계산

        Args:
            test_answers: 12개 질문에 대한 선택지 인덱스 (0, 1, 2)

        Returns:
            {'empathy': 0-100, 'activity': 0-100, 'patience': 0-100, 'independence': 0-100}
        """
        if len(test_answers) != 12:
            raise ValueError(f"정확히 12개의 답변이 필요합니다 (받은 답변: {len(test_answers)})")

        axis_scores = {
            'empathy': [],
            'activity': [],
            'patience': [],
            'independence': []
        }

        # 각 질문의 답변으로부터 축별 점수 수집
        for i, answer_index in enumerate(test_answers):
            if answer_index < 0 or answer_index > 2:
                raise ValueError(f"질문 {i+1}: 선택지는 0-2 사이여야 합니다")

            question = PERSONALITY_TEST_QUESTIONS[i]
            axis = question['axis']
            score = question['choices'][answer_index]['score']
            axis_scores[axis].append(score)

        # 각 축별 점수 계산 (합계 → 정규화 0-100)
        normalized_scores = {}
        for axis, scores in axis_scores.items():
            # 합계: 각 축은 3개 질문 × 10점 = 최대 30점, 최소 -30점
            total = sum(scores)
            # 정규화: [-30, 30] → [0, 100]
            normalized = ((total + 30) / 60) * 100
            normalized = np.clip(normalized, 0, 100)
            normalized_scores[axis] = round(normalized, 1)

        return normalized_scores

    @staticmethod
    def classify_personality_type(scores: Dict[str, float]) -> str:
        """
        4개 축 점수 → 성향 타입 분류

        Args:
            scores: {'empathy': float, 'activity': float, 'patience': float, 'independence': float}

        Returns:
            성향 타입 문자열
        """
        empathy = scores['empathy']
        activity = scores['activity']
        patience = scores['patience']
        independence = scores['independence']

        # 점수가 높은 축 우선순위 파악
        high_threshold = 65
        low_threshold = 35

        characteristics = []

        if empathy > high_threshold:
            characteristics.append('공감 중심형')
        elif empathy < low_threshold:
            characteristics.append('독립형')

        if activity > high_threshold:
            characteristics.append('활동형')
        elif activity < low_threshold:
            characteristics.append('휴식형')

        if patience > high_threshold:
            characteristics.append('차분형')
        elif patience < low_threshold:
            characteristics.append('효율형')

        if independence > high_threshold:
            characteristics.append('자립형')
        elif independence < low_threshold:
            characteristics.append('의존형')

        # 특성 없으면 '균형형'
        if not characteristics:
            return '균형형'

        return ' + '.join(characteristics[:2])  # 상위 2개 특성만 표시

    @staticmethod
    def generate_personality_description(scores: Dict[str, float], personality_type: str) -> str:
        """
        AI 기반 성향 설명 생성 (템플릿 기반)

        Args:
            scores: 성향 점수
            personality_type: 성향 타입

        Returns:
            설명 텍스트
        """
        empathy = scores['empathy']
        activity = scores['activity']
        patience = scores['patience']
        independence = scores['independence']

        description = f"당신은 다음과 같은 특징을 가지고 있습니다:\n\n"

        # 공감도 설명
        if empathy > 65:
            description += f"• 🤝 공감도 ({empathy:.0f}): 감정적 지지가 매우 중요합니다. 간병인과의 따뜻한 관계를 원하고, 당신의 감정을 이해해주는 사람을 선호합니다.\n"
        elif empathy < 35:
            description += f"• 🎯 공감도 ({empathy:.0f}): 전문적이고 효율적인 관계를 선호합니다. 감정보다는 실질적인 도움에 더 가치를 둡니다.\n"
        else:
            description += f"• ⚖️ 공감도 ({empathy:.0f}): 전문성과 따뜻함의 균형을 원합니다.\n"

        # 활동성 설명
        if activity > 65:
            description += f"• 🏃 활동성 ({activity:.0f}): 활동적인 생활을 원합니다. 산책, 취미, 새로운 경험 등 다양한 활동을 통해 자극을 받고 싶어 합니다.\n"
        elif activity < 35:
            description += f"• 🛏️ 활동성 ({activity:.0f}): 조용하고 편안한 환경을 선호합니다. 무리하지 않는 범위에서 필요한 활동만 하길 원합니다.\n"
        else:
            description += f"• ⚖️ 활동성 ({activity:.0f}): 적당한 수준의 활동을 원합니다.\n"

        # 인내심 필요도 설명
        if patience > 65:
            description += f"• ⏳ 인내심 필요도 ({patience:.0f}): 간병인의 차분함과 인내심을 매우 중요하게 생각합니다. 반복된 설명과 천천한 진행을 원합니다.\n"
        elif patience < 35:
            description += f"• ⚡ 인내심 필요도 ({patience:.0f}): 빠르고 효율적인 진행을 선호합니다. 간병인이 능숙하고 신속하게 일하길 원합니다.\n"
        else:
            description += f"• ⚖️ 인내심 필요도 ({patience:.0f}): 적절한 속도의 진행을 원합니다.\n"

        # 독립성 설명
        if independence > 65:
            description += f"• 🦅 독립성 ({independence:.0f}): 최대한 스스로 할 수 있기를 원합니다. 간병인은 필요할 때만 도움을 주길 바랍니다.\n"
        elif independence < 35:
            description += f"• 🤝 의존성 ({independence:.0f}): 자주 도움과 지지가 필요합니다. 간병인의 세심한 관리와 전폭적인 지원을 원합니다.\n"
        else:
            description += f"• ⚖️ 독립성 ({independence:.0f}): 필요할 때 도움을 청하는 균형 있는 관계를 원합니다.\n"

        description += f"\n🎯 **권장 간병인 유형**: {PersonalityCalculator.recommend_caregiver_type(scores)}"

        return description

    @staticmethod
    def recommend_caregiver_type(scores: Dict[str, float]) -> str:
        """
        점수 기반 권장 간병인 유형

        Args:
            scores: 성향 점수

        Returns:
            권장 간병인 유형
        """
        empathy = scores['empathy']
        activity = scores['activity']
        independence = scores['independence']

        if empathy > 65 and activity > 55:
            return "따뜻한 감정 지원과 함께 활동을 함께하는 간병인 (Therapist/Care Provider)"
        elif empathy > 65:
            return "감정적 지지에 강한 간병인 (Caregiver with high empathy)"
        elif activity > 65:
            return "활동을 활발하게 지원하는 간병인 (Active Therapist)"
        elif independence > 70:
            return "전문적이고 효율적인 간병인 (Professional Caregiver)"
        else:
            return "균형 잡힌 전담 간병인 (Balanced Care Provider)"

    @staticmethod
    def calculate_patient_personality(test_answers: List[int]) -> Dict:
        """
        12개 테스트 답변 → 환자 성향 프로필 계산

        Args:
            test_answers: 12개 질문에 대한 선택지 인덱스 (0, 1, 2)

        Returns:
            {
                'empathy': float (0-100),
                'activity': float (0-100),
                'patience': float (0-100),
                'independence': float (0-100),
                'type': str,
                'description': str
            }
        """
        # 1. 축별 점수 계산
        scores = PersonalityCalculator.calculate_axis_score(test_answers)

        # 2. 성향 타입 분류
        personality_type = PersonalityCalculator.classify_personality_type(scores)

        # 3. AI 기반 설명 생성
        description = PersonalityCalculator.generate_personality_description(scores, personality_type)

        return {
            'empathy': scores['empathy'],
            'activity': scores['activity'],
            'patience': scores['patience'],
            'independence': scores['independence'],
            'type': personality_type,
            'description': description
        }


# =====================================================================
# 테스트 코드
# =====================================================================

if __name__ == "__main__":
    # 샘플 테스트: 공감 중심형 환자
    sample_answers = [
        0,  # Q1: 차분히 다시 설명 (patience +10)
        0,  # Q2: 완전히 동의 (independence +10)
        0,  # Q3: 매우 중요 (empathy +10)
        1,  # Q4: 적당히 활동 (activity +5)
        0,  # Q5: 정말 필요 (empathy +10)
        1,  # Q6: 가끔 시도 (activity +5)
        0,  # Q7: 몇 번이라도 (patience +10)
        1,  # Q8: 필요할 때 (independence +5)
        0,  # Q9: 매우 중요 (empathy +10)
        1,  # Q10: 주 3-4회 (activity +5)
        0,  # Q11: 차분하게 (patience +10)
        0,  # Q12: 완전히 동의 (independence +10)
    ]

    result = PersonalityCalculator.calculate_patient_personality(sample_answers)

    print("=" * 60)
    print("🎯 환자 성향 프로필")
    print("=" * 60)
    print(f"\n공감도 (Empathy): {result['empathy']:.1f}")
    print(f"활동성 (Activity): {result['activity']:.1f}")
    print(f"인내심 (Patience): {result['patience']:.1f}")
    print(f"독립성 (Independence): {result['independence']:.1f}")
    print(f"\n성향 타입: {result['type']}")
    print(f"\n설명:\n{result['description']}")
    print("\n" + "=" * 60)
