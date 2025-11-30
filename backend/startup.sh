#!/bin/bash
set -e

echo "========================================"
echo "🚀 Starting BluedonuLab Backend"
echo "========================================"

# Python 버전 확인
echo "📋 Python Version:"
python --version

# 작업 디렉토리 확인
echo "📁 Working Directory:"
pwd
ls -la

# 의존성 설치 (Oryx가 이미 했지만 확인)
echo "📦 Checking dependencies..."
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found, installing dependencies..."
    pip install -r requirements.txt
fi

# 환경 변수 확인
echo "🔐 Environment Variables:"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "DEBUG: $DEBUG"
echo "FRONTEND_URL: $FRONTEND_URL"

# 데이터베이스 연결 테스트 (선택사항)
# python -c "from app.core.database import engine; engine.connect()" || echo "⚠️  DB connection failed"

# Gunicorn + Uvicorn Worker로 FastAPI 실행
echo "🎯 Starting Gunicorn with Uvicorn workers..."
exec gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
