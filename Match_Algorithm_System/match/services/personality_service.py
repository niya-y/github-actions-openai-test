"""
Personality Service for BluedonuLab Caregiver Matching System
환자 성향 관련 비즈니스 로직
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.connection import DatabaseConnection
from database.schema import Resident, PatientPersonality
from models.personality_calculator import PersonalityCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalityService:
    """성향 테스트 및 분석 서비스"""

    @staticmethod
    def save_personality_test(
        patient_id: int,
        test_answers: List[int],
        db: Optional[Session] = None
    ) -> Dict:
        """
        환자의 성향 테스트 결과 저장

        Args:
            patient_id: 환자 ID
            test_answers: 12개 질문에 대한 답변 (각 0-2 점수)
            db: 데이터베이스 세션 (기본값: 새 세션 생성)

        Returns:
            저장된 성향 정보 딕셔너리

        Raises:
            ValueError: 환자를 찾을 수 없거나 답변이 유효하지 않은 경우
            IntegrityError: 데이터베이스 저장 실패
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

            # 답변 유효성 검증
            if not test_answers or len(test_answers) != 12:
                raise ValueError("12개의 답변이 필요합니다.")

            if not all(isinstance(ans, int) and 0 <= ans <= 2 for ans in test_answers):
                raise ValueError("각 답변은 0, 1, 또는 2여야 합니다.")

            # 성향 계산
            personality_profile = PersonalityCalculator.calculate_patient_personality(
                test_answers
            )

            # 기존 성향 정보 확인
            existing_personality = db.query(PatientPersonality).filter(
                PatientPersonality.patient_id == patient_id
            ).first()

            if existing_personality:
                # 기존 데이터 업데이트
                existing_personality.empathy = personality_profile['empathy']
                existing_personality.activity = personality_profile['activity']
                existing_personality.patience = personality_profile['patience']
                existing_personality.independence = personality_profile['independence']
                existing_personality.personality_type = personality_profile['type']
                existing_personality.description = personality_profile['description']
                existing_personality.test_completed = True
                existing_personality.test_completed_at = datetime.utcnow()
                existing_personality.updated_at = datetime.utcnow()
                db.merge(existing_personality)
                logger.info(f"✅ 환자 {patient_id}의 성향 정보 업데이트 완료")
            else:
                # 새 데이터 생성
                patient_personality = PatientPersonality(
                    patient_id=patient_id,
                    empathy=personality_profile['empathy'],
                    activity=personality_profile['activity'],
                    patience=personality_profile['patience'],
                    independence=personality_profile['independence'],
                    personality_type=personality_profile['type'],
                    description=personality_profile['description'],
                    test_completed=True,
                    test_completed_at=datetime.utcnow()
                )
                db.add(patient_personality)
                logger.info(f"✅ 환자 {patient_id}의 성향 정보 생성 완료")

            db.commit()

            return {
                "patient_id": patient_id,
                "personality_type": personality_profile['type'],
                "empathy": personality_profile['empathy'],
                "activity": personality_profile['activity'],
                "patience": personality_profile['patience'],
                "independence": personality_profile['independence'],
                "description": personality_profile['description'],
                "test_completed_at": datetime.utcnow().isoformat()
            }

        except ValueError as e:
            logger.error(f"❌ 입력 검증 실패: {e}")
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"❌ 데이터베이스 저장 실패: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def get_patient_personality(
        patient_id: int,
        db: Optional[Session] = None
    ) -> Dict:
        """
        환자의 성향 정보 조회

        Args:
            patient_id: 환자 ID
            db: 데이터베이스 세션

        Returns:
            성향 정보 딕셔너리

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

            # 성향 정보 조회
            personality = db.query(PatientPersonality).filter(
                PatientPersonality.patient_id == patient_id
            ).first()

            if not personality:
                raise ValueError(f"환자 {patient_id}의 성향 정보를 찾을 수 없습니다.")

            return {
                "patient_id": patient_id,
                "resident_name": resident.name,
                "personality_type": personality.personality_type,
                "empathy": personality.empathy,
                "activity": personality.activity,
                "patience": personality.patience,
                "independence": personality.independence,
                "description": personality.description,
                "test_completed": personality.test_completed,
                "test_completed_at": personality.test_completed_at.isoformat() if personality.test_completed_at else None,
                "created_at": personality.created_at.isoformat() if personality.created_at else None,
                "updated_at": personality.updated_at.isoformat() if personality.updated_at else None
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
    def update_personality(
        patient_id: int,
        test_answers: List[int],
        db: Optional[Session] = None
    ) -> Dict:
        """
        환자의 성향 정보 업데이트 (재평가)

        Args:
            patient_id: 환자 ID
            test_answers: 새로운 12개 질문 답변
            db: 데이터베이스 세션

        Returns:
            업데이트된 성향 정보

        Raises:
            ValueError: 환자를 찾을 수 없거나 답변이 유효하지 않은 경우
        """
        return PersonalityService.save_personality_test(patient_id, test_answers, db)

    @staticmethod
    def list_all_personalities(
        db: Optional[Session] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        모든 환자의 성향 정보 목록 조회

        Args:
            db: 데이터베이스 세션
            limit: 반환할 최대 개수
            offset: 시작 위치

        Returns:
            성향 정보 목록 및 페이지 정보
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 총 개수 조회
            total_count = db.query(PatientPersonality).count()

            # 성향 정보 조회
            personalities = db.query(PatientPersonality).order_by(
                PatientPersonality.patient_id
            ).limit(limit).offset(offset).all()

            personalities_list = []
            for p in personalities:
                resident = db.query(Resident).filter(
                    Resident.resident_id == p.patient_id
                ).first()

                personalities_list.append({
                    "patient_id": p.patient_id,
                    "resident_name": resident.name if resident else "Unknown",
                    "personality_type": p.personality_type,
                    "empathy": p.empathy,
                    "activity": p.activity,
                    "patience": p.patience,
                    "independence": p.independence,
                    "test_completed": p.test_completed,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                })

            return {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "returned_count": len(personalities_list),
                "personalities": personalities_list
            }

        except Exception as e:
            logger.error(f"❌ 목록 조회 실패: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def get_personality_stats(db: Optional[Session] = None) -> Dict:
        """
        성향 통계 정보 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            성향 통계 딕셔너리
                - 평균 점수
                - 성향 타입별 분포
                - 테스트 완료율
                - 범위 정보
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            personalities = db.query(PatientPersonality).all()

            if not personalities:
                return {
                    "total_count": 0,
                    "test_completed_count": 0,
                    "completion_rate": 0.0,
                    "average_empathy": 0.0,
                    "average_activity": 0.0,
                    "average_patience": 0.0,
                    "average_independence": 0.0,
                    "personality_type_distribution": {},
                    "score_ranges": {}
                }

            # 기본 통계
            total_count = len(personalities)
            test_completed = sum(1 for p in personalities if p.test_completed)
            completion_rate = (test_completed / total_count * 100) if total_count > 0 else 0.0

            # 평균 점수
            avg_empathy = sum(p.empathy for p in personalities) / total_count if total_count > 0 else 0
            avg_activity = sum(p.activity for p in personalities) / total_count if total_count > 0 else 0
            avg_patience = sum(p.patience for p in personalities) / total_count if total_count > 0 else 0
            avg_independence = sum(p.independence for p in personalities) / total_count if total_count > 0 else 0

            # 성향 타입별 분포
            type_distribution = {}
            for p in personalities:
                if p.personality_type:
                    type_distribution[p.personality_type] = type_distribution.get(p.personality_type, 0) + 1

            # 범위 정보
            empathy_scores = [p.empathy for p in personalities if p.empathy is not None]
            activity_scores = [p.activity for p in personalities if p.activity is not None]
            patience_scores = [p.patience for p in personalities if p.patience is not None]
            independence_scores = [p.independence for p in personalities if p.independence is not None]

            score_ranges = {
                "empathy": {
                    "min": min(empathy_scores) if empathy_scores else 0,
                    "max": max(empathy_scores) if empathy_scores else 0,
                    "avg": avg_empathy
                },
                "activity": {
                    "min": min(activity_scores) if activity_scores else 0,
                    "max": max(activity_scores) if activity_scores else 0,
                    "avg": avg_activity
                },
                "patience": {
                    "min": min(patience_scores) if patience_scores else 0,
                    "max": max(patience_scores) if patience_scores else 0,
                    "avg": avg_patience
                },
                "independence": {
                    "min": min(independence_scores) if independence_scores else 0,
                    "max": max(independence_scores) if independence_scores else 0,
                    "avg": avg_independence
                }
            }

            return {
                "total_count": total_count,
                "test_completed_count": test_completed,
                "completion_rate": round(completion_rate, 2),
                "average_empathy": round(avg_empathy, 2),
                "average_activity": round(avg_activity, 2),
                "average_patience": round(avg_patience, 2),
                "average_independence": round(avg_independence, 2),
                "personality_type_distribution": type_distribution,
                "score_ranges": score_ranges
            }

        except Exception as e:
            logger.error(f"❌ 통계 조회 실패: {e}")
            raise
        finally:
            db.close()
