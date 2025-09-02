#!/usr/bin/env python3
"""
A.X 4.0 API 에이전트 - SKT A.X API 기반 Q&A 생성
"""

import json
import openai
from openai import OpenAI
from utils.json_parser import parse_model_output
from utils.prompt_loader import get_prompt_loader
from utils.qna_validator import validate_qna


# A.X 4.0 API 설정
AX4_API_BASE_URL = "https://guest-api.sktax.chat/v1"
AX4_API_KEY = "sktax-XyeKFrq67ZjS4EpsDlrHHXV8it"
AX4_MODEL = "ax4"

# 전역 클라이언트 변수 (지연 로딩)
_client = None


def get_ax4_client():
    """A.X 4.0 API 클라이언트 가져오기 (지연 로딩)"""
    global _client
    
    if _client is None:
        try:
            print("A.X 4.0 API 클라이언트 초기화 중...")
            _client = OpenAI(
                base_url=AX4_API_BASE_URL,
                api_key=AX4_API_KEY
            )
            print("✅ A.X 4.0 API 클라이언트 초기화 완료")
        except Exception as e:
            print(f"❌ A.X 4.0 API 클라이언트 초기화 실패: {e}")
            raise
    
    return _client


def generate_with_ax4_api(prompt: str, max_tokens: int = 12288, temperature: float = 0.7, max_retries: int = 5) -> str:
    """A.X 4.0 API를 사용하여 텍스트 생성 (재시도 로직 포함)"""
    import time
    import random
    
    client = get_ax4_client()
    
    for attempt in range(max_retries):
        try:
            # 지수 백오프와 지터 적용
            if attempt > 0:
                backoff_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"   ⏳ {backoff_time:.1f}초 대기 후 재시도...")
                time.sleep(backoff_time)
            
            print(f"   🔄 API 호출 시도 {attempt + 1}/{max_retries}")
            
            response = client.chat.completions.create(
                model=AX4_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=60.0  # 60초 타임아웃 설정
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ API 호출 실패 (시도 {attempt + 1}): {error_msg[:100]}")
            
            # 마지막 시도였다면 예외를 그대로 raise
            if attempt == max_retries - 1:
                raise e
            
            # 타임아웃이나 서버 오류인 경우 재시도
            if any(keyword in error_msg.lower() for keyword in 
                   ['timeout', 'timed out', '504', '502', '503', 'gateway', 'server error', 'request timeout']):
                print(f"   🔄 타임아웃/서버 오류 감지 - 재시도 예정")
                continue
            else:
                # 진짜 클라이언트 오류 (4xx, 인증 오류 등)는 재시도하지 않음
                if any(keyword in error_msg.lower() for keyword in ['401', '403', '400', 'unauthorized', 'forbidden']):
                    print(f"   ❌ 클라이언트 오류 - 재시도 중단")
                    raise e
                else:
                    # 확실하지 않은 오류는 재시도
                    print(f"   🔄 알 수 없는 오류 - 재시도 예정")
                    continue


def generate_artwork_questions_visitor_batch(artwork: dict, fast_mode: bool = True, exclude_instructions: set = None, batch_size: int = 10) -> list:
    """작품에 관한 질문 - 일반 관람객 관점 (배치 크기 조정 가능)"""
    
    prompt_loader = get_prompt_loader()
    
    # 배치 크기에 맞춰 프롬프트 조정
    original_prompt = prompt_loader.format_visitor_prompt(artwork, exclude_instructions)
    adjusted_prompt = original_prompt.replace("30개", f"{batch_size}개")
    
    print(f"   📝 일반 관람객 프롬프트 생성 완료 ({len(adjusted_prompt)} 문자, {batch_size}개 목표)")
    
    # API 최적화 설정 (배치 크기에 따라 토큰 수 조정) - 더 보수적으로
    max_tokens = min(4000, batch_size * 250)  # 배치당 약 250토큰 (더 작게)
    temperature = 0.7 if fast_mode else 0.8
    mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
    print(f"   {mode_str} (max_tokens: {max_tokens})")
    
    response = generate_with_ax4_api(
        prompt=adjusted_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        max_retries=4  # 배치 처리 시 충분한 재시도
    )
    
    parsed_result = parse_model_output(response, "AX4_API_Visitor_Batch")
    if parsed_result and isinstance(parsed_result, list):
        if len(parsed_result) < batch_size // 2:  # 목표의 절반 이상
            print(f"   ⚠️ 생성 부족: {len(parsed_result)}/{batch_size}개")
        return parsed_result
    return []


def generate_artwork_questions_visitor(artwork: dict, fast_mode: bool = True, exclude_instructions: set = None) -> list:
    """작품에 관한 질문 - 일반 관람객 관점 (30개)"""
    
    prompt_loader = get_prompt_loader()
    prompt = prompt_loader.format_visitor_prompt(artwork, exclude_instructions)
    
    print(f"   📝 일반 관람객 프롬프트 생성 완료 ({len(prompt)} 문자)")
    
    # API 최적화 설정
    max_tokens = 12288 if fast_mode else 16384
    temperature = 0.7 if fast_mode else 0.8
    mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
    print(f"   {mode_str}")
    
    response = generate_with_ax4_api(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    parsed_result = parse_model_output(response, "AX4_API_Visitor")
    if parsed_result and isinstance(parsed_result, list):
        if len(parsed_result) < 20:  # 30개 목표 중 최소 20개는 있어야 함
            print(f"   ⚠️ 생성 부족: {len(parsed_result)}/30개 - 재시도 권장")
        return parsed_result
    return []


def generate_artwork_questions_curator_batch(artwork: dict, fast_mode: bool = True, exclude_instructions: set = None, batch_size: int = 10) -> list:
    """작품에 관한 질문 - 큐레이터/공예이론가 관점 (배치 크기 조정 가능)"""
    
    prompt_loader = get_prompt_loader()
    
    # 배치 크기에 맞춰 프롬프트 조정
    original_prompt = prompt_loader.format_curator_artwork_prompt(artwork, exclude_instructions)
    adjusted_prompt = original_prompt.replace("30개", f"{batch_size}개")
    
    print(f"   📝 큐레이터 작품 프롬프트 생성 완료 ({len(adjusted_prompt)} 문자, {batch_size}개 목표)")
    
    # API 최적화 설정 (배치 크기에 따라 토큰 수 조정) - 더 보수적으로
    max_tokens = min(4000, batch_size * 250)  # 배치당 약 250토큰 (더 작게)
    temperature = 0.7 if fast_mode else 0.8
    mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
    print(f"   {mode_str} (max_tokens: {max_tokens})")
    
    response = generate_with_ax4_api(
        prompt=adjusted_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        max_retries=4  # 배치 처리 시 충분한 재시도
    )
    
    parsed_result = parse_model_output(response, "AX4_API_Curator_Batch")
    if parsed_result and isinstance(parsed_result, list):
        if len(parsed_result) < batch_size // 2:  # 목표의 절반 이상
            print(f"   ⚠️ 생성 부족: {len(parsed_result)}/{batch_size}개")
        return parsed_result
    return []


def generate_artwork_questions_curator(artwork: dict, fast_mode: bool = True, exclude_instructions: set = None) -> list:
    """작품에 관한 질문 - 큐레이터/공예이론가 관점 (30개)"""
    
    prompt_loader = get_prompt_loader()
    prompt = prompt_loader.format_curator_artwork_prompt(artwork, exclude_instructions)
    
    print(f"   📝 큐레이터 작품 프롬프트 생성 완료 ({len(prompt)} 문자)")
    
    # API 최적화 설정
    max_tokens = 12288 if fast_mode else 16384
    temperature = 0.7 if fast_mode else 0.8
    mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
    print(f"   {mode_str}")
    
    response = generate_with_ax4_api(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    parsed_result = parse_model_output(response, "AX4_API_Curator")
    if parsed_result and isinstance(parsed_result, list):
        if len(parsed_result) < 20:  # 30개 목표 중 최소 20개는 있어야 함
            print(f"   ⚠️ 생성 부족: {len(parsed_result)}/30개 - 재시도 권장")
        return parsed_result
    return []


def generate_artist_questions_curator_batch(artwork: dict, fast_mode: bool = True, exclude_instructions: set = None, batch_size: int = 10) -> list:
    """작가에 대한 질문 - 큐레이터/공예이론가 관점 (배치 크기 조정 가능)"""
    
    prompt_loader = get_prompt_loader()
    
    # 배치 크기에 맞춰 프롬프트 조정
    original_prompt = prompt_loader.format_curator_artist_prompt(artwork, exclude_instructions)
    adjusted_prompt = original_prompt.replace("20개", f"{batch_size}개")
    
    print(f"   📝 큐레이터 작가 프롬프트 생성 완료 ({len(adjusted_prompt)} 문자, {batch_size}개 목표)")
    
    # 배치 크기에 따라 토큰 수 조정 (작가 질문은 좀 더 길 수 있음) - 보수적으로
    max_tokens = min(5000, batch_size * 300)  # 배치당 약 300토큰 (더 작게)
    temperature = 0.8  # 작가 질문은 좀 더 다양성 필요
    print(f"   🎯 작가 관점 모드 (max_tokens: {max_tokens})")
    
    response = generate_with_ax4_api(
        prompt=adjusted_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        max_retries=4  # 배치 처리 시 충분한 재시도
    )
    
    parsed_result = parse_model_output(response, "AX4_API_Artist_Batch")
    if parsed_result and isinstance(parsed_result, list):
        if len(parsed_result) < batch_size // 2:  # 목표의 절반 이상
            print(f"   ⚠️ 생성 부족: {len(parsed_result)}/{batch_size}개")
        return parsed_result
    return []


def generate_artist_questions_curator(artwork: dict, fast_mode: bool = True, exclude_instructions: set = None) -> list:
    """작가에 대한 질문 - 큐레이터/공예이론가 관점 (20개)"""
    
    prompt_loader = get_prompt_loader()
    prompt = prompt_loader.format_curator_artist_prompt(artwork, exclude_instructions)
    
    print(f"   📝 큐레이터 작가 프롬프트 생성 완료 ({len(prompt)} 문자)")
    
    # 고품질 모드 강제 적용 (20개 완전 생성을 위해)
    max_tokens = 16384  # 충분한 토큰 할당
    temperature = 0.8  # 더 높은 다양성과 완성도
    print("   🎯 고품질 모드 활성화 (20개 완전 생성)")
    
    response = generate_with_ax4_api(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    parsed_result = parse_model_output(response, "AX4_API_Artist")
    if parsed_result and isinstance(parsed_result, list):
        if len(parsed_result) < 15:  # 20개 목표 중 최소 15개는 있어야 함
            print(f"   ⚠️ 생성 부족: {len(parsed_result)}/20개 - 재시도 권장")
        return parsed_result
    return []


def generate_all_qa_batch(artwork: dict, fast_mode: bool = True, exclude_questions: list = None) -> str:
    """모든 유형의 Q&A를 배치로 생성 (타임아웃 방지를 위한 순차 처리)"""
    import time
    
    mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
    print(f"   📊 {mode_str}로 Q&A 생성 시작 (순차 처리)")
    
    # 기존 질문 정보 처리
    exclude_instructions = set()
    if exclude_questions:
        for q in exclude_questions:
            instruction = q.get('instruction', '').strip().lower()
            exclude_instructions.add(instruction)
        print(f"   ⚠️ 제외할 기존 질문: {len(exclude_instructions)}개")
    
    all_qa = []
    
    # 더 작은 배치로 세분화 (10개씩 8단계)
    batches = [
        ("일반 관람객 1차", "visitor", 10),
        ("일반 관람객 2차", "visitor", 10), 
        ("일반 관람객 3차", "visitor", 10),
        ("큐레이터 작품 1차", "curator_artwork", 10),
        ("큐레이터 작품 2차", "curator_artwork", 10),
        ("큐레이터 작품 3차", "curator_artwork", 10),
        ("큐레이터 작가 1차", "curator_artist", 10),
        ("큐레이터 작가 2차", "curator_artist", 10),
    ]
    
    for i, (batch_name, batch_type, batch_size) in enumerate(batches, 1):
        print(f"   📝 [{i}/8] {batch_name} 질문 생성 중... ({batch_size}개)")
        try:
            if batch_type == "visitor":
                qa_batch = generate_artwork_questions_visitor_batch(artwork, fast_mode, exclude_instructions, batch_size=batch_size)
            elif batch_type == "curator_artwork":
                qa_batch = generate_artwork_questions_curator_batch(artwork, fast_mode, exclude_instructions, batch_size=batch_size)
            else:  # curator_artist
                qa_batch = generate_artist_questions_curator_batch(artwork, fast_mode, exclude_instructions, batch_size=batch_size)
            
            print(f"   ✅ {batch_name}: {len(qa_batch)}개 생성")
            all_qa.extend(qa_batch)
            
            # 배치 간 더 긴 대기시간
            if i < len(batches):  # 마지막 배치가 아니면
                print(f"   ⏳ 다음 배치까지 3초 대기...")
                time.sleep(3)
                
        except Exception as e:
            print(f"   ⚠️ {batch_name} 생성 실패: {e}")
            # 실패해도 계속 진행
    
    total_count = len(all_qa)
    print(f"   📊 총 생성된 Q&A: {total_count}개")
    
    if total_count < 50:  # 최소 기준을 낮춤 (타임아웃으로 인한 부분 실패 고려)
        print(f"   ⚠️ 생성된 Q&A가 부족합니다: {total_count}/80개 (목표)")
    
    # 결과를 검증하고 반환
    validated_items = validate_qna(all_qa)
    
    print(f"   ✅ 검증 완료: {len(validated_items)}개 유효한 Q&A")
    return json.dumps(validated_items, ensure_ascii=False, indent=2)


# 기존 함수들과의 호환성을 위한 wrapper
def generate_qa_batch(model_tokenizer_tuple, artwork: dict) -> str:
    """배치 처리용 wrapper 함수 (API에서는 model_tokenizer_tuple 불필요)"""
    return generate_all_qa_batch(artwork)


def generate_qa_directly(artwork: dict) -> str:
    """API를 직접 사용해서 Q&A 생성"""
    return generate_all_qa_batch(artwork)