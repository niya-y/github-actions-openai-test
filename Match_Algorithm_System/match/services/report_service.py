"""
Report Service for BluedonuLab Caregiver Matching System
리포트 생성 및 관리 비즈니스 로직
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import DatabaseConnection
from database.schema import (
    Resident, Staff, DailyReport, PersonalityBasedMatching,
    PatientPersonality, CaregiverStyle
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportService:
    """리포트 생성 및 분석 서비스"""

    @staticmethod
    def generate_daily_report(
        matching_id: int,
        report_date: Optional[date] = None,
        content: str = "",
        mood: str = "Neutral",
        activities: str = "",
        medications_taken: bool = True,
        notes: str = "",
        created_by: str = "System",
        db: Optional[Session] = None
    ) -> Dict:
        """
        일일 리포트 생성

        Args:
            matching_id: 매칭 ID
            report_date: 리포트 날짜 (기본값: 오늘)
            content: 리포트 내용
            mood: 환자 기분 (Happy, Neutral, Sad)
            activities: 활동 기록
            medications_taken: 약물 복용 여부
            notes: 추가 메모
            created_by: 작성자 (기본값: System)
            db: 데이터베이스 세션

        Returns:
            생성된 리포트 정보

        Raises:
            ValueError: 매칭을 찾을 수 없는 경우
        """
        if db is None:
            db = DatabaseConnection.get_session()

        if report_date is None:
            report_date = datetime.utcnow().date()

        try:
            # 매칭 확인
            matching = db.query(PersonalityBasedMatching).filter(
                PersonalityBasedMatching.matching_id == matching_id
            ).first()

            if not matching:
                raise ValueError(f"매칭 ID {matching_id}를 찾을 수 없습니다.")

            # 환자 정보 조회
            resident = db.query(Resident).filter(
                Resident.resident_id == matching.patient_id
            ).first()

            # 환자 성향 조회
            personality = db.query(PatientPersonality).filter(
                PatientPersonality.patient_id == matching.patient_id
            ).first()

            # 성향에 따른 맞춤 리포트 템플릿 생성
            report_template = ReportService._generate_report_template(
                personality,
                mood,
                activities,
                content
            )

            # 리포트 생성
            daily_report = DailyReport(
                matching_id=matching_id,
                patient_id=matching.patient_id,
                report_date=datetime.combine(report_date, datetime.min.time()),
                content=report_template,
                mood=mood,
                activities=activities,
                medications_taken=medications_taken,
                notes=notes,
                created_by=created_by
            )

            db.add(daily_report)
            db.commit()

            logger.info(f"✅ 매칭 {matching_id}의 일일 리포트 생성 완료 (날짜: {report_date})")

            return {
                "report_id": daily_report.report_id,
                "matching_id": matching_id,
                "patient_id": matching.patient_id,
                "patient_name": resident.name if resident else "Unknown",
                "report_date": report_date.isoformat(),
                "mood": mood,
                "medications_taken": medications_taken,
                "created_by": created_by,
                "created_at": daily_report.created_at.isoformat()
            }

        except ValueError as e:
            logger.error(f"❌ 리포트 생성 실패: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def generate_weekly_report(
        patient_id: int,
        week_start_date: Optional[date] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        주간 리포트 생성

        Args:
            patient_id: 환자 ID
            week_start_date: 주간 시작 날짜 (기본값: 지난 월요일)
            db: 데이터베이스 세션

        Returns:
            주간 리포트 정보

        Raises:
            ValueError: 환자를 찾을 수 없는 경우
        """
        if db is None:
            db = DatabaseConnection.get_session()

        if week_start_date is None:
            today = datetime.utcnow().date()
            week_start_date = today - timedelta(days=today.weekday())

        try:
            # 환자 확인
            resident = db.query(Resident).filter(
                Resident.resident_id == patient_id
            ).first()

            if not resident:
                raise ValueError(f"환자 ID {patient_id}를 찾을 수 없습니다.")

            week_end_date = week_start_date + timedelta(days=6)

            # 기간 내 일일 리포트 조회
            daily_reports = db.query(DailyReport).filter(
                DailyReport.patient_id == patient_id,
                DailyReport.report_date >= datetime.combine(week_start_date, datetime.min.time()),
                DailyReport.report_date <= datetime.combine(week_end_date, datetime.max.time())
            ).all()

            # 통계 계산
            total_reports = len(daily_reports)
            mood_distribution = {}
            medications_taken_count = 0

            for report in daily_reports:
                # 기분 분포
                mood_distribution[report.mood] = mood_distribution.get(report.mood, 0) + 1

                # 약물 복용 집계
                if report.medications_taken:
                    medications_taken_count += 1

            # 활동 요약
            activities_summary = []
            for report in daily_reports:
                if report.activities:
                    activities_summary.append({
                        "date": report.report_date.date().isoformat(),
                        "activities": report.activities
                    })

            # 주간 평가
            if total_reports == 0:
                weekly_summary = "이주간 리포트 데이터가 없습니다."
            else:
                medication_rate = (medications_taken_count / total_reports) * 100
                weekly_summary = ReportService._generate_weekly_summary(
                    resident,
                    total_reports,
                    mood_distribution,
                    medication_rate
                )

            return {
                "patient_id": patient_id,
                "patient_name": resident.name,
                "week_start": week_start_date.isoformat(),
                "week_end": week_end_date.isoformat(),
                "total_reports": total_reports,
                "mood_distribution": mood_distribution,
                "medications_taken_count": medications_taken_count,
                "activities_summary": activities_summary,
                "weekly_summary": weekly_summary,
                "generated_at": datetime.utcnow().isoformat()
            }

        except ValueError as e:
            logger.error(f"❌ 주간 리포트 생성 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def generate_monthly_performance_report(
        start_date: date,
        end_date: date,
        db: Optional[Session] = None
    ) -> Dict:
        """
        월간 성과 리포트 생성

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            db: 데이터베이스 세션

        Returns:
            월간 성과 리포트 정보
        """
        if db is None:
            db = DatabaseConnection.get_session()

        try:
            # 기간 내 매칭 조회
            matchings = db.query(PersonalityBasedMatching).filter(
                PersonalityBasedMatching.created_at >= start_date,
                PersonalityBasedMatching.created_at <= end_date
            ).all()

            # 기간 내 일일 리포트 조회
            daily_reports = db.query(DailyReport).filter(
                DailyReport.report_date >= datetime.combine(start_date, datetime.min.time()),
                DailyReport.report_date <= datetime.combine(end_date, datetime.max.time())
            ).all()

            # 통계 계산
            total_matchings = len(matchings)
            total_reports = len(daily_reports)
            avg_matching_score = sum(m.matching_score for m in matchings) / total_matchings if total_matchings > 0 else 0

            # 등급별 분포
            grade_distribution = {}
            for m in matchings:
                grade_distribution[m.grade] = grade_distribution.get(m.grade, 0) + 1

            # 기분 분포
            mood_distribution = {}
            for r in daily_reports:
                mood_distribution[r.mood] = mood_distribution.get(r.mood, 0) + 1

            # 약물 복용율
            medications_taken_count = sum(1 for r in daily_reports if r.medications_taken)
            medication_compliance_rate = (medications_taken_count / total_reports * 100) if total_reports > 0 else 0

            # 성과 평가
            performance_rating = ReportService._calculate_performance_rating(
                avg_matching_score,
                medication_compliance_rate,
                mood_distribution
            )

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "matching_statistics": {
                    "total_matchings": total_matchings,
                    "average_matching_score": round(avg_matching_score, 2),
                    "grade_distribution": grade_distribution
                },
                "care_statistics": {
                    "total_daily_reports": total_reports,
                    "medications_taken_count": medications_taken_count,
                    "medication_compliance_rate": round(medication_compliance_rate, 2),
                    "mood_distribution": mood_distribution
                },
                "performance_rating": performance_rating,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 월간 리포트 생성 실패: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def _generate_report_template(
        personality: Optional['PatientPersonality'],
        mood: str,
        activities: str,
        content: str
    ) -> str:
        """
        성향 기반 리포트 템플릿 생성

        Args:
            personality: 환자 성향 객체
            mood: 기분
            activities: 활동 기록
            content: 추가 내용

        Returns:
            생성된 리포트 템플릿
        """
        template = f"""
=== 일일 간병 리포트 ===

[기분 상태]
{mood}

[활동 기록]
{activities if activities else '활동 기록 없음'}

[추가 메모]
{content if content else '추가 메모 없음'}
"""

        # 성향에 맞춘 조언 추가
        if personality:
            personality_type = personality.personality_type
            if personality_type == "공감 중심형":
                template += "\n[전문가 조언]: 공감 중심형 환자분입니다. 정서적 지원과 대화를 통한 케어가 효과적입니다."
            elif personality_type == "활동 중심형":
                template += "\n[전문가 조언]: 활동 중심형 환자분입니다. 신체활동과 다양한 활동을 통한 케어를 권장합니다."
            elif personality_type == "자립형":
                template += "\n[전문가 조언]: 자립형 환자분입니다. 환자의 독립성을 존중하면서 필요시에만 지원하는 것이 좋습니다."
            elif personality_type == "전담형":
                template += "\n[전문가 조언]: 높은 의존도의 환자분입니다. 정기적인 관찰과 전문적 케어가 중요합니다."

        return template.strip()

    @staticmethod
    def _generate_weekly_summary(
        resident: 'Resident',
        total_reports: int,
        mood_distribution: Dict[str, int],
        medication_rate: float
    ) -> str:
        """
        주간 리포트 요약 생성

        Args:
            resident: 환자 정보
            total_reports: 총 리포트 수
            mood_distribution: 기분 분포
            medication_rate: 약물 복용율

        Returns:
            생성된 요약 텍스트
        """
        summary = f"""
주간 건강 현황 ({resident.name})
- 총 보고 일수: {total_reports}일
- 기분 분포: {', '.join(f'{mood}({count}일)' for mood, count in mood_distribution.items())}
- 약물 복용율: {medication_rate:.1f}%
"""

        if medication_rate >= 90:
            summary += "✅ 약물 복용율이 높은 편입니다."
        elif medication_rate >= 70:
            summary += "⚠️ 약물 복용율을 더 관심 있게 살펴봐야 합니다."
        else:
            summary += "❌ 약물 복용율이 낮습니다. 간병인과 보호자 간 협력이 필요합니다."

        # 기분 평가
        happy_count = mood_distribution.get("Happy", 0)
        sad_count = mood_distribution.get("Sad", 0)

        if happy_count > sad_count:
            summary += "\n✅ 전반적으로 긍정적인 기분 상태를 유지하고 있습니다."
        elif sad_count > happy_count:
            summary += "\n❌ 부정적인 감정이 자주 보입니다. 케어 방식 검토가 필요합니다."
        else:
            summary += "\n⚠️ 기분 변화가 있습니다. 지속적인 관찰이 필요합니다."

        return summary.strip()

    @staticmethod
    def _calculate_performance_rating(
        avg_matching_score: float,
        medication_compliance_rate: float,
        mood_distribution: Dict[str, int]
    ) -> str:
        """
        성과 평가 등급 계산

        Args:
            avg_matching_score: 평균 매칭 점수
            medication_compliance_rate: 약물 복용율
            mood_distribution: 기분 분포

        Returns:
            평가 등급 (우수/양호/보통/개선필요)
        """
        scores = []

        # 매칭 점수 평가
        if avg_matching_score >= 90:
            scores.append(3)
        elif avg_matching_score >= 75:
            scores.append(2)
        else:
            scores.append(1)

        # 약물 복용율 평가
        if medication_compliance_rate >= 90:
            scores.append(3)
        elif medication_compliance_rate >= 70:
            scores.append(2)
        else:
            scores.append(1)

        # 기분 평가
        total_mood_reports = sum(mood_distribution.values())
        happy_ratio = mood_distribution.get("Happy", 0) / total_mood_reports if total_mood_reports > 0 else 0

        if happy_ratio >= 0.6:
            scores.append(3)
        elif happy_ratio >= 0.4:
            scores.append(2)
        else:
            scores.append(1)

        avg_rating = sum(scores) / len(scores)

        if avg_rating >= 2.7:
            return "✅ 우수"
        elif avg_rating >= 2.0:
            return "✅ 양호"
        elif avg_rating >= 1.3:
            return "⚠️ 보통"
        else:
            return "❌ 개선 필요"
