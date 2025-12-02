# ========================================
# 늘봄케어 매칭 모델 - 특성 생성 (V2)
# ========================================
# 파일: backend/app/services/feature_engineering.py
# 설명: 환자-간병인 쌍에 대한 특성(Feature) 생성
# 버전: V2 (전문분야, 지역, 프로필 정보 포함)

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """특성 생성 클래스 (V2)"""
    
    def __init__(self):
        """특성 컬럼 목록 정의"""
        self.feature_columns = [
            # 성격 차이 (4개)
            "personality_diff_empathy",
            "personality_diff_activity", 
            "personality_diff_patience",
            "personality_diff_independence",
            # 전문분야 일치
            "specialty_match_ratio",
            # 지역 일치
            "region_match_score",
            # 간병인 정보
            "caregiver_experience",
            "caregiver_specialties_count",
            # 환자 정보
            "patient_care_level",
            "patient_disease_count",
        ]
        
    def calculate_personality_diff(
        self, 
        patient_personality: Dict[str, float], 
        caregiver_personality: Dict[str, float]
    ) -> Dict[str, float]:
        """
        성격 점수 차이 계산
        
        Args:
            patient_personality: 환자 성격 정보
            caregiver_personality: 간병인 성격 정보
            
        Returns:
            dict: 성격 차이 점수들
        """
        personality_types = ["empathy", "activity", "patience", "independence"]
        diffs = {}
        
        for ptype in personality_types:
            p_score = patient_personality.get(f"{ptype}_score", 50)
            c_score = caregiver_personality.get(f"{ptype}_score", 50)
            
            # 차이의 절대값 (0~100 범위)
            diff = abs(float(p_score) - float(c_score))
            diffs[f"personality_diff_{ptype}"] = diff
            
        return diffs
    
    def calculate_specialty_match(
        self,
        patient_diseases: List[str],
        caregiver_specialties: List[str]
    ) -> float:
        """
        전문분야 일치율 계산
        
        Args:
            patient_diseases: 환자 질병 리스트
            caregiver_specialties: 간병인 전문분야 리스트
            
        Returns:
            float: 일치율 (0~1)
        """
        if not patient_diseases or not caregiver_specialties:
            return 0.0
        
        # 환자 질병 중 간병인이 전문으로 하는 비율
        matched = sum(1 for d in patient_diseases if d in caregiver_specialties)
        return matched / len(patient_diseases)
    
    def calculate_region_score(
        self,
        patient_region: str,
        caregiver_region: str
    ) -> float:
        """
        지역 일치 점수 계산
        
        Args:
            patient_region: 환자 지역 코드
            caregiver_region: 간병인 지역 코드
            
        Returns:
            float: 지역 점수 (0, 0.5, 0.75, 1.0)
        """
        if not patient_region or not caregiver_region:
            return 0.5
        
        # 완전 일치
        if patient_region == caregiver_region:
            return 1.0
        
        # 같은 시/도
        p_city = patient_region.split("_")[0] if "_" in patient_region else patient_region
        c_city = caregiver_region.split("_")[0] if "_" in caregiver_region else caregiver_region
        
        if p_city == c_city:
            return 0.75
        
        # 수도권 내 (서울-경기-인천)
        capital_area = ["SEOUL", "GYEONGGI", "INCHEON"]
        if p_city in capital_area and c_city in capital_area:
            return 0.5
        
        # 그 외 (지역 불일치)
        return 0.0
    
    def create_features_for_pair(
        self,
        patient_data: Dict,
        caregiver_data: Dict
    ) -> Dict[str, float]:
        """
        환자-간병인 쌍에 대한 특성 생성
        
        Args:
            patient_data: 환자 데이터 딕셔너리
                {
                    "personality": {"empathy_score": 75, ...},
                    "diseases": ["치매", "고혈압"],
                    "region_code": "SEOUL_GANGNAM",
                    "care_level": 3
                }
            caregiver_data: 간병인 데이터 딕셔너리
                {
                    "personality": {"empathy_score": 70, ...},
                    "specialties": ["치매", "파킨슨"],
                    "service_region": "SEOUL_GANGNAM",
                    "experience_years": 5
                }
            
        Returns:
            dict: 생성된 특성들
        """
        features = {}
        
        # 1. 성격 차이 (4개)
        patient_personality = patient_data.get("personality", {})
        caregiver_personality = caregiver_data.get("personality", {})
        
        personality_diffs = self.calculate_personality_diff(
            patient_personality, 
            caregiver_personality
        )
        features.update(personality_diffs)
        
        # 2. 전문분야 일치율
        patient_diseases = patient_data.get("diseases", [])
        caregiver_specialties = caregiver_data.get("specialties", [])
        
        # 문자열인 경우 빈 리스트로 처리
        if isinstance(patient_diseases, str):
            patient_diseases = []
        if isinstance(caregiver_specialties, str):
            caregiver_specialties = []
            
        features["specialty_match_ratio"] = self.calculate_specialty_match(
            patient_diseases, caregiver_specialties
        )
        
        # 3. 지역 일치 점수
        features["region_match_score"] = self.calculate_region_score(
            patient_data.get("region_code", ""),
            caregiver_data.get("service_region", "")
        )
        
        # 4. 간병인 정보
        features["caregiver_experience"] = float(caregiver_data.get("experience_years", 0))
        
        # 전문분야 개수
        if isinstance(caregiver_specialties, list):
            features["caregiver_specialties_count"] = float(len(caregiver_specialties))
        else:
            features["caregiver_specialties_count"] = 0.0
        
        # 5. 환자 정보
        # 요양등급을 숫자로 변환 (1등급=1, 2등급=2, ..., 등급외=7)
        care_level = patient_data.get("care_level", "3등급")
        if isinstance(care_level, str):
            if "1등급" in care_level:
                care_level_num = 1
            elif "2등급" in care_level:
                care_level_num = 2
            elif "3등급" in care_level:
                care_level_num = 3
            elif "4등급" in care_level:
                care_level_num = 4
            elif "5등급" in care_level:
                care_level_num = 5
            elif "인지지원" in care_level:
                care_level_num = 6
            else:  # 등급외
                care_level_num = 7
        else:
            care_level_num = int(care_level) if care_level else 3
            
        features["patient_care_level"] = float(care_level_num)
        
        # 질병 개수
        if isinstance(patient_diseases, list):
            features["patient_disease_count"] = float(len(patient_diseases))
        else:
            features["patient_disease_count"] = 0.0
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """특성 컬럼 이름 반환"""
        return self.feature_columns.copy()
