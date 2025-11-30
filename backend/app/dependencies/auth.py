"""
인증 의존성
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.dependencies.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)  # auto_error=False로 설정하여 쿠키 인증 fallback 가능


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
) -> User:
    """
    JWT 토큰으로 현재 사용자 가져오기 (Bearer 토큰 또는 HttpOnly 쿠키)
    
    Args:
        request: FastAPI Request 객체
        credentials: Authorization 헤더의 Bearer 토큰 (선택)
        db: 데이터베이스 세션
        access_token: HttpOnly 쿠키의 JWT 토큰 (선택)
    
    Returns:
        현재 로그인한 사용자
    
    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    # 1. Bearer 토큰 우선 확인
    token = None
    if credentials:
        token = credentials.credentials
    # 2. Bearer 토큰이 없으면 쿠키에서 토큰 가져오기
    elif access_token:
        token = access_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다. 로그인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 정보를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user
