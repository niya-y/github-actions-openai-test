"""
Configuration for BluedonuLab Caregiver Matching System
"""

import os
from pathlib import Path

# 기본 경로
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DB_DIR = DATA_DIR

# 데이터베이스 설정
DATABASE_URL = f"sqlite:///{DB_DIR / 'carehome.db'}"

# 데이터 파일 경로
RESIDENTS_CSV = RAW_DATA_DIR / "Residents.csv"
STAFF_CSV = RAW_DATA_DIR / "staff.csv"
MEDICATIONS_CSV = RAW_DATA_DIR / "medications.csv"

# 처리된 데이터 파일 경로
RESIDENTS_PROCESSED_CSV = PROCESSED_DATA_DIR / "residents_processed.csv"
STAFF_PROCESSED_CSV = PROCESSED_DATA_DIR / "staff_processed.csv"
MEDICATIONS_PROCESSED_CSV = PROCESSED_DATA_DIR / "medications_processed.csv"

# 매칭 설정
MATCHING_CONFIG = {
    'care_weight': 0.4,              # 의료 필요도 가중치
    'personality_weight': 0.6,       # 성향 일치도 가중치
    'top_n_recommendations': 5,      # 추천 상위 N명
    'matching_grade_thresholds': {
        'A+': (95, 100),
        'A': (85, 95),
        'B+': (75, 85),
        'B': (65, 75),
        'C': (0, 65)
    }
}

# API 설정
API_CONFIG = {
    'title': 'BluedonuLab Caregiver Matching API',
    'version': '1.0.0',
    'description': '성향 기반 간병인 매칭 시스템',
    'debug': True
}

# 로깅 설정
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

# 성향 테스트 설정
PERSONALITY_TEST_CONFIG = {
    'num_questions': 12,
    'score_range': (0, 100),
    'high_threshold': 65,
    'low_threshold': 35
}

# 데이터 전처리 설정
PREPROCESSING_CONFIG = {
    'missing_value_method': 'median',  # median, mean, forward_fill
    'outlier_detection_method': 'iqr',  # iqr, zscore
    'outlier_threshold': 1.5,
    'normalize_range': (0, 100)
}
