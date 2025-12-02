"""
XGBoost 기반 AI 매칭 서비스 (V2)
새 알고리즘: 전문분야, 지역, 프로필 정보 포함

Features (10개):
1. personality_diff_empathy: |환자_공감도 - 간병인_공감도|
2. personality_diff_activity: |환자_활동성 - 간병인_활동성|
3. personality_diff_patience: |환자_인내심 - 간병인_인내심|
4. personality_diff_independence: |환자_자립성 - 간병인_자립성|
5. specialty_match_ratio: 전문분야 일치율 (0~1)
6. region_match_score: 지역 일치 점수 (0, 0.5, 0.75, 1.0)
7. caregiver_experience: 간병인 경력 (년)
8. caregiver_specialties_count: 간병인 전문분야 개수
9. patient_care_level: 환자 요양등급 (1~7)
10. patient_disease_count: 환자 질병 개수

성능: R² 0.916, RMSE 3.21, MAE 2.72
"""

import logging
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from xgboost import XGBRegressor
import warnings

from app.services.feature_engineering import FeatureEngineer

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XGBoostMatchingService:
    """XGBoost V2 기반 매칭 서비스 (전문분야, 지역, 프로필 포함)"""

    # 싱글톤 패턴: 모델을 메모리에 한 번만 로드
    _instance = None
    _model = None
    _feature_engineer = None
    _feature_columns = [
        'personality_diff_empathy',
        'personality_diff_activity',
        'personality_diff_patience',
        'personality_diff_independence',
        'specialty_match_ratio',
        'region_match_score',
        'caregiver_experience',
        'caregiver_specialties_count',
        'patient_care_level',
        'patient_disease_count'
    ]

    def __new__(cls):
        """싱글톤 인스턴스 생성"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        """XGBoost V2 모델 및 FeatureEngineer 로드"""
        try:
            # FeatureEngineer 초기화
            self._feature_engineer = FeatureEngineer()
            logger.info("✅ FeatureEngineer 초기화 완료")
            
            # 모델 경로 찾기 (V2 모델 사용)
            current_dir = Path(__file__).parent
            model_path = current_dir.parent.parent / "models" / "xgboost_v2.json"

            # 대체 경로들
            alternative_paths = [
                Path("/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/backend/models/xgboost_v2.json"),
                current_dir.parent.parent.parent / "Match_Algorithm_System" / "match_ML_v3" / "models" / "xgboost.json",  # 폴백
            ]

            model_file = None
            for path in [model_path] + alternative_paths:
                if path.exists():
                    model_file = path
                    logger.info(f"✅ XGBoost V2 모델 찾음: {path}")
                    break

            if not model_file:
                raise FileNotFoundError(
                    f"XGBoost V2 모델을 찾을 수 없습니다. 확인된 경로: {model_path}\n"
                    f"대체 경로: {alternative_paths}"
                )

            # 모델 로드
            self._model = XGBRegressor()
            self._model.load_model(str(model_file))
            logger.info(f"✅ XGBoost V2 모델 로드 완료: {model_file}")
            logger.info(f"   - 특성 개수: {len(self._feature_columns)}개")
            logger.info(f"   - 알고리즘: V2 (전문분야, 지역, 프로필 포함)")

        except Exception as e:
            logger.error(f"❌ 모델 로드 실패: {e}")
            raise

    @staticmethod
    def generate_features(
        patient_personality: Dict[str, float],
        caregiver_personality: Dict[str, float],
        patient_data: Optional[Dict] = None,
        caregiver_data: Optional[Dict] = None
    ) -> Dict[str, float]:
        """
        Patient와 Caregiver의 정보로 10개 feature 생성 (V2)
        
        Args:
            patient_personality: {
                "empathy_score": float (0-100),
                "activity_score": float (0-100),
                "patience_score": float (0-100),
                "independence_score": float (0-100)
            }
            caregiver_personality: {...same structure...}
            patient_data: {
                "diseases": List[str],  # 질병 리스트
                "region_code": str,     # 지역 코드
                "care_level": str       # 요양등급
            }
            caregiver_data: {
                "specialties": List[str],  # 전문분야 리스트
                "service_region": str,     # 서비스 지역
                "experience_years": int    # 경력
            }
            
        Returns:
            10개 feature의 dictionary
            
        Example:
            >>> patient_pers = {"empathy_score": 75, "activity_score": 55, ...}
            >>> caregiver_pers = {"empathy_score": 70, "activity_score": 60, ...}
            >>> patient_data = {"diseases": ["치매"], "region_code": "SEOUL_GANGNAM", "care_level": "3등급"}
            >>> caregiver_data = {"specialties": ["치매", "파킨슨"], "service_region": "SEOUL_GANGNAM", "experience_years": 5}
            >>> features = XGBoostMatchingService.generate_features(patient_pers, caregiver_pers, patient_data, caregiver_data)
        """
        # FeatureEngineer 인스턴스 생성
        engineer = FeatureEngineer()
        
        # 데이터 준비
        patient_full_data = {
            "personality": patient_personality,
            "diseases": patient_data.get("diseases", []) if patient_data else [],
            "region_code": patient_data.get("region_code", "") if patient_data else "",
            "care_level": patient_data.get("care_level", "3등급") if patient_data else "3등급"
        }
        
        caregiver_full_data = {
            "personality": caregiver_personality,
            "specialties": caregiver_data.get("specialties", []) if caregiver_data else [],
            "service_region": caregiver_data.get("service_region", "") if caregiver_data else "",
            "experience_years": caregiver_data.get("experience_years", 0) if caregiver_data else 0
        }
        
        # 특성 생성
        features = engineer.create_features_for_pair(patient_full_data, caregiver_full_data)
        
        return features

    def predict_compatibility(
        self,
        patient_personality: Dict[str, float],
        caregiver_personality: Dict[str, float],
        patient_data: Optional[Dict] = None,
        caregiver_data: Optional[Dict] = None
    ) -> float:
        """
        XGBoost V2 모델로 호환도 점수 예측

        Args:
            patient_personality: 환자 성격 정보
            caregiver_personality: 간병인 성격 정보
            patient_data: 환자 추가 정보 (질병, 지역, 요양등급)
            caregiver_data: 간병인 추가 정보 (전문분야, 지역, 경력)

        Returns:
            호환도 점수 (0-100)

        Example:
            >>> service = XGBoostMatchingService()
            >>> patient_pers = {"empathy_score": 75, ...}
            >>> caregiver_pers = {"empathy_score": 70, ...}
            >>> patient_data = {"diseases": ["치매"], "region_code": "SEOUL_GANGNAM", "care_level": "3등급"}
            >>> caregiver_data = {"specialties": ["치매"], "service_region": "SEOUL_GANGNAM", "experience_years": 5}
            >>> score = service.predict_compatibility(patient_pers, caregiver_pers, patient_data, caregiver_data)
            >>> print(f"호환도: {score:.1f}/100")  # 호환도: 85.3/100
        """
        if self._model is None:
            raise RuntimeError("XGBoost V2 모델이 로드되지 않았습니다.")

        try:
            # Feature 생성
            features = self.generate_features(
                patient_personality, 
                caregiver_personality,
                patient_data,
                caregiver_data
            )

            # Feature 벡터 생성 (순서 중요! - V2 특성 순서)
            feature_vector = np.array([[
                features['personality_diff_empathy'],
                features['personality_diff_activity'],
                features['personality_diff_patience'],
                features['personality_diff_independence'],
                features['specialty_match_ratio'],
                features['region_match_score'],
                features['caregiver_experience'],
                features['caregiver_specialties_count'],
                features['patient_care_level'],
                features['patient_disease_count'],
            ]])

            # 예측
            prediction = self._model.predict(feature_vector)[0]

            # 점수 범위 확인 (0-100)
            score = max(0, min(100, float(prediction)))

            return score

        except Exception as e:
            logger.error(f"❌ 예측 실패: {e}")
            raise

    @staticmethod
    def get_grade_from_score(score: float) -> str:
        """
        호환도 점수로부터 등급 판정

        Args:
            score: 호환도 점수 (0-100)

        Returns:
            등급 문자열 ("A", "B", "C")

        점수 범위:
        - A등급: 70점 이상 (강력 추천)
        - B등급: 50-69점 (추천)
        - C등급: 50점 미만 (고려)
        """
        if score >= 70:
            return "A"
        elif score >= 50:
            return "B"
        else:
            return "C"

    @staticmethod
    def get_analysis_from_features(features: Dict[str, float]) -> str:
        """
        Feature 정보로부터 분석 메시지 생성 (V2)

        Args:
            features: generate_features()의 반환값

        Returns:
            분석 메시지 문자열
        """
        empathy_diff = features.get('personality_diff_empathy', 0)
        patience_diff = features.get('personality_diff_patience', 0)
        activity_diff = features.get('personality_diff_activity', 0)
        independence_diff = features.get('personality_diff_independence', 0)
        
        specialty_match = features.get('specialty_match_ratio', 0)
        region_score = features.get('region_match_score', 0)
        experience = features.get('caregiver_experience', 0)

        messages = []

        # 성향 분석
        avg_diff = (empathy_diff + patience_diff + activity_diff + independence_diff) / 4

        # 공감 능력 분석
        if empathy_diff < 15:
            messages.append("공감 능력이 잘 맞습니다")
        elif empathy_diff < 30:
            messages.append("공감 능력에서 약간의 차이가 있습니다")
        else:
            messages.append("공감 능력에서 차이가 있습니다")

        # 인내심 분석
        if patience_diff < 15:
            messages.append("인내심 수준이 유사합니다")
        elif patience_diff < 30:
            messages.append("인내심에서 약간의 차이가 있습니다")

        # 전문분야 일치
        if specialty_match >= 0.7:
            messages.append("전문분야가 잘 맞습니다")
        elif specialty_match >= 0.3:
            messages.append("일부 전문분야가 일치합니다")

        # 지역 일치
        if region_score >= 0.75:
            messages.append("지역이 가깝습니다")
        elif region_score >= 0.5:
            messages.append("같은 권역입니다")

        # 경력
        if experience >= 5:
            messages.append("풍부한 경력을 보유하고 있습니다")

        # 전체 호환도
        if avg_diff < 12:
            messages.append("전반적으로 성향이 잘 맞습니다")
        elif avg_diff < 20:
            messages.append("전반적으로 무난한 조합입니다")
        else:
            messages.append("성향 조정이 필요할 수 있습니다")

        return " | ".join(messages) if messages else "매칭 분석 완료"

    def batch_predict(
        self,
        patient_personality: Dict[str, float],
        caregivers: List[Dict],
        patient_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        여러 간병인에 대한 일괄 예측 (V2)

        Args:
            patient_personality: 환자 성격 정보
            caregivers: 간병인 정보 리스트
                [
                    {
                        "caregiver_id": 1, 
                        "personality": {...},
                        "specialties": [...],  # 선택
                        "service_region": "...",  # 선택
                        "experience_years": 5  # 선택
                    },
                    ...
                ]
            patient_data: 환자 추가 정보 (질병, 지역, 요양등급)

        Returns:
            예측 결과 리스트
                [
                    {
                        "caregiver_id": 1,
                        "score": 85.3,
                        "grade": "A",
                        "analysis": "공감 능력이 잘 맞습니다 | 전문분야가 잘 맞습니다 | ..."
                    },
                    ...
                ]
        """
        results = []

        for caregiver_info in caregivers:
            caregiver_id = caregiver_info.get('caregiver_id')
            caregiver_personality = caregiver_info.get('personality', {})
            
            # 간병인 추가 데이터
            caregiver_data = {
                "specialties": caregiver_info.get('specialties', []),
                "service_region": caregiver_info.get('service_region', ''),
                "experience_years": caregiver_info.get('experience_years', 0)
            }

            try:
                # 호환도 예측
                score = self.predict_compatibility(
                    patient_personality,
                    caregiver_personality,
                    patient_data,
                    caregiver_data
                )

                # Feature 정보 (분석용)
                features = self.generate_features(
                    patient_personality,
                    caregiver_personality,
                    patient_data,
                    caregiver_data
                )

                # 등급 판정
                grade = self.get_grade_from_score(score)

                # 분석 메시지
                analysis = self.get_analysis_from_features(features)

                results.append({
                    "caregiver_id": caregiver_id,
                    "score": round(score, 1),
                    "grade": grade,
                    "analysis": analysis,
                    "features": features  # 디버깅용
                })

            except Exception as e:
                logger.error(f"❌ 간병인 {caregiver_id} 예측 실패: {e}")
                results.append({
                    "caregiver_id": caregiver_id,
                    "score": 0,
                    "grade": "C",
                    "analysis": "예측 실패",
                    "error": str(e)
                })

        return results


# 글로벌 서비스 인스턴스 - Lazy로드로 변경 (startup 오류 방지)
# xgboost_matching_service = XGBoostMatchingService()
xgboost_matching_service = None  # On-demand initialization
