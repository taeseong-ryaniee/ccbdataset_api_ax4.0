#!/usr/bin/env python3
"""
강력한 JSON 파싱 유틸리티 - 모든 파싱 문제를 해결하는 통합 솔루션
"""

import json
import re
from typing import List, Dict, Any

def clean_json_string(text: str) -> str:
    """JSON 문자열을 정리하여 파싱 가능하게 만듭니다"""
    
    # 1. 기본 정리
    text = text.strip()
    
    # 2. 예시 부분 제거 (예시:, Example:, 예제: 등으로 시작하는 부분)
    example_patterns = [
        r'예시:\s*```json.*?```',
        r'Example:\s*```json.*?```',
        r'예제:\s*```json.*?```',
        r'예시:\s*\[.*?\]',
        r'Example:\s*\[.*?\]'
    ]
    
    for pattern in example_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 3. 코드 블록 처리 - 마지막 JSON 배열만 추출
    json_blocks = []
    if "```json" in text.lower():
        # 모든 ```json 블록 찾기
        blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
        json_blocks.extend(blocks)
    elif "```" in text:
        # 일반 코드 블록에서 JSON 찾기
        blocks = re.findall(r'```\s*(.*?)\s*```', text, re.DOTALL)
        for block in blocks:
            if block.strip().startswith('[') or block.strip().startswith('{'):
                json_blocks.append(block)
    
    # 가장 큰(완전한) JSON 블록 선택
    if json_blocks:
        # 가장 긴 블록을 선택 (일반적으로 완전한 출력)
        text = max(json_blocks, key=len).strip()
    
    # 4. ### 요청, ### 지시사항 등의 프롬프트 부분 제거
    prompt_patterns = [
        r'###.*?(?=\[)',
        r'\*\*.*?\*\*',
        r'필수.*?(?=\[)',
        r'요청.*?(?=\[)',
        r'지시.*?(?=\[)',
    ]
    
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # 5. JSON 배열 영역만 추출 (가장 완전한 배열 선택)
    json_arrays = re.findall(r'\[.*?]', text, re.DOTALL)
    if json_arrays:
        # 가장 긴 JSON 배열 선택 (완전한 출력일 가능성이 높음)
        text = max(json_arrays, key=len)
    
    # 6. 불완전한 JSON 보정
    text = text.strip()
    if text.startswith('[') and not text.endswith(']'):
        text += ']'
    if text.startswith('{') and not text.endswith('}'):
        text += '}'
    
    return text

def fix_json_structure(text: str) -> str:
    """JSON 구조적 문제를 수정합니다"""
    
    # 1. 잘못된 필드 구조 수정 (예: "input": "..." 대신 "output": "...")
    # 중복되거나 잘못된 input 필드 패턴 수정
    text = re.sub(
        r'"input":\s*"([^"]*(?:\\.[^"]*)*)",\s*"input":', 
        '"input": "",\n    "output":', 
        text
    )
    
    # 2. 불완전한 객체 시작 수정 (예: {"," -> {)
    text = re.sub(r'\{\s*",', '{', text)
    
    # 3. 미완성된 문자열 닫기
    quote_count = text.count('"')
    if quote_count % 2 == 1:
        text += '"'
    
    # 4. 미완성된 객체/배열 닫기
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    
    text += '}' * open_braces
    text += ']' * open_brackets
    
    # 5. 마지막 콤마 제거
    text = re.sub(r',\s*([}\]])', r'\1', text)
    
    # 6. 연속 콤마 제거
    text = re.sub(r',\s*,+', ',', text)
    
    # 7. 빈 객체 제거
    text = re.sub(r'\{\s*}', '', text)
    text = re.sub(r',\s*,', ',', text)
    
    return text

def extract_complete_objects(text: str) -> List[str]:
    """완전한 JSON 객체들만 추출합니다"""
    
    # instruction과 output 필드가 모두 있는 완전한 객체 패턴
    pattern = (
        r'\{\s*"instruction"\s*:\s*"([^"]*(?:\\"[^"]*)*)"\s*,'
        r'\s*"input"\s*:\s*"([^"]*(?:\\"[^"]*)*)"\s*,'
        r'\s*"output"\s*:\s*"([^"]*(?:\\"[^"]*)*)"\s*\}'
    )
    
    objects = []
    for match in re.finditer(pattern, text, re.DOTALL):
        instruction = match.group(1).replace('\\"', '"')
        input_field = match.group(2).replace('\\"', '"')
        output = match.group(3).replace('\\"', '"')
        
        # 완전한 객체 생성
        obj = {
            "instruction": instruction,
            "input": input_field,
            "output": output
        }
        
        # JSON 유효성 검사
        try:
            json.dumps(obj)
            objects.append(json.dumps(obj, ensure_ascii=False))
        except (TypeError, ValueError) as e:
            continue
    
    return objects

