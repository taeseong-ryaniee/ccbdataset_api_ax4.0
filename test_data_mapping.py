#!/usr/bin/env python3
"""
데이터 매핑 테스트 - N/A 문제 해결 확인
"""

import json
from pathlib import Path
from processors.ax4_processor import AX4Processor
from utils.common import load_json_safe

def test_data_conversion():
    """데이터 변환 테스트"""
    print("🧪 데이터 변환 테스트")
    print("=" * 50)
    
    # 테스트 데이터 로드
    data_file = Path("data/items_202509011603.json")
    if not data_file.exists():
        print("❌ 테스트 데이터 파일이 없습니다")
        return False
    
    json_data = load_json_safe(data_file)
    if not json_data or 'items' not in json_data:
        print("❌ 잘못된 데이터 형식")
        return False
    
    # 첫 번째 아이템으로 테스트
    first_item = json_data['items'][0]
    
    print("📋 원본 데이터:")
    print(f"  artist_name: {first_item.get('artist_name')}")
    print(f"  title: {first_item.get('title')}")
    print(f"  materials: {first_item.get('materials')}")
    
    # 프로세서로 변환
    processor = AX4Processor()
    converted = processor.convert_item_to_artwork_format(first_item)
    
    print("\n📋 변환된 데이터:")
    print(f"  작가: {converted.get('작가')}")
    print(f"  제목: {converted.get('제목')}")
    print(f"  재료: {converted.get('재료')}")
    
    # N/A 체크
    has_na = any(value == 'N/A' for key, value in converted.items() 
                 if key in ['작가', '제목', '재료'])
    
    if has_na:
        print("❌ N/A 값이 여전히 존재합니다")
        return False
    
    print("✅ 데이터 변환 성공 - N/A 문제 해결됨")
    return True


def test_prompt_generation():
    """프롬프트 생성 테스트"""
    print("\n🧪 프롬프트 생성 테스트")
    print("=" * 50)
    
    # 테스트용 작품 데이터
    test_artwork = {
        "작가": "리차드 맥베티스",
        "제목": "Happening",
        "재료": "울, 면",
        "국적": "영국",
        "제작년도": "2025",
        "크기": "100×4×100cm",
        "작가노트": "시간과 공간에 대한 탐구...",
        "작품설명": "강박적 바느질로 표현한 작품"
    }
    
    # 프롬프트 로더 테스트
    from utils.prompt_loader import get_prompt_loader
    prompt_loader = get_prompt_loader()
    
    try:
        # 일반 관람객 프롬프트 생성
        visitor_prompt = prompt_loader.format_visitor_prompt(test_artwork)
        
        # 작가명과 작품명이 포함되었는지 확인
        has_artist = "리차드 맥베티스" in visitor_prompt
        has_title = "Happening" in visitor_prompt
        has_na = "N/A" in visitor_prompt
        
        print(f"작가명 포함: {'✅' if has_artist else '❌'}")
        print(f"작품명 포함: {'✅' if has_title else '❌'}")
        print(f"N/A 없음: {'✅' if not has_na else '❌'}")
        
        if has_artist and has_title and not has_na:
            print("✅ 프롬프트 생성 성공 - 작가명/작품명 정상 포함")
            return True
        else:
            print("❌ 프롬프트 생성 실패")
            if has_na:
                print("   - N/A 값이 포함되어 있습니다")
            return False
            
    except Exception as e:
        print(f"❌ 프롬프트 생성 중 오류: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🔍 N/A 문제 해결 테스트")
    print("=" * 60)
    
    tests = [
        ("데이터 변환", test_data_conversion),
        ("프롬프트 생성", test_prompt_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ [{test_name}] 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("🎯 테스트 결과")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n총 결과: {success_count}/{len(results)}개 성공")
    
    if success_count == len(results):
        print("🎉 모든 테스트 통과! N/A 문제 해결 완료")
        return 0
    else:
        print("⚠️ 일부 테스트 실패. 추가 수정이 필요합니다.")
        return 1


if __name__ == "__main__":
    exit(main())