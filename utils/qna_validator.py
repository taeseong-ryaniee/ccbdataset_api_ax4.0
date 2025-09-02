#!/usr/bin/env python3
"""
Q&A 데이터 검증 유틸리티
"""

from typing import List, Dict, Any, Optional

def validate_qna(qna_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Q&A 데이터 검증 및 정리"""
    if not qna_list:
        return []
    
    valid_items = []
    
    for item in qna_list:
        # 기본 유형 및 필드 검증
        if (not isinstance(item, dict) or 
            not item.get('instruction', '').strip() or 
            not item.get('output', '').strip()):
            continue
        
        instruction = item.get('instruction', '').strip()
        output = item.get('output', '').strip()
        
        # 최소 길이 검증
        if len(instruction) < 5 or len(output) < 10:
            continue
        
        # 유효한 항목 추가
        valid_items.append({
            'instruction': instruction,
            'input': item.get('input', '').strip(),
            'output': output
        })
    
    return valid_items

def validate_single_qna(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """단일 Q&A 항목 검증"""
    # 기본 유형 및 필드 검증
    if (not isinstance(item, dict) or 
        not item.get('instruction', '').strip() or 
        not item.get('output', '').strip()):
        return None
    
    instruction = item.get('instruction', '').strip()
    output = item.get('output', '').strip()
    
    # 최소 길이 검증
    if len(instruction) < 5 or len(output) < 10:
        return None
    
    # 유효한 항목 반환
    return {
        'instruction': instruction,
        'input': item.get('input', '').strip(),
        'output': output
    }