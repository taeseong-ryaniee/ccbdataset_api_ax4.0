#!/usr/bin/env python3
"""
CCB Dataset Transformer - A.X 4.0 API 전용 메인 실행기
- A.X 4.0 API 기반 Q&A 생성
- 기존 EXAONE MLX와 동일한 인터페이스
- 고속 모드/정밀 모드 선택 가능
"""

import sys
import argparse
from processors.ax4_processor import AX4Processor


def main():
    """메인 실행 함수"""
    
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description="CCB Dataset Transformer - A.X 4.0 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_ax4.py                # 기본 고속 모드
  python main_ax4.py --fast         # 고속 모드 (빠른 생성)
  python main_ax4.py --precise      # 정밀 모드 (높은 품질)
"""
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--fast', action='store_true',
        help='고속 모드 (기본값): 빠른 생성'
    )
    mode_group.add_argument(
        '--precise', action='store_true',
        help='정밀 모드: 높은 품질'
    )
    
    args = parser.parse_args()
    
    # 모드 결정
    fast_mode = not args.precise  # 기본값: 고속 모드
    
    print("🎨 CCB Dataset Transformer (A.X 4.0 API)")
    print("=" * 60)
    
    mode_str = "⚡ 고속 모드" if fast_mode else "🎯 정밀 모드"
    print(f"📊 실행 모드: {mode_str}")
    print(f"🌐 API 제공자: SKT A.X 4.0")
    print(f"🎯 목표 생성량: 80개 Q&A (30+30+20)")
    print("=" * 60)
    
    try:
        # A.X 4.0 프로세서 생성 및 실행
        processor = AX4Processor(fast_mode=fast_mode)
        
        # 처리 통계 출력
        stats = processor.get_processing_stats()
        print(f"📁 데이터 디렉토리: {stats['data_dir']}")
        print(f"📂 출력 디렉토리: {stats['output_dir']}")
        print("=" * 60)
        
        processor.process_all_files()
        
        print(f"\n🎉 모든 작업이 완료되었습니다! ({mode_str})")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())