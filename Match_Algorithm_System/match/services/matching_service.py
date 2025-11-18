"""
Matching Service for BluedonuLab Caregiver Matching System
간병인 매칭 관련 비즈니스 로직
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import pandas as pd

from database.connection import DatabaseConnection
from database.schema import (
    Resident, Staff, PatientPersonality, CaregiverStyle,
    PersonalityBasedMatching, MatchingHistory
)
from models.matching_algorithm import MatchingAlgorithm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingService:
    """간병인 매칭 관련 비즈니스 로직"""

    @staticmethod
    def recommend_caregivers(
        patient_id: int,
        limit: int = 5,
        db: Optional[Session] = None
    ) -> Dict:
        """
        환자에게 추천할 간병인 목록 조회

        Args:
            patient_id: 환자 ID
            limit: 반환할 최대 간병인 수 (기본값: 5)
            db: 데이터베이스 세션

        Returns:
            추천 간병인 목록 및 매칭 정보

        Raises:
            ValueError: 환자나 성향 정보를 찾을 수 없는 경우
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 환자 확인
            resident = db.query(Resident).filter(
                Resident.resident_id == patient_id
            ).first()

            if not resident:
                raise ValueError(f"환자 ID {patient_id}를 찾을 수 없습니다.")

            # 환자 성향 확인
            patient_personality = db.query(PatientPersonality).filter(
                PatientPersonality.patient_id == patient_id
            ).first()

            if not patient_personality:
                raise ValueError(f"환자 {patient_id}의 성향 정보를 찾을 수 없습니다.")

            # 모든 간병인 스타일 조회
            caregiver_styles = db.query(CaregiverStyle).all()

            if not caregiver_styles:
                raise ValueError("등록된 간병인이 없습니다.")

            # 간병인 데이터를 DataFrame으로 변환
            caregiver_data = []
            for cs in caregiver_styles:
                caregiver = db.query(Staff).filter(
                    Staff.staff_id == cs.caregiver_id
                ).first()

                if caregiver:
                    caregiver_data.append({
                        'staff_id': cs.caregiver_id,
                        'job_title': caregiver.job_title,
                        'experience_years': caregiver.experience_years,
                        'empathy': cs.empathy,
                        'activity_support': cs.activity_support,
                        'patience': cs.patience,
                        'independence_support': cs.independence_support
                    })

            if not caregiver_data:
                raise ValueError("유효한 간병인 정보가 없습니다.")

            caregivers_df = pd.DataFrame(caregiver_data)

            # 매칭 알고리즘 실행
            recommendations = MatchingAlgorithm.recommend_caregivers(
                patient_id=patient_id,
                patient_care_level=resident.care_level,
                patient_personality={
                    'empathy': patient_personality.empathy,
                    'activity': patient_personality.activity,
                    'patience': patient_personality.patience,
                    'independence': patient_personality.independence
                },
                caregivers_df=caregivers_df,
                top_n=limit
            )

            # 간병인 정보 보강
            recommendations_with_info = []
            for rec in recommendations:
                caregiver = db.query(Staff).filter(
                    Staff.staff_id == rec['caregiver_id']
                ).first()

                recommendations_with_info.append({
                    "caregiver_id": rec['caregiver_id'],
                    "caregiver_name": caregiver.name if caregiver else "Unknown",
                    "job_title": caregiver.job_title if caregiver else "Unknown",
                    "matching_score": rec['matching_score'],
                    "grade": rec['grade'],
                    "care_compatibility": rec['care_compatibility'],
                    "personality_compatibility": rec['personality_compatibility'],
                    "empathy_match": rec['empathy_match'],
                    "activity_match": rec['activity_match'],
                    "patience_match": rec['patience_match'],
                    "independence_match": rec['independence_match'],
                    "reason": rec['reason']
                })

            logger.info(f"✅ 환자 {patient_id}에 대해 {len(recommendations_with_info)}명의 간병인 추천 완료")

            return {
                "patient_id": patient_id,
                "patient_care_level": resident.care_level,
                "total_recommendations": len(recommendations_with_info),
                "recommendations": recommendations_with_info
            }

        except ValueError as e:
            logger.error(f"❌ 추천 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def create_matching(
        patient_id: int,
        caregiver_id: int,
        db: Optional[Session] = None
    ) -> Dict:
        """
        환자와 간병인 간의 매칭 생성

        Args:
            patient_id: 환자 ID
            caregiver_id: 간병인 ID
            db: 데이터베이스 세션

        Returns:
            생성된 매칭 정보

        Raises:
            ValueError: 환자나 간병인을 찾을 수 없거나 유효하지 않은 경우
            IntegrityError: 중복 매칭 또는 데이터베이스 오류
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 환자 확인
            resident = db.query(Resident).filter(
                Resident.resident_id == patient_id
            ).first()

            if not resident:
                raise ValueError(f"환자 ID {patient_id}를 찾을 수 없습니다.")

            # 간병인 확인
            caregiver = db.query(Staff).filter(
                Staff.staff_id == caregiver_id
            ).first()

            if not caregiver:
                raise ValueError(f"간병인 ID {caregiver_id}를 찾을 수 없습니다.")

            # 중복 매칭 확인 (활성 상태의 매칭)
            existing_matching = db.query(PersonalityBasedMatching).filter(
                PersonalityBasedMatching.patient_id == patient_id,
                PersonalityBasedMatching.caregiver_id == caregiver_id,
                PersonalityBasedMatching.status == "Active"
            ).first()

            if existing_matching:
                raise ValueError(f"이미 활성 상태의 매칭이 존재합니다 (Matching ID: {existing_matching.matching_id})")

            # 환자 성향 조회
            patient_personality = db.query(PatientPersonality).filter(
                PatientPersonality.patient_id == patient_id
            ).first()

            if not patient_personality:
                raise ValueError(f"환자 {patient_id}의 성향 정보가 없습니다.")

            # 간병인 스타일 조회
            caregiver_style = db.query(CaregiverStyle).filter(
                CaregiverStyle.caregiver_id == caregiver_id
            ).first()

            if not caregiver_style:
                raise ValueError(f"간병인 {caregiver_id}의 스타일 정보가 없습니다.")

            # 매칭 점수 계산
            caregivers_df = pd.DataFrame([{
                'staff_id': caregiver_id,
                'job_title': caregiver.job_title,
                'experience_years': caregiver.experience_years,
                'empathy': caregiver_style.empathy,
                'activity_support': caregiver_style.activity_support,
                'patience': caregiver_style.patience,
                'independence_support': caregiver_style.independence_support
            }])

            recommendations = MatchingAlgorithm.recommend_caregivers(
                patient_id=patient_id,
                patient_care_level=resident.care_level,
                patient_personality={
                    'empathy': patient_personality.empathy,
                    'activity': patient_personality.activity,
                    'patience': patient_personality.patience,
                    'independence': patient_personality.independence
                },
                caregivers_df=caregivers_df,
                top_n=1
            )

            if not recommendations:
                raise ValueError("매칭 점수 계산 실패")

            rec = recommendations[0]

            # 매칭 생성
            matching = PersonalityBasedMatching(
                patient_id=patient_id,
                caregiver_id=caregiver_id,
                matching_score=rec['matching_score'],
                grade=rec['grade'],
                care_compatibility=rec['care_compatibility'],
                personality_compatibility=rec['personality_compatibility'],
                empathy_match=rec['empathy_match'],
                activity_match=rec['activity_match'],
                patience_match=rec['patience_match'],
                independence_match=rec['independence_match'],
                matching_reason=rec['reason'],
                status="Active",
                started_at=datetime.utcnow()
            )

            db.add(matching)
            db.commit()

            # 매칭 이력 생성
            matching_history = MatchingHistory(
                matching_id=matching.matching_id,
                patient_id=patient_id,
                caregiver_id=caregiver_id,
                status="Active",
                status_reason="매칭 생성"
            )

            db.add(matching_history)
            db.commit()

            logger.info(f"✅ 환자 {patient_id}와 간병인 {caregiver_id}의 매칭 생성 완료 (점수: {rec['matching_score']:.1f})")

            return {
                "matching_id": matching.matching_id,
                "patient_id": patient_id,
                "caregiver_id": caregiver_id,
                "caregiver_name": caregiver.name,
                "matching_score": matching.matching_score,
                "grade": matching.grade,
                "status": matching.status,
                "started_at": matching.started_at.isoformat(),
                "reason": matching.matching_reason
            }

        except ValueError as e:
            logger.error(f"❌ 매칭 생성 실패: {e}")
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"❌ 데이터베이스 오류: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def get_matching_history(
        patient_id: int,
        db: Optional[Session] = None
    ) -> Dict:
        """
        환자의 매칭 이력 조회

        Args:
            patient_id: 환자 ID
            db: 데이터베이스 세션

        Returns:
            매칭 이력 정보

        Raises:
            ValueError: 환자를 찾을 수 없는 경우
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 환자 확인
            resident = db.query(Resident).filter(
                Resident.resident_id == patient_id
            ).first()

            if not resident:
                raise ValueError(f"환자 ID {patient_id}를 찾을 수 없습니다.")

            # 매칭 이력 조회
            matchings = db.query(PersonalityBasedMatching).filter(
                PersonalityBasedMatching.patient_id == patient_id
            ).order_by(PersonalityBasedMatching.created_at.desc()).all()

            matchings_list = []
            for matching in matchings:
                caregiver = db.query(Staff).filter(
                    Staff.staff_id == matching.caregiver_id
                ).first()

                matchings_list.append({
                    "matching_id": matching.matching_id,
                    "patient_id": patient_id,
                    "caregiver_id": matching.caregiver_id,
                    "caregiver_name": caregiver.name if caregiver else "Unknown",
                    "matching_score": matching.matching_score,
                    "grade": matching.grade,
                    "status": matching.status,
                    "started_at": matching.started_at.isoformat() if matching.started_at else None,
                    "ended_at": matching.ended_at.isoformat() if matching.ended_at else None,
                    "created_at": matching.created_at.isoformat() if matching.created_at else None
                })

            return {
                "patient_id": patient_id,
                "total_matchings": len(matchings_list),
                "matchings": matchings_list
            }

        except ValueError as e:
            logger.error(f"❌ 조회 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def cancel_matching(
        matching_id: int,
        reason: str = "사용자 요청",
        db: Optional[Session] = None
    ) -> Dict:
        """
        매칭 취소

        Args:
            matching_id: 매칭 ID
            reason: 취소 사유
            db: 데이터베이스 세션

        Returns:
            취소된 매칭 정보

        Raises:
            ValueError: 매칭을 찾을 수 없거나 이미 종료된 경우
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 매칭 확인
            matching = db.query(PersonalityBasedMatching).filter(
                PersonalityBasedMatching.matching_id == matching_id
            ).first()

            if not matching:
                raise ValueError(f"매칭 ID {matching_id}를 찾을 수 없습니다.")

            if matching.status in ["Cancelled", "Completed"]:
                raise ValueError(f"이미 종료된 매칭입니다 (상태: {matching.status})")

            # 매칭 상태 변경
            matching.status = "Cancelled"
            matching.ended_at = datetime.utcnow()
            matching.updated_at = datetime.utcnow()
            db.merge(matching)

            # 매칭 이력 기록
            matching_history = MatchingHistory(
                matching_id=matching_id,
                patient_id=matching.patient_id,
                caregiver_id=matching.caregiver_id,
                status="Cancelled",
                status_reason=reason
            )

            db.add(matching_history)
            db.commit()

            logger.info(f"✅ 매칭 {matching_id} 취소 완료 (사유: {reason})")

            return {
                "matching_id": matching_id,
                "status": matching.status,
                "ended_at": matching.ended_at.isoformat(),
                "reason": reason
            }

        except ValueError as e:
            logger.error(f"❌ 취소 실패: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def evaluate_matching_performance(
        start_date: date,
        end_date: date,
        db: Optional[Session] = None
    ) -> Dict:
        """
        기간별 매칭 성능 평가

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            db: 데이터베이스 세션

        Returns:
            매칭 성능 평가 정보
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 기간 내 매칭 조회
            matchings = db.query(PersonalityBasedMatching).filter(
                PersonalityBasedMatching.created_at >= start_date,
                PersonalityBasedMatching.created_at <= end_date
            ).all()

            if not matchings:
                return {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_matchings": 0,
                    "average_matching_score": 0.0,
                    "grade_distribution": {},
                    "status_distribution": {},
                    "performance_summary": "데이터 없음"
                }

            # 통계 계산
            total_matchings = len(matchings)
            avg_score = sum(m.matching_score for m in matchings) / total_matchings

            # 등급 분포
            grade_distribution = {}
            for m in matchings:
                grade_distribution[m.grade] = grade_distribution.get(m.grade, 0) + 1

            # 상태 분포
            status_distribution = {}
            for m in matchings:
                status_distribution[m.status] = status_distribution.get(m.status, 0) + 1

            # 성능 평가
            if avg_score >= 90:
                performance_summary = "✅ 매우 우수"
            elif avg_score >= 75:
                performance_summary = "✅ 우수"
            elif avg_score >= 65:
                performance_summary = "⚠️ 보통"
            else:
                performance_summary = "❌ 개선 필요"

            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_matchings": total_matchings,
                "average_matching_score": round(avg_score, 2),
                "grade_distribution": grade_distribution,
                "status_distribution": status_distribution,
                "performance_summary": performance_summary
            }

        except Exception as e:
            logger.error(f"❌ 성능 평가 실패: {e}")
            raise
        finally:
            db.close()
