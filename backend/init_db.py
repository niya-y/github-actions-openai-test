"""
데이터베이스 초기화 스크립트
모든 테이블을 삭제하고 재생성합니다.
"""

from app.core.database import Base, engine
from app.models import *

if __name__ == "__main__":
    print("⚠️  모든 테이블을 삭제하고 재생성합니다...")
    
    # 모든 테이블 삭제
    Base.metadata.drop_all(bind=engine)
    print("✅ 기존 테이블 삭제 완료")
    
    # 모든 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("✅ 새 테이블 생성 완료")
    
    print("\n생성된 테이블:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
