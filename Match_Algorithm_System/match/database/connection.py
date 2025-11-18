"""
Database Connection Manager for BluedonuLab Caregiver Matching System
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import logging
import os

from .schema import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 글로벌 DB 변수
_engine = None
_SessionLocal = None


class DatabaseConnection:
    """데이터베이스 연결 관리"""

    def __init__(self, database_url: str = None):
        """
        DB 연결 초기화

        Args:
            database_url: 데이터베이스 URL
                         (기본: SQLite at ./data/carehome.db)
        """
        global _engine, _SessionLocal

        if _engine is not None:
            return  # 이미 초기화됨

        if database_url is None:
            # 기본 SQLite 경로 설정
            db_dir = Path(__file__).parent.parent / "data"
            db_dir.mkdir(exist_ok=True)
            database_url = f"sqlite:///{db_dir / 'carehome.db'}"

        self.database_url = database_url
        self._initialize_engine()
        self._initialize_session_factory()

    def _initialize_engine(self):
        """SQLAlchemy 엔진 초기화"""
        global _engine
        try:
            logger.info(f"🔗 데이터베이스 연결 중: {self.database_url}")

            # SQLite 특수 설정
            if "sqlite" in self.database_url:
                _engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    echo=False  # SQL 로깅 비활성화 (True로 설정하면 모든 SQL 쿼리 출력)
                )
                # SQLite 외래키 활성화
                @event.listens_for(_engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            else:
                _engine = create_engine(
                    self.database_url,
                    echo=False
                )

            logger.info("✅ 데이터베이스 엔진 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 엔진 초기화 실패: {e}")
            raise

    def _initialize_session_factory(self):
        """SQLAlchemy 세션 팩토리 초기화"""
        global _SessionLocal, _engine
        try:
            _SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=_engine
            )
            logger.info("✅ 세션 팩토리 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 세션 팩토리 초기화 실패: {e}")
            raise

    @staticmethod
    def get_session() -> Session:
        """
        새로운 데이터베이스 세션 반환

        Returns:
            SQLAlchemy Session 객체
        """
        global _SessionLocal
        if _SessionLocal is None:
            DatabaseConnection()  # 초기화되지 않으면 초기화

        return _SessionLocal()

    @staticmethod
    def create_all_tables():
        """모든 테이블 생성"""
        global _engine
        if _engine is None:
            raise ValueError("Database engine not initialized")

        try:
            logger.info("🔄 데이터베이스 테이블 생성 중...")
            Base.metadata.create_all(bind=_engine)
            logger.info("✅ 모든 테이블 생성 완료")
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {e}")
            raise

    @staticmethod
    def drop_all_tables():
        """모든 테이블 삭제 (개발 용도)"""
        global _engine
        if _engine is None:
            DatabaseConnection()

        try:
            logger.warning("⚠️ 모든 데이터베이스 테이블을 삭제하는 중...")
            Base.metadata.drop_all(bind=_engine)
            logger.info("✅ 모든 테이블 삭제 완료")
        except Exception as e:
            logger.error(f"❌ 테이블 삭제 실패: {e}")
            raise

    @staticmethod
    def reset_database():
        """데이터베이스 초기화 (모든 테이블 삭제 후 재생성)"""
        DatabaseConnection.drop_all_tables()
        DatabaseConnection.create_all_tables()
        logger.info("✅ 데이터베이스 초기화 완료")

    @staticmethod
    def close():
        """데이터베이스 연결 종료"""
        global _engine
        if _engine is not None:
            _engine.dispose()
            logger.info("✅ 데이터베이스 연결 종료")

    @staticmethod
    def health_check() -> bool:
        """데이터베이스 연결 상태 확인"""
        try:
            session = DatabaseConnection.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 상태 확인 실패: {e}")
            return False


def get_db() -> Session:
    """
    FastAPI 의존성 주입용 함수

    Usage:
        @app.get("/api/...")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = DatabaseConnection.get_session()
    try:
        yield db
    finally:
        db.close()


# =====================================================================
# 초기화 함수
# =====================================================================

def init_database(database_url: str = None, reset: bool = False):
    """
    데이터베이스 초기화

    Args:
        database_url: 데이터베이스 URL (기본: SQLite)
        reset: True이면 기존 데이터 삭제 후 재생성
    """
    db = DatabaseConnection(database_url)

    if reset:
        db.reset_database()
    else:
        db.create_all_tables()

    if db.health_check():
        logger.info("✅ 데이터베이스 초기화 및 상태 확인 완료")
        return True
    else:
        logger.error("❌ 데이터베이스 초기화 실패")
        return False


if __name__ == "__main__":
    # 테스트: 데이터베이스 초기화
    print("=" * 60)
    print("데이터베이스 초기화 테스트")
    print("=" * 60)

    # 초기화 (기존 데이터 유지)
    init_database()

    # 연결 확인
    db = DatabaseConnection()
    if db.health_check():
        print("\n✅ 데이터베이스 연결 정상")
    else:
        print("\n❌ 데이터베이스 연결 실패")
