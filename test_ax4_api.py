#!/usr/bin/env python3
"""
A.X 4.0 API 테스트 스크립트
- API 연결 테스트
- 단일 작품 Q&A 생성 테스트
"""

import json
import sys
from pathlib import Path

# openai 패키지 설치 확인
try:
    from openai import OpenAI
    print("✅ openai 패키지 확인 완료")
except ImportError:
    print("❌ openai 패키지가 설치되지 않았습니다.")
    print("설치 명령: pip install openai")
    sys.exit(1)

from models.ax4_api_agent import get_ax4_client, generate_all_qa_batch
from utils.common import load_json_safe


def test_api_connection():
    """API 연결 테스트"""
    print("\n🔗 A.X 4.0 API 연결 테스트")
    print("=" * 50)
    
    try:
        client = get_ax4_client()
        
        # 간단한 테스트 요청
        response = client.chat.completions.create(
            model="ax4",
            messages=[
                {"role": "user", "content": "안녕하세요! 간단한 인사말로 답변해주세요."}
            ],
            max_tokens=100
        )
        
        answer = response.choices[0].message.content
        print(f"✅ API 연결 성공!")
        print(f"테스트 응답: {answer[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")
        return False


def test_qa_generation():
    """단일 작품 Q&A 생성 테스트"""
    print("\n📝 Q&A 생성 테스트")
    print("=" * 50)
    
    # 테스트용 샘플 작품 데이터
    sample_artwork = {
        "제목": "Happening",
        "작가": "리차드 맥베티스",
        "국적": "영국",
        "재료": "울, 면",
        "크기": "100×4×100cm",
        "제작년도": "2025",
        "작가노트": "4년에 걸쳐 제작된 작품은 천체와 세포를 모두 암시하는 상상의 시공간을 형성합니다...",
        "작품설명": "상상의 시공간으로 표현한 강박적 바느질은 천체와 세포적 세계를 동시에 암시한다."
    }
    
    try:
        print("🎯 테스트 작품: Happening - 리차드 맥베티스")
        print("⚡ 고속 모드로 Q&A 생성 중...")
        
        qa_json = generate_all_qa_batch(
            artwork=sample_artwork,
            fast_mode=True,
            exclude_questions=None
        )
        
        qa_list = json.loads(qa_json)
        total_count = len(qa_list)
        
        print(f"✅ Q&A 생성 완료: {total_count}개")
        
        # 생성된 Q&A 샘플 출력
        if qa_list:
            print("\n📋 생성된 Q&A 샘플 (처음 3개):")
            for i, qa in enumerate(qa_list[:3], 1):
                instruction = qa.get('instruction', '질문 없음')[:80]
                output = qa.get('output', '답변 없음')[:80]
                print(f"  {i}. 질문: {instruction}...")
                print(f"     답변: {output}...")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Q&A 생성 실패: {e}")
        return False


def test_with_real_data():
    """실제 데이터 파일을 사용한 테스트"""
    print("\n📁 실제 데이터 파일 테스트")
    print("=" * 50)
    
    data_file = Path("data/items_202509011603.json")
    
    if not data_file.exists():
        print(f"⚠️ 테스트 데이터 파일 없음: {data_file}")
        return False
    
    try:
        # 데이터 로드
        data = load_json_safe(data_file)
        if not isinstance(data, dict) or 'items' not in data:
            print("❌ 잘못된 데이터 형식")
            return False
        
        items = data['items']
        if not items:
            print("❌ 데이터 항목 없음")
            return False
        
        # 첫 번째 항목으로 테스트
        first_item = items[0]
        
        # 데이터 변환 (API에 맞는 형식으로)
        artwork = {
            "제목": first_item.get('title', ''),
            "영문제목": first_item.get('title_eng', ''),
            "작가": first_item.get('artist_name', ''),
            "영문작가명": first_item.get('artist_name_eng', ''),
            "국적": first_item.get('nationality', ''),
            "재료": first_item.get('materials', ''),
            "크기": first_item.get('size', ''),
            "제작년도": first_item.get('year', ''),
            "작가노트": first_item.get('artist_note', ''),
            "작품설명": first_item.get('description', '')
        }
        
        print(f"🎯 테스트 작품: {artwork['제목']} - {artwork['작가']}")
        print("⚡ 실제 데이터로 Q&A 생성 중...")
        
        qa_json = generate_all_qa_batch(
            artwork=artwork,
            fast_mode=True,
            exclude_questions=None
        )
        
        qa_list = json.loads(qa_json)
        total_count = len(qa_list)
        
        print(f"✅ 실제 데이터 Q&A 생성 완료: {total_count}개")
        return True
        
    except Exception as e:
        print(f"❌ 실제 데이터 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🧪 A.X 4.0 API 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("API 연결", test_api_connection),
        ("Q&A 생성", test_qa_generation),
        ("실제 데이터", test_with_real_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 [{test_name}] 테스트 실행 중...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ [{test_name}] 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("🎯 테스트 결과 요약")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n총 성공: {success_count}/{len(results)}개")
    
    if success_count == len(results):
        print("🎉 모든 테스트 통과! A.X 4.0 API 사용 준비 완료")
        return 0
    else:
        print("⚠️ 일부 테스트 실패. 설정을 확인하세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())