# 🚀 A.X 4.0 API with uv 실행 가이드

## ⚡ 빠른 실행 (권장)

### 기본 실행
```bash
# 고속 모드 (기본값)
uv run python main_ax4.py

# 정밀 모드
uv run python main_ax4.py --precise

# 또는 편리한 스크립트 사용
./run_ax4.sh
```

## 🛠️ 환경 설정

### 의존성 설치 및 동기화
```bash
# 처음 설정 (자동으로 가상환경 생성)
uv sync

# 패키지 추가
uv add requests beautifulsoup4

# 개발 도구 추가  
uv add --dev pytest black isort mypy

# 현재 패키지 확인
uv pip list
```

### 환경 관리
```bash
# 가상환경 활성화 (대화형 셸)
uv shell

# 환경 정보 확인
uv info

# 캐시 정리
uv cache clean
```

## 📊 A.X 4.0 API 장점

### 🌐 클라우드 기반
- ✅ **로컬 모델 불필요**: GPU/MLX 하드웨어 요구사항 제거
- ✅ **즉시 시작**: 모델 다운로드 대기시간 없음
- ✅ **크로스 플랫폼**: macOS, Linux, Windows 모두 지원

### ⚡ 성능 및 편의성
- ✅ **일관된 응답**: 서버급 모델 품질
- ✅ **빠른 응답**: 네트워크 기반 고속 처리
- ✅ **메모리 효율**: 로컬 메모리 사용량 최소화

## 🎯 Q&A 생성 워크플로우

### 1. 데이터 준비
```bash
# data/ 디렉토리에 JSON 파일 배치
ls data/
# -> items_202509011603.json
```

### 2. 실행
```bash
# uv 환경에서 실행
uv run python main_ax4.py --fast
```

### 3. 결과 확인
```bash
# 생성된 Q&A 확인
ls final_output/
# -> 리차드_맥베티스_Happening.json
# -> 여_약카_애슐리_Scent_of_Time.json
```

## 🔧 고급 사용법

### 특정 Python 버전 사용
```bash
uv run --python 3.12 python main_ax4.py
```

### 환경 변수와 함께 실행
```bash
# .env 파일 활용
uv run --env-file .env python main_ax4.py
```

### API 연결 테스트
```bash
# 간단한 연결 테스트
uv run python simple_test.py

# 전체 테스트 스위트 
uv run python test_ax4_api.py
```

## 📈 성능 비교

### 기존 로컬 모델 방식
```bash
# EXAONE MLX (M3 Pro 필요, ~20GB 메모리)
python main.py --fast
```

### A.X 4.0 API + uv 방식 ⭐
```bash
# 어떤 하드웨어에서도 동작 (~1GB 메모리)
uv run python main_ax4.py --fast
```

## 🎛️ 설정 옵션

### 생성 모드
- `--fast`: 고속 생성 (temperature=0.7, max_tokens=12288)
- `--precise`: 정밀 생성 (temperature=0.8, max_tokens=16384)

### 목표 Q&A 수량
- **일반 관람객 관점**: 30개 질문/답변
- **큐레이터 작품 관점**: 30개 질문/답변  
- **큐레이터 작가 관점**: 20개 질문/답변
- **총 합계**: 80개 Q&A

## 🚨 문제 해결

### API 연결 오류
```bash
# 네트워크 연결 확인
curl -I https://guest-api.sktax.chat/v1

# 간단한 테스트
uv run python simple_test.py
```

### 의존성 오류  
```bash
# 의존성 재설치
uv sync

# 캐시 정리 후 재설치
uv cache clean
uv sync
```

### 모듈 임포트 오류
```bash
# 가상환경 경로 확인
uv venv --show-path

# 프로젝트 재빌드
uv sync --reinstall
```

## 💡 개발 팁

### 1. 자주 사용하는 명령어 alias
```bash
alias ax4-fast="uv run python main_ax4.py --fast"
alias ax4-precise="uv run python main_ax4.py --precise" 
alias ax4-test="uv run python simple_test.py"
```

### 2. IDE 설정
```bash
# uv 가상환경 경로를 IDE Python 인터프리터로 설정
uv venv --show-path
```

### 3. 배치 처리
```bash
# 여러 데이터 파일 일괄 처리
for file in data/*.json; do
    echo "Processing $file..."
    uv run python main_ax4.py --fast
done
```

## 🌟 uv의 장점

### 속도
- **설치 속도**: pip 대비 10-100배 빠름
- **의존성 해결**: 병렬 처리로 초고속
- **가상환경**: 즉시 생성 및 활성화

### 편의성
- **자동 관리**: 가상환경 자동 생성/관리
- **크로스 플랫폼**: 일관된 동작 보장
- **현대적 도구**: Poetry/pipenv의 장점 결합

이제 `uv run python main_ax4.py --fast`로 A.X 4.0 API 기반 Q&A 생성을 빠르고 안정적으로 실행할 수 있습니다!