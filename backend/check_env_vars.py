"""
Azure App Service 환경 변수 검증 스크립트
현재 설정된 환경 변수를 확인하고 누락된 항목을 체크합니다.
"""

import os
import sys
from typing import Dict, List, Tuple

# 필수 환경 변수 정의
REQUIRED_VARS = {
    "DATABASE_URL": "Azure PostgreSQL 연결 문자열",
    "SECRET_KEY": "JWT 토큰 서명용 비밀 키",
    "KAKAO_REST_API_KEY": "카카오 REST API 키",
    "KAKAO_REDIRECT_URI": "카카오 OAuth 리디렉트 URI",
    "FRONTEND_URL": "프론트엔드 URL (CORS 허용)",
}

# 권장 환경 변수
RECOMMENDED_VARS = {
    "DEBUG": "디버그 모드 (프로덕션에서는 False)",
}

# 선택 환경 변수
OPTIONAL_VARS = {
    "KAKAO_CLIENT_SECRET": "카카오 클라이언트 시크릿",
    "JWT_ALGORITHM": "JWT 서명 알고리즘",
    "JWT_EXPIRE_MINUTES": "JWT 토큰 만료 시간 (분)",
}


def check_env_var(var_name: str, description: str) -> Tuple[bool, str]:
    """환경 변수 존재 여부 및 값 확인"""
    value = os.getenv(var_name)
    if value:
        # 민감한 정보는 일부만 표시
        if any(keyword in var_name.upper() for keyword in ["KEY", "SECRET", "PASSWORD", "TOKEN"]):
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
        elif "DATABASE_URL" in var_name:
            # DATABASE_URL은 호스트 정보만 표시
            if "@" in value:
                masked_value = "postgresql://***@" + value.split("@")[1].split("/")[0] + "/***"
            else:
                masked_value = "***"
        else:
            masked_value = value
        return True, masked_value
    return False, ""


