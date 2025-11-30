"""
XGBoost 기반 AI 매칭 서비스
match_ML_v3의 XGBoost 모델을 사용한 고급 간병인 매칭

Features (13개):
1. empathy_diff: |환자_공감도 - 간병인_공감도|
2. patience_diff: |환자_인내심 - 간병인_인내심|
3. activity_diff: |환자_활동성 - 간병인_활동성|
4. independence_diff: |환자_자립성 - 간병인_자립성|
5. max_diff: 위 4개 차이의 최댓값
6. avg_diff: 위 4개 차이의 평균값
7. empathy_diff_sq: empathy_diff^2 (비선형성)
8. patience_diff_sq: patience_diff^2
9. empathy_patience_interaction: empathy_diff * patience_diff
10. resident_empathy: 환자 공감도 (절대값)
11. resident_patience: 환자 인내심 (절대값)
12. caregiver_empathy: 간병인 공감도 (절대값)
13. caregiver_patience: 간병인 인내심 (절대값)
"""

import logging
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from xgboost import XGBRegressor
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XGBoostMatchingService:
    """match_ML_v3 XGBoost 기반 매칭 서비스"""

    # 싱글톤 패턴: 모델을 메모리에 한 번만 로드
    _instance = None
    _model = None
    _feature_columns = [
        'empathy_diff', 'patience_diff', 'activity_diff', 'independence_diff',
        'max_diff', 'avg_diff',
        'empathy_diff_sq', 'patience_diff_sq',
        'empathy_patience_interaction',
        'resident_empathy', 'resident_patience',
        'caregiver_empathy', 'caregiver_patience'
    ]

    def __new__(cls):
        """싱글톤 인스턴스 생성"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        """XGBoost 모델 로드"""
        try:
            # 모델 경로 찾기 (현재 파일 기준 상대경로)
            current_dir = Path(__file__).parent
            model_path = current_dir.parent.parent.parent / "models" / "xgboost.json"

            # 대체 경로들
            alternative_paths = [
                Path("/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/Match_Algorithm_System/match_ML_v3/models/xgboost.json"),
                Path("../../../models/xgboost.json"),
                Path("./models/xgboost.json"),
            ]

            model_file = None
            for path in [model_path] + alternative_paths:
                if path.exists():
                    model_file = path
                    logger.info(f"✅ XGBoost 모델 찾음: {path}")
                    break

            if not model_file:
                raise FileNotFoundError(
                    f"XGBoost 모델을 찾을 수 없습니다. 확인된 경로: {model_path}\n"
                    f"대체 경로: {alternative_paths}"
                )

            # 모델 로드
            self._model = XGBRegressor()
            self._model.load_model(str(model_file))
            logger.info(f"✅ XGBoost 모델 로드 완료: {model_file}")

        except Exception as e:
            logger.error(f"❌ 모델 로드 실패: {e}")
            raise

    @staticmethod
    def generate_features(
        patient_personality: Dict[str, float],
        caregiver_personality: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Patient와 Caregiver의 성격 정보로 13개 feature 생성

        Args:
            patient_personality: {
                "empathy_score": float (0-100),
                "activity_score": float (0-100),
                "patience_score": float (0-100),
                "independence_score": float (0-100)
            }
            caregiver_personality: {...same structure...}

        Returns:
            13개 feature의 dictionary

        Example:
            >>> patient = {"empathy_score": 75, "activity_score": 55, ...}
            >>> caregiver = {"empathy_score": 70, "activity_score": 60, ...}
            >>> features = XGBoostMatchingService.generate_features(patient, caregiver)
            >>> print(features['empathy_diff'])  # 5.0
        """
        # 기본 차이값 계산 (절대값)
        empathy_diff = abs(
            patient_personality.get('empathy_score', 50) -
            caregiver_personality.get('empathy_score', 50)
        )
        patience_diff = abs(
            patient_personality.get('patience_score', 50) -
            caregiver_personality.get('patience_score', 50)
        )
        activity_diff = abs(
            patient_personality.get('activity_score', 50) -
            caregiver_personality.get('activity_score', 50)
        )
        independence_diff = abs(
            patient_personality.get('independence_score', 50) -
            caregiver_personality.get('independence_score', 50)
        )

        # 통계값
        all_diffs = [empathy_diff, patience_diff, activity_diff, independence_diff]
        max_diff = max(all_diffs) if all_diffs else 0
        avg_diff = np.mean(all_diffs) if all_diffs else 0

        # 제곱 항 (비선형성 포착)
        empathy_diff_sq = empathy_diff ** 2
        patience_diff_sq = patience_diff ** 2

        # 상호작용 항
        empathy_patience_interaction = empathy_diff * patience_diff

        # 절대 점수 (베이스라인)
        resident_empathy = patient_personality.get('empathy_score', 50)
        resident_patience = patient_personality.get('patience_score', 50)
        caregiver_empathy = caregiver_personality.get('empathy_score', 50)
        caregiver_patience = caregiver_personality.get('patience_score', 50)

        return {
            'empathy_diff': empathy_diff,
            'patience_diff': patience_diff,
            'activity_diff': activity_diff,
            'independence_diff': independence_diff,
            'max_diff': max_diff,
            'avg_diff': avg_diff,
            'empathy_diff_sq': empathy_diff_sq,
            'patience_diff_sq': patience_diff_sq,
            'empathy_patience_interaction': empathy_patience_interaction,
            'resident_empathy': resident_empathy,
            'resident_patience': resident_patience,
            'caregiver_empathy': caregiver_empathy,
            'caregiver_patience': caregiver_patience,
        }

    def predict_compatibility(
        self,
        patient_personality: Dict[str, float],
        caregiver_personality: Dict[str, float]
    ) -> float:
        """
        XGBoost 모델로 호환도 점수 예측

        Args:
            patient_personality: 환자 성격 정보
            caregiver_personality: 간병인 성격 정보

        Returns:
            호환도 점수 (0-100)

        Example:
            >>> service = XGBoostMatchingService()
            >>> patient = {"empathy_score": 75, ...}
            >>> caregiver = {"empathy_score": 70, ...}
            >>> score = service.predict_compatibility(patient, caregiver)
            >>> print(f"호환도: {score:.1f}/100")  # 호환도: 78.5/100
        """
        if self._model is None:
            raise RuntimeError("XGBoost 모델이 로드되지 않았습니다.")

        try:
            # Feature 생성
            features = self.generate_features(patient_personality, caregiver_personality)

            # Feature 벡터 생성 (순서 중요!)
            feature_vector = np.array([[
                features['empathy_diff'],
                features['patience_diff'],
                features['activity_diff'],
                features['independence_diff'],
                features['max_diff'],
                features['avg_diff'],
                features['empathy_diff_sq'],
                features['patience_diff_sq'],
                features['empathy_patience_interaction'],
                features['resident_empathy'],
                features['resident_patience'],
                features['caregiver_empathy'],
                features['caregiver_patience'],
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
        Feature 정보로부터 분석 메시지 생성

        Args:
            features: generate_features()의 반환값

        Returns:
            분석 메시지 문자열
        """
        empathy_diff = features['empathy_diff']
        patience_diff = features['patience_diff']
        activity_diff = features['activity_diff']
        independence_diff = features['independence_diff']
        avg_diff = features['avg_diff']

        messages = []

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
        else:
            messages.append("인내심 차이가 있습니다")

        # 활동성 분석
        if activity_diff < 15:
            messages.append("활동성 선호도가 일치합니다")

        # 전체 호환도
        if avg_diff < 12:
            messages.append("전반적으로 성향이 잘 맞습니다")
        elif avg_diff < 20:
            messages.append("전반적으로 무난한 조합입니다")
        else:
            messages.append("성향 조정이 필요할 수 있습니다")

        return " | ".join(messages)

    def batch_predict(
        self,
        patient_personality: Dict[str, float],
        caregivers: List[Dict[str, float]]
    ) -> List[Dict]:
        """
        여러 간병인에 대한 일괄 예측

        Args:
            patient_personality: 환자 성격 정보
            caregivers: 간병인 성격 정보 리스트
                [
                    {"caregiver_id": 1, "personality": {...}},
                    {"caregiver_id": 2, "personality": {...}},
                    ...
                ]

        Returns:
            예측 결과 리스트
                [
                    {
                        "caregiver_id": 1,
                        "score": 78.5,
                        "grade": "A",
                        "analysis": "공감 능력이 잘 맞습니다 | ..."
                    },
                    ...
                ]
        """
        results = []

        for caregiver_info in caregivers:
            caregiver_id = caregiver_info.get('caregiver_id')
            caregiver_personality = caregiver_info.get('personality', {})

            try:
                # 호환도 예측
                score = self.predict_compatibility(
                    patient_personality,
                    caregiver_personality
                )

                # Feature 정보 (분석용)
                features = self.generate_features(
                    patient_personality,
                    caregiver_personality
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
