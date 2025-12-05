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
        timeout = settings.AZURE_OPENAI_TIMEOUT

        logger.info("=" * 80)
        logger.info("[CarePlanGenerationService] 초기화 중...")
        logger.info(f"API Key exists: {bool(api_key)}")
        logger.info(f"Endpoint exists: {bool(endpoint)}")
        logger.info(f"Endpoint value: {endpoint}")
        logger.info(f"Deployment exists: {bool(deployment_name)}")
        logger.info(f"Deployment value: {deployment_name}")
        logger.info(f"API Version: {api_version}")
        logger.info(f"Timeout: {timeout} seconds")
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
                azure_endpoint=endpoint,
                timeout=timeout
            )
            self.deployment_name = deployment_name
            self.timeout = timeout

    def generate_care_plan(
        self,
        patient_info: Dict[str, Any],
        caregiver_info: Dict[str, Any],
        patient_personality: Dict[str, float],
        care_requirements: Dict[str, Any],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
        preferred_time_slots: Optional[list] = None
    ) -> CarePlanResponse:
        """
        환자 정보와 간병인 정보를 기반으로 케어 플랜을 생성합니다.

        Args:
            patient_info: 환자 정보 (나이, 건강상태 등)
            caregiver_info: 간병인 정보 (이름, 경력, 전문성 등)
            patient_personality: 환자 성격 점수
            care_requirements: 돌봄 요구사항
            start_date: 케어 시작일 (YYYY-MM-DD)
            end_date: 케어 종료일 (YYYY-MM-DD)
            days: 일수 (start_date/end_date 대신 사용 가능)
            preferred_time_slots: 선호 시간대 리스트 (예: ['morning', 'afternoon'])

        Returns:
            생성된 케어 플랜
        """
        # preferred_time_slots 기본값 설정
        if not preferred_time_slots:
            preferred_time_slots = care_requirements.get('time_slots', ['morning', 'afternoon'])

        logger.info("=" * 80)
        logger.info("[generate_care_plan] 시작")
        logger.info(f"Patient: {patient_info}")
        logger.info(f"Caregiver: {caregiver_info}")
        logger.info(f"Preferred time slots: {preferred_time_slots}")
        logger.info(f"Client initialized: {self.client is not None}")
        logger.info("=" * 80)

        if self.client is None:
            logger.warning("❌ Using fallback care plan generation (Azure OpenAI not configured)")
            return self._generate_fallback_care_plan(patient_info, caregiver_info, preferred_time_slots)

        try:
            # 일수 계산
            from datetime import datetime
            try:
                if start_date and end_date:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    calculated_days = (end - start).days + 1  # 시작일 포함
                    # 최대 7일로 제한
                    calculated_days = min(calculated_days, 7)
                elif days:
                    calculated_days = min(days, 7)
                else:
                    calculated_days = 7  # 기본값
            except ValueError as date_error:
                logger.error(f"❌ Date parsing error: {str(date_error)}")
                calculated_days = 7  # 기본값으로 폴백

            logger.info(f"📅 케어 플랜 생성 기간: {calculated_days}일")

            # 프롬프트 구성
            try:
                prompt = self._build_prompt(
                    patient_info,
                    caregiver_info,
                    patient_personality,
                    care_requirements,
                    calculated_days,
                    preferred_time_slots
                )
            except Exception as prompt_error:
                logger.error(f"❌ Prompt building error: {str(prompt_error)}")
                raise

            # Azure OpenAI 호출 (타임아웃 설정)
            try:
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
                    max_tokens=2000,
                    timeout=30  # 30초 타임아웃
                )
            except Exception as api_error:
                logger.error(f"❌ Azure OpenAI API error: {str(api_error)}")
                raise

            # 응답 검증
            if not response or not response.choices or len(response.choices) == 0:
                logger.error("❌ Empty response from Azure OpenAI")
                raise ValueError("Azure OpenAI returned empty response")

            # 응답 파싱
            try:
                response_text = response.choices[0].message.content
                if not response_text:
                    logger.error("❌ Response content is empty")
                    raise ValueError("Response content is empty")

                care_plan_json = self._extract_json(response_text)
            except (ValueError, json.JSONDecodeError) as parse_error:
                logger.error(f"❌ Response parsing error: {str(parse_error)}")
                raise

            # JSON을 CarePlanResponse로 변환 (검증)
            try:
                care_plan = CarePlanResponse(**care_plan_json)
                logger.info(f"✅ Care plan generated successfully for patient: {patient_info.get('name', 'Unknown')}")
                return care_plan
            except Exception as validation_error:
                logger.error(f"❌ CarePlanResponse validation error: {str(validation_error)}")
                logger.error(f"❌ Invalid JSON structure: {care_plan_json}")
                raise

        except Exception as e:
            logger.error(f"❌ Error generating care plan: {str(e)}")
            logger.warning("⚠️ Falling back to default care plan generation")
            # 폴백: 하드코딩된 케어 플랜 반환
            return self._generate_fallback_care_plan(patient_info, caregiver_info, preferred_time_slots)

    def _build_prompt(
        self,
        patient_info: Dict[str, Any],
        caregiver_info: Dict[str, Any],
        patient_personality: Dict[str, float],
        care_requirements: Dict[str, Any],
        days: int = 7,
        preferred_time_slots: Optional[list] = None
    ) -> str:
        """AI에게 전달할 프롬프트 구성"""

        # 시간대 한글 변환
        time_slot_map = {
            'morning': '오전 (09:00~12:00)',
            'afternoon': '오후 (12:00~18:00)',
            'evening': '저녁 (18:00~22:00)',
            'night': '야간 (22:00~09:00)'
        }
        time_slots_kr = [time_slot_map.get(slot, slot) for slot in (preferred_time_slots or [])]

        prompt = f"""
다음 환자와 간병인 정보를 기반으로 {days}일간의 상세한 케어 플랜을 생성하세요.

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
- 선호 시간대: {', '.join(time_slots_kr) if time_slots_kr else '전체 시간'}
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
    ...{days}일 모두 작성 (월요일부터 시작)...
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
1. **중요**: 선호 시간대({', '.join(time_slots_kr) if time_slots_kr else '전체 시간'})에 집중하여 일정 생성
   - 오전: 09:00~12:00
   - 오후: 12:00~18:00
   - 저녁: 18:00~22:00
   - 야간: 22:00~09:00
2. 식사, 약 복용, 활동, 휴식 등을 균형있게 배치
3. 간병인과 가족 모두가 참여할 수 있도록 배치
4. 환자의 성격 점수와 건강상태를 반영
5. 현실적이고 실행 가능한 일정
6. 반드시 유효한 JSON 형식으로만 응답

응답은 JSON만 포함하고 다른 텍스트는 포함하지 마세요.
"""
        return prompt

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """응답에서 JSON 추출 - 에러 처리 강화"""
        if not text or not isinstance(text, str):
            logger.error(f"❌ Invalid response text type: {type(text)}")
            raise ValueError("Response text is not a valid string")

        # JSON 블록 찾기
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx == -1 or end_idx <= start_idx:
            logger.error(f"❌ No JSON block found in response. Text: {text[:200]}")
            raise ValueError("No valid JSON block found in response")

        json_str = text[start_idx:end_idx]

        try:
            parsed = json.loads(json_str)
            logger.info("✅ JSON parsing successful")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {str(e)}")
            logger.error(f"❌ JSON string: {json_str[:300]}")
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def _generate_fallback_care_plan(
        self,
        patient_info: Dict[str, Any],
        caregiver_info: Dict[str, Any],
        preferred_time_slots: Optional[list] = None
    ) -> CarePlanResponse:
        """폴백: 환자 데이터 기반 7일 케어 플랜 생성"""

        patient_name = patient_info.get("name", "환자")
        caregiver_name = caregiver_info.get("name", "간병인")

        # 환자의 실제 약물 정보 가져오기
        medications = patient_info.get("medications", [])
        health_conditions = patient_info.get("health_conditions", [])

        # 약물 정보 문자열 생성
        if medications and len(medications) > 0:
            medication_note = f"⚠️ {', '.join(medications[:3])}"  # 최대 3개까지 표시
            if len(medications) > 3:
                medication_note += f" 외 {len(medications) - 3}개"
        else:
            medication_note = "⚠️ 처방된 약물 확인 필요"

        # 시간대별 활동 정의
        # morning: 09:00~12:00, afternoon: 12:00~18:00, evening: 18:00~22:00, night: 22:00~09:00
        morning_activities = [
            {"time": "09:00", "title": "가벼운 스트레칭", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "09:30", "title": "약 복용 확인", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}", "note": medication_note},
            {"time": "10:00", "title": "산책 (날씨 좋을 시)", "assignee": "👩 가족"},
            {"time": "11:00", "title": "독서 또는 가벼운 활동", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
        ]

        afternoon_activities = [
            {"time": "12:00", "title": "점심 식사 준비", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "13:00", "title": "점심 약 복용", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}", "note": medication_note},
            {"time": "14:00", "title": "낮잠 및 휴식", "assignee": "👨 환자"},
            {"time": "15:00", "title": "가벼운 체조", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "16:00", "title": "간식 시간", "assignee": "👩 가족"},
            {"time": "17:00", "title": "TV 시청 또는 대화", "assignee": "👩 가족"},
        ]

        evening_activities = [
            {"time": "18:00", "title": "저녁 식사 준비", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "19:00", "title": "저녁 약 복용", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}", "note": medication_note},
            {"time": "20:00", "title": "가족과 함께 시간", "assignee": "👩 가족"},
            {"time": "21:00", "title": "취침 준비", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
        ]

        night_activities = [
            {"time": "22:00", "title": "야간 체크 (1차)", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "02:00", "title": "야간 체크 (2차)", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "06:00", "title": "기상 준비", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "07:00", "title": "아침 식사 준비", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}"},
            {"time": "08:00", "title": "아침 약 복용", "assignee": f"👨‍⚕️ 간병인 {caregiver_name}", "note": medication_note},
        ]

        # 선호 시간대에 따라 활동 선택
        default_activities = []
        if not preferred_time_slots:
            preferred_time_slots = ['morning', 'afternoon']  # 기본값

        logger.info(f"📋 폴백 케어 플랜 시간대: {preferred_time_slots}")

        if 'morning' in preferred_time_slots:
            default_activities.extend(morning_activities)
        if 'afternoon' in preferred_time_slots:
            default_activities.extend(afternoon_activities)
        if 'evening' in preferred_time_slots:
            default_activities.extend(evening_activities)
        if 'night' in preferred_time_slots:
            default_activities.extend(night_activities)

        # 활동이 없으면 기본값 추가
        if not default_activities:
            default_activities = morning_activities + afternoon_activities

        # 질병에 따른 특별 활동 추가
        for condition in health_conditions:
            condition_lower = condition.lower() if condition else ""
            if "당뇨" in condition_lower or "diabetes" in condition_lower:
                if 'morning' in preferred_time_slots:
                    default_activities.append({
                        "time": "10:30",
                        "title": "혈당 체크",
                        "assignee": f"👨‍⚕️ 간병인 {caregiver_name}",
                        "note": "⚠️ 당뇨 관리"
                    })
            if "치매" in condition_lower or "dementia" in condition_lower:
                if 'afternoon' in preferred_time_slots:
                    default_activities.append({
                        "time": "14:30",
                        "title": "인지 활동 (퍼즐, 회상 치료)",
                        "assignee": f"👨‍⚕️ 간병인 {caregiver_name}",
                        "note": "⚠️ 인지 기능 유지"
                    })
            if "고혈압" in condition_lower or "hypertension" in condition_lower:
                if 'morning' in preferred_time_slots:
                    default_activities.append({
                        "time": "09:30",
                        "title": "혈압 측정",
                        "assignee": f"👨‍⚕️ 간병인 {caregiver_name}",
                        "note": "⚠️ 고혈압 모니터링"
                    })

        # 시간순 정렬
        default_activities.sort(key=lambda x: x["time"])

        logger.info(f"📋 Fallback care plan: medications={medications}, conditions={health_conditions}")

        # 7일 스케줄 생성
        days_of_week = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

        try:
            weekly_schedule = [
                DaySchedule(
                    day=day,
                    activities=[
                        ActivityItem(
                            time=act["time"],
                            title=act["title"],
                            assignee=act["assignee"],
                            note=act.get("note", "")
                        )
                        for act in default_activities
                    ]
                )
                for day in days_of_week
            ]
            logger.info(f"✅ Fallback care plan generated with {len(weekly_schedule)} days")
        except Exception as e:
            logger.error(f"❌ Error generating fallback schedule: {str(e)}")
            # 최소한의 폴백 데이터
            weekly_schedule = [
                DaySchedule(
                    day=days_of_week[0],
                    activities=[
                        ActivityItem(
                            time="07:00",
                            title="기상 도움",
                            assignee=f"👨‍⚕️ 간병인 {caregiver_name}"
                        )
                    ]
                )
            ]

        # 질병 기반 피드백 생성
        activity_reviews = [
            ActivityReview(
                activity_time="08:00",
                activity_title="약 복용 확인",
                feedback_type="adjustment",
                reason="order",
                suggestion="약 복용은 식사 후 30분 뒤에 하는 것이 더 좋습니다.",
                alternative_time="08:30"
            ),
            ActivityReview(
                activity_time="10:00",
                activity_title="산책 (날씨 좋을 시)",
                feedback_type="appropriate",
                reason="health",
                suggestion="규칙적인 산책은 혈액순환과 정신건강에 매우 도움이 됩니다."
            )
        ]

        # 질병별 추가 피드백
        for condition in health_conditions:
            condition_lower = condition.lower() if condition else ""
            if "당뇨" in condition_lower or "diabetes" in condition_lower:
                activity_reviews.append(ActivityReview(
                    activity_time="10:30",
                    activity_title="혈당 체크",
                    feedback_type="appropriate",
                    reason="health",
                    suggestion="식후 2시간 혈당 체크가 중요합니다. 정상 범위(140mg/dL 이하)를 유지하세요."
                ))
            if "치매" in condition_lower or "dementia" in condition_lower:
                activity_reviews.append(ActivityReview(
                    activity_time="14:30",
                    activity_title="인지 활동",
                    feedback_type="suggestion",
                    reason="cognitive",
                    suggestion="매일 같은 시간에 인지 활동을 하면 일상 루틴 형성에 도움이 됩니다."
                ))

        # 전체 코멘트 생성
        conditions_text = ", ".join(health_conditions) if health_conditions else "일반"
        overall_comment = f"{patient_name}님의 건강 상태({conditions_text})를 고려한 케어 플랜입니다. 환자의 컨디션에 따라 활동 강도를 조정해주세요."

        return CarePlanResponse(
            patient_name=patient_name,
            caregiver_name=caregiver_name,
            summary={
                "total_activities": len(default_activities) * 7,
                "participants": 4,
                "daily_hours": 14
            },
            weekly_schedule=weekly_schedule,
            caregiver_feedback=CaregiverFeedback(
                overall_comment=overall_comment,
                activity_reviews=activity_reviews
            )
        )
