"""
Data loading and preprocessing module for BluedonuLab Caregiver Matching System
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """CSV 파일 로딩 및 기본 검증"""

    def __init__(self, data_dir: str = "./data/raw"):
        self.data_dir = Path(data_dir)

    def load_residents(self) -> pd.DataFrame:
        """Residents.csv 로딩"""
        try:
            path = self.data_dir / "Residents.csv"
            df = pd.read_csv(path, index_col=0)
            logger.info(f"✅ Residents 데이터 로딩 완료: {len(df)} 행")
            return df
        except FileNotFoundError:
            logger.error(f"❌ 파일을 찾을 수 없음: {path}")
            raise

    def load_staff(self) -> pd.DataFrame:
        """staff.csv 로딩"""
        try:
            path = self.data_dir / "staff.csv"
            df = pd.read_csv(path, index_col=0)
            logger.info(f"✅ Staff 데이터 로딩 완료: {len(df)} 행")
            return df
        except FileNotFoundError:
            logger.error(f"❌ 파일을 찾을 수 없음: {path}")
            raise

    def load_medications(self) -> pd.DataFrame:
        """medications.csv 로딩"""
        try:
            path = self.data_dir / "medications.csv"
            df = pd.read_csv(path, index_col=0)
            logger.info(f"✅ Medications 데이터 로딩 완료: {len(df)} 행, 결측치: {df.isna().sum().sum()}")
            return df
        except FileNotFoundError:
            logger.error(f"❌ 파일을 찾을 수 없음: {path}")
            raise


class DataPreprocessor:
    """데이터 전처리: 결측치, 타입 변환, 정규화, 이상치 처리"""

    @staticmethod
    def handle_missing_values(df: pd.DataFrame, column: str, method: str = 'median') -> pd.DataFrame:
        """
        결측치 처리

        Args:
            df: DataFrame
            column: 처리할 컬럼명
            method: 'median' (중앙값), 'mean' (평균), 'forward_fill' (앞값 전파)

        Returns:
            결측치 처리된 DataFrame
        """
        missing_count = df[column].isna().sum()
        if missing_count == 0:
            return df

        if method == 'median':
            median_value = df[column].median()
            df[column].fillna(median_value, inplace=True)
            logger.info(f"✅ {column}: {missing_count}개 결측치 → 중앙값({median_value})으로 충전")
        elif method == 'mean':
            mean_value = df[column].mean()
            df[column].fillna(mean_value, inplace=True)
            logger.info(f"✅ {column}: {missing_count}개 결측치 → 평균값({mean_value:.2f})으로 충전")
        elif method == 'forward_fill':
            df[column].fillna(method='ffill', inplace=True)
            logger.info(f"✅ {column}: {missing_count}개 결측치 → 앞값 전파로 충전")

        return df

    @staticmethod
    def convert_date_columns(df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
        """
        날짜 컬럼을 datetime으로 변환

        Args:
            df: DataFrame
            date_columns: 날짜 컬럼 리스트

        Returns:
            날짜 변환된 DataFrame
        """
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
                logger.info(f"✅ {col}: datetime으로 변환")

        return df

    @staticmethod
    def categorize_columns(df: pd.DataFrame, categorical_columns: Dict[str, list]) -> pd.DataFrame:
        """
        카테고리 컬럼 처리

        Args:
            df: DataFrame
            categorical_columns: {컬럼명: [카테고리값들]}

        Returns:
            카테고리 변환된 DataFrame
        """
        for col, categories in categorical_columns.items():
            if col in df.columns:
                df[col] = pd.Categorical(df[col], categories=categories)
                logger.info(f"✅ {col}: Categorical로 변환 ({len(categories)}개 카테고리)")

        return df

    @staticmethod
    def normalize_numeric_columns(df: pd.DataFrame, columns: list, min_val: float = 0, max_val: float = 100) -> pd.DataFrame:
        """
        수치 컬럼 정규화 (min-max 스케일링)

        Args:
            df: DataFrame
            columns: 정규화할 컬럼 리스트
            min_val: 최소값 (기본: 0)
            max_val: 최대값 (기본: 100)

        Returns:
            정규화된 DataFrame
        """
        for col in columns:
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                original_min = df[col].min()
                original_max = df[col].max()

                if original_max - original_min > 0:
                    df[col] = (df[col] - original_min) / (original_max - original_min) * (max_val - min_val) + min_val
                    logger.info(f"✅ {col}: [{original_min:.2f}, {original_max:.2f}] → [{min_val}, {max_val}]로 정규화")

        return df

    @staticmethod
    def detect_outliers(df: pd.DataFrame, columns: list, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """
        이상치 탐지 및 제거

        Args:
            df: DataFrame
            columns: 검사할 컬럼 리스트
            method: 'iqr' (사분위수 범위), 'zscore' (표준화된 점수)
            threshold: IQR 방식에서는 승수, zscore에서는 표준편차

        Returns:
            이상치 제거된 DataFrame
        """
        initial_len = len(df)

        for col in columns:
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                if method == 'iqr':
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - threshold * IQR
                    upper = Q3 + threshold * IQR
                    df = df[(df[col] >= lower) & (df[col] <= upper)]
                    removed = initial_len - len(df)
                    if removed > 0:
                        logger.info(f"✅ {col}: {removed}개 이상치 제거")
                elif method == 'zscore':
                    mean = df[col].mean()
                    std = df[col].std()
                    df = df[np.abs((df[col] - mean) / std) <= threshold]
                    removed = initial_len - len(df)
                    if removed > 0:
                        logger.info(f"✅ {col}: {removed}개 이상치 제거")

        return df

    @staticmethod
    def validate_data_quality(df: pd.DataFrame) -> Dict:
        """
        데이터 품질 검증

        Returns:
            품질 지표 딕셔너리
        """
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isna().sum().sum(),
            'missing_percentage': (df.isna().sum().sum() / (len(df) * len(df.columns))) * 100,
            'duplicate_rows': len(df) - len(df.drop_duplicates()),
            'data_types': df.dtypes.to_dict()
        }

        logger.info(f"\n📊 데이터 품질 리포트:")
        logger.info(f"   - 행: {quality_report['total_rows']}")
        logger.info(f"   - 열: {quality_report['total_columns']}")
        logger.info(f"   - 결측치: {quality_report['missing_values']} ({quality_report['missing_percentage']:.2f}%)")
        logger.info(f"   - 중복행: {quality_report['duplicate_rows']}")

        return quality_report


class ResidentsPreprocessor:
    """Residents 데이터 전처리"""

    @staticmethod
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        """
        Residents 데이터 전처리 파이프라인

        Args:
            df: 원본 Residents DataFrame

        Returns:
            전처리된 DataFrame
        """
        logger.info("\n🔄 Residents 전처리 시작...")

        # 1. 날짜 컬럼 변환
        df = DataPreprocessor.convert_date_columns(
            df,
            ['Date of Birth', 'Admission Date']
        )

        # 2. 카테고리 변환
        df = DataPreprocessor.categorize_columns(
            df,
            {
                'Gender': ['Male', 'Female', 'Other'],
                'Care Level': ['Low', 'Moderate', 'High']
            }
        )

        # 3. 데이터 품질 검증
        DataPreprocessor.validate_data_quality(df)

        logger.info("✅ Residents 전처리 완료\n")
        return df


class StaffPreprocessor:
    """Staff 데이터 전처리"""

    @staticmethod
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        """
        Staff 데이터 전처리 파이프라인

        Args:
            df: 원본 Staff DataFrame

        Returns:
            전처리된 DataFrame
        """
        logger.info("\n🔄 Staff 전처리 시작...")

        # 1. 날짜 컬럼 변환
        df = DataPreprocessor.convert_date_columns(
            df,
            ['Date of Birth', 'Employment Date']
        )

        # 2. 경험도 계산 (년수)
        today = datetime.now()
        df['Experience_Years'] = df['Employment Date'].apply(
            lambda x: (today - x).days / 365.25
        )
        df['Experience_Years'] = df['Experience_Years'].clip(lower=0)

        # 3. 카테고리 변환
        df = DataPreprocessor.categorize_columns(
            df,
            {
                'Gender': ['Male', 'Female', 'Other'],
                'Job Title': ['Nurse', 'Caregiver', 'Doctor', 'Therapist', 'Administrator']
            }
        )

        # 4. 데이터 품질 검증
        DataPreprocessor.validate_data_quality(df)

        logger.info("✅ Staff 전처리 완료\n")
        return df


class MedicationsPreprocessor:
    """Medications 데이터 전처리"""

    @staticmethod
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        """
        Medications 데이터 전처리 파이프라인

        Args:
            df: 원본 Medications DataFrame

        Returns:
            전처리된 DataFrame
        """
        logger.info("\n🔄 Medications 전처리 시작...")

        # 1. Dosage 컬럼에서 숫자만 추출 (e.g., "500mg" → 500)
        if 'Dosage' in df.columns:
            df['Dosage'] = df['Dosage'].str.replace('mg', '', regex=False).str.strip()
            # 숫자로 변환
            df['Dosage'] = pd.to_numeric(df['Dosage'], errors='coerce')
            # 결측치 처리
            df = DataPreprocessor.handle_missing_values(df, 'Dosage', method='median')
            logger.info(f"✅ Dosage: 숫자로 변환 완료")

        # 2. 날짜 컬럼 변환
        df = DataPreprocessor.convert_date_columns(
            df,
            ['Prescription End Date']
        )

        # 3. 데이터 품질 검증
        DataPreprocessor.validate_data_quality(df)

        logger.info("✅ Medications 전처리 완료\n")
        return df


def preprocess_all_data(raw_data_dir: str = "./data/raw", output_dir: str = "./data/processed") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    전체 데이터 전처리 파이프라인

    Args:
        raw_data_dir: 원본 CSV 디렉토리
        output_dir: 전처리된 CSV 저장 디렉토리

    Returns:
        (residents_df, staff_df, medications_df) 튜플
    """

    # 출력 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 데이터 로딩
    loader = DataLoader(raw_data_dir)
    residents = loader.load_residents()
    staff = loader.load_staff()
    medications = loader.load_medications()

    # 전처리
    residents = ResidentsPreprocessor.preprocess(residents)
    staff = StaffPreprocessor.preprocess(staff)
    medications = MedicationsPreprocessor.preprocess(medications)

    # CSV 저장
    output_path = Path(output_dir)
    residents.to_csv(output_path / "residents_processed.csv")
    staff.to_csv(output_path / "staff_processed.csv")
    medications.to_csv(output_path / "medications_processed.csv")

    logger.info(f"\n✅ 전처리된 파일 저장 완료: {output_dir}/")

    return residents, staff, medications


if __name__ == "__main__":
    # 테스트 실행
    residents, staff, medications = preprocess_all_data()
    print("\n✅ 데이터 전처리 완료!")
    print(f"Residents: {len(residents)} 행")
    print(f"Staff: {len(staff)} 행")
    print(f"Medications: {len(medications)} 행")
