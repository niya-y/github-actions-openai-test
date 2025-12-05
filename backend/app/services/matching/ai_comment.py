# ========================================
# 늘봄케어 - Azure OpenAI 코멘트 생성
# ========================================
# 파일: ai_comment.py
# 설명: Azure OpenAI를 사용한 AI 코멘트 생성

import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Azure OpenAI 클라이언트 import
try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai 패키지가 설치되지 않았습니다. pip install openai")


class AICommentGenerator:
    """Azure OpenAI를 사용한 AI 코멘트 생성기"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        """
        Args:
            api_key: Azure OpenAI API 키 (환경변수 AZURE_OPENAI_API_KEY)
            endpoint: Azure OpenAI 엔드포인트 (환경변수 AZURE_OPENAI_ENDPOINT)
            deployment_name: 배포된 모델 이름 (환경변수 AZURE_OPENAI_DEPLOYMENT)
            api_version: API 버전 (환경변수 AZURE_OPENAI_API_VERSION)
        """
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        self.client = None
        self.is_available = False

        # 클라이언트 초기화 시도
        self._init_client()

    def _init_client(self):
        """Azure OpenAI 클라이언트 초기화"""
        if not OPENAI_AVAILABLE:
            logger.warning("openai 패키지 미설치 - 규칙 기반 코멘트 사용")
            self.is_available = False
            return

        if not self.api_key:
            logger.debug("AZURE_OPENAI_API_KEY 미설정 - 규칙 기반 코멘트 사용")
            self.is_available = False
            return

        if not self.endpoint:
            logger.debug("AZURE_OPENAI_ENDPOINT 미설정 - 규칙 기반 코멘트 사용")
            self.is_available = False
            return

        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            self.is_available = True
            logger.info(f"✅ Azure OpenAI 클라이언트 초기화 성공 (deployment: {self.deployment_name})")
        except Exception as e:
            logger.warning(f"Azure OpenAI 클라이언트 초기화 실패: {e}")
            self.is_available = False

    def generate_comment(
        self,
        patient_info: Dict,
        caregiver_info: Dict,
        matching_score: float,
        grade: str,
        features: Dict,
        verbose: bool = False
    ) -> Dict:
        """
        AI 코멘트 생성

        Args:
            patient_info: 환자 정보
            caregiver_info: 간병인 정보
            matching_score: 매칭 점수
            grade: 매칭 등급
            features: 특성 값들
            verbose: 디버깅 출력 여부

        Returns:
            Dict: {"comment": str, "source": "azure_openai" | "rule_based"}
        """
        # Azure OpenAI 사용 불가시 규칙 기반 코멘트 반환
        if not self.is_available:
            return {
                "comment": self._generate_rule_based_comment(grade, features, caregiver_info),
                "source": "rule_based"
            }

        try:
            if verbose:
                logger.debug(f"Azure OpenAI API 호출 (model: {self.deployment_name})")

            # 프롬프트 생성
            prompt = self._create_prompt(
                patient_info, caregiver_info, matching_score, grade, features
            )

            # Azure OpenAI 호출
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 늘봄케어 AI 매칭 서비스의 전문 상담사입니다.
환자와 간병인의 매칭 결과를 바탕으로 보호자에게 추천 이유를 설명합니다.
- 친절하고 따뜻한 톤으로 작성하세요
- 1-2문장으로 간결하게 작성하세요
- 구체적인 장점을 언급하세요
- 한국어로 작성하세요"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )

            comment = response.choices[0].message.content.strip()

            if verbose:
                logger.debug(f"Azure OpenAI 응답 성공 (토큰: {response.usage.total_tokens})")

            return {
                "comment": comment,
                "source": "azure_openai"
            }

        except Exception as e:
            logger.warning(f"Azure OpenAI 호출 실패: {e}")
            return {
                "comment": self._generate_rule_based_comment(grade, features, caregiver_info),
                "source": "rule_based"
            }

    def _create_prompt(
        self,
        patient_info: Dict,
        caregiver_info: Dict,
        matching_score: float,
        grade: str,
        features: Dict
    ) -> str:
        """프롬프트 생성"""

        # 환자 정보
        patient_name = patient_info.get("name", "환자")
        patient_diseases = patient_info.get("diseases_list", [])
        patient_care_level = patient_info.get("care_level", "")

        # 간병인 정보
        caregiver_name = caregiver_info.get("name", caregiver_info.get("caregiver_name", "간병인"))
        experience = caregiver_info.get("experience_years", 0)
        specialties = caregiver_info.get("specialties", "")
        certifications = caregiver_info.get("certifications", "")

        # 특성 정보
        specialty_match = features.get("specialty_match_ratio", 0) * 100
        region_match = features.get("region_match_score", 0) * 100

        prompt = f"""다음 매칭 정보를 바탕으로 추천 코멘트를 작성해주세요:

[환자 정보]
- 요양등급: {patient_care_level}
- 질환: {', '.join(patient_diseases) if patient_diseases else '없음'}

[간병인 정보]
- 이름: {caregiver_name}
- 경력: {experience}년
- 자격증: {certifications}
- 전문분야: {specialties}

[매칭 결과]
- 매칭 점수: {matching_score:.1f}점
- 등급: {grade}
- 전문분야 일치율: {specialty_match:.0f}%
- 지역 일치: {region_match:.0f}%

위 정보를 바탕으로 이 간병인을 추천하는 이유를 2-3문장으로 작성해주세요."""

        return prompt

    def _generate_rule_based_comment(
        self,
        grade: str,
        features: Dict,
        caregiver_info: Dict
    ) -> str:
        """규칙 기반 코멘트 생성 (fallback)"""
        comments = []

        # 전문분야 일치율 기반 코멘트
        specialty_ratio = features.get("specialty_match_ratio", 0)
        if specialty_ratio >= 0.75:
            comments.append("환자의 질환에 대한 전문성이 매우 높습니다.")
        elif specialty_ratio >= 0.5:
            comments.append("주요 질환에 대한 케어 경험이 있습니다.")

        # 지역 기반 코멘트
        region_score = features.get("region_match_score", 0)
        if region_score >= 1.0:
            comments.append("같은 지역에서 활동하여 이동이 편리합니다.")
        elif region_score >= 0.75:
            comments.append("인근 지역에서 활동합니다.")

        # 경력 기반 코멘트
        experience = caregiver_info.get("experience_years", 0)
        if experience >= 10:
            comments.append(f"{experience}년의 풍부한 경력을 보유하고 있습니다.")
        elif experience >= 5:
            comments.append(f"{experience}년 경력의 숙련된 간병인입니다.")

        # 성격 궁합 코멘트
        avg_personality_diff = sum([
            features.get("personality_diff_empathy", 50),
            features.get("personality_diff_activity", 50),
            features.get("personality_diff_patience", 50),
            features.get("personality_diff_independence", 50)
        ]) / 4

        if avg_personality_diff <= 15:
            comments.append("성격 궁합이 매우 좋습니다.")
        elif avg_personality_diff <= 25:
            comments.append("원활한 소통이 기대됩니다.")

        # 등급별 기본 코멘트
        if not comments:
            grade_comments = {
                "A+": "모든 조건이 탁월하게 일치하는 최적의 매칭입니다.",
                "A": "전반적으로 우수한 매칭입니다.",
                "B+": "좋은 케어 서비스가 기대됩니다.",
                "B": "기본적인 케어 역량을 갖추고 있습니다.",
                "C": "추가 검토가 필요할 수 있습니다."
            }
            comments.append(grade_comments.get(grade, ""))

        return " ".join(comments)
