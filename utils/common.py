#!/usr/bin/env python3
"""
공통 유틸리티 함수들 (A.X 4.0 API 전용)
- API 기반 Q&A 생성을 위한 간소화된 유틸리티
"""

import os
import json
import gc
import time
import signal
import sys
import psutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Callable, List

from config import (
    FILE_WAIT_TIMEOUT, FILE_CHECK_INTERVAL, MAX_MODEL_ATTEMPTS
)


def get_memory_info() -> Dict[str, float]:
    """메모리 정보 반환 (GB 단위)"""
    memory = psutil.virtual_memory()
    return {
        "total": memory.total / (1024**3),
        "available": memory.available / (1024**3), 
        "used": memory.used / (1024**3),
        "percent": memory.percent
    }


def check_memory_safety() -> Tuple[str, float, float]:
    """메모리 안전성 검사 (간소화)"""
    memory_info = get_memory_info()
    available = memory_info["available"]
    current_usage = memory_info["used"]
    
    if available < 2.0:  # 2GB 미만
        return "CRITICAL", available, current_usage
    elif available < 4.0:  # 4GB 미만
        return "WARNING", available, current_usage
    else:
        return "SAFE", available, current_usage


def force_cleanup():
    """강제 메모리 정리 (간소화)"""
    try:
        gc.collect()
        time.sleep(0.1)
    except Exception:
        pass


def setup_signal_handlers(cleanup_func: Optional[Callable] = None):
    """시그널 핸들러 설정"""
    def cleanup_handler(signum, _):
        print(f"\n⚠️ 시그널 {signum} 수신 - 정리 중...")
        if cleanup_func:
            cleanup_func()
        else:
            force_cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)


def wait_for_file(file_path: Path, timeout: int = FILE_WAIT_TIMEOUT) -> bool:
    """파일 생성 대기 (완전 쓰기 확인 포함)"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if file_path.exists():
            try:
                # 파일 크기 확인
                file_size = file_path.stat().st_size
                
                if file_size > 100:  # 최소 크기 체크
                    # 1초 더 대기 후 크기 재확인 (쓰기 완료 확인)
                    time.sleep(1)
                    if file_path.stat().st_size == file_size:
                        return True
            except (OSError, PermissionError):
                pass
        
        base_name = file_path.stem
        print(f"⏳ {base_name} 파일 대기 중... ({int(time.time() - start_time)}초)")
        time.sleep(FILE_CHECK_INTERVAL)  # 설정된 간격으로 체크
    
    return file_path.exists()


def load_json_safe(file_path: Path) -> Optional[Dict[str, Any]]:
    """안전한 JSON 파일 로드"""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"   ❌ JSON 파일 로드 실패 ({file_path.name}): {e}")
        return None


def save_json_safe(data: Any, file_path: Path) -> bool:
    """안전한 JSON 파일 저장"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, str):
            # 이미 JSON 문자열인 경우
            with open(file_path, "w", encoding="utf-8-sig") as f:
                f.write(data)
        else:
            # 객체인 경우
            with open(file_path, "w", encoding="utf-8-sig") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"   ❌ JSON 파일 저장 실패 ({file_path.name}): {e}")
        return False


def print_progress(current: int, total: int, item_name: str = ""):
    """진행률 출력"""
    progress = (current + 1) / total * 100
    if item_name:
        print(f"📊 진행률: {progress:.1f}% ({current+1}/{total}) - {item_name}")
    else:
        print(f"📊 진행률: {progress:.1f}% ({current+1}/{total})")


def ensure_directory(directory: Path):
    """디렉토리 존재 확인 및 생성"""
    directory.mkdir(parents=True, exist_ok=True)


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """JSON 파일 로드 (호환성 함수)"""
    return load_json_safe(file_path)


def save_output_json(data: Any, file_path: Path) -> bool:
    """출력 JSON 저장 (호환성 함수)"""
    return save_json_safe(data, file_path)


class ProcessorBase:
    """프로세서 베이스 클래스 - API 전용 간소화 버전"""
    
    def __init__(self, name: str):
        self.name = name
        self.processed_count = 0
        self.failed_count = 0
        self.success_count = 0
        
        # 시그널 핸들러만 설정
        setup_signal_handlers()
    
    @staticmethod
    def check_memory_and_exit_if_critical() -> bool:
        """메모리 확인 및 위험 시 종료 (간소화)"""
        status, available, _ = check_memory_safety()
        if status == "CRITICAL":
            print("⛔ 메모리 부족으로 처리 중단")
            return True
        return False
    
    def print_summary(self, elapsed_time: float):
        """처리 요약 출력"""
        print("\n" + "="*60)
        print(f"📊 {self.name} 처리 완료!")
        print(f"✅ 처리된 파일: {self.processed_count}개")
        print(f"❌ 실패한 파일: {self.failed_count}개")
        print(f"🔥 {self.name} 성공: {self.success_count}개")
        print(f"⏱️ 소요 시간: {elapsed_time/60:.1f}분")
    
    @staticmethod
    def get_json_files(data_dir: Path) -> List[Path]:
        """JSON 파일 목록 가져오기"""
        json_files = list(data_dir.glob("*.json"))
        if not json_files:
            print("❌ 처리할 JSON 파일이 없습니다.")
            return []
        
        print(f"🔍 발견된 파일: {len(json_files)}개")
        return json_files