# 🎨 Artwork Q&A Builder for Dataset #

## 🌐 Language
- 한국어: [README.md](README.md)
- English: [README_EN.md](README_EN.md)

---

얘술작품 데이터셋을 위한 AI 기반 Q&A 생성 시스템입니다.
이프로젝트는 청주국제공예공모전 챗봇 구축을 위한 데이터셋 제작을 위한 것으로 출발하였으며, 보편적인 예술전시들에 적용할 수 있도록 프롬포트 커스터마이징 기능을 수정하여 공개하였습니다

**SKT A.X 4.0 무료 API**와 **uv 패키지 매니저**기반으로 작성하였습니다.
**일반관람객의 작품관람 관점(30)** + **큐레이터의 작품 관람 관점(30)** + **큐레이터관점에서의 작가제 관한 질답(20)** = 총 80개 Q&A 제작을 목표로합니다

## 🚀 빠른 시작

```bash
# 1. 환경 설정 (uv 설치)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 2. 데이터 준비
cp your_artwork_data.json data/  # 또는 data/sample.json 참조

# 3. 실행
uv run python main.py            # 고속 모드
uv run python main.py --precise  # 정밀 모드
./run_ax4.sh                     # 스크립트 사용

# 4. 결과 확인
ls final_output/                 # 작가명_작품명.json 형태로 생성
```

## 📋 데이터 형식

JSON 파일은 다음 필드들을 포함해야 합니다:

```json
{
  "items": [
    {
      "nationality": "영국",
      "artist_name": "존 스미스", 
      "artist_name_eng": "John SMITH",
      "artist_info": "{\"birth\":\"1985\",\"exhibits\":[\"전시이력\"],\"awards\":[\"수상경력\"]}",
      "title": "시간의 흔적",
      "title_eng": "Traces of Time", 
      "size": "120×80×10cm",
      "weight": "8",
      "year": "2024",
      "materials": "캔버스, 아크릴",
      "artist_note": "작가의 작품 의도와 제작 과정 설명...",
      "description": "작품에 대한 간단한 요약 설명"
    }
  ]
}
```

## 📊 출력 결과

각 작품마다 `final_output/작가명_작품명.json` 파일이 생성되며, 80개의 Q&A가 포함됩니다:

```json
[
  {
    "instruction": "이 작품에서 드러나는 작가의 철학은 무엇인가요?",
    "input": "nationality: 영국, artist_name: 존 스미스, title: 시간의 흔적...",
    "output": "존 스미스의 '시간의 흔적'에서는 시간을 층층이 쌓이는...",
    "system": "",
    "history": []
  }
]
```

**관점별 구성**: 일반관람객(30) + 큐레이터작품(30) + 큐레이터작가(20)

## 🎨 프롬프트 커스터마이징

### 프롬프트 파일 구조
```
prompts/
├── visitor_questions.md         # 일반 관람객 관점
├── curator_artwork_questions.md # 큐레이터 작품 분석  
└── curator_artist_questions.md  # 큐레이터 작가 배경
```

### 수정 방법
1. **질문 수량**: 각 파일에서 목표 개수 변경
2. **카테고리**: 질문 분류와 개수 조정
3. **스타일**: 답변 톤앤매너 설정
4. **새 관점**: 새 프롬프트 파일 추가 + 코드 수정

### 프롬프트 작성 팁
✅ **좋은 예**: 구체적 역할, 명확한 형식, 정확한 수량  
❌ **피할 것**: 모호한 지시, 열린 형식, 불명확한 역할

## ⚙️ 설정

### API 설정 (config.py)
```python
AX4_API_BASE_URL = "https://guest-api.sktax.chat/v1"
AX4_API_KEY = "sktax-XyeKFrq67ZjS4EpsDlrHHXV8it"  # 무료 게스트 키
AX4_MODEL = "ax4"
```

### 생성 모드
- `--fast`: 고속 (temperature=0.7, max_tokens=12288)
- `--precise`: 정밀 (temperature=0.8, max_tokens=16384)

## 🔧 문제 해결

```bash
# API 연결 확인
curl -I https://guest-api.sktax.chat/v1
uv run python main.py --help

# 의존성 문제
uv cache clean && uv sync

# 메모리 부족
python -c "import psutil; print(f'{psutil.virtual_memory().available/1024**3:.1f}GB')"
```

## 📁 프로젝트 구조

```
ccbdataset_api_ax4.0/
├── 📄 main.py                   # 메인 실행기
├── 🔧 config.py                # 설정
├── 🛠️ models/ax4_api_agent.py  # A.X 4.0 API 에이전트
├── ⚙️ processors/ax4_processor.py # 데이터 처리
├── 📝 prompts/                 # 프롬프트 템플릿 (3개)
├── 📊 data/sample.json         # 샘플 데이터
├── 📁 final_output/            # 생성 결과
└── 🚀 run_ax4.sh              # 실행 스크립트
```

## 📜 라이선스

MIT 라이선스

## 📞 지원

- [GitHub Issues](https://github.com/your-repo/issues)
- [A.X 4.0 API 문서](https://github.com/SKT-AI/A.X-4.0/blob/main/apis/README.md)


---