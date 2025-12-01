"""
🍽️ 늘봄케어 AI 맞춤 식단 추천 시스템
==============================================
Azure OpenAI + 식약처 API 통합 버전
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from openai import AzureOpenAI

# ============================================
# 1. 설정
# ============================================

class MealRecommendationConfig:
    """시스템 설정"""
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_API_VERSION = "2024-08-01-preview"
    
    # 식약처 API (선택)
    MFDS_API_KEY = os.getenv("MFDS_API_KEY", "")
    
    # 데이터베이스 연결 (FastAPI에서 주입)
    DB_CONNECTION_STRING = os.getenv("DATABASE_URL")

# ============================================
# 2. 약물-음식 상호작용 데이터베이스
# ============================================

DRUG_FOOD_INTERACTIONS = {
    "와파린": {
        "avoid": ["시금치", "브로콜리", "케일", "양배추", "녹색 채소"],
        "reason": "비타민K가 많아 약효 감소",
        "recommend": ["생선", "닭고기", "두부"]
    },
    "아스피린": {
        "avoid": ["술", "커피", "매운 음식", "토마토"],
        "reason": "위장 자극 증가",
        "recommend": ["우유", "요거트", "바나나", "감자"]
    },
    "메트포르민": {
        "avoid": ["술", "고지방 음식", "탄산음료"],
        "reason": "저혈당 위험, 소화불량 유발",
        "recommend": ["통곡물", "채소", "저지방 단백질", "콩"]
    },
    "글리메피리드": {
        "avoid": ["술", "설탕", "백미"],
        "reason": "저혈당 위험 증가",
        "recommend": ["현미", "잡곡", "채소", "생선"]
    },
    "시타글립틴": {
        "avoid": ["술", "고지방 음식"],
        "reason": "췌장 부담 증가",
        "recommend": ["채소", "통곡물", "저지방 생선"]
    },
    "도네페질": {
        "avoid": ["술", "카페인 과다", "자극적인 음식"],
        "reason": "부작용(구토, 설사) 증가",
        "recommend": ["견과류", "등푸른생선", "블루베리", "시금치"]
    },
    "메만틴": {
        "avoid": ["술", "카페인 과다"],
        "reason": "중추신경계 부작용",
        "recommend": ["견과류", "등푸른생선", "블루베리"]
    },
    "갈란타민": {
        "avoid": ["술", "카페인"],
        "reason": "부작용 증가",
        "recommend": ["채소", "생선", "견과류"]
    },
    "레보도파": {
        "avoid": ["고단백 식품(고기 과다)", "철분 보충제", "비타민B6"],
        "reason": "약물 흡수 방해",
        "recommend": ["저단백 아침식사", "과일", "채소", "두부"]
    },
    "프라미펙솔": {
        "avoid": ["술", "고단백"],
        "reason": "약효 감소",
        "recommend": ["채소", "과일", "저지방 음식"]
    },
    "엔타카폰": {
        "avoid": ["고단백", "철분"],
        "reason": "약물 흡수 저해",
        "recommend": ["과일", "채소"]
    },
    "아토르바스타틴": {
        "avoid": ["자몽", "자몽주스", "술", "고지방 음식"],
        "reason": "약물 농도 증가로 근육통 부작용",
        "recommend": ["오트밀", "아몬드", "연어", "올리브유"]
    },
    "로사르탄": {
        "avoid": ["소금", "감초", "바나나(과다)"],
        "reason": "고칼륨혈증 위험",
        "recommend": ["저염식", "채소", "저지방 유제품"]
    },
    "발사르탄": {
        "avoid": ["소금", "감초"],
        "reason": "혈압 조절 방해",
        "recommend": ["저염식", "채소", "과일"]
    },
    "텔미사르탄": {
        "avoid": ["소금", "감초"],
        "reason": "혈압 조절 방해",
        "recommend": ["저염식", "채소"]
    },
    "아모디핀": {
        "avoid": ["자몽", "감초"],
        "reason": "약물 농도 증가",
        "recommend": ["저염식", "채소", "생선"]
    },
    "클로피도그렐": {
        "avoid": ["자몽", "은행", "마늘(과다)", "비타민E"],
        "reason": "출혈 위험 증가",
        "recommend": ["생선", "채소", "과일"]
    },
    "셀레콕시브": {
        "avoid": ["술", "매운 음식"],
        "reason": "위장 손상",
        "recommend": ["우유", "요거트", "부드러운 음식"]
    },
    "멜록시캄": {
        "avoid": ["술", "매운 음식"],
        "reason": "위장 자극",
        "recommend": ["우유", "두부", "찜 요리"]
    },
    "아세트아미노펜": {
        "avoid": ["술"],
        "reason": "간 손상 위험",
        "recommend": ["물", "과일"]
    },
    "알렌드로네이트": {
        "avoid": ["칼슘", "철분", "커피", "주스"],
        "reason": "약물 흡수 방해",
        "recommend": ["물만 섭취(공복)"]
    },
    "리세드로네이트": {
        "avoid": ["칼슘", "철분", "음식"],
        "reason": "약물 흡수 방해",
        "recommend": ["공복 섭취"]
    },
    "칼슘": {
        "avoid": ["시금치", "곡물", "철분제"],
        "reason": "흡수 방해",
        "recommend": ["우유", "요거트", "치즈", "멸치"]
    },
    "비타민D": {
        "avoid": [],
        "reason": "",
        "recommend": ["등푸른생선", "계란", "버섯"]
    },
    "오메프라졸": {
        "avoid": ["커피", "술", "매운 음식"],
        "reason": "위산 자극",
        "recommend": ["부드러운 음식", "찜 요리"]
    },
    "온단세트론": {
        "avoid": ["자극적인 음식"],
        "reason": "구토 유발",
        "recommend": ["담백한 음식", "미음", "죽"]
    },
}

# 질병별 추천 음식
DISEASE_RECOMMENDATIONS = {
    "당뇨": {
        "recommend": ["현미", "퀴노아", "통밀", "채소", "콩", "두부", "생선", "견과류"],
        "avoid": ["백미", "흰 빵", "설탕", "과자", "케이크", "탄산음료", "사탕"],
        "focus": "저혈당지수(GI) 식품, 식이섬유 풍부"
    },
    "고혈압": {
        "recommend": ["바나나", "감자", "시금치", "저지방 우유", "연어", "견과류", "토마토"],
        "avoid": ["소금", "절임류", "가공식품", "라면", "치즈", "햄", "베이컨"],
        "focus": "저나트륨(하루 2000mg 이하), 고칼륨 식단"
    },
    "치매": {
        "recommend": ["등푸른생선", "견과류", "블루베리", "올리브유", "녹차", "브로콜리"],
        "avoid": ["트랜스지방", "가공육", "설탕", "정제 탄수화물"],
        "focus": "오메가3, 항산화제 풍부"
    },
    "파킨슨": {
        "recommend": ["저단백 식사", "과일", "채소", "통곡물", "콩"],
        "avoid": ["고단백(과다 육류)", "철분 보충제"],
        "focus": "저단백 식사로 약물 흡수 개선"
    },
    "관절염": {
        "recommend": ["등푸른생선", "올리브유", "생강", "강황", "녹황색 채소"],
        "avoid": ["포화지방", "설탕", "정제 탄수화물"],
        "focus": "항염증 식품"
    },
    "골다공증": {
        "recommend": ["우유", "요거트", "치즈", "멸치", "두부", "브로콜리", "아몬드"],
        "avoid": ["카페인 과다", "술", "탄산음료", "고염식"],
        "focus": "칼슘(하루 1000-1200mg), 비타민D"
    },
    "뇌졸중": {
        "recommend": ["등푸른생선", "채소", "과일", "통곡물", "저지방"],
        "avoid": ["소금", "포화지방", "트랜스지방"],
        "focus": "저염, 저지방, 항산화"
    },
    "중풍": {
        "recommend": ["채소", "과일", "생선", "통곡물"],
        "avoid": ["소금", "기름진 음식"],
        "focus": "저염, 균형식"
    },
    "인지장애": {
        "recommend": ["등푸른생선", "견과류", "베리류", "녹차"],
        "avoid": ["가공식품", "설탕"],
        "focus": "뇌 건강 영양소"
    },
    "암": {
        "recommend": ["다양한 채소", "과일", "통곡물", "생선", "콩"],
        "avoid": ["가공육", "알코올", "탄 음식"],
        "focus": "항산화, 면역력 강화"
    }
}

# ============================================
# 3. 환자 데이터 분석
# ============================================

class PatientDietaryAnalyzer:
    """환자 식단 제약사항 분석"""
    
    @staticmethod
    def analyze_patient_constraints(
        patient_id: int,
        patient_data: Dict,
        health_conditions: List[str],
        medications: List[str],
        dietary_prefs: Dict
    ) -> Dict:
        """
        환자의 식단 제약 사항 종합 분석
        
        Args:
            patient_id: 환자 ID
            patient_data: 환자 기본 정보 (이름, 나이, 성별, 요양등급 등)
            health_conditions: 질병 리스트
            medications: 복용 약물 리스트
            dietary_prefs: 알레르기/제한 음식 dict
        
        Returns:
            종합 분석 결과 dict
        """
        
        # 약물 분석
        drug_avoid = []
        drug_recommend = []
        drug_reasons = []
        
        for drug in medications:
            drug = drug.strip()
            if drug in DRUG_FOOD_INTERACTIONS:
                interaction = DRUG_FOOD_INTERACTIONS[drug]
                drug_avoid.extend(interaction['avoid'])
                drug_recommend.extend(interaction['recommend'])
                drug_reasons.append({
                    "drug": drug,
                    "reason": interaction['reason']
                })
        
        # 질병 분석
        disease_recommend = []
        disease_avoid = []
        disease_focus = []
        
        for disease in health_conditions:
            if disease in DISEASE_RECOMMENDATIONS:
                rec = DISEASE_RECOMMENDATIONS[disease]
                disease_recommend.extend(rec['recommend'])
                disease_avoid.extend(rec['avoid'])
                disease_focus.append({
                    "disease": disease,
                    "focus": rec['focus']
                })
        
        return {
            "patient_id": patient_id,
            "patient_info": patient_data,
            "health_conditions": health_conditions,
            "medications": medications,
            
            # 절대 금지
            "allergy_foods": dietary_prefs.get('allergy_foods', []),
            
            # 제한
            "restriction_foods": dietary_prefs.get('restriction_foods', []),
            
            # 약물 관련
            "drug_avoid_foods": list(set(drug_avoid)),
            "drug_recommend_foods": list(set(drug_recommend)),
            "drug_interaction_reasons": drug_reasons,
            
            # 질병 관련
            "disease_avoid_foods": list(set(disease_avoid)),
            "disease_recommend_foods": list(set(disease_recommend)),
            "disease_focus_areas": disease_focus,
            
            # 전체 회피 음식 (중복 제거)
            "all_avoid_foods": list(set(
                dietary_prefs.get('allergy_foods', []) +
                dietary_prefs.get('restriction_foods', []) +
                drug_avoid +
                disease_avoid
            )),
            
            # 전체 추천 음식
            "all_recommend_foods": list(set(
                drug_recommend +
                disease_recommend
            ))
        }

# ============================================
# 4. Azure OpenAI 식단 생성
# ============================================

class AIMealGenerator:
    """Azure OpenAI 기반 식단 생성기"""
    
    def __init__(self, config: MealRecommendationConfig):
        self.config = config
        self.client = AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION
        )
    
    def generate_meal_plan(
        self,
        patient_constraints: Dict,
        meal_date: str,
        meal_type: str  # breakfast, lunch, dinner, snack
    ) -> Dict:
        """
        Azure OpenAI로 맞춤 식단 생성
        
        Returns:
            {
                "menu_name": str,
                "ingredients": List[str],
                "nutrition_info": Dict,
                "cooking_tips": str,
                "health_benefits": str
            }
        """
        
        prompt = self._create_prompt(patient_constraints, meal_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 한국의 전문 영양사이며 노인 영양 관리 전문가입니다. 제공된 제약사항을 절대 준수하며, 맛있고 건강한 한식 메뉴를 추천합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            meal_plan = json.loads(response.choices[0].message.content)
            
            # 결과 포맷팅
            return {
                "patient_id": patient_constraints['patient_id'],
                "meal_date": meal_date,
                "meal_type": meal_type,
                "menu_name": meal_plan.get('menu_name'),
                "ingredients": meal_plan.get('ingredients'),
                "nutrition_info": json.dumps(meal_plan.get('nutrition_info')),
                "cooking_tips": meal_plan.get('cooking_tips'),
                "health_benefits": meal_plan.get('health_benefits'),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Azure OpenAI 에러: {e}")
            return None
    
    def _create_prompt(self, constraints: Dict, meal_type: str) -> str:
        """AI 프롬프트 생성"""
        
        meal_type_korean = {
            "breakfast": "아침식사",
            "lunch": "점심식사",
            "dinner": "저녁식사",
            "snack": "간식"
        }.get(meal_type, meal_type)
        
        patient = constraints['patient_info']
        
        prompt = f"""
