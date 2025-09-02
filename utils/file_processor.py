#!/usr/bin/env python3
"""
파일 처리 유틸리티
- JSON 파일 로딩 및 저장
- JSONL 출력 생성
- 파일명 안전화
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from utils.common import load_json_safe, save_json_safe
from utils.logger import log_info, log_err, log_warn


class FileProcessor:
    """파일 처리 유틸리티 클래스"""
    
    def __init__(self):
        pass
    
    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """JSON 파일 로드"""
        return load_json_safe(file_path)
    
    def save_json_file(self, data: Any, file_path: Path) -> bool:
        """JSON 파일 저장"""
        return save_json_safe(data, file_path)




def sanitize_filename(name: str) -> str:
    """파일명 안전화"""
    s = re.sub(r'[<>:"/\\|?*]', "_", name or "Unknown")
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "Unknown"


def load_artwork_items_from_file(file_path: Path) -> Optional[List[Dict[str, Any]]]:
    """JSON 파일에서 작품 아이템 목록 로드 (통합 처리용)"""
    json_data = load_json_safe(file_path)
    if json_data is None:
        log_err(f"JSON 파일 로드 실패: {file_path}")
        return None
    
    # Case 1: API 응답 형식 - {"items": [...]}
    if isinstance(json_data, dict) and 'items' in json_data:
        items_list = json_data['items']
        if isinstance(items_list, list):
            log_info(f"✅ API 형식에서 {len(items_list)}개 작품 로드")
            return items_list
        else:
            log_err("'items' 키의 값이 리스트가 아님")
            return None
    
    # Case 2: 단일 작품 형식 - {...}
    elif isinstance(json_data, dict):
        log_info("단일 작품을 리스트로 변환")
        return [json_data]
    
    # Case 3: 직접 배열 형식 - [...]
    elif isinstance(json_data, list):
        log_info(f"✅ 배열 형식에서 {len(json_data)}개 작품 로드")
        return json_data
    
    else:
        log_err(f"지원되지 않는 JSON 구조: {type(json_data)}")
        return None


# 하위 호환성을 위한 별칭
load_artwork_items = load_artwork_items_from_file


def convert_raw_item_to_standard_artwork(raw_item: Dict[str, Any]) -> Dict[str, Any]:
    """API 응답 아이템을 표준 작품 데이터로 변환"""
    try:
        # artist_info JSON 문자열 파싱
        artist_metadata = {}
        raw_artist_info = raw_item.get('artist_info', '')
        if raw_artist_info:
            try:
                artist_metadata = json.loads(raw_artist_info)
            except json.JSONDecodeError:
                item_id = raw_item.get('id', 'Unknown')
                log_warn(f"artist_info JSON 파싱 실패 (ID: {item_id})")
        
        # 표준 작품 데이터 형식으로 변환
        standard_artwork = {
            # 작가 정보
            "성명": raw_item.get("artist_name", "Unknown"),
            "성명_영문": raw_item.get("artist_name_eng", ""),
            "국적": raw_item.get("nationality", ""),
            "출생년도": artist_metadata.get("birth", ""),
            
            # 작품 정보
            "작품명": raw_item.get("title", "Unknown"),
            "작품명_영문": raw_item.get("title_eng", ""),
            "크기": raw_item.get("size", ""),
            "무게": raw_item.get("weight", ""),
            "제작연도": raw_item.get("year", ""),
            "소재": raw_item.get("materials", ""),
            
            # 설명 및 노트
            "작가노트": raw_item.get("artist_note", ""),
            "작품설명": raw_item.get("description", ""),
            
            # 전시 및 수상 이력
            "전시이력": artist_metadata.get("exhibits", []),
            "수상이력": artist_metadata.get("awards", []),
            
            # 메타데이터 (디버깅용)
            "item_id": raw_item.get("id"),
            "item_no": raw_item.get("no")
        }
        
        return standard_artwork
        
    except Exception as e:
        item_id = raw_item.get("id", "Unknown")
        log_err(f"작품 형식 변환 실패 (ID: {item_id}): {e}")
        
        # 최소 필수 데이터로 폴백
        return {
            "성명": raw_item.get("artist_name", "Unknown"),
            "작품명": raw_item.get("title", "Unknown"), 
            "소재": raw_item.get("materials", "다양한 재료"),
            "item_id": raw_item.get("id"),
            "item_no": raw_item.get("no")
        }


# 하위 호환성을 위한 별칭
convert_item_to_artwork_format = convert_raw_item_to_standard_artwork


def create_jsonl_output(results: List[Dict[str, Any]], output_path: Path) -> bool:
    """JSONL 형식으로 결과 저장"""
    if not results:
        log_err("저장할 결과가 없습니다")
        return False
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in results:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        
        log_info(f"✅ JSONL 저장 완료: {output_path}")
        log_info(f"   총 {len(results)}개 항목")
        return True
        
    except Exception as e:
        log_err(f"JSONL 저장 실패: {e}")
        return False


def save_final_result(result: List[Dict[str, Any]], artwork: Dict[str, Any], all_results: list, output_dir: Path) -> bool:
    """최종 결과를 JSON 파일로 저장"""
    try:
        # 작가명과 작품명으로 파일명 생성
        artist_name = artwork.get("성명", "Unknown_Artist")
        artwork_title = artwork.get("작품명", "Unknown_Artwork")
        
        clean_artist = sanitize_filename(artist_name)
        clean_title = sanitize_filename(artwork_title)
        
        filename = f"{clean_artist}_{clean_title}.json"
        file_path = output_dir / filename
        
        # 디렉토리 생성
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 결과 저장
        if save_json_safe(result, file_path):
            all_results.append({
                'artist': artist_name,
                'artwork': artwork_title,
                'file_path': str(file_path),
                'result': result
            })
            
            log_info(f"✅ 결과 저장: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        log_err(f"결과 저장 실패: {e}")
        return False


def create_fallback_result(artwork: Dict[str, Any], error: str) -> str:
    """폴백 결과 생성 (파싱 실패 시)"""
    artist_name = artwork.get("성명", "Unknown")
    artwork_title = artwork.get("작품명", "Unknown")
    materials = artwork.get("소재", "다양한 재료")
    
    fallback_qa = {
        "instruction": f"'{artwork_title}' 작품에 대해 어떻게 생각하시나요?",
        "input": "",
        "output": f"{artist_name}의 '{artwork_title}'은 {materials}을 사용하여 독창적인 예술적 표현을 보여주는 작품입니다."
    }
    
    log_info(f"⚠️ 폴백 결과 생성: {error}")
    
    return json.dumps([fallback_qa], ensure_ascii=False, indent=2)