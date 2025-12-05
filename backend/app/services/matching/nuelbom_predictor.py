# ========================================
# 늘봄케어 매칭 모델 - 예측 (추론)
# ========================================
# 파일: nuelbom_predictor.py
# 설명: 학습된 XGBoost 모델을 사용하여 간병인 추천

import os
from pathlib import Path
from typing import List, Dict, Optional
import logging
import json

import pandas as pd
import numpy as np
import joblib

from .data_preprocessing import DataPreprocessor
from .feature_engineering import FeatureEngineer
from .ai_comment import AICommentGenerator

logger = logging.getLogger(__name__)


class NuelbomMatchingPredictor:
    """늘봄케어 매칭 예측 클래스 (XGBoost 기반)"""

    # 싱글톤 인스턴스
    _instance: Optional['NuelbomMatchingPredictor'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        model_dir: str = None,
        data_dir: str = None,
        use_azure_openai: bool = True
    ):
        """
        Args:
            model_dir: 모델 저장 경로
            data_dir: 데이터 경로
            use_azure_openai: Azure OpenAI 사용 여부
        """
        # 이미 초기화된 경우 스킵
        if NuelbomMatchingPredictor._initialized:
            return

        # 기본 경로 설정 (matching 폴더 기준)
        base_dir = Path(__file__).parent.parent.parent.parent.parent  # backend/../
        matching_dir = base_dir / "matching"

        self.model_dir = Path(model_dir) if model_dir else matching_dir / "models"
        self.data_dir = Path(data_dir) if data_dir else matching_dir / "data"

        logger.info(f"모델 경로: {self.model_dir}")
        logger.info(f"데이터 경로: {self.data_dir}")

        # 모델 로드
        self.regressor = None
        self.classifier = None
        self.feature_columns = None

        # 데이터 로드
        self.preprocessor = None
        self.engineer = None
        self.caregivers = None
        self.patients = None

        # Azure OpenAI 코멘트 생성기
        self.ai_comment_generator = None
        self.use_azure_openai = use_azure_openai

        NuelbomMatchingPredictor._initialized = True

    def load_models(self, model_type: str = "xgboost"):
        """
        학습된 모델 로드

        Args:
            model_type: "xgboost" 또는 "randomforest"
        """
        logger.info(f"📦 모델 로드 중... ({model_type})")

        # 회귀 모델 로드
        reg_path = self.model_dir / f"{model_type}_regressor.pkl"
        if reg_path.exists():
            self.regressor = joblib.load(reg_path)
            logger.info(f"   ✅ 회귀 모델 로드: {reg_path}")
        else:
            raise FileNotFoundError(f"회귀 모델을 찾을 수 없습니다: {reg_path}")

        # 분류 모델 로드
        clf_path = self.model_dir / f"{model_type}_classifier.pkl"
        if clf_path.exists():
            self.classifier = joblib.load(clf_path)
            logger.info(f"   ✅ 분류 모델 로드: {clf_path}")

        # 특성 컬럼 로드
        feature_path = self.model_dir / "feature_columns.json"
        if feature_path.exists():
            with open(feature_path, "r", encoding="utf-8") as f:
                self.feature_columns = json.load(f)
            logger.info(f"   ✅ 특성 컬럼 로드: {len(self.feature_columns)}개")

        # Azure OpenAI 코멘트 생성기 초기화
        if self.use_azure_openai:
            self.ai_comment_generator = AICommentGenerator()
            if self.ai_comment_generator.is_available:
                logger.info("   ✅ Azure OpenAI 연결 성공")
            else:
                logger.info("   ⚠️ Azure OpenAI 미연결 - 규칙 기반 코멘트 사용")
        else:
            logger.info("   ⚠️ Azure OpenAI 비활성화 - 규칙 기반 코멘트 사용")

        logger.info("✅ 모델 로드 완료!")

    def load_data(self):
        """데이터 로드 및 전처리"""
        logger.info("📂 데이터 로드 중...")

        self.preprocessor = DataPreprocessor(data_dir=str(self.data_dir))
        self.preprocessor.load_all_data()

        self.caregivers = self.preprocessor.preprocess_caregivers()
        self.patients = self.preprocessor.preprocess_patients()

        self.engineer = FeatureEngineer()

        logger.info("✅ 데이터 로드 완료!")

    def initialize(self, model_type: str = "xgboost"):
        """전체 초기화 (모델 + 데이터)"""
        try:
            self.load_models(model_type=model_type)
            self.load_data()
            logger.info("✅ NuelbomMatchingPredictor 초기화 완료!")
            return True
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {e}")
            return False

    def filter_caregivers(
        self,
        patient_id: int,
        region_filter: bool = True,
        specialty_filter: bool = True
    ) -> List[int]:
        """
        1차 필터링: 조건에 맞는 간병인 후보 선정

        Args:
            patient_id: 환자 ID
            region_filter: 지역 필터 적용 여부
            specialty_filter: 전문분야 필터 적용 여부

        Returns:
            List[int]: 후보 간병인 ID 리스트
        """
        # 환자 정보 조회
        patient = self.patients[self.patients["patient_id"] == patient_id]
        if patient.empty:
            raise ValueError(f"환자 ID {patient_id}를 찾을 수 없습니다.")

        patient_row = patient.iloc[0]
        patient_region = patient_row.get("region_code", "")
        patient_diseases = patient_row.get("diseases_list", [])

        candidates = self.caregivers.copy()

        # 지역 필터
        if region_filter and patient_region:
            patient_city = patient_region.split("_")[0]
            capital_area = ["SEOUL", "GYEONGGI", "INCHEON"]

            def is_region_match(cg_region):
                if pd.isna(cg_region):
                    return False
                cg_city = cg_region.split("_")[0]
                # 같은 시/도 또는 수도권 내
                if cg_city == patient_city:
                    return True
                if patient_city in capital_area and cg_city in capital_area:
                    return True
                return False

            candidates = candidates[
                candidates["service_region"].apply(is_region_match)
            ]

        # 전문분야 필터
        if specialty_filter and patient_diseases:
            def has_specialty_match(specialties_list):
                if not isinstance(specialties_list, list):
                    return False
                return any(d in specialties_list for d in patient_diseases)

            candidates = candidates[
                candidates["specialties_list"].apply(has_specialty_match)
            ]

        return candidates["caregiver_id"].tolist()

    def get_grade(self, score: float) -> str:
        """점수 → 등급 변환"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        else:
            return "C"

    def generate_ai_comment(
        self,
        grade: str,
        features: Dict,
        caregiver_info: Dict,
        patient_info: Dict = None,
        matching_score: float = 0,
        verbose: bool = False
    ) -> Dict:
        """
        AI 코멘트 생성

        Args:
            grade: 매칭 등급
            features: 특성 값들
            caregiver_info: 간병인 정보
            patient_info: 환자 정보
            matching_score: 매칭 점수
            verbose: 디버깅 출력 여부

        Returns:
            Dict: {"comment": str, "source": str}
        """
        # Azure OpenAI 사용 가능하면 사용
        if (self.ai_comment_generator is not None and
            self.ai_comment_generator.is_available and
            patient_info is not None):
            result = self.ai_comment_generator.generate_comment(
                patient_info=patient_info,
                caregiver_info=caregiver_info,
                matching_score=matching_score,
                grade=grade,
                features=features,
                verbose=verbose
            )
            return result

        # 규칙 기반 코멘트 (fallback)
        return {
            "comment": self._generate_rule_based_comment(grade, features, caregiver_info),
            "source": "rule_based"
        }

    def _generate_rule_based_comment(
        self,
        grade: str,
        features: Dict,
        caregiver_info: Dict
    ) -> str:
        """규칙 기반 코멘트 생성"""
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
        avg_personality_diff = np.mean([
            features.get("personality_diff_empathy", 50),
            features.get("personality_diff_activity", 50),
            features.get("personality_diff_patience", 50),
            features.get("personality_diff_independence", 50)
        ])

        if avg_personality_diff <= 15:
            comments.append("성격 궁합이 매우 좋습니다.")
        elif avg_personality_diff <= 25:
            comments.append("원활한 소통이 기대됩니다.")

        # 등급별 기본 코멘트
        grade_comments = {
            "A+": "모든 조건이 탁월하게 일치하는 최적의 매칭입니다.",
            "A": "전반적으로 우수한 매칭입니다.",
            "B+": "좋은 케어 서비스가 기대됩니다.",
            "B": "기본적인 케어 역량을 갖추고 있습니다.",
            "C": "추가 검토가 필요할 수 있습니다."
        }

        if not comments:
            comments.append(grade_comments.get(grade, ""))

        return " ".join(comments)

    def recommend_caregivers(
        self,
        patient_id: int,
        top_n: int = 5,
        region_filter: bool = True,
        specialty_filter: bool = True,
        verbose: bool = False
    ) -> List[Dict]:
        """
        환자에게 간병인 추천

        Args:
            patient_id: 환자 ID
            top_n: 추천할 간병인 수
            region_filter: 지역 필터 적용
            specialty_filter: 전문분야 필터 적용
            verbose: 디버깅 출력 여부

        Returns:
            List[Dict]: 추천 간병인 목록
        """
        if self.regressor is None:
            raise ValueError("모델이 로드되지 않았습니다. initialize()를 먼저 호출하세요.")

        if self.caregivers is None:
            raise ValueError("데이터가 로드되지 않았습니다. initialize()를 먼저 호출하세요.")

        logger.info(f"🔍 환자 ID {patient_id}에 대한 간병인 추천 시작...")

        # 1. 후보 간병인 필터링
        candidate_ids = self.filter_caregivers(
            patient_id, region_filter, specialty_filter
        )
        logger.info(f"   - 1차 필터링 후 후보: {len(candidate_ids)}명")

        if not candidate_ids:
            logger.warning("   ⚠️ 조건에 맞는 간병인이 없습니다.")
            return []

        # 2. 특성 생성
        X = self.engineer.create_features_for_prediction(
            patient_id=patient_id,
            caregiver_ids=candidate_ids,
            patients=self.patients,
            caregivers=self.caregivers
        )

        caregiver_ids = X["caregiver_id"].tolist()
        X_features = X[self.feature_columns]

        # 3. 점수 예측
        predicted_scores = self.regressor.predict(X_features)

        # 4. 성공 확률 예측 (분류 모델이 있는 경우)
        success_probs = None
        if self.classifier is not None:
            success_probs = self.classifier.predict_proba(X_features)[:, 1]

        # 5. 결과 정리
        results = []
        caregivers_dict = self.caregivers.set_index("caregiver_id").to_dict("index")
        patients_dict = self.patients.set_index("patient_id").to_dict("index")

        # 환자 정보 조회
        patient_info = patients_dict.get(patient_id, {})

        for i, cg_id in enumerate(caregiver_ids):
            score = float(predicted_scores[i])
            grade = self.get_grade(score)

            cg_info = caregivers_dict.get(cg_id, {})
            features = X_features.iloc[i].to_dict()

            result = {
                "caregiver_id": cg_id,
                "name": cg_info.get("name", ""),
                "predicted_score": round(score, 1),
                "grade": grade,
                "experience_years": cg_info.get("experience_years", 0),
                "certifications": cg_info.get("certifications", ""),
                "specialties": cg_info.get("specialties", ""),
                "service_region": cg_info.get("service_region", ""),
                "hourly_rate": cg_info.get("hourly_rate", 0),
                "specialty_match_ratio": round(features.get("specialty_match_ratio", 0) * 100, 1),
                "region_match_score": features.get("region_match_score", 0),
                "_features": features,
                "_cg_info": cg_info,
            }

            if success_probs is not None:
                result["success_probability"] = round(float(success_probs[i]) * 100, 1)

            results.append(result)

        # 6. 점수순 정렬 및 상위 N개 선택
        results.sort(key=lambda x: x["predicted_score"], reverse=True)
        top_results = results[:top_n]

        # 7. 상위 N명에만 AI 코멘트 생성
        logger.info(f"   - 상위 {len(top_results)}명에 대해 AI 코멘트 생성 중...")

        for i, result in enumerate(top_results):
            features = result.pop("_features")
            cg_info = result.pop("_cg_info")

            comment_result = self.generate_ai_comment(
                grade=result["grade"],
                features=features,
                caregiver_info=cg_info,
                patient_info=patient_info,
                matching_score=result["predicted_score"],
                verbose=verbose
            )

            result["ai_comment"] = comment_result.get("comment", "")
            result["comment_source"] = comment_result.get("source", "unknown")

        # 결과 요약
        azure_count = sum(1 for r in top_results if r.get("comment_source") == "azure_openai")
        rule_count = sum(1 for r in top_results if r.get("comment_source") == "rule_based")
        logger.info(f"   - 코멘트 생성 완료: Azure OpenAI {azure_count}건, 규칙 기반 {rule_count}건")

        return top_results

    def recommend_caregivers_with_db_personality(
        self,
        patient_id: int,
        patient_personality: Dict[str, float],
        caregivers_with_personality: List[Dict],
        top_n: int = 5,
        verbose: bool = False
    ) -> List[Dict]:
        """
        DB에서 가져온 성격 데이터를 사용하여 간병인 추천
        (CSV 없이 DB 데이터만으로 추천)

        Args:
            patient_id: 환자 ID
            patient_personality: 환자 성격 점수 딕셔너리
            caregivers_with_personality: 간병인 정보 + 성격 점수 리스트
            top_n: 추천할 간병인 수
            verbose: 디버깅 출력 여부

        Returns:
            List[Dict]: 추천 간병인 목록
        """
        if self.regressor is None:
            raise ValueError("모델이 로드되지 않았습니다. initialize()를 먼저 호출하세요.")

        logger.info(f"🔍 환자 ID {patient_id}에 대한 DB 기반 간병인 추천...")
        logger.info(f"   - 후보 간병인: {len(caregivers_with_personality)}명")

        if not caregivers_with_personality:
            logger.warning("   ⚠️ 후보 간병인이 없습니다.")
            return []

        # Feature Engineering (DB 데이터 기반)
        engineer = FeatureEngineer()
        features_list = []
        caregiver_ids = []

        for cg_data in caregivers_with_personality:
            features = engineer.create_features_from_db_data(
                patient_personality=patient_personality,
                caregiver_data=cg_data
            )
            features_list.append(features)
            caregiver_ids.append(cg_data["caregiver_id"])

        # DataFrame 생성
        X = pd.DataFrame(features_list)
        X = X[self.feature_columns]

        # 점수 예측
        predicted_scores = self.regressor.predict(X)

        # 결과 정리
        results = []
        for i, cg_id in enumerate(caregiver_ids):
            score = float(predicted_scores[i])
            grade = self.get_grade(score)

            cg_data = caregivers_with_personality[i]
            features = X.iloc[i].to_dict()

            result = {
                "caregiver_id": cg_id,
                "caregiver_name": cg_data.get("caregiver_name", ""),
                "job_title": cg_data.get("job_title", ""),
                "predicted_score": round(score, 1),
                "grade": grade,
                "experience_years": cg_data.get("experience_years", 0),
                "hourly_rate": cg_data.get("hourly_rate", 0),
                "avg_rating": cg_data.get("avg_rating", 0),
                "profile_image_url": cg_data.get("profile_image_url", ""),
                "specialties": cg_data.get("specialties", []),
                "_features": features,
                "_cg_data": cg_data,
            }

            results.append(result)

        # 점수순 정렬 및 상위 N개 선택
        results.sort(key=lambda x: x["predicted_score"], reverse=True)
        top_results = results[:top_n]

        # AI 코멘트 생성
        for result in top_results:
            features = result.pop("_features")
            cg_data = result.pop("_cg_data")

            comment_result = self.generate_ai_comment(
                grade=result["grade"],
                features=features,
                caregiver_info=cg_data,
                patient_info={"patient_id": patient_id},
                matching_score=result["predicted_score"],
                verbose=verbose
            )

            result["ai_comment"] = comment_result.get("comment", "")
            result["comment_source"] = comment_result.get("source", "unknown")

        logger.info(f"   ✅ 추천 완료: {len(top_results)}명")
        return top_results

    def get_status(self) -> Dict:
        """현재 상태 반환"""
        status = {
            "model_loaded": self.regressor is not None,
            "classifier_loaded": self.classifier is not None,
            "data_loaded": self.caregivers is not None and self.patients is not None,
            "azure_openai_available": (
                self.ai_comment_generator is not None and
                self.ai_comment_generator.is_available
            ),
        }

        if self.caregivers is not None:
            status["caregivers_count"] = len(self.caregivers)
        if self.patients is not None:
            status["patients_count"] = len(self.patients)

        return status

    @classmethod
    def reset_instance(cls):
        """싱글톤 인스턴스 초기화 (테스트용)"""
        cls._instance = None
        cls._initialized = False


# 전역 인스턴스 (lazy initialization)
_predictor: Optional[NuelbomMatchingPredictor] = None


def get_nuelbom_predictor() -> NuelbomMatchingPredictor:
    """NuelbomMatchingPredictor 싱글톤 인스턴스 반환"""
    global _predictor

    if _predictor is None:
        _predictor = NuelbomMatchingPredictor()
        try:
            _predictor.initialize()
        except Exception as e:
            logger.error(f"NuelbomMatchingPredictor 초기화 실패: {e}")
            # 초기화 실패해도 인스턴스는 반환 (나중에 재시도 가능)

    return _predictor