당신은 한국의 전문 영양사입니다. 아래 환자 정보를 바탕으로 {meal_type_korean} 메뉴를 추천해주세요.

## 환자 정보
- 이름: {patient['name']}
- 나이: {patient['age']}세
- 성별: {patient['gender']}
- 요양등급: {patient.get('care_level', '해당없음')}
- 질병: {', '.join(constraints['health_conditions'])}
- 복용 약물: {', '.join(constraints['medications'])}

## 🚫 절대 사용 금지 (알레르기 - 매우 중요!)
{', '.join(constraints['allergy_foods']) if constraints['allergy_foods'] else '없음'}

## ⚠️ 제한 식품
{', '.join(constraints['restriction_foods']) if constraints['restriction_foods'] else '없음'}

## 💊 약물 상호작용으로 피해야 할 음식
{', '.join(constraints['drug_avoid_foods'][:10]) if constraints['drug_avoid_foods'] else '없음'}

피해야 하는 이유:
"""
        
        # 약물 상호작용 이유 추가
        if constraints.get('drug_interaction_reasons'):
            for reason in constraints['drug_interaction_reasons'][:3]:
                prompt += f"- {reason['drug']}: {reason['reason']}\n"
        
        prompt += f"""

## 🏥 질병으로 인해 피해야 할 음식
{', '.join(constraints['disease_avoid_foods'][:10]) if constraints['disease_avoid_foods'] else '없음'}

