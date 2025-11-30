"""
Personality Test FastAPI router.
"""

import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from openai import AzureOpenAI

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import Patient, Guardian, Caregiver
from app.models.care_details import PatientPersonality, CaregiverPersonality
from app.schemas.personality import (
    PersonalityTestRequest,
    PatientPersonalityResponse,
    CaregiverPersonalityResponse
)

router = APIRouter(prefix="/personality", tags=["Personality"])

@router.post("/tests", status_code=status.HTTP_201_CREATED)
async def create_personality_test(
    request: PersonalityTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    성향 테스트 결과 저장 및 AI 분석

    1. 사용자 유형 확인 (guardian -> patient, caregiver -> caregiver)
    2. Azure OpenAI로 답변 분석하여 점수 추출
    3. DB에 저장 또는 업데이트
    """

    # 1. 대상 엔티티 확인
    target_entity = None
    personality_model = None
    entity_id_field = None

    if request.user_type == "guardian":
        # 보호자의 경우 연결된 환자를 찾음 (첫 번째 환자라고 가정하거나 로직 보완 필요)
        # 여기서는 보호자가 등록한 첫 번째 환자를 대상으로 함
        guardian = db.query(Guardian).filter(Guardian.user_id == current_user.user_id).first()
        if not guardian:
            raise HTTPException(status_code=404, detail="Guardian profile not found")

        target_entity = db.query(Patient).filter(Patient.guardian_id == guardian.guardian_id).first()
        if not target_entity:
            raise HTTPException(status_code=404, detail="Patient profile not found. Please register a patient first.")

        personality_model = PatientPersonality
        entity_id_field = "patient_id"

    elif request.user_type == "caregiver":
        target_entity = db.query(Caregiver).filter(Caregiver.user_id == current_user.user_id).first()
        if not target_entity:
            raise HTTPException(status_code=404, detail="Caregiver profile not found")

        personality_model = CaregiverPersonality
        entity_id_field = "caregiver_id"
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    # 2. 답변 점수 계산
    try:
        # 프론트엔드에서 전송된 답변은 q1, q2, ... 형태의 JSON 문자열
        combined_scores = {
            "empathy": 0,
            "activity": 0,
            "patience": 0,
            "independence": 0
        }

        question_count = 0

        # 각 답변의 점수 합산
        for question_id, score_json in request.answers.items():
            try:
                # score_json은 {"empathy": 5, "activity": 1, ...} 형태의 문자열
                if isinstance(score_json, str):
                    scores = json.loads(score_json)
                else:
                    scores = score_json

                combined_scores["empathy"] += scores.get("empathy", 0)
                combined_scores["activity"] += scores.get("activity", 0)
                combined_scores["patience"] += scores.get("patience", 0)
                combined_scores["independence"] += scores.get("independence", 0)
                question_count += 1
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parsing scores for {question_id}: {e}")
                continue

        # 점수 정규화 (0-100 범위)
        if question_count > 0:
            max_score = question_count * 5  # 각 차원당 최대값은 5
            normalized_scores = {
                "empathy_score": min(100, (combined_scores["empathy"] / max_score) * 100),
                "activity_score": min(100, (combined_scores["activity"] / max_score) * 100),
                "patience_score": min(100, (combined_scores["patience"] / max_score) * 100),
                "independence_score": min(100, (combined_scores["independence"] / max_score) * 100)
            }
        else:
            normalized_scores = {
                "empathy_score": 50.0,
                "activity_score": 50.0,
                "patience_score": 50.0,
                "independence_score": 50.0
            }

        # Azure OpenAI로 분석 및 추천 생성
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        prompt = f"""
당신은 간병인 성향 평가 전문가입니다. 다음은 사용자의 성향 검사 결과입니다.

성향 점수 (0-100 범위):
- 공감 능력 (Empathy): {normalized_scores['empathy_score']:.1f}
- 활동성 (Activity): {normalized_scores['activity_score']:.1f}
- 인내심 (Patience): {normalized_scores['patience_score']:.1f}
- 자립성 (Independence): {normalized_scores['independence_score']:.1f}

이 점수를 바탕으로 어떤 유형의 간병인이 이 사용자와 잘 맞을지 분석하고, 다음의 JSON 형식으로 응답하세요:

{{
    "analysis": "<한국어로 된 상세 성격 분석 (150자 이상)>",
    "recommendation": "<추천 간병인 유형 (예: 따뜻하고 꼼꼼한 간병인)>"
}}

분석 시 다음을 고려하세요:
1. 각 점수의 높고 낮음을 해석
2. 사용자의 강점과 약점을 균형있게 설명
3. 추천 간병인 유형은 사용자의 높은 점수 차원들을 반영하여 작성
        """

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert caregiver profiling AI."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result_content = response.choices[0].message.content
        result = json.loads(result_content)

        # 정규화된 점수를 결과에 추가
        result["empathy_score"] = normalized_scores["empathy_score"]
        result["activity_score"] = normalized_scores["activity_score"]
        result["patience_score"] = normalized_scores["patience_score"]
        result["independence_score"] = normalized_scores["independence_score"]

    except Exception as e:
        print(f"Score calculation/AI Analysis Error: {e}")
        # 실패 시 기본값 반환
        result = {
            "empathy_score": 50.0,
            "activity_score": 50.0,
            "patience_score": 50.0,
            "independence_score": 50.0,
            "analysis": "성향 분석 중 오류가 발생했습니다. 다시 시도해주세요.",
            "recommendation": "적절한 간병인"
        }

    # 3. DB에 저장 또는 업데이트
    # 해당 엔티티의 기존 성향 정보가 있는지 확인
    entity_id = getattr(target_entity, entity_id_field)

    personality_record = db.query(personality_model).filter(
        getattr(personality_model, entity_id_field) == entity_id
    ).first()

    if not personality_record:
        # 새로 생성
        personality_data = {
            entity_id_field: entity_id,
            "empathy_score": result.get('empathy_score', 50.0),
            "activity_score": result.get('activity_score', 50.0),
            "patience_score": result.get('patience_score', 50.0),
            "independence_score": result.get('independence_score', 50.0),
            # "raw_test_answers": request.answers, # 모델에 필드가 있다면 추가
            # "ai_analysis_text": result.get('analysis', "") # 모델에 필드가 있다면 추가
        }

        # 모델에 해당 필드가 있는지 확인 후 추가 (안전하게)
        if hasattr(personality_model, 'raw_test_answers'):
            personality_data['raw_test_answers'] = request.answers
        if hasattr(personality_model, 'ai_analysis_text'):
            personality_data['ai_analysis_text'] = result.get('analysis', "")

        personality_record = personality_model(**personality_data)
        db.add(personality_record)
    else:
        # 업데이트
        personality_record.empathy_score = result.get('empathy_score', 50.0)
        personality_record.activity_score = result.get('activity_score', 50.0)
        personality_record.patience_score = result.get('patience_score', 50.0)
        personality_record.independence_score = result.get('independence_score', 50.0)

        if hasattr(personality_model, 'raw_test_answers'):
            personality_record.raw_test_answers = request.answers
        if hasattr(personality_model, 'ai_analysis_text'):
            personality_record.ai_analysis_text = result.get('analysis', "")

    db.commit()
    db.refresh(personality_record)

    # 응답 반환 (타입에 따라 다르게)
    if request.user_type == "guardian":
        return PatientPersonalityResponse.model_validate(personality_record)
    else:
        return CaregiverPersonalityResponse.model_validate(personality_record)
