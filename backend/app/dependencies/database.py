"""
데이터베이스 세션 의존성
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성
    
    각 요청마다 새로운 DB 세션을 생성하고,
    요청이 끝나면 자동으로 닫습니다.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
