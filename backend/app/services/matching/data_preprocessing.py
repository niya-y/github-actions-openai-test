# ========================================
# 늘봄케어 매칭 모델 - 데이터 전처리
# ========================================
# 파일: data_preprocessing.py
# 설명: CSV 파일을 로드하고 학습에 필요한 형태로 전처리

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """데이터 전처리 클래스"""

    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: 데이터 폴더 경로
        """
        self.data_dir = Path(data_dir)

        # 데이터프레임 저장용
        self.caregivers = None
        self.caregiver_personality = None
        self.patients = None
        self.patient_personality = None
        self.health_conditions = None
        self.matching_results = None
        self.reviews = None

    def load_all_data(self) -> dict:
        """
        모든 CSV 파일 로드

        Returns:
            dict: 로드된 데이터프레임 딕셔너리
        """
        logger.info("📂 데이터 로드 시작...")

        # 간병인 데이터
        self.caregivers = pd.read_csv(
            self.data_dir / "caregivers_profile.csv"
        )
        self.caregiver_personality = pd.read_csv(
            self.data_dir / "caregiver_personality.csv"
        )

        # 환자 데이터
        self.patients = pd.read_csv(
            self.data_dir / "patients_profile.csv"
        )
        self.patient_personality = pd.read_csv(
            self.data_dir / "patient_personality.csv"
        )
        self.health_conditions = pd.read_csv(
            self.data_dir / "health_conditions.csv"
        )

        # 매칭 결과 데이터
        self.matching_results = pd.read_csv(
            self.data_dir / "matching_results.csv"
        )
        self.reviews = pd.read_csv(
            self.data_dir / "reviews.csv"
        )

        logger.info(f"✅ 간병인 프로필: {len(self.caregivers)}명")
        logger.info(f"✅ 환자 프로필: {len(self.patients)}명")
        logger.info(f"✅ 매칭 결과: {len(self.matching_results)}건")
        logger.info(f"✅ 리뷰: {len(self.reviews)}건")

        return {
            "caregivers": self.caregivers,
            "caregiver_personality": self.caregiver_personality,
            "patients": self.patients,
            "patient_personality": self.patient_personality,
            "health_conditions": self.health_conditions,
            "matching_results": self.matching_results,
            "reviews": self.reviews
        }

    def preprocess_caregivers(self) -> pd.DataFrame:
        """
        간병인 데이터 전처리
        - 성격 점수 병합
        - 전문분야 리스트 변환

        Returns:
            pd.DataFrame: 전처리된 간병인 데이터
        """
        if self.caregivers is None:
            raise ValueError("데이터를 먼저 로드하세요. load_all_data() 호출 필요")

        # 간병인 프로필 + 성격 점수 병합
        df = self.caregivers.merge(
            self.caregiver_personality,
            on="caregiver_id",
            how="left"
        )

        # 전문분야를 리스트로 변환
        df["specialties_list"] = df["specialties"].apply(
            lambda x: x.split("|") if pd.notna(x) else []
        )

        # 전문분야 개수
        df["specialties_count"] = df["specialties_list"].apply(len)

        # 결측치 처리 (성격 점수)
        personality_cols = [
            "empathy_score", "activity_score",
            "patience_score", "independence_score"
        ]
        for col in personality_cols:
            df[col] = df[col].fillna(50.0)  # 중간값으로 채움

        logger.info(f"✅ 간병인 전처리 완료: {len(df)}명")

        return df

    def preprocess_patients(self) -> pd.DataFrame:
        """
        환자 데이터 전처리
        - 성격 점수 병합
        - 질환 정보 병합
        - 요양등급 숫자 변환

        Returns:
            pd.DataFrame: 전처리된 환자 데이터
        """
        if self.patients is None:
            raise ValueError("데이터를 먼저 로드하세요. load_all_data() 호출 필요")

        # 환자 프로필 + 성격 점수 병합
        df = self.patients.merge(
            self.patient_personality,
            on="patient_id",
            how="left"
        )

        # 환자별 질환 리스트 생성
        diseases_df = self.health_conditions.groupby("patient_id")["disease_name"].apply(list).reset_index()
        diseases_df.columns = ["patient_id", "diseases_list"]

        df = df.merge(diseases_df, on="patient_id", how="left")

        # 질환 리스트 결측치 처리
        df["diseases_list"] = df["diseases_list"].apply(
            lambda x: x if isinstance(x, list) else []
        )

        # 질환 개수
        df["disease_count"] = df["diseases_list"].apply(len)

        # 요양등급 → 숫자 변환
        care_level_map = {
            "1등급": 1,
            "2등급": 2,
            "3등급": 3,
            "4등급": 4,
            "5등급": 5,
            "인지지원등급": 6
        }
        df["care_level_num"] = df["care_level"].map(care_level_map).fillna(3)

        # 결측치 처리 (성격 점수)
        personality_cols = [
            "empathy_score", "activity_score",
            "patience_score", "independence_score"
        ]
        for col in personality_cols:
            df[col] = df[col].fillna(50.0)

        logger.info(f"✅ 환자 전처리 완료: {len(df)}명")

        return df

    def preprocess_matching_results(self) -> pd.DataFrame:
        """
        매칭 결과 데이터 전처리
        - 리뷰(만족도) 병합
        - 타겟 변수 생성

        Returns:
            pd.DataFrame: 전처리된 매칭 결과 데이터
        """
        if self.matching_results is None:
            raise ValueError("데이터를 먼저 로드하세요. load_all_data() 호출 필요")

        df = self.matching_results.copy()

        # 리뷰 데이터 병합 (완료된 매칭만 리뷰 있음)
        reviews_df = self.reviews[["matching_id", "rating"]].copy()
        df = df.merge(reviews_df, on="matching_id", how="left")

        # 등급 → 숫자 변환 (타겟 변수로 사용 가능)
        grade_map = {
            "A+": 5,
            "A": 4,
            "B+": 3,
            "B": 2,
            "C": 1
        }
        df["grade_num"] = df["grade"].map(grade_map)

        # 성공 여부 (이진 분류용)
        # completed + rating >= 3 = 성공
        df["is_success"] = (
            (df["status"] == "completed") &
            (df["rating"].fillna(0) >= 3)
        ).astype(int)

        logger.info(f"✅ 매칭 결과 전처리 완료: {len(df)}건")
        logger.info(f"   - 성공 매칭: {df['is_success'].sum()}건")
        logger.info(f"   - 실패/미완료: {len(df) - df['is_success'].sum()}건")

        return df

    def get_region_type(self, region_code: str) -> str:
        """
        지역 코드에서 광역 지역 추출

        Args:
            region_code: 지역 코드 (예: SEOUL_GANGNAM)

        Returns:
            str: 광역 지역 (SEOUL, GYEONGGI, BUSAN 등)
        """
        if pd.isna(region_code):
            return "UNKNOWN"
        return region_code.split("_")[0]

    def run_all_preprocessing(self) -> dict:
        """
        전체 전처리 파이프라인 실행

        Returns:
            dict: 전처리된 데이터프레임 딕셔너리
        """
        logger.info("🔄 전처리 파이프라인 시작")

        # 1. 데이터 로드
        self.load_all_data()

        # 2. 각 데이터 전처리
        caregivers_processed = self.preprocess_caregivers()
        patients_processed = self.preprocess_patients()
        matching_processed = self.preprocess_matching_results()

        logger.info("✅ 전처리 완료!")

        return {
            "caregivers": caregivers_processed,
            "patients": patients_processed,
            "matching_results": matching_processed,
            "health_conditions": self.health_conditions
        }
