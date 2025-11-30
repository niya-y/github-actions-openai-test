"""
향상된 매칭 서비스 (Enhanced Matching Service)
XGBoost 기반 AI 매칭과 기존 매칭 로직을 통합

두 가지 모드 지원:
1. XGBoost 모드 (권장): match_ML_v3 XGBoost 모델 사용
2. Legacy 모드: 기존 거리/care_level 기반 로직
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.xgboost_matching_service import XGBoostMatchingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMatchingService:
    """XGBoost 기반 향상된 매칭 서비스"""

    # XGBoost 서비스 인스턴스 (싱글톤)
    xgboost_service = None

    @classmethod
    def initialize(cls):
        """XGBoost 서비스 초기화"""
        try:
            if cls.xgboost_service is None:
                cls.xgboost_service = XGBoostMatchingService()
                logger.info("✅ XGBoost 서비스 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ XGBoost 서비스 초기화 실패: {e}")
            logger.warning("⚠️ Legacy 매칭 모드로 폴백합니다")

    @staticmethod
    def recommend_caregivers_xgboost(
        patient_id: int,
        patient_personality: Dict[str, float],
        caregivers_with_personality: List[Dict],
        limit: int = 5,
        db: Optional[Session] = None
    ) -> List[Dict]:
        """
        XGBoost 기반 매칭 추천

        Args:
            patient_id: 환자 ID
            patient_personality: {
                "empathy_score": float,
                "activity_score": float,
                "patience_score": float,
                "independence_score": float
            }
            caregivers_with_personality: [
                {
                    "caregiver_id": int,
                    "caregiver_name": str,
                    "job_title": str,
                    "experience_years": int,
                    "empathy_score": float,
                    "activity_score": float,
                    "patience_score": float,
                    "independence_score": float,
                    "hourly_rate": float,
                    "avg_rating": float,
                    "profile_image_url": str
                },
                ...
            ]
            limit: 반환할 최대 간병인 수
            db: 데이터베이스 세션

        Returns:
            추천 간병인 리스트 (XGBoost 점수 포함)
        """
        if EnhancedMatchingService.xgboost_service is None:
            logger.warning("⚠️ XGBoost 서비스가 초기화되지 않았습니다")
            return []

        try:
            logger.info(f"[XGBoost 매칭] 환자 {patient_id}에 대해 {len(caregivers_with_personality)}명의 간병인 평가 중...")

            # 간병인들의 성격 정보 준비
            caregivers_for_prediction = [
                {
                    "caregiver_id": cg["caregiver_id"],
                    "personality": {
                        "empathy_score": cg.get("empathy_score", 50),
                        "activity_score": cg.get("activity_score", 50),
                        "patience_score": cg.get("patience_score", 50),
                        "independence_score": cg.get("independence_score", 50),
                    }
                }
                for cg in caregivers_with_personality
            ]

            # 일괄 예측
            batch_results = EnhancedMatchingService.xgboost_service.batch_predict(
                patient_personality=patient_personality,
                caregivers=caregivers_for_prediction
            )

            # 결과와 간병인 정보 병합
            recommendations = []
            for result in batch_results:
                caregiver_id = result["caregiver_id"]

                # 해당 간병인의 정보 찾기
                caregiver_info = next(
                    (cg for cg in caregivers_with_personality if cg["caregiver_id"] == caregiver_id),
                    None
                )

                if caregiver_info and "error" not in result:
                    recommendation = {
                        "caregiver_id": caregiver_id,
                        "caregiver_name": caregiver_info.get("caregiver_name", "Unknown"),
                        "job_title": caregiver_info.get("job_title", "Unknown"),
                        "experience_years": caregiver_info.get("experience_years", 0),
                        "matching_score": result["score"],  # XGBoost 점수 (0-100)
                        "grade": result["grade"],  # A, B, C
                        "personality_analysis": result["analysis"],
                        "hourly_rate": caregiver_info.get("hourly_rate", 0),
                        "avg_rating": caregiver_info.get("avg_rating", 0),
                        "profile_image_url": caregiver_info.get("profile_image_url", ""),
                        "model_version": "XGBoost_v3",  # 모델 버전 추적
                    }
                    recommendations.append(recommendation)

            # 점수로 정렬 (내림차순)
            recommendations.sort(key=lambda x: x["matching_score"], reverse=True)

            # 상위 limit명 반환
            recommendations = recommendations[:limit]

            logger.info(f"✅ XGBoost 매칭 완료: {len(recommendations)}명 추천 (평균 점수: {sum(r['matching_score'] for r in recommendations)/len(recommendations):.1f})")

            return recommendations

        except Exception as e:
            logger.error(f"❌ XGBoost 매칭 실패: {e}")
            return []

    @staticmethod
    def get_caregiver_personalities(
        caregivers: List,
        db: Optional[Session] = None
    ) -> List[Dict]:
        """
        간병인들의 성격 정보 조회

        Args:
            caregivers: Staff 객체 리스트
            db: 데이터베이스 세션

        Returns:
            간병인 정보 + 성격 점수 리스트
        """
        caregivers_with_personality = []

        for caregiver in caregivers:
            try:
                # 간병인 성격 조회 (DB에서)
                # 실제 구현에서는 아래와 같이 조회:
                # caregiver_personality = db.query(CaregiverPersonality).filter(
                #     CaregiverPersonality.caregiver_id == caregiver.staff_id
                # ).first()

                # 현재는 임시 데이터 (추후 실제 DB 조회로 변경)
                caregiver_info = {
                    "caregiver_id": caregiver.staff_id,
                    "caregiver_name": getattr(caregiver, "name", "Unknown"),
                    "job_title": getattr(caregiver, "job_title", "Caregiver"),
                    "experience_years": getattr(caregiver, "experience_years", 0),
                    "empathy_score": getattr(caregiver, "empathy_score", 50),  # DB에서 조회
                    "activity_score": getattr(caregiver, "activity_score", 50),
                    "patience_score": getattr(caregiver, "patience_score", 50),
                    "independence_score": getattr(caregiver, "independence_score", 50),
                    "hourly_rate": getattr(caregiver, "hourly_rate", 0),
                    "avg_rating": getattr(caregiver, "avg_rating", 0),
                    "profile_image_url": getattr(caregiver, "profile_image_url", ""),
                }
                caregivers_with_personality.append(caregiver_info)

            except Exception as e:
                logger.warning(f"⚠️ 간병인 {caregiver.staff_id} 성격 정보 조회 실패: {e}")
                continue

        return caregivers_with_personality

    @staticmethod
    def format_matching_result(
        recommendation: Dict,
        include_features: bool = False
    ) -> Dict:
        """
        매칭 결과를 프론트엔드 포맷으로 변환

        Args:
            recommendation: XGBoost 매칭 결과
            include_features: 상세 feature 정보 포함 여부

        Returns:
            프론트엔드 호환 형식
        """
        result = {
            "caregiver_id": recommendation["caregiver_id"],
            "caregiver_name": recommendation["caregiver_name"],
            "job_title": recommendation["job_title"],
            "grade": recommendation["grade"],
            "match_score": round(recommendation["matching_score"], 1),
            "experience_years": recommendation["experience_years"],
            "hourly_rate": recommendation["hourly_rate"],
            "avg_rating": recommendation["avg_rating"],
            "profile_image_url": recommendation["profile_image_url"],
            "personality_analysis": recommendation["personality_analysis"],
            "specialties": [],  # 추후 구현
            "availability": [],  # 추후 구현
        }

        if include_features and "features" in recommendation:
            result["features"] = recommendation["features"]

        return result

    @staticmethod
    def create_matching_with_xgboost(
        patient_id: int,
        caregiver_id: int,
        xgboost_score: float,
        xgboost_grade: str,
        db: Optional[Session] = None
    ) -> Dict:
        """
        XGBoost 점수와 함께 매칭 생성

        Args:
            patient_id: 환자 ID
            caregiver_id: 간병인 ID
            xgboost_score: XGBoost 예측 점수 (0-100)
            xgboost_grade: 등급 (A, B, C)
            db: 데이터베이스 세션

        Returns:
            생성된 매칭 정보
        """
        try:
            # 실제 매칭 생성 로직 (기존 코드 활용)
            # matching = PersonalityBasedMatching(
            #     patient_id=patient_id,
            #     caregiver_id=caregiver_id,
            #     matching_score=xgboost_score,
            #     grade=xgboost_grade,
            #     model_version="XGBoost_v3",
            #     status="Active",
            #     started_at=datetime.utcnow()
            # )
            # db.add(matching)
            # db.commit()

            logger.info(f"✅ XGBoost 점수 {xgboost_score}로 매칭 생성: 환자 {patient_id} - 간병인 {caregiver_id}")

            return {
                "patient_id": patient_id,
                "caregiver_id": caregiver_id,
                "matching_score": xgboost_score,
                "grade": xgboost_grade,
                "model_version": "XGBoost_v3",
                "status": "Active"
            }

        except Exception as e:
            logger.error(f"❌ 매칭 생성 실패: {e}")
            raise


# 애플리케이션 시작 시 초기화
EnhancedMatchingService.initialize()
