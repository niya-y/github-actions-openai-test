"""
데이터베이스 초기화 스크립트
schema.sql 기반 모델로 테이블 생성
"""

from app.core.database import Base, engine
from app.models import *

if __name__ == "__main__":
    print("⚠️  schema.sql 기반 테이블을 생성합니다...")
    
    # 모든 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료")
    
    print("\n생성된 테이블:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"  ✓ {table_name}")
    
    print(f"\n총 {len(Base.metadata.tables)} 개의 테이블이 생성되었습니다.")
