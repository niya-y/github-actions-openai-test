"""
카카오 OAuth 인증 라우터
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx

from app.core.config import get_settings
from app.core.security import create_access_token
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.get("/kakao/login")
async def kakao_login():
    """
    카카오 로그인 URL 반환
    
    프론트엔드에서 이 URL로 리디렉션하면 카카오 로그인 페이지가 표시됩니다.
    """
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={settings.KAKAO_REST_API_KEY}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    
    return {"url": kakao_auth_url}


@router.get("/kakao/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    """
    카카오 OAuth 콜백 처리
    
    1. 인가 코드로 카카오 액세스 토큰 요청
    2. 액세스 토큰으로 사용자 정보 조회
    3. DB에 사용자 생성/업데이트
    4. JWT 토큰 발급
    5. 프론트엔드로 리디렉션
    
    Args:
        code: 카카오 인가 코드
        db: 데이터베이스 세션
    
    Returns:
        프론트엔드로 리디렉션 (JWT 토큰 포함)
    """
    # 1. 카카오 액세스 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code,
    }
    
    if settings.KAKAO_CLIENT_SECRET:
        token_data["client_secret"] = settings.KAKAO_CLIENT_SECRET
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카카오 토큰 요청 실패"
            )
        
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        
        # 2. 카카오 사용자 정보 조회
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        user_info_response = await client.get(user_info_url, headers=headers)
        
        if user_info_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카카오 사용자 정보 조회 실패"
            )
        
        user_info = user_info_response.json()
    
    # 3. 사용자 정보 추출
    kakao_id = str(user_info.get("id"))
    kakao_account = user_info.get("kakao_account", {})
    profile = kakao_account.get("profile", {})
    
    email = kakao_account.get("email")
    nickname = profile.get("nickname")
    profile_image = profile.get("profile_image_url")
    
    # 4. DB에서 사용자 찾기 또는 생성
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    
    if user is None:
        # 새 사용자 생성
        user = User(
            kakao_id=kakao_id,
            email=email,
            nickname=nickname,
            profile_image=profile_image
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 기존 사용자 정보 업데이트
        user.email = email
        user.nickname = nickname
        user.profile_image = profile_image
        db.commit()
        db.refresh(user)
    
    # 5. JWT 토큰 생성
    jwt_token = create_access_token(data={"sub": str(user.id)})
    
    # 6. 프론트엔드로 리디렉션 (토큰 포함)
    frontend_redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}"
    
    return RedirectResponse(url=frontend_redirect_url)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회
    
    Args:
        current_user: JWT 토큰으로 인증된 현재 사용자
    
    Returns:
        사용자 정보
    """
    return current_user
