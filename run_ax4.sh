#!/bin/bash

# CCB Dataset Transformer - A.X 4.0 API 실행 스크립트 (uv 사용)
# SKT A.X 4.0 API를 사용한 Q&A 생성

echo "🎨 CCB Dataset Transformer (A.X 4.0 API with uv)"
echo "=================================================="
echo "📊 API 제공자: SKT A.X 4.0"
echo "🎯 목표: 80개 Q&A 생성 (30+30+20)"
echo "⚡ 패키지 매니저: uv (빠른 의존성 관리)"
echo "=================================================="

# uv 환경 확인
if ! command -v uv &> /dev/null; then
    echo "❌ uv가 설치되지 않았습니다."
    echo "설치: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# uv로 Python 실행
echo "🚀 uv 환경에서 A.X 4.0 API 기반 Q&A 생성 시작..."
uv run python main.py --fast

# 실행 결과 확인
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Q&A 생성이 성공적으로 완료되었습니다!"
    echo "📁 결과 확인: final_output/ 디렉토리"
else
    echo ""
    echo "❌ Q&A 생성 중 오류가 발생했습니다."
    exit 1
fi