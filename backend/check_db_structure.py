"""
데이터베이스 구조 확인 스크립트
테이블 수, 뷰 수, 그리고 각 테이블의 구조를 확인합니다.
"""

import sys
from sqlalchemy import create_engine, inspect, text
from app.core.config import get_settings

def main():
    settings = get_settings()
    
    # 데이터베이스 연결
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    inspector = inspect(engine)
    
    # 테이블 목록 가져오기
    tables = inspector.get_table_names()
    
    # 뷰 목록 가져오기
    views = inspector.get_view_names()
    
    print("=" * 80)
    print("데이터베이스 구조 분석")
    print("=" * 80)
    print(f"\n📊 총 테이블 수: {len(tables)}")
    print(f"📊 총 뷰 수: {len(views)}")
    print(f"📊 총 개수 (테이블 + 뷰): {len(tables) + len(views)}")
    print("=" * 80)
    
    # 테이블 상세 정보
    if tables:
        print("\n" + "=" * 80)
        print("📋 테이블 목록 및 구조")
        print("=" * 80)
        
        for table_name in sorted(tables):
            print(f"\n테이블: {table_name}")
            print("-" * 80)
            
            # 컬럼 정보
            columns = inspector.get_columns(table_name)
            print(f"  컬럼 수: {len(columns)}")
            print("  컬럼 정보:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f", DEFAULT: {col['default']}" if col['default'] else ""
                print(f"    - {col['name']}: {col['type']} {nullable}{default}")
            
            # Primary Key 정보
            pk = inspector.get_pk_constraint(table_name)
            if pk and pk['constrained_columns']:
                print(f"  Primary Key: {', '.join(pk['constrained_columns'])}")
            
            # Foreign Key 정보
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print("  Foreign Keys:")
                for fk in fks:
                    print(f"    - {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
            
            # 인덱스 정보
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else ""
                    print(f"    - {idx['name']}: {', '.join(idx['column_names'])} {unique}")
    
    # 뷰 상세 정보
    if views:
        print("\n" + "=" * 80)
        print("👁️  뷰 목록 및 구조")
        print("=" * 80)
        
        for view_name in sorted(views):
            print(f"\n뷰: {view_name}")
            print("-" * 80)
            
            # 컬럼 정보
            columns = inspector.get_columns(view_name)
            print(f"  컬럼 수: {len(columns)}")
            print("  컬럼 정보:")
            for col in columns:
                print(f"    - {col['name']}: {col['type']}")
    
    # 추가 통계 정보
    print("\n" + "=" * 80)
    print("📈 추가 통계")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 각 테이블의 레코드 수 확인
        if tables:
            print("\n테이블별 레코드 수:")
            for table_name in sorted(tables):
                try:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                    count = result.scalar()
                    print(f"  - {table_name}: {count:,} 레코드")
                except Exception as e:
                    print(f"  - {table_name}: 조회 실패 ({str(e)})")
    
    print("\n" + "=" * 80)
    print("✅ 분석 완료")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
