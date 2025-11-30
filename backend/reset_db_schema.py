"""
데이터베이스 스키마 완전 재설정 스크립트
"""

from sqlalchemy import text
from app.core.database import engine

if __name__ == "__main__":
    print("⚠️  데이터베이스를 완전히 초기화합니다 (public 스키마 삭제 및 재생성)...")
    
    with engine.connect() as conn:
        # public 스키마 삭제 및 재생성
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    
    print("✅ public 스키마 초기화 완료")
    print("이제 init_db_schema.py를 실행하여 테이블을 생성하세요.")
