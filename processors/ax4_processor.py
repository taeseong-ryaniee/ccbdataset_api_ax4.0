#!/usr/bin/env python3
"""
A.X 4.0 API 프로세서 - CCB Dataset Transformer
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from utils.logger import setup_logger
from utils.file_processor import FileProcessor
from utils.common import load_json_file, ensure_directory, save_output_json, get_memory_info, check_memory_safety
from models.ax4_api_agent import generate_all_qa_batch
from config import (
    FINAL_OUTPUT_DIR, DATA_DIR, FILE_WAIT_TIMEOUT, FILE_CHECK_INTERVAL,
    MAX_MODEL_ATTEMPTS, MIN_PARSED_QA_COUNT, MAX_REGENERATION_ATTEMPTS
)


class AX4Processor:
    """A.X 4.0 API 기반 CCB Dataset 처리기"""
    
    def __init__(self, fast_mode: bool = True):
        """
        초기화
        
        Args:
            fast_mode: 고속 모드 여부 (기본: True)
        """
        self.fast_mode = fast_mode
        self.logger = setup_logger("AX4Processor")
        self.file_processor = FileProcessor()
        
        # 디렉토리 확인
        ensure_directory(FINAL_OUTPUT_DIR)
        ensure_directory(DATA_DIR)
        
        mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
        self.logger.info(f"AX4Processor 초기화 완료 ({mode_str})")
    
    def convert_item_to_artwork_format(self, raw_item: Dict) -> Dict:
        """원본 데이터 아이템을 작품 형식으로 변환"""
        try:
            # artist_info JSON 파싱
            artist_metadata = {}
            raw_artist_info = raw_item.get('artist_info', '')
            if raw_artist_info:
                try:
                    artist_metadata = json.loads(raw_artist_info)
                except json.JSONDecodeError:
                    self.logger.warning(f"artist_info JSON 파싱 실패")
            
            # 변환된 작품 데이터
            artwork = {
                "작가": raw_item.get("artist_name", "Unknown"),
                "영문작가명": raw_item.get("artist_name_eng", ""),
                "국적": raw_item.get("nationality", ""),
                "출생년도": artist_metadata.get("birth", ""),
                "제목": raw_item.get("title", "Unknown"),
                "영문제목": raw_item.get("title_eng", ""),
                "크기": raw_item.get("size", ""),
                "무게": raw_item.get("weight", ""),
                "제작년도": raw_item.get("year", ""),
                "재료": raw_item.get("materials", ""),
                "작가노트": raw_item.get("artist_note", ""),
                "작품설명": raw_item.get("description", ""),
                "전시이력": artist_metadata.get("exhibits", []),
                "수상이력": artist_metadata.get("awards", [])
            }
            
            return artwork
            
        except Exception as e:
            self.logger.error(f"데이터 변환 실패: {e}")
            # 최소 데이터로 폴백
            return {
                "작가": raw_item.get("artist_name", "Unknown"),
                "제목": raw_item.get("title", "Unknown"),
                "재료": raw_item.get("materials", "다양한 재료")
            }
    
    def sanitize_filename(self, filename: str) -> str:
        """파일명 안전화"""
        import re
        if not filename or filename == "Unknown":
            return "Unknown"
        
        # 특수문자 제거 및 공백을 언더스코어로 변경
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_name = re.sub(r'\s+', '_', safe_name)
        safe_name = safe_name.strip('_')
        
        return safe_name if safe_name else "Unknown"
    
    def process_artwork(self, artwork: Dict, output_filename: str) -> Optional[str]:
        """
        단일 작품 처리
        
        Args:
            artwork: 작품 정보 딕셔너리
            output_filename: 출력 파일명
        
        Returns:
            성공 시 출력 파일 경로, 실패 시 None
        """
        self.logger.info(f"📝 작품 처리 시작: {artwork.get('제목', 'Unknown')}")
        
        # 메모리 체크 (간소화)
        status, available, _ = check_memory_safety()
        if status != "SAFE":
            self.logger.warning(f"⚠️ 메모리 상태: {status} (사용가능: {available:.1f}GB)")
        
        # 기존 파일 확인 (이어서 생성 로직)
        output_path = FINAL_OUTPUT_DIR / output_filename
        existing_qa = []
        
        if output_path.exists():
            try:
                existing_data = load_json_file(output_path)
                if isinstance(existing_data, list):
                    existing_qa = existing_data
                    self.logger.info(f"   📂 기존 Q&A {len(existing_qa)}개 발견")
            except Exception as e:
                self.logger.warning(f"   ⚠️ 기존 파일 로드 실패: {e}")
        
        # Q&A 생성 시도
        success = False
        attempts = 0
        
        while not success and attempts < MAX_MODEL_ATTEMPTS:
            attempts += 1
            self.logger.info(f"   🎯 생성 시도 {attempts}/{MAX_MODEL_ATTEMPTS}")
            
            try:
                # A.X 4.0 API로 Q&A 생성
                qa_json = generate_all_qa_batch(
                    artwork=artwork,
                    fast_mode=self.fast_mode,
                    exclude_questions=existing_qa
                )
                
                # 파싱 및 검증
                generated_qa = json.loads(qa_json)
                
                if len(generated_qa) >= MIN_PARSED_QA_COUNT:
                    # 기존 Q&A와 결합
                    all_qa = existing_qa + generated_qa
                    
                    # 최종 출력 저장
                    save_output_json(all_qa, output_path)
                    
                    total_count = len(all_qa)
                    new_count = len(generated_qa)
                    
                    self.logger.info(f"   ✅ Q&A 생성 완료: 신규 {new_count}개, 총 {total_count}개")
                    success = True
                    
                    return str(output_path)
                
                else:
                    self.logger.warning(f"   ⚠️ 생성 부족: {len(generated_qa)}/{MIN_PARSED_QA_COUNT}개")
                    
            except Exception as e:
                self.logger.error(f"   ❌ 생성 실패 (시도 {attempts}): {e}")
                time.sleep(2)  # 잠시 대기 후 재시도
        
        self.logger.error(f"❌ 작품 처리 실패: {attempts}회 시도 후 포기")
        return None
    
    def process_file(self, json_file_path: Path) -> bool:
        """
        JSON 파일 처리
        
        Args:
            json_file_path: 처리할 JSON 파일 경로
        
        Returns:
            처리 성공 여부
        """
        self.logger.info(f"📁 파일 처리 시작: {json_file_path}")
        
        try:
            # JSON 파일 로드
            json_data = load_json_file(json_file_path)
            
            if not isinstance(json_data, dict):
                self.logger.error(f"   ❌ 잘못된 파일 형식: dict가 아님")
                return False
            
            # items 배열 추출
            if 'items' not in json_data:
                self.logger.error(f"   ❌ 'items' 키가 없습니다")
                return False
            
            items = json_data['items']
            if not isinstance(items, list):
                self.logger.error(f"   ❌ 'items'가 배열이 아닙니다")
                return False
            
            self.logger.info(f"   📋 처리할 작품 수: {len(items)}개")
            
            success_count = 0
            
            # 각 작품 개별 처리
            for i, raw_item in enumerate(items, 1):
                self.logger.info(f"\n   📝 [{i}/{len(items)}] 작품 처리 중...")
                
                # 데이터 형식 변환
                artwork = self.convert_item_to_artwork_format(raw_item)
                
                # 출력 파일명 생성 (작가명_작품명.json)
                artist_name = artwork.get('작가', 'Unknown')
                artwork_title = artwork.get('제목', 'Unknown')
                
                # 파일명 안전화
                safe_artist = self.sanitize_filename(artist_name)
                safe_title = self.sanitize_filename(artwork_title)
                output_filename = f"{safe_artist}_{safe_title}.json"
                
                # 작품 처리
                result_path = self.process_artwork(artwork, output_filename)
                
                if result_path:
                    self.logger.info(f"   ✅ 작품 처리 완료: {artist_name} - {artwork_title}")
                    success_count += 1
                else:
                    self.logger.error(f"   ❌ 작품 처리 실패: {artist_name} - {artwork_title}")
            
            self.logger.info(f"📊 파일 처리 결과: {success_count}/{len(items)}개 성공")
            return success_count > 0
                
        except Exception as e:
            self.logger.error(f"❌ 파일 처리 중 오류: {e}")
            return False
    
    def process_all_files(self) -> None:
        """모든 데이터 파일 처리"""
        self.logger.info("🚀 전체 파일 처리 시작")
        
        # data 디렉토리에서 JSON 파일 검색
        json_files = list(DATA_DIR.glob("*.json"))
        
        if not json_files:
            self.logger.warning(f"⚠️ 처리할 JSON 파일이 없습니다: {DATA_DIR}")
            return
        
        self.logger.info(f"📋 처리 대상 파일: {len(json_files)}개")
        
        success_count = 0
        
        for i, json_file in enumerate(json_files, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"📁 [{i}/{len(json_files)}] {json_file.name}")
            self.logger.info(f"{'='*60}")
            
            if self.process_file(json_file):
                success_count += 1
            
            # 간단한 메모리 정리
            import gc
            gc.collect()
        
        # 최종 결과 출력
        self.logger.info(f"\n🎉 전체 처리 완료")
        self.logger.info(f"   ✅ 성공: {success_count}/{len(json_files)}개")
        self.logger.info(f"   📁 출력 디렉토리: {FINAL_OUTPUT_DIR}")
        
        if success_count < len(json_files):
            failed_count = len(json_files) - success_count
            self.logger.warning(f"   ⚠️ 실패: {failed_count}개 파일")
    
    def get_processing_stats(self) -> Dict:
        """처리 통계 정보 반환"""
        stats = {
            "mode": "⚡ 고속 모드" if self.fast_mode else "🎯 정밀 모드",
            "api_provider": "A.X 4.0 API",
            "data_dir": str(DATA_DIR),
            "output_dir": str(FINAL_OUTPUT_DIR),
            "memory_status": get_memory_info()
        }
        return stats