## ✅ 적극 추천 식재료
### 약물 효과 증진:
{', '.join(constraints['drug_recommend_foods'][:8]) if constraints['drug_recommend_foods'] else '없음'}

### 질병 관리에 도움:
{', '.join(constraints['disease_recommend_foods'][:8]) if constraints['disease_recommend_foods'] else '없음'}

## 영양 포커스:
"""
        
        # 질병별 영양 포커스
        if constraints.get('disease_focus_areas'):
            for focus in constraints['disease_focus_areas'][:3]:
                prompt += f"- {focus['disease']}: {focus['focus']}\n"
        
        prompt += """

## 요구사항
1. 한국 가정식 기반 (밥, 국, 반찬 형식 또는 죽, 찜 등)
2. 고령자가 먹기 쉬운 부드러운 음식 (요양등급 고려)
3. 위의 제약조건을 철저히 준수 (특히 알레르기!)
4. 영양 균형 고려 (저염, 저당, 적정 칼로리)
5. 조리가 간단하고 소화가 잘 되는 메뉴

다음 JSON 형식으로 응답해주세요:
{
    "menu_name": "메뉴 이름 (예: 연두부 버섯전골)",
    "ingredients": ["재료1", "재료2", "재료3", ...],
    "nutrition_info": {
        "calories": 500,
        "protein_g": 20,
        "carbs_g": 60,
        "fat_g": 15,
        "sodium_mg": 800,
        "fiber_g": 5
    },
    "cooking_tips": "조리 시 주의사항과 팁",
    "health_benefits": "이 식단이 환자의 건강과 질병 관리에 도움이 되는 구체적인 이유"
}
"""
        
        return prompt

# ============================================
# 5. 메인 서비스 클래스
# ============================================

class MealRecommendationService:
    """전체 식단 추천 서비스"""
    
    def __init__(self, config: MealRecommendationConfig):
        self.config = config
        self.analyzer = PatientDietaryAnalyzer()
        self.generator = AIMealGenerator(config)
    
    def recommend_meal(
        self,
        patient_id: int,
        patient_data: Dict,
        health_conditions: List[str],
        medications: List[str],
        dietary_prefs: Dict,
        meal_date: str,
        meal_type: str
    ) -> Optional[Dict]:
        """
        환자 맞춤 식단 추천 (전체 프로세스)
        
        Returns:
            생성된 식단 정보 or None
        """
        
        # 1. 환자 제약사항 분석
        constraints = self.analyzer.analyze_patient_constraints(
            patient_id=patient_id,
            patient_data=patient_data,
            health_conditions=health_conditions,
            medications=medications,
            dietary_prefs=dietary_prefs
        )
        
        # 2. AI 식단 생성
        meal_plan = self.generator.generate_meal_plan(
            patient_constraints=constraints,
            meal_date=meal_date,
            meal_type=meal_type
        )
        
        return meal_plan

# ============================================
# 6. 테스트 및 사용 예시
# ============================================

def test_meal_recommendation():
    """테스트 함수"""
    
    # 설정 (실제로는 환경변수에서 가져옴)
    config = MealRecommendationConfig()
    config.AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
    config.AZURE_OPENAI_KEY = "your-api-key"
    config.AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
    
    # 서비스 초기화
    service = MealRecommendationService(config)
    
    # 테스트 환자 데이터
    patient_data = {
        "name": "김할머니",
        "age": 75,
        "gender": "Female",
        "care_level": "3등급"
    }
    
    health_conditions = ["당뇨", "고혈압", "관절염"]
    medications = ["메트포르민", "아모디핀", "셀레콕시브"]
    dietary_prefs = {
        "allergy_foods": ["땅콩", "새우"],
        "restriction_foods": ["밀가루", "설탕"]
    }
    
    # 식단 추천
    meal_plan = service.recommend_meal(
        patient_id=1,
        patient_data=patient_data,
        health_conditions=health_conditions,
        medications=medications,
        dietary_prefs=dietary_prefs,
        meal_date="2025-01-15",
        meal_type="lunch"
    )
    
    if meal_plan:
        print("✅ 식단 생성 성공!")
        print(json.dumps(meal_plan, indent=2, ensure_ascii=False))
    else:
        print("❌ 식단 생성 실패")

if __name__ == "__main__":
    test_meal_recommendation()