def _validate_json_item(item: Dict[str, Any]) -> bool:
    """JSON 아이템이 유효한지 검사"""
    has_instruction = 'instruction' in item and 'output' in item
    has_question = 'question' in item and 'answer' in item
    return has_instruction or has_question

def _try_basic_json_parse(text: str) -> List[Dict[str, Any]]:
    """기본 JSON 파싱 시도"""
    clean_text = clean_json_string(text)
    parsed = json.loads(clean_text)
    
    if isinstance(parsed, list):
        valid_items = []
        for item in parsed:
            if isinstance(item, dict) and _validate_json_item(item):
                valid_items.append(item)
        return valid_items
    elif isinstance(parsed, dict) and _validate_json_item(parsed):
        return [parsed]
    
    return []

def smart_json_parse(text: str) -> List[Dict[str, Any]]:
    """스마트 JSON 파싱 - 모든 경우를 처리합니다"""
    
    if not text or not text.strip():
        return []
    
    # 1단계: 기본 JSON 파싱 시도
    try:
        result = _try_basic_json_parse(text)
        if result:
            return result
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"🔍 1단계 파싱 실패: {e}")
    
    # 2단계: 불완전한 JSON 수정 후 재시도
    try:
        clean_text = clean_json_string(text)
        # 불완전한 마지막 객체 제거
        clean_text = remove_incomplete_last_object(clean_text)
        fixed_text = fix_json_structure(clean_text)
        parsed = json.loads(fixed_text)
        if isinstance(parsed, list):
            valid_items = []
            for item in parsed:
                if isinstance(item, dict):
                    has_instruction = 'instruction' in item and 'output' in item
                    has_question = 'question' in item and 'answer' in item
                    if has_instruction or has_question:
                        valid_items.append(item)
            return valid_items
    except (json.JSONDecodeError, ValueError) as e:
        print(f"🔍 2단계 파싱 실패: {e}")
    
    # 3단계: 완전한 객체들만 추출
    try:
        object_strings = extract_complete_objects(text)
        if object_strings:
            array_text = '[' + ','.join(object_strings) + ']'
            parsed = json.loads(array_text)
            return parsed
    except (json.JSONDecodeError, ValueError) as e:
        print(f"🔍 3단계 파싱 실패: {e}")
    
    # 4단계: 정규식으로 필드별 추출
    try:
        results = []
        
        # 더 유연한 패턴들
        patterns = [
            # 완전한 객체 패턴 (input 필드 포함)
            r'"instruction"\s*:\s*"([^"]*(?:\\.[^"]*)*)"\s*,\s*"input"\s*:\s*"([^"]*(?:\\.[^"]*)*)"\s*,\s*"output"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
            # instruction과 output만 있는 패턴
            r'"instruction"\s*:\s*"([^"]*(?:\\.[^"]*)*)"\s*.*?"output"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
            # question과 answer 패턴 (Gemma용)
            r'"question"\s*:\s*"([^"]*(?:\\.[^"]*)*)"\s*.*?"answer"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
            # 줄바꿈이 있는 패턴
            r'"instruction"\s*:\s*"([^"]*(?:\\.[^"]*)*)"[\s\S]*?"output"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
            # 간단한 패턴 - instruction/output
            r'instruction[^"]*"([^"]*(?:\\.[^"]*)*)"[^"]*output[^"]*"([^"]*(?:\\.[^"]*)*)"',
            # 간단한 패턴 - question/answer  
            r'question[^"]*"([^"]*(?:\\.[^"]*)*)"[^"]*answer[^"]*"([^"]*(?:\\.[^"]*)*)"'
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                if len(match) == 3:  # 완전한 객체 (instruction, input, output)
                    result = {
                        "instruction": match[0].replace('\\"', '"').strip(),
                        "input": match[1].replace('\\"', '"').strip(),
                        "output": match[2].replace('\\"', '"').strip()
                    }
                    results.append(result)
                elif len(match) == 2:  # instruction/output 또는 question/answer
                    if i == 2 or i == 5:  # question/answer 패턴
                        result = {
                            "question": match[0].replace('\\"', '"').strip(),
                            "answer": match[1].replace('\\"', '"').strip()
                        }
                    else:  # instruction/output 패턴
                        result = {
                            "instruction": match[0].replace('\\"', '"').strip(),
                            "input": "",
                            "output": match[1].replace('\\"', '"').strip()
                        }
                    results.append(result)
            
            if results:
                break
        
        print(f"🔍 4단계 정규식 파싱 결과: {len(results)}개 항목 추출")
        return results[:10]  # 최대 10개로 제한
    
    except (re.error, ValueError, IndexError) as e:
        print(f"🔍 4단계 파싱 실패: {e}")
    
    return []

def remove_incomplete_last_object(text: str) -> str:
    """불완전한 마지막 객체를 제거합니다"""
    try:
        # 마지막 완전한 }를 찾습니다
        last_complete_brace = text.rfind('}')
        if last_complete_brace == -1:
            return text
        
        # } 이후에 ]가 있는지 확인
        remaining = text[last_complete_brace + 1:].strip()
        if remaining.startswith(','):
            # 마지막 }에서 콤마 제거하고 ] 추가
            text = text[:last_complete_brace + 1] + ']'
        elif not remaining or remaining == ']':
            # 이미 완전함
            return text
        else:
            # 불완전한 객체가 있으므로 마지막 완전한 }에서 자름
            text = text[:last_complete_brace + 1] + ']'
        
        return text
    except (ValueError, IndexError):
        return text

def parse_model_output(text: str, model_name: str = "Unknown") -> List[Dict[str, Any]]:
    """모델 출력을 안전하게 파싱하는 메인 함수"""

    print(f"🔄 {model_name} 출력 파싱 시작...")
    
    if not text:
        print(f"❌ {model_name}: 빈 출력")
        return []
    
    # 디버깅: 원본 텍스트 정보
    print(f"🔍 원본 텍스트 길이: {len(text)} 문자")
    print(f"🔍 코드 블록 여부: {'```' in text}")
    print(f"🔍 JSON 배열 여부: '[' in text and ']' in text = {('[' in text and ']' in text)}")
    
    # 스마트 파싱 실행
    parsed_items = smart_json_parse(text)
    
    if not parsed_items:
        print(f"❌ {model_name}: 파싱 실패")
        print(f"🔍 정리된 텍스트 미리보기:")
        cleaned = clean_json_string(text)
        print(f"   정리 후: {cleaned[:300]}...")
        return []
    
    # 검증 및 수정
    final_items = []
    for item in parsed_items:
        # Gemma의 question/answer 형식도 처리
        if isinstance(item, dict):
            if 'question' in item and 'answer' in item:
                # question/answer를 instruction/output으로 변환
                final_items.append({
                    'instruction': item['question'],
                    'input': '',
                    'output': item['answer']
                })
            elif 'instruction' in item and 'output' in item:
                if 'input' not in item:
                    item['input'] = ""
                final_items.append(item)

    if not final_items:
        print(f"❌ {model_name}: 유효한 항목 없음 (필수 필드 누락)")
        print(f"🔍 파싱된 항목 형식 확인:")
        for i, item in enumerate(parsed_items[:3]):
            keys = list(item.keys()) if isinstance(item, dict) else ["invalid_type"]
            print(f"   항목 {i+1}: {keys}")
        return []
    
    print(f"✅ {model_name}: {len(final_items)}개 항목 파싱 성공")
    
    # 결과 요약 출력
    for i, item in enumerate(final_items[:3]):  # 처음 3개만 미리보기
        word_count = len(item['output'].split())
        print(f"   항목 {i+1}: {item['instruction'][:30]}... ({word_count}단어)")
    
    return final_items

def create_fallback_questions(artwork_info: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
    """파싱 실패 시 기본 질문들을 생성합니다"""
    
    artwork_title = artwork_info.get("작품명", "이 작품")
    artist_name = artwork_info.get("성명", "작가")
    materials = artwork_info.get("소재", "다양한 재료")
    
    fallback_questions = [
        {
            "instruction": f"'{artwork_title}'에 대한 첫 인상은 어떠세요?",
            "input": "",
            "output": f"{materials}의 독특한 조합이 시각적으로 매우 인상적이고 감동적입니다."
        },
        {
            "instruction": f"이 작품에 사용된 재료의 특징은 무엇인가요?",
            "input": "",
            "output": f"{materials}가 작품의 의미와 미적 가치를 효과적으로 표현하고 있습니다."
        },
        {
            "instruction": f"{artist_name}의 작품 세계는 어떻게 평가하시나요?",
            "input": "",
            "output": f"{artist_name}은 전통과 현대를 조화롭게 결합한 독창적 작업을 보여줍니다."
        },
        {
            "instruction": f"이 작품이 전달하는 메시지는 무엇일까요?",
            "input": "",
            "output": f"문화적 정체성과 예술적 표현이 조화롭게 어우러진 깊이 있는 작품입니다."
        },
        {
            "instruction": f"관람객에게 어떤 감정을 불러일으키나요?",
            "input": "",
            "output": f"작품의 정교함과 의미가 관람객에게 깊은 감동과 사색을 제공합니다."
        }
    ]
    
    return fallback_questions[:count]
