"""
환경설정 관리
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database
    DATABASE_URL: str
    
    # Application
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Kakao OAuth
    KAKAO_REST_API_KEY: str
    KAKAO_REDIRECT_URI: str
    KAKAO_CLIENT_SECRET: str = ""
    
    # CORS
    FRONTEND_URL: str
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스 반환 (캐싱)"""
    return Settings()
