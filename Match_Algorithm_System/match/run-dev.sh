#!/bin/bash

# BluedonuLab 개발 환경 실행 스크립트

echo "🚀 BluedonuLab 개발 환경 시작"
echo "================================"

# 가상환경 활성화
echo "📦 가상환경 활성화 중..."
source .venv/bin/activate

# 의존성 확인
echo "✅ 의존성 확인 완료"

# FastAPI 서버 실행
echo ""
echo "🌐 FastAPI 서버 시작 중..."
echo "📍 http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/api/docs"
echo "🎨 UI: http://localhost:8000/ui"
echo "🧪 테스트: http://localhost:8000/ui/api-test.html"
echo ""
echo "서버를 중지하려면 Ctrl+C 를 누르세요"
echo "================================"
echo ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
