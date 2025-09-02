# 🎨 CCB Dataset Transformer (A.X 4.0 API)

CCB(청주공예비엔날레) 데이터셋을 위한 AI 기반 Q&A 생성 시스템입니다.  
**SKT A.X 4.0 API**를 활용하여 작품 정보로부터 고품질 질문/답변 쌍을 자동 생성합니다.

## ✨ 주요 특징

### 🌐 클라우드 기반 AI
- **SKT A.X 4.0 API**: 서버급 AI 모델 활용
- **크로스 플랫폼**: macOS, Linux, Windows 모두 지원
- **즉시 시작**: 로컬 모델 다운로드 불필요

### ⚡ uv 패키지 매니저
- **초고속 설치**: pip 대비 10-100배 빠른 의존성 관리
- **자동 환경 관리**: 가상환경 자동 생성/활성화
- **모던 워크플로우**: 현대적 Python 개발 도구

### 🎯 다중 관점 Q&A 생성
- **일반 관람객** (30개): 접근하기 쉬운 감상 중심
- **큐레이터 작품** (30개): 전문적 작품 분석 
- **큐레이터 작가** (20개): 작가 배경 및 맥락
- **총 80개** Q&A 자동 생성

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치 및 가상환경 생성
uv sync
```

### 2. 실행
```bash
# 기본 실행 (고속 모드)
uv run python main_ax4.py

# 정밀 모드  
uv run python main_ax4.py --precise

# 편리한 스크립트
./run_ax4.sh
```

### 3. 결과 확인
```bash
# 생성된 Q&A 확인
ls final_output/
```

## 📁 프로젝트 구조

```
ccbdataset_api_ax4.0/
├── 📄 main_ax4.py              # 메인 실행기
├── 🔧 config.py                # 설정 파일
├── 🛠️ models/
│   └── ax4_api_agent.py        # A.X 4.0 API 에이전트
├── ⚙️ processors/
│   └── ax4_processor.py        # 데이터 처리기
├── 📝 prompts/                 # 프롬프트 템플릿
├── 🔨 utils/                   # 유틸리티 함수들
├── 📊 data/                    # 입력 데이터 (JSON)
├── 📁 final_output/            # 생성된 Q&A
├── 🚀 run_ax4.sh              # 실행 스크립트
└── 📖 README.md               # 이 문서
```

## 🎛️ 사용법

### 기본 명령어
```bash
# 고속 모드 (기본값)
uv run python main_ax4.py --fast

# 정밀 모드 (높은 품질)  
uv run python main_ax4.py --precise

# API 연결 테스트
uv run python simple_test.py
```

### 데이터 준비
```bash
# data/ 디렉토리에 JSON 파일 배치
cp your_artwork_data.json data/

# 파일 형식 예시
{
  "items": [
    {
      "title": "작품명",
      "artist_name": "작가명", 
      "materials": "재료",
      "artist_note": "작가노트",
      "description": "작품설명"
      // ... 기타 필드
    }
  ]
}
```

## ⚙️ 설정 옵션

### 생성 모드
- **고속 모드**: `temperature=0.7`, `max_tokens=12288`
- **정밀 모드**: `temperature=0.8`, `max_tokens=16384`

### API 설정
```python
# config.py에서 수정 가능
AX4_API_BASE_URL = "https://guest-api.sktax.chat/v1"
AX4_API_KEY = "sktax-XyeKFrq67ZjS4EpsDlrHHXV8it"
AX4_MODEL = "ax4"
```

## 📊 출력 형식

생성된 Q&A는 다음 형식으로 저장됩니다:

```json
[
  {
    "instruction": "이 작품에서 드러나는 작가의 철학은 무엇인가요?",
    "input": "작품명: Happening, 작가: 리차드 맥베티스, 재료: 울,면...",
    "output": "리차드 맥베티스의 'Happening'은 시간과 존재에 대한 깊은 철학적 탐구를 담고 있습니다...",
    "system": "",
    "history": []
  }
]
```

## 🚨 문제 해결

### API 연결 오류
```bash
# 네트워크 연결 확인
curl -I https://guest-api.sktax.chat/v1

# 간단한 연결 테스트
uv run python simple_test.py
```

### 의존성 문제
```bash
# 의존성 재설치
uv cache clean
uv sync

# 가상환경 재생성
rm -rf .venv
uv sync
```

### 메모리 문제
```bash
# 시스템 메모리 확인
python -c "import psutil; print(f'{psutil.virtual_memory().available/1024**3:.1f}GB 사용가능')"
```

## 🌟 장점

### vs 로컬 모델
| 항목 | 로컬 모델 | A.X 4.0 API |
|------|-----------|-------------|
| 설치 시간 | ~30분 | ~30초 |
| 메모리 사용량 | ~20GB | ~1GB |
| 하드웨어 요구사항 | M1/M2/M3 Pro+ | 모든 시스템 |
| 모델 품질 | 로컬 제한 | 서버급 최신 |
| 유지보수 | 복잡 | 간단 |

### vs 다른 API
- ✅ **무료 제공**: 게스트 API 키 제공
- ✅ **한국어 특화**: 국내 데이터 최적화  
- ✅ **안정적 서비스**: SKT 인프라
- ✅ **빠른 응답**: 최적화된 엔드포인트

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **문서**: [RUN_WITH_UV_AX4.md](RUN_WITH_UV_AX4.md)
- **API 문서**: [A.X 4.0 API](https://github.com/SKT-AI/A.X-4.0/blob/main/apis/README.md)

---

**⚡ uv와 A.X 4.0 API로 빠르고 쉬운 Q&A 생성을 경험하세요!**