def main():
    print("=" * 80)
    print("🔍 Azure App Service 환경 변수 검증")
    print("=" * 80)
    
    missing_required = []
    missing_recommended = []
    
    # 필수 환경 변수 체크
    print("\n" + "=" * 80)
    print("🔴 필수 환경 변수")
    print("=" * 80)
    
    for var_name, description in REQUIRED_VARS.items():
        exists, value = check_env_var(var_name, description)
        status = "✅" if exists else "❌"
        print(f"\n{status} {var_name}")
        print(f"   설명: {description}")
        if exists:
            print(f"   값: {value}")
        else:
            print(f"   ⚠️  설정되지 않음!")
            missing_required.append(var_name)
    
    # 권장 환경 변수 체크
    print("\n" + "=" * 80)
    print("🟡 권장 환경 변수")
    print("=" * 80)
    
    for var_name, description in RECOMMENDED_VARS.items():
        exists, value = check_env_var(var_name, description)
        status = "✅" if exists else "⚠️"
        print(f"\n{status} {var_name}")
        print(f"   설명: {description}")
        if exists:
            print(f"   값: {value}")
        else:
            print(f"   기본값 사용 중")
            missing_recommended.append(var_name)
    
    # 선택 환경 변수 체크
    print("\n" + "=" * 80)
    print("🟢 선택 환경 변수")
    print("=" * 80)
    
    for var_name, description in OPTIONAL_VARS.items():
        exists, value = check_env_var(var_name, description)
        status = "✅" if exists else "ℹ️"
        print(f"\n{status} {var_name}")
        print(f"   설명: {description}")
        if exists:
            print(f"   값: {value}")
        else:
            print(f"   기본값 사용 중")
    
    # 추가 환경 변수 확인
    print("\n" + "=" * 80)
    print("📋 기타 설정된 환경 변수")
    print("=" * 80)
    
    all_defined_vars = set(REQUIRED_VARS.keys()) | set(RECOMMENDED_VARS.keys()) | set(OPTIONAL_VARS.keys())
    other_vars = {k: v for k, v in os.environ.items() 
                  if k not in all_defined_vars and not k.startswith("_")}
    
    if other_vars:
        for var_name in sorted(other_vars.keys()):
            print(f"  - {var_name}")
    else:
        print("  (없음)")
    
    # 최종 요약
    print("\n" + "=" * 80)
    print("📊 검증 결과 요약")
    print("=" * 80)
    
    total_required = len(REQUIRED_VARS)
    set_required = total_required - len(missing_required)
    
    print(f"\n필수 환경 변수: {set_required}/{total_required} 설정됨")
    print(f"권장 환경 변수: {len(RECOMMENDED_VARS) - len(missing_recommended)}/{len(RECOMMENDED_VARS)} 설정됨")
    
    if missing_required:
        print("\n❌ 누락된 필수 환경 변수:")
        for var in missing_required:
            print(f"  - {var}: {REQUIRED_VARS[var]}")
        print("\n⚠️  이 변수들을 설정하지 않으면 애플리케이션이 정상 작동하지 않습니다!")
    
    if missing_recommended:
        print("\n⚠️  누락된 권장 환경 변수:")
        for var in missing_recommended:
            print(f"  - {var}: {RECOMMENDED_VARS[var]}")
    
    # 특정 값 검증
    print("\n" + "=" * 80)
    print("🔍 값 검증")
    print("=" * 80)
    
    # DATABASE_URL 검증
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        print("\n✅ DATABASE_URL 형식 검증:")
        if "postgresql://" in db_url:
            print("  ✅ PostgreSQL 프로토콜 확인")
        else:
            print("  ❌ PostgreSQL 프로토콜이 아닙니다")
        
        if "sslmode=require" in db_url:
            print("  ✅ SSL 모드 설정됨")
        else:
            print("  ⚠️  SSL 모드가 설정되지 않았습니다 (Azure에서는 필수)")
        
        if "azure" in db_url or "postgres.database.azure.com" in db_url:
            print("  ✅ Azure PostgreSQL 연결")
        else:
            print("  ℹ️  Azure PostgreSQL이 아닐 수 있습니다")
    
    # DEBUG 검증
    debug = os.getenv("DEBUG", "True")
    print(f"\n{'✅' if debug.lower() == 'false' else '⚠️'} DEBUG 모드:")
    print(f"  현재 값: {debug}")
    if debug.lower() != "false":
        print("  ⚠️  프로덕션 환경에서는 DEBUG=False를 권장합니다")
    
    # SECRET_KEY 검증
    secret_key = os.getenv("SECRET_KEY", "")
    if secret_key:
        print(f"\n✅ SECRET_KEY 강도 검증:")
        if len(secret_key) >= 32:
            print(f"  ✅ 충분한 길이 ({len(secret_key)} 문자)")
        else:
            print(f"  ⚠️  너무 짧습니다 ({len(secret_key)} 문자, 최소 32자 권장)")
    
    # KAKAO_REDIRECT_URI 검증
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI", "")
    if redirect_uri:
        print(f"\n✅ KAKAO_REDIRECT_URI 검증:")
        if redirect_uri.startswith("https://"):
            print("  ✅ HTTPS 프로토콜 사용")
        elif redirect_uri.startswith("http://localhost"):
            print("  ⚠️  로컬 개발 환경 설정입니다")
        else:
            print("  ❌ HTTPS를 사용해야 합니다")
        
        if "/auth/kakao/callback" in redirect_uri:
            print("  ✅ 올바른 콜백 경로")
        else:
            print("  ⚠️  콜백 경로를 확인하세요")
    
    print("\n" + "=" * 80)
    
    if missing_required:
        print("❌ 검증 실패: 필수 환경 변수가 누락되었습니다")
        print("=" * 80)
        sys.exit(1)
    else:
        print("✅ 검증 성공: 모든 필수 환경 변수가 설정되었습니다")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
