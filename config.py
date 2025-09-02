"""
CCB Dataset Transformer 설정 파일 (EXAONE 전용)
- 모델 경로 및 출력 디렉토리 설정
- 메모리 임계값 및 시스템 설정
"""

from pathlib import Path

# === 모델 설정 ===
# MLX 모델 사용 (EXAONE-4.0-32B)
MODEL_REPO = "lmstudio-community/EXAONE-4.0-32B-MLX-4bit"
MODEL_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"  # HuggingFace 표준 캐시

# MLX 모델로 로드
MODEL_TYPE = "MLX"  # MLX 모델 사용
MODEL_NAME = "lmstudio-community/EXAONE-4.0-32B-MLX-4bit"

# 사용 가능한 모델 버전 (MLX 단일 모델)
AVAILABLE_MODELS = {
    "mlx": MODEL_NAME,
    "auto": MODEL_NAME,
}

# === 모델 다운로드 설정 ===
AUTO_DOWNLOAD_MODEL = True
# MLX 모델 사용
DEFAULT_MODEL_VARIANT = "mlx" 

# --- 내부 사용 ---
# MLX 모델은 모델명으로 직접 로드
_model_variant = DEFAULT_MODEL_VARIANT if DEFAULT_MODEL_VARIANT in AVAILABLE_MODELS else "auto"
SELECTED_MODEL_NAME = AVAILABLE_MODELS[_model_variant]

# --- 호환성을 위한 기존 변수 유지 ---
MODEL_PATHS = {"exaone": SELECTED_MODEL_NAME}

# === 출력 디렉토리 설정 ===
FINAL_OUTPUT_DIR = Path("final_output").resolve()
DATA_DIR = Path("data").resolve()

# === 메모리 관리 설정 ===
# 메모리 임계값 (GB) - 36GB 시스템에 맞게 조정
MEMORY_CRITICAL_THRESHOLD_GB = 4.0   # 4GB 미만 시 위험
MEMORY_WARNING_THRESHOLD_GB = 6.0    # 6GB 미만 시 경고  
MEMORY_SAFE_THRESHOLD_GB = 10.0      # 10GB 이상 시 안전

# --- Backward compatibility aliases (deprecated) ---
# 구명칭(MEMORY_*_THRESHOLD)으로 임포트하는 모듈 호환용
MEMORY_CRITICAL_THRESHOLD = MEMORY_CRITICAL_THRESHOLD_GB
MEMORY_WARNING_THRESHOLD  = MEMORY_WARNING_THRESHOLD_GB
MEMORY_SAFE_THRESHOLD     = MEMORY_SAFE_THRESHOLD_GB

# MLX 메모리 설정
MLX_MAX_MEMORY_GB = 20
MLX_CONTEXT_LENGTH = 4096

# === 생성 속도 최적화 설정 ===
# 토큰 수 제한 (80개 Q&A 생성을 위해 충분한 크기로 증가)
FAST_MAX_TOKENS = 12288     # 빠른 생성용 (80개 Q&A를 위해 대폭 증가)
NORMAL_MAX_TOKENS = 16384   # 일반 생성용 (더 여유있게)

# 빠른 생성을 위한 샘플링 설정
FAST_TEMPERATURE = 0.6      # 약간 올려서 다양성 확보 (기본: 0.7)
FAST_TOP_P = 0.85          # 약간 올려서 완전성 확보 (기본: 0.9)

# === 처리 설정 ===
# 파일 대기 시간 (초)
FILE_WAIT_TIMEOUT = 300   # 5분
FILE_CHECK_INTERVAL = 5   # 5초 간격

# 모델 처리 재시도 횟수
MAX_MODEL_ATTEMPTS = 3

# 파싱 결과 검증 설정
MIN_PARSED_QA_COUNT = 30  # 최소 파싱된 Q&A 개수
MAX_REGENERATION_ATTEMPTS = 2  # 최대 재생성 시도 횟수

# === 환경변수 설정 ===
MEMORY_OPTIMIZATION_ENV = {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0"
}
