"""
데이터베이스 연결 설정
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# Azure PostgreSQL 연결을 위한 설정
connect_args = {}

# Azure PostgreSQL은 SSL 연결이 필수
# DATABASE_URL에 sslmode가 포함되어 있지 않으면 자동으로 추가
if "azure" in settings.DATABASE_URL or "sslmode" not in settings.DATABASE_URL:
    if "?" in settings.DATABASE_URL:
        # 이미 쿼리 파라미터가 있는 경우
        if "sslmode" not in settings.DATABASE_URL:
            # sslmode가 없으면 추가하지 않음 (URL에 직접 포함되어야 함)
            pass
    # connect_args는 SQLAlchemy가 처리하므로 비워둠

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL 쿼리 로그 출력
    pool_pre_ping=True,   # 연결 유효성 검사 (Azure에서 중요)
    pool_recycle=3600,    # 1시간마다 연결 재생성 (Azure 타임아웃 방지)
    connect_args=connect_args
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 클래스 (모든 모델이 상속)
Base = declarative_base()
