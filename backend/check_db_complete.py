"""
데이터베이스 구조 완전 확인 스크립트
PostgreSQL 시스템 카탈로그를 직접 쿼리하여 모든 테이블과 뷰를 확인합니다.
"""

import sys
from sqlalchemy import create_engine, text
from app.core.config import get_settings

def main():
    settings = get_settings()
    
    # 데이터베이스 연결
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    with engine.connect() as conn:
        print("=" * 80)
        print("데이터베이스 구조 완전 분석 (PostgreSQL 시스템 카탈로그 직접 쿼리)")
        print("=" * 80)
        
        # 테이블 목록 조회 (pg_catalog 직접 쿼리)
        table_query = text("""
            SELECT 
                schemaname,
                tablename,
                'table' as object_type
            FROM pg_catalog.pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY tablename;
        """)
        
        tables_result = conn.execute(table_query)
        tables = list(tables_result)
        
        # 뷰 목록 조회 (pg_catalog 직접 쿼리)
        view_query = text("""
            SELECT 
                schemaname,
                viewname as tablename,
                'view' as object_type
            FROM pg_catalog.pg_views
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY viewname;
        """)
        
        views_result = conn.execute(view_query)
        views = list(views_result)
        
        print(f"\n📊 총 테이블 수: {len(tables)}")
        print(f"📊 총 뷰 수: {len(views)}")
        print(f"📊 총 개수 (테이블 + 뷰): {len(tables) + len(views)}")
        print("=" * 80)
        
        # 테이블 목록 출력
        if tables:
            print("\n" + "=" * 80)
            print("📋 테이블 목록")
            print("=" * 80)
            for idx, row in enumerate(tables, 1):
                print(f"{idx:2d}. {row.tablename} (스키마: {row.schemaname})")
        
        # 뷰 목록 출력
        if views:
            print("\n" + "=" * 80)
            print("👁️  뷰 목록")
            print("=" * 80)
            for idx, row in enumerate(views, 1):
                print(f"{idx:2d}. {row.tablename} (스키마: {row.schemaname})")
                
            # 각 뷰의 정의 확인
            print("\n" + "=" * 80)
            print("👁️  뷰 상세 정보")
            print("=" * 80)
            
            for row in views:
                view_name = row.tablename
                schema_name = row.schemaname
                
                print(f"\n뷰: {schema_name}.{view_name}")
                print("-" * 80)
                
                # 뷰 정의 조회
                view_def_query = text("""
                    SELECT definition
                    FROM pg_views
                    WHERE schemaname = :schema AND viewname = :view
                """)
                
                view_def_result = conn.execute(
                    view_def_query, 
                    {"schema": schema_name, "view": view_name}
                )
                view_def = view_def_result.scalar()
                
                if view_def:
                    print(f"정의:\n{view_def}")
                
                # 뷰의 컬럼 정보
                columns_query = text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = :schema 
                      AND table_name = :view
                    ORDER BY ordinal_position;
                """)
                
                columns_result = conn.execute(
                    columns_query,
                    {"schema": schema_name, "view": view_name}
                )
                columns = list(columns_result)
                
                print(f"\n컬럼 정보 ({len(columns)}개):")
                for col in columns:
                    nullable = "NULL" if col.is_nullable == 'YES' else "NOT NULL"
                    print(f"  - {col.column_name}: {col.data_type} {nullable}")
        
        # 전체 객체 요약
        print("\n" + "=" * 80)
        print("📊 전체 데이터베이스 객체 요약")
        print("=" * 80)
        
        all_objects_query = text("""
            SELECT 
                n.nspname as schema_name,
                c.relname as object_name,
                CASE c.relkind
                    WHEN 'r' THEN 'table'
                    WHEN 'v' THEN 'view'
                    WHEN 'm' THEN 'materialized view'
                    WHEN 'i' THEN 'index'
                    WHEN 'S' THEN 'sequence'
                    WHEN 's' THEN 'special'
                    WHEN 'f' THEN 'foreign table'
                    WHEN 'p' THEN 'partitioned table'
                    WHEN 'I' THEN 'partitioned index'
                END as object_type
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
              AND c.relkind IN ('r', 'v', 'm')
            ORDER BY object_type, object_name;
        """)
        
        all_objects_result = conn.execute(all_objects_query)
        all_objects = list(all_objects_result)
        
        # 객체 타입별 그룹화
        from collections import defaultdict
        objects_by_type = defaultdict(list)
        
        for obj in all_objects:
            objects_by_type[obj.object_type].append(obj.object_name)
        
        for obj_type, obj_names in sorted(objects_by_type.items()):
            print(f"\n{obj_type.upper()} ({len(obj_names)}개):")
            for name in sorted(obj_names):
                print(f"  - {name}")
        
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
