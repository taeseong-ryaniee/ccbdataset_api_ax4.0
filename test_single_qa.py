#!/usr/bin/env python3
"""
단일 작품 Q&A 생성 테스트
"""

from pathlib import Path
from processors.ax4_processor import AX4Processor
from utils.common import load_json_safe

def test_single_artwork_qa():
    """단일 작품 Q&A 생성 테스트"""
    print("🎨 단일 작품 Q&A 생성 테스트")
    print("=" * 60)
    
    # 데이터 로드
    data_file = Path("data/items_202509011603.json")
    if not data_file.exists():
        print("❌ 테스트 데이터 파일이 없습니다")
        return False
    
    json_data = load_json_safe(data_file)
    if not json_data or 'items' not in json_data:
        print("❌ 잘못된 데이터 형식")
        return False
    
    # 첫 번째 작품만 선택
    first_item = json_data['items'][0]
    
    print(f"📝 테스트 작품: {first_item.get('title')} - {first_item.get('artist_name')}")
    
    # 프로세서 생성 (고속 모드)
    processor = AX4Processor(fast_mode=True)
    
    # 데이터 변환
    artwork = processor.convert_item_to_artwork_format(first_item)
    
    print(f"   작가: {artwork.get('작가')}")
    print(f"   제목: {artwork.get('제목')}")
    print(f"   재료: {artwork.get('재료')}")
    print(f"   국적: {artwork.get('국적')}")
    
    # 파일명 생성
    safe_artist = processor.sanitize_filename(artwork.get('작가', 'Unknown'))
    safe_title = processor.sanitize_filename(artwork.get('제목', 'Unknown'))
    output_filename = f"TEST_{safe_artist}_{safe_title}.json"
    
    print(f"\n🚀 Q&A 생성 시작...")
    print(f"   출력 파일명: {output_filename}")
    
    try:
        # Q&A 생성
        result_path = processor.process_artwork(artwork, output_filename)
        
        if result_path:
            print(f"✅ Q&A 생성 성공!")
            print(f"   결과 파일: {result_path}")
            
            # 생성된 파일 확인
            output_path = Path(result_path)
            if output_path.exists():
                qa_data = load_json_safe(output_path)
                if qa_data and isinstance(qa_data, list):
                    print(f"   생성된 Q&A 수: {len(qa_data)}개")
                    
                    # 첫 번째 Q&A 샘플 출력
                    if qa_data:
                        sample_qa = qa_data[0]
                        instruction = sample_qa.get('instruction', '')[:100]
                        output_text = sample_qa.get('output', '')[:100]
                        
                        print(f"\n📋 샘플 Q&A:")
                        print(f"   질문: {instruction}...")
                        print(f"   답변: {output_text}...")
                        
                        # 작가명/작품명 포함 확인
                        has_artist = artwork.get('작가', '') in instruction and artwork.get('작가', '') in output_text
                        has_title = artwork.get('제목', '') in instruction or artwork.get('제목', '') in output_text
                        
                        print(f"\n✅ 품질 확인:")
                        print(f"   작가명 포함: {'✅' if has_artist else '❌'}")
                        print(f"   작품명 포함: {'✅' if has_title else '❌'}")
                        print(f"   N/A 없음: {'✅' if 'N/A' not in instruction + output_text else '❌'}")
                        
                        return True
            
        else:
            print("❌ Q&A 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ Q&A 생성 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    success = test_single_artwork_qa()
    
    if success:
        print("\n🎉 테스트 완료! Q&A 생성이 정상적으로 작동합니다.")
        print("   이제 ./run_ax4.sh 를 실행하여 모든 작품을 처리할 수 있습니다.")
    else:
        print("\n❌ 테스트 실패. 문제를 확인하세요.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())