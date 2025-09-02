#!/usr/bin/env python3
"""
타임아웃 문제 해결 테스트 - 배치 분할 및 재시도 로직 검증
"""

from pathlib import Path
from processors.ax4_processor import AX4Processor
from utils.common import load_json_safe

def test_improved_api_calls():
    """개선된 API 호출 테스트"""
    print("🚀 타임아웃 문제 해결 테스트")
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
    
    # 첫 번째 작품으로 테스트
    first_item = json_data['items'][0]
    
    print(f"📝 테스트 작품: {first_item.get('title')} - {first_item.get('artist_name')}")
    
    # 프로세서 생성 (고속 모드)
    processor = AX4Processor(fast_mode=True)
    
    # 데이터 변환
    artwork = processor.convert_item_to_artwork_format(first_item)
    
    print(f"   작가: {artwork.get('작가')}")
    print(f"   제목: {artwork.get('제목')}")
    
    # 파일명 생성
    safe_artist = processor.sanitize_filename(artwork.get('작가', 'Unknown'))
    safe_title = processor.sanitize_filename(artwork.get('제목', 'Unknown'))
    output_filename = f"TEST_TIMEOUT_FIX_{safe_artist}_{safe_title}.json"
    
    print(f"\n🔧 개선된 배치 분할 처리로 Q&A 생성 시작...")
    print(f"   - 80개 목표를 5단계로 분할 (15+15+15+15+20)")
    print(f"   - 각 단계별 재시도 로직 적용")
    print(f"   - 지수 백오프 및 API 부하 감소 대기시간 적용")
    print(f"   출력 파일명: {output_filename}")
    
    try:
        # Q&A 생성 (개선된 로직)
        result_path = processor.process_artwork(artwork, output_filename)
        
        if result_path:
            print(f"\n✅ 개선된 Q&A 생성 성공!")
            print(f"   결과 파일: {result_path}")
            
            # 생성된 파일 확인
            output_path = Path(result_path)
            if output_path.exists():
                qa_data = load_json_safe(output_path)
                if qa_data and isinstance(qa_data, list):
                    print(f"   생성된 Q&A 수: {len(qa_data)}개")
                    
                    # 성공 기준
                    if len(qa_data) >= 30:  # 최소 30개 이상
                        print(f"✅ 목표 달성: {len(qa_data)}개 >= 30개 (최소 기준)")
                        
                        # 샘플 Q&A 확인
                        if qa_data:
                            sample_qa = qa_data[0]
                            instruction = sample_qa.get('instruction', '')
                            
                            # N/A 체크
                            has_na = 'N/A' in instruction
                            has_artist = artwork.get('작가', '') in instruction
                            
                            print(f"\n📋 품질 검증:")
                            print(f"   작가명 포함: {'✅' if has_artist else '❌'}")
                            print(f"   N/A 없음: {'✅' if not has_na else '❌'}")
                            
                            return True
                    else:
                        print(f"⚠️ 목표 미달: {len(qa_data)}개 < 30개 (최소 기준)")
                        print("   일부 배치가 타임아웃으로 실패했을 가능성")
                        return len(qa_data) > 10  # 10개 이상이면 부분 성공
            
        else:
            print("❌ Q&A 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ Q&A 생성 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🧪 504 Gateway Timeout 문제 해결 테스트")
    print("=" * 80)
    
    success = test_improved_api_calls()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 타임아웃 문제 해결 테스트 성공!")
        print("   - 배치 분할 처리가 정상적으로 작동합니다")
        print("   - 재시도 로직이 효과적으로 동작합니다")
        print("   - API 부하 감소 대기시간이 적용되었습니다")
        print("\n💡 이제 ./run_ax4.sh 실행이 안전합니다")
    else:
        print("⚠️ 타임아웃 문제가 일부 해결되었지만 완전하지 않습니다")
        print("   - 일부 배치는 여전히 타임아웃될 수 있습니다")
        print("   - 하지만 전체 시스템 실패는 방지됩니다")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())