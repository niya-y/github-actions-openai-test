"""
Care Plan 생성 AI 서비스
Azure OpenAI를 사용하여 환자 정보와 간병인 정보를 기반으로 케어 플랜을 생성합니다.
"""

import json
import logging
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from pydantic import BaseModel
import os
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ActivityItem(BaseModel):
    """활동 항목"""
    time: str
    title: str
    assignee: str
    note: str = ""


class DaySchedule(BaseModel):
    """일일 일정"""
    day: str
    activities: list[ActivityItem]


class ActivityReview(BaseModel):
    """활동 피드백"""
    activity_time: str
    activity_title: str
    feedback_type: str  # adjustment, appropriate, inappropriate, suggestion
    reason: str
    suggestion: str
    alternative_time: Optional[str] = None


class CaregiverFeedback(BaseModel):
    """간병인 피드백"""
    overall_comment: str
    activity_reviews: list[ActivityReview]


class CarePlanResponse(BaseModel):
    """케어 플랜 응답"""
    patient_name: str
    caregiver_name: str
    summary: Dict[str, Any]
    weekly_schedule: list[DaySchedule]
    caregiver_feedback: CaregiverFeedback


class CarePlanGenerationService:
    """Azure OpenAI를 사용한 케어 플랜 생성"""

    def __init__(self):
        """Azure OpenAI 클라이언트 초기화"""
        settings = get_settings()

        api_key = settings.AZURE_OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT
        deployment_name = settings.AZURE_OPENAI_DEPLOYMENT
        api_version = settings.AZURE_OPENAI_API_VERSION

        logger.info("=" * 80)
        logger.info("[CarePlanGenerationService] 초기화 중...")
        logger.info(f"API Key exists: {bool(api_key)}")
        logger.info(f"Endpoint exists: {bool(endpoint)}")
        logger.info(f"Endpoint value: {endpoint}")
        logger.info(f"Deployment exists: {bool(deployment_name)}")
        logger.info(f"Deployment value: {deployment_name}")
        logger.info(f"API Version: {api_version}")
        logger.info("=" * 80)

        if not all([api_key, endpoint, deployment_name]):
            logger.warning("❌ Azure OpenAI credentials are not fully configured")
            logger.warning(f"API Key: {bool(api_key)}, Endpoint: {bool(endpoint)}, Deployment: {bool(deployment_name)}")
            self.client = None
        else:
            logger.info(f"✅ Azure OpenAI 클라이언트 초기화 성공 - Deployment: {deployment_name}")
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            self.deployment_name = deployment_name

    def generate_care_plan(
        self,
        patient_info: Dict[str, Any],
        caregiver_info: Dict[str, Any],
        patient_personality: Dict[str, float],
        care_requirements: Dict[str, Any]
    ) -> CarePlanResponse:
        """
        환자 정보와 간병인 정보를 기반으로 케어 플랜을 생성합니다.

        Args:
            patient_info: 환자 정보 (나이, 건강상태 등)
            caregiver_info: 간병인 정보 (이름, 경력, 전문성 등)
            patient_personality: 환자 성격 점수
            care_requirements: 돌봄 요구사항

        Returns:
            생성된 케어 플랜
        """

        logger.info("=" * 80)
        logger.info("[generate_care_plan] 시작")
        logger.info(f"Patient: {patient_info}")
        logger.info(f"Caregiver: {caregiver_info}")
        logger.info(f"Client initialized: {self.client is not None}")
        logger.info("=" * 80)

        if self.client is None:
            logger.warning("❌ Using fallback care plan generation (Azure OpenAI not configured)")
            return self._generate_fallback_care_plan(patient_info, caregiver_info)

        try:
            # 프롬프트 구성
            prompt = self._build_prompt(
                patient_info,
                caregiver_info,
                patient_personality,
                care_requirements
            )

            # Azure OpenAI 호출
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 전문적인 간병 플래너입니다. 환자와 간병인의 정보를 기반으로 최적의 케어 플랜을 생성합니다. 항상 유효한 JSON 형식으로 응답하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            # 응답 파싱
            response_text = response.choices[0].message.content
            care_plan_json = self._extract_json(response_text)

            # JSON을 CarePlanResponse로 변환
            care_plan = CarePlanResponse(**care_plan_json)
            logger.info(f"Care plan generated successfully for patient")
            return care_plan

        except Exception as e:
            logger.error(f"Error generating care plan: {e}")
            # 폴백: 하드코딩된 케어 플랜 반환
            return self._generate_fallback_care_plan(patient_info, caregiver_info)

    def _build_prompt(
        self,
        patient_info: Dict[str, Any],
        caregiver_info: Dict[str, Any],
        patient_personality: Dict[str, float],
        care_requirements: Dict[str, Any]
    ) -> str:
        """AI에게 전달할 프롬프트 구성"""

        prompt = f"""
다음 환자와 간병인 정보를 기반으로 7일간의 상세한 케어 플랜을 생성하세요.

## 환자 정보
- 이름: {patient_info.get('name', '환자')}
- 나이: {patient_info.get('age', 'N/A')}
- 건강상태: {patient_info.get('condition', 'N/A')}
- 특수질환: {patient_info.get('special_conditions', 'N/A')}

## 환자 성격 점수 (0-100)
- 공감도: {patient_personality.get('empathy_score', 50)}
- 활동성: {patient_personality.get('activity_score', 50)}
- 인내심: {patient_personality.get('patience_score', 50)}
- 자립성: {patient_personality.get('independence_score', 50)}

## 간병인 정보
- 이름: {caregiver_info.get('name', '간병인')}
- 경력: {caregiver_info.get('experience_years', 0)}년
- 전문성: {caregiver_info.get('specialties', [])}

## 돌봄 요구사항
- 돌봄 유형: {care_requirements.get('care_type', 'nursing-aide')}
- 희망 시간: {care_requirements.get('time_slots', [])}
- 성별 선호: {care_requirements.get('gender', 'any')}
- 필요 기술: {care_requirements.get('skills', [])}

## 생성해야 할 형식 (JSON):
{{
  "patient_name": "환자이름",
  "caregiver_name": "간병인이름",
  "summary": {{
    "total_activities": 42,
    "participants": 4,
    "daily_hours": 6
  }},
  "weekly_schedule": [
    {{
      "day": "월요일",
      "activities": [
        {{
          "time": "HH:MM",
          "title": "활동명",
          "assignee": "담당자",
          "note": "특수사항"
        }}
      ]
    }},
    ...7일 모두 작성...
  ],
  "caregiver_feedback": {{
    "overall_comment": "종합 의견",
    "activity_reviews": [
      {{
        "activity_time": "HH:MM",
        "activity_title": "활동명",
        "feedback_type": "adjustment|appropriate|inappropriate|suggestion",
        "reason": "이유",
        "suggestion": "구체적인 제안",
        "alternative_time": "HH:MM (선택사항)"
      }}
    ]
  }}
}}

다음 요구사항을 꼭 지켜주세요:
1. 각 일정은 07:00부터 21:00까지의 범위에서 생성
2. 식사, 약 복용, 활동, 휴식 등을 균형있게 배치
3. 간병인과 가족 모두가 참여할 수 있도록 배치
4. 환자의 성격 점수와 건강상태를 반영
5. 현실적이고 실행 가능한 일정
6. 반드시 유효한 JSON 형식으로만 응답

응답은 JSON만 포함하고 다른 텍스트는 포함하지 마세요.
"""
        return prompt

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """응답에서 JSON 추출"""
        # JSON 블록 찾기
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)

        raise ValueError("No valid JSON found in response")

    def _generate_fallback_care_plan(
        self,
        patient_info: Dict[str, Any],
        caregiver_info: Dict[str, Any]
    ) -> CarePlanResponse:
        """폴백: 기본 케어 플랜 생성"""

        patient_name = patient_info.get("name", "환자")
        caregiver_name = caregiver_info.get("name", "간병인")

        return CarePlanResponse(
            patient_name=patient_name,
            caregiver_name=caregiver_name,
            summary={
                "total_activities": 42,
                "participants": 4,
                "daily_hours": 6
            },
            weekly_schedule=[
                DaySchedule(
                    day="월요일",
                    activities=[
                        ActivityItem(
                            time="07:00",
                            title="기상 도움",
                            assignee=f"👨‍⚕️ 간병인 {caregiver_name}"
                        ),
                        ActivityItem(
                            time="07:30",
                            title="아침 식사 준비",
                            assignee="👩 가족"
                        ),
                        ActivityItem(
                            time="08:00",
                            title="약 복용 확인",
                            assignee=f"👨‍⚕️ 간병인 {caregiver_name}",
                            note="⚠️ 아스피린 100mg, 메트포민 500mg"
                        ),
                        ActivityItem(
                            time="09:00",
                            title="가벼운 스트레칭",
                            assignee=f"👨‍⚕️ 간병인 {caregiver_name}"
                        ),
                        ActivityItem(
                            time="10:00",
                            title="산책 (날씨 좋을 시)",
                            assignee="👩 가족"
                        ),
                        ActivityItem(
                            time="12:00",
                            title="점심 식사 준비",
                            assignee=f"👨‍⚕️ 간병인 {caregiver_name}"
                        )
                    ]
                )
            ],
            caregiver_feedback=CaregiverFeedback(
                overall_comment="전반적으로 잘 구성된 케어 플랜입니다.",
                activity_reviews=[
                    ActivityReview(
                        activity_time="08:00",
                        activity_title="약 복용 확인",
                        feedback_type="adjustment",
                        reason="order",
                        suggestion="약 복용은 식사 후 30분 뒤에 하는 것이 더 좋습니다.",
                        alternative_time="08:30"
                    )
                ]
            )
        )
