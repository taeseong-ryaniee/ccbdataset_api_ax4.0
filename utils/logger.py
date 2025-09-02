#!/usr/bin/env python3
"""
공통 로깅 유틸리티 (A.X 4.0 API 전용)
"""

import logging
from typing import Optional


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """로거 설정 및 반환"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # 중복 핸들러 방지
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger


def log_info(msg: str) -> None:
    """정보 로그 출력"""
    print(f"ℹ️ {msg}")


def log_warn(msg: str) -> None:
    """경고 로그 출력"""
    print(f"⚠️ Warning: {msg}")


def log_err(msg: str) -> None:
    """에러 로그 출력"""
    print(f"❌ Error: {msg}")


def log_success(msg: str) -> None:
    """성공 로그 출력"""
    print(f"✅ {msg}